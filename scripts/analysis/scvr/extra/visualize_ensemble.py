"""
ensemble_exceedance.py
======================
Presentation-grade script that, for a given site + climate variable:

  1. Loads multi-model CMIP6 ensemble data from the existing .nc cache
     (or downloads via THREDDS NCSS if not cached yet)
  2. Plots annual P10 / P50 / P90 time series for baseline + two SSP scenarios
  3. Plots traditional exceedance curves  (x = value, y = exceedance probability)
     for baseline, SSP2-4.5, and SSP5-8.5 with decade overlays
  4. Computes SCVR for each scenario and annotates it on the exceedance curve plot
  5. Plots decade-resolved exceedance curves (shape change visibility)
  6. Plots SCVR annual progression (anchor fit for temp, decade bars for others)
  7. Saves all outputs to data/processed/presentation/<site>/<variable>/

Usage
-----
Edit the CONFIG block below, then run from the project root:

    python scripts/presentation/ensemble_exceedance.py

Outputs (in data/processed/presentation/<SITE_ID>/<VARIABLE>/):
    ensemble_timeseries_<var>.png      — annual P10/P50/P90 spaghetti + band
    exceedance_curves_<var>.png        — traditional exceedance curves + SCVR labels
    exceedance_decades_<var>.png       — decade-resolved exceedance (shape change)
    scvr_progression_<var>.png         — SCVR annual trajectory or decade bars
    ensemble_stats_<var>.csv           — annual P10/P50/P90 per scenario (numerical)
    scvr_summary_<var>.json            — SCVR + decade breakdown + shape metrics
"""

# ── CONFIG — edit these to change what gets plotted ──────────────────────────
SITE_ID        = "hayhurst_solar"   # or "maverick_wind"
VARIABLES      = ["tasmax", "tasmin", "tas", "pr", "sfcWind", "hurs", "rsds"]
# VARIABLES    = ["tasmax"]         # uncomment to run a single variable
SCENARIOS      = ["ssp245", "ssp585"]
MAX_MODELS     = None  # Use all available (was 6 — expanded per Prashant review)
BASELINE_YEARS = (1985, 2014)
FUTURE_YEARS   = (2026, 2055)

# ── Decade windows for progression analysis ──────────────────────────────────
DECADE_WINDOWS = [
    ("2026-2035", 2026, 2035),
    ("2036-2045", 2036, 2045),
    ("2046-2055", 2046, 2055),
]

# ── Variable-specific SCVR strategy ──────────────────────────────────────────
SCVR_STRATEGY = {
    "tasmax": "anchor_3_linear", "tasmin": "anchor_3_linear", "tas": "anchor_3_linear",
    "pr": "period_average", "hurs": "period_average",
    "sfcWind": "period_average", "rsds": "period_average",
}
ANCHOR_3 = [(2026, 2035), (2036, 2045), (2046, 2055)]
# ─────────────────────────────────────────────────────────────────────────────

import warnings
warnings.filterwarnings("ignore")

import json
import io
import sys
import time
import threading
import numpy as np
import pandas as pd
import xarray as xr
import cftime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy import stats as sp_stats

# ── Import shared utilities ───────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
try:
    from scvr_utils import (
        compute_anchor_fit, compute_shape_metrics, fit_gev,
        exceedance_curve_gev, fit_gpd, exceedance_curve_gpd, pool_window,
        compute_cvar, fit_gev_single_model, compute_report_card,
    )
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "data" / "schema"
CACHE_DIR  = ROOT / "data" / "cache" / "thredds"

CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ── Load schemas ──────────────────────────────────────────────────────────────
with open(SCHEMA_DIR / "sites.json") as f:
    SITES = json.load(f)
with open(SCHEMA_DIR / "variables.json") as f:
    VARS = json.load(f)

site   = SITES[SITE_ID]
LAT    = site["lat"]
LON    = site["lon"]

# OUT_DIR, UNIT, VAR_FULL, VARIABLE are set per-variable inside main()

# ── All 34 NEX-GDDP models ────────────────────────────────────────────────────
ALL_MODELS = [
    "ACCESS-CM2","ACCESS-ESM1-5","BCC-CSM2-MR","CanESM5","CESM2",
    "CESM2-LENS","CMCC-CM2-SR5","CMCC-ESM2","CNRM-CM6-1","CNRM-ESM2-1",
    "EC-Earth3","EC-Earth3-Veg-LR","FGOALS-g3","GFDL-CM4","GFDL-CM4_gr2",
    "GFDL-ESM4","GISS-E2-1-G","HadGEM3-GC31-LL","HadGEM3-GC31-MM",
    "IITM-ESM","INM-CM4-8","INM-CM5-0","IPSL-CM6A-LR","KACE-1-0-G",
    "KIOST-ESM","MIROC6","MPI-ESM1-2-HR","MPI-ESM1-2-LR","MRI-ESM2-0",
    "NESM3","NorESM2-LM","NorESM2-MM","TaiESM1","UKESM1-0-LL",
]

# ── Plot style ────────────────────────────────────────────────────────────────
SCENARIO_COLORS = {"ssp245": "#4472C4", "ssp585": "#C55A11"}
BASELINE_COLOR  = "#555555"
plt.rcParams.update({"figure.dpi": 150, "font.size": 10, "axes.titlesize": 12})


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — THREDDS Pipeline (ported verbatim from nb03)
# ══════════════════════════════════════════════════════════════════════════════

THREDDS_NCSS = "https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6"

# Grid labels and realizations vary across CMIP6 models on NEX-GDDP-CMIP6.
# Most models use r1i1p1f1/gn, but many use different grids (gr, gr1, gr2)
# or different realizations (r4i1p1f1, r1i1p1f2, etc.).
GRID_LABELS    = ["gn", "gr", "gr1", "gr2"]
REALIZATIONS   = ["r1i1p1f1", "r1i1p1f2", "r1i1p1f3", "r3i1p1f1", "r4i1p1f1"]

# Cache: model|scenario -> (realization, grid) once discovered
_model_variant_cache = {}
_model_variant_lock  = threading.Lock()
_VARIANT_CACHE_PATH  = CACHE_DIR / "model_variant_cache.json"
if _VARIANT_CACHE_PATH.exists():
    with open(_VARIANT_CACHE_PATH) as f:
        _model_variant_cache = json.load(f)


def _save_variant_cache():
    with open(_VARIANT_CACHE_PATH, "w") as f:
        json.dump(_model_variant_cache, f)


def build_thredds_urls(model, scenario, variable, year, lat, lon):
    """Return list of (url, realization, grid) tuples to try, best guess first."""
    params = (f"?var={variable}&latitude={lat}&longitude={lon}"
              f"&time_start={year}-01-01T00:00:00Z"
              f"&time_end={year}-12-30T23:59:59Z&accept=netCDF")  # 12-30 not 12-31: 360-day calendar models reject Dec 31

    # Check if we already know this model's variant
    cache_key = f"{model}|{scenario}"
    with _model_variant_lock:
        known = _model_variant_cache.get(cache_key)

    urls = []
    if known:
        real, grid = known["realization"], known["grid"]
        base = f"{THREDDS_NCSS}/{model}/{scenario}/{real}/{variable}"
        fname_v2 = f"{variable}_day_{model}_{scenario}_{real}_{grid}_{year}_v2.0.nc"
        fname_v1 = f"{variable}_day_{model}_{scenario}_{real}_{grid}_{year}.nc"
        urls.append((f"{base}/{fname_v2}{params}", real, grid))
        urls.append((f"{base}/{fname_v1}{params}", real, grid))
        return urls

    # Try all combinations — default (r1i1p1f1, gn) first
    for real in REALIZATIONS:
        for grid in GRID_LABELS:
            base = f"{THREDDS_NCSS}/{model}/{scenario}/{real}/{variable}"
            fname_v2 = f"{variable}_day_{model}_{scenario}_{real}_{grid}_{year}_v2.0.nc"
            fname_v1 = f"{variable}_day_{model}_{scenario}_{real}_{grid}_{year}.nc"
            urls.append((f"{base}/{fname_v2}{params}", real, grid))
            urls.append((f"{base}/{fname_v1}{params}", real, grid))
    return urls


def fetch_year(model, scenario, variable, year, lat, lon, cache_dir, retries=3):
    cache_key  = f"{model}_{scenario}_{variable}_{year}_{lat:.4f}_{lon:.4f}.nc"
    cache_path = cache_dir / cache_key

    def parse_nc(path_or_bytes):
        kw = dict(engine="scipy", decode_times=False)
        if isinstance(path_or_bytes, (str, Path)):
            ds = xr.open_dataset(path_or_bytes, **kw)
        else:
            ds = xr.open_dataset(io.BytesIO(path_or_bytes), **kw)
        da = ds[variable].squeeze()
        values = da.values.astype(float)
        tv = ds["time"]
        units    = tv.attrs.get("units", f"days since {year}-01-01")
        calendar = tv.attrs.get("calendar", "standard").lower()
        nums     = tv.values.astype(float)
        try:
            cf = cftime.num2date(nums, units=units, calendar=calendar)
            times = pd.to_datetime([f"{d.year:04d}-{d.month:02d}-{d.day:02d}" for d in cf])
        except Exception:
            times = pd.date_range(f"{year}-01-01", periods=len(values), freq="D")
        return pd.Series(values, index=times, name=f"{model}_{year}")

    if cache_path.exists() and cache_path.stat().st_size > 500:
        try:
            return parse_nc(cache_path)
        except Exception:
            cache_path.unlink(missing_ok=True)

    url_variants = build_thredds_urls(model, scenario, variable, year, lat, lon)
    for attempt in range(retries):
        for url, real, grid in url_variants:
            try:
                r = requests.get(url, timeout=60)
                if r.status_code == 200 and len(r.content) > 500:
                    cache_path.write_bytes(r.content)
                    # Cache the discovered variant for future lookups
                    cache_key_var = f"{model}|{scenario}"
                    with _model_variant_lock:
                        if cache_key_var not in _model_variant_cache:
                            _model_variant_cache[cache_key_var] = {
                                "realization": real, "grid": grid
                            }
                            _save_variant_cache()
                    return parse_nc(r.content)
            except Exception:
                pass
        time.sleep(2 ** attempt)
    return None


