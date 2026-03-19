# Notebook 03 — Integrated SCVR: Multi-Model CMIP6 Ensemble

*Implementation notes for `notebook_analysis/03_integrated_scvr_cmip6.ipynb`*

**Sites:** Hayhurst Texas Solar (Culberson County, 24.8 MW) + Maverick Creek Wind (Concho County, 491.6 MW)
**Data source:** NASA NEX-GDDP-CMIP6 via NCCS THREDDS NCSS (34 models, daily, 0.25° grid)
**Scenarios:** SSP2-4.5 (moderate) and SSP5-8.5 (high emissions) — true separation, unlike Notebook 01
**Baseline:** 1985–2014 (30 years, CMIP6 standard)
**Future:** 2026–2055 (30-year asset lifetime, construction start 2026)

---

## Where This Fits in the LTRisk Pipeline

```
  Notebook 01 (SCVR Math)            Notebook 02 (THREDDS Pipeline)
  ┌─────────────────────────┐        ┌──────────────────────────────────┐
  │ compute_scvr()          │        │ fetch_year() via NCSS            │
  │ exceedance area ratio   │        │ multi-model probing              │
  │ (trapezoid integral)    │        │ cftime calendar handling         │
  │ SINGLE model only       │        │ disk caching (.nc per year)      │
  └────────────┬────────────┘        └──────────────────┬───────────────┘
               │                                        │
               └────────────────┬───────────────────────┘
                                ▼
                   THIS NOTEBOOK (03)
                   ┌──────────────────────────────────────────┐
                   │ Dynamic asset timeline (2026–2055)        │
                   │ Up to 6 CMIP6 models per variable/scen   │
                   │ Pool N models × 30 yrs of daily values   │
                   │ SCVR per variable per scenario            │
                   │ SSP2-4.5 vs SSP5-8.5 side-by-side        │
                   └──────────────────┬───────────────────────┘
                                      │
                                      ▼
                   Notebook 04: HCR + EFR → IUL → NAV impairment
```

**What this notebook adds over Notebooks 01 and 02:**

| Feature | Notebook 01 | Notebook 02 | Notebook 03 |
|---|---|---|---|
| Data source | Open-Meteo API | NASA THREDDS | NASA THREDDS |
| Models | 1 (EC-Earth3P-HR) | up to 6 (probed) | All available (typically 13, was 6) |
| Scenarios | Effectively SSP5-8.5 only | SSP2-4.5 or SSP5-8.5 | Both simultaneously |
| Asset timeline | Rolling 20-yr windows | Configurable | Dynamic from `sites.json` |
| SCVR computation | Yes | No | Yes (ported from nb01) |
| Output | Per-window SCVR | Statistical envelopes | Ensemble SCVR Parquet |

---

## Key Design Decisions

### 1. Dynamic Asset Timeline (not IPCC blocks)

Notebook 01 used rolling 20-year windows (2030, 2035, 2040…). This is correct for
exploratory analysis but wrong for financial modeling. A solar farm built in 2026 with
a 30-year lifespan is only exposed to climate during **2026–2055**.

```
  IPCC standard blocks (wrong for this use case):
  2021────────────────2040  (Near-term, 20 years)
  2041────────────────2060  (Mid-term)

  This notebook (asset-lifetime aware):
  2026────────────────────────────────2055  (Hayhurst + Maverick, 30 years)
               ↑ exact asset window ↑

  The tail years (2041–2055) have the most severe climate AND the most
  degraded hardware — averaging them into a 2021-2040 block is a blind spot.
```

The asset timeline comes from `data/schema/sites.json` + `construction_start_year`
and `operational_lifespan` set in the configuration cell.

### 2. Ensemble Pooling (not per-model averaging)

For SCVR, we **concatenate** daily values from all models into one flat array before
computing. This is different from averaging model outputs first.

