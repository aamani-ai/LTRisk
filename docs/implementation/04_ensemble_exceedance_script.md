# Script 04 — Ensemble Exceedance Curves + SCVR Presentation Output

*Implementation notes for `scripts/presentation/ensemble_exceedance.py`*

**Sites:** Hayhurst Texas Solar (default) — configurable via `SITE_ID` at top of script
**Variables:** All 7 (tasmax, tasmin, tas, pr, sfcWind, hurs, rsds) — configurable via `VARIABLES`
**Data source:** NASA NEX-GDDP-CMIP6 via NCCS THREDDS NCSS (same cache as Notebook 03)
**Output:** Presentation-grade PNG plots + CSV + JSON per variable

---

## Where This Fits in the LTRisk Pipeline

```
  Notebook 03 (Integrated SCVR)
  ┌──────────────────────────────────────┐
  │ compute_scvr() per variable          │
  │ multi-model ensemble pooling         │
  │ SSP2-4.5 + SSP5-8.5 side-by-side    │
  │ Parquet output                       │
  └─────────────────┬────────────────────┘
                    │ same cache, same functions
                    ▼
    THIS SCRIPT (ensemble_exceedance.py)
    ┌──────────────────────────────────────────────┐
    │ Loops over ALL 7 variables automatically     │
    │ Produces 2 presentation plots per variable   │
    │  - Annual time series (model spread)         │
    │  - Exceedance curves (traditional view)      │
    │ Saves SCVR summary JSON per variable         │
    │ Designed for stakeholder sharing             │
    └──────────────────────────────────────────────┘
                    │
                    ▼
     data/processed/presentation/<site>/<variable>/
       ensemble_timeseries_<var>.png
       exceedance_curves_<var>.png
       ensemble_stats_<var>.csv
       scvr_summary_<var>.json
```

**What this script adds over Notebook 03:**

| Feature | Notebook 03 | This Script |
|---|---|---|
| Runs from CLI | No (Jupyter) | Yes — `python scripts/presentation/ensemble_exceedance.py` |
| Variables per run | 1 at a time | All 7 automatically (loop) |
| Time series plot | Yes | Yes — with corrected aggregation labels |
| Exceedance curve plot | Yes | Yes — traditional view (x=value, y=prob) |
| SCVR summary JSON | No | Yes — one file per variable |
| Ensemble stats CSV | No | Yes — annual P10/P50/P90 per scenario |
| Threading fix | N/A | Yes — lock on probe cache |
| Shareable output | No | Yes — all outputs in one folder tree |

---

## Script Structure — 7 Sections

### Section 1 — CONFIG block (lines 27–35)

```python
SITE_ID        = "hayhurst_solar"
VARIABLES      = ["tasmax", "tasmin", "tas", "pr", "sfcWind", "hurs", "rsds"]
SCENARIOS      = ["ssp245", "ssp585"]
MAX_MODELS     = 6
BASELINE_YEARS = (1985, 2014)
FUTURE_YEARS   = (2026, 2055)
```

These are the only lines that need to change to re-run for a different site or variable subset.
No argparse — intentionally kept simple for ease of editing before a run.

---

### Section 2 — THREDDS Pipeline (lines 91–214)

Ported verbatim from `notebook_analysis/03_integrated_scvr_cmip6.ipynb`.
Five functions:

| Function | What it does |
|---|---|
| `build_thredds_url()` | Constructs NCSS URL for a model/scenario/variable/year. Tries v2 filename first, falls back to v1. |
| `fetch_year()` | Downloads one year of daily data, caches as `.nc`. Parses cftime calendar into pandas DatetimeIndex. |
| `fetch_model_years()` | Runs `fetch_year()` in parallel (ThreadPoolExecutor) across all years for one model. Concatenates result. |
| `unit_convert()` | K → °C for temperature variables; kg/m²/s → mm/day for precipitation. |
| `probe_model_cached()` | HEAD + GET probe to check a model exists for a given scenario/year. Thread-safe with a `Lock`. |

#### Threading race condition fix

The original notebook probe loop had a race condition: multiple threads could write to
`_probe_cache` and call `json.dump()` simultaneously, corrupting the file:

```python
# Fix applied in this script:
_probe_cache_lock = threading.Lock()

def probe_model_cached(...):
    with _probe_cache_lock:
        if key in _probe_cache:
            return _probe_cache[key]         # safe read

    result = probe_model(...)                # network call (outside lock — OK)

    with _probe_cache_lock:
        _probe_cache[key] = result
        with open(PROBE_CACHE_PATH, "w") as f:
            json.dump(_probe_cache, f)       # safe write
```