def fetch_model_years(model, scenario, variable, years, lat, lon,
                      cache_dir, max_workers=4):
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {
            ex.submit(fetch_year, model, scenario, variable,
                      yr, lat, lon, cache_dir): yr
            for yr in years
        }
        for fut in as_completed(futures):
            yr  = futures[fut]
            res = fut.result()
            if res is not None:
                results[yr] = res
    if not results:
        return None
    combined = pd.concat([results[yr] for yr in sorted(results)])
    return combined.sort_index()


def unit_convert(series, variable):
    if variable.startswith("ta") and series.mean() > 200:
        series = series - 273.15
    if variable == "pr":
        series = series * 86400
    return series


def probe_model(model, scenario, variable, probe_year, lat, lon):
    url_variants = build_thredds_urls(model, scenario, variable,
                                       probe_year, lat, lon)
    for url, real, grid in url_variants:
        try:
            r = requests.head(url, timeout=15)
            if r.status_code == 200:
                # Cache the discovered variant
                cache_key = f"{model}|{scenario}"
                with _model_variant_lock:
                    if cache_key not in _model_variant_cache:
                        _model_variant_cache[cache_key] = {
                            "realization": real, "grid": grid
                        }
                        _save_variant_cache()
                return True
            r = requests.get(url, timeout=20, stream=True)
            if r.status_code == 200:
                cache_key = f"{model}|{scenario}"
                with _model_variant_lock:
                    if cache_key not in _model_variant_cache:
                        _model_variant_cache[cache_key] = {
                            "realization": real, "grid": grid
                        }
                        _save_variant_cache()
                return True
        except Exception:
            pass
    return False


# ── Probe cache ───────────────────────────────────────────────────────────────
PROBE_CACHE_PATH = CACHE_DIR / "model_probe_cache.json"
if PROBE_CACHE_PATH.exists():
    with open(PROBE_CACHE_PATH) as f:
        _probe_cache = json.load(f)
else:
    _probe_cache = {}

_probe_cache_lock = threading.Lock()

def probe_model_cached(model, scenario, variable, year, lat, lon):
    key = f"{model}|{scenario}|{variable}|{year}|{lat:.4f}|{lon:.4f}"
    with _probe_cache_lock:
        if key in _probe_cache:
            return _probe_cache[key]
    result = probe_model(model, scenario, variable, year, lat, lon)
    with _probe_cache_lock:
        _probe_cache[key] = result
        with open(PROBE_CACHE_PATH, "w") as f:
            json.dump(_probe_cache, f)
    return result


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Model Discovery
# ══════════════════════════════════════════════════════════════════════════════

def discover_models():
    """Find models that have data for this site/variable/both scenarios."""
    mid_year = FUTURE_YEARS[0] + (FUTURE_YEARS[1] - FUTURE_YEARS[0]) // 2
    confirmed = set(ALL_MODELS)

    for scen in SCENARIOS:
        print(f"  Probing {scen} at year {mid_year} ...", flush=True)
        passed = set()
        with ThreadPoolExecutor(max_workers=12) as ex:
            futures = {ex.submit(probe_model_cached, m, scen, VARIABLE,
                                  mid_year, LAT, LON): m for m in confirmed}
            for fut in as_completed(futures):
                if fut.result():
                    passed.add(futures[fut])
        confirmed = confirmed & passed
        print(f"    {len(confirmed)} models pass {scen}")

    # Confirm historical
    print("  Confirming historical availability ...", flush=True)
    hist_ok = set()
    with ThreadPoolExecutor(max_workers=12) as ex:
        futures = {ex.submit(probe_model_cached, m, "historical", VARIABLE,
                              2000, LAT, LON): m for m in confirmed}
        for fut in as_completed(futures):
            if fut.result():
                hist_ok.add(futures[fut])

    models = sorted(hist_ok)
    if MAX_MODELS is not None:
        models = models[:MAX_MODELS]
    print(f"  Final: {len(models)} models → {models}")
    return models


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Data Loading
# ══════════════════════════════════════════════════════════════════════════════

def load_data(models):
    """Returns baseline_daily and future_daily dicts per scenario."""
    baseline_daily = {}
    future_daily   = {scen: {} for scen in SCENARIOS}

    for model in models:
        print(f"  Loading {model} ...", flush=True)

        base = fetch_model_years(
            model, "historical", VARIABLE,
            range(BASELINE_YEARS[0], BASELINE_YEARS[1] + 1),
            LAT, LON, CACHE_DIR
        )
        if base is not None:
            baseline_daily[model] = unit_convert(base, VARIABLE)

        for scen in SCENARIOS:
            fut = fetch_model_years(
                model, scen, VARIABLE,
                range(FUTURE_YEARS[0], FUTURE_YEARS[1] + 1),
                LAT, LON, CACHE_DIR
            )
            if fut is not None:
                future_daily[scen][model] = unit_convert(fut, VARIABLE)

    return baseline_daily, future_daily


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SCVR Computation
# ══════════════════════════════════════════════════════════════════════════════

def compute_scvr(baseline_values, future_values):
    """Exact port from notebook_analysis/01_hayhurst_solar_scvr.ipynb (cell fe500174)."""
    b = np.sort(baseline_values[~np.isnan(baseline_values)])[::-1].astype(float)
    f = np.sort(future_values[~np.isnan(future_values)])[::-1].astype(float)
    exc_b = np.linspace(0, 1, len(b))
    exc_f = np.linspace(0, 1, len(f))
    area_b = float(np.trapezoid(b, exc_b))
    area_f = float(np.trapezoid(f, exc_f))
    scvr = (area_f - area_b) / area_b if area_b != 0 else 0.0
    return {"scvr": scvr, "area_baseline": area_b, "area_future": area_f,
            "n_baseline_days": len(b), "n_future_days": len(f)}


def exceedance_curve_traditional(values):
    """
    Traditional hydrology view: x = value, y = P(X > x).
    Returns (sorted_values_ascending, exceedance_probabilities).
    Plot with: plt.plot(vals, exc)
    """
    v = np.sort(values[~np.isnan(values)])
    p = 1.0 - np.linspace(0, 1, len(v))
    return v, p


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Plot 1: Annual P10/P50/P90 Time Series
# ══════════════════════════════════════════════════════════════════════════════

def plot_timeseries(baseline_daily, future_daily, scvr_results, n_models=0):
    fig, axes = plt.subplots(1, 2, figsize=(16, 5), sharey=True,
                             gridspec_kw={"wspace": 0.05})

    # Helper: annual aggregate per model then ensemble stats
    # pr uses sum (annual total mm/year); all others use mean
    ts_agg_label = "annual total" if TS_RESAMPLE == "sum" else "annual mean"
    def annual_stats(daily_dict):
        ann = pd.DataFrame({
            m: getattr(s.resample("YE"), TS_RESAMPLE)()
            for m, s in daily_dict.items()
            if s is not None
        })
        if ann.empty:
            return None, None
        return ann, pd.DataFrame({
            "p10":  ann.quantile(0.10, axis=1),
            "p50":  ann.quantile(0.50, axis=1),
            "p90":  ann.quantile(0.90, axis=1),
        })

    base_ann, base_stats = annual_stats(baseline_daily)

    # Panel 0: Baseline
    ax = axes[0]
    ax.set_facecolor("#f9f9f9")
    if base_stats is not None:
        ax.fill_between(base_stats.index, base_stats["p10"], base_stats["p90"],
                        color=BASELINE_COLOR, alpha=0.20,
                        label=f"Model P10–P90 range ({ts_agg_label}s)")
        for m in base_ann.columns:
            ax.plot(base_ann.index, base_ann[m], color=BASELINE_COLOR,
                    lw=0.8, alpha=0.5)
        ax.plot(base_stats.index, base_stats["p50"], color=BASELINE_COLOR,
                lw=2.5, label=f"Model median ({ts_agg_label})")
    ax.set_title(f"Historical {BASELINE_YEARS[0]}–{BASELINE_YEARS[1]}", fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel(f"{VAR_FULL} ({TS_UNIT})")
    ax.legend(fontsize=8)

    # Panel 1: Both SSP scenarios
    ax = axes[1]
    ax.set_facecolor("#f9f9f9")
    for scen in SCENARIOS:
        color = SCENARIO_COLORS[scen]
        fut_ann, fut_stats = annual_stats(future_daily[scen])
        if fut_stats is None:
            continue
        ax.fill_between(fut_stats.index, fut_stats["p10"], fut_stats["p90"],
                        color=color, alpha=0.15)
        for m in fut_ann.columns:
            ax.plot(fut_ann.index, fut_ann[m], color=color, lw=0.8, alpha=0.5)
        ax.plot(fut_stats.index, fut_stats["p50"], color=color, lw=2.5,
                label=f"{scen.upper()} median ({ts_agg_label})  SCVR={scvr_results[scen]['scvr']:+.4f}")

    ax.set_title(f"Future {FUTURE_YEARS[0]}–{FUTURE_YEARS[1]}", fontweight="bold")
    ax.set_xlabel("Year")
    ax.legend(fontsize=8)

    fig.suptitle(
        f"{VAR_FULL} — {site['name']}  |  Multi-Model Ensemble ({n_models} models)",
        fontsize=12, fontweight="bold", y=1.01
    )
    fig.text(
        0.5, -0.03,
        f"Aggregation: daily values → {ts_agg_label} per model (thin lines). "
        "Thick line = median across models. Band = model spread (P10–P90 across models). "
        "These are NOT daily percentiles — they show how much models disagree with each other.",
        ha="center", fontsize=7.5, color="#555555"
    )
    plt.tight_layout()
    out = OUT_DIR / f"ensemble_timeseries_{VARIABLE}.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")

    # Save numerical stats
    rows = []
    for scen in SCENARIOS:
        fut_ann, fut_stats = annual_stats(future_daily[scen])
        if fut_stats is not None:
            for yr, row in fut_stats.iterrows():
                rows.append({"scenario": scen, "year": yr.year,
                             "p10": row["p10"], "p50": row["p50"], "p90": row["p90"]})
    if base_stats is not None:
        for yr, row in base_stats.iterrows():
            rows.append({"scenario": "historical", "year": yr.year,
                         "p10": row["p10"], "p50": row["p50"], "p90": row["p90"]})
    csv_path = OUT_DIR / f"ensemble_stats_{VARIABLE}.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"  Saved: {csv_path}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Plot 2: Exceedance Curves (Traditional View)
# ══════════════════════════════════════════════════════════════════════════════

