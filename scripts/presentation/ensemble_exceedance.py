"""
ensemble_exceedance.py
======================
Presentation-grade script that, for a given site + climate variable:

  1. Loads multi-model CMIP6 ensemble data from the existing .nc cache
     (or downloads via THREDDS NCSS if not cached yet)
  2. Plots annual P10 / P50 / P90 time series for baseline + two SSP scenarios
  3. Plots traditional exceedance curves  (x = value, y = exceedance probability)
     for baseline, SSP2-4.5, and SSP5-8.5
  4. Computes SCVR for each scenario and annotates it on the exceedance curve plot
  5. Saves all outputs to data/processed/presentation/<site>/<variable>/

Usage
-----
Edit the CONFIG block below, then run from the project root:

    python scripts/presentation/ensemble_exceedance.py

Outputs (in data/processed/presentation/<SITE_ID>/<VARIABLE>/):
    ensemble_timeseries_<var>.png   — annual P10/P50/P90 spaghetti + band
    exceedance_curves_<var>.png     — traditional exceedance curves + SCVR labels
    ensemble_stats_<var>.csv        — annual P10/P50/P90 per scenario (numerical)
    scvr_summary_<var>.json         — SCVR for SSP245, SSP585, delta
"""

# ── CONFIG — edit these to change what gets plotted ──────────────────────────
SITE_ID        = "hayhurst_solar"   # or "maverick_wind"
VARIABLES      = ["tasmax", "tasmin", "tas", "pr", "sfcWind", "hurs", "rsds"]
# VARIABLES    = ["tasmax"]         # uncomment to run a single variable
SCENARIOS      = ["ssp245", "ssp585"]
MAX_MODELS     = 6
BASELINE_YEARS = (1985, 2014)
FUTURE_YEARS   = (2026, 2055)
# ─────────────────────────────────────────────────────────────────────────────

import warnings
warnings.filterwarnings("ignore")

import json
import io
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

def build_thredds_url(model, scenario, variable, year, lat, lon):
    fname_v2 = f"{variable}_day_{model}_{scenario}_r1i1p1f1_gn_{year}_v2.0.nc"
    fname_v1 = f"{variable}_day_{model}_{scenario}_r1i1p1f1_gn_{year}.nc"
    base     = f"{THREDDS_NCSS}/{model}/{scenario}/r1i1p1f1/{variable}"
    params   = (f"?var={variable}&latitude={lat}&longitude={lon}"
                f"&time_start={year}-01-01T00:00:00Z"
                f"&time_end={year}-12-31T23:59:59Z&accept=netCDF")
    return f"{base}/{fname_v2}{params}", f"{base}/{fname_v1}{params}"


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

    url_v2, url_v1 = build_thredds_url(model, scenario, variable, year, lat, lon)
    for attempt in range(retries):
        for url in [url_v2, url_v1]:
            try:
                r = requests.get(url, timeout=60)
                if r.status_code == 200 and len(r.content) > 500:
                    cache_path.write_bytes(r.content)
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
    url_v2, url_v1 = build_thredds_url(model, scenario, variable,
                                        probe_year, lat, lon)
    for url in [url_v2, url_v1]:
        try:
            r = requests.head(url, timeout=15)
            if r.status_code == 200:
                return True
            r = requests.get(url, timeout=20, stream=True)
            if r.status_code == 200:
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

    models = sorted(hist_ok)[:MAX_MODELS]
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

def plot_timeseries(baseline_daily, future_daily, scvr_results):
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
        f"{VAR_FULL} — {site['name']}  |  Multi-Model Ensemble (up to {MAX_MODELS} models)",
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
# SECTION 7 — Save SCVR Summary JSON
# ══════════════════════════════════════════════════════════════════════════════

def save_scvr_summary(scvr_results, n_models):
    summary = {
        "site_id": SITE_ID,
        "site_name": site["name"],
        "variable": VARIABLE,
        "variable_full": VAR_FULL,
        "unit": UNIT,
        "baseline_period": list(BASELINE_YEARS),
        "future_period": list(FUTURE_YEARS),
        "n_models": n_models,
        "scvr": {}
    }
    for scen in SCENARIOS:
        r = scvr_results.get(scen, {})
        summary["scvr"][scen] = round(r.get("scvr", 0), 6)
    if len(SCENARIOS) == 2:
        delta = summary["scvr"][SCENARIOS[1]] - summary["scvr"][SCENARIOS[0]]
        summary["scvr"]["delta_585_minus_245"] = round(delta, 6)

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
    print("\n[3/4] Computing SCVR ...")
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

    # 4. Generate outputs
    print("\n[4/4] Generating plots and outputs ...")
    plot_timeseries(baseline_daily, future_daily, scvr_results)
    plot_exceedance(baseline_daily, future_daily, scvr_results)
    summary = save_scvr_summary(scvr_results, len(models))

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
