# data/schema/

The **single source of truth** for all data contracts in the LTRisk project.
Every file here is committed to version control.

> When a schema changes, update the relevant file here first —
> never silently change Parquet column layouts in notebooks.

---

## Files

| File | Format | Purpose |
|---|---|---|
| `VARIABLES.md` | Markdown | **Start here.** Human-readable priority tables, confirmed model list, SCVR logic map |
| `variables.json` | JSON | Machine-readable variable definitions, units, API params, priority tier, confirmed availability |
| `sites.json` | JSON | Pilot site registry (coordinates, capacity, climate zone, confirmed Open-Meteo model) |
| `cmip6_raw_schema.json` | JSON | Column spec and dtypes for raw CMIP6 Parquet files in `data/raw/cmip6/` |
| `noaa_schema.json` | JSON | Column spec for NOAA ground-station validation Parquet files in `data/raw/noaa/` |
| `scvr_schema.json` | JSON | Column spec, methodology, and downstream-use notes for SCVR output Parquet files |

---

## Priority Tiers (quick reference)

| Tier | Variables | When needed |
|---|---|---|
| **P1 — Core** | `tasmax`, `tasmin`, `tas`, `pr`, `sfcWind`, `hurs` | Notebook 01 (SCVR) |
| **P2 — Performance** | `rsds` | Notebook 03 (solar generation with pvlib) |
| **P3 — Additional** | `wind_speed_10m_max`, NOAA obs | Validation, later notebooks |

See `VARIABLES.md` for full variable tables and the confirmed model list.

---

## Confirmed API Model

The Open-Meteo Climate API only accepts specific model identifiers.
`MRI_ESM2_0` and `MPI_ESM1_2_HR` **return 400 errors** — they are not valid names.

**Primary model: `EC_Earth3P_HR`** — confirmed working, all P1+P2 variables.  
Verification script: `scripts/tests/probe_openmeteo_variables.py`  
Full results: `scripts/tests/probe_results.json`

---

## Usage in Code

Load schema files at the top of every notebook or script:

```python
import json
from pathlib import Path

REPO_ROOT = Path.cwd()  # or Path(__file__).resolve().parents[N]
SCHEMA_DIR = REPO_ROOT / "data" / "schema"

with open(SCHEMA_DIR / "sites.json") as f:
    SITES = json.load(f)

with open(SCHEMA_DIR / "variables.json") as f:
    VARIABLES = json.load(f)
```

Never hardcode site coordinates, variable units, or model names in notebooks.

---

## Adding a New Variable

1. Add entry to `variables.json` with all required fields including `priority` and `api_confirmed`.
2. Add column entry to `cmip6_raw_schema.json` with dtype, unit, and valid range.
3. Update `VARIABLES.md` table (the correct priority tier section).
4. Run `scripts/tests/probe_openmeteo_variables.py` to confirm availability.
5. Update the data acquisition cell in the relevant notebook.

## Adding a New Site

1. Add entry to `sites.json` with `open_meteo_model` set to a confirmed model name.
2. Re-run notebook 01 with the new `SITE_ID` — raw files will land automatically.