The network call itself is outside the lock (safe — it's read-only, pure I/O).
Only the dict mutation and file write are locked.

---

### Section 3 — Model Discovery (lines 221–250)

```python
def discover_models():
    # 1. Probe all 34 models at the midpoint year of FUTURE_YEARS
    # 2. Keep only models that pass BOTH SSP245 and SSP585
    # 3. Further filter to models with historical data (probe year 2000)
    # 4. Take the first MAX_MODELS = 6 from the sorted list
```

```
34 models → probe ssp245 (mid-year) → 13–15 pass
          → probe ssp585 (mid-year) → intersection ~13
          → probe historical (2000)  → final: 6
```

Results are cached in `data/cache/thredds/model_probe_cache.json` — on re-runs
for the same variable, no network calls are needed for models already probed.

The specific 6 models vary by variable because not all models publish all 7 variables:
- tasmax/tasmin: typically ACCESS-CM2, ACCESS-ESM1-5, BCC-CSM2-MR, CMCC-ESM2, CanESM5, MIROC6
- tas/hurs: may include IITM-ESM instead of MIROC6
- pr/sfcWind/rsds: may include CMCC-CM2-SR5

---

### Section 4 — SCVR Computation (lines 289–310)

```python
def compute_scvr(baseline_values, future_values):
    b = np.sort(baseline_values)[::-1]       # descending
    exc_b = np.linspace(0, 1, len(b))        # [0, 1] exceedance axis
    area_b = np.trapezoid(b, exc_b)          # ≈ E[X_baseline]

    f = np.sort(future_values)[::-1]
    exc_f = np.linspace(0, 1, len(f))
    area_f = np.trapezoid(f, exc_f)          # ≈ E[X_future]

    scvr = (area_f - area_b) / area_b
```

Exact port from `notebook_analysis/01_hayhurst_solar_scvr.ipynb`. At n≈65,700 daily values
(6 models × 30 years × ~365.25 days), the trapezoid error is < 0.0001% — negligible.

See [docs/learning/04_scvr_methodology.md](../learning/04_scvr_methodology.md) for the
formula derivation, and [docs/learning/08_distribution_shift_methods.md](../learning/08_distribution_shift_methods.md)
for how SCVR relates to Wasserstein W1 and other industry methods.

---

### Section 5 — Plot 1: Annual Time Series (lines 317–405)

#### The aggregation chain — two steps

```
INPUT: daily values (n ≈ 10,950 per model × 6 models over 30 years)

Step 1: daily → annual aggregate per model  (method depends on variable)
  all variables except pr:  series.resample("YE").mean()   → annual mean
  pr only:                  series.resample("YE").sum()    → annual total (mm/year)
  → DataFrame: 30 rows (years) × 6 columns (models)

Step 2: annual aggregates → cross-model P10/P50/P90 per year
  ann.quantile([0.10, 0.50, 0.90], axis=1)
  → 3 series: each year gets a P10, P50, P90 across the 6 models
```

**Why pr uses `.sum()` not `.mean()`:**
Precipitation is reported as annual total (mm/year) in hydrology and climate literature —
"West Texas gets ~400 mm/year". `.mean()` would give an average daily rate (mm/day) which
is not how anyone communicates rainfall. The two are proportional (sum = mean × ~365) so
the trend shape is identical; only the axis scale and units change.

The `TS_RESAMPLE` and `TS_UNIT` globals are set in `run_variable()` before `plot_timeseries()`
is called, so all labels, y-axis units, and caption text update automatically.

**What these percentiles mean:**

| Element | What it is | What it is NOT |
|---|---|---|
| Thin lines (spaghetti) | One model's annual aggregate — the full 30-year trajectory of that model | Individual daily values |
| Thick line (median) | P50 across models for each year — the "middle" model | Ensemble mean over all days |
| Shaded band | P10–P90 across models — how much the 6 models disagree | Daily percentiles (hottest/coldest days of the year) |

The band shows **model uncertainty** (how much models disagree), not **intra-year variability**
(how extreme individual days are). These are completely different concepts. This distinction
is documented in the plot caption (dynamically worded "annual mean" or "annual total"):

```python
fig.text(0.5, -0.03,
    f"Aggregation: daily values → {ts_agg_label} per model (thin lines). "
    "Thick line = median across models. Band = model spread (P10–P90 across models). "
    "These are NOT daily percentiles — they show how much models disagree with each other.",
    ...)
```

#### Layout: two panels

- **Left panel** — Historical (1985–2014): gray spaghetti + band
- **Right panel** — Future (2026–2055): SSP245 blue + SSP585 red spaghetti + bands, with SCVR in legend

Both panels share the y-axis (`sharey=True`) so the magnitude of the shift is visible.

#### Also saves

`ensemble_stats_<var>.csv` — the annual P10/P50/P90 numbers for historical + both scenarios,
for use in downstream financial modeling or external review.

---

### Section 6 — Plot 2: Exceedance Curves (lines 412–489)

Traditional hydrology / CAT modeling convention:
- x-axis = value (°C, mm/day, m/s, %)
- y-axis = P(X > x), from 1 (all days exceed this value) to 0 (no days do)
- Rightward shift of future curves = more extreme values more often

```python
def exceedance_curve_traditional(values):
    v = np.sort(values)           # ascending
    p = 1.0 - np.linspace(0, 1, len(v))   # P(X > x)
    return v, p
    # Plot: plt.plot(v, p)
```

Three curves on one chart: baseline (gray), SSP245 (blue), SSP585 (red).

#### SCVR annotation

The SCVR is computed on the raw pooled daily values (same as Notebook 03's formula),
then annotated as a text box:

```
SCVR (computed via value-integrated area):
  SSP245: +0.0734
  SSP585: +0.0832
  Delta:  +0.0098
```

**Important:** The shaded area visible in the traditional exceedance plot is NOT the SCVR area.
SCVR integrates along the exceedance probability axis (x=prob, y=value), while the traditional
plot shows x=value, y=prob. These are the same curve viewed from different orientations — the
areas are different integrals. SCVR is always computed from the probability-axis orientation.

#### P90 arrow annotations

At exceedance = 0.10 (the 90th percentile level), a double-headed arrow marks the horizontal
gap between the baseline P90 value and the future P90 value. This is a visual marker of where
the future distribution has shifted at the tail — useful for stakeholder communication, though
it is not numerically equal to SCVR.

---

### Section 7 — Multi-Variable Loop (lines 526–615)

The core of what makes this a script rather than a notebook:

```python
def run_variable(variable):
    global VARIABLE, OUT_DIR, UNIT, VAR_FULL   # reassigned per iteration
    VARIABLE = variable
    UNIT     = VARS[variable]["unit"]
    VAR_FULL = VARS[variable]["full_name"]
    OUT_DIR  = ROOT / "data/processed/presentation" / SITE_ID / variable
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # ... full pipeline: discover → load → compute → plot → save

def main():
    for var in VARIABLES:
        run_variable(var)
```

The `global` reassignment pattern was chosen over passing these as function arguments
throughout the entire call chain, since all downstream functions (`discover_models`,
`load_data`, `plot_timeseries`, etc.) reference `VARIABLE`, `OUT_DIR`, `UNIT`, `VAR_FULL`
directly. This is intentional for legibility — the script is designed to be readable and
editable by non-developers.

---

## Output Files per Variable

All outputs saved to `data/processed/presentation/<SITE_ID>/<variable>/`:

| File | Contents | Use |
|---|---|---|
| `ensemble_timeseries_<var>.png` | Annual mean spaghetti + P10–P90 band, baseline + 2 scenarios | Stakeholder deck — model spread and trend |
| `exceedance_curves_<var>.png` | Traditional exceedance curves, 3 periods, SCVR annotated | Stakeholder deck — distributional shift |
| `ensemble_stats_<var>.csv` | Annual P10/P50/P90 per scenario (numerical) | Financial modeling, external review |
| `scvr_summary_<var>.json` | SCVR values for SSP245, SSP585, delta | Downstream pipeline, Notebook 04 |

---

## Actual SCVR Results — Hayhurst Solar (March 2026 run)

Run with 6 models, 1985–2014 baseline, 2026–2055 future:

| Variable | SSP245 | SSP585 | Delta | Signal |
|---|---|---|---|---|
| tasmin | +0.1435 | +0.1634 | +0.020 | Dominant — nights warming fastest |
| tas | +0.0854 | +0.0991 | +0.014 | Strong mean warming |
| tasmax | +0.0734 | +0.0832 | +0.010 | Daytime heat stress |
| pr | +0.0478 | +0.0233 | −0.025 | SSP245 > SSP585 — near-term wetter signal |
| hurs | −0.0327 | −0.0424 | −0.010 | Drying — slight thermal aging relief |
| sfcWind | −0.0149 | −0.0110 | +0.004 | Mild wind decline — negligible for solar |
| rsds | +0.0022 | +0.0005 | −0.002 | Flat — irradiance barely changes |

The `pr` inversion (SSP245 SCVR > SSP585 SCVR) is physically plausible: under SSP245,
the near-term warming drives more convective rainfall events in West Texas (~2026–2055),
while the stronger warming in SSP585 eventually dries the region more in the long run.
The 2026–2055 window captures the wetter-near-term phase for SSP245 but already shows
drying for SSP585's more aggressive trajectory.

---

## How to Re-Run

```bash
# From project root:
python scripts/presentation/ensemble_exceedance.py

# To run a single variable only, edit the CONFIG block:
# VARIABLES = ["tasmax"]

# To run for a different site, edit:
# SITE_ID = "maverick_wind"
```

Cached `.nc` files in `data/cache/thredds/` are reused automatically — no re-download
unless the cache is cleared. Probe results in `model_probe_cache.json` are also reused.

---

## Cross-References

- [03_integrated_scvr_cmip6.md](03_integrated_scvr_cmip6.md) — Notebook 03 implementation doc (same THREDDS pipeline)
- [docs/learning/04_scvr_methodology.md](../learning/04_scvr_methodology.md) — SCVR formula detail
- [docs/learning/08_distribution_shift_methods.md](../learning/08_distribution_shift_methods.md) — how SCVR relates to Wasserstein W1 / AAL / CVaR
- [docs/learning/scvr/01_what_is_scvr.md](../learning/scvr/01_what_is_scvr.md) — exceedance curve conventions, trapezoid error, empirical vs theoretical
