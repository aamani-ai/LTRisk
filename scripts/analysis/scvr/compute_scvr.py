"""
compute_scvr.py
===============
Canonical script for computing SCVR (Severe Climate Variability Rating) from
cached CMIP6 daily climate data.

Reads NetCDF files from data/cache/thredds/ (produced by fetch_cmip6.py),
computes ensemble SCVR, decade-resolved SCVR, anchor-fit annual SCVR,
and distribution shape metrics. Outputs Parquet files and a JSON report.

Pipeline position:
  fetch_cmip6.py  →  compute_scvr.py  →  (later: compute_hcr.py → ...)
       ↓                    ↓
  data/cache/          data/output/
  thredds/*.nc         scvr/<site>/*.parquet

Usage:
  # Dry-run — show what would be computed
  python scripts/analysis/scvr/compute_scvr.py --dry-run

  # Compute SCVR for Hayhurst Solar (default)
  python scripts/analysis/scvr/compute_scvr.py --site hayhurst_solar

  # Single variable
  python scripts/analysis/scvr/compute_scvr.py --variables tasmax

  # Maverick Wind site
  python scripts/analysis/scvr/compute_scvr.py --site maverick_wind
"""

import argparse
import io
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import cftime
import numpy as np
import pandas as pd
import xarray as xr

# Optional: scipy for GEV/GPD fitting and skewness/kurtosis
try:
    from scipy import stats as sp_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "data" / "schema"
CACHE_DIR  = ROOT / "data" / "cache" / "thredds"
OUTPUT_DIR = ROOT / "data" / "output" / "scvr"

# ── Import config loaders from fetch_cmip6 ───────────────────────────────────
sys.path.insert(0, str(ROOT))
from scripts.data.fetch_cmip6 import load_sites, load_p1_variables, ALL_MODELS

# ── Variable strategy ────────────────────────────────────────────────────────
SCVR_STRATEGY = {
    "tasmax": "anchor_3_linear",
    "tasmin": "anchor_3_linear",
    "tas":    "anchor_3_linear",
    "pr":     "period_average",
    "hurs":   "period_average",
    "sfcWind": "period_average",
    "rsds":   "period_average",
}

DEFAULT_DECADES = [
    ("2026-2035", 2026, 2035),
    ("2036-2045", 2036, 2045),
    ("2046-2055", 2046, 2055),
]


# ══════════════════════════════════════════════════════════════════════════════
# Data Loading (cache-only — no THREDDS calls)
# ══════════════════════════════════════════════════════════════════════════════

def cache_path(model, scenario, variable, year, lat, lon, cache_dir):
    """Return Path to cached NetCDF file."""
    key = f"{model}_{scenario}_{variable}_{year}_{lat:.4f}_{lon:.4f}.nc"
    return Path(cache_dir) / key


def parse_nc(path, variable, year):
    """Parse a cached NetCDF file into a pd.Series with DatetimeIndex."""
    ds = xr.open_dataset(path, engine="scipy", decode_times=False)
    da = ds[variable].squeeze()
    values = da.values.astype(float)

    tv = ds["time"]
    units = tv.attrs.get("units", f"days since {year}-01-01")
    calendar = tv.attrs.get("calendar", "standard").lower()
    nums = tv.values.astype(float)

    try:
        cf = cftime.num2date(nums, units=units, calendar=calendar)
        times = pd.to_datetime([
            f"{d.year:04d}-{d.month:02d}-{d.day:02d}" for d in cf
        ])
    except Exception:
        times = pd.date_range(f"{year}-01-01", periods=len(values), freq="D")

    ds.close()
    return pd.Series(values, index=times)


def unit_convert(series, variable):
    """Convert Kelvin → Celsius for temperature, kg/m²/s → mm/day for precip."""
    if variable.startswith("ta") and series.mean() > 200:
        series = series - 273.15
    if variable == "pr":
        series = series * 86400
    return series


