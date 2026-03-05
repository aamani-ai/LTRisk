# LTRisk — Project TODO

> Last updated: 2026-03-05

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| [x] | Done |
| [ ] | Pending |
| [~] | In progress |

---

## Phase 1 — Notebooks & Core Pipeline

### Notebook 01: Hayhurst Solar SCVR (Single Model)
- [x] `compute_scvr` function — exceedance area ratio
- [x] Exceedance curve plots
- [x] Rolling window analysis (2030–2050)

### Notebook 02: NEX-GDDP-CMIP6 THREDDS Pipeline
- [x] THREDDS NCSS point extraction (`build_thredds_url`, `fetch_year`)
- [x] cftime calendar handling (standard / noleap / 360_day)
- [x] Unit conversion (K->C, kg/m2/s->mm/day)
- [x] Multi-model discovery and parallel probing
- [x] NetCDF file caching (`data/cache/thredds/`)

### Notebook 03: Integrated SCVR + CMIP6 Ensemble
- [x] Fuse SCVR math (nb01) + THREDDS pipeline (nb02)
- [x] Asset-lifetime aware windows (construction_start + lifespan)
- [x] Historical/SSP stitching at 2014 boundary
- [x] Ensemble pooling (concatenate daily values across models)
- [x] Parallel model probing with disk cache (`model_probe_cache.json`)
- [x] SCVR computation — ensemble + per-model
- [x] Output to Parquet (`data/processed/scvr/<site>/cmip6_ensemble_scvr.parquet`)
- [x] Plots: exceedance curves, bar chart, spaghetti, strip plot
- [ ] **Run notebook end-to-end** — verify all cells execute without error
- [ ] Verify SCVR signs make physical sense (tasmax +, sfcWind ~0, SSP585 > SSP245)

### Notebook 04: HCR + EFR -> IUL -> NAV Impairment
- [ ] Design cell structure and plan
- [ ] Implement HCR = SCVR x hazard_scaling_factor
- [ ] Implement EFR using Peck's model, Coffin-Manson, Palmgren-Miner
- [ ] Business interruption and useful life shortening
- [ ] NAV = asset_value - (BI_losses + IUL_shortening_cost)

---

## Phase 2 — Data & Caching Improvements

### Local Data Consolidation (NEW)
> Instead of reading 1000s of individual `.nc` files every run, consolidate
> all fetched daily data into a single Parquet per site.

- [ ] After fetch loop, save all daily data to `data/processed/daily_climate/<site>/all_daily.parquet`
  - Columns: `date | variable | scenario | model | value`
  - One file per site (~10-20 MB)
- [ ] Add check at top of fetch loop — if Parquet exists, load from it and skip THREDDS
- [ ] Keep `.nc` cache as fallback / source of truth for re-consolidation

**Workflow after implementation:**
```
First run:    THREDDS --> .nc cache --> DATA dict --> save all_daily.parquet
Future runs:  all_daily.parquet --> DATA dict  (instant, skip THREDDS)
```

### Other Data Tasks
- [ ] Validate cache integrity — check for corrupted/incomplete `.nc` files
- [ ] Add cache size reporting (how much disk space used)
- [ ] Consider compression for Parquet outputs (snappy vs gzip)

---

## Phase 3 — Documentation

### Learning Guides (`docs/learning/`)
- [x] 00_index.md — Table of contents with reading orders
- [x] 01_climate_science_fundamentals.md
- [x] 02_cmip6_and_climate_models.md
- [x] 03_ssp_scenarios.md
- [x] 04_scvr_methodology.md
- [x] 05_data_pipeline.md
- [x] 06_baseline_vs_future.md
- [x] 07_from_climate_to_finance.md

### Implementation Docs (`docs/implementation/`)
- [x] 02_nex_gddp_cmip6_thredds.md
- [ ] 03_integrated_scvr_cmip6.md — document nb03 design decisions

### Plan Docs (`docs/plan/`)
- [x] plan.md — Notebook 03 build plan

---

## Phase 4 — Future Work

- [ ] Add more sites beyond Hayhurst and Maverick
- [ ] Support additional SSP scenarios (SSP1-2.6, SSP3-7.0)
- [ ] Expand beyond 6 models per combo (currently capped by MAX_MODELS)
- [ ] Uncertainty quantification — confidence intervals on SCVR
- [ ] Automated report generation (PDF/HTML from notebook outputs)
- [ ] API wrapper for SCVR computation (standalone from notebooks)

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `notebook_analysis/01_hayhurst_solar_scvr.ipynb` | Single-model SCVR prototype |
| `notebook_analysis/02_NEX_GDDP_CMIP6_THREDDS.ipynb` | THREDDS pipeline development |
| `notebook_analysis/03_integrated_scvr_cmip6.ipynb` | Main SCVR computation (ensemble) |
| `data/schema/sites.json` | Site coordinates and metadata |
| `data/schema/variables.json` | Variable definitions and priorities |
| `data/schema/scvr_schema.json` | Output Parquet column spec |
| `data/cache/thredds/` | Cached NetCDF files from THREDDS |
| `data/processed/scvr/` | SCVR output Parquet files |
