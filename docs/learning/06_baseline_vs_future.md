# Baseline vs Future — Time Windows, the Gap, and Ensemble Pooling

> Why we split time the way we do, why the 2015-2025 gap is intentional, how ensemble pooling works, and comparisons with alternative approaches.

---

## 1. Our Two Time Windows

```
TIMELINE

  1985                    2014    2025  2026                    2055
  ├─────── BASELINE ───────┤     GAP   ├─────── FUTURE ─────────┤
  │  30 years              │   11 yrs  │  30 years              │
  │  historical experiment │           │  SSP experiment        │
  │  "What was normal?"    │           │  "What will the asset  │
  │                        │           │   experience?"         │
  └────────────────────────┘           └────────────────────────┘
```

| Window | Period | Years | Source Experiment | Purpose |
|---|---|---|---|---|
| Baseline | 1985-2014 | 30 | `historical` | Define "normal" climate |
| Future | 2026-2055 | 30 | `ssp245` or `ssp585` | Asset's operational exposure |

---

## 2. Why 1985-2014 for Baseline?

Three reasons:

### Reason 1: CMIP6 Historical Experiment Ends at 2014

```
CMIP6 experiment design:

  historical experiment:  1850 ──────────────────── 2014  (ENDS HERE)
  SSP experiments:                                  2015 ──────── 2100

  The historical experiment LITERALLY has no data after 2014.
  It's not a choice — it's a constraint.
```

### Reason 2: IPCC Standard Reference Period

The IPCC Sixth Assessment Report (AR6) uses 1995-2014 or 1985-2014 as the modern reference period. By using this same window, our results are **directly comparable** with published climate science.

### Reason 3: 30 Years = Statistical Robustness

```
WHY 30 YEARS AND NOT 20 OR 10?

  Climate has natural variability:
  - El Nino/La Nina cycles: 2-7 years
  - Pacific Decadal Oscillation: 20-30 years
  - Atlantic Multidecadal Oscillation: 60-80 years
  - Volcanic eruptions: random (Pinatubo 1991, etc.)

  Window too short (10 years):
    Might land on an El Nino cluster -> baseline looks too warm
    Or a volcanic eruption -> baseline looks too cool
    Not enough data for robust tail estimation

  30 years smooths these out:
    Contains ~5 El Nino cycles
    Contains ~1 full PDO cycle
    ~10,950 daily values per model -> robust exceedance curves
```

### Why Not Start Earlier (1950)?

```
1950─────────1985─────────2014
 ^             ^
 |             |
 Climate was   This is the "modern baseline."
 different     Close enough to present to be
 then — less   relevant, but before the
 CO2, less     acceleration of warming that
 warming.      happened after 2014.

 Using 1950-2014 would MIX:
  - A cooler early period (less CO2)
  - A warmer late period (more CO2)
  = An artificially "medium" baseline
    that doesn't represent either period well.
```

---

## 3. Why 2026-2055 for Future?

This is driven by the **asset's actual operational lifetime**:

```
ASSET CONFIGURATION (from sites.json + Notebook 03)

  construction_start_year = 2026
  operational_lifespan    = 30 years
  -> future window: 2026 to 2055

  The solar farm at Hayhurst:
    Built: 2026
    Operates: 2026-2055
    Decommissioned: ~2056

  We only care about climate the asset ACTUALLY FACES.
  Climate in 2060? Irrelevant — the asset is gone.
  Climate in 2020? Irrelevant — the asset doesn't exist yet.
```

### Notebook 01 vs Notebook 03 Approach

```
NOTEBOOK 01 (old approach):
  Fixed target years: 2030, 2035, 2040, 2045, 2050
  Each with a 20-year rolling window:
    2030 -> window 2020-2040
    2035 -> window 2025-2045
    2050 -> window 2040-2060

  Problem: Multiple overlapping SCVRs, confusing to interpret.
           Which one represents "the asset's risk"?

NOTEBOOK 03 (new approach):
  ONE window: 2026-2055 (the entire asset lifetime)
  ONE SCVR per variable per scenario.

  Advantage: Clear, definitive answer.
  For schema compatibility: center_year = (2026+2055)//2 = 2040
```

---

## 4. The Gap (2015-2025): Why It's Correct

### The Gap Is NOT Missing Data

```
    Baseline                    Future
    1985──────2014    2015──2025    2026──────2055
                        ^^^^^^^^
                        This data EXISTS on THREDDS.
                        We CHOOSE not to use it.
                        Here's why:
```

### Reason 1: It Doesn't Belong in the Baseline

```
TEMPERATURE TREND

Temp anomaly
(vs 1850-1900)

  +1.5C |                              * * *
        |                          * *
  +1.0C |                    * * *
        |              * * *
  +0.5C |        * * *                    <- 2015-2025 is HERE
        |  * * *                              already +1.0 to +1.3C
  0.0C  |*                                    above pre-industrial
        └──────────────────────────────
        1900  1950  1985  2014  2025

  Adding 2015-2025 to baseline:
    Old baseline mean: +0.6C (average of 1985-2014)
    New baseline mean: +0.7C (average of 1985-2025)

    = baseline gets warmer
    = future looks LESS different
    = SCVR is ARTIFICIALLY LOWER
    = YOU UNDERESTIMATE THE RISK
```

### Reason 2: It Doesn't Belong in the Future

```
  The asset starts in 2026. Including 2015-2025 in the future:

  - Adds 11 years of cooler-than-2040s data
  - Dilutes the hotter end of the distribution
  - Makes future look milder than what the asset will face
  - Again: UNDERESTIMATES RISK

  Also: those years are NOT part of the asset's operational life.
  No revenue, no depreciation, no risk during 2015-2025.
```

