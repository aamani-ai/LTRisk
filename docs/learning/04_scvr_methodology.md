# SCVR Methodology — From Daily Data to a Risk Number

> Step-by-step walkthrough of how SCVR works, with numerical examples, visual explanations of exceedance curves, and interpretation of results.

---

## 1. The Core Question SCVR Answers

> "By what fraction did the climate distribution shift between the historical baseline and the asset's future?"

It takes ~10,000+ daily values from each period, compresses them into a **single number** that captures how much more (or less) extreme the future climate is.

---

## 2. Step-by-Step: How SCVR Is Computed

### Step 1: Collect Daily Values

```
BASELINE (1985-2014): 30 years x ~365 days = ~10,950 values per model
                      x 6 models (pooled) = ~65,700 values

FUTURE (2026-2055):   30 years x ~365 days = ~10,950 values per model
                      x 6 models (pooled) = ~65,700 values
```

Example — daily max temperature (tasmax) for one model at Hayhurst:
```
Baseline sample:  32.1, 35.4, 28.9, 41.2, 33.7, 19.8, 38.5, ...  (10,950 values)
Future sample:    33.8, 36.9, 30.1, 43.0, 34.2, 21.5, 40.1, ...  (10,950 values)
```

### Step 2: Sort Values (Descending)

```python
baseline_sorted = np.sort(baseline_values)[::-1]  # highest first
future_sorted   = np.sort(future_values)[::-1]    # highest first
```

```
Baseline sorted:  45.2, 44.8, 44.5, 44.1, ..., 2.3, 1.8, 0.5
Future sorted:    47.1, 46.5, 46.0, 45.8, ..., 3.1, 2.5, 1.2
                  ^^^^                           ^^^
                  Highest extreme                Lowest value
```

### Step 3: Create Exceedance Probabilities

```python
exceedance_probs = np.linspace(0, 1, len(sorted_values))
```

This creates evenly spaced probabilities from 0 to 1:
```
Probability:  0.000, 0.0001, 0.0002, ..., 0.999, 1.000
Value:        45.2,  44.8,   44.5,   ..., 1.8,   0.5

Meaning: "The probability of exceeding 45.2C is ~0%"
         "The probability of exceeding 44.8C is ~0.01%"
         ...
         "The probability of exceeding 0.5C is ~100%"
```

### Step 4: Plot the Exceedance Curve

```
EXCEEDANCE CURVE

Value
(C)
  45 |*
     | *
  40 | *
     |  *
  35 |   **
     |     ***
  30 |        ****
     |            *****
  25 |                 ********
     |                         **********
  20 |                                    ************
     |                                                ********
  15 |                                                        *****
     |                                                             *****
  10 |                                                                  ****
     |                                                                      ***
   5 |                                                                         **
   0 └──────────────────────────────────────────────────────────────────────────────
     0%    10%    20%    30%    40%    50%    60%    70%    80%    90%   100%
                             Exceedance Probability

     "What fraction of days exceed this temperature?"
```

### Step 5: Compute Area Under the Curve

```python
area = np.trapezoid(sorted_values, exceedance_probs)
```

The **trapezoidal rule** approximates the area under the curve:

```
Value
  40 |████
     |████████
  35 |████████████
     |████████████████
  30 |████████████████████████
     |████████████████████████████████
  25 |████████████████████████████████████████████
     |████████████████████████████████████████████████████████
  20 |████████████████████████████████████████████████████████████████████
     └────────────────────────────────────────────────────────────────────
     0%                         50%                                  100%

     area_baseline = shaded area = e.g., 25.3
```

### Step 6: Compare Baseline vs Future Areas

```
BOTH CURVES OVERLAID

Value
  47 |  F
  45 |B F
     |B  F
  40 |B   FF
     | B    FF
  35 | BB     FFF
     |   BBB     FFFF
  30 |     BBBBB     FFFFF
     |         BBBBBBB   FFFFF
  25 |              BBBBBBBB  FFFFFF
     |                   BBBBBBBBB  FFFFFFFF
  20 |                        BBBBBBBBBB  FFFFFFFFFF
     └────────────────────────────────────────────────────
     0%            25%            50%           75%      100%

  B = Baseline curve       area_baseline = 25.3
  F = Future curve         area_future   = 27.1

  The future curve is ABOVE the baseline = more extreme values
```