```
  Per-model averaging approach (wrong):
    model_1: [34.1, 35.2, 33.8, ...] → mean=34.4
    model_2: [33.9, 36.1, 34.2, ...] → mean=34.7
    ensemble_mean = mean(34.4, 34.7)  ← destroys daily distribution shape

  Ensemble pooling approach (correct):
    pool = [34.1, 35.2, 33.8, ...,   ← model_1 daily values
            33.9, 36.1, 34.2, ...]   ← model_2 daily values appended
    compute_scvr(pool_baseline, pool_future)  ← one exceedance curve from all days
```

Pooling preserves the full daily distribution across models, so the exceedance
curve is built from N_models × 30 years × ~365 days per year ≈ 65,000+ data points.
This gives a robust estimate of the tail behaviour.

### 3. Daily Data — No Annual Aggregation

SCVR must be computed on **daily** values. Notebook 02 aggregated to annual means
for its statistical envelope output — that is not appropriate here.

```
  Annual aggregation (used in nb02 statistical envelopes):
    365 daily values → 1 annual mean
    30 years × 1 value = 30 data points per model
    Exceedance curve has only 30 × N_models points — smooth but loses tail detail

  Daily (used here for SCVR):
    30 years × 365 days = 10,950 daily values per model
    6 models × 10,950 = 65,700 data points
    Exceedance curve captures true tail structure — the heat waves, the wet bursts
```

Annual averages compress away the variance that SCVR measures. A year with 40
days above 40°C and a year with 5 days above 40°C both average to the same annual
mean temperature — but their exceedance curves look very different.

### 4. True SSP Scenario Separation

Notebook 01 used Open-Meteo HighResMIP data, which only ran under one emissions
pathway (effectively SSP5-8.5). The `ssp245` labels in nb01 were metadata, not real
scenario branching.

NASA NEX-GDDP-CMIP6 has **separate model runs** for each SSP. The same 34 models
were each run independently under SSP2-4.5 and SSP5-8.5 boundary conditions. This
allows genuine side-by-side comparison.

---

## Section-by-Section Notes

### Section 0 — Setup & Configuration

Loads three canonical schemas:
- `data/schema/sites.json` — coordinates, capacity, asset type
- `data/schema/variables.json` — P1/P2 priority tiers, units, scvr_direction
- `data/schema/scvr_schema.json` — output column specification

Variables per site:
- **Both sites**: `tasmax, tasmin, tas, pr, sfcWind, hurs` (P1_core)
- **Hayhurst Solar only**: + `rsds` (solar irradiance, P2_performance)

### Section 1 — THREDDS NCSS Pipeline

Ported directly from Notebook 02. Four core functions:

| Function | Purpose |
|---|---|
| `build_thredds_url(model, scenario, variable, year, lat, lon)` | Constructs v2/v1 URL pair for THREDDS NCSS |
| `fetch_year(...)` | Downloads one year, handles cftime, caches as `.nc` |
| `fetch_model_years(...)` | Fetches multiple years in parallel via `ThreadPoolExecutor` |
| `unit_convert(series, variable)` | K→°C for temperature, flux→mm/day for precipitation |
| `probe_model(...)` | HEAD/GET check — does this model have data for this year? |

**Cache location**: `data/cache/thredds/<model>_<scenario>_<variable>_<year>_<lat>_<lon>.nc`

First run downloads from NASA THREDDS (~5-15 sec per year per model). Subsequent
runs load from the local `.nc` cache in milliseconds.

### Section 2 — Model Discovery

Probe all 34 NEX-GDDP models to find which ones have data for each
(site, variable, scenario) combination. `MAX_MODELS = None` uses all available.

**Two-step probing:**
1. Probe SSP availability at `mid_year = 2026 + 15 = 2041` (mid-lifespan)
2. Confirm historical availability at year 2000

Both steps run in parallel (`ThreadPoolExecutor(max_workers=12)`).

