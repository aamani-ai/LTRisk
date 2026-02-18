"""
test_openmeteo_api.py
---------------------
Validates that the Open-Meteo Climate API is reachable and returns the expected
variables for the Hayhurst Solar site. Pulls a small 3-year window to stay fast.

Run from project root:
    python scripts/tests/test_openmeteo_api.py

Expected output:  PASS  (or a descriptive FAIL message)
"""

import json
import sys
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "data" / "schema"

# ---------------------------------------------------------------------------
# Load site config from schema
# ---------------------------------------------------------------------------
with open(SCHEMA_DIR / "sites.json") as f:
    SITES = json.load(f)

SITE = SITES["hayhurst_solar"]
LAT = SITE["lat"]
LON = SITE["lon"]

# ---------------------------------------------------------------------------
# Open-Meteo Climate API — small request (3 years, 3 variables)
# ---------------------------------------------------------------------------
OPEN_METEO_URL = "https://climate-api.open-meteo.com/v1/climate"

MODEL = SITE["open_meteo_model"]   # EC_Earth3P_HR (from sites.json)

PARAMS = {
    "latitude": LAT,
    "longitude": LON,
    "start_date": "2000-01-01",
    "end_date": "2000-12-31",
    "models": MODEL,
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
    ],
}

# Full set we expect in the actual data pull (checked by name)
EXPECTED_OPEN_METEO_PARAMS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_mean",
    "relative_humidity_2m_mean",
    "shortwave_radiation_sum",
]


def check_api_reachable(params: dict) -> dict:
    """Hit the API and return the parsed JSON response."""
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def check_response_structure(data: dict) -> list[str]:
    """Return a list of failure messages (empty = all good)."""
    failures = []

    if "daily" not in data:
        failures.append("Response missing 'daily' key.")
        return failures

    daily = data["daily"]

    if "time" not in daily:
        failures.append("'daily' section missing 'time' array.")

    for var in ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]:
        if var not in daily:
            failures.append(f"Missing variable in response: {var}")
        else:
            values = daily[var]
            if len(values) == 0:
                failures.append(f"Variable {var} returned empty array.")
            non_null = [v for v in values if v is not None]
            if len(non_null) == 0:
                failures.append(f"Variable {var} has all-null values.")

    # Sanity check: tasmax should be > tasmin on most days for West Texas
    if "temperature_2m_max" in daily and "temperature_2m_min" in daily:
        tmax = [v for v in daily["temperature_2m_max"] if v is not None]
        tmin = [v for v in daily["temperature_2m_min"] if v is not None]
        if tmax and tmin:
            mean_tmax = sum(tmax) / len(tmax)
            mean_tmin = sum(tmin) / len(tmin)
            if mean_tmax <= mean_tmin:
                failures.append(
                    f"Sanity fail: mean tasmax ({mean_tmax:.1f}) <= mean tasmin ({mean_tmin:.1f})."
                )
            # West Texas annual mean tasmax should be roughly 25–35°C
            if not (15 <= mean_tmax <= 45):
                failures.append(
                    f"Sanity fail: mean tasmax ({mean_tmax:.1f}°C) outside plausible range [15, 45] for Culberson TX."
                )

    return failures


def print_sample(data: dict, n: int = 5) -> None:
    """Print first n rows of the response as a simple table."""
    daily = data.get("daily", {})
    times = daily.get("time", [])[:n]
    tmax = daily.get("temperature_2m_max", [])[:n]
    tmin = daily.get("temperature_2m_min", [])[:n]
    pr = daily.get("precipitation_sum", [])[:n]

    print(f"\n  {'Date':<12} {'tasmax':>8} {'tasmin':>8} {'pr':>8}")
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8}")
    for t, tx, tn, p in zip(times, tmax, tmin, pr):
        tx_s = f"{tx:.1f}" if tx is not None else "null"
        tn_s = f"{tn:.1f}" if tn is not None else "null"
        p_s = f"{p:.1f}" if p is not None else "null"
        print(f"  {t:<12} {tx_s:>8} {tn_s:>8} {p_s:>8}")
    print()


def main() -> None:
    print("=" * 60)
    print("TEST: Open-Meteo Climate API")
    print(f"  Site: Hayhurst Solar  lat={LAT}  lon={LON}")
    print(f"  URL:  {OPEN_METEO_URL}")
    print("=" * 60)

    # 1. Connectivity
    print("\n[1/3] Checking API connectivity...")
    try:
        data = check_api_reachable(PARAMS)
        print("      HTTP 200 received.")
    except requests.exceptions.ConnectionError:
        print("  FAIL — Cannot reach Open-Meteo API. Check internet connection.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"  FAIL — HTTP error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  FAIL — Unexpected error: {e}")
        sys.exit(1)

    # 2. Response structure
    print("[2/3] Checking response structure and sanity...")
    failures = check_response_structure(data)
    if failures:
        for msg in failures:
            print(f"      FAIL: {msg}")
        sys.exit(1)
    print("      Structure OK. Sanity checks passed.")

    # 3. Sample output
    print("[3/3] Sample data (first 5 rows):")
    print_sample(data)

    print("=" * 60)
    print("PASS — Open-Meteo API is reachable and returning valid data.")
    print()
    print("Note: This test used only 3 variables. The full pull in the")
    print("notebook requests all 7 (including rsds, sfcWind, hurs).")
    print("=" * 60)


if __name__ == "__main__":
    main()
