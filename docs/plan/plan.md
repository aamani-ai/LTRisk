# Notebook 03 Build Plan: Integrated SCVR + NASA NEX-GDDP-CMIP6

## Objective

Build `notebook_analysis/03_integrated_scvr_cmip6.ipynb` by combining:
- **SCVR math** from Notebook 01 (`compute_scvr` function — exceedance area ratio)
- **THREDDS data pipeline** from Notebook 02 (NASA NEX-GDDP-CMIP6, multi-model ensemble)

The notebook takes a site's **construction start year + operational lifespan** as the primary inputs and outputs a definitive SCVR score per climate variable per scenario, representing the asset's full lifetime exposure.

---

## Design Decision: Why Dynamic Asset Timeline?

In Notebook 01, SCVR is computed at five rolling 20-year windows (2030, 2035, 2040, 2045, 2050).
This works for exploratory analysis but is wrong for financial modeling:

- A solar farm built in 2026 with a 30-year lifespan is only exposed during **2026–2055**.
- Averaging SCVR over IPCC standard blocks (e.g. 2021–2040) misses the tail-risk years 2041–2055 when hardware is most degraded and climate is most severe.
- NPV and IUL models require exact year-over-year exposure, not averaged blocks.

**Notebook 03 design:** compute ONE SCVR per variable per scenario = full asset lifetime window vs CMIP6 historical baseline. This gives a single, auditable number that maps directly into the EFR/HCR impairment formulas.

---

## Important: `compute_scvr` Signature (from Notebook 01)

```python
def compute_scvr(baseline_values: np.ndarray, future_values: np.ndarray) -> dict:
    """Returns {'scvr': float, 'area_baseline': float, 'area_future': float,
                'n_baseline_days': int, 'n_future_days': int}"""
```

The function takes two flat numpy arrays. There is NO threshold parameter and NO `exceed_higher` flag. It computes the full exceedance area ratio (integral of the sorted descending distribution). This is correct — do not add parameters that do not exist.

---

## Notebook 03 Cell Structure

### Section 0 — Setup & Configuration

```
Cell 0: Markdown header + pipeline overview diagram
Cell 1: Imports
  - numpy, pandas, xarray, requests, cftime (from nb02)
  - matplotlib, seaborn (for plots)
  - concurrent.futures, tqdm
  - pathlib, warnings

Cell 2: Asset + scenario configuration
  SITES = [
      {
          "name": "Hayhurst Texas Solar",
          "lat": 31.815992,
          "lon": -104.0853,
          "asset_type": "Solar",
          "capacity_mw": 24.8,
          "construction_start_year": 2026,
          "operational_lifespan": 30,    # future window: 2026–2055
      },
      {
          "name": "Maverick Creek Wind",
          "lat": 31.262546,
          "lon": -99.84396,
          "asset_type": "Wind",
          "capacity_mw": 491.6,
          "construction_start_year": 2026,
          "operational_lifespan": 30,
      }
  ]

  SCENARIOS = ["ssp245", "ssp585"]

  VARIABLES = [
      {"id": "tasmax", "name": "Daily Max Temp",    "units": "C"},
      {"id": "tasmin", "name": "Daily Min Temp",    "units": "C"},
      {"id": "pr",     "name": "Precipitation",     "units": "mm/day"},
      {"id": "sfcWind","name": "Wind Speed",        "units": "m/s"},
      {"id": "rsds",   "name": "Solar Radiation",   "units": "W/m2"},   # Solar only
      {"id": "hurs",   "name": "Relative Humidity", "units": "%"},      # Solar only
  ]

  BASELINE_YEARS = (1985, 2014)   # 30-year CMIP6 historical standard
  MODELS_TO_TRY  = [              # Probe these; use whichever respond
      "ACCESS-CM2", "ACCESS-ESM1-5", "BCC-CSM2-MR",
      "CMCC-ESM2", "CanESM5", "MIROC6",
      "MPI-ESM1-2-HR", "MPI-ESM1-2-LR", "MRI-ESM2-0"
  ]
  MAX_MODELS = 6   # cap for speed
  CACHE_DIR  = Path("cmip6_cache")
```

### Section 1 — THREDDS Data Pipeline (ported from Notebook 02)