**Disk cache for probe results** (`data/cache/thredds/model_probe_cache.json`):
- First run: probes THREDDS HTTP (slow, one request per model)
- Subsequent runs: reads from JSON cache (instant)
- Delete the file to force a fresh probe

With `MAX_MODELS = None`, typically 13 models pass for temperature variables.

### Section 3 — Data Fetch Loop

For each (site, variable, scenario, model):

```
  Baseline fetch:
    fetch_model_years(model, "historical", var, range(1985, 2015), ...)
    → 30 years of daily data, always from historical experiment

  Future fetch (our asset starts 2026, so purely SSP):
    fetch_model_years(model, scen, var, range(2026, 2056), ...)
    → 30 years of daily data from SSP experiment

  Stitching logic (for assets starting before 2015):
    if future_start <= 2014:
        hist_part = fetch historical up to 2014
        ssp_part  = fetch SSP from 2015 onwards
        combine   = pd.concat([hist_part, ssp_part])
    else:
        all SSP (our case — 2026 > 2014)
```

Result stored in `DATA[(site_id, variable, scenario)]`:
```python
{
    "models": ["ACCESS-CM2", "MIROC6", ...],
    "baseline_daily": {"ACCESS-CM2": pd.Series([...]), ...},
    "future_daily":   {"ACCESS-CM2": pd.Series([...]), ...},
}
```

### Section 4 — SCVR Computation

`compute_scvr` ported **exactly** from Notebook 01 (cell `fe500174`):

```python
def compute_scvr(baseline_values: np.ndarray, future_values: np.ndarray) -> dict:
    b = np.sort(baseline_values[~np.isnan(baseline_values)])[::-1].astype(float)
    f = np.sort(future_values[~np.isnan(future_values)])[::-1].astype(float)
    exc_b = np.linspace(0, 1, len(b))
    exc_f = np.linspace(0, 1, len(f))
    area_b = float(np.trapezoid(b, exc_b))
    area_f = float(np.trapezoid(f, exc_f))
    scvr = (area_f - area_b) / area_b if area_b != 0 else 0.0
    return {'scvr': scvr, 'area_baseline': area_b, 'area_future': area_f,
            'n_baseline_days': len(b), 'n_future_days': len(f)}
```

**Do not add parameters to this function.** It takes two flat numpy arrays only.
No threshold parameter, no `exceed_higher` flag.

Two SCVR computations per (site, variable, scenario):
1. **Ensemble pooled** — all models concatenated → one robust SCVR
2. **Per-model** — each model independently → spread/uncertainty

### Section 3b — Decade Analysis, Anchor Fitting, Shape Metrics, GEV (NEW — March 2026)

Added to address senior reviewer feedback that exceedance curves showed only horizontal shift,
not shape/slope change over time. See `docs/discussion/discussion_decade_shape_analysis.md`.

**Uses shared module** (`scripts/shared/scvr_utils.py`) with inline fallbacks if unavailable.

#### A. Decade-Resolved SCVR

Split the 30-year future into 3 non-overlapping decades. For each (site, variable, scenario, decade),
pool all models' daily values within that decade and compute SCVR against the full baseline.

```
Decade windows: 2026-2035 | 2036-2045 | 2046-2055
Pool size: ~47,000 daily values per decade (13 models × 10 years × 365 days)
```

#### B. Anchor-Based Annual SCVR (temperature only)

For variables with `SCVR_STRATEGY = "anchor_3_linear"` (tasmax, tasmin, tas):
- Compute SCVR at each decade midpoint (2030.5, 2040.5, 2050.5) → 3 anchor points
- Fit linear trend via `np.polyfit(mids, scvrs, 1)`
- Interpolate to 30 annual values (2026–2055)
- Report R² on anchor points

For variables with `SCVR_STRATEGY = "period_average"` (pr, hurs, sfcWind, rsds):
- Use decade-level SCVR directly (no interpolation — signal too noisy)

#### C. Shape Metrics per Decade