### Step 7: Compute SCVR

```python
SCVR = (area_future - area_baseline) / area_baseline
SCVR = (27.1 - 25.3) / 25.3
SCVR = 1.8 / 25.3
SCVR = +0.0711  (about +7.1%)
```

---

## 3. The Actual Code

From Notebook 01, cell `fe500174` — ported exactly to Notebook 03:

```python
def compute_scvr(baseline_values: np.ndarray, future_values: np.ndarray) -> dict:
    # Remove NaN, sort descending
    b = np.sort(baseline_values[~np.isnan(baseline_values)])[::-1].astype(float)
    f = np.sort(future_values[~np.isnan(future_values)])[::-1].astype(float)

    # Create exceedance probabilities (0 to 1)
    exc_b = np.linspace(0, 1, len(b))
    exc_f = np.linspace(0, 1, len(f))

    # Compute areas using trapezoidal integration
    area_b = float(np.trapezoid(b, exc_b))
    area_f = float(np.trapezoid(f, exc_f))

    # SCVR = fractional change
    scvr = (area_f - area_b) / area_b if area_b != 0 else 0.0

    return {
        'scvr': scvr,
        'area_baseline': area_b,
        'area_future': area_f,
        'n_baseline_days': len(b),
        'n_future_days': len(f),
    }
```

**Note**: The function takes exactly 2 arguments (baseline array, future array). The old `generate_03.py` script incorrectly called it with 4 arguments (threshold, direction) — that was a bug from a different SCVR implementation.

---

## 4. Why Daily Data, Not Annual?

This is a critical design decision. Here's why:

```
ANNUAL AGGREGATION DESTROYS TAIL INFORMATION

  Daily data (10,950 values):
  ┌──────────────────────────────────────────────────────────┐
  │ 45.2, 44.8, 44.5, ..., 35.1, 34.9, ..., 2.3, 1.8, 0.5 │
  │ ^^^^                                                     │
  │ Extreme days visible                                     │
  └──────────────────────────────────────────────────────────┘
        |
        | resample("YE").mean()  (what generate_03.py did wrong)
        v
  Annual means (30 values):
  ┌────────────────────────────────────────┐
  │ 22.3, 22.1, 22.5, 22.4, ..., 22.8    │  <-- everything looks
  │                                        │      nearly identical!
  │ The 45C extreme days are INVISIBLE     │
  │ because they're averaged with the      │
  │ 300+ normal days in that year.         │
  └────────────────────────────────────────┘
```

**Numerical example**:

```
Year 2030 daily temps: 15, 18, 22, 35, 42, 45, 38, 20, 12, ...
Annual mean: 22.3C

Year 2040 daily temps: 16, 19, 23, 37, 44, 48, 40, 21, 13, ...
Annual mean: 23.1C  (only +0.8C difference in mean)

But the TAIL shifted dramatically:
  Days above 40C:  2030 = 3 days,  2040 = 5 days  (+67% increase!)
  Maximum temp:    2030 = 45C,     2040 = 48C      (+3C shift!)

Daily SCVR captures this. Annual SCVR misses it entirely.
```

---

## 5. Interpreting SCVR Values

### The Magnitude Guide

| SCVR Value | Label | What It Means |
|:---:|:---:|:---|
| 0.00 to 0.05 | Negligible | Essentially no change. Within noise. |
| 0.05 to 0.10 | Low | Small shift (<10%). Detectable but minor. |
| 0.10 to 0.30 | Moderate | Clear climate signal. Plan for it. |
| 0.30 to 0.60 | High | Major shift. Significant asset impact expected. |
| > 0.60 | Very High | Review carefully. May indicate model sensitivity issues. |

### Direction Matters

Not all positive SCVR is bad, and not all negative is good:

