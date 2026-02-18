# notebook_analysis/

Jupyter notebooks for exploratory analysis and visualisation.
Run notebooks in order — each one builds on the outputs of the previous.

---

## Notebook Index

| # | File | What it does | Inputs | Outputs | Implementation doc |
|---|---|---|---|---|---|
| 01 | `01_hayhurst_solar_scvr.ipynb` | Pull CMIP6 data for Hayhurst Solar (Culberson TX), compute SCVR, visualise exceedance curve shifts | Open-Meteo API | `data/raw/cmip6/hayhurst_solar/`, `data/processed/scvr/hayhurst_solar/` | [`docs/implementation/01_scvr_hayhurst_solar.md`](../docs/implementation/01_scvr_hayhurst_solar.md) |
| 02 | *(planned)* HCR derivation | Compute Hazard Change Ratios from SCVR using literature coefficients | SCVR Parquet | HCR tables | — |
| 03 | *(planned)* Asset performance | Run performance models with climate-adjusted weather | CMIP6 raw, InfraSure | Revenue projections | — |
| 04 | *(planned)* NAV impairment | Combine BI losses + IUL + revenue to compute NAV impairment ratio | All above | NAV impairment table | — |

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