```
Cell 3: Markdown — "THREDDS extraction: server-side point query, no full file download"

Cell 4: build_thredds_url(model, scenario, variable, year, lat, lon) -> str
  Port directly from Notebook 02. No changes needed.

Cell 5: fetch_thredds(model, scenario, variable, year, lat, lon, cache=True) -> pd.DataFrame
  Port directly from Notebook 02.
  - cftime calendar handling (standard / noleap / 360_day)
  - Unit conversion: K -> C, pr flux -> mm/day
  - File cache in CACHE_DIR

Cell 6: probe_model(model, scenario, variable, year, lat, lon) -> bool
  Port directly from Notebook 02.

Cell 7: temporal_aggregate(df, mode) -> pd.Series
  Port directly from Notebook 02.
  mode options: "annual_mean", "annual_sum", "annual_max"
```

### Section 2 — Data Fusing (asset-lifetime aware)

```
Cell 8: Markdown — explain the historical/SSP boundary (2014/2015)
  "For assets starting before 2015, we stitch CMIP6 historical data (ends 2014)
   with SSP projection data (starts 2015) into one continuous array."

Cell 9: discover_models(site, scenario, variable) -> list[str]
  For each model in MODELS_TO_TRY:
    probe using mid-lifespan year (construction_start + lifespan // 2)
    If probe passes -> include in available list
  Cap at MAX_MODELS.
  Print summary table of available models per site/scenario/variable.

Cell 10: fetch_asset_data(site, model, scenario, variable) -> (base_df, fut_df)
  """
  Returns two DataFrames:
    base_df: annual aggregates for BASELINE_YEARS (1985-2014), historical scenario
    fut_df:  annual aggregates for asset lifetime (construction_start -> construction_start + lifespan - 1)
             stitching historical (<=2014) + ssp (>=2015) as needed
  """

  KEY LOGIC — data fusion at 2014/2015 boundary:
    if construction_start_year <= 2014:
      years_hist = range(construction_start_year, min(2014, end_year) + 1)
      years_ssp  = range(max(2015, construction_start_year), end_year + 1)
      fetch years_hist with scenario="historical"
      fetch years_ssp  with scenario=<ssp>
      concatenate both into fut_df
    else:
      fetch all years with scenario=<ssp>

Cell 11: fetch_all_data() — main execution loop
  For each site × variable × scenario:
    Run discover_models()
    For each available model, run fetch_asset_data() in ThreadPoolExecutor
    Collect results_base[model] = pd.Series and results_fut[model] = pd.Series
    Store in RESULTS dict keyed by (site_name, variable_id, scenario)

  RESULTS structure:
    RESULTS[(site, var, scen)] = {
        "site": ...,
        "variable": ...,
        "scenario": ...,
        "models": [...],
        "base_df": pd.DataFrame(index=years, columns=models),  # shape (30, n_models)
        "fut_df":  pd.DataFrame(index=years, columns=models),  # shape (lifespan, n_models)
    }
```

### Section 3 — SCVR Computation (ported from Notebook 01)

```
Cell 12: Markdown — explain SCVR concept + formula

Cell 13: compute_scvr(baseline_values, future_values) -> dict
  Port EXACTLY from Notebook 01. Do not modify the signature.
  Returns: {scvr, area_baseline, area_future, n_baseline_days, n_future_days}

Cell 14: Run SCVR on all ensemble results
  For each key in RESULTS:
    base_vals = RESULTS[key]["base_df"].values.flatten()  # pool all models + years
    fut_vals  = RESULTS[key]["fut_df"].values.flatten()
    base_vals = base_vals[~np.isnan(base_vals)]
    fut_vals  = fut_vals[~np.isnan(fut_vals)]

    result = compute_scvr(base_vals, fut_vals)

    Append to scvr_rows:
      Site, Variable, Scenario, SCVR, n_models, n_baseline_days, n_future_days,
      window_start (construction_start_year), window_end (construction_start + lifespan - 1)

  df_scvr = pd.DataFrame(scvr_rows)
  Save to: data/processed/scvr/<site_id>/cmip6_ensemble_scvr.parquet

Cell 15: Display styled SCVR table
  Pivot: rows=Variable, cols=Scenario, values=SCVR
  Style with background_gradient, highlight direction (+ = more risk, - = less risk)
  Also show SSP245 vs SSP585 delta column
```

### Section 4 — Visualisations

