# notebook_analysis/

Jupyter notebooks for exploratory analysis and visualisation.
Run notebooks in order — each one builds on the outputs of the previous.

---

## Notebook Index

| # | File | What it does | Inputs | Outputs | Implementation doc |
|---|---|---|---|---|---|
| 01 | `01_hayhurst_solar_scvr.ipynb` | Pull CMIP6 data for Hayhurst Solar (Culberson TX), compute SCVR, visualise exceedance curve shifts | Open-Meteo API | `data/raw/cmip6/hayhurst_solar/`, `data/processed/scvr/hayhurst_solar/` | [`docs/implementation/01_scvr_hayhurst_solar.md`](../docs/implementation/01_scvr_hayhurst_solar.md) |
| 02 | `02_NEX_GDDP_CMIP6_THREDDS.ipynb` | THREDDS pipeline development — server-side point extraction from NASA NEX-GDDP-CMIP6, multi-model probing, cftime handling, caching | NASA THREDDS | `data/cache/thredds/` | [`docs/implementation/02_nex_gddp_cmip6_thredds.md`](../docs/implementation/02_nex_gddp_cmip6_thredds.md) |
| 03 | `03_integrated_scvr_cmip6.ipynb` | Fuse SCVR math (nb01) + THREDDS pipeline (nb02) — ensemble SCVR for 2 TX sites across SSP2-4.5 and SSP5-8.5 using pooled daily data from up to 6 CMIP6 models | NASA THREDDS, `data/schema/sites.json`, `data/schema/variables.json` | `data/processed/scvr/<site>/cmip6_ensemble_scvr.parquet` | [`docs/plan/plan.md`](../docs/plan/plan.md) |
| 04 | *(planned)* HCR + EFR | Compute Hazard Change Ratios from SCVR, then Engineering Failure Rates using Peck's model, Coffin-Manson, Palmgren-Miner | SCVR Parquet | HCR/EFR tables | — |
| 05 | *(planned)* NAV impairment | Combine BI losses + IUL shortening + revenue to compute NAV impairment ratio | All above | NAV impairment table | — |

---

## How to Run

```bash
# From project root
source .venv/bin/activate
jupyter lab
```

Then open the notebook from JupyterLab. Notebooks assume the working directory
is the **project root** (not `notebook_analysis/`). Path resolution at the top
of each notebook uses `pathlib` to find the repo root reliably.

---

## Before Running Notebook 01

Run the three test scripts to confirm the environment is working:

```bash
python scripts/tests/test_openmeteo_api.py
python scripts/tests/test_parquet_io.py
python scripts/tests/test_scvr_math.py
```