### Reason 3: It's the Transition Zone

```
EXPERIMENT BOUNDARY

  historical experiment  SSP experiment
  ────────────────────>  ──────────────>
                     2014|2015

  At this boundary:
  - CO2 concentrations are identical (both ~400 ppm)
  - But the experiment "source" changes
  - Some models have a tiny discontinuity at the join
  - Including data from both sides of the join in
    ONE bag would mix experiment artifacts with climate signal
```

### The Analogy

Think of it like comparing two blood tests:
- **Test 1**: Your blood panel from 2020 (baseline health)
- **Test 2**: Your blood panel from 2030 (after a decade of changed diet)

You wouldn't mix in blood work from 2023-2029 into either test. Those intermediate results don't represent your original state OR your final state — they're the transition.

---

## 5. What If the Asset Started Before 2015?

Our `construction_start_year = 2026` so this doesn't apply, but the code handles it:

```python
if future_start <= 2014:
    # Stitch historical + SSP
    hist_part = fetch_model_years(model, "historical", var,
        range(future_start, min(2015, future_end+1)), ...)
    ssp_part = fetch_model_years(model, scen, var,
        range(2015, future_end+1), ...)
    fut_series = pd.concat([hist_part, ssp_part]).sort_index()
else:
    # All future years come from SSP
    fut_series = fetch_model_years(model, scen, var,
        range(future_start, future_end+1), ...)
```

Example: If an asset started in 2010 with 40-year lifespan (2010-2049):
```
  2010──2014: from "historical" experiment
  2015──2049: from "ssp245" or "ssp585"
  Stitched together into one continuous series
```

---

## 6. Ensemble Pooling Explained

### What Pooling Means

Instead of keeping models separate, we throw all their daily values into one bag:

```
WITHOUT POOLING (per-model):

  Model A baseline:  [32.1, 35.4, 28.9, ...]   10,950 values
  Model B baseline:  [31.8, 34.9, 29.2, ...]   10,950 values
  Model C baseline:  [33.0, 36.1, 28.5, ...]   10,950 values

  -> 3 separate SCVR values
  -> Which one do you report?

WITH POOLING (ensemble):

  Pooled baseline:   [32.1, 35.4, 28.9, ...,   <- Model A
                      31.8, 34.9, 29.2, ...,   <- Model B
                      33.0, 36.1, 28.5, ...]   <- Model C
                     = 32,850 values in ONE bag

  -> 1 SCVR value that represents the ensemble
```

### Why Pooling Works

```
THE LAW OF LARGE NUMBERS IN ACTION

  Model A alone: might be biased warm (+1C)
  Model B alone: might be biased cool (-0.5C)
  Model C alone: might be unbiased

  Per-model SCVR:
    A: 0.095  (inflated by warm bias)
    B: 0.052  (deflated by cool bias)
    C: 0.073  (probably closest to truth)
    Average: 0.073

  Pooled SCVR:
    0.074  (biases cancel in the combined distribution)

  Pooling naturally averages out individual model biases
  because the exceedance curve is computed on ALL values at once.
```

### Why We Also Compute Per-Model SCVR

```
PURPOSE: UNCERTAINTY QUANTIFICATION

  If all models agree:        If models disagree:

  A: 0.071   ──┐              A: 0.032   ──┐
  B: 0.068     ├── tight       B: 0.145     ├── wide spread
  C: 0.073     │   spread      C: 0.025     │   = LOW confidence
  D: 0.079     │   = HIGH      D: 0.180     │
  E: 0.075     │   confidence  E: 0.065     │
  F: 0.074   ──┘              F: 0.120   ──┘

  Pooled: 0.074               Pooled: 0.088

  The pooled value is "right"  The pooled value is "right"
  AND we're confident.        BUT we're NOT confident.

  -> The Strip Plot (Plot D in NB03) shows this visually.
```

---

## 7. Comparison with Alternative Approaches

### Approach A: Rolling Windows (what Notebook 01 did)

```
  Target year 2030: window 2020-2040, SCVR_2030 = 0.05
  Target year 2035: window 2025-2045, SCVR_2035 = 0.06
  Target year 2040: window 2030-2050, SCVR_2040 = 0.07
  Target year 2050: window 2040-2060, SCVR_2050 = 0.09

  Pro: Shows how risk evolves over time
  Con: Windows overlap heavily (2030-2040 appears in ALL of them)
  Con: Which SCVR represents "the asset's risk"? Ambiguous.
  Con: More complex output, harder to communicate to stakeholders.
```

### Approach B: Full Lifetime Window (what Notebook 03 does)

```
  Window 2026-2055, SCVR = 0.073

  Pro: One definitive number per variable/scenario
  Pro: Directly answers "what will THIS ASSET experience?"
  Pro: Simple to communicate: "7.3% more extreme climate"
  Con: Loses temporal evolution (you don't know if it's front-loaded)
```

### Approach C: Decade Buckets

```
  2026-2035: SCVR_early  = 0.04
  2036-2045: SCVR_mid    = 0.07
  2046-2055: SCVR_late   = 0.10

  Pro: Shows acceleration
  Con: Only 10 years per bucket (fewer data points, noisier)
  Con: Bucket boundaries are arbitrary
```

We chose Approach B because the primary consumer (HCR/EFR computation in Notebook 04) needs a single SCVR per variable per scenario. Temporal evolution can be explored in visualizations (Plot C spaghetti) without changing the core output.

---

## Next

- [07 - From Climate to Finance](07_from_climate_to_finance.md) — How SCVR translates to financial impact