For each (site, variable, scenario) × each decade + baseline:
- Mean, standard deviation, variance, skewness, P95, P99

These reveal whether the distribution is changing shape (variance/kurtosis increase)
or simply shifting (only mean changes).

#### D. GEV Fit (temperature only)

`scipy.stats.genextreme.fit()` on annual block maxima across all models:
- Shape parameter ξ: tracks tail evolution (ξ < 0 light tail, ξ ≈ 0 Gumbel, ξ > 0 heavy tail)
- Location μ: tracks where the annual max sits (analogous to mean shift)
- Scale σ: tracks annual max variability
- **Diagnostics:** KS D-statistic, KS p-value, log-likelihood, AIC (added 2026-03-13)

#### E. GPD Fit — Peaks-Over-Threshold (temperature only)

`scipy.stats.genpareto.fit()` on daily values above P95 threshold (Pickands-Balkema-de Haan):
- Shape ξ, scale σ, threshold, exceedance rate
- Gives exceedance probabilities in the **same space** as the empirical daily curve
- **Diagnostics:** KS D-statistic (D < 0.02 = excellent fit), log-likelihood, AIC

Shared functions: `fit_gpd()`, `exceedance_curve_gpd()` in `scripts/shared/scvr_utils.py`.

**Note:** Both GEV and GPD are computed as diagnostics — SCVR uses empirical area. The
presentation script also prints a 3-method comparison (empirical, normal, direct mean)
proving they agree to 6 decimal places at n > 10,000.

#### F. SCVR Report Card — Tail Confidence Diagnostic (NEW — March 2026)

SCVR (the headline number) captures the **mean** of the distribution shift. But hazards and
financial impacts depend on **tail** behavior — which SCVR can miss entirely for some variables
(see [discussion_scvr_method_equivalence.md §13](../discussion/discussion_scvr_method_equivalence.md)).

The report card answers: **"How much should I trust this SCVR number?"**

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                SCVR Decomposition (existing)                    │
  │  5 diagnostics: per-model spread, P95/P99 tail, GEV ξ,        │
  │  variance decomposition, leave-one-out sensitivity             │
  └──────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │              SCVR Report Card (NEW)                             │
  │                                                                 │
  │  Inputs from decomposition:                                     │
  │    mean_scvr ─────────────────┐                                 │
  │    tail_scvr_p95 ─────────────┤                                 │
  │    cvar95_ratio ──────────────┤─→ compute_report_card()         │
  │    extreme_scvr_p99 ──────────┤   (scvr_utils.py)              │
  │    per_model_iqr ─────────────┘                                 │
  │                                                                 │
  │  Outputs:                                                       │
  │    mean_tail_ratio ── P95/Mean (how much tail tracks the mean)  │
  │    tail_confidence ── HIGH | MODERATE | LOW | DIVERGENT         │
  │                                                                 │
  │  Computed at TWO levels:                                        │
  │    Epoch   (full 30yr: 2026-2055)  ── one card per scenario     │
  │    Decade  (3 × 10yr windows)      ── shows if trust changes    │
  └─────────────────────────────────────────────────────────────────┘
```

**Tail Confidence algorithm:**

```
  Signs differ (mean vs P95)?  ──yes──→  DIVERGENT
         │ no                             (mean says one thing, tail says another)
         ▼
  Mean-Tail Ratio < 0.3?  ──yes──→  LOW
         │ no                       (tail barely moves despite mean shift)
         ▼
  Model IQR > 2 × |mean|? ──yes──→  LOW
         │ no                       (models disagree too much)
         ▼
  Mean-Tail Ratio > 0.6?  ──yes──→  HIGH
         │ no                       (tail tracks mean closely, models agree)
         ▼
       MODERATE