```
VARIABLE-SPECIFIC INTERPRETATION

tasmax (daily max temp):
  SCVR = +0.08 means "8% more extreme heat"
  This is BAD: panels degrade, efficiency drops

tasmin (daily min temp):
  SCVR = +0.05 means "warmer minimum temperatures"
  MIXED: fewer freeze days (good for icing) but
         less nighttime cooling for panels (bad)

  SCVR = -0.03 means "colder minimums" (unlikely under warming)
  Would be BAD: more icing risk

pr (precipitation):
  SCVR = +0.15 means "15% more extreme rainfall"
  BAD: flood risk, erosion, equipment damage
  But also means fewer dry spells? Not necessarily —
  precipitation has "extremes_both_directions"

sfcWind (wind speed):
  SCVR near 0 means "wind patterns barely change"
  For wind turbines, this is NEUTRAL (neither good nor bad)
  But note: mean wind matters for generation, extremes for damage

hurs (humidity):
  SCVR context_dependent — high humidity + heat = accelerated aging
                           high humidity + cold = icing risk
```

### Reading the SCVR Table

```
EXAMPLE OUTPUT FROM NOTEBOOK 03

              SSP2-4.5    SSP5-8.5    Delta    Direction
Variable
tasmax         0.0523      0.0841     0.0318   higher_is_worse
tasmin         0.0412      0.0689     0.0277   lower_is_worse_for_freeze
tas            0.0485      0.0790     0.0305   higher_is_worse
pr             0.0156      0.0312     0.0156   extremes_both_directions
sfcWind       -0.0023     -0.0018     0.0005   higher_extremes_are_worse
hurs           0.0089      0.0145     0.0056   context_dependent
```

**What to look for**:
1. **Which variables have the highest SCVR?** Temperature variables usually dominate.
2. **How big is the SSP delta?** If SSP5-8.5 is much worse than SSP2-4.5, the emission pathway matters a lot.
3. **Is sfcWind near zero?** Wind is hard to project — models often disagree, so the ensemble averages out.
4. **Are any values suspiciously high (>0.60)?** This might indicate a single model dominating the ensemble.

---

## 6. Per-Model vs Ensemble SCVR

We compute SCVR two ways:

### Ensemble (Pooled) SCVR
- Concatenate daily values from ALL models into one bag
- Compute one SCVR on the pooled data
- This is the "official" result saved to Parquet
- More robust because it averages across model biases

### Per-Model SCVR
- Compute SCVR separately for each model
- Used for **uncertainty quantification** (the Strip Plot)
- Shows whether models agree or disagree

```
PER-MODEL SCVR SPREAD (from Strip Plot)

  ACCESS-CM2:       *     0.071
  MIROC6:            *    0.082
  MRI-ESM2-0:      *     0.068      <-- Models agree (tight spread)
  GFDL-CM4:          *   0.079          = HIGH CONFIDENCE
  CanESM5:           *   0.085
  MPI-ESM1-2-HR:    *    0.074

  Ensemble pooled:   D   0.076      D = diamond marker


  If instead:
  ACCESS-CM2:    *        0.032
  MIROC6:                    * 0.145
  MRI-ESM2-0:       *    0.078      <-- Models disagree (wide spread)
  GFDL-CM4:     *         0.025         = LOW CONFIDENCE
  CanESM5:                      * 0.180
  MPI-ESM1-2-HR:      *  0.065

  Ensemble pooled:     D  0.088     The pooled value is "right" but
                                    the uncertainty is high.
```

---

## 7. Edge Cases and Caveats

### What if area_baseline is zero?
- Can happen for variables like precipitation in extremely arid regions
- We return SCVR = 0.0 (can't compute fractional change from zero)
- In practice, our Texas sites always have non-zero baselines

### What about different sample sizes?
- Baseline might have 10,800 values (a few NaN days)
- Future might have 10,600 values (different calendar, some missing)
- This is fine — `np.linspace(0, 1, len(values))` normalizes the x-axis
- The exceedance curves are always [0, 1] regardless of sample size

### What about seasonal patterns?
- Daily data includes all seasons (summer AND winter)
- This means the exceedance curve has a mix of hot and cold days
- The area under the curve captures the FULL annual distribution
- For seasonal analysis, you would filter by month first — not implemented in Notebook 03, could be added in Notebook 04

---

## Next

- [05 - Data Pipeline](05_data_pipeline.md) — How we get the data from NASA THREDDS to our notebook
