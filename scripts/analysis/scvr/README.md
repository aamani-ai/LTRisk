# scripts/analysis/scvr/ — SCVR Computation Pipeline

## What This Does

`compute_scvr.py` is the canonical script for computing **SCVR (Severe Climate Variability Rating)**
from cached CMIP6 daily climate data. It reads NetCDF files produced by `fetch_cmip6.py`, computes
ensemble SCVR across all available models, and outputs Parquet files + a JSON report.

**Pipeline position:**

```
fetch_cmip6.py  →  compute_scvr.py  →  (later: compute_hcr.py → compute_efr.py → compute_nav.py)
     ↓                    ↓
data/cache/          data/processed/
thredds/*.nc         scvr/<site>/*.parquet
```

This script is **self-contained** — all SCVR math (exceedance area, decade anchors, shape metrics,
GEV/GPD fits) lives in this one file. No external math utils needed.

---

## Quick Start

```bash
# Activate the virtual environment
source .venv/bin/activate

# Dry-run: show what would be computed (no computation, no I/O)
python scripts/analysis/scvr/compute_scvr.py --dry-run

# Compute SCVR for Hayhurst Solar (default site)
python scripts/analysis/scvr/compute_scvr.py --site hayhurst_solar

# Single variable only
python scripts/analysis/scvr/compute_scvr.py --variables tasmax

# Single variable + single scenario
python scripts/analysis/scvr/compute_scvr.py --variables tasmax --scenarios ssp585

# Different site
python scripts/analysis/scvr/compute_scvr.py --site maverick_wind

# Custom year ranges
python scripts/analysis/scvr/compute_scvr.py --baseline 1985 2014 --future 2026 2055
```

**Prerequisite:** Data must be fetched first via `fetch_cmip6.py`. This script reads
from `data/cache/thredds/` only — no network calls.

---

## CLI Flags

| Flag | Default | Description |
|---|---|---|
| `--site SITE_ID` | `hayhurst_solar` | Site from `data/schema/sites.json` |
| `--variables VAR [...]` | P1_core from `variables.json` | Climate variables to compute |
| `--scenarios SCN [...]` | `ssp245 ssp585` | SSP scenarios |
| `--baseline START END` | `1985 2014` | Historical baseline year range (inclusive) |
| `--future START END` | `2026 2055` | Future projection year range (inclusive) |
| `--dry-run` | off | Show what would be computed without running |

---

## SCVR Methodology

### Definition

SCVR quantifies the **fractional increase** in the area under the empirical exceedance curve
for a future climate period compared to the historical baseline.

```
SCVR = (area_future - area_baseline) / area_baseline
```

A positive SCVR means extreme events are more frequent or more severe than baseline.
A negative SCVR means extremes are less frequent (e.g., fewer freeze days under warming).

### Exceedance Area Computation

1. Sort daily values in descending order
2. Assign exceedance probabilities on [0, 1] via `linspace(0, 1, n)`
3. Integrate using the trapezoidal rule: `area = trapz(sorted_values, exceedance_probs)`

At n > 10,000 pooled daily values, the trapezoid error is < 0.0001% — negligible.
The exceedance area equals the expected value E[X] of the distribution.

### Ensemble Pooling

All available models are **pooled** — their daily values are concatenated into one array
before computing exceedance. This means a 28-model ensemble with 30 years each produces
~306,600 daily values (28 × 30 × 365.25). Pooling captures both inter-model spread and
inter-annual variability in a single robust SCVR estimate.

### Baseline and Future Periods

| Period | Default | Source |
|---|---|---|
| **Baseline** | 1985–2014 (30 years) | CMIP6 `historical` scenario |
| **Future** | 2026–2055 (30 years) | CMIP6 `ssp245` or `ssp585` |

### Interpretation Guide

| SCVR Value | Meaning | Example |
|---|---|---|
| `= 0` | No change from baseline | sfcWind at inland sites |
| `0.00 – 0.10` | Low change | tasmax under SSP2-4.5 |
| `0.10 – 0.30` | Moderate change | tasmin under SSP5-8.5 |
| `0.30 – 0.60` | High change | Hypothetical extreme scenario |
| `> 0.60` | Very high change | Review — may indicate tail sensitivity |
| `< 0` | Less frequent extremes | Frost days under warming |

### Variable-Specific Strategy

Not all variables are suitable for annual interpolation. The strategy is variable-dependent:

| Strategy | Variables | Method |
|---|---|---|
| **anchor_3_linear** | `tasmax`, `tasmin`, `tas` | Split future into 3 non-overlapping 10-year decades. Compute SCVR per decade as "anchors". Fit a linear trend through the 3 midpoints. Interpolate to annual values. |
| **period_average** | `pr`, `hurs`, `sfcWind`, `rsds` | Use decade-level SCVR directly. No interpolation — these variables are too noisy for a linear fit (R² < 0.7). |

**Why temperature gets linear fitting:**

