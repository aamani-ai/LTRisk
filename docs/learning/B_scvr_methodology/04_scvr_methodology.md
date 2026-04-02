# SCVR Report Methodology — Definitive Reference

**SCVR (Severe Climate Variability Rating) measures the fractional change in
the mean of a climate variable's distribution between a historical baseline
and a future period.**

It answers: *"By what fraction did the distribution mean shift between the
baseline climate and the asset's future?"*

It takes ~300,000 daily values from each period and compresses them into a
**single number** — then wraps that number in a **Report Card** of companion
metrics that reveal whether the single number tells the full story.

---

## 1. What SCVR Actually Measures

### The Formula

```
SCVR = (mean_future - mean_baseline) / mean_baseline
```

SCVR is computed via the area under an empirical exceedance curve, which
at large sample sizes (n > 10,000) converges exactly to the sample mean
E[X]. This equivalence is proven in Section 3.

### What It Captures

- **Location shift** — the center of the distribution moved
- **Direction** — sign-preserving: positive = warmer/wetter, negative = cooler/drier
- **Comparable across variables** — dimensionless ratio, works for temperature,
  precipitation, wind, humidity alike
- **Empirical** — no distributional assumptions, no parametric fitting

### What It Does NOT Capture

- **Variance changes** — distribution widens while mean stays constant → SCVR = 0
- **Tail fattening** — extreme events intensify but mean barely moves → SCVR ≈ 0
- **Shape changes** — skewness, kurtosis shifts invisible in a single mean ratio
- **Compensating shifts** — summer warming + winter cooling may offset in the mean

### Why This Is OK (And When It Isn't)

For **temperature** at mid-century timescales (2026–2055), empirical evidence
shows that variance changes are small (+2%) relative to the mean shift (+2.8°C).
The mean IS the dominant signal. SCVR captures what matters.

For **precipitation**, the mean can be near-zero while extreme rainfall events
increase significantly. Mean SCVR says "no change" but the tail says "more
floods." **This is why the SCVR Report Card exists** — companion metrics
catch what the mean misses.

```
THE SCVR PARADOX — WHY ONE NUMBER ISN'T ENOUGH

  Temperature (tasmax):                Precipitation (pr):
  ┌─────────────────────┐              ┌─────────────────────┐
  │ Mean SCVR: +6.9%    │              │ Mean SCVR: -0.1%    │
  │ P95 SCVR:  +4.9%    │              │ P95 SCVR:  +1.9%    │
  │ Direction: SAME  ✓  │              │ Direction: OPPOSITE ✗│
  │ Confidence: HIGH     │              │ Confidence: DIVERGENT│
  │                      │              │                      │
  │ Mean tells the story │              │ Mean HIDES the story │
  └─────────────────────┘              └─────────────────────┘

  The Report Card catches this.
```

---

## 2. Step-by-Step Computation

### Step 1: Collect Daily Values

```
BASELINE (1985-2014): 30 years x ~365 days = ~10,950 values per model
                      x 28 models (pooled) = ~306,600 values

FUTURE (2026-2055):   30 years x ~365 days = ~10,950 values per model
                      x 28 models (pooled) = ~306,600 values
```

Models are **pooled by concatenation**, not averaged. Every daily value from
every model is preserved. Model identity is lost, but nothing is averaged away.

### Step 2: Sort Values (Descending)

```python
baseline_sorted = np.sort(baseline_values)[::-1]  # highest first
future_sorted   = np.sort(future_values)[::-1]    # highest first
```

```
Baseline sorted:  [45.2, 44.8, 44.5, 43.1, ..., 2.3, 1.8, 0.5]
Future sorted:    [47.1, 46.5, 46.0, 44.9, ..., 3.1, 2.5, 1.2]
                   ^^^^                           ^^^
                   Highest extreme                Lowest value
```

### Step 3: Assign Exceedance Probabilities

```python
exc_probs = np.linspace(0, 1, len(sorted_values))
```

This normalizes both arrays to [0, 1] regardless of how many values there are.
Index 0 (hottest day) → probability 0.0. Index n-1 (coolest day) → probability 1.0.

### Step 4: Plot the Exceedance Curve

```
EXCEEDANCE CURVE — sorted daily values vs exceedance probability

Temperature (°C)
    ▲
 46 │                         ╭─── Future curve (shifted right)
 44 │                    ╭────╯
 42 │              ╭─────╯   ╭─── Baseline curve
 40 │        ╭─────╯   ╭─────╯
 38 │  ╭─────╯   ╭─────╯
 36 │──╯   ╭─────╯
    └──────────────────────────────► Exceedance probability
       0%      25%     50%     75%   100%
       (hottest)                     (coolest)
```

