"""
annual_scvr_test.py
===================
Quick experiment: compute SCVR per-year vs anchor-based interpolation
using existing cached CMIP6 data. No THREDDS downloads needed.

Compares four methods:
  1. Per-year SCVR (each year's daily values vs full baseline)
  2. 3 non-overlapping 10-year anchors + linear fit
  3. 6 non-overlapping 5-year anchors + linear fit
  4. Full 30-year window (current NB03 approach)

Run from project root:
    python scripts/experiments/annual_scvr_test.py
"""

import warnings
warnings.filterwarnings("ignore")

import json, io, time, threading
import numpy as np
import pandas as pd
import xarray as xr
import cftime
import matplotlib.pyplot as plt
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── CONFIG ────────────────────────────────────────────────────────────────────
SITE_ID        = "hayhurst_solar"
VARIABLES      = ["tasmax", "tasmin", "tas", "pr", "sfcWind", "hurs", "rsds"]
SCENARIO       = "ssp585"
MAX_MODELS     = 6
BASELINE_YEARS = (1985, 2014)
FUTURE_YEARS   = (2026, 2055)
# ──────────────────────────────────────────────────────────────────────────────

ROOT       = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "data" / "schema"
CACHE_DIR  = ROOT / "data" / "cache" / "thredds"
OUT_DIR    = Path(__file__).resolve().parent / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(SCHEMA_DIR / "sites.json") as f:
    SITES = json.load(f)
site = SITES[SITE_ID]
LAT, LON = site["lat"], site["lon"]

ALL_MODELS = [
    "ACCESS-CM2","ACCESS-ESM1-5","BCC-CSM2-MR","CanESM5","CESM2",
    "CESM2-LENS","CMCC-CM2-SR5","CMCC-ESM2","CNRM-CM6-1","CNRM-ESM2-1",
    "EC-Earth3","EC-Earth3-Veg-LR","FGOALS-g3","GFDL-CM4","GFDL-CM4_gr2",
    "GFDL-ESM4","GISS-E2-1-G","HadGEM3-GC31-LL","HadGEM3-GC31-MM",
    "IITM-ESM","INM-CM4-8","INM-CM5-0","IPSL-CM6A-LR","KACE-1-0-G",
    "KIOST-ESM","MIROC6","MPI-ESM1-2-HR","MPI-ESM1-2-LR","MRI-ESM2-0",
    "NESM3","NorESM2-LM","NorESM2-MM","TaiESM1","UKESM1-0-LL",
]

THREDDS_NCSS = "https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Utility functions (from ensemble_exceedance.py)
# ══════════════════════════════════════════════════════════════════════════════

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
            times = pd.to_datetime([
                f"{d.year:04d}-{d.month:02d}-{d.day:02d}" for d in cf
            ])
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


def compute_scvr(baseline_values, future_values):
    b = np.sort(baseline_values[~np.isnan(baseline_values)])[::-1].astype(float)
    f = np.sort(future_values[~np.isnan(future_values)])[::-1].astype(float)
    exc_b = np.linspace(0, 1, len(b))
    exc_f = np.linspace(0, 1, len(f))
    area_b = float(np.trapezoid(b, exc_b))
    area_f = float(np.trapezoid(f, exc_f))
    scvr = (area_f - area_b) / area_b if area_b != 0 else 0.0
    return {"scvr": scvr, "area_baseline": area_b, "area_future": area_f,
            "n_baseline_days": len(b), "n_future_days": len(f)}


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Find models in cache (no probing needed)
# ══════════════════════════════════════════════════════════════════════════════

def find_cached_models(variable):
    """Find models that have cached .nc files for our site/variable/scenario."""
    models_with_data = set()
    test_year = 2040
    for model in ALL_MODELS:
        cache_key = f"{model}_{SCENARIO}_{variable}_{test_year}_{LAT:.4f}_{LON:.4f}.nc"
        if (CACHE_DIR / cache_key).exists():
            hist_key = f"{model}_historical_{variable}_2000_{LAT:.4f}_{LON:.4f}.nc"
            if (CACHE_DIR / hist_key).exists():
                models_with_data.add(model)
    models = sorted(models_with_data)[:MAX_MODELS]
    print(f"Found {len(models)} models in cache: {models}")
    return models


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Load data
# ══════════════════════════════════════════════════════════════════════════════