```

**What each flag means for downstream use:**

| Flag | Meaning | Pipeline action |
|------|---------|-----------------|
| HIGH | Mean and tail agree, models converge. SCVR is a reliable proxy. | Use SCVR directly in Channel 2 (EFR/IUL). HCR Pathway A cross-validates with B. |
| MODERATE | Partial agreement or moderate model spread. SCVR is usable with caveats. | Use SCVR but flag uncertainty range. Prefer Pathway B for HCR. |
| LOW | Weak mean-tail link or large model disagreement. SCVR underestimates tail risk. | Do not use SCVR alone. Pathway B mandatory for HCR. Report P95 alongside. |
| DIVERGENT | Mean and tail have opposite signs. SCVR gives wrong direction. | SCVR is misleading — Pathway B only. Flag in stakeholder reports. |

**Actual results — Hayhurst Solar (Epoch):**

| Variable | SSP245 SCVR | Confidence | SSP585 SCVR | Confidence | M-T Ratio |
|----------|:-----------:|:----------:|:-----------:|:----------:|:---------:|
| tasmax   | +0.069      | HIGH       | +0.080      | HIGH       | 0.71      |
| tasmin   | +0.144      | MODERATE   | +0.174      | MODERATE   | 0.56      |
| tas      | +0.088      | HIGH       | +0.104      | HIGH       | 0.68      |
| pr       | -0.001      | DIVERGENT  | -0.007      | DIVERGENT  | N/A       |
| sfcWind  | -0.022      | MODERATE   | -0.026      | HIGH       | 0.59/0.67 |
| hurs     | -0.031      | MODERATE   | -0.036      | MODERATE   | 0.56      |
| rsds     | +0.005      | MODERATE   | +0.003      | MODERATE   | N/A       |

Key observations:
- **tasmin is MODERATE** (not HIGH) — nighttime temperatures have a less uniform tail response
  (M-T ratio 0.56, just below the 0.6 threshold). The tail amplification is weaker at night.
- **pr is DIVERGENT** — mean SCVR is near zero but tail metrics are positive. Pathway B mandatory.
- **rsds is MODERATE** — both mean and tail signals are very small (< 0.005). Not DIVERGENT
  because the guard threshold correctly prevents false alarms when both signals are near noise.

**Decade progression reveals emerging divergence:**

For precipitation (pr), the decade report cards show confidence degrading over time
as the mean drifts negative while tail extremes grow:

```
  pr SSP245 decade progression:
    2026-2035:  Mean=+0.030  P95=+0.010  → LOW (ratio 0.34)
    2036-2045:  Mean=-0.016  P95=+0.021  → DIVERGENT (signs differ)
    2046-2055:  Mean=-0.018  P95=+0.024  → DIVERGENT (signs differ)