def discover_cached_models(variable, scenarios, lat, lon,
                           baseline_years, future_years, cache_dir):
    """Scan cache dir to find models with complete data coverage.

    A model is 'complete' if it has cached files for ALL years in both
    baseline and future periods, for ALL scenarios + historical.
    """
    complete_models = []

    for model in ALL_MODELS:
        ok = True

        # Check historical baseline
        for yr in range(baseline_years[0], baseline_years[1] + 1):
            p = cache_path(model, "historical", variable, yr, lat, lon, cache_dir)
            if not p.exists() or p.stat().st_size < 500:
                ok = False
                break

        if not ok:
            continue

        # Check future scenarios
        for scen in scenarios:
            for yr in range(future_years[0], future_years[1] + 1):
                p = cache_path(model, scen, variable, yr, lat, lon, cache_dir)
                if not p.exists() or p.stat().st_size < 500:
                    ok = False
                    break
            if not ok:
                break

        if ok:
            complete_models.append(model)

    return complete_models


def load_model_years(model, scenario, variable, years, lat, lon,
                     cache_dir, max_workers=4):
    """Load multiple years from cache in parallel. Returns pd.Series or None."""
    def _load_one(yr):
        p = cache_path(model, scenario, variable, yr, lat, lon, cache_dir)
        if not p.exists() or p.stat().st_size < 500:
            return None
        try:
            return parse_nc(p, variable, yr)
        except Exception:
            return None

    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_load_one, yr): yr for yr in years}
        for fut in as_completed(futures):
            yr = futures[fut]
            res = fut.result()
            if res is not None:
                results[yr] = res

    if not results:
        return None
    combined = pd.concat([results[yr] for yr in sorted(results)])
    return combined.sort_index()


def load_data(models, variable, scenarios, baseline_years, future_years,
              lat, lon, cache_dir):
    """Load baseline and future daily data for all models.

    Returns (baseline_daily, future_daily) where:
      baseline_daily = {model: pd.Series}
      future_daily = {scenario: {model: pd.Series}}
    """
    baseline_daily = {}
    future_daily = {scen: {} for scen in scenarios}

    for model in models:
        base = load_model_years(
            model, "historical", variable,
            range(baseline_years[0], baseline_years[1] + 1),
            lat, lon, cache_dir
        )
        if base is not None:
            baseline_daily[model] = unit_convert(base, variable)

        for scen in scenarios:
            fut = load_model_years(
                model, scen, variable,
                range(future_years[0], future_years[1] + 1),
                lat, lon, cache_dir
            )
            if fut is not None:
                future_daily[scen][model] = unit_convert(fut, variable)

    return baseline_daily, future_daily


# ══════════════════════════════════════════════════════════════════════════════
# SCVR Core
# ══════════════════════════════════════════════════════════════════════════════