def load_all_data(models, variable):
    """Load baseline and future daily data per model. Returns per-model dicts."""
    baseline_daily = {}
    future_daily = {}

    for model in models:
        print(f"  Loading {model} ...", end=" ", flush=True)

        base = fetch_model_years(
            model, "historical", variable,
            range(BASELINE_YEARS[0], BASELINE_YEARS[1] + 1),
            LAT, LON, CACHE_DIR
        )
        if base is not None:
            baseline_daily[model] = unit_convert(base, variable)

        fut = fetch_model_years(
            model, SCENARIO, variable,
            range(FUTURE_YEARS[0], FUTURE_YEARS[1] + 1),
            LAT, LON, CACHE_DIR
        )
        if fut is not None:
            future_daily[model] = unit_convert(fut, variable)

        n_base = len(baseline_daily.get(model, []))
        n_fut = len(future_daily.get(model, []))
        print(f"baseline={n_base}, future={n_fut} days")

    return baseline_daily, future_daily


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Compute SCVR four ways
# ══════════════════════════════════════════════════════════════════════════════

def compute_all_methods(baseline_daily, future_daily):
    # Pool baseline (always full 30 years across all models)
    base_pool = np.concatenate([s.values for s in baseline_daily.values()])
    print(f"\nBaseline pool: {len(base_pool):,} daily values")

    years = list(range(FUTURE_YEARS[0], FUTURE_YEARS[1] + 1))

    # ── Method 1: Per-Year SCVR ──────────────────────────────────────────────
    print("\n--- Method 1: Per-Year SCVR ---")
    per_year = {}
    for yr in years:
        yr_vals = []
        for model, series in future_daily.items():
            mask = series.index.year == yr
            yr_vals.append(series[mask].values)
        yr_pool = np.concatenate(yr_vals)
        result = compute_scvr(base_pool, yr_pool)
        per_year[yr] = result["scvr"]

    per_year_arr = np.array([per_year[yr] for yr in years])
    print(f"  Values: min={per_year_arr.min():.4f}, max={per_year_arr.max():.4f}, "
          f"std={per_year_arr.std():.4f}, mean={per_year_arr.mean():.4f}")

    # ── Method 2: 3 Non-Overlapping Anchors (10-year windows) ────────────────
    print("\n--- Method 2: 3 Anchors (10-year) ---")
    anchors_3 = [
        (2026, 2035),
        (2036, 2045),
        (2046, 2055),
    ]
    anchor_3_scvr = []
    anchor_3_mid = []
    for start, end in anchors_3:
        window_vals = []
        for model, series in future_daily.items():
            mask = (series.index.year >= start) & (series.index.year <= end)
            window_vals.append(series[mask].values)
        window_pool = np.concatenate(window_vals)
        result = compute_scvr(base_pool, window_pool)
        mid = (start + end) / 2
        anchor_3_mid.append(mid)
        anchor_3_scvr.append(result["scvr"])
        print(f"  {start}-{end} (mid={mid:.0f}): SCVR={result['scvr']:.4f}  "
              f"({len(window_pool):,} values)")

    fit_3 = np.polyfit(anchor_3_mid, anchor_3_scvr, 1)
    annual_3 = np.polyval(fit_3, years)
    r2_3 = 1 - np.sum((np.array(anchor_3_scvr) - np.polyval(fit_3, anchor_3_mid))**2) / \
               np.sum((np.array(anchor_3_scvr) - np.mean(anchor_3_scvr))**2) if len(anchors_3) > 2 else 1.0
    print(f"  Linear fit: SCVR(t) = {fit_3[1]:.4f} + {fit_3[0]:.6f} * t")
    print(f"  R² = {r2_3:.4f}")

    # ── Method 3: 6 Non-Overlapping Anchors (5-year windows) ─────────────────
    print("\n--- Method 3: 6 Anchors (5-year) ---")
    anchors_6 = [
        (2026, 2030),
        (2031, 2035),
        (2036, 2040),
        (2041, 2045),
        (2046, 2050),
        (2051, 2055),
    ]
    anchor_6_scvr = []
    anchor_6_mid = []
    for start, end in anchors_6:
        window_vals = []
        for model, series in future_daily.items():
            mask = (series.index.year >= start) & (series.index.year <= end)
            window_vals.append(series[mask].values)
        window_pool = np.concatenate(window_vals)
        result = compute_scvr(base_pool, window_pool)
        mid = (start + end) / 2
        anchor_6_mid.append(mid)
        anchor_6_scvr.append(result["scvr"])
        print(f"  {start}-{end} (mid={mid:.1f}): SCVR={result['scvr']:.4f}  "
              f"({len(window_pool):,} values)")

    fit_6 = np.polyfit(anchor_6_mid, anchor_6_scvr, 1)
    annual_6 = np.polyval(fit_6, years)
    ss_res = np.sum((np.array(anchor_6_scvr) - np.polyval(fit_6, anchor_6_mid))**2)
    ss_tot = np.sum((np.array(anchor_6_scvr) - np.mean(anchor_6_scvr))**2)
    r2_6 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    print(f"  Linear fit: SCVR(t) = {fit_6[1]:.4f} + {fit_6[0]:.6f} * t")
    print(f"  R² = {r2_6:.4f}")

    # ── Method 4: Full Window (current NB03) ─────────────────────────────────
    print("\n--- Method 4: Full 30-year Window ---")
    full_pool = np.concatenate([s.values for s in future_daily.values()])
    full_result = compute_scvr(base_pool, full_pool)
    full_scvr = full_result["scvr"]
    print(f"  SCVR = {full_scvr:.4f}  ({len(full_pool):,} values)")

    return {
        "years": years,
        "per_year": per_year_arr,
        "anchor_3_mid": anchor_3_mid,
        "anchor_3_scvr": anchor_3_scvr,
        "annual_3": annual_3,
        "fit_3": fit_3,
        "r2_3": r2_3,
        "anchor_6_mid": anchor_6_mid,
        "anchor_6_scvr": anchor_6_scvr,
        "annual_6": annual_6,
        "fit_6": fit_6,
        "r2_6": r2_6,
        "full_scvr": full_scvr,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Plot & Summary
# ══════════════════════════════════════════════════════════════════════════════

def plot_comparison(results, variable):
    years = results["years"]

    fig, ax = plt.subplots(figsize=(14, 6))

    # Per-year scatter
    ax.scatter(years, results["per_year"], s=40, c="#999999", alpha=0.7,
               zorder=3, label=f"Per-year SCVR (std={results['per_year'].std():.4f})")

    # 3-anchor fit
    ax.plot(years, results["annual_3"], "b-", lw=2.5, zorder=4,
            label=f"3-anchor linear fit (R²={results['r2_3']:.3f})")
    ax.scatter(results["anchor_3_mid"], results["anchor_3_scvr"],
               s=120, c="blue", marker="D", zorder=5, edgecolors="white", linewidths=1.5)

    # 6-anchor fit
    ax.plot(years, results["annual_6"], "g--", lw=2, zorder=4,
            label=f"6-anchor linear fit (R²={results['r2_6']:.3f})")
    ax.scatter(results["anchor_6_mid"], results["anchor_6_scvr"],
               s=80, c="green", marker="s", zorder=5, edgecolors="white", linewidths=1.5)

    # Full window reference
    ax.axhline(results["full_scvr"], color="red", ls=":", lw=1.5, zorder=2,
               label=f"Full 30yr window (NB03) = {results['full_scvr']:.4f}")

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("SCVR", fontsize=12)
    ax.set_title(f"Annual SCVR Comparison — {SITE_ID} / {variable} / {SCENARIO}",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(2025, 2056)

    plt.tight_layout()
    out_path = OUT_DIR / f"annual_scvr_comparison_{variable}_{SCENARIO}.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved: {out_path}")
    plt.close()


def print_summary(results, variable):
    years = results["years"]
    print("\n" + "=" * 75)
    print(f"SUMMARY — {SITE_ID} / {variable} / {SCENARIO}")
    print("=" * 75)

    print(f"\n{'Year':>6}  {'Per-Year':>10}  {'3-Anchor':>10}  {'6-Anchor':>10}  {'Full-Win':>10}")
    print("-" * 52)
    for i, yr in enumerate(years):
        if yr % 5 == 0 or yr == years[0] or yr == years[-1]:
            print(f"{yr:>6}  {results['per_year'][i]:>10.4f}  "
                  f"{results['annual_3'][i]:>10.4f}  "
                  f"{results['annual_6'][i]:>10.4f}  "
                  f"{results['full_scvr']:>10.4f}")

    py = results["per_year"]
    print(f"\n--- Per-Year Stats ---")
    print(f"  Mean:    {py.mean():.4f}")
    print(f"  Std:     {py.std():.4f}")
    print(f"  Min:     {py.min():.4f}  (year {years[np.argmin(py)]})")
    print(f"  Max:     {py.max():.4f}  (year {years[np.argmax(py)]})")
    print(f"  Range:   {py.max() - py.min():.4f}")
    neg_count = np.sum(py < 0)
    print(f"  Negative years: {neg_count}")

    print(f"\n--- Anchor Comparison ---")
    print(f"  3-anchor R²:  {results['r2_3']:.4f}")
    print(f"  6-anchor R²:  {results['r2_6']:.4f}")
    print(f"  Full window:  {results['full_scvr']:.4f}")
    print(f"  3-anchor mean of fit: {results['annual_3'].mean():.4f}")
    print(f"  6-anchor mean of fit: {results['annual_6'].mean():.4f}")

    noise_ratio = py.std() / py.mean() if py.mean() != 0 else float("inf")
    print(f"\n--- Verdict ---")
    print(f"  Noise-to-signal (std/mean): {noise_ratio:.2f}")
    if noise_ratio > 0.5:
        print(f"  >> Per-year SCVR is NOISY (ratio > 0.5). Anchor approach recommended.")
    elif noise_ratio > 0.3:
        print(f"  >> Per-year SCVR is MODERATELY noisy. Anchor approach preferred.")
    else:
        print(f"  >> Per-year SCVR is reasonably stable. Per-year may be acceptable.")

    if neg_count > 0:
        print(f"  >> {neg_count} years show NEGATIVE SCVR for {variable} — "
              f"confirms noise issue.")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"Annual SCVR Experiment")
    print(f"  Site:     {SITE_ID} ({LAT}, {LON})")
    print(f"  Variables: {VARIABLES}")
    print(f"  Scenario: {SCENARIO}")
    print(f"  Baseline: {BASELINE_YEARS[0]}-{BASELINE_YEARS[1]}")
    print(f"  Future:   {FUTURE_YEARS[0]}-{FUTURE_YEARS[1]}")

    all_summaries = {}

    for variable in VARIABLES:
        print(f"\n{'#' * 75}")
        print(f"# VARIABLE: {variable}")
        print(f"{'#' * 75}\n")

        models = find_cached_models(variable)
        if not models:
            print(f"  SKIP: No cached models found for {variable}.")
            continue

        baseline_daily, future_daily = load_all_data(models, variable)
        if not baseline_daily or not future_daily:
            print(f"  SKIP: Failed to load data for {variable}.")
            continue

        results = compute_all_methods(baseline_daily, future_daily)
        plot_comparison(results, variable)
        print_summary(results, variable)

        all_summaries[variable] = {
            "mean": results["per_year"].mean(),
            "std": results["per_year"].std(),
            "min": results["per_year"].min(),
            "max": results["per_year"].max(),
            "noise_ratio": results["per_year"].std() / abs(results["per_year"].mean())
                           if results["per_year"].mean() != 0 else float("inf"),
            "neg_count": int(np.sum(results["per_year"] < 0)),
            "r2_3": results["r2_3"],
            "r2_6": results["r2_6"],
            "full_scvr": results["full_scvr"],
        }

    # ── Cross-variable comparison ────────────────────────────────────────────
    if len(all_summaries) > 1:
        print(f"\n{'=' * 75}")
        print(f"CROSS-VARIABLE COMPARISON")
        print(f"{'=' * 75}")
        print(f"\n{'Variable':>10}  {'Mean':>8}  {'Std':>8}  {'Noise/Sig':>10}  "
              f"{'Neg Yrs':>8}  {'R²(3)':>7}  {'R²(6)':>7}")
        print("-" * 70)
        for var, s in all_summaries.items():
            print(f"{var:>10}  {s['mean']:>8.4f}  {s['std']:>8.4f}  "
                  f"{s['noise_ratio']:>10.2f}  {s['neg_count']:>8}  "
                  f"{s['r2_3']:>7.3f}  {s['r2_6']:>7.3f}")
