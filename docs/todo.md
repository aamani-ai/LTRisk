# LTRisk — Project TODO

> Last updated: 2026-03-09

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
- [ ] **CORRECTION: Refactor SCVR from 5 target years to annual computation**
  - Current: 20-year rolling windows at 5 discrete years (2030, 2035, 2040, 2045, 2050)
  - Target: Annual SCVR(t) for each year 2026–2055, per team framework annual tables
  - Annual SCVR maps directly to CFADS cash flow adjustments at each time step
  - Consider: use all 34 available models instead of 6 for per-year statistical robustness
  - Reference: `docs/learning/C_financial_translation/07_hcr_hazard_change.md` §3, `docs/learning/C_financial_translation/09_nav_impairment_chain.md` §1

### Notebook 04: HCR + EFR -> IUL -> NAV Impairment
- [ ] Design cell structure and plan
- [ ] Implement annual HCR(t) = SCVR(t) × hazard_scaling_factor (see `docs/learning/C_financial_translation/07_hcr_hazard_change.md`)
  - Per hazard: heat stress (×2.5), flood (×1.5-2.0), freeze-thaw (×1.0-1.5), soiling, fire weather
  - Allow negative HCR (warming reduces icing, freeze events)
  - Cross-validate against NB01 annual climate indices (heat_wave_days, frost_days, rx5day)
- [ ] Implement annual EFR(t) using engineering models (see `docs/learning/C_financial_translation/08_efr_equipment_degradation.md`)
  - Peck's thermal aging: AF = exp(Ea/k × (1/T_ref − 1/T_stress)) × (RH/RH_ref)^n
  - Coffin-Manson thermal cycling: N_f = C × (ΔT)^(−β)
  - Palmgren-Miner wind fatigue: D = Σ(n_i / N_i)
  - Report both linearised and full exponential Peck's estimates
- [ ] Combine EFR: weighted sum (w₁=0.7 Peck's, w₂=0.2 C-M, w₃=0.1 HCR-events)
- [ ] Compute IUL = EUL × (1 − EFR_combined_avg)
- [ ] Compute annual generation: Gen(t) = Gen_base × (1−std_degrad)^t × (1−climate_degrad) × (1−hazard_BI)
- [ ] NAV impairment = Σ (standard_Gen − climate_Gen) × price × discount
- [ ] Output annual HCR and EFR to Parquet
- [ ] Sensitivity analysis: report NAV under low/mid/high scaling factor scenarios

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
- [x] 00_index.md — Table of contents with section headers (A-D) and reading orders
- [x] A_climate_foundations/01_climate_primer.md
- [x] A_climate_foundations/02_cmip6_models.md
- [x] A_climate_foundations/03_scenarios_and_time_windows.md
- [x] B_scvr_methodology/04_scvr_methodology.md
- [x] B_scvr_methodology/05_variables_and_use_cases.md
- [x] B_scvr_methodology/06_scenario_comparison.md
- [x] C_financial_translation/07_hcr_hazard_change.md — HCR deep dive (hazard amplification, scaling factors, annual computation)
- [x] C_financial_translation/08_efr_equipment_degradation.md — EFR deep dive (Peck's, Coffin-Manson, Palmgren-Miner, IUL)
- [x] C_financial_translation/09_nav_impairment_chain.md — Complete SCVR→NAV pipeline (CFADS overlay, three channels, dollar amounts)
- [x] D_technical_reference/10_data_pipeline.md (was 08)
- [x] D_technical_reference/11_distribution_shift_methods.md (was 09)

### Implementation Docs (`docs/implementation/`)
- [x] 02_nex_gddp_cmip6_thredds.md
- [x] 03_integrated_scvr_cmip6.md — document nb03 design decisions

### Plan Docs (`docs/plan/`)
- [x] plan.md — Notebook 03 build plan

---

## Phase 3.5 — Visualization Improvements

> Identified after writing the SCVR learning docs. The core insight: at large n,
> SCVR ≈ fractional change in E[X] (the distribution mean). Plots should reflect this.

### `scripts/presentation/ensemble_exceedance.py`

- [ ] **Fix SCVR annotation text** (line 446): change `"SCVR (computed via value-integrated area):"` →
  `"SCVR = (E[X_future] − E[X_baseline]) / E[X_baseline]"` — more interpretable, matches what the math actually does at large n
- [ ] **Fix caption text** (line 470): change `"fractional change in value-integrated exceedance area"` →
  `"SCVR ≈ fractional change in mean daily value — computed via rank-based exceedance area ratio"`
- [ ] **Add mean (E[X]) vertical lines** on the traditional exceedance plot: vertical dashed lines at
  `np.nanmean(baseline_pool)`, `np.nanmean(ssp245_pool)`, `np.nanmean(ssp585_pool)` — the gap between
  these lines is proportional to SCVR and visually shows what the number measures
- [ ] **Add dual-convention subplot** (optional, educational): second panel showing SCVR convention
  (x = exceedance probability, y = value, sorted descending) — the SCVR area is the actual shaded gap
  between the baseline and future curves in this view. Helps explain why traditional view arrow ≠ SCVR.
- [ ] **CORRECTION: Support annual SCVR visualisation** — add mode to show SCVR progression over time
  (annual SCVR(t) line plot). Currently computes one SCVR per entire period; needs to support the
  annual framing from the team framework.

### Notebook 03 — Plot Improvements

- [ ] **Add mean lines** to existing exceedance curve plots (same as above) — makes SCVR interpretable
  without having to read the number
- [ ] **Label the P90 arrow** in exceedance plots as `"P90 shift (not SCVR)"` to avoid confusion between
  the horizontal threshold shift (arrow) and SCVR (which is a ratio of full-distribution areas)

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