### Step 5: Compute Area Under Each Curve

```python
area = np.trapezoid(sorted_values, exceedance_probs)
```

The trapezoidal rule approximates the area under the curve:

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

### Step 6: Compare Baseline vs Future

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

  The future curve is ABOVE the baseline = warmer climate
```

### Step 7: Compute SCVR

```python
SCVR = (area_future - area_baseline) / area_baseline
SCVR = (27.1 - 25.3) / 25.3
SCVR = 1.8 / 25.3
SCVR = +0.0711  (about +7.1%)
```

### Numerical Example (By Hand)

**Baseline** (5 values, sorted descending): [42, 40, 38, 35, 30]
**Future** (5 values, sorted descending): [45, 43, 41, 38, 33]

```
Baseline area = (42+40)/2 × 0.25 + (40+38)/2 × 0.25
              + (38+35)/2 × 0.25 + (35+30)/2 × 0.25
              = 10.25 + 9.75 + 9.125 + 8.125 = 37.25

Future area   = (45+43)/2 × 0.25 + (43+41)/2 × 0.25
              + (41+38)/2 × 0.25 + (38+33)/2 × 0.25
              = 11.0 + 10.5 + 9.875 + 8.875 = 40.25

SCVR = (40.25 - 37.25) / 37.25 = 3.0 / 37.25 = +0.0806 (+8.1%)
```

### The Code

```python
def compute_scvr(baseline_values: np.ndarray, future_values: np.ndarray) -> dict:
    # Remove NaNs and sort descending
    b = np.sort(baseline_values[~np.isnan(baseline_values)])[::-1].astype(float)
    f = np.sort(future_values[~np.isnan(future_values)])[::-1].astype(float)

    # Create exceedance probability axis
    exc_b = np.linspace(0, 1, len(b))
    exc_f = np.linspace(0, 1, len(f))

    # Compute trapezoid area under each curve
    area_b = float(np.trapezoid(b, exc_b))
    area_f = float(np.trapezoid(f, exc_f))

    # Fractional change
    scvr = (area_f - area_b) / area_b if area_b != 0 else 0.0

    return {
        'scvr': scvr,
        'area_baseline': area_b,
        'area_future': area_f,
        'n_baseline_days': len(b),
        'n_future_days': len(f),
    }
