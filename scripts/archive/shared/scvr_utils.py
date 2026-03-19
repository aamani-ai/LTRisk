"""
scvr_utils.py
=============
Shared utilities for the LTRisk SCVR pipeline.

Consolidates functions previously duplicated across:
  - notebook_analysis/03_integrated_scvr_cmip6.ipynb
  - scripts/presentation/ensemble_exceedance.py
  - scripts/experiments/annual_scvr_test.py

Sections:
  1. THREDDS pipeline  — fetch, cache, unit-convert CMIP6 daily data
  2. SCVR core         — empirical exceedance area computation
  3. Anchor fitting    — decade-anchor SCVR with linear interpolation
  4. Decade metrics    — shape/tail statistics per time window
  5. GEV fitting       — parametric exceedance overlay via scipy

Usage from a notebook:
    import sys; sys.path.insert(0, str(Path("../scripts/shared").resolve()))
    from scvr_utils import compute_scvr, compute_anchor_fit, ...
"""

import io
import time
import numpy as np
import pandas as pd
import xarray as xr
import cftime
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional: scipy for GEV fitting (graceful fallback if not installed)
try:
    from scipy import stats as sp_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — THREDDS Pipeline
# ══════════════════════════════════════════════════════════════════════════════

THREDDS_NCSS = "https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6"


def build_thredds_url(model, scenario, variable, year, lat, lon):
    """Construct THREDDS NCSS point-extraction URLs (v2.0 and v1 fallback)."""
    fname_v2 = f"{variable}_day_{model}_{scenario}_r1i1p1f1_gn_{year}_v2.0.nc"
    fname_v1 = f"{variable}_day_{model}_{scenario}_r1i1p1f1_gn_{year}.nc"
    base     = f"{THREDDS_NCSS}/{model}/{scenario}/r1i1p1f1/{variable}"
    params   = (f"?var={variable}&latitude={lat}&longitude={lon}"
                f"&time_start={year}-01-01T00:00:00Z"
                f"&time_end={year}-12-31T23:59:59Z&accept=netCDF")
    return f"{base}/{fname_v2}{params}", f"{base}/{fname_v1}{params}"


def fetch_year(model, scenario, variable, year, lat, lon, cache_dir, retries=3):
    """Fetch one year of daily data from THREDDS. Returns pd.Series or None."""
    cache_dir = Path(cache_dir)
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
    """Fetch multiple years in parallel. Returns concatenated pd.Series or None."""
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
    """Convert Kelvin → Celsius for temperature, kg/m²/s → mm/day for precip."""
    if variable.startswith("ta") and series.mean() > 200:
        series = series - 273.15
    if variable == "pr":
        series = series * 86400
    return series


def probe_model(model, scenario, variable, probe_year, lat, lon):
    """Check if a model/scenario/variable combination exists on THREDDS."""
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


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — SCVR Core
# ══════════════════════════════════════════════════════════════════════════════

