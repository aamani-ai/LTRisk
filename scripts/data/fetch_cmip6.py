"""
fetch_cmip6.py
==============
Canonical script for fetching NEX-GDDP-CMIP6 daily climate data from NASA
THREDDS, with smart caching (skip if already on disk) and variant discovery
(tries multiple realizations × grids per model).

Consolidates fetch logic previously duplicated across:
  - scripts/shared/scvr_utils.py       (basic r1i1p1f1/gn only)
  - scripts/presentation/ensemble_exceedance.py (variant discovery)
  - notebook_analysis/03_integrated_scvr_cmip6.ipynb (inline copies)

Usage:
  # Dry-run for Hayhurst Solar — show cache state, don't fetch
  python scripts/data/fetch_cmip6.py --dry-run

  # Fetch everything for Hayhurst Solar
  python scripts/data/fetch_cmip6.py --site hayhurst_solar

  # Fetch a single model/variable/year for testing
  python scripts/data/fetch_cmip6.py --models ACCESS-CM2 --variables tasmax --future 2026 2026

  # Discover which models are available on THREDDS
  python scripts/data/fetch_cmip6.py --discover-only

  # Validate cached files can be opened
  python scripts/data/fetch_cmip6.py --dry-run --integrity
"""

import argparse
import io
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Literal

import requests
import xarray as xr

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "data" / "schema"
CACHE_DIR  = ROOT / "data" / "cache" / "thredds"

# ── THREDDS constants ────────────────────────────────────────────────────────
THREDDS_NCSS = "https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6"

GRID_LABELS  = ["gn", "gr", "gr1", "gr2"]
REALIZATIONS = ["r1i1p1f1", "r1i1p1f2", "r1i1p1f3", "r3i1p1f1", "r4i1p1f1"]

# ── All 34 NEX-GDDP-CMIP6 models ────────────────────────────────────────────
ALL_MODELS = [
    "ACCESS-CM2", "ACCESS-ESM1-5", "BCC-CSM2-MR", "CanESM5", "CESM2",
    "CESM2-LENS", "CMCC-CM2-SR5", "CMCC-ESM2", "CNRM-CM6-1", "CNRM-ESM2-1",
    "EC-Earth3", "EC-Earth3-Veg-LR", "FGOALS-g3", "GFDL-CM4", "GFDL-CM4_gr2",
    "GFDL-ESM4", "GISS-E2-1-G", "HadGEM3-GC31-LL", "HadGEM3-GC31-MM",
    "IITM-ESM", "INM-CM4-8", "INM-CM5-0", "IPSL-CM6A-LR", "KACE-1-0-G",
    "KIOST-ESM", "MIROC6", "MPI-ESM1-2-HR", "MPI-ESM1-2-LR", "MRI-ESM2-0",
    "NESM3", "NorESM2-LM", "NorESM2-MM", "TaiESM1", "UKESM1-0-LL",
]


# ══════════════════════════════════════════════════════════════════════════════
# Data types
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class FetchTask:
    model: str
    scenario: str
    variable: str
    year: int
    lat: float
    lon: float


@dataclass
class FetchResult:
    task: FetchTask
    status: Literal["cached", "fetched", "failed"]
    path: Path | None = None
    error: str | None = None


# ══════════════════════════════════════════════════════════════════════════════
# Config loading
# ══════════════════════════════════════════════════════════════════════════════

def load_sites():
    with open(SCHEMA_DIR / "sites.json") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def load_p1_variables():
    """Return list of P1_core variable names from variables.json."""
    with open(SCHEMA_DIR / "variables.json") as f:
        data = json.load(f)
    return [k for k, v in data.items()
            if not k.startswith("_") and v.get("priority") == "P1_core"]


# ══════════════════════════════════════════════════════════════════════════════
# Variant cache (model|scenario -> {realization, grid})
# ══════════════════════════════════════════════════════════════════════════════

_variant_lock = threading.Lock()


def load_variant_cache(cache_dir):
    path = Path(cache_dir) / "model_variant_cache.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_variant_cache(cache, cache_dir):
    path = Path(cache_dir) / "model_variant_cache.json"
    with open(path, "w") as f:
        json.dump(cache, f, indent=2)


