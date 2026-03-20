# notebook_analysis/

Interactive Jupyter notebooks for exploratory analysis.

## Active Notebooks

| # | File | Status | What it does |
|---|---|---|---|
| 04 | `04_hcr_hazard_change_ratio.ipynb` | Done | HCR: 10 hazards × 2 scenarios × 30 years (Pathway A for temp, B for precip) |

## Archive

NB01-03 were stepping stones — each superseded by production scripts:

| Notebook | Superseded by |
|---|---|
| `01_hayhurst_solar_scvr.ipynb` | `scripts/analysis/scvr/compute_scvr.py` |
| `02_NEX_GDDP_CMIP6_THREDDS.ipynb` | `scripts/data/fetch_cmip6.py` |
| `03_integrated_scvr_cmip6.ipynb` | `scripts/analysis/scvr/compute_scvr.py` |

Archived notebooks are in `archive/` for reference.

## How to Run

```bash
source .venv/bin/activate
jupyter lab
```

Notebooks assume the working directory is the **project root** (not `notebook_analysis/`).