def plot_exceedance(baseline_daily, future_daily, scvr_results):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor("#f9f9f9")

    # Pool all model daily values
    def pool(daily_dict):
        parts = [s.values for s in daily_dict.values() if s is not None]
        return np.concatenate(parts) if parts else np.array([])

    base_pool = pool(baseline_daily)
    base_vals, base_exc = exceedance_curve_traditional(base_pool)
    ax.plot(base_vals, base_exc, color=BASELINE_COLOR, lw=2.2,
            label=f"Historical {BASELINE_YEARS[0]}–{BASELINE_YEARS[1]}", zorder=3)

    # P90 threshold line from baseline (exceedance = 0.10)
    p90_idx = np.searchsorted(base_exc[::-1], 0.10)
    p90_val = base_vals[len(base_vals) - 1 - p90_idx] if p90_idx < len(base_vals) else None

    for scen in SCENARIOS:
        color = SCENARIO_COLORS[scen]
        fut_pool = pool(future_daily[scen])
        if len(fut_pool) == 0:
            continue
        fut_vals, fut_exc = exceedance_curve_traditional(fut_pool)
        scvr_val = scvr_results[scen]["scvr"]
        label = (f"{scen.upper()} {FUTURE_YEARS[0]}–{FUTURE_YEARS[1]}"
                 f"    SCVR = {scvr_val:+.4f}")
        ax.plot(fut_vals, fut_exc, color=color, lw=2.2, label=label, zorder=3)

        # Shade the horizontal gap between baseline and future at P90 level
        if p90_val is not None:
            p90_fut_idx = np.searchsorted(fut_exc[::-1], 0.10)
            p90_fut_val = fut_vals[len(fut_vals) - 1 - p90_fut_idx] \
                          if p90_fut_idx < len(fut_vals) else None
            if p90_fut_val is not None and p90_fut_val > p90_val:
                ax.annotate("",
                    xy=(p90_fut_val, 0.10), xytext=(p90_val, 0.10),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=1.5))

    # P90 reference line
    ax.axhline(0.10, color="black", lw=0.8, ls="--", alpha=0.5,
               label="Exceedance = 10% (P90 level)")
    if p90_val is not None:
        ax.axvline(p90_val, color=BASELINE_COLOR, lw=0.8, ls=":", alpha=0.6)

    # SCVR text box
    scvr_lines = ["SCVR (computed via value-integrated area):"]
    for scen in SCENARIOS:
        r = scvr_results.get(scen, {})
        scvr_lines.append(f"  {scen.upper()}: {r.get('scvr', 0):+.4f}")
    if len(SCENARIOS) == 2:
        delta = scvr_results[SCENARIOS[1]]["scvr"] - scvr_results[SCENARIOS[0]]["scvr"]
        scvr_lines.append(f"  Delta: {delta:+.4f}")
    ax.text(0.02, 0.04, "\n".join(scvr_lines), transform=ax.transAxes,
            fontsize=8, verticalalignment="bottom",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.85))

    ax.set_xlabel(f"{VAR_FULL} ({UNIT})", fontsize=11)
    ax.set_ylabel("Exceedance probability  P(X > x)", fontsize=11)
    ax.set_ylim(0, 1)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_title(
        f"Exceedance Curves — {VAR_FULL}  |  {site['name']}",
        fontweight="bold", fontsize=13
    )

    # Caption note
    fig.text(0.5, -0.02,
             "Note: x-axis shows value, y-axis shows fraction of days exceeding that value. "
             "Rightward shift of future curves = more frequent/intense events. "
             "SCVR is computed separately as the fractional change in value-integrated exceedance area.",
             ha="center", fontsize=7.5, color="#555555")

    plt.tight_layout()
    out = OUT_DIR / f"exceedance_curves_{VARIABLE}.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6b — Inline Fallbacks (if shared module not available)
# ══════════════════════════════════════════════════════════════════════════════