```
Cell 16: Markdown

Cell 17: plot_spaghetti(result_key) — per-model time series
  Port from Notebook 02.
  Show each model as a thin line (spaghetti), P10/P50/P90 envelope as shaded band.
  Two panels: baseline period (1985-2014) and future period (asset lifetime).
  For tasmax and pr, one plot per site.

Cell 18: SCVR comparison bar chart
  X-axis: climate variables
  Y-axis: SCVR value
  Two bars per variable: ssp245 (blue) and ssp585 (red)
  Horizontal line at 0
  One chart per site.
  Annotation: asset lifetime window dates, number of models used.

Cell 19: Exceedance curve shift plot (from Notebook 01 Plot A)
  Reuse the same exceedance curve visual but now powered by the multi-model ensemble.
  Baseline distribution (pooled historical) vs Future distribution (pooled asset lifetime).
  For tasmax and pr, one plot per site.
```

### Section 5 — Summary Output

```
Cell 20: Print/display final SCVR table formatted for use in Notebook 04 (HCR/EFR)
  Show:
    - Site, Variable, Scenario
    - SCVR value (the key output)
    - n_models used (confidence indicator)
    - Asset lifetime window
    - Direction label: "More stress" / "Less stress" / "Neutral"

Cell 21: Save outputs
  data/processed/scvr/<site_id>/cmip6_ensemble_scvr.parquet  <- main output
  data/processed/scvr/<site_id>/figures/03_*.png             <- all plots
```

---

## Data Flow Summary

```
CMIP6 Historical (1985-2014)          SSP Future (asset lifetime)
     via THREDDS                            via THREDDS
          │                                      │
          ▼                                      ▼
  Pool all models × years              Pool all models × years
  into one flat baseline array         into one flat future array
     (n_models × 30 years of           (n_models × lifespan years
      daily/annual values)              of daily/annual values)
          │                                      │
          └────────────┬─────────────────────────┘
                       ▼
              compute_scvr(baseline_vals, future_vals)
                       │
                       ▼
              SCVR per variable per scenario
                       │
                       ▼
              → Notebook 04: HCR + EFR → IUL → NAV impairment
```

---

## Files to Create / Modify

| Action | File | Notes |
|---|---|---|
| CREATE | `notebook_analysis/03_integrated_scvr_cmip6.ipynb` | The main deliverable |
| DELETE | `generate_03.py` | Temp script — had wrong `compute_scvr` signature; superseded by this plan |
| KEEP | `notebook_analysis/01_hayhurst_solar_scvr.ipynb` | Source of `compute_scvr` — do not modify |
| KEEP | `notebook_analysis/02_NEX_GDDP_CMIP6_THREDDS.ipynb` | Source of THREDDS pipeline — do not modify |

---

## Known Issues in `generate_03.py` (why it was not used)

1. **Wrong `compute_scvr` signature**: The script calls `compute_scvr(base_vals, fut_vals, threshold, exceed_higher=...)` but the actual function in Notebook 01 takes only `(baseline_values, future_values)` — no threshold, no exceed_higher flag.

2. **Fragile cell-index references**: `nb2['cells'][7]`, `nb2['cells'][9]`, etc. — any edit to Notebook 02 would silently break this, pulling the wrong cell.

3. **Incomplete data fusion logic**: The script had `attempt_historical=True` for future years too, which would incorrectly fetch historical data for 2026+ (those years don't exist in the historical experiment).

---

## Verification Steps (manual, run cells sequentially)

1. After `fetch_all_data()`: confirm `RESULTS` dict has entries for both sites, both scenarios, all variables. Print shape of `base_df` and `fut_df` for one entry — should be `(30, n_models)` and `(lifespan, n_models)`.

2. After `compute_scvr` loop: verify SCVR signs make physical sense:
   - `tasmax` → positive (hotter future)
   - `tasmin` → positive (warmer nights)
   - `sfcWind` → near-zero (no strong signal expected)
   - SSP585 SCVR > SSP245 SCVR for temperature variables

3. Check `n_baseline_days` and `n_future_days` in output: should reflect `n_models × 30 × 365` and `n_models × lifespan × 365` approximately (some variation for leap years and noleap calendars).

4. Visual check: spaghetti plot should show model spread. Ensemble P90 for future tasmax should be clearly higher than baseline P90.