# ══════════════════════════════════════════════════════════════════════════════
# Probe cache (model|scenario|variable|year|lat|lon -> bool)
# ══════════════════════════════════════════════════════════════════════════════

_probe_lock = threading.Lock()


def load_probe_cache(cache_dir):
    path = Path(cache_dir) / "model_probe_cache.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_probe_cache(cache, cache_dir):
    path = Path(cache_dir) / "model_probe_cache.json"
    with open(path, "w") as f:
        json.dump(cache, f)


# ══════════════════════════════════════════════════════════════════════════════
# THREDDS URL construction
# ══════════════════════════════════════════════════════════════════════════════

def build_thredds_urls(model, scenario, variable, year, lat, lon,
                       variant_cache=None):
    """Return list of (url, realization, grid) tuples, best guess first."""
    params = (f"?var={variable}&latitude={lat}&longitude={lon}"
              f"&time_start={year}-01-01T00:00:00Z"
              # 12-30 not 12-31: 360-day calendar models reject Dec 31
              f"&time_end={year}-12-30T23:59:59Z&accept=netCDF")

    cache_key = f"{model}|{scenario}"
    known = None
    if variant_cache:
        with _variant_lock:
            known = variant_cache.get(cache_key)

    urls = []
    if known:
        real, grid = known["realization"], known["grid"]
        base = f"{THREDDS_NCSS}/{model}/{scenario}/{real}/{variable}"
        fname_v2 = f"{variable}_day_{model}_{scenario}_{real}_{grid}_{year}_v2.0.nc"
        fname_v1 = f"{variable}_day_{model}_{scenario}_{real}_{grid}_{year}.nc"
        urls.append((f"{base}/{fname_v2}{params}", real, grid))
        urls.append((f"{base}/{fname_v1}{params}", real, grid))
        return urls

    for real in REALIZATIONS:
        for grid in GRID_LABELS:
            base = f"{THREDDS_NCSS}/{model}/{scenario}/{real}/{variable}"
            fname_v2 = f"{variable}_day_{model}_{scenario}_{real}_{grid}_{year}_v2.0.nc"
            fname_v1 = f"{variable}_day_{model}_{scenario}_{real}_{grid}_{year}.nc"
            urls.append((f"{base}/{fname_v2}{params}", real, grid))
            urls.append((f"{base}/{fname_v1}{params}", real, grid))
    return urls


# ══════════════════════════════════════════════════════════════════════════════
# Cache check
# ══════════════════════════════════════════════════════════════════════════════

def cache_key(task):
    """Return the .nc filename used as cache key."""
    return (f"{task.model}_{task.scenario}_{task.variable}"
            f"_{task.year}_{task.lat:.4f}_{task.lon:.4f}.nc")


def check_cache(task, cache_dir, min_size=500):
    """Return Path if cached file exists and is > min_size bytes, else None."""
    path = Path(cache_dir) / cache_key(task)
    if path.exists() and path.stat().st_size > min_size:
        return path
    return None


# ══════════════════════════════════════════════════════════════════════════════
# Probe
# ══════════════════════════════════════════════════════════════════════════════

def probe_model(model, scenario, variable, probe_year, lat, lon,
                variant_cache, cache_dir):
    """Check if a model/scenario/variable exists on THREDDS.

    Updates variant_cache on success.
    """
    url_variants = build_thredds_urls(model, scenario, variable,
                                      probe_year, lat, lon, variant_cache)
    for url, real, grid in url_variants:
        try:
            r = requests.head(url, timeout=15)
            if r.status_code == 200:
                _record_variant(model, scenario, real, grid,
                                variant_cache, cache_dir)
                return True
            r = requests.get(url, timeout=20, stream=True)
            if r.status_code == 200:
                _record_variant(model, scenario, real, grid,
                                variant_cache, cache_dir)
                return True
        except Exception:
            pass
    return False