```

**Critical rules:**
- Takes exactly **2 numpy arrays** — no threshold, no direction flag
- Works on **daily values** — never aggregate to annual before calling this
- Handles different array lengths via `linspace` normalization
- Pool sizes are typically ~300,000 values per period (28 models × 30 years × 365 days)

---

## 3. Why Three Methods Give the Same Answer

### The Proof

The exceedance curve area is a trapezoid approximation of:

```
∫₀¹ Q(p) dp     where Q(p) is the quantile function (inverse CDF)
```

By the **quantile representation theorem**, this integral equals **E[X]** (the
distribution mean) for any distribution. So the SCVR area converges to the
sample mean as n grows.

At n = 306,600 (our pool size), the trapezoid error is:

```
Error = O(1/n²) ≈ 1/(306,600)² ≈ 1.1 × 10⁻¹¹    (negligible)
```

This means three apparently different methods give **identical results**:

| Method | What It Computes | Formula |
|--------|-----------------|---------|
| **Empirical trapezoid** | Area under sorted exceedance curve | `np.trapezoid(sorted_desc, linspace(0,1,n))` |
| **Normal parametric** | MLE mean of fitted Normal distribution | `scipy.stats.norm.fit(values)[0]` |
| **Direct mean ratio** | Simple ratio of sample means | `(np.mean(fut) - np.mean(base)) / np.mean(base)` |

### Verification Across All 7 Variables

**SSP2-4.5 (2026-2055 vs 1985-2014 baseline):**

```
Variable   Empirical Trapez.   Normal Parametric   Direct Mean Ratio   Max Divergence
─────────  ─────────────────   ────────────────    ─────────────────   ──────────────
tasmax       +0.068731           +0.068731           +0.068731           0.000000
tasmin       +0.146275           +0.146276           +0.146276           0.000001
tas          +0.088369           +0.088369           +0.088369           0.000000
pr           +0.000862           +0.000884           +0.000884           0.000022
sfcWind      -0.006924           -0.006924           -0.006924           0.000000
hurs         -0.033334           -0.033334           -0.033334           0.000000
rsds         +0.004031           +0.004031           +0.004031           0.000000
```

**SSP5-8.5:**

```
Variable   Empirical Trapez.   Normal Parametric   Direct Mean Ratio
─────────  ─────────────────   ────────────────    ─────────────────
tasmax       +0.080661           +0.080661           +0.080661
tasmin       +0.172875           +0.172879           +0.172879
tas          +0.104614           +0.104614           +0.104614
pr           -0.020700           -0.020690           -0.020690
sfcWind      -0.007403           -0.007403           -0.007403
hurs         -0.045242           -0.045242           -0.045242
rsds         +0.002507           +0.002507           +0.002507
```

Maximum divergence across all 14 comparisons: **0.000022** (precipitation
only, due to its highly non-normal distribution). For all practical purposes,
the three methods are identical.

### Why Use Exceedance Curves Then?

If SCVR equals the mean ratio, why bother with exceedance curves? Three reasons:

1. **Visual proof** — the curve shows the full distribution shifted, not just
   a number. Stakeholders can see the shift with their own eyes.
2. **Foundation for companion metrics** — P95, P99, CVaR are read directly
   from the sorted curve. The curve is infrastructure, not just visualization.
3. **Diagnostic hooks** — GEV/GPD overlays on the curve reveal departures
   from assumptions (tail fattening, shape changes).

The exceedance curve **computes** a mean ratio but **communicates** a
distribution shift. Both are valuable.

---

## 4. The SCVR Report Card

### Why SCVR Alone Isn't Enough

A single mean-shift number has a blind spot: **it can miss tail changes when
the mean is stable.** This matters most for precipitation, where the mean
barely moves but extreme rainfall events can increase significantly.

```
THE PRECIPITATION PROBLEM

  Precipitation daily distribution:

  Baseline:    [0, 0, 0, 0.1, 0.5, 2.0, 8.0, 15.0, 45.0]
  Future:      [0, 0, 0, 0.1, 0.4, 1.8, 9.5, 18.0, 55.0]
                                          ^^^   ^^^^  ^^^^
                                          Tails grew, but mean barely moved

  Mean baseline: 7.84        Mean future: 9.42
  Mean SCVR: +0.20 ... but wait, at Hayhurst it's actually:

  Mean SCVR: -0.1%    ← "no change"
  P95 SCVR:  +1.9%    ← "extreme rainfall increasing"
  CVaR 95%:  +2.4%    ← "worst events getting worse"

  OPPOSITE SIGNS. Mean says decreasing, tail says increasing.
  Which do you trust for flood risk? The tail.
```

### The Six Companion Metrics

The SCVR Report Card augments the mean SCVR with six companion metrics
that reveal whether the tail tells the same story as the mean:

| Metric | Formula | What It Reveals |
|--------|---------|----------------|
| **P95 SCVR** | `(P95_future - P95_baseline) / \|P95_baseline\|` | Did the 95th percentile shift proportionally to the mean? |
| **P99 SCVR** | `(P99_future - P99_baseline) / \|P99_baseline\|` | Did the extreme tail shift? |
| **CVaR 95%** | `(E[X\|X≥P95]_fut - E[X\|X≥P95]_base) / \|E[X\|X≥P95]_base\|` | Expected Shortfall — average of worst 5% of days |
| **Mean-Tail Ratio** | `P95_SCVR / Mean_SCVR` | >0.6 = mean and tail move together; <0.3 = weak linkage |
| **Model IQR** | `P75 - P25 of per-model SCVR values` | Do models agree? Low IQR = consensus |
| **Tail Confidence** | Classification flag (see algorithm below) | Overall reliability verdict: HIGH, MODERATE, LOW, DIVERGENT |

### Tail Confidence Algorithm

```
INPUT: mean_scvr, tail_scvr_p95, mean_tail_ratio, model_iqr

CLASSIFY:
  if sign(mean_scvr) != sign(tail_scvr_p95):
      → DIVERGENT     "Mean and tail point opposite directions"

  elif abs(mean_tail_ratio) < 0.3:
      → LOW            "Weak linkage between mean and tail"

  elif model_iqr > 2 × abs(mean_scvr):
      → LOW            "Models disagree strongly"

  elif mean_tail_ratio > 0.6:
      → HIGH           "Mean and tail move together, models agree"

  else:
      → MODERATE       "Usable with caution"
```

### Worked Example: tasmax (HIGH Confidence)

```
HAYHURST SOLAR — tasmax (SSP2-4.5)
══════════════════════════════════════════════════════════════
  Mean SCVR (headline):     +6.9%     ← pipeline input
  ──────────────────────────────────────────────────────────
  P95 SCVR:                 +4.9%     ← 71% of mean
  P99 SCVR:                 +4.7%     ← 68% of mean
  CVaR 95%:                 +4.8%     ← 69% of mean
  ──────────────────────────────────────────────────────────
  Mean-Tail Ratio:          0.71      ← strong linkage
  Model IQR:                2.5%      ← 28 models agree
  ──────────────────────────────────────────────────────────
  Tail Confidence:          HIGH ■
  ──────────────────────────────────────────────────────────
  Interpretation:  Mean is conservative for tail risk (overstates
                   it by ~30%). SCVR is safe for pipeline use.