Temperature shows a clean, monotonic climate signal with R² > 0.95 across the 3 decade
anchors. The physical basis is clear: greenhouse gas forcing produces a roughly linear
warming trend over 30-year horizons.

**Why others don't:**

Precipitation (R² ≈ 0.59), wind (R² ≈ 0.13), and radiation (R² ≈ 0.31) are dominated
by natural variability at decadal scales. Fitting a line through 3 noisy points would
produce misleading annual values.

### Decade-Resolved SCVR

Three non-overlapping 10-year windows within the future period:

| Decade | Years |
|---|---|
| 2026–2035 | Near-term (already underway) |
| 2036–2045 | Mid-term |
| 2046–2055 | End of typical asset life |

Each decade's SCVR is computed by pooling all model daily values within that window
against the full baseline.

### Shape Metrics

For each decade and the baseline, the script computes:

| Metric | What it measures |
|---|---|
| `mean` | Central tendency |
| `std` / `variance` | Spread of daily values |
| `skewness` | Asymmetry (requires scipy) |
| `kurtosis` | Tail heaviness (requires scipy) |
| `p95` | 95th percentile |
| `p99` | 99th percentile |

### GEV / GPD Fitting (optional, requires scipy)

| Fit | What it models | Input |
|---|---|---|
| **GEV** (Generalised Extreme Value) | Annual block maxima distribution | One max per model per year |
| **GPD** (Generalised Pareto) | Peaks-over-threshold | Daily values above P95 |

Both return shape, location/scale parameters plus KS goodness-of-fit statistics.
These are optional diagnostics — SCVR computation does not depend on parametric fits.

---

## Input Requirements

Before running `compute_scvr.py`, data must be cached via `fetch_cmip6.py`:

```
data/cache/thredds/
├── ACCESS-CM2_historical_tasmax_1985_31.8160_-104.0853.nc
├── ACCESS-CM2_historical_tasmax_1986_31.8160_-104.0853.nc
├── ...
├── ACCESS-CM2_ssp245_tasmax_2026_31.8160_-104.0853.nc
├── ...
└── (thousands of .nc files)
```

**File naming:** `{MODEL}_{SCENARIO}_{VARIABLE}_{YEAR}_{LAT:.4f}_{LON:.4f}.nc`

A model is considered "complete" and included in computation only if it has cached files
for ALL years in both the baseline and future periods, across all requested scenarios.
Files smaller than 500 bytes are treated as corrupt.

The script auto-discovers which models have complete data — no manual model list needed.

---

## Output Files

All outputs saved to `data/processed/scvr/<site_id>/`:

### `cmip6_ensemble_scvr.parquet`

Main SCVR output — one row per variable × scenario (full future period, all models pooled).

| Column | dtype | Description |
|---|---|---|
| `site_id` | str | Site identifier |
| `scenario` | str | `ssp245` or `ssp585` |
| `variable` | str | Climate variable |
| `center_year` | int | Center of future window |
| `scvr` | float | SCVR value |
| `area_baseline` | float | Baseline exceedance area |
| `area_future` | float | Future exceedance area |
| `n_baseline_days` | int | Valid baseline days |
| `n_future_days` | int | Valid future days |
| `n_models` | int | Number of models in ensemble |
| `window_start_year` | int | First future year |
| `window_end_year` | int | Last future year |

### `cmip6_scvr_decade.parquet`

Decade-resolved SCVR — one row per variable × scenario × decade.

| Column | dtype | Description |
|---|---|---|
| `site_id` | str | Site identifier |
| `scenario` | str | SSP scenario |
| `variable` | str | Climate variable |
| `decade` | str | Decade label (e.g., `2026-2035`) |
| `scvr` | float | SCVR for this decade vs baseline |
| `area_baseline` | float | Baseline area |
| `area_future` | float | Decade future area |
| `n_future_days` | int | Pooled days in this decade |

### `cmip6_scvr_annual.parquet`

Annual SCVR values — method depends on variable strategy.

| Column | dtype | Description |
|---|---|---|
| `site_id` | str | Site identifier |
| `scenario` | str | SSP scenario |
| `variable` | str | Climate variable |
| `year` | int | Calendar year |
| `scvr` | float | Annual SCVR value |
| `method` | str | `anchor_3_linear` or `period_average` |
| `r2` | float | Linear fit R² (null for period_average) |

### `cmip6_shape_metrics.parquet`

Distribution shape statistics per period.

| Column | dtype | Description |
|---|---|---|
| `site_id` | str | Site identifier |
| `scenario` | str | `baseline` or SSP scenario |
| `variable` | str | Climate variable |
| `period` | str | `baseline`, `2026-2035`, etc. |
| `n_days` | int | Number of pooled daily values |
| `mean` | float | Mean |
| `std` | float | Standard deviation |
| `variance` | float | Variance |
| `skewness` | float | Fisher skewness (null without scipy) |
| `kurtosis` | float | Excess kurtosis (null without scipy) |
| `p95` | float | 95th percentile |
| `p99` | float | 99th percentile |

### `scvr_report.json`