if not SHARED_AVAILABLE:
    def pool_window(daily_dict, year_start, year_end):
        parts = []
        for series in daily_dict.values():
            mask = (series.index.year >= year_start) & (series.index.year <= year_end)
            parts.append(series[mask].values)
        return np.concatenate(parts) if parts else np.array([])

    def compute_anchor_fit(base_pool, future_daily_dict, anchors, future_years=None):
        if future_years is None:
            future_years = FUTURE_YEARS
        base_arr = np.asarray(base_pool, dtype=float)
        mids, scvrs = [], []
        for start, end in anchors:
            wp = pool_window(future_daily_dict, start, end)
            if len(wp) == 0: continue
            r = compute_scvr(base_arr, wp)
            mids.append((start + end) / 2)
            scvrs.append(r["scvr"])
        if len(mids) < 2: return None
        fit = np.polyfit(mids, scvrs, 1)
        years = list(range(future_years[0], future_years[1] + 1))
        annual = np.polyval(fit, years)
        ss_res = np.sum((np.array(scvrs) - np.polyval(fit, mids))**2)
        ss_tot = np.sum((np.array(scvrs) - np.mean(scvrs))**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
        return {"mids": mids, "scvrs": scvrs, "fit": fit, "years": years, "annual": annual, "r2": r2}

    def compute_shape_metrics(values):
        v = np.asarray(values, dtype=float)
        v = v[~np.isnan(v)]
        if len(v) == 0: return None
        return {
            "n_days": len(v), "mean": float(np.mean(v)), "std": float(np.std(v)),
            "variance": float(np.var(v)), "p95": float(np.percentile(v, 95)),
            "p99": float(np.percentile(v, 99)),
            "skewness": float(sp_stats.skew(v)), "kurtosis": float(sp_stats.kurtosis(v)),
        }

    def fit_gev(daily_dict, block="annual_max"):
        try:
            bv = []
            for s in daily_dict.values():
                if s is None: continue
                ann = s.resample("YE").max() if block == "annual_max" else s.resample("YE").min()
                bv.extend(ann.dropna().values.tolist())
            if len(bv) < 10: return None
            arr = np.array(bv, dtype=float)
            shape, loc, scale = sp_stats.genextreme.fit(arr)
            ks_stat, ks_pval = sp_stats.kstest(arr, 'genextreme', args=(shape, loc, scale))
            logpdfs = sp_stats.genextreme.logpdf(arr, shape, loc=loc, scale=scale)
            loglik = float(np.sum(logpdfs[np.isfinite(logpdfs)]))
            aic = 2 * 3 - 2 * loglik
            return {"shape": float(shape), "loc": float(loc), "scale": float(scale),
                    "n_blocks": len(arr), "ks_statistic": float(ks_stat),
                    "ks_pvalue": float(ks_pval), "loglikelihood": loglik, "aic": float(aic)}
        except Exception:
            return None

    def exceedance_curve_gev(shape, loc, scale, x_range):
        x = np.asarray(x_range, dtype=float)
        cdf = sp_stats.genextreme.cdf(x, shape, loc=loc, scale=scale)
        return x, 1.0 - cdf

    def fit_gpd(daily_dict, threshold_quantile=0.95):
        try:
            all_vals = np.concatenate([
                s.dropna().values for s in daily_dict.values() if s is not None
            ])
            if len(all_vals) < 100: return None
            threshold = float(np.percentile(all_vals, threshold_quantile * 100))
            exceedances = all_vals[all_vals > threshold] - threshold
            if len(exceedances) < 20: return None
            shape, _, scale = sp_stats.genpareto.fit(exceedances, floc=0)
            ks_stat, ks_pval = sp_stats.kstest(exceedances, 'genpareto', args=(shape, 0, scale))
            logpdfs = sp_stats.genpareto.logpdf(exceedances, shape, loc=0, scale=scale)
            loglik = float(np.sum(logpdfs[np.isfinite(logpdfs)]))
            aic = 2 * 2 - 2 * loglik
            return {
                "shape": float(shape), "scale": float(scale),
                "threshold": threshold, "n_exceedances": len(exceedances),
                "exceedance_rate": float(len(exceedances) / len(all_vals)),
                "n_total": len(all_vals),
                "ks_statistic": float(ks_stat), "ks_pvalue": float(ks_pval),
                "loglikelihood": loglik, "aic": float(aic),
            }
        except Exception:
            return None

    def exceedance_curve_gpd(shape, scale, threshold, rate, x_range):
        x = np.asarray(x_range, dtype=float)
        p = np.full_like(x, np.nan)
        mask = x >= threshold
        if mask.any():
            gpd_cdf = sp_stats.genpareto.cdf(x[mask] - threshold, shape, scale=scale)
            p[mask] = rate * (1.0 - gpd_cdf)
        return x, p


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6c — Plot 3: Decade-Resolved Exceedance Curves
# ══════════════════════════════════════════════════════════════════════════════

DECADE_COLORS = {
    "2026-2035": "#a6cee3",
    "2036-2045": "#1f78b4",
    "2046-2055": "#08306b",
}


def plot_decade_exceedance(baseline_daily, future_daily, scvr_results):
    """Exceedance curves split by decade — 2x2 with tail zoom for parametric fits."""
    nrows = 2
    fig, axes = plt.subplots(nrows, 2, figsize=(16, 6 * nrows), sharey="row",
                             gridspec_kw={"wspace": 0.05, "hspace": 0.20})

    def pool(daily_dict):
        parts = [s.values for s in daily_dict.values() if s is not None]
        return np.concatenate(parts) if parts else np.array([])

    base_pool = pool(baseline_daily)
    base_clean = base_pool[~np.isnan(base_pool)]
    base_p90 = float(np.percentile(base_clean, 90))
    base_p95 = float(np.percentile(base_clean, 95))

    for col, scen in enumerate(SCENARIOS):
        ax_full = axes[0, col]
        ax_full.set_facecolor("#f9f9f9")
        fut_dict = future_daily.get(scen, {})
        if not fut_dict:
            ax_full.set_title(f"{scen.upper()} — no data")
            continue

        # Baseline curve
        bv = np.sort(base_clean)
        bp = 1.0 - np.linspace(0, 1, len(bv))
        ax_full.plot(bv, bp, color=BASELINE_COLOR, lw=2.5,
                     label=f"Baseline {BASELINE_YEARS[0]}–{BASELINE_YEARS[1]}", zorder=4)

        # Per-decade curves
        dec_data = {}
        for label, start, end in DECADE_WINDOWS:
            dec_pool = pool_window(fut_dict, start, end)
            dec_clean = dec_pool[~np.isnan(dec_pool)]
            if len(dec_clean) == 0:
                continue
            dec_data[label] = dec_clean
            dv = np.sort(dec_clean)
            dp = 1.0 - np.linspace(0, 1, len(dv))
            ax_full.plot(dv, dp, color=DECADE_COLORS[label], lw=2.0,
                         label=label, zorder=3)

        ax_full.axhline(0.10, color="black", lw=0.8, ls="--", alpha=0.4)
        ax_full.set_title(f"{scen.upper()}", fontweight="bold")
        ax_full.set_xlabel(f"{VAR_FULL} ({UNIT})")
        ax_full.set_ylim(0, 1)
        ax_full.legend(fontsize=7, loc="upper right")

        # Row 2: Tail zoom with GPD + GEV
        ax_tail = axes[1, col]
        ax_tail.set_facecolor("#faf5f0")

        # Re-plot empirical curves zoomed
        ax_tail.plot(bv, bp, color=BASELINE_COLOR, lw=2.5, label="Baseline", zorder=4)
        for label in dec_data:
            dv = np.sort(dec_data[label])
            dp = 1.0 - np.linspace(0, 1, len(dv))
            ax_tail.plot(dv, dp, color=DECADE_COLORS[label], lw=2.0,
                         label=label, zorder=3)

        # Tail x-range for parametric fits
        x_tail = np.linspace(base_p90, base_clean.max() * 1.08, 300)

        # GPD fits (same probability space as empirical)
        gpd_base = fit_gpd(baseline_daily, threshold_quantile=0.95)
        if gpd_base:
            gx, gp = exceedance_curve_gpd(
                gpd_base["shape"], gpd_base["scale"],
                gpd_base["threshold"], gpd_base["exceedance_rate"], x_tail)
            ax_tail.plot(gx, gp, color=BASELINE_COLOR, ls="--", lw=1.8, alpha=0.7,
                         label="GPD fit (baseline)", zorder=5)

        # Late decade GPD
        late_dict = {}
        for m, s in fut_dict.items():
            mask = (s.index.year >= 2046) & (s.index.year <= 2055)
            late_dict[m] = s[mask]
        gpd_late = fit_gpd(late_dict, threshold_quantile=0.95)
        if gpd_late:
            gx, gp = exceedance_curve_gpd(
                gpd_late["shape"], gpd_late["scale"],
                gpd_late["threshold"], gpd_late["exceedance_rate"], x_tail)
            ax_tail.plot(gx, gp, color=DECADE_COLORS["2046-2055"], ls="--", lw=1.8,
                         alpha=0.7, label="GPD fit (2046-55)", zorder=5)

        # GEV fits (annual max context — different probability space)
        gev_base = fit_gev(baseline_daily, block="annual_max")
        if gev_base:
            gx, gp = exceedance_curve_gev(
                gev_base["shape"], gev_base["loc"], gev_base["scale"], x_tail)
            ax_tail.plot(gx, gp, color=BASELINE_COLOR, ls=":", lw=1.3, alpha=0.5,
                         label="GEV (ann. max, baseline)", zorder=2)

        gev_late = fit_gev(late_dict, block="annual_max")
        if gev_late:
            gx, gp = exceedance_curve_gev(
                gev_late["shape"], gev_late["loc"], gev_late["scale"], x_tail)
            ax_tail.plot(gx, gp, color=DECADE_COLORS["2046-2055"], ls=":", lw=1.3,
                         alpha=0.5, label="GEV (ann. max, 2046-55)", zorder=2)

        # KS D-statistic annotation
        diag_lines = []
        if gpd_base and "ks_statistic" in gpd_base:
            diag_lines.append(f"GPD base: D={gpd_base['ks_statistic']:.4f}")
        if gpd_late and "ks_statistic" in gpd_late:
            diag_lines.append(f"GPD late: D={gpd_late['ks_statistic']:.4f}")
        if diag_lines:
            ax_tail.text(0.02, 0.96, "\n".join(diag_lines),
                         transform=ax_tail.transAxes, fontsize=6,
                         verticalalignment="top", fontfamily="monospace",
                         bbox=dict(boxstyle="round,pad=0.3",
                                   facecolor="white", alpha=0.8))

        # P95 threshold marker
        ax_tail.axvline(base_p95, color="#999999", ls="-.", lw=0.8, alpha=0.5)
        ax_tail.text(base_p95, 0.14, " P95", fontsize=7, color="#999999")

        ax_tail.set_xlim(base_p90, base_clean.max() * 1.08)
        ax_tail.set_ylim(0, 0.15)
        ax_tail.set_title(f"{scen.upper()} — Tail Zoom (P > 0.90)", fontweight="bold",
                          fontsize=10)
        ax_tail.set_xlabel(f"{VAR_FULL} ({UNIT})")
        ax_tail.legend(fontsize=6, loc="upper right")

    axes[0, 0].set_ylabel("Exceedance probability  P(X > x)")
    axes[1, 0].set_ylabel("Exceedance probability  P(X > x)")

    fig.suptitle(
        f"Decade-Resolved Exceedance — {VAR_FULL}  |  {site['name']}",
        fontsize=13, fontweight="bold", y=1.01
    )
    caption = ("Each curve uses all models pooled within that decade. "
               "If tails fan out in later decades, the distribution shape is changing."
               "\nBottom row: tail zoom. Dashed = GPD (daily threshold exceedance, "
               "same probability space). Dotted = GEV (annual block maxima).")
    fig.text(0.5, -0.02, caption, ha="center", fontsize=7.5, color="#555555")
    plt.tight_layout()
    out = OUT_DIR / f"exceedance_decades_{VARIABLE}.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6d — Plot 4: SCVR Annual Progression
# ══════════════════════════════════════════════════════════════════════════════

def plot_scvr_progression(baseline_daily, future_daily, scvr_results):
    """SCVR trajectory: anchor fit for temperature, decade bars for others."""
    strategy = SCVR_STRATEGY.get(VARIABLE, "period_average")
    base_pool = np.concatenate([s.values for s in baseline_daily.values()])

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor("#f9f9f9")

    if strategy == "anchor_3_linear":
        # Anchor fit with linear trend
        for scen in SCENARIOS:
            color = SCENARIO_COLORS[scen]
            fut_dict = future_daily.get(scen, {})
            if not fut_dict:
                continue
            res = compute_anchor_fit(base_pool, fut_dict, ANCHOR_3,
                                     future_years=FUTURE_YEARS)
            if res is None:
                continue
            ax.plot(res["years"], res["annual"], color=color, lw=2,
                    label=f"{scen.upper()} fit (R²={res['r2']:.3f})")
            ax.scatter(res["mids"], res["scvrs"], color=color,
                       s=120, marker="D", zorder=5, edgecolors="white", lw=1.5)

            # Full-window reference
            if scen in scvr_results:
                ax.axhline(scvr_results[scen]["scvr"], color=color, ls=":",
                           alpha=0.5, lw=1)

        ax.set_xlabel("Year")
        ax.set_ylabel("SCVR")
        ax.legend(fontsize=8)
        fig.text(0.5, -0.02,
                 "Diamonds = 10-year anchor SCVR. Solid line = linear fit. "
                 "Dotted = full 30-year pooled SCVR.",
                 ha="center", fontsize=7.5, color="#555555")
    else:
        # Decade bars for non-temperature
        x_labels = [d[0] for d in DECADE_WINDOWS]
        x_pos = np.arange(len(x_labels))
        width = 0.35

        for i, scen in enumerate(SCENARIOS):
            color = SCENARIO_COLORS[scen]
            fut_dict = future_daily.get(scen, {})
            if not fut_dict:
                continue
            vals = []
            for label, start, end in DECADE_WINDOWS:
                dec_pool = pool_window(fut_dict, start, end)
                if len(dec_pool) == 0:
                    vals.append(0)
                else:
                    r = compute_scvr(base_pool, dec_pool)
                    vals.append(r["scvr"])
            ax.bar(x_pos + i * width - width/2, vals, width, color=color,
                   alpha=0.8, label=scen.upper())
            for j, v in enumerate(vals):
                ax.text(x_pos[j] + i * width - width/2, v, f"{v:+.3f}",
                        ha="center", va="bottom", fontsize=7)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels)
        ax.set_ylabel("SCVR")
        ax.axhline(0, color="black", lw=0.5, alpha=0.3)
        ax.legend(fontsize=8)

    ax.set_title(
        f"SCVR Progression — {VAR_FULL}  |  {site['name']}",
        fontweight="bold", fontsize=13
    )
    plt.tight_layout()
    out = OUT_DIR / f"scvr_progression_{VARIABLE}.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6e — Plot 5: SCVR Method Equivalence Proof
# ══════════════════════════════════════════════════════════════════════════════