def _record_variant(model, scenario, real, grid, variant_cache, cache_dir):
    key = f"{model}|{scenario}"
    with _variant_lock:
        if key not in variant_cache:
            variant_cache[key] = {"realization": real, "grid": grid}
            save_variant_cache(variant_cache, cache_dir)


def probe_model_cached(model, scenario, variable, year, lat, lon,
                       variant_cache, probe_cache, cache_dir):
    """Probe with persistent JSON cache."""
    key = f"{model}|{scenario}|{variable}|{year}|{lat:.4f}|{lon:.4f}"
    with _probe_lock:
        if key in probe_cache:
            return probe_cache[key]

    result = probe_model(model, scenario, variable, year, lat, lon,
                         variant_cache, cache_dir)
    with _probe_lock:
        probe_cache[key] = result
        save_probe_cache(probe_cache, cache_dir)
    return result


# ══════════════════════════════════════════════════════════════════════════════
# Fetch single year (download only — no parse into Series)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_year(task, cache_dir, variant_cache, retries=3):
    """Download one year of daily data. Returns FetchResult."""
    # Check cache first
    cached = check_cache(task, cache_dir)
    if cached:
        return FetchResult(task=task, status="cached", path=cached)

    out_path = Path(cache_dir) / cache_key(task)
    url_variants = build_thredds_urls(
        task.model, task.scenario, task.variable,
        task.year, task.lat, task.lon, variant_cache
    )

    for attempt in range(retries):
        for url, real, grid in url_variants:
            try:
                r = requests.get(url, timeout=60)
                if r.status_code == 200 and len(r.content) > 500:
                    out_path.write_bytes(r.content)
                    _record_variant(task.model, task.scenario, real, grid,
                                    variant_cache, cache_dir)
                    return FetchResult(task=task, status="fetched", path=out_path)
            except Exception as e:
                last_err = str(e)
        if attempt < retries - 1:
            time.sleep(2 ** attempt)

    return FetchResult(task=task, status="failed", error=last_err if 'last_err' in dir() else "all URLs failed")


# ══════════════════════════════════════════════════════════════════════════════
# Batch fetch with progress
# ══════════════════════════════════════════════════════════════════════════════