```

### Worked Example: pr (DIVERGENT Confidence)

```
HAYHURST SOLAR — pr (SSP2-4.5)
══════════════════════════════════════════════════════════════
  Mean SCVR (headline):     -0.1%     ← "no change"
  ──────────────────────────────────────────────────────────
  P95 SCVR:                 +1.9%     ← OPPOSITE SIGN
  P99 SCVR:                 +2.1%     ← OPPOSITE SIGN
  CVaR 95%:                 +2.4%     ← OPPOSITE SIGN
  ──────────────────────────────────────────────────────────
  Mean-Tail Ratio:          N/A       ← signs differ
  Model IQR:                7.8%      ← models disagree
  ──────────────────────────────────────────────────────────
  Tail Confidence:          DIVERGENT ■
  ──────────────────────────────────────────────────────────
  ⚠ WARNING: Mean and tail diverge. SCVR is misleading for
  precipitation. Use Pathway B (direct hazard counting) for
  flood, extreme precipitation, and dry spell hazards.
```

### Three Variable Classes

The Report Card reveals three behavioral classes:

```
CLASS A — Temperature (tasmax, tas)
  Tail Confidence: HIGH
  Mean overstates tail by ~30% (conservative)
  SCVR alone is sufficient for downstream use
  Annual strategy: anchor_3_linear (R² > 0.97)

CLASS B — Divergent (pr, rsds)
  Tail Confidence: DIVERGENT or LOW
  Mean and tail disagree in direction or magnitude
  SCVR alone is misleading — Pathway B is mandatory
  Annual strategy: period_average (no meaningful trend)

CLASS C — Moderate (tasmin, hurs, sfcWind)
  Tail Confidence: MODERATE
  Mean overstates tail significantly (2-4×)
  SCVR usable with companion metrics alongside
  Annual strategy: varies (tasmin = anchor_3_linear; others = period_average)
```

---

## 5. Decade-Resolved Progression

### Why Decade Resolution Matters

A single 30-year SCVR compresses three decades into one number. But climate
change accelerates — the 2046-2055 decade is warmer than 2026-2035.
Decade resolution reveals the trajectory.

### Hayhurst tasmax Example

```
DECADE SCVR PROGRESSION — tasmax

  SCVR (%)
    12 │                                              ╭── SSP5-8.5
    10 │                                    ╭─────────╯
     8 │                  ╭─────────────────╯╭── SSP2-4.5
     6 │    ╭─────────────╯   ╭─────────────╯
     4 │    │             ╭───╯
     2 │    │             │
     0 └────┴─────────────┴──────────────────────────────
         2026-2035      2036-2045      2046-2055

  Decade        SSP2-4.5    SSP5-8.5    Gap
  ──────────    ────────    ────────    ────
  2026-2035     +0.051      +0.060      0.009
  2036-2045     +0.070      +0.075      0.005
  2046-2055     +0.085      +0.107      0.022
                                         ↑
                               Scenario gap WIDENS
                               in the final decade
```

### Shape Metrics Per Decade (SSP5-8.5)

```
  Period        Mean (°C)   Variance   P99 (°C)   GEV ξ
  ──────────    ─────────   ────────   ────────   ─────
  Baseline      26.52       70.48      40.83      +0.321
  2026-2035     28.12       71.75      42.50      +0.234
  2036-2045     28.80       71.90      43.10      +0.238
  2046-2055     29.35       72.00      43.70      +0.240
```

**Key finding:** The warming is primarily a **mean shift** (+2.8°C), not a
shape change. Variance increases only +2% (70.5 → 72.0). P99 tracks the mean
proportionally (+2.9°C). GEV shape parameter ξ stays positive (heavy-tailed)
but doesn't trend upward — tails are not getting heavier at this site through
mid-century.

**This confirms SCVR as the right metric for temperature variables** — the mean
shift IS the dominant signal. Shape changes may become more pronounced post-2070.

---

## 6. Annual SCVR — Variable-Specific Strategy

### The Problem

Downstream models (HCR, EFR) need **annual** SCVR values — one number per
year from 2026 to 2055. But computing SCVR from a single year's data
(~2,190 values) is noisy because weather variability dominates the climate signal.

### Three Approaches Considered

```
APPROACH A: Per-Year SCVR (noisy)
  Pool: 365 days × 6 models = ~2,190 values per year
  Noise-to-signal ratio: 0.33 (temp) to 9.05 (precip)
  Problem: dominated by weather, not climate

