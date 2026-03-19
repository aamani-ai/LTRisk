# data/schema/

The **single source of truth** for all data contracts in the LTRisk project.
Every file here is committed to version control.

> When a schema changes, update the relevant file here first —
> never silently change Parquet column layouts in scripts.

---

## Files

| File | Format | Purpose |
|---|---|---|
| `sites.json` | JSON | **Runtime config.** Pilot site registry — lat/lon, capacity, EUL, climate zone. Imported by `fetch_cmip6.py` and `compute_scvr.py` at runtime. |
| `variables.json` | JSON | **Runtime config.** Variable definitions — units, API params, priority tier, confirmed models. Imported at runtime. |
| `VARIABLES.md` | Markdown | Human-readable variable reference — priority tables, SCVR logic map |
| `cmip6_raw_schema.json` | JSON | Column spec and dtypes for raw CMIP6 Parquet files |
| `noaa_schema.json` | JSON | Column spec for NOAA ground-station validation Parquet files |
| `scvr_schema.json` | JSON | Column spec, methodology, and downstream-use notes for SCVR output Parquet |

---

## Priority Tiers

| Tier | Variables | Use |
|---|---|---|
| **P1 — Core** | `tasmax`, `tasmin`, `tas`, `pr`, `sfcWind`, `hurs` | SCVR computation (default for `compute_scvr.py`) |
| **P2 — Performance** | `rsds` | Solar generation modeling (pvlib) |
| **P3 — Additional** | `wind_speed_10m_max`, NOAA obs | Validation, future HCR calibration |

See `VARIABLES.md` for full variable tables.

---

## Data Source

**NASA NEX-GDDP-CMIP6** via THREDDS NCSS — 34 CMIP6 models, daily resolution, SSP2-4.5 + SSP5-8.5.

Data is fetched by `scripts/data/fetch_cmip6.py` and cached as NetCDF files in `data/cache/thredds/`.
31 of the 34 models are available (3 are not on THREDDS: CESM2-LENS, GFDL-CM4_gr2, HadGEM3-GC31-MM).

---

## Usage in Code

The production scripts import config via `fetch_cmip6.py` helper functions:

```python
# In compute_scvr.py:
from scripts.data.fetch_cmip6 import load_sites, load_p1_variables, ALL_MODELS

sites = load_sites()             # reads data/schema/sites.json
variables = load_p1_variables()  # reads data/schema/variables.json, returns P1 names
```

For direct access in notebooks:

```python
import json
from pathlib import Path

SCHEMA_DIR = Path.cwd() / "data" / "schema"

with open(SCHEMA_DIR / "sites.json") as f:
    SITES = json.load(f)

with open(SCHEMA_DIR / "variables.json") as f:
    VARIABLES = json.load(f)
```

Never hardcode site coordinates, variable units, or model names.

---

## Adding a New Variable

1. Add entry to `variables.json` with all required fields (`priority`, `unit`, `cmip6_standard_name`).
2. Add column entry to `cmip6_raw_schema.json` with dtype, unit, and valid range.
3. Update `VARIABLES.md` table in the correct priority tier section.
4. Run `python scripts/data/fetch_cmip6.py --variables your_var --discover-only` to confirm availability.
5. Fetch data and compute SCVR.

## Adding a New Site

1. Add entry to `sites.json` with lat, lon, asset_type, capacity_mw, eul_years, etc.
2. Fetch data: `python scripts/data/fetch_cmip6.py --site your_new_site`
3. Compute SCVR: `python scripts/analysis/scvr/compute_scvr.py --site your_new_site`