def fetch_batch(tasks, cache_dir, variant_cache, max_workers=6,
                progress_callback=None):
    """Fetch a list of FetchTasks in parallel. Returns list of FetchResults."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {
            ex.submit(fetch_year, t, cache_dir, variant_cache): t
            for t in tasks
        }
        for fut in as_completed(futures):
            result = fut.result()
            results.append(result)
            if progress_callback:
                progress_callback(result, len(results), len(tasks))
    return results


# ══════════════════════════════════════════════════════════════════════════════
# Model discovery
# ══════════════════════════════════════════════════════════════════════════════

def discover_models(variable, scenarios, lat, lon, future_years,
                    cache_dir, variant_cache, probe_cache,
                    max_workers=12):
    """Probe all 34 models, return those available for all scenarios + historical."""
    mid_year = future_years[0] + (future_years[1] - future_years[0]) // 2
    confirmed = set(ALL_MODELS)

    for scen in scenarios:
        print(f"  Probing {scen} ({variable}) at year {mid_year} ...", flush=True)
        passed = set()
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {
                ex.submit(probe_model_cached, m, scen, variable,
                          mid_year, lat, lon,
                          variant_cache, probe_cache, cache_dir): m
                for m in confirmed
            }
            for fut in as_completed(futures):
                if fut.result():
                    passed.add(futures[fut])
        confirmed &= passed
        print(f"    {len(confirmed)} models pass {scen}")

    print(f"  Confirming historical ({variable}) ...", flush=True)
    hist_ok = set()
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {
            ex.submit(probe_model_cached, m, "historical", variable,
                      2000, lat, lon,
                      variant_cache, probe_cache, cache_dir): m
            for m in confirmed
        }
        for fut in as_completed(futures):
            if fut.result():
                hist_ok.add(futures[fut])

    models = sorted(hist_ok)
    print(f"    {len(models)} models confirmed for {variable}")
    return models


# ══════════════════════════════════════════════════════════════════════════════
# Build fetch plan
# ══════════════════════════════════════════════════════════════════════════════

def build_fetch_plan(models_per_variable, variables, scenarios,
                     baseline_years, future_years, lat, lon, cache_dir):
    """Generate all FetchTasks and check cache for each.

    Args:
        models_per_variable: dict mapping variable -> list of model names
        variables: list of variable names
        scenarios: list of scenario names (e.g. ["ssp245", "ssp585"])
        baseline_years: (start, end) inclusive
        future_years: (start, end) inclusive
        lat, lon: site coordinates
        cache_dir: Path to cache directory

    Returns:
        (all_tasks, cached_tasks, to_fetch_tasks, summary_dict)
    """
    all_tasks = []
    cached_tasks = []
    to_fetch = []

    for var in variables:
        models = models_per_variable.get(var, [])
        for model in models:
            # Historical baseline
            for yr in range(baseline_years[0], baseline_years[1] + 1):
                t = FetchTask(model, "historical", var, yr, lat, lon)
                all_tasks.append(t)
            # Future scenarios
            for scen in scenarios:
                for yr in range(future_years[0], future_years[1] + 1):
                    t = FetchTask(model, scen, var, yr, lat, lon)
                    all_tasks.append(t)

    for t in all_tasks:
        if check_cache(t, cache_dir):
            cached_tasks.append(t)
        else:
            to_fetch.append(t)

    # Build summary per variable
    var_summary = {}
    for var in variables:
        var_tasks = [t for t in all_tasks if t.variable == var]
        var_cached = [t for t in cached_tasks if t.variable == var]
        var_fetch = [t for t in to_fetch if t.variable == var]
        n_models = len(models_per_variable.get(var, []))
        var_summary[var] = {
            "total": len(var_tasks),
            "cached": len(var_cached),
            "to_fetch": len(var_fetch),
            "models": n_models,
        }

    summary = {
        "total": len(all_tasks),
        "cached": len(cached_tasks),
        "to_fetch": len(to_fetch),
        "by_variable": var_summary,
    }

    return all_tasks, cached_tasks, to_fetch, summary


# ══════════════════════════════════════════════════════════════════════════════
# Integrity check
# ══════════════════════════════════════════════════════════════════════════════

def validate_cache_file(path, variable):
    """Return True if the .nc file opens and contains the expected variable."""
    try:
        ds = xr.open_dataset(path, engine="scipy", decode_times=False)
        ok = variable in ds and len(ds[variable].values) > 0
        ds.close()
        return ok
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Display
# ══════════════════════════════════════════════════════════════════════════════

def print_summary_table(summary, total_models=34):
    """Print a formatted summary table."""
    by_var = summary["by_variable"]
    vars_list = list(by_var.keys())

    # Column widths
    w_var, w_cached, w_fetch, w_models = 10, 8, 10, 9
    sep = f"+-{'-'*w_var}-+-{'-'*w_cached}-+-{'-'*w_fetch}-+-{'-'*w_models}-+"
    hdr = f"| {'Variable':<{w_var}} | {'Cached':>{w_cached}} | {'To Fetch':>{w_fetch}} | {'Models':>{w_models}} |"

    print(sep)
    print(hdr)
    print(sep)
    for var in vars_list:
        v = by_var[var]
        models_str = f"{v['models']}/{total_models}"
        print(f"| {var:<{w_var}} | {v['cached']:>{w_cached}} | {v['to_fetch']:>{w_fetch}} | {models_str:>{w_models}} |")
    print(sep)
    print(f"| {'TOTAL':<{w_var}} | {summary['cached']:>{w_cached}} | {summary['to_fetch']:>{w_fetch}} | {'':>{w_models}} |")
    print(sep)


def print_progress(result, done, total):
    """Callback for fetch_batch: print single-line progress."""
    status_char = {"fetched": "+", "failed": "!", "cached": "."}
    c = status_char.get(result.status, "?")
    pct = done * 100 // total
    print(f"\r  [{done}/{total}] {pct}% {c} {result.task.model}/{result.task.variable}/{result.task.year}     ",
          end="", flush=True)
    if done == total:
        print()


# ══════════════════════════════════════════════════════════════════════════════
# Fetch report
# ══════════════════════════════════════════════════════════════════════════════

def save_fetch_report(results, summary, site_id, lat, lon,
                      models_unavailable, cache_dir):
    """Save a JSON fetch report to cache_dir."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path(cache_dir) / f"fetch_report_{ts}.json"

    failed_tasks = []
    for r in results:
        if r.status == "failed":
            failed_tasks.append({
                "model": r.task.model,
                "scenario": r.task.scenario,
                "variable": r.task.variable,
                "year": r.task.year,
                "error": r.error,
            })

    fetched_count = sum(1 for r in results if r.status == "fetched")
    failed_count = sum(1 for r in results if r.status == "failed")

    report = {
        "timestamp": datetime.now().isoformat(),
        "site": site_id,
        "lat": lat,
        "lon": lon,
        "summary": {
            "total_tasks": summary["total"],
            "already_cached": summary["cached"],
            "fetched": fetched_count,
            "failed": failed_count,
        },
        "models_unavailable": models_unavailable,
        "failed_tasks": failed_tasks,
    }

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved: {report_path}")
    return report_path


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="Fetch NEX-GDDP-CMIP6 daily climate data with smart caching.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--site", default="hayhurst_solar",
                   help="Site ID from sites.json (default: hayhurst_solar)")
    p.add_argument("--models", nargs="+", default=None,
                   help="Specific models (default: all 34, filtered by probe)")
    p.add_argument("--variables", nargs="+", default=None,
                   help="Variables to fetch (default: P1_core from variables.json)")
    p.add_argument("--scenarios", nargs="+", default=["ssp245", "ssp585"],
                   help="SSP scenarios (default: ssp245 ssp585)")
    p.add_argument("--baseline", nargs=2, type=int, default=[1985, 2014],
                   metavar=("START", "END"),
                   help="Baseline year range inclusive (default: 1985 2014)")
    p.add_argument("--future", nargs=2, type=int, default=[2026, 2055],
                   metavar=("START", "END"),
                   help="Future year range inclusive (default: 2026 2055)")
    p.add_argument("--max-workers", type=int, default=6,
                   help="Parallel download threads (default: 6)")
    p.add_argument("--dry-run", action="store_true",
                   help="Show fetch plan without downloading")
    p.add_argument("--integrity", action="store_true",
                   help="Validate cached files can be opened with xarray")
    p.add_argument("--discover-only", action="store_true",
                   help="Only probe model availability, don't fetch")
    p.add_argument("--skip-probe", action="store_true",
                   help="Skip model probing, assume all requested models exist")
    p.add_argument("--verbose", action="store_true",
                   help="Print per-file progress during fetch")
    return p.parse_args()


