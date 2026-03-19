"""
probe_openmeteo_variables.py
-----------------------------
Systematically probes the Open-Meteo Climate API to discover exactly which
variables and models are available, and what the response structure looks like.

Results are printed and saved to scripts/tests/probe_results.json for use
in updating data/schema/variables.json.

Run from project root:
    python scripts/tests/probe_openmeteo_variables.py
"""

import json
import sys
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = Path(__file__).parent / "probe_results.json"

OM_CLIMATE_URL = "https://climate-api.open-meteo.com/v1/climate"
OM_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Site: Hayhurst Solar, Culberson TX
LAT, LON = 31.815992, -104.0853

# Short window to keep requests fast
TEST_START = "2000-01-01"
TEST_END   = "2000-12-31"

# ── All candidate daily variables to probe ─────────────────────────────────────
CANDIDATE_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_mean",
    "wind_speed_10m_max",
    "relative_humidity_2m_mean",
    "relative_humidity_2m_max",
    "relative_humidity_2m_min",
    "shortwave_radiation_sum",
    "snowfall_sum",
    "cloud_cover_mean",
    "pressure_msl_mean",
    "et0_fao_evapotranspiration_sum",
    "soil_moisture_0_to_10cm_mean",
]

# ── Models to probe ────────────────────────────────────────────────────────────
MODELS = [
    "MRI_ESM2_0",
    "MPI_ESM1_2_HR",
    "EC_Earth3P_HR",
    "CMCC_CM2_VHR4",
]

results = {}


def probe_one(model: str, variables: list[str],
              start: str, end: str, url: str) -> dict:
    """
    Probe a single request. Returns dict with:
        status_code, available_vars, error (if any), sample row
    """
    params = {
        "latitude": LAT, "longitude": LON,
        "start_date": start, "end_date": end,
        "models": model,
        "daily": variables,
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            body = resp.json()
            daily = body.get("daily", {})
            available = [v for v in variables if v in daily and daily[v] is not None]
            # Sample first non-null value per variable
            sample = {v: daily[v][0] if daily[v] else None for v in available}
            return {
                "status": 200,
                "available": available,
                "missing": [v for v in variables if v not in available],
                "sample_2000_01_01": sample,
                "error": None,
            }
        else:
            return {
                "status": resp.status_code,
                "available": [],
                "missing": variables,
                "sample_2000_01_01": {},
                "error": resp.text[:300],
            }
    except Exception as e:
        return {
            "status": -1,
            "available": [],
            "missing": variables,
            "sample_2000_01_01": {},
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 1: Each model with ALL candidate variables
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 70)
print("PROBE 1: Climate API — all candidate vars, each model")
print("=" * 70)

for model in MODELS:
    print(f"\n  Model: {model}")
    r = probe_one(model, CANDIDATE_VARS, TEST_START, TEST_END, OM_CLIMATE_URL)
    results[f"climate_{model}_all_vars"] = r
    if r["status"] == 200:
        print(f"    AVAILABLE ({len(r['available'])}): {r['available']}")
        if r["missing"]:
            print(f"    MISSING   ({len(r['missing'])}): {r['missing']}")
    else:
        print(f"    ERROR {r['status']}: {r['error'][:120]}")
        # Try probing variable by variable to find which one fails
        print("    Probing variable by variable...")
        available_single = []
        for var in CANDIDATE_VARS:
            r2 = probe_one(model, [var], TEST_START, TEST_END, OM_CLIMATE_URL)
            status = "OK" if r2["status"] == 200 else f"FAIL({r2['status']})"
            print(f"      {var:<45} {status}")
            if r2["status"] == 200:
                available_single.append(var)
            time.sleep(0.3)
        results[f"climate_{model}_single_probe"] = {"available": available_single}
    time.sleep(0.5)

# ─────────────────────────────────────────────────────────────────────────────
# PROBE 2: Check what's in the historical (pre-2015) vs future range
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("PROBE 2: Historical (2000) vs Future (2030) for best model")
print("=" * 70)

# Use the first model that succeeded (or MRI_ESM2_0)
for model in MODELS:
    key = f"climate_{model}_all_vars"
    if key in results and results[key]["status"] == 200 and results[key]["available"]:
        best_model = model
        best_vars  = results[key]["available"]
        break
    key2 = f"climate_{model}_single_probe"
    if key2 in results and results[key2]["available"]:
        best_model = model
        best_vars  = results[key2]["available"]
        break
else:
    best_model = "MRI_ESM2_0"
    best_vars  = ["temperature_2m_max", "temperature_2m_min",
                  "precipitation_sum", "wind_speed_10m_mean", "shortwave_radiation_sum"]

print(f"\n  Using model: {best_model}  vars: {best_vars}")

r_hist = probe_one(best_model, best_vars, "2000-01-01", "2000-12-31", OM_CLIMATE_URL)
r_fut  = probe_one(best_model, best_vars, "2030-01-01", "2030-12-31", OM_CLIMATE_URL)
results["historical_probe"] = {"model": best_model, "result": r_hist}
results["future_probe"]     = {"model": best_model, "result": r_fut}

print(f"  Historical 2000: status={r_hist['status']}  available={r_hist['available']}")
print(f"  Future     2030: status={r_fut['status']}   available={r_fut['available']}")

# ─────────────────────────────────────────────────────────────────────────────
# PROBE 3: ERA5 Archive API (for reference — actual observations)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("PROBE 3: ERA5 Archive API (open-meteo archive, actual observations)")
print("=" * 70)

ERA5_VARS = [
    "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
    "precipitation_sum", "wind_speed_10m_mean", "wind_speed_10m_max",
    "relative_humidity_2m_mean", "relative_humidity_2m_max",
    "shortwave_radiation_sum",
]

r_era5 = probe_one("ERA5", ERA5_VARS, "2000-01-01", "2000-12-31", OM_ARCHIVE_URL)
results["era5_archive_probe"] = r_era5

if r_era5["status"] == 200:
    print(f"  ERA5 Archive AVAILABLE ({len(r_era5['available'])}): {r_era5['available']}")
    if r_era5["missing"]:
        print(f"  ERA5 Archive MISSING  ({len(r_era5['missing'])}): {r_era5['missing']}")
    print(f"  Sample 2000-01-01: {r_era5['sample_2000_01_01']}")
else:
    print(f"  ERA5 Archive ERROR {r_era5['status']}: {r_era5['error'][:200]}")
    # Try without model param
    params = {
        "latitude": LAT, "longitude": LON,
        "start_date": "2000-01-01", "end_date": "2000-12-31",
        "daily": ERA5_VARS,
    }
    resp = requests.get(OM_ARCHIVE_URL, params=params, timeout=30)
    print(f"  Without model param: status={resp.status_code}")
    if resp.status_code == 200:
        daily = resp.json().get("daily", {})
        available = [v for v in ERA5_VARS if v in daily and daily[v] is not None]
        print(f"  Available without model: {available}")
        results["era5_archive_no_model"] = {"status": 200, "available": available}

# ─────────────────────────────────────────────────────────────────────────────
# Save results
# ─────────────────────────────────────────────────────────────────────────────
with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print(f"Full results saved → {RESULTS_PATH}")
print("=" * 70)

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print("\nSUMMARY")
print("-" * 70)
for key, val in results.items():
    if "single_probe" in key:
        continue
    avail = val.get("available") or (val.get("result", {}).get("available") if isinstance(val.get("result"), dict) else [])
    status = val.get("status") or val.get("result", {}).get("status", "?")
    print(f"  {key:<45} status={status}  available={len(avail) if avail else 0} vars")
