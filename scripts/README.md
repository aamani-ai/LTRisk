# scripts/

Runnable Python scripts for the LTRisk project.

---

## Pipeline

```
scripts/data/fetch_cmip6.py  →  scripts/analysis/scvr/compute_scvr.py  →  (later: compute_hcr.py → ...)
         ↓                                ↓
   data/cache/thredds/              data/processed/scvr/
   (cached NetCDF files)            (Parquet + JSON outputs)
```

---

## Structure

```
scripts/
├── README.md                               ← you are here
├── data/
│   ├── fetch_cmip6.py                      ← fetch CMIP6 data from THREDDS
│   └── README.md                           ← detailed documentation
├── analysis/
│   └── scvr/
│       ├── compute_scvr.py                 ← compute SCVR (self-contained)
│       ├── README.md                       ← detailed documentation
│       └── extra/
│           ├── visualize_ensemble.py       ← presentation-grade plots
│           └── scvr_report_card_pdf.py     ← PDF report generation
└── archive/                                ← superseded scripts (reference only)
    ├── shared/                             ← scvr_utils.py (absorbed into compute_scvr.py)
    ├── experiments/                         ← annual_scvr_test.py + output/
    └── tests/                              ← probe_openmeteo_variables.py, etc.
```

---

## Quick Start

```bash
source .venv/bin/activate

# Step 1: Check what data is cached
python scripts/data/fetch_cmip6.py --dry-run

# Step 2: Fetch CMIP6 data (first run only — ~10 min)
python scripts/data/fetch_cmip6.py --site hayhurst_solar

# Step 3: Compute SCVR
python scripts/analysis/scvr/compute_scvr.py --dry-run     # preview
python scripts/analysis/scvr/compute_scvr.py                # run
```

---

## Active Scripts

| Script | What it does | Docs |
|---|---|---|
| `data/fetch_cmip6.py` | Download and cache daily CMIP6 data from NASA THREDDS | [`data/README.md`](data/README.md) |
| `analysis/scvr/compute_scvr.py` | Compute SCVR from cached data — ensemble, decade, annual, shape metrics | [`analysis/scvr/README.md`](analysis/scvr/README.md) |
| `analysis/scvr/extra/visualize_ensemble.py` | Exceedance curves, time series, SCVR progression plots | — |
| `analysis/scvr/extra/scvr_report_card_pdf.py` | PDF report card from SCVR outputs | — |

---

## Archive

Scripts in `archive/` are superseded by the active scripts above. They are kept for
reference and audit trail, not for production use.

| Archived | Superseded by |
|---|---|
| `archive/shared/scvr_utils.py` | Math absorbed into `analysis/scvr/compute_scvr.py` |
| `archive/experiments/annual_scvr_test.py` | Analysis done — results documented in `docs/discussion/` |
| `archive/tests/` | Validation scripts from early development |