```

Function: `compute_report_card()` in `scripts/shared/scvr_utils.py` (Section 4).
Called from: `plot_scvr_decomposition()` in `scripts/presentation/ensemble_exceedance.py`.

#### New Plots

- **Plot E: Decade-Resolved Exceedance** — 2×2 for temperature (top: full empirical, bottom:
  tail zoom with GPD dashed + GEV dotted + P95 marker + KS annotation); 1×2 for others
- **Plot F: SCVR Progression** — anchor diamonds + linear fit (temperature) or decade bars (others)
- **Plot G: Shape Metrics Table** — variance, P95, P99 per decade; GEV ξ evolution

#### New Outputs

```
data/processed/scvr/<site>/cmip6_scvr_decade.parquet
data/processed/scvr/<site>/cmip6_shape_metrics.parquet
```

Existing `cmip6_ensemble_scvr.parquet` unchanged. Schema in `data/schema/scvr_schema.json`.

---

## Output Files

| File | Contents |
|---|---|
| `data/processed/scvr/<site>/cmip6_ensemble_scvr.parquet` | Ensemble SCVR, one row per (variable, scenario) |
| `data/processed/presentation/<site>/<var>/scvr_decomposition_<var>.json` | Per-model SCVR, tail metrics, GEV, variance, LOO, **epoch + decade report cards** |
| `data/processed/presentation/<site>/<var>/scvr_decomposition_<var>.png` | 4-panel decomposition figure (per-model strip, mean vs tail, GEV xi, variance) |
| `data/processed/presentation/<site>/<var>/scvr_summary_<var>.json` | SCVR + decade breakdown + shape metrics + GEV/GPD + anchor fits + report cards |
| `data/cache/thredds/*.nc` | Cached daily NetCDF point extractions |
| `data/cache/thredds/model_probe_cache.json` | Probe results cache |
| `docs/exports/03_integrated_scvr_cmip6.html` | Rendered notebook with all outputs |

**Parquet schema** (from `data/schema/scvr_schema.json`):

| Column | Type | Description |
|---|---|---|
| `site_id` | str | `hayhurst_solar` or `maverick_wind` |
| `scenario` | str | `ssp245` or `ssp585` |
| `model` | str | `ensemble_pooled` (or model name for per-model) |
| `center_year` | int | Midpoint of future window (2040) |
| `variable` | str | `tasmax`, `pr`, etc. |
| `scvr` | float | The main output |
| `area_baseline` | float | Trapezoid area under baseline exceedance curve |
| `area_future` | float | Trapezoid area under future exceedance curve |
| `window_start_year` | int | 2026 |
| `window_end_year` | int | 2055 |
| `n_baseline_days` | int | Total daily values used (N_models × ~10,950) |
| `n_future_days` | int | Total daily values used (N_models × ~10,950) |

---

## Interpreting SCVR Results

```
  SCVR = (area_future - area_baseline) / area_baseline

  Positive SCVR → future distribution shifted toward more extreme values
  Negative SCVR → future has fewer extremes (e.g., fewer frost days)
  SCVR = 0      → no change in distribution shape
```

Expected signs by variable (West Texas physical intuition):

| Variable | Expected sign | Reason |
|---|---|---|
| `tasmax` | + | Hotter daytime temperatures under all scenarios |
| `tasmin` | + | Nights warming faster than days (confirmed in nb01: +17.9% by 2050) |
| `tas` | + | Mean temp follows tasmax/tasmin |
| `pr` | ± | Near-term wetter; long-term drier. Distribution-dependent |
| `sfcWind` | ~0 | No strong projected wind signal for TX |
| `hurs` | − | West Texas drying under warming (confirmed nb01) |
| `rsds` | + | Slightly more irradiance under warming/drying |

SSP5-8.5 SCVR should always be ≥ SSP2-4.5 SCVR for temperature variables — if not,
check for probe or data issues with specific models.

---

## Known Limitations

### 1. ~~MAX_MODELS = 6 cap~~ (RESOLVED)

`MAX_MODELS` is now `None` — all available models are used. Typically 13 for temperature
variables. The models are sorted alphabetically but all are included.

### 2. r1i1p1f1 ensemble member only

All URLs use `r1i1p1f1` (first run, first initialisation, first physics, first
forcing). Some models have multiple ensemble members. Using only r1i1p1f1 slightly
underestimates internal variability. Acceptable for screening; not for final reports.

### 3. No local daily consolidation (yet)

After the first run, daily data sits in thousands of individual `.nc` files.
Future improvement: consolidate into `data/processed/daily_climate/<site>/all_daily.parquet`
so re-runs load from one file instead of reading the full `.nc` cache.
See `docs/todo.md` (Phase 2 — Local Data Consolidation).

### 4. Exceedance curve for precipitation

The `compute_scvr` function sorts values **descending** — this is correct for
variables like `tasmax` where higher = worse. For `pr`, a positive SCVR means more
total precipitation area (wetter), which could mean either more frequent rain or
more intense events. The SCVR does not distinguish these — HCR computation in
Notebook 04 will need to decompose this.

---

## Next Steps → Notebook 04

SCVR feeds into:

```
  SCVR (this notebook)
      │
      ├── × hazard_scaling_factor  →  HCR (Hazard Change Ratio)
      │       from published damage functions (flood, hail, fire, dust)
      │
      └── → EFR (Equipment Failure Ratio)
              via Peck's model         → thermal aging rate
              via Coffin-Manson        → freeze-thaw fatigue
              via Palmgren-Miner       → structural fatigue (wind)
                      │
                      ▼
               IUL (Impaired Useful Life) = EUL × [1 - Σ(EFR × SCVR)]
                      │
                      ▼
               NAV = asset_value - (BI_losses + IUL_shortening_cost)
```

---

## Time Series Plot — What P10/P50/P90 Actually Mean

The `ensemble_timeseries_<var>.png` plot (generated by `scripts/presentation/ensemble_exceedance.py`) does a **two-step aggregation** that must be understood to read the plot correctly:

```
Step 1: daily values → annual mean per model
        resample("YE").mean()
        Result: one value per year per model (e.g., 30 years × 6 models = 180 values)

Step 2: annual means → P10/P50/P90 across models, per year
        quantile(0.10/0.50/0.90, axis=1)  ← axis=1 = across models
        Result: three time series showing how much models disagree
```

**What each visual element shows:**

| Element | What it is | What it is NOT |
|---|---|---|
| Thin spaghetti lines | One model's annual mean per year | Daily values |
| Thick line (P50) | The median model for that year | Median daily temperature |
| Shaded band (P10–P90) | Model spread — how much the 6 models disagree | Intra-year variability |

**Why this is the right visualization:**
- The x-axis is **year**, so each point is already a 365-day average
- The P10–P90 band shows **model uncertainty** (epistemic: which model is "right"?)
- Natural variability (aleatory: year-to-year weather noise) is visible in the spaghetti wiggle
- The future band width vs baseline band width shows whether models agree more or less about the future

**What this does NOT show:**
- Daily extremes (use the exceedance curve plot for that)
- Intra-year percentiles (e.g., "P90 of daily temperatures in a given year")
- The SCVR-relevant quantity (SCVR uses all 65,700 daily values pooled, not annual means)

---

*Related documentation:*
- [docs/implementation/ensemble_exceedance_script.md](ensemble_exceedance_script.md) — Presentation script implementation (same pipeline, CLI-runnable)
- [docs/discussion/discussion_decade_shape_analysis.md](../discussion/discussion_decade_shape_analysis.md) — Team feedback and decade analysis rationale
- [docs/discussion/discussion_annual_scvr_methodology.md](../discussion/discussion_annual_scvr_methodology.md) — Annual SCVR computation options, anchor fit evidence
- [docs/learning/04_scvr_methodology.md](../learning/B_scvr_methodology/04_scvr_methodology.md) — SCVR formula and intuition
- [docs/learning/10_data_pipeline.md](../learning/D_technical_reference/10_data_pipeline.md) — THREDDS, NetCDF, caching
- [docs/learning/03_scenarios_and_time_windows.md](../learning/A_climate_foundations/03_scenarios_and_time_windows.md) — why 1985-2014 baseline, why the 2015-2025 gap is intentional
- [docs/learning/09_nav_impairment_chain.md](../learning/C_financial_translation/09_nav_impairment_chain.md) — full SCVR → HCR → EFR → NAV chain
- [scripts/shared/scvr_utils.py](../../scripts/shared/scvr_utils.py) — Shared utility module (`compute_scvr`, `compute_report_card`, anchors, GEV/GPD)
- [docs/discussion/discussion_scvr_method_equivalence.md §13](../discussion/discussion_scvr_method_equivalence.md) — Companion metrics rationale and three design options
- [docs/discussion/discussion_hcr_pathway_a_vs_b.md](../discussion/discussion_hcr_pathway_a_vs_b.md) — HCR Pathway A vs B: when SCVR-based HCR fails
- [docs/plan/plan.md](../plan/plan.md) — original build plan for this notebook