APPROACH B: Rolling Window (autocorrelated)
  Pool: 3,650 days × 6 models = ~21,900 values per window
  Problem: 90% overlap between adjacent years
           → 30 values contain ~3-5 independent samples

APPROACH C: 3 Anchor Points + Linear Fit (recommended)
  Non-overlapping 10-year anchors:
    Anchor 1: 2026-2035 → SCVR_early (midpoint 2030.5)
    Anchor 2: 2036-2045 → SCVR_mid   (midpoint 2040.5)
    Anchor 3: 2046-2055 → SCVR_late  (midpoint 2050.5)
  Fit: f(t) = intercept + slope × t
  Read off annual values via interpolation
```

### Anchor Fit — How It Works

```
ANCHOR FIT DIAGRAM — tasmax SSP5-8.5

  SCVR
  0.12 │
       │                                      *  Anchor 3 (2050.5)
  0.10 │                               ·····
       │                         ·····
  0.08 │                   *····        ← Fitted line (R² = 0.97)
       │             ·····
  0.06 │       *····         Anchor 2 (2040.5)
       │  ····
  0.04 │··     Anchor 1 (2030.5)
       │
  0.02 │
       └──────────────────────────────────────────────
        2026    2030    2035    2040    2045    2050   2055
                                Year

  * = Anchor points (computed from 10-year non-overlapping windows)
  · = Linear interpolation (annual SCVR values read off the line)
```

### Variable-Specific Strategy (From Experiment)

The team ran a concrete experiment computing per-year SCVR for all 7 variables
and fitting linear trends to determine which approach works for each:

```
Variable    Mean SCVR   Noise/Signal   R² (anchor)   Strategy
─────────   ─────────   ────────────   ───────────   ─────────────────
tasmax      +0.083       0.33           0.972         anchor_3_linear ✓
tasmin      +0.164       0.29           0.985         anchor_3_linear ✓
tas         +0.099       0.33           0.982         anchor_3_linear ✓
pr          +0.012       9.05           0.589         period_average  ✗
sfcWind     -0.011       1.29           0.131         period_average  ✗
hurs        -0.043       0.97           0.668         period_average  ✗
rsds        +0.001       8.40           0.308         period_average  ✗
```

**Temperature variables (R² > 0.97):** Clear monotonic trend. 3-anchor linear
fit captures the climate signal with high fidelity. Per-year noise is visible
but the trend is robust.

**Precipitation (R² = 0.59):** Too noisy for linear interpolation. The linear
fit captures only 60% of anchor variation. May be non-linear (wetter early,
drier later). Use period-average SCVR (one value per decade, not per year).

**Wind/radiation (SCVR ≈ 0):** No meaningful climate signal at this site.
Annual computation adds noise, not information. Report period-average SCVR.

---

## 7. Shape Metrics & Extreme Value Fits

### Beyond SCVR: Distribution Shape

The production pipeline computes distribution shape metrics for each variable,
scenario, and decade. These don't feed the financial model directly — they're
**diagnostic tools** that verify SCVR's assumptions and detect shape changes
that SCVR alone would miss.

```
SHAPE METRICS COMPUTED PER PERIOD

  Metric        What It Measures                    Watch For
  ──────────    ───────────────────────────────     ──────────────────
  Variance      Spread of the distribution          Increasing = more variability
  CV            Coefficient of variation (std/|μ|)  Normalized spread
  Skewness      Asymmetry (Fisher)                  Changing = tail behavior shifting
  Kurtosis      Tail heaviness (excess)             Increasing = fatter tails
  P10-P90       Middle 80% range                    Widening = more extremes both sides
  P95, P99      Individual tail quantiles           Moving faster than mean = tail fattening
```

### Extreme Value Theory: GEV and GPD

For formal tail analysis, the pipeline fits two parametric distributions:

**GEV (Generalized Extreme Value)** — fitted to **annual block maxima**

```
  Parameters: shape ξ, location μ, scale σ
  ξ > 0: Frechet (heavy tail, unbounded)    ← temperature, precipitation
  ξ = 0: Gumbel (light tail, exponential)
  ξ < 0: Weibull (bounded upper tail)

  Example (tasmax baseline):
    ξ = +0.279, μ = 41.25°C, σ = 1.541°C
    KS p-value = 0.982 (good fit)