Metadata and summary of the computation run.

```json
{
  "timestamp": "2026-03-19T14:30:00",
  "site_id": "hayhurst_solar",
  "lat": 31.816,
  "lon": -104.0853,
  "summary": {
    "ensemble_scvr_rows": 12,
    "decade_scvr_rows": 36,
    "shape_metrics_rows": 42,
    "annual_scvr_rows": 72
  },
  "ensemble_scvr": [ ... ],
  "gev_fits": { ... },
  "files_saved": [ ... ]
}
```

---

## Internal Functions Reference

| Function | Section | What it does |
|---|---|---|
| `cache_path()` | Data Loading | Build path to cached `.nc` file |
| `parse_nc()` | Data Loading | Parse NetCDF → `pd.Series` with DatetimeIndex (handles cftime calendars) |
| `unit_convert()` | Data Loading | K→°C for temperature, kg/m²/s→mm/day for precip |
| `discover_cached_models()` | Data Loading | Scan cache dir, return models with complete baseline + future coverage |
| `load_model_years()` | Data Loading | Load multiple years in parallel (ThreadPoolExecutor), concatenate |
| `load_data()` | Data Loading | Load baseline + future data for all models, apply unit conversion |
| `compute_scvr()` | SCVR Core | Empirical exceedance area ratio (the core formula) |
| `pool_window()` | Pooling | Pool daily values from all models within a year range |
| `compute_decade_scvr()` | Pooling | SCVR per decade window vs baseline |
| `compute_anchor_fit()` | Anchor Fitting | 3-anchor linear fit → annual SCVR interpolation |
| `compute_shape_metrics()` | Shape Metrics | mean, std, variance, skewness, kurtosis, P95, P99 |
| `compute_decade_shape()` | Shape Metrics | Shape metrics per decade window |
| `fit_gev()` | GEV/GPD | GEV fit to annual block maxima + KS test |
| `fit_gpd()` | GEV/GPD | GPD fit to peaks-over-threshold + KS test |
| `run_scvr_pipeline()` | Orchestration | Full pipeline for one variable: load → SCVR → decades → anchors → shape → GEV |
| `save_outputs()` | Output | Save all Parquet files + JSON report |

---

## Model Coverage

The script auto-discovers available models from cache. Typical counts for Hayhurst Solar:

| Variable | Models | Notes |
|---|---|---|
| tasmax | 28 | Most complete |
| tasmin | 28 | Same as tasmax |
| tas | 22 | 6 models missing `tas` (CESM2, CMCC-CM2-SR5, etc.) |
| pr | 31 | Widest coverage |
| sfcWind | 28 | — |
| hurs | 24 | BCC-CSM2-MR and NESM3 missing |
| rsds | 27 | — |

3 models are never available on THREDDS: CESM2-LENS, GFDL-CM4_gr2, HadGEM3-GC31-MM.

---

## Downstream Use

SCVR is the **central hub** connecting climate projections to financial impact:

```
SCVR(t)                           Annual climate shift per variable
  │
  ├──► HCR(t)                     Hazard-specific amplification
  │      │                        (heat ×2.5, flood ×1.5-2.0, etc.)
  │      │
  │      ├──► BI losses           Revenue lost to hazard events
  │      │
  │      └──► EFR(t)              Equipment degradation rate
  │             │                 (Peck's, Coffin-Manson, Palmgren-Miner)
  │             │
  │             └──► IUL          Asset life: 25yr → 21yr
  │
  └──► Gen(t) adjustment          Climate-adjusted annual generation
         │
         └──► CFADS(t)           Cash flow available for debt service
                │
                └──► NAV         Net Asset Value impairment
```

| Consumer | What it takes from SCVR |
|---|---|
| **HCR** (Hazard Change Ratio) | SCVR per variable → hazard-specific scaling factors |
| **EFR** (Equipment Failure Ratio) | SCVR → Peck's, Coffin-Manson, Palmgren-Miner models |
| **NAV** (Net Asset Value) | HCR + EFR → CFADS adjustment → impaired NAV |

---

## `extra/` — Supporting Scripts

| Script | Purpose |
|---|---|
| `extra/visualize_ensemble.py` | Presentation-grade plots: exceedance curves, time series, SCVR progression, decomposition |
| `extra/scvr_report_card_pdf.py` | PDF report card generation from SCVR outputs |

These are visualisation and reporting tools that consume `compute_scvr.py` outputs.

---

## Cross-References

- [`scripts/data/README.md`](../../data/README.md) — fetch_cmip6.py documentation
- [`data/schema/scvr_schema.json`](../../../data/schema/scvr_schema.json) — Output format specification
- [`docs/learning/B_scvr_methodology/04_scvr_methodology.md`](../../../docs/learning/B_scvr_methodology/04_scvr_methodology.md) — SCVR formula derivation
- [`docs/discussion/discussion_annual_scvr_methodology.md`](../../../docs/discussion/discussion_annual_scvr_methodology.md) — Anchor fit vs per-year SCVR analysis
