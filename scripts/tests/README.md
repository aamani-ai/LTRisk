# scripts/tests/

Quick validation scripts. Each script tests one specific thing, prints a clear
PASS or FAIL, and exits. Run these before executing notebooks to confirm that
your environment and external APIs are working correctly.

---

## Scripts

| Script | What it validates | Typical runtime |
|---|---|---|
| `test_openmeteo_api.py` | Open-Meteo Climate API reachable, returns core variables for Hayhurst Solar using `EC_Earth3P_HR` | ~10 s |
| `test_parquet_io.py` | Parquet write/read round-trip works, column dtypes match `cmip6_raw_schema.json` | <1 s |
| `test_scvr_math.py` | SCVR area-under-exceedance calculation is correct against a known analytical input | <1 s |
| `probe_openmeteo_variables.py` | Full API probe — discovers which models and variables are available; saves to `probe_results.json` | ~60 s |

---

## How to Run

From the project root with the venv activated:

```bash
source .venv/bin/activate

python scripts/tests/test_openmeteo_api.py
python scripts/tests/test_parquet_io.py
python scripts/tests/test_scvr_math.py
```

All three should print `PASS` before you run any notebook.

---

## What These Are NOT

- Not a pytest/unittest test suite
- Not run automatically in CI
- Not testing InfraSure models (those are tested separately when available)

Think of them as "smoke tests you run by hand when something seems off."