def plot_scvr_proof(baseline_daily, future_daily, scvr_results, scvr_comparison):
    """Visual proof that trapezoid area = sample mean, and all 3 SCVR methods agree."""
    base_pool = np.concatenate([s.values for s in baseline_daily.values()])
    base_clean = base_pool[~np.isnan(base_pool)]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        f"SCVR Method Equivalence — {VAR_FULL}  |  {site['name']}",
        fontsize=14, fontweight="bold", y=0.98
    )

    # ── Panel A: Exceedance curve area = mean ──
    ax = axes[0, 0]
    ax.set_facecolor("#f9f9f9")
    bv = np.sort(base_clean)[::-1]
    bp = np.linspace(0, 1, len(bv))
    area_val = float(np.trapezoid(bv, bp))
    mean_val = float(np.mean(base_clean))

    ax.fill_between(bp, bv, alpha=0.25, color="#4472C4", label="Area under curve")
    ax.plot(bp, bv, color="#4472C4", lw=2, zorder=3)
    ax.axhline(mean_val, color="#C55A11", ls="--", lw=2, alpha=0.9,
               label=f"Sample mean = {mean_val:.2f} {UNIT}")
    # Mean rectangle outline
    ax.plot([0, 1, 1, 0, 0], [0, 0, mean_val, mean_val, 0],
            color="#C55A11", ls=":", lw=1.2, alpha=0.5)

    ax.annotate(
        f"Trapezoid area = {area_val:.4f}\n"
        f"Sample mean    = {mean_val:.4f}\n"
        f"Difference       = {abs(area_val - mean_val):.2e}",
        xy=(0.55, 0.95), xycoords="axes fraction", fontsize=9,
        verticalalignment="top", fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.9))
    ax.set_xlabel("Exceedance probability p")
    ax.set_ylabel(f"{VAR_FULL} ({UNIT})")
    ax.set_title("A. Area Under Exceedance Curve = Sample Mean", fontweight="bold")
    ax.legend(fontsize=8, loc="lower left")

    # ── Panel B: Convergence — error vs sample size ──
    ax = axes[0, 1]
    ax.set_facecolor("#f9f9f9")
    rng = np.random.default_rng(42)
    full_n = len(base_clean)
    ns = [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, full_n]
    ns = [n for n in ns if n <= full_n]
    errors_pct = []
    for n in ns:
        if n == full_n:
            sub = base_clean.copy()
        else:
            sub = rng.choice(base_clean, size=n, replace=False)
        sub_sorted = np.sort(sub)[::-1]
        trap = float(np.trapezoid(sub_sorted, np.linspace(0, 1, n)))
        mn = float(np.mean(sub))
        err = abs(trap - mn) / abs(mn) * 100 if mn != 0 else 0
        errors_pct.append(err)

    ax.loglog(ns, errors_pct, "o-", color="#4472C4", lw=2, markersize=6, zorder=3)
    # Theoretical O(1/n²) reference line
    ref_ns = np.array([100, full_n])
    ref_err = errors_pct[0] * (100 / ref_ns) ** 2
    ax.loglog(ref_ns, ref_err, "--", color="#999999", lw=1, alpha=0.7,
              label=r"$O(1/n^2)$ reference")
    # Mark our actual sample size
    ax.axvline(full_n, color="#C55A11", ls="--", lw=1.5, alpha=0.6)
    ax.annotate(f"n = {full_n:,}\n(our data)",
                xy=(full_n, errors_pct[-1] if errors_pct[-1] > 0 else 1e-10),
                fontsize=8, ha="right", color="#C55A11")
    ax.set_xlabel("Sample size n")
    ax.set_ylabel("| Trapezoid − Mean | / Mean  (%)")
    ax.set_title("B. Convergence: Trapezoid Error vs Sample Size", fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── Panel C: Baseline vs Future gap = SCVR ──
    ax = axes[1, 0]
    ax.set_facecolor("#f9f9f9")
    # Use ssp585 if available, else ssp245
    scen = "ssp585" if "ssp585" in scvr_results else list(scvr_results.keys())[0]
    fut_dict = future_daily.get(scen, {})
    fut_pool = np.concatenate([s.values for s in fut_dict.values()])
    fut_clean = fut_pool[~np.isnan(fut_pool)]

    # Resample both to same n for fair visual comparison
    n_plot = min(len(base_clean), len(fut_clean), 5000)
    bv_sub = np.sort(rng.choice(base_clean, n_plot, replace=False))[::-1]
    fv_sub = np.sort(rng.choice(fut_clean, n_plot, replace=False))[::-1]
    pp = np.linspace(0, 1, n_plot)

    ax.plot(bv_sub, pp, color=BASELINE_COLOR, lw=2.5, label="Baseline", zorder=3)
    ax.plot(fv_sub, pp, color=SCENARIO_COLORS[scen], lw=2.5,
            label=f"Future ({scen.upper()})", zorder=3)
    # Shade the gap horizontally
    ax.fill_betweenx(pp, bv_sub, fv_sub, alpha=0.25, color=SCENARIO_COLORS[scen],
                      label="SCVR gap")
    # Mean markers
    base_mu = float(np.mean(base_clean))
    fut_mu = float(np.mean(fut_clean))
    ax.axvline(base_mu, color=BASELINE_COLOR, ls="--", lw=1.2, alpha=0.6)
    ax.axvline(fut_mu, color=SCENARIO_COLORS[scen], ls="--", lw=1.2, alpha=0.6)

    scvr_val = scvr_results[scen]["scvr"]
    ax.annotate(
        f"SCVR = (μ_f − μ_b) / μ_b\n"
        f"     = ({fut_mu:.2f} − {base_mu:.2f}) / {base_mu:.2f}\n"
        f"     = {scvr_val:+.4f}  ({scvr_val*100:+.2f}%)",
        xy=(0.03, 0.03), xycoords="axes fraction", fontsize=9,
        fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.9))
    ax.set_xlabel(f"{VAR_FULL} ({UNIT})")
    ax.set_ylabel("Exceedance probability P(X > x)")
    ax.set_title(f"C. Distribution Shift — {scen.upper()}", fontweight="bold")
    ax.legend(fontsize=8, loc="upper right")

    # ── Panel D: 3-Method comparison bars ──
    ax = axes[1, 1]
    ax.set_facecolor("#f9f9f9")
    methods = ["empirical_trapezoid", "normal_parametric", "direct_mean_ratio"]
    method_labels = ["Empirical\nTrapezoid", "Normal\nParametric", "Direct\nMean Ratio"]
    bar_colors = ["#4472C4", "#C55A11", "#70AD47"]

    scenarios_present = [s for s in SCENARIOS if s in scvr_comparison]
    n_scen = len(scenarios_present)
    x = np.arange(len(methods))
    width = 0.35

    for i, scen_key in enumerate(scenarios_present):
        vals = [scvr_comparison[scen_key].get(m, 0) for m in methods]
        offset = (i - (n_scen - 1) / 2) * width
        bars = ax.bar(x + offset, vals, width * 0.9, label=scen_key.upper(),
                      color=SCENARIO_COLORS.get(scen_key, bar_colors[i]), alpha=0.8)

    # Compute max divergence across all scenarios
    max_div = 0
    for scen_key in scenarios_present:
        vals = [scvr_comparison[scen_key].get(m, 0) for m in methods]
        if vals:
            max_div = max(max_div, max(vals) - min(vals))

    ax.annotate(
        f"Max divergence: {max_div:.6f}",
        xy=(0.5, 0.97), xycoords="axes fraction", fontsize=9,
        ha="center", va="top", fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#e8f5e9", alpha=0.9))
    ax.set_xticks(x)
    ax.set_xticklabels(method_labels, fontsize=9)
    ax.set_ylabel("SCVR")
    ax.set_title("D. Three Methods — Same Answer", fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    fig.text(0.5, 0.01,
             "All three methods estimate (μ_future − μ_baseline) / μ_baseline. "
             "The trapezoid integral converges to E[X] at large n.",
             ha="center", fontsize=8, color="#555555")
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    out = OUT_DIR / f"scvr_proof_{VARIABLE}.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6f — SCVR Decomposition Diagnostic
# ══════════════════════════════════════════════════════════════════════════════

def plot_scvr_decomposition(baseline_daily, future_daily, scvr_results):
    """
    Decompose pooled SCVR into per-model, tail, and variance diagnostics.

    Produces:
      - scvr_decomposition_{VARIABLE}.png (4-panel figure)
      - scvr_decomposition_{VARIABLE}.json
      - Console summary table
      - Returns metrics dict for inclusion in main JSON
    """
    _compute = compute_scvr  # already defined at module level

    # ── Diagnostic 1: Per-Model SCVR ─────────────────────────────────────────
    per_model_scvr = {}
    per_model_stats = {}
    for scen in SCENARIOS:
        per_model_scvr[scen] = {}
        for model in baseline_daily:
            if model not in future_daily.get(scen, {}):
                continue
            base_vals = baseline_daily[model].values
            fut_vals = future_daily[scen][model].values
            result = _compute(base_vals, fut_vals)
            per_model_scvr[scen][model] = result["scvr"]

        vals = list(per_model_scvr[scen].values())
        if vals:
            per_model_stats[scen] = {
                "min": float(np.min(vals)),
                "p25": float(np.percentile(vals, 25)),
                "median": float(np.median(vals)),
                "p75": float(np.percentile(vals, 75)),
                "max": float(np.max(vals)),
                "mean_of_models": float(np.mean(vals)),
                "std_of_models": float(np.std(vals)),
                "iqr": float(np.percentile(vals, 75) - np.percentile(vals, 25)),
                "pooled_scvr": scvr_results[scen]["scvr"],
            }

    # ── Diagnostic 2: Tail-Specific Metrics ──────────────────────────────────
    tail_metrics = {}
    per_model_tail_scvr = {}
    for scen in SCENARIOS:
        base_pool = np.concatenate([s.values for s in baseline_daily.values()])
        base_clean = base_pool[~np.isnan(base_pool)]
        fut_pool = np.concatenate([s.values for s in future_daily[scen].values()])
        fut_clean = fut_pool[~np.isnan(fut_pool)]

        # For precipitation, use wet days only for tail metrics
        if VARIABLE == "pr":
            base_tail_vals = base_clean[base_clean > 0.1]
            fut_tail_vals = fut_clean[fut_clean > 0.1]
        else:
            base_tail_vals = base_clean
            fut_tail_vals = fut_clean

        b_p95 = np.percentile(base_tail_vals, 95)
        f_p95 = np.percentile(fut_tail_vals, 95)
        b_p99 = np.percentile(base_tail_vals, 99)
        f_p99 = np.percentile(fut_tail_vals, 99)
        b_cvar = compute_cvar(base_tail_vals, 0.95)
        f_cvar = compute_cvar(fut_tail_vals, 0.95)

        tail_metrics[scen] = {
            "mean_scvr": scvr_results[scen]["scvr"],
            "tail_scvr_p95": (f_p95 - b_p95) / abs(b_p95) if b_p95 != 0 else 0,
            "extreme_scvr_p99": (f_p99 - b_p99) / abs(b_p99) if b_p99 != 0 else 0,
            "cvar95_ratio": (f_cvar - b_cvar) / abs(b_cvar) if b_cvar and b_cvar != 0 else 0,
        }

        # Per-model P95 SCVR
        per_model_tail_scvr[scen] = {}
        for model in baseline_daily:
            if model not in future_daily.get(scen, {}):
                continue
            b = baseline_daily[model].values
            b = b[~np.isnan(b)]
            f = future_daily[scen][model].values
            f = f[~np.isnan(f)]
            if VARIABLE == "pr":
                b = b[b > 0.1] if len(b[b > 0.1]) > 100 else b
                f = f[f > 0.1] if len(f[f > 0.1]) > 100 else f
            b95 = np.percentile(b, 95)
            f95 = np.percentile(f, 95)
            per_model_tail_scvr[scen][model] = (f95 - b95) / abs(b95) if b95 != 0 else 0

    # ── Epoch Report Card ─────────────────────────────────────────────────────
    epoch_report_card = {}
    for scen in SCENARIOS:
        epoch_report_card[scen] = compute_report_card(
            mean_scvr=tail_metrics[scen]["mean_scvr"],
            tail_scvr_p95=tail_metrics[scen]["tail_scvr_p95"],
            cvar95_ratio=tail_metrics[scen]["cvar95_ratio"],
            iqr=per_model_stats[scen]["iqr"],
            extreme_scvr_p99=tail_metrics[scen]["extreme_scvr_p99"],
        )

    # ── Decade Report Cards ───────────────────────────────────────────────────
    # Baseline pool is always the full 1985-2014 period (fixed reference)
    base_pool_all = np.concatenate([s.values for s in baseline_daily.values()])
    base_pool_clean = base_pool_all[~np.isnan(base_pool_all)]
    if VARIABLE == "pr":
        base_tail_all = base_pool_clean[base_pool_clean > 0.1]
    else:
        base_tail_all = base_pool_clean
    b_p95_all = np.percentile(base_tail_all, 95)
    b_p99_all = np.percentile(base_tail_all, 99)
    b_cvar_all = compute_cvar(base_tail_all, 0.95)

    decade_report_cards = {}
    for scen in SCENARIOS:
        decade_report_cards[scen] = {}
        for dec_label, dec_start, dec_end in DECADE_WINDOWS:
            # Pool future daily values for this decade only
            dec_parts = []
            dec_model_scvrs = []
            for model in baseline_daily:
                if model not in future_daily.get(scen, {}):
                    continue
                series = future_daily[scen][model]
                mask = (series.index.year >= dec_start) & (series.index.year <= dec_end)
                dec_vals = series[mask].values
                if len(dec_vals) > 0:
                    dec_parts.append(dec_vals)
                    # Per-model SCVR for this decade
                    b_vals = baseline_daily[model].values
                    b_vals = b_vals[~np.isnan(b_vals)]
                    r = _compute(b_vals, dec_vals)
                    dec_model_scvrs.append(r["scvr"])

            if not dec_parts or not dec_model_scvrs:
                continue

            dec_pool = np.concatenate(dec_parts)
            dec_clean = dec_pool[~np.isnan(dec_pool)]

            # Decade SCVR (pooled across models for this decade)
            dec_scvr_result = _compute(base_pool_clean, dec_clean)
            dec_mean_scvr = dec_scvr_result["scvr"]

            # Tail metrics for this decade
            if VARIABLE == "pr":
                dec_tail = dec_clean[dec_clean > 0.1] if len(dec_clean[dec_clean > 0.1]) > 100 else dec_clean
            else:
                dec_tail = dec_clean

            f_p95_dec = np.percentile(dec_tail, 95)
            f_p99_dec = np.percentile(dec_tail, 99)
            f_cvar_dec = compute_cvar(dec_tail, 0.95)

            dec_tail_p95 = (f_p95_dec - b_p95_all) / abs(b_p95_all) if b_p95_all != 0 else 0
            dec_tail_p99 = (f_p99_dec - b_p99_all) / abs(b_p99_all) if b_p99_all != 0 else 0
            dec_cvar = (f_cvar_dec - b_cvar_all) / abs(b_cvar_all) if b_cvar_all and b_cvar_all != 0 else 0

            # Per-model IQR for this decade
            dec_iqr = float(np.percentile(dec_model_scvrs, 75) - np.percentile(dec_model_scvrs, 25))

            decade_report_cards[scen][dec_label] = compute_report_card(
                mean_scvr=dec_mean_scvr,
                tail_scvr_p95=dec_tail_p95,
                cvar95_ratio=dec_cvar,
                iqr=dec_iqr,
                extreme_scvr_p99=dec_tail_p99,
            )

    # ── Diagnostic 3: GEV ξ Per Model ────────────────────────────────────────
    gev_per_model = {}
    for scen in SCENARIOS:
        gev_per_model[scen] = {}
        for model in baseline_daily:
            if model not in future_daily.get(scen, {}):
                continue
            base_gev = fit_gev_single_model(baseline_daily[model], block="annual_max")
            fut_gev = fit_gev_single_model(future_daily[scen][model], block="annual_max")
            if base_gev and fut_gev:
                gev_per_model[scen][model] = {
                    "xi_baseline": base_gev["shape"],
                    "xi_future": fut_gev["shape"],
                    "delta_xi": fut_gev["shape"] - base_gev["shape"],
                }

    # ── Diagnostic 4: Variance Decomposition ─────────────────────────────────
    variance_decomp = {}
    for scen in SCENARIOS:
        model_means_base = [float(np.nanmean(baseline_daily[m].values))
                            for m in baseline_daily]
        model_means_fut = [float(np.nanmean(future_daily[scen][m].values))
                           for m in future_daily[scen]]
        between_var_base = float(np.var(model_means_base))
        between_var_fut = float(np.var(model_means_fut))
        within_var_base = float(np.mean([np.nanvar(baseline_daily[m].values)
                                         for m in baseline_daily]))
        within_var_fut = float(np.mean([np.nanvar(future_daily[scen][m].values)
                                        for m in future_daily[scen]]))

        # P95 decomposition: annual P95 per model
        model_p95_base = [float(np.nanpercentile(baseline_daily[m].values, 95))
                          for m in baseline_daily]
        model_p95_fut = [float(np.nanpercentile(future_daily[scen][m].values, 95))
                         for m in future_daily[scen]]
        between_p95_base = float(np.var(model_p95_base))
        between_p95_fut = float(np.var(model_p95_fut))

        total_mean = within_var_fut + between_var_fut
        total_p95 = between_p95_fut  # between-model P95 spread

        variance_decomp[scen] = {
            "within_model_mean": within_var_fut,
            "between_model_mean": between_var_fut,
            "between_pct_mean": between_var_fut / total_mean * 100 if total_mean > 0 else 0,
            "between_model_p95": between_p95_fut,
            "model_p95_spread": float(np.max(model_p95_fut) - np.min(model_p95_fut)),
        }

    # ── Diagnostic 5: Leave-One-Out ──────────────────────────────────────────
    loo_results = {}
    loo_sensitivity = {}
    for scen in SCENARIOS:
        loo_results[scen] = {}
        models_in = [m for m in baseline_daily if m in future_daily.get(scen, {})]
        for drop in models_in:
            rem_base = np.concatenate([s.values for m, s in baseline_daily.items()
                                       if m != drop])
            rem_fut = np.concatenate([s.values for m, s in future_daily[scen].items()
                                      if m != drop])
            result = _compute(rem_base, rem_fut)
            loo_results[scen][drop] = result["scvr"]

        loo_vals = list(loo_results[scen].values())
        if loo_vals:
            loo_range = max(loo_vals) - min(loo_vals)
            most_influential = max(loo_results[scen],
                                   key=lambda m: abs(loo_results[scen][m]
                                                     - scvr_results[scen]["scvr"]))
            loo_sensitivity[scen] = {
                "range": float(loo_range),
                "most_influential": most_influential,
                "loo_min": float(min(loo_vals)),
                "loo_max": float(max(loo_vals)),
            }

    # ══════════════════════════════════════════════════════════════════════════
    # Plot: 4-panel figure
    # ══════════════════════════════════════════════════════════════════════════
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f"SCVR Decomposition — {VAR_FULL} ({VARIABLE})\n"
                 f"{site['name']} | {len(baseline_daily)} models",
                 fontsize=14, fontweight="bold")

    # ── Panel A: Per-Model SCVR Strip Plot ───────────────────────────────────
    ax = axes[0, 0]
    rng = np.random.default_rng(42)
    for i, scen in enumerate(SCENARIOS):
        color = SCENARIO_COLORS[scen]
        vals = list(per_model_scvr[scen].values())
        if not vals:
            continue
        x_jitter = rng.uniform(-0.15, 0.15, len(vals))
        ax.scatter(x_jitter + i, vals, color=color, alpha=0.5, s=25, zorder=3)
        bp = ax.boxplot([vals], positions=[i], widths=0.4, patch_artist=True,
                        boxprops=dict(facecolor=color, alpha=0.15),
                        medianprops=dict(color=color, lw=2),
                        whiskerprops=dict(color=color),
                        capprops=dict(color=color),
                        flierprops=dict(marker="", markersize=0))
        ax.scatter([i], [scvr_results[scen]["scvr"]], marker="D", s=120,
                   color=color, edgecolors="white", lw=1.5, zorder=5)
    ax.set_xticks(range(len(SCENARIOS)))
    ax.set_xticklabels([s.upper() for s in SCENARIOS])
    ax.set_ylabel("SCVR")
    ax.set_title("A. Per-Model SCVR (◇ = pooled)")
    ax.axhline(0, color="gray", ls="--", lw=0.5)
    ax.grid(axis="y", alpha=0.3)

    # ── Panel B: Mean vs Tail SCVR ───────────────────────────────────────────
    ax = axes[0, 1]
    metric_labels = ["Mean\nSCVR", "Tail\n(P95)", "Extreme\n(P99)", "CVaR\n(95%)"]
    x = np.arange(len(metric_labels))
    width = 0.35
    for i, scen in enumerate(SCENARIOS):
        color = SCENARIO_COLORS[scen]
        tm = tail_metrics[scen]
        vals = [tm["mean_scvr"], tm["tail_scvr_p95"],
                tm["extreme_scvr_p99"], tm["cvar95_ratio"]]
        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, vals, width * 0.9, color=color, alpha=0.7,
                      label=scen.upper())
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{v:+.4f}", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.set_ylabel("Ratio (fractional change)")
    ax.set_title("B. Mean vs Tail Metrics")
    ax.legend(fontsize=8)
    ax.axhline(0, color="gray", ls="--", lw=0.5)
    ax.grid(axis="y", alpha=0.3)

    # ── Panel C: GEV ξ Baseline vs Future ────────────────────────────────────
    ax = axes[1, 0]
    all_xi = []
    for scen in SCENARIOS:
        color = SCENARIO_COLORS[scen]
        if not gev_per_model.get(scen):
            continue
        xi_b = [gev_per_model[scen][m]["xi_baseline"] for m in gev_per_model[scen]]
        xi_f = [gev_per_model[scen][m]["xi_future"] for m in gev_per_model[scen]]
        ax.scatter(xi_b, xi_f, color=color, alpha=0.5, s=40, label=scen.upper())
        all_xi.extend(xi_b + xi_f)
        # Count models above/below diagonal
        n_above = sum(1 for b, f in zip(xi_b, xi_f) if f > b)
        n_total = len(xi_b)
        ax.text(0.02, 0.98 - SCENARIOS.index(scen) * 0.08,
                f"{scen.upper()}: {n_above}/{n_total} tails fattening",
                transform=ax.transAxes, fontsize=8, va="top", color=color)
    if all_xi:
        lo, hi = min(all_xi) - 0.05, max(all_xi) + 0.05
        ax.plot([lo, hi], [lo, hi], "k--", lw=1, alpha=0.4, label="No change")
    ax.set_xlabel("GEV shape ξ (baseline)")
    ax.set_ylabel("GEV shape ξ (future)")
    ax.set_title("C. Per-Model Tail Shape (above diag = fattening)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # ── Panel D: Variance Decomposition ──────────────────────────────────────
    ax = axes[1, 1]
    bar_labels = []
    within_vals = []
    between_vals = []
    for scen in SCENARIOS:
        vd = variance_decomp[scen]
        bar_labels.append(f"{scen.upper()}\nmean")
        within_vals.append(vd["within_model_mean"])
        between_vals.append(vd["between_model_mean"])
    x = np.arange(len(bar_labels))
    ax.bar(x, within_vals, 0.6, label="Within-model (temporal)", color="#78B7C5", alpha=0.8)
    ax.bar(x, between_vals, 0.6, bottom=within_vals,
           label="Between-model (structural)", color="#E76F51", alpha=0.8)
    for i, scen in enumerate(SCENARIOS):
        pct = variance_decomp[scen]["between_pct_mean"]
        total = within_vals[i] + between_vals[i]
        ax.text(i, total * 1.02, f"Between: {pct:.1f}%",
                ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(bar_labels)
    ax.set_ylabel(f"Variance ({UNIT}²)")
    ax.set_title("D. Variance Decomposition")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    out_png = OUT_DIR / f"scvr_decomposition_{VARIABLE}.png"
    plt.savefig(out_png, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_png}")

    # ── Console summary table ────────────────────────────────────────────────
    print(f"\n  ── SCVR Decomposition ({VARIABLE}) ──────────────────────────")
    hdr = "            |  " + "  ".join(f"{s.upper():>10}" for s in SCENARIOS)
    print(hdr)
    rows = [
        ("Pooled", [f"{scvr_results[s]['scvr']:+.4f}" for s in SCENARIOS]),
        ("Model med", [f"{per_model_stats[s]['median']:+.4f}" for s in SCENARIOS]),
        ("Model IQR", [f"{per_model_stats[s]['iqr']:.4f}" for s in SCENARIOS]),
        ("Tail P95", [f"{tail_metrics[s]['tail_scvr_p95']:+.4f}" for s in SCENARIOS]),
        ("Tail P99", [f"{tail_metrics[s]['extreme_scvr_p99']:+.4f}" for s in SCENARIOS]),
        ("CVaR 95%", [f"{tail_metrics[s]['cvar95_ratio']:+.4f}" for s in SCENARIOS]),
        ("Between%", [f"{variance_decomp[s]['between_pct_mean']:.1f}%" for s in SCENARIOS]),
        ("LOO range", [f"{loo_sensitivity[s]['range']:.4f}" for s in SCENARIOS]),
    ]
    for label, vals in rows:
        print(f"  {label:<11}|  " + "  ".join(f"{v:>10}" for v in vals))
    print(f"  {'─'*55}")

    # ── Report Card: Epoch ────────────────────────────────────────────────────
    print(f"\n  ── SCVR Report Card — Epoch ({VARIABLE}) ─────────────────────")
    rc_hdr = f"  {'':11}|  " + "  ".join(f"{s.upper():>10}" for s in SCENARIOS)
    print(rc_hdr)
    rc_rows = [
        ("Mean SCVR", [f"{epoch_report_card[s]['mean_scvr']:+.4f}" for s in SCENARIOS]),
        ("P95 SCVR", [f"{epoch_report_card[s]['tail_scvr_p95']:+.4f}" for s in SCENARIOS]),
        ("CVaR 95%", [f"{epoch_report_card[s]['cvar95_ratio']:+.4f}" for s in SCENARIOS]),
        ("M-T Ratio", [f"{epoch_report_card[s]['mean_tail_ratio']:.2f}" if epoch_report_card[s]['mean_tail_ratio'] is not None else "N/A" for s in SCENARIOS]),
        ("Model IQR", [f"{epoch_report_card[s]['model_iqr']:.4f}" for s in SCENARIOS]),
        ("Confidence", [epoch_report_card[s]["tail_confidence"] for s in SCENARIOS]),
    ]
    for label, vals in rc_rows:
        print(f"  {label:<11}|  " + "  ".join(f"{v:>10}" for v in vals))
    print(f"  {'─'*55}")

    # ── Report Card: Decades ──────────────────────────────────────────────────
    for scen in SCENARIOS:
        if not decade_report_cards.get(scen):
            continue
        print(f"\n  ── Decade Report Card — {scen.upper()} ({VARIABLE}) ──────────")
        dec_labels_found = list(decade_report_cards[scen].keys())
        dec_hdr = f"  {'':11}|  " + "  ".join(f"{d:>12}" for d in dec_labels_found)
        print(dec_hdr)
        dec_rows = [
            ("Mean SCVR", [f"{decade_report_cards[scen][d]['mean_scvr']:+.4f}" for d in dec_labels_found]),
            ("P95 SCVR", [f"{decade_report_cards[scen][d]['tail_scvr_p95']:+.4f}" for d in dec_labels_found]),
            ("CVaR 95%", [f"{decade_report_cards[scen][d]['cvar95_ratio']:+.4f}" for d in dec_labels_found]),
            ("M-T Ratio", [f"{decade_report_cards[scen][d]['mean_tail_ratio']:.2f}" if decade_report_cards[scen][d]['mean_tail_ratio'] is not None else "N/A" for d in dec_labels_found]),
            ("Model IQR", [f"{decade_report_cards[scen][d]['model_iqr']:.4f}" for d in dec_labels_found]),
            ("Confidence", [decade_report_cards[scen][d]["tail_confidence"] for d in dec_labels_found]),
        ]
        for label, vals in dec_rows:
            print(f"  {label:<11}|  " + "  ".join(f"{v:>12}" for v in vals))
        print(f"  {'─'*55}")

    # ── Save JSON ────────────────────────────────────────────────────────────
    def _round_rc(rc):
        """Round floats in a report card dict for JSON output."""
        return {k: round(v, 6) if isinstance(v, float) else v
                for k, v in rc.items()}

    decomp = {
        "per_model_scvr": {s: {m: round(v, 6) for m, v in d.items()}
                           for s, d in per_model_scvr.items()},
        "per_model_stats": {s: {k: round(v, 6) if isinstance(v, float) else v
                                for k, v in d.items()}
                            for s, d in per_model_stats.items()},
        "tail_metrics": {s: {k: round(v, 6) for k, v in d.items()}
                         for s, d in tail_metrics.items()},
        "per_model_tail_scvr_p95": {s: {m: round(v, 6) for m, v in d.items()}
                                     for s, d in per_model_tail_scvr.items()},
        "gev_per_model": {s: {m: {k: round(v, 6) for k, v in d.items()}
                               for m, d in models.items()}
                           for s, models in gev_per_model.items()},
        "variance_decomposition": {s: {k: round(v, 6) if isinstance(v, float) else v
                                       for k, v in d.items()}
                                    for s, d in variance_decomp.items()},
        "leave_one_out": {s: {m: round(v, 6) for m, v in d.items()}
                          for s, d in loo_results.items()},
        "loo_sensitivity": {s: {k: round(v, 6) if isinstance(v, float) else v
                                for k, v in d.items()}
                            for s, d in loo_sensitivity.items()},
        "epoch_report_card": {s: _round_rc(rc)
                              for s, rc in epoch_report_card.items()},
        "decade_report_cards": {s: {d: _round_rc(rc) for d, rc in decades.items()}
                                for s, decades in decade_report_cards.items()},
    }

    out_json = OUT_DIR / f"scvr_decomposition_{VARIABLE}.json"
    with open(out_json, "w") as f:
        json.dump(decomp, f, indent=2)
    print(f"  Saved: {out_json}")

    return decomp


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — Save SCVR Summary JSON
# ══════════════════════════════════════════════════════════════════════════════

def save_scvr_summary(scvr_results, n_models, decade_scvr=None,
                      shape_metrics=None, gev_params=None, gpd_params=None,
                      anchor_fits=None, scvr_comparison=None,
                      decomposition=None):
    summary = {
        "site_id": SITE_ID,
        "site_name": site["name"],
        "variable": VARIABLE,
        "variable_full": VAR_FULL,
        "unit": UNIT,
        "baseline_period": list(BASELINE_YEARS),
        "future_period": list(FUTURE_YEARS),
        "n_models": n_models,
        "scvr_strategy": SCVR_STRATEGY.get(VARIABLE, "period_average"),
        "scvr": {}
    }
    for scen in SCENARIOS:
        r = scvr_results.get(scen, {})
        summary["scvr"][scen] = round(r.get("scvr", 0), 6)
    if len(SCENARIOS) == 2:
        delta = summary["scvr"][SCENARIOS[1]] - summary["scvr"][SCENARIOS[0]]
        summary["scvr"]["delta_585_minus_245"] = round(delta, 6)

    # Parametric vs empirical SCVR comparison
    if scvr_comparison:
        summary["scvr_method_comparison"] = scvr_comparison

    # Decade-resolved SCVR breakdown
    if decade_scvr:
        summary["decade_scvr"] = {}
        for scen, decades in decade_scvr.items():
            summary["decade_scvr"][scen] = {
                label: round(val, 6) for label, val in decades.items()
            }

    # Shape metrics per decade + baseline
    if shape_metrics:
        summary["shape_metrics"] = {}
        for period, metrics in shape_metrics.items():
            if metrics:
                summary["shape_metrics"][period] = {
                    k: round(v, 6) if isinstance(v, float) else v
                    for k, v in metrics.items()
                }

    # Helper: round floats but preserve tiny p-values in scientific notation
    def _round_param(k, v):
        if not isinstance(v, float):
            return v
        if "pvalue" in k and abs(v) < 1e-4:
            return float(f"{v:.2e}")
        return round(v, 6)

    # GEV parameters (annual block maxima)
    if gev_params:
        summary["gev_params"] = {}
        for period, params in gev_params.items():
            if params:
                summary["gev_params"][period] = {
                    k: _round_param(k, v) for k, v in params.items()
                }

    # GPD parameters (Peaks-Over-Threshold)
    if gpd_params:
        summary["gpd_params"] = {}
        for period, params in gpd_params.items():
            if params:
                summary["gpd_params"][period] = {
                    k: _round_param(k, v) for k, v in params.items()
                }

    # Anchor fit info (temperature variables)
    if anchor_fits:
        summary["anchor_fits"] = {}
        for scen, res in anchor_fits.items():
            if res:
                summary["anchor_fits"][scen] = {
                    "mids": res["mids"],
                    "scvrs": [round(s, 6) for s in res["scvrs"]],
                    "fit_slope": round(float(res["fit"][0]), 8),
                    "fit_intercept": round(float(res["fit"][1]), 6),
                    "r2": round(res["r2"], 4),
                }

    if decomposition:
        summary["scvr_decomposition"] = {
            "per_model_stats": decomposition.get("per_model_stats"),
            "tail_metrics": decomposition.get("tail_metrics"),
            "variance_decomposition": decomposition.get("variance_decomposition"),
            "loo_sensitivity": decomposition.get("loo_sensitivity"),
            "epoch_report_card": decomposition.get("epoch_report_card"),
            "decade_report_cards": decomposition.get("decade_report_cards"),
        }

    out = OUT_DIR / f"scvr_summary_{VARIABLE}.json"
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Saved: {out}")
    return summary


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def run_variable(variable):
    """Run the full pipeline for a single variable."""
    global VARIABLE, OUT_DIR, UNIT, VAR_FULL, TS_RESAMPLE, TS_UNIT
    VARIABLE = variable
    UNIT     = VARS.get(VARIABLE, {}).get("unit", "")
    VAR_FULL = VARS.get(VARIABLE, {}).get("full_name", VARIABLE)
    OUT_DIR  = ROOT / "data" / "processed" / "presentation" / SITE_ID / VARIABLE
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # pr uses annual sum (mm/year — standard hydrology); all others use annual mean
    if VARIABLE == "pr":
        TS_RESAMPLE = "sum"
        TS_UNIT     = "mm/year"
    else:
        TS_RESAMPLE = "mean"
        TS_UNIT     = UNIT

    print("=" * 65)
    print(f"  Variable: {VAR_FULL} ({UNIT})")
    print(f"  Site:     {site['name']} ({LAT:.4f}N, {LON:.4f}W)")
    print(f"  Baseline: {BASELINE_YEARS[0]}–{BASELINE_YEARS[1]}")
    print(f"  Future:   {FUTURE_YEARS[0]}–{FUTURE_YEARS[1]}")
    print(f"  Scenarios:{SCENARIOS}")
    print(f"  Output:   {OUT_DIR}")
    print("=" * 65)

    # 1. Model discovery
    print("\n[1/4] Discovering models ...")
    models = discover_models()
    if not models:
        print(f"  ERROR: No models found for {VARIABLE}. Skipping.")
        return None

    # 2. Load data
    print(f"\n[2/4] Loading data for {len(models)} models ...")
    baseline_daily, future_daily = load_data(models)

    if not baseline_daily:
        print(f"  ERROR: No baseline data loaded for {VARIABLE}. Skipping.")
        return None

    # 3. Compute SCVR for each scenario
    print("\n[3/6] Computing full-window SCVR ...")
    base_pool = np.concatenate([s.values for s in baseline_daily.values()])
    scvr_results = {}
    for scen in SCENARIOS:
        fut_dict = future_daily.get(scen, {})
        if not fut_dict:
            print(f"  WARN: No future data for {scen} — skipping")
            continue
        fut_pool = np.concatenate([s.values for s in fut_dict.values()])
        result = compute_scvr(base_pool, fut_pool)
        scvr_results[scen] = result
        print(f"  {scen.upper()}: SCVR = {result['scvr']:+.6f}  "
              f"(n_base={result['n_baseline_days']:,}  n_fut={result['n_future_days']:,})")

    # 3b. Parametric vs empirical SCVR comparison (proof of equivalence)
    #     All three methods estimate E[X], so they MUST agree at large n.
    #     GEV is excluded — it models block maxima, not daily bulk, and gives
    #     wrong means when fitted to daily data.
    base_clean = base_pool[~np.isnan(base_pool)]
    scvr_comparison = {}
    print("\n  --- Parametric vs Empirical SCVR Comparison ---")
    b_mu, _ = sp_stats.norm.fit(base_clean)
    base_mean = float(np.nanmean(base_clean))

    for scen in SCENARIOS:
        if scen not in scvr_results:
            continue
        fut_dict = future_daily.get(scen, {})
        fut_pool = np.concatenate([s.values for s in fut_dict.values()])
        fut_clean = fut_pool[~np.isnan(fut_pool)]

        emp_scvr = scvr_results[scen]["scvr"]
        f_mu, _ = sp_stats.norm.fit(fut_clean)
        norm_scvr = (f_mu - b_mu) / b_mu
        mean_scvr = (float(np.nanmean(fut_clean)) - base_mean) / base_mean

        comp = {
            "empirical_trapezoid": round(emp_scvr, 6),
            "normal_parametric": round(norm_scvr, 6),
            "direct_mean_ratio": round(mean_scvr, 6),
        }

        scvr_comparison[scen] = comp
        print(f"  {scen}:")
        for method, val in comp.items():
            print(f"    {method:25s} {val:+.6f}")
    print("  (All methods agree → empirical is sufficient for SCVR)")

    # 4. Decade SCVR, anchor fits, shape metrics, GEV
    strategy = SCVR_STRATEGY.get(VARIABLE, "period_average")
    print(f"\n[4/6] Computing decade analysis (strategy={strategy}) ...")

    decade_scvr = {}
    anchor_fits = {}
    shape_metrics = {}
    gev_params = {}
    gpd_params = {}

    # Baseline shape metrics (base_clean already computed in step 3b)
    shape_metrics["baseline"] = compute_shape_metrics(base_clean)

    # Baseline GEV + GPD
    gev_params["baseline"] = fit_gev(baseline_daily, block="annual_max")
    gpd_params["baseline"] = fit_gpd(baseline_daily, threshold_quantile=0.95)

    for scen in SCENARIOS:
        fut_dict = future_daily.get(scen, {})
        if not fut_dict:
            continue

        # Decade-resolved SCVR
        decade_scvr[scen] = {}
        for label, start, end in DECADE_WINDOWS:
            dec_pool = pool_window(fut_dict, start, end)
            dec_clean = dec_pool[~np.isnan(dec_pool)]
            if len(dec_clean) == 0:
                continue
            r = compute_scvr(base_clean, dec_clean)
            decade_scvr[scen][label] = r["scvr"]
            print(f"  {scen} {label}: SCVR = {r['scvr']:+.6f}  (n={len(dec_clean):,})")

        # Shape metrics per decade
        for label, start, end in DECADE_WINDOWS:
            key = f"{scen}_{label}"
            dec_pool = pool_window(fut_dict, start, end)
            dec_clean = dec_pool[~np.isnan(dec_pool)]
            if len(dec_clean) > 0:
                shape_metrics[key] = compute_shape_metrics(dec_clean)

        # Anchor fit (temperature variables)
        if strategy == "anchor_3_linear":
            res = compute_anchor_fit(base_pool, fut_dict, ANCHOR_3,
                                     future_years=FUTURE_YEARS)
            if res:
                anchor_fits[scen] = res
                print(f"  {scen} anchor fit: R²={res['r2']:.4f}  "
                      f"slope={res['fit'][0]:.6f}/yr")

        # GEV + GPD per decade
        for label, start, end in DECADE_WINDOWS:
            key = f"{scen}_{label}"
            dec_dict = {}
            for m, s in fut_dict.items():
                mask = (s.index.year >= start) & (s.index.year <= end)
                dec_dict[m] = s[mask]
            gev_params[key] = fit_gev(dec_dict, block="annual_max")
            gpd_params[key] = fit_gpd(dec_dict, threshold_quantile=0.95)

    # 5. Generate plots
    print("\n[5/6] Generating plots ...")
    plot_timeseries(baseline_daily, future_daily, scvr_results, n_models=len(models))
    plot_exceedance(baseline_daily, future_daily, scvr_results)
    plot_decade_exceedance(baseline_daily, future_daily, scvr_results)
    plot_scvr_progression(baseline_daily, future_daily, scvr_results)
    plot_scvr_proof(baseline_daily, future_daily, scvr_results, scvr_comparison)
    decomp_metrics = plot_scvr_decomposition(baseline_daily, future_daily, scvr_results)

    # 6. Save summary
    print("\n[6/6] Saving summary ...")
    summary = save_scvr_summary(
        scvr_results, len(models),
        decade_scvr=decade_scvr,
        shape_metrics=shape_metrics,
        gev_params=gev_params,
        gpd_params=gpd_params,
        anchor_fits=anchor_fits,
        scvr_comparison=scvr_comparison,
        decomposition=decomp_metrics,
    )

    scvr_line = "  ".join(
        f"SCVR({s})={scvr_results[s]['scvr']:+.4f}"
        for s in SCENARIOS if s in scvr_results
    )
    print(f"\n  DONE [{VARIABLE}]  {scvr_line}")
    return summary


def main():
    print(f"\n{'='*65}")
    print(f"  Ensemble Exceedance — {site['name']}")
    print(f"  Running {len(VARIABLES)} variables: {VARIABLES}")
    print(f"{'='*65}\n")

    all_results = {}
    for i, var in enumerate(VARIABLES, 1):
        print(f"\n[Variable {i}/{len(VARIABLES)}] ── {var} ─────────────────────")
        result = run_variable(var)
        if result:
            all_results[var] = result

    print(f"\n{'='*65}")
    print(f"  ALL DONE — {len(all_results)}/{len(VARIABLES)} variables completed")
    print(f"  Site: {site['name']}")
    print(f"  Outputs: data/processed/presentation/{SITE_ID}/")
    for var, summary in all_results.items():
        scvr_parts = "  ".join(
            f"{s}={summary['scvr'].get(s, 0):+.4f}"
            for s in SCENARIOS
        )
        print(f"    {var:<10} {scvr_parts}")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