```

**GPD (Generalized Pareto Distribution)** — fitted to **daily values above
P95 threshold** (peaks-over-threshold method)

```
  Parameters: shape ξ, scale σ, threshold u
  Uses: tail behavior of daily values, not just annual maxima
  More data-efficient than GEV (uses ~5% of all days vs 30 annual maxima)
```

**When to use parametric fits:**
- GEV/GPD are for **tail diagnostics** — detecting shape changes, estimating
  return periods, comparing tail heaviness across periods
- They are NOT used for SCVR computation itself (SCVR is empirical)
- The KS goodness-of-fit test (p > 0.05 = adequate fit) flags when the
  parametric model doesn't match the data

---

## 8. Per-Model vs Ensemble SCVR

### Ensemble (Pooled) — The Official Result

All models' daily values concatenated into one pool. One SCVR computed on the
combined data. This is the **headline number** saved to Parquet and used by
downstream models.

**Why pooling works:** Individual model biases (some run hot, some cold) average
out. The pooled SCVR represents the ensemble consensus on climate shift.

### Per-Model — For Uncertainty Quantification

SCVR computed separately for each model. Used to measure **model agreement**
(the IQR metric in the Report Card) and displayed in the dashboard strip plot.

```
PER-MODEL SCVR SPREAD — tasmax SSP2-4.5

  ACCESS-CM2:       *     0.071
  MIROC6:            *    0.082
  MRI-ESM2-0:      *     0.068      ← Models agree (tight spread)
  GFDL-CM4:          *   0.079         IQR = 0.025 → HIGH confidence
  CanESM5:           *   0.085
  MPI-ESM1-2-HR:    *    0.074
  ...               ...  ...
  (28 models total)

  Ensemble pooled:   ◆   0.069      ◆ = diamond marker
                     ↑
              IQR = P75 - P25 of the * values
```

```
PER-MODEL SCVR SPREAD — pr SSP2-4.5

  ACCESS-CM2:    *        0.032
  MIROC6:                    * 0.145
  MRI-ESM2-0:       *    0.078      ← Models DISAGREE (wide spread)
  GFDL-CM4:     *         0.025         IQR = 0.078 → triggers LOW flag
  CanESM5:                      * 0.180
  MPI-ESM1-2-HR:      *  0.065

  Ensemble pooled:     ◆  0.001    The pooled value is near zero,
                                    but individual models range from
                                    -0.05 to +0.18. High uncertainty.
```

When the IQR exceeds 2× the absolute mean SCVR, the Tail Confidence flag
drops to LOW — the models don't agree enough to trust the ensemble mean.

---

## 9. SCVR in Context — Comparison to Other Metrics

### How SCVR Relates to W1 (Wasserstein Distance)

Both use quantile integrals but compute different things:

```
W1   = ∫₀¹ |Q_future(p) - Q_baseline(p)| dp
       ← absolute quantile distances (shape-aware, unsigned)
       ← captures BOTH location shift AND shape change

SCVR = (∫₀¹ Q_future(p) dp  -  ∫₀¹ Q_baseline(p) dp) / ∫₀¹ Q_baseline(p) dp
     = (E[X_future] - E[X_baseline]) / E[X_baseline]
       ← difference of integral means (shape-blind, signed)
```

**SCVR is a weaker metric than W1** — it captures location shift but misses
shape changes. However, for mid-century temperature where variance is stable,
SCVR is appropriate. For precipitation, the Report Card's tail metrics
(Section 4) compensate for SCVR's shape-blindness.

### Cross-Industry Analogy: Insurance AAL

Insurers compute **Average Annual Loss (AAL)** = area under the loss exceedance
probability (EP) curve = E[annual loss]. A climate-adjusted catastrophe model
finds AAL_future > AAL_baseline and charges higher premiums.

```
SCVR is structurally identical to the insurance AAL ratio:

  SCVR    = (AAL_future - AAL_baseline) / AAL_baseline
  Applied to: physical climate variables (°C, mm, m/s)
  Instead of: dollar losses

  Insurers have used mean-based exceedance area integrals for decades.