def compute_scvr(baseline_values, future_values):
    """
    Compute SCVR as fractional change in area under the empirical exceedance curve.

    SCVR = (area_future - area_baseline) / area_baseline

    Parameters
    ----------
    baseline_values, future_values : array-like
        1-D arrays of daily climate values (NaN-safe).

    Returns
    -------
    dict with keys: scvr, area_baseline, area_future, n_baseline_days, n_future_days
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


def exceedance_curve_empirical(values):
    """
    Empirical exceedance curve (traditional hydrology view).

    Returns (sorted_values_ascending, exceedance_probabilities) for plotting
    with x = value, y = P(X > x).
    """
    v = np.sort(np.asarray(values, dtype=float))
    v = v[~np.isnan(v)]
    p = 1.0 - np.linspace(0, 1, len(v))
    return v, p


def exceedance_curve_descending(values):
    """
    Exceedance curve in SCVR convention (sorted descending, p from 0 to 1).

    Returns (sorted_values_descending, exceedance_probs).
    """
    v = np.sort(np.asarray(values, dtype=float))
    v = v[~np.isnan(v)][::-1]
    p = np.linspace(0, 1, len(v))
    return v, p


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Anchor Fitting
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


def compute_anchor_fit(base_pool, future_daily_dict, anchors, future_years=None):
    """
    Compute SCVR at non-overlapping anchor windows, fit linear trend.

    Parameters
    ----------
    base_pool : array-like
        Pooled baseline daily values.
    future_daily_dict : dict
        {model_name: pd.Series} of future daily values.
    anchors : list of (start_year, end_year) tuples
        Non-overlapping anchor windows.
    future_years : tuple (start, end), optional
        Full future range for annual interpolation. Default (2026, 2055).

    Returns
    -------
    dict with keys: mids, scvrs, fit, years, annual, r2
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

    # R-squared
    ss_res = np.sum((np.array(scvrs) - np.polyval(fit, mids)) ** 2)
    ss_tot = np.sum((np.array(scvrs) - np.mean(scvrs)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0

    return {
        "mids": mids,
        "scvrs": scvrs,
        "fit": fit,           # [slope, intercept] from np.polyfit
        "years": years,
        "annual": annual,     # interpolated annual SCVR values
        "r2": r2,
    }


def compute_decade_scvr(base_pool, future_daily_dict, decades):
    """
    Compute SCVR for each decade window.

    Parameters
    ----------
    base_pool : array-like
        Pooled baseline daily values.
    future_daily_dict : dict
        {model_name: pd.Series}.
    decades : list of (label, start_year, end_year) tuples

    Returns
    -------
    dict of {label: scvr_result_dict}
    """
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
# SECTION 4 — Decade Shape / Tail Metrics
# ══════════════════════════════════════════════════════════════════════════════

def compute_shape_metrics(values):
    """
    Compute distribution shape metrics for a pool of daily values.

    Returns dict: n_days, mean, std, variance, skewness, kurtosis, p95, p99
    """
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return None

    result = {
        "n_days": len(v),
        "mean": float(np.mean(v)),
        "std": float(np.std(v)),
        "variance": float(np.var(v)),
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


def compute_cvar(values, alpha=0.95):
    """
    Conditional Value at Risk (Expected Shortfall).
    CVaR_alpha = E[X | X > Q_alpha]

    Parameters
    ----------
    values : array-like
        1-D array of daily climate values.
    alpha : float
        Quantile level (default 0.95).

    Returns
    -------
    float or None if insufficient data.
    """
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return None
    threshold = np.percentile(v, alpha * 100)
    tail = v[v >= threshold]
    if len(tail) == 0:
        return None
    return float(np.mean(tail))


def compute_report_card(mean_scvr, tail_scvr_p95, cvar95_ratio, iqr,
                         extreme_scvr_p99=None):
    """
    Compute SCVR report card with Tail Confidence flag.

    Classifies the reliability of SCVR as a proxy for tail behavior:
      HIGH      — mean and tail agree, models converge
      MODERATE  — partial agreement or moderate model spread
      LOW       — weak mean-tail link or large model disagreement
      DIVERGENT — mean and tail have opposite signs

    Parameters
    ----------
    mean_scvr : float
        Pooled SCVR (mean ratio).
    tail_scvr_p95 : float
        Fractional change in 95th percentile.
    cvar95_ratio : float
        Fractional change in CVaR at 95%.
    iqr : float
        Inter-quartile range of per-model SCVR values.
    extreme_scvr_p99 : float, optional
        Fractional change in 99th percentile.

    Returns
    -------
    dict with report card fields + tail_confidence flag.
    """
    # Mean-Tail Ratio
    if mean_scvr != 0 and np.sign(mean_scvr) == np.sign(tail_scvr_p95):
        mean_tail_ratio = tail_scvr_p95 / mean_scvr
    else:
        mean_tail_ratio = None  # signs differ or mean ≈ 0

    # Tail Confidence flag
    if (np.sign(mean_scvr) != np.sign(tail_scvr_p95)
            and (abs(mean_scvr) > 0.005 or abs(tail_scvr_p95) > 0.005)):
        confidence = "DIVERGENT"
    elif mean_tail_ratio is not None and abs(mean_tail_ratio) < 0.3:
        confidence = "LOW"
    elif iqr > 2 * abs(mean_scvr) and abs(mean_scvr) > 0.005:
        confidence = "LOW"
    elif mean_tail_ratio is not None and mean_tail_ratio > 0.6:
        confidence = "HIGH"
    else:
        confidence = "MODERATE"

    return {
        "mean_scvr": mean_scvr,
        "tail_scvr_p95": tail_scvr_p95,
        "cvar95_ratio": cvar95_ratio,
        "extreme_scvr_p99": extreme_scvr_p99,
        "mean_tail_ratio": round(mean_tail_ratio, 4) if mean_tail_ratio is not None else None,
        "model_iqr": iqr,
        "tail_confidence": confidence,
    }


def fit_gev_single_model(series, block="annual_max"):
    """
    Fit GEV to annual block maxima from a single model's daily series.

    Parameters
    ----------
    series : pd.Series
        Daily values with DatetimeIndex for one model.
    block : str
        "annual_max" or "annual_min".

    Returns
    -------
    dict with shape (xi), loc, scale, n_blocks or None on failure.
    """
    if not HAS_SCIPY:
        return None
    try:
        if block == "annual_max":
            ann = series.resample("YE").max()
        else:
            ann = series.resample("YE").min()
        block_values = ann.dropna().values
        if len(block_values) < 10:
            return None
        arr = np.array(block_values, dtype=float)
        shape, loc, scale = sp_stats.genextreme.fit(arr)
        return {
            "shape": float(shape),
            "loc": float(loc),
            "scale": float(scale),
            "n_blocks": len(arr),
        }
    except Exception:
        return None


def compute_decade_shape(daily_dict, decades):
    """
    Compute shape metrics for each decade window.

    Parameters
    ----------
    daily_dict : dict
        {model_name: pd.Series}.
    decades : list of (label, start_year, end_year) tuples

    Returns
    -------
    dict of {label: shape_metrics_dict}
    """
    results = {}
    for label, start, end in decades:
        pooled = pool_window(daily_dict, start, end)
        metrics = compute_shape_metrics(pooled)
        if metrics is not None:
            results[label] = metrics
    return results


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — GEV Fitting
# ══════════════════════════════════════════════════════════════════════════════

def fit_gev(daily_dict, block="annual_max"):
    """
    Fit a GEV distribution to annual block maxima.

    Parameters
    ----------
    daily_dict : dict
        {model_name: pd.Series} of daily values.
    block : str
        "annual_max" (default) or "annual_min".

    Returns
    -------
    dict with shape (xi), loc (mu), scale (sigma), n_blocks
    or None on failure.
    """
    if not HAS_SCIPY:
        return None

    try:
        block_values = []
        for series in daily_dict.values():
            if series is None:
                continue
            if block == "annual_max":
                ann = series.resample("YE").max()
            else:
                ann = series.resample("YE").min()
            block_values.extend(ann.dropna().values.tolist())

        if len(block_values) < 10:
            return None

        arr = np.array(block_values, dtype=float)
        shape, loc, scale = sp_stats.genextreme.fit(arr)

        # Goodness-of-fit diagnostics
        ks_stat, ks_pval = sp_stats.kstest(arr, 'genextreme', args=(shape, loc, scale))
        logpdfs = sp_stats.genextreme.logpdf(arr, shape, loc=loc, scale=scale)
        loglik = float(np.sum(logpdfs[np.isfinite(logpdfs)]))
        aic = 2 * 3 - 2 * loglik  # k=3 params (shape, loc, scale)

        return {
            "shape": float(shape),   # xi — tail behavior
            "loc": float(loc),       # mu — location
            "scale": float(scale),   # sigma — spread
            "n_blocks": len(arr),
            "ks_statistic": float(ks_stat),
            "ks_pvalue": float(ks_pval),
            "loglikelihood": loglik,
            "aic": float(aic),
        }
    except Exception:
        return None


def exceedance_curve_gev(shape, loc, scale, x_range):
    """
    Theoretical GEV exceedance curve for overlay plotting.

    Parameters
    ----------
    shape, loc, scale : float
        GEV parameters from fit_gev().
    x_range : array-like
        Values at which to evaluate.

    Returns
    -------
    (x_values, exceedance_probabilities) tuple
    """
    if not HAS_SCIPY:
        return None, None

    x = np.asarray(x_range, dtype=float)
    cdf = sp_stats.genextreme.cdf(x, shape, loc=loc, scale=scale)
    exceed = 1.0 - cdf
    return x, exceed


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5b — GPD Fitting (Peaks-Over-Threshold)
# ══════════════════════════════════════════════════════════════════════════════

def fit_gpd(daily_dict, threshold_quantile=0.95):
    """
    Fit a Generalized Pareto Distribution to daily values above a threshold.

    Unlike GEV (which models annual block maxima), GPD models threshold
    exceedances — values above a high quantile. This gives exceedance
    probabilities in the same space as the empirical daily curve.

    Parameters
    ----------
    daily_dict : dict
        {model_name: pd.Series} of daily values.
    threshold_quantile : float
        Quantile to use as threshold (default 0.95 = P95).

    Returns
    -------
    dict with shape, scale, threshold, n_exceedances, exceedance_rate, n_total
    or None on failure.
    """
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

        # Goodness-of-fit diagnostics
        ks_stat, ks_pval = sp_stats.kstest(exceedances, 'genpareto', args=(shape, 0, scale))
        logpdfs = sp_stats.genpareto.logpdf(exceedances, shape, loc=0, scale=scale)
        loglik = float(np.sum(logpdfs[np.isfinite(logpdfs)]))
        aic = 2 * 2 - 2 * loglik  # k=2 params (shape, scale; loc fixed=0)

        return {
            "shape": float(shape),
            "scale": float(scale),
            "threshold": threshold,
            "n_exceedances": len(exceedances),
            "exceedance_rate": float(len(exceedances) / len(all_vals)),
            "n_total": len(all_vals),
            "ks_statistic": float(ks_stat),
            "ks_pvalue": float(ks_pval),
            "loglikelihood": loglik,
            "aic": float(aic),
        }
    except Exception:
        return None


def exceedance_curve_gpd(shape, scale, threshold, rate, x_range):
    """
    GPD-based exceedance curve for daily values.

    P(X > x) = rate × [1 - GPD_cdf(x - threshold)]
    Only valid for x >= threshold.

    Parameters
    ----------
    shape, scale : float
        GPD parameters from fit_gpd().
    threshold : float
        The threshold value.
    rate : float
        Fraction of all days above threshold (exceedance_rate from fit_gpd).
    x_range : array-like
        Values at which to evaluate.

    Returns
    -------
    (x_values, exceedance_probabilities) tuple
    """
    if not HAS_SCIPY:
        return None, None

    x = np.asarray(x_range, dtype=float)
    p = np.full_like(x, np.nan)
    mask = x >= threshold
    if mask.any():
        gpd_cdf = sp_stats.genpareto.cdf(x[mask] - threshold, shape, scale=scale)
        p[mask] = rate * (1.0 - gpd_cdf)
    return x, p


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Variable Strategy
# ══════════════════════════════════════════════════════════════════════════════

# Default strategy mapping (can be overridden by caller)
DEFAULT_SCVR_STRATEGY = {
    "tasmax": "anchor_3_linear",
    "tasmin": "anchor_3_linear",
    "tas":    "anchor_3_linear",
    "pr":     "period_average",
    "hurs":   "period_average",
    "sfcWind": "period_average",
    "rsds":   "period_average",
}

DEFAULT_ANCHOR_3 = [(2026, 2035), (2036, 2045), (2046, 2055)]
DEFAULT_ANCHOR_6 = [(2026, 2030), (2031, 2035), (2036, 2040),
                    (2041, 2045), (2046, 2050), (2051, 2055)]

DEFAULT_DECADES = [
    ("2026-2035", 2026, 2035),
    ("2036-2045", 2036, 2045),
    ("2046-2055", 2046, 2055),
]


def variable_scvr_strategy(variable, strategy_map=None):
    """
    Return the recommended SCVR method for a variable.

    Returns one of: "anchor_3_linear", "anchor_6_linear", "period_average"
    """
    if strategy_map is None:
        strategy_map = DEFAULT_SCVR_STRATEGY
    return strategy_map.get(variable, "period_average")