def compute_scvr(baseline_values, future_values):
    """Compute SCVR as fractional change in empirical exceedance area.

    SCVR = (area_future - area_baseline) / area_baseline
    """
    b = np.sort(np.asarray(baseline_values, dtype=float))
    b = b[~np.isnan(b)][::-1]
    f = np.sort(np.asarray(future_values, dtype=float))
    f = f[~np.isnan(f)][::-1]

    exc_b = np.linspace(0, 1, len(b))
    exc_f = np.linspace(0, 1, len(f))

    area_b = float(np.trapezoid(b, exc_b))
    area_f = float(np.trapezoid(f, exc_f))

    scvr = (area_f - area_b) / area_b if area_b != 0 else 0.0

    return {
        "scvr": scvr,
        "area_baseline": area_b,
        "area_future": area_f,
        "n_baseline_days": len(b),
        "n_future_days": len(f),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Pooling + Decade SCVR
# ══════════════════════════════════════════════════════════════════════════════

def pool_window(daily_dict, year_start, year_end):
    """Pool daily values from all models for years in [year_start, year_end]."""
    parts = []
    for series in daily_dict.values():
        mask = (series.index.year >= year_start) & (series.index.year <= year_end)
        parts.append(series[mask].values)
    if not parts:
        return np.array([])
    return np.concatenate(parts)


def compute_decade_scvr(base_pool, future_daily_dict, decades):
    """Compute SCVR for each decade window."""
    base_arr = np.asarray(base_pool, dtype=float)
    results = {}
    for label, start, end in decades:
        window_pool = pool_window(future_daily_dict, start, end)
        if len(window_pool) == 0:
            continue
        result = compute_scvr(base_arr, window_pool)
        result["decade"] = label
        result["window_start"] = start
        result["window_end"] = end
        results[label] = result
    return results


# ══════════════════════════════════════════════════════════════════════════════
# Anchor Fitting (annual SCVR)
# ══════════════════════════════════════════════════════════════════════════════

def compute_anchor_fit(base_pool, future_daily_dict, anchors, future_years=None):
    """Compute SCVR at anchor windows, fit linear trend, interpolate annually.

    For temperature variables (anchor_3_linear strategy):
      - 3 non-overlapping 10-year windows as anchors
      - Linear polyfit through anchor midpoints
      - Interpolate to annual values

    Returns dict with: mids, scvrs, fit, years, annual, r2
    """
    if future_years is None:
        future_years = (2026, 2055)

    base_arr = np.asarray(base_pool, dtype=float)
    mids, scvrs = [], []

    for start, end in anchors:
        window_pool = pool_window(future_daily_dict, start, end)
        if len(window_pool) == 0:
            continue
        result = compute_scvr(base_arr, window_pool)
        mids.append((start + end) / 2)
        scvrs.append(result["scvr"])

    if len(mids) < 2:
        return None

    fit = np.polyfit(mids, scvrs, 1)
    years = list(range(future_years[0], future_years[1] + 1))
    annual = np.polyval(fit, years)

    ss_res = np.sum((np.array(scvrs) - np.polyval(fit, mids)) ** 2)
    ss_tot = np.sum((np.array(scvrs) - np.mean(scvrs)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0

    return {
        "mids": mids,
        "scvrs": scvrs,
        "fit": fit.tolist(),
        "years": years,
        "annual": annual.tolist(),
        "r2": r2,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Shape Metrics
# ══════════════════════════════════════════════════════════════════════════════

def compute_shape_metrics(values):
    """Compute distribution shape metrics for a pool of daily values."""
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return None

    mean_val = float(np.mean(v))
    std_val = float(np.std(v))

    result = {
        "n_days": len(v),
        "min": float(np.min(v)),
        "max": float(np.max(v)),
        "mean": mean_val,
        "std": std_val,
        "variance": float(np.var(v)),
        "cv": std_val / abs(mean_val) if mean_val != 0 else None,
        "p10": float(np.percentile(v, 10)),
        "p25": float(np.percentile(v, 25)),
        "p50": float(np.percentile(v, 50)),
        "p75": float(np.percentile(v, 75)),
        "p90": float(np.percentile(v, 90)),
        "p95": float(np.percentile(v, 95)),
        "p99": float(np.percentile(v, 99)),
    }

    if HAS_SCIPY:
        result["skewness"] = float(sp_stats.skew(v))
        result["kurtosis"] = float(sp_stats.kurtosis(v))
    else:
        result["skewness"] = None
        result["kurtosis"] = None

    return result


def compute_decade_shape(daily_dict, decades):
    """Compute shape metrics for each decade window."""
    results = {}
    for label, start, end in decades:
        pooled = pool_window(daily_dict, start, end)
        metrics = compute_shape_metrics(pooled)
        if metrics is not None:
            results[label] = metrics
    return results


# ══════════════════════════════════════════════════════════════════════════════
# Companion Metrics (Audit Trail)
# ══════════════════════════════════════════════════════════════════════════════

def compute_cvar(values, alpha=0.95):
    """Conditional Value at Risk: mean of values above alpha-quantile."""
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return None
    threshold = np.percentile(v, alpha * 100)
    tail = v[v >= threshold]
    return float(np.mean(tail)) if len(tail) > 0 else None


def _classify_tail_confidence(mean_scvr, tail_scvr_p95, mean_tail_ratio, iqr):
    """Classify SCVR tail confidence: HIGH / MODERATE / LOW / DIVERGENT."""
    if tail_scvr_p95 is None or mean_scvr is None:
        return "INSUFFICIENT_DATA"
    # Signs differ → divergent
    if (abs(mean_scvr) > 0.005 and abs(tail_scvr_p95) > 0.005
            and np.sign(mean_scvr) != np.sign(tail_scvr_p95)):
        return "DIVERGENT"
    # Weak mean-tail linkage or high model disagreement
    if mean_tail_ratio is not None and abs(mean_tail_ratio) < 0.3:
        return "LOW"
    if abs(mean_scvr) > 1e-10 and iqr > 2 * abs(mean_scvr):
        return "LOW"
    # Strong agreement
    if mean_tail_ratio is not None and mean_tail_ratio > 0.6:
        return "HIGH"
    return "MODERATE"


def compute_companion_metrics(base_pool, fut_dict, scenario, variable):
    """Compute Tier 1 companion metrics for SCVR audit trail.

    Returns dict with: mean_scvr, tail_scvr_p95, extreme_scvr_p99, cvar95_ratio,
    mean_tail_ratio, model_iqr, tail_confidence, per_model_scvr, per_model_stats.
    """
    # 1. Per-model SCVR
    per_model = {}
    for model, series in fut_dict.items():
        fut_vals = series.dropna().values
        if len(fut_vals) == 0:
            continue
        result = compute_scvr(base_pool, fut_vals)
        per_model[model] = result["scvr"]

    if len(per_model) < 2:
        return None

    model_scvrs = np.array(list(per_model.values()))
    p25, p75 = np.percentile(model_scvrs, [25, 75])
    iqr = float(p75 - p25)

    # 2. Pooled future values
    fut_pool = np.concatenate([s.dropna().values for s in fut_dict.values()])

    # For precipitation, filter to wet days (> 0.1 mm/day) before computing tail
    # metrics. ~78% of days are dry at arid sites — the all-days P95 sits in the
    # dry/wet transition zone and produces meaningless tail SCVR values.
    # Mean SCVR stays on all days (correct for the mean).
    if variable == "pr":
        base_tail_vals = base_pool[base_pool > 0.1]
        fut_tail_vals = fut_pool[fut_pool > 0.1]
        # Fallback to all days if insufficient wet days
        if len(base_tail_vals) < 100 or len(fut_tail_vals) < 100:
            base_tail_vals = base_pool
            fut_tail_vals = fut_pool
    else:
        base_tail_vals = base_pool
        fut_tail_vals = fut_pool

    # 3. P95 SCVR (ratio of 95th percentiles)
    b_p95 = np.percentile(base_tail_vals, 95)
    f_p95 = np.percentile(fut_tail_vals, 95)
    tail_scvr_p95 = float((f_p95 - b_p95) / abs(b_p95)) if abs(b_p95) > 1e-10 else None

    # 4. P99 SCVR
    b_p99 = np.percentile(base_tail_vals, 99)
    f_p99 = np.percentile(fut_tail_vals, 99)
    extreme_scvr_p99 = float((f_p99 - b_p99) / abs(b_p99)) if abs(b_p99) > 1e-10 else None

    # 5. CVaR 95% ratio
    b_cvar = compute_cvar(base_tail_vals, 0.95)
    f_cvar = compute_cvar(fut_tail_vals, 0.95)
    cvar95_ratio = None
    if b_cvar is not None and f_cvar is not None and abs(b_cvar) > 1e-10:
        cvar95_ratio = float((f_cvar - b_cvar) / abs(b_cvar))

    # 6. Mean SCVR (pooled)
    pooled_result = compute_scvr(base_pool, fut_pool)
    mean_scvr = pooled_result["scvr"]

    # 7. Mean-Tail Ratio
    mean_tail_ratio = None
    if tail_scvr_p95 is not None and abs(mean_scvr) > 1e-10:
        mean_tail_ratio = float(tail_scvr_p95 / mean_scvr)

    # 8. Tail Confidence Flag
    tail_confidence = _classify_tail_confidence(
        mean_scvr, tail_scvr_p95, mean_tail_ratio, iqr
    )

    return {
        "scenario": scenario,
        "variable": variable,
        "mean_scvr": mean_scvr,
        "tail_scvr_p95": tail_scvr_p95,
        "extreme_scvr_p99": extreme_scvr_p99,
        "cvar95_ratio": cvar95_ratio,
        "mean_tail_ratio": mean_tail_ratio,
        "model_iqr": iqr,
        "tail_confidence": tail_confidence,
        "n_models": len(per_model),
        "per_model_scvr": per_model,
        "per_model_stats": {
            "min": float(model_scvrs.min()),
            "p25": float(p25),
            "median": float(np.median(model_scvrs)),
            "p75": float(p75),
            "max": float(model_scvrs.max()),
            "std": float(model_scvrs.std()),
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# GEV / GPD Fitting
# ══════════════════════════════════════════════════════════════════════════════

def fit_gev(daily_dict, block="annual_max"):
    """Fit GEV distribution to annual block maxima from pooled models."""
    if not HAS_SCIPY:
        return None
    try:
        block_values = []
        for series in daily_dict.values():
            if series is None:
                continue
            ann = series.resample("YE").max() if block == "annual_max" else series.resample("YE").min()
            block_values.extend(ann.dropna().values.tolist())

        if len(block_values) < 10:
            return None

        arr = np.array(block_values, dtype=float)
        shape, loc, scale = sp_stats.genextreme.fit(arr)
        ks_stat, ks_pval = sp_stats.kstest(arr, 'genextreme', args=(shape, loc, scale))

        return {
            "shape": float(shape),
            "loc": float(loc),
            "scale": float(scale),
            "n_blocks": len(arr),
            "ks_statistic": float(ks_stat),
            "ks_pvalue": float(ks_pval),
        }
    except Exception:
        return None


def fit_gpd(daily_dict, threshold_quantile=0.95):
    """Fit GPD to daily values above a threshold."""
    if not HAS_SCIPY:
        return None
    try:
        all_vals = np.concatenate([
            s.dropna().values for s in daily_dict.values() if s is not None
        ])
        if len(all_vals) < 100:
            return None

        threshold = float(np.percentile(all_vals, threshold_quantile * 100))
        exceedances = all_vals[all_vals > threshold] - threshold
        if len(exceedances) < 20:
            return None

        shape, _, scale = sp_stats.genpareto.fit(exceedances, floc=0)
        ks_stat, ks_pval = sp_stats.kstest(exceedances, 'genpareto', args=(shape, 0, scale))

        return {
            "shape": float(shape),
            "scale": float(scale),
            "threshold": threshold,
            "n_exceedances": len(exceedances),
            "exceedance_rate": float(len(exceedances) / len(all_vals)),
            "ks_statistic": float(ks_stat),
            "ks_pvalue": float(ks_pval),
        }
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SCVR Pipeline Orchestration
# ══════════════════════════════════════════════════════════════════════════════

def run_scvr_pipeline(variable, models, scenarios, baseline_years, future_years,
                      lat, lon, cache_dir, decades=None):
    """Run full SCVR pipeline for one variable.

    Returns dict with:
      ensemble_scvr: list of row dicts (for DataFrame)
      decade_scvr: list of row dicts
      shape_metrics: list of row dicts
      annual_scvr: list of row dicts (if anchor strategy)
      companion_metrics: list of dicts (per-model SCVR, tail confidence, etc.)
      gev_fits: dict per scenario
    """
    if decades is None:
        decades = DEFAULT_DECADES

    strategy = SCVR_STRATEGY.get(variable, "period_average")
    anchors = [(d[1], d[2]) for d in decades]  # [(2026,2035), ...]

    ensemble_rows = []
    decade_rows = []
    shape_rows = []
    annual_rows = []
    companion_rows = []
    anchor_fits = {}

    for scen in scenarios:
        print(f"    [{variable}] Loading {scen} ...", flush=True)
        baseline_daily, future_daily = load_data(
            models, variable, [scen], baseline_years, future_years,
            lat, lon, cache_dir
        )

        if not baseline_daily or not future_daily.get(scen):
            print(f"    [{variable}] No data for {scen}, skipping")
            continue

        # Pool baseline
        base_pool = pool_window(baseline_daily,
                                baseline_years[0], baseline_years[1])
        fut_dict = future_daily[scen]

        # Pool future (full period)
        fut_pool = pool_window(fut_dict, future_years[0], future_years[1])

        # 1. Ensemble SCVR (full period)
        result = compute_scvr(base_pool, fut_pool)
        center_year = (future_years[0] + future_years[1]) // 2
        ensemble_rows.append({
            "scenario": scen,
            "variable": variable,
            "center_year": center_year,
            "scvr": result["scvr"],
            "area_baseline": result["area_baseline"],
            "area_future": result["area_future"],
            "n_baseline_days": result["n_baseline_days"],
            "n_future_days": result["n_future_days"],
            "n_models": len(fut_dict),
            "window_start_year": future_years[0],
            "window_end_year": future_years[1],
        })

        # 1b. Companion metrics (audit trail)
        companions = compute_companion_metrics(base_pool, fut_dict, scen, variable)
        if companions is not None:
            companion_rows.append(companions)

        # 2. Decade SCVR
        dec_results = compute_decade_scvr(base_pool, fut_dict, decades)
        for label, dr in dec_results.items():
            decade_rows.append({
                "scenario": scen,
                "variable": variable,
                "decade": label,
                "scvr": dr["scvr"],
                "area_baseline": dr["area_baseline"],
                "area_future": dr["area_future"],
                "n_future_days": dr["n_future_days"],
            })

        # 3. Shape metrics (baseline + each decade)
        base_shape = compute_shape_metrics(base_pool)
        if base_shape:
            base_shape.update({"scenario": "baseline", "variable": variable,
                               "period": "baseline"})
            shape_rows.append(base_shape)

        dec_shapes = compute_decade_shape(fut_dict, decades)
        for label, sm in dec_shapes.items():
            sm.update({"scenario": scen, "variable": variable, "period": label})
            shape_rows.append(sm)

        # 4. Annual SCVR (strategy-dependent)
        if strategy == "anchor_3_linear":
            fit = compute_anchor_fit(base_pool, fut_dict, anchors, future_years)
            if fit:
                for yr, val in zip(fit["years"], fit["annual"]):
                    annual_rows.append({
                        "scenario": scen,
                        "variable": variable,
                        "year": yr,
                        "scvr": val,
                        "method": "anchor_3_linear",
                        "r2": fit["r2"],
                    })
                # Save anchor fit details for report
                anchor_fits[scen] = {
                    "mids": fit["mids"],
                    "scvrs": fit["scvrs"],
                    "slope": fit["fit"][0],
                    "intercept": fit["fit"][1],
                    "r2": fit["r2"],
                }
        else:
            # period_average: use decade SCVR directly, assign to midpoint year
            for label, dr in dec_results.items():
                mid = (dr["window_start"] + dr["window_end"]) // 2
                annual_rows.append({
                    "scenario": scen,
                    "variable": variable,
                    "year": mid,
                    "scvr": dr["scvr"],
                    "method": "period_average",
                    "r2": None,
                })

    # 5. GEV + GPD fits (baseline and future)
    gev_fits = {}
    gpd_fits = {}
    if HAS_SCIPY:
        for scen in scenarios:
            baseline_daily, future_daily = load_data(
                models[:3], variable, [scen], baseline_years, future_years,
                lat, lon, cache_dir
            )
            if baseline_daily:
                gev_fits[f"baseline_{variable}"] = fit_gev(baseline_daily)
                gpd_fits[f"baseline_{variable}"] = fit_gpd(baseline_daily)
            if future_daily.get(scen):
                gev_fits[f"{scen}_{variable}"] = fit_gev(future_daily[scen])
                gpd_fits[f"{scen}_{variable}"] = fit_gpd(future_daily[scen])

    return {
        "ensemble_scvr": ensemble_rows,
        "decade_scvr": decade_rows,
        "shape_metrics": shape_rows,
        "annual_scvr": annual_rows,
        "companion_metrics": companion_rows,
        "anchor_fits": anchor_fits,
        "gev_fits": gev_fits,
        "gpd_fits": gpd_fits,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Output
# ══════════════════════════════════════════════════════════════════════════════

def save_outputs(all_results, site_id, lat, lon, out_dir, config=None):
    """Save DataFrames and comprehensive JSON report.

    Args:
        all_results: dict of {variable: pipeline_result}
        site_id: site identifier
        lat, lon: coordinates
        out_dir: output directory
        config: run configuration dict (from main())
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect rows across all variables
    ensemble_rows = []
    decade_rows = []
    shape_rows = []
    annual_rows = []
    companion_rows = []
    gev_fits = {}
    gpd_fits = {}
    anchor_fits_all = {}

    for var, res in all_results.items():
        ensemble_rows.extend(res["ensemble_scvr"])
        decade_rows.extend(res["decade_scvr"])
        shape_rows.extend(res["shape_metrics"])
        annual_rows.extend(res["annual_scvr"])
        companion_rows.extend(res.get("companion_metrics", []))
        gev_fits.update(res["gev_fits"])
        gpd_fits.update(res.get("gpd_fits", {}))
        if res.get("anchor_fits"):
            anchor_fits_all[var] = res["anchor_fits"]

    # Save Parquet files
    saved = []

    if ensemble_rows:
        df = pd.DataFrame(ensemble_rows)
        df["site_id"] = site_id
        path = out_dir / "cmip6_ensemble_scvr.parquet"
        df.to_parquet(path, index=False)
        saved.append(path.name)
        print(f"  Saved: {path} ({len(df)} rows)")

    if decade_rows:
        df = pd.DataFrame(decade_rows)
        df["site_id"] = site_id
        path = out_dir / "cmip6_scvr_decade.parquet"
        df.to_parquet(path, index=False)
        saved.append(path.name)
        print(f"  Saved: {path} ({len(df)} rows)")

    if shape_rows:
        df = pd.DataFrame(shape_rows)
        df["site_id"] = site_id
        path = out_dir / "cmip6_shape_metrics.parquet"
        df.to_parquet(path, index=False)
        saved.append(path.name)
        print(f"  Saved: {path} ({len(df)} rows)")

    if annual_rows:
        df = pd.DataFrame(annual_rows)
        df["site_id"] = site_id
        path = out_dir / "cmip6_scvr_annual.parquet"
        df.to_parquet(path, index=False)
        saved.append(path.name)
        print(f"  Saved: {path} ({len(df)} rows)")

    # Filter out None GPD fits
    gpd_fits = {k: v for k, v in gpd_fits.items() if v is not None}

    # Build comprehensive JSON report
    report = {
        "timestamp": datetime.now().isoformat(),
        "site_id": site_id,
        "lat": lat,
        "lon": lon,

        # Run configuration — what was computed and how
        "config": config or {},

        # Model coverage per variable
        "models": {
            var: {
                "count": len(models),
                "names": models,
            }
            for var, models in (config or {}).get("models_per_var", {}).items()
        } if config else {},

        # Row counts
        "summary": {
            "ensemble_scvr_rows": len(ensemble_rows),
            "decade_scvr_rows": len(decade_rows),
            "shape_metrics_rows": len(shape_rows),
            "annual_scvr_rows": len(annual_rows),
            "companion_metrics_rows": len(companion_rows),
        },

        # All SCVR data (mirrors Parquet but readable without pandas)
        "ensemble_scvr": ensemble_rows,
        "decade_scvr": decade_rows,
        "annual_scvr": annual_rows,

        # Anchor fit details (temperature variables only)
        "anchor_fits": anchor_fits_all,

        # Companion metrics (audit trail: per-model SCVR, tail confidence, etc.)
        "companion_metrics": companion_rows,

        # Distribution shape metrics
        "shape_metrics": shape_rows,

        # Extreme value fits
        "gev_fits": gev_fits,
        "gpd_fits": gpd_fits,

        # Output manifest (relative filenames)
        "files_saved": saved,
    }

    # Remove models_per_var from config to avoid duplication with top-level "models"
    if config and "models_per_var" in report.get("config", {}):
        report["config"] = {
            k: v for k, v in report["config"].items() if k != "models_per_var"
        }

    report_path = out_dir / "scvr_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"  Saved: {report_path}")

    return report


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="Compute SCVR from cached CMIP6 daily climate data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--site", default="hayhurst_solar",
                   help="Site ID from sites.json (default: hayhurst_solar)")
    p.add_argument("--variables", nargs="+", default=None,
                   help="Variables (default: P1_core from variables.json)")
    p.add_argument("--scenarios", nargs="+", default=["ssp245", "ssp585"],
                   help="SSP scenarios (default: ssp245 ssp585)")
    p.add_argument("--baseline", nargs=2, type=int, default=[1985, 2014],
                   metavar=("START", "END"),
                   help="Baseline year range (default: 1985 2014)")
    p.add_argument("--future", nargs=2, type=int, default=[2026, 2055],
                   metavar=("START", "END"),
                   help="Future year range (default: 2026 2055)")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would be computed without computing")
    return p.parse_args()


def main():
    args = parse_args()

    # Load config
    sites = load_sites()
    if args.site not in sites:
        print(f"ERROR: site '{args.site}' not in sites.json. "
              f"Available: {list(sites.keys())}")
        sys.exit(1)

    site = sites[args.site]
    lat, lon = site["lat"], site["lon"]
    variables = args.variables or load_p1_variables()
    scenarios = args.scenarios
    baseline_years = tuple(args.baseline)
    future_years = tuple(args.future)

    print(f"Site: {site['name']} ({args.site})")
    print(f"  lat={lat}, lon={lon}")
    print(f"  Variables: {variables}")
    print(f"  Scenarios: {scenarios}")
    print(f"  Baseline: {baseline_years[0]}-{baseline_years[1]}")
    print(f"  Future:   {future_years[0]}-{future_years[1]}")
    print(f"  scipy:    {'available' if HAS_SCIPY else 'not installed (no GEV/GPD)'}")

    # Discover available models per variable
    print(f"\nDiscovering cached models ...")
    models_per_var = {}
    for var in variables:
        models = discover_cached_models(
            var, scenarios, lat, lon, baseline_years, future_years, CACHE_DIR
        )
        models_per_var[var] = models
        strategy = SCVR_STRATEGY.get(var, "period_average")
        print(f"  {var}: {len(models)} models (strategy: {strategy})")

    # Dry run
    if args.dry_run:
        print(f"\n--dry-run summary:")
        total_computations = 0
        for var in variables:
            n = len(models_per_var[var])
            n_scen = len(scenarios)
            total_computations += n * n_scen
            print(f"  {var}: {n} models × {n_scen} scenarios = {n * n_scen} SCVR computations")
        print(f"  Total: {total_computations} computations")
        print(f"  Output: {OUTPUT_DIR / args.site}/")
        return

    # Run pipeline
    all_results = {}
    t0 = time.time()
    for var in variables:
        models = models_per_var[var]
        if not models:
            print(f"\n  [{var}] No models with complete data, skipping")
            continue
        print(f"\n  [{var}] Computing SCVR ({len(models)} models) ...")
        result = run_scvr_pipeline(
            var, models, scenarios, baseline_years, future_years,
            lat, lon, CACHE_DIR
        )
        all_results[var] = result

    elapsed = time.time() - t0
    print(f"\nComputation done in {elapsed:.1f}s")

    # Build run configuration for report
    config = {
        "baseline_years": [baseline_years[0], baseline_years[1]],
        "future_years": [future_years[0], future_years[1]],
        "scenarios": scenarios,
        "variables": variables,
        "decades": [d[0] for d in DEFAULT_DECADES],
        "scvr_strategy": {v: SCVR_STRATEGY.get(v, "period_average")
                          for v in variables},
        "scipy_available": HAS_SCIPY,
        "computation_time_s": round(elapsed, 1),
        "models_per_var": {v: sorted(models_per_var[v]) for v in variables
                           if v in models_per_var},
    }

    # Save outputs
    out_dir = OUTPUT_DIR / args.site
    print(f"\nSaving outputs to {out_dir}/ ...")
    save_outputs(all_results, args.site, lat, lon, out_dir, config)
    print("\nDone.")


if __name__ == "__main__":
    main()