```

### Comparison Table

```
Method           Field          Captures         Normalized?  Signed?  Shape?
──────────────   ────────────   ──────────────   ──────────   ──────   ──────
SCVR             Climate risk   Mean shift       Yes          Yes      No
Wasserstein W1   Info theory    Location+shape   No           No       Yes
KS statistic     Statistics     Max CDF gap      No           No       No
VaR              Finance        Single quantile  No           Yes      No
CVaR / ES        Finance        Tail mean        No           Yes      Tail
AAL              Insurance      Distribution mean No           Yes      No
Delta method     Hydrology      Mean shift       No           Yes      No
GEV non-stat.    Hydrology      Location+scale   Optional     Yes      Yes
PSI              Credit/ML      Binned divergence No          No       Yes
```

SCVR combines: **normalized** (comparable across variables), **signed**
(direction matters), and **empirical** (no assumptions). It trades shape
sensitivity for simplicity — and the Report Card fills that gap.

---

## 10. Interpreting SCVR Values

### Severity Scale

| SCVR Range | Label | Color | What It Means |
|:---:|:---:|:---:|:---|
| 0.00 – 0.05 | LOW | Green | Within noise. Minimal climate signal. |
| 0.05 – 0.10 | MODERATE | Amber | Detectable shift. Plan accordingly. |
| 0.10 – 0.20 | ELEVATED | Orange | Clear climate signal. Material asset impact. |
| > 0.20 | HIGH | Red | Major shift. Review carefully — may indicate model sensitivity. |

### Variable-Specific Interpretation

```
tasmax (daily max temperature):
  SCVR = +0.08 → "8% higher daily max temperatures on average"
  BAD: panels degrade faster (Peck's), more heat wave shutdowns

tasmin (daily min temperature):
  SCVR = +0.16 → "warmer nights — 16% higher minimum temperatures"
  MIXED: fewer freeze days (good for icing) but less nighttime
         cooling for panels (bad for thermal relief)

tas (daily mean temperature):
  SCVR = +0.10 → "10% warmer overall"
  BAD: primary input to Peck's thermal aging model

pr (precipitation):
  SCVR = -0.01 → "mean precipitation barely changed"
  ⚠ CHECK REPORT CARD: mean may hide extreme rainfall increases
  Tail Confidence likely DIVERGENT at arid sites

sfcWind (wind speed):
  SCVR ≈ 0 → "wind patterns essentially stable"
  NEUTRAL: resource is secure; not a risk driver

hurs (relative humidity):
  SCVR = -0.04 → "site is drying"
  CONTEXT: lower humidity REDUCES Peck's aging acceleration
           (partially offsets temperature increase)

rsds (solar radiation):
  SCVR ≈ 0 → "solar resource essentially stable"
  GOOD NEWS: the fuel supply is secure
```

### Common Misconceptions

| You might think... | But actually... |
|---|---|
| SCVR measures distribution shape | No — it measures the mean shift. Shape changes require companion metrics. |
| Higher SCVR always means more risk | Not always — `hurs` declining reduces Peck's aging acceleration |
| SCVR works on annual means | No — annual aggregation destroys tail information |
| SCVR = 0 means no climate change | No — it means the mean didn't change. Tails may have shifted (see pr). |
| All variables behave the same | No — temperature is Class A (HIGH), precipitation is Class B (DIVERGENT) |
| Per-model SCVR is better than pooled | No — pooled is more robust. Per-model is for uncertainty quantification. |

---

## 11. Downstream — How SCVR Feeds HCR and EFR

### Pipeline Overview

```
SCVR(t) per variable
    │
    ├──► Channel 1: HCR (Hazard Change Ratio)
    │    "How many more hazard events per year?"
    │    SCVR × scaling factor (Pathway A)
    │    or direct daily counting (Pathway B)
    │    → BI_loss ($) → subtracted from CFADS
    │
    └──► Channel 2: EFR (Equipment Failure Ratio)
         "How much faster does equipment degrade?"
         Peck's thermal aging (from SCVR_tas, SCVR_hurs)
         Coffin-Manson cycling (from SCVR_tasmax, SCVR_tasmin)
         Palmgren-Miner fatigue (from SCVR_sfcWind)
         → generation decline → multiplicative on CFADS
```

### Variable → Channel Routing

```
Variable    Primary Channel    Routing Logic
─────────   ───────────────    ──────────────────────────────────────
tasmax      Channel 2 (EFR)    SCVR → Peck's aging (direct)
tasmin      Channel 2 (EFR)    SCVR → Peck's + Coffin-Manson
tas         Channel 2 (EFR)    SCVR → Peck's aging (direct)
pr          Channel 1 (HCR)    Pathway B only (SCVR is DIVERGENT)
sfcWind     Channel 1 (HCR)    SCVR → HCR scaling (minimal signal)
hurs        Both channels       SCVR → Peck's humidity term + HCR
rsds        Channel 3 (tiny)    Document only, don't adjust
```

### Why Pathway B Exists

For precipitation, Pathway A (`HCR = SCVR × scaling_factor`) gives the
**wrong answer** because SCVR ≈ 0 while actual extreme rainfall days increase:

```
Pathway A: HCR_flood = SCVR_pr × 1.75 = -0.001 × 1.75 = -0.002 ← wrong sign
Pathway B: HCR_flood = (count_future - count_baseline) / count_baseline = +0.04 ← correct
```

This is Jensen's inequality in action: the threshold-crossing function is
non-linear, so applying it to the mean gives a different answer than counting
actual crossings. See [Jensen's inequality discussion](../../discussion/hcr_financial/jensen_inequality_hcr_scvr.md).

**Cross-references:**
- HCR methodology: [07_hcr_hazard_change.md](../C_financial_translation/07_hcr_hazard_change.md)
- EFR physics models: [08_efr_equipment_degradation.md](../C_financial_translation/08_efr_equipment_degradation.md)
- NAV impairment chain: [09_nav_impairment_chain.md](../C_financial_translation/09_nav_impairment_chain.md)
- HCR pathways: [hcr_pathway_a_vs_b.md](../../discussion/hcr_financial/hcr_pathway_a_vs_b.md)

---

## 12. Edge Cases and Data Notes

### Why Daily Data — Not Annual Means

```
ANNUAL AGGREGATION DESTROYS TAIL INFORMATION

  Daily data (10,950 values per model):
  ┌──────────────────────────────────────────────────────────┐
  │ 45.2, 44.8, 44.5, ..., 35.1, 34.9, ..., 2.3, 1.8, 0.5 │
  │ ^^^^                                                     │
  │ Extreme days visible — the exceedance curve captures them │
  └──────────────────────────────────────────────────────────┘
        |
        | resample("YE").mean()
        v
  Annual means (30 values):
  ┌────────────────────────────────────────┐
  │ 22.3, 22.1, 22.5, 22.4, ..., 22.8    │  ← everything looks
  │                                        │    nearly identical!
  │ The 45°C extreme days are INVISIBLE    │
  │ averaged with 300+ normal days.        │
  └────────────────────────────────────────┘
```

65,700 daily values per model give a statistically robust exceedance curve.
30 annual means give only 30 points — too few to estimate tails reliably.

### Precipitation: Wet-Day Filtering

At arid sites like Hayhurst, ~78% of days have < 0.1 mm precipitation.
Computing P95 on all days gives a meaningless threshold (~5.9 mm).
Computing P95 on **wet days only** (> 0.1 mm) gives a physically meaningful
threshold (~15 mm).

```
Which uses which:
  Mean SCVR:          All days    (correct reference for distribution mean)
  P95/P99/CVaR SCVR:  Wet days    (meaningful extreme precipitation threshold)
  Shape metrics:       All days    (full distribution characterization)
  GEV/GPD fits:        All days    (extreme value analysis on complete record)
```

The Report Card (Section 4) notes "Data Filter: Wet days only (> 0.1 mm)"
for precipitation companion metrics.

### Unit Conversions

```
Variable    Raw Unit (CMIP6)     Converted Unit    Conversion
─────────   ─────────────────    ──────────────    ──────────────────
tasmax      Kelvin               °C                - 273.15
tasmin      Kelvin               °C                - 273.15
tas         Kelvin               °C                - 273.15
pr          kg/m²/s              mm/day            × 86400
sfcWind     m/s                  m/s               (none)
hurs        %                    %                 (none)
rsds        W/m²                 MJ/m²/day         × 0.0864
```

### Different Sample Sizes

Baseline might have 10,800 values (some NaN days), future might have 10,600
(different calendar). This is fine — `np.linspace(0, 1, len(values))`
normalizes the x-axis. Both exceedance curves span [0, 1] regardless of
sample size.

### What if area_baseline is zero?

Can happen for variables like precipitation in extremely arid regions. We
return SCVR = 0.0 (can't compute fractional change from zero). In practice,
pooled data across models always produces non-zero baselines.

---

## Next

- [05 - Variables and Use Cases](05_variables_and_use_cases.md) — What SCVR means per variable, and real asset walkthroughs
- [11 - Distribution Shift Methods](../D_technical_reference/11_distribution_shift_methods.md) — Deep dive: SCVR vs W1, CVaR, KS, and AAL

## Discussion Docs (Detailed Evidence)

- [Method equivalence proof](../../discussion/scvr_methodology/scvr_method_equivalence.md) — Full derivation, all 7 variables, companion metrics design
- [Annual methodology experiment](../../discussion/scvr_methodology/annual_scvr_methodology.md) — Per-year vs rolling vs anchor fit, R² results
- [Decade shape analysis](../../discussion/scvr_methodology/decade_shape_analysis.md) — Variance, P99, GEV evolution across decades
- [Performance adjustment](../../discussion/scvr_methodology/scvr_performance_adjustment.md) — Why Channel 3 (resource change) is negligible