def main():
    args = parse_args()

    # ── Load config ──────────────────────────────────────────────────────
    sites = load_sites()
    if args.site not in sites:
        print(f"ERROR: site '{args.site}' not in sites.json. "
              f"Available: {list(sites.keys())}")
        sys.exit(1)

    site = sites[args.site]
    lat, lon = site["lat"], site["lon"]
    print(f"Site: {site['name']} ({args.site})")
    print(f"  lat={lat}, lon={lon}")

    variables = args.variables or load_p1_variables()
    scenarios = args.scenarios
    baseline_years = tuple(args.baseline)
    future_years = tuple(args.future)

    print(f"  Variables: {variables}")
    print(f"  Scenarios: {scenarios}")
    print(f"  Baseline: {baseline_years[0]}-{baseline_years[1]}")
    print(f"  Future:   {future_years[0]}-{future_years[1]}")

    # Ensure cache dir exists
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load caches ──────────────────────────────────────────────────────
    variant_cache = load_variant_cache(CACHE_DIR)
    probe_cache = load_probe_cache(CACHE_DIR)
    print(f"  Variant cache: {len(variant_cache)} entries")
    print(f"  Probe cache:   {len(probe_cache)} entries")

    # ── Model discovery ──────────────────────────────────────────────────
    models_unavailable = []
    models_per_variable = {}

    if args.models:
        # User specified models — use for all variables
        for var in variables:
            models_per_variable[var] = list(args.models)
        print(f"\nUsing specified models: {args.models}")
    elif args.skip_probe:
        for var in variables:
            models_per_variable[var] = list(ALL_MODELS)
        print(f"\nSkipping probe — using all {len(ALL_MODELS)} models")
    else:
        print(f"\nDiscovering models on THREDDS ...")
        all_discovered = set()
        for var in variables:
            discovered = discover_models(
                var, scenarios, lat, lon, future_years,
                CACHE_DIR, variant_cache, probe_cache
            )
            models_per_variable[var] = discovered
            all_discovered.update(discovered)

        models_unavailable = sorted(set(ALL_MODELS) - all_discovered)
        if models_unavailable:
            print(f"\n  Models NOT available for any variable: {models_unavailable}")

    if args.discover_only:
        print("\n--discover-only: done.")
        return

    # ── Build fetch plan ─────────────────────────────────────────────────
    print("\nBuilding fetch plan ...")
    all_tasks, cached_tasks, to_fetch, summary = build_fetch_plan(
        models_per_variable, variables, scenarios,
        baseline_years, future_years, lat, lon, CACHE_DIR
    )

    print()
    print_summary_table(summary, total_models=len(ALL_MODELS))

    # ── Integrity check ──────────────────────────────────────────────────
    if args.integrity and cached_tasks:
        print(f"\nValidating {len(cached_tasks)} cached files ...")
        bad_count = 0
        for i, t in enumerate(cached_tasks):
            path = check_cache(t, CACHE_DIR)
            if path and not validate_cache_file(path, t.variable):
                bad_path = path.with_suffix(".nc.bad")
                path.rename(bad_path)
                to_fetch.append(t)
                bad_count += 1
                if args.verbose:
                    print(f"  BAD: {path.name} -> .bad")
            if (i + 1) % 500 == 0:
                print(f"  checked {i+1}/{len(cached_tasks)} ...", flush=True)

        if bad_count:
            print(f"  {bad_count} files failed integrity — moved to .bad, "
                  f"added to fetch queue")
            summary["to_fetch"] += bad_count
            summary["cached"] -= bad_count
        else:
            print(f"  All {len(cached_tasks)} cached files OK")

    # ── Dry run ──────────────────────────────────────────────────────────
    if args.dry_run:
        if to_fetch:
            print(f"\n--dry-run: would fetch {len(to_fetch)} files. Examples:")
            for t in to_fetch[:10]:
                print(f"  {cache_key(t)}")
            if len(to_fetch) > 10:
                print(f"  ... and {len(to_fetch) - 10} more")
        else:
            print("\n--dry-run: nothing to fetch — cache is complete.")
        return

    # ── Fetch ────────────────────────────────────────────────────────────
    if not to_fetch:
        print("\nNothing to fetch — cache is complete.")
        return

    print(f"\nFetching {len(to_fetch)} files "
          f"(max_workers={args.max_workers}) ...")
    callback = print_progress if args.verbose else None
    results = fetch_batch(to_fetch, CACHE_DIR, variant_cache,
                          max_workers=args.max_workers,
                          progress_callback=callback)

    # ── Final report ─────────────────────────────────────────────────────
    fetched = sum(1 for r in results if r.status == "fetched")
    failed = sum(1 for r in results if r.status == "failed")
    print(f"\nDone: {fetched} fetched, {failed} failed")

    if failed:
        # Group failures by model
        fail_by_model = {}
        for r in results:
            if r.status == "failed":
                fail_by_model.setdefault(r.task.model, []).append(r)
        print("\nFailed downloads:")
        for model in sorted(fail_by_model):
            failures = fail_by_model[model]
            vars_failed = set(r.task.variable for r in failures)
            print(f"  {model}: {len(failures)} files "
                  f"({', '.join(sorted(vars_failed))})")

    save_fetch_report(results, summary, args.site, lat, lon,
                      models_unavailable, CACHE_DIR)


if __name__ == "__main__":
    main()
