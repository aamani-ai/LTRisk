# SCVR Methodology — Definitive Reference

**SCVR (Severe Climate Variability Rating) is a single number that measures how much the shape of a climate variable's distribution shifts between a historical baseline and a future period.**

It answers: *"By what fraction did the climate distribution shift between the historical baseline and the asset's future?"*

It takes ~65,700 daily values from each period and compresses them into a **single number** that captures how much more (or less) extreme the future climate is.

---

## 1. The Simple Version

Think of the daily temperatures at a site over 30 years. If you sort them from hottest to coldest and draw a curve, you get an **exceedance curve** — it shows the probability of exceeding any given temperature.

```
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

The **area under each curve** is a summary of the whole distribution.

SCVR measures how much that area grew:

```
SCVR = (area_future - area_baseline) / area_baseline
```

- **SCVR = 0** → distributions identical, no change
- **SCVR = +0.10** → future area is 10% larger (more or more intense extremes)
- **SCVR = −0.10** → future area is 10% smaller (fewer extremes — e.g., fewer frost days)

---

## 2. Step-by-Step Walkthrough

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
Baseline sorted:  [45.2, 44.8, 44.5, 43.1, ..., 2.3, 1.8, 0.5]
Future sorted:    [47.1, 46.5, 46.0, 44.9, ..., 3.1, 2.5, 1.2]
                   ^^^^                           ^^^
                   Highest extreme                Lowest value
```

Higher values come first (index 0 = hottest day ever recorded).

### Step 3: Assign Exceedance Probabilities

```python
exc_probs = np.linspace(0, 1, len(sorted_values))
# Maps: index 0 → prob 0.0 (hottest), index -1 → prob 1.0 (coolest)
```

This normalizes both arrays to [0, 1] regardless of how many values there are.

```
Probability:  0.000, 0.0001, 0.0002, ..., 0.999, 1.000
Value:        45.2,  44.8,   44.5,   ..., 1.8,   0.5

Meaning: "The probability of exceeding 45.2C is ~0%"
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

## 3. Empirical vs Theoretical Exceedance — Deep Dive

### 3a. What "exceedance curve" actually means

The exceedance curve is conceptually **1 − CDF**: at value *x*, exceedance probability = P(X > *x*) = 1 − F(*x*).

```
P(X > x)
  ▲
1 │●                         ← at x = coldest ever, P(exceed) = ~1.0
  │  ●
  │    ●
  │       ●
0.5│          ●     ← at x = median, P(exceed) = 0.5
  │             ●
  │                ●
  │                   ●
0 │                      ● ← at x = hottest ever, P(exceed) = ~0.0
  └─────────────────────────► x (temperature °C)
    cold ←─────────────→ hot
```

If climate warms, the whole curve shifts right: at any fixed temperature *x*, there is now a *higher* probability of exceeding it. The curve stays between 0 and 1, just at different x-positions.

---

### 3b. Three approaches to building this curve

**Approach 1: Fitted parametric distribution (theoretical)**

Assume the data follows a known distribution (e.g., GEV, Normal, Gumbel). Fit parameters (μ, σ, ξ), then evaluate 1 − F(x) at every x analytically.

```
Pros:
  + Smooth curve at any x
  + Can extrapolate beyond observed data range
  + Closed-form integral → exact area

Cons:
  − Requires picking the right distribution family
  − Wrong family choice = wrong tail behavior
  − GEV tail index (ξ) is hard to estimate robustly from 30-year data
  − Not auditable: "trust the model"
  − Different distribution assumptions → different SCVR numbers
```

**Approach 2: Empirical with plotting positions i/(n+1) (Weibull)**

Sort the n values ascending. Assign each rank i (1 to n) the exceedance probability:
```
p_i = 1 - i/(n+1)
```
This gives slightly interior points — the minimum value gets p = n/(n+1), not 1.0. It's a classic bias correction for extreme value analysis.

```
Pros:
  + No distributional assumptions
  + Bias-corrected for plotting on probability paper

Cons:
  − The p-spacing is non-uniform (numerically identical to linspace for large n)
  − SCVR integral area = Σ values × Δp:
    the extra "gap" near p=0 and p=1 slightly changes the area
  − Still a discretization, still uses trapezoid approximation
```

**Approach 3: Rank-based linspace(0, 1, n) — what SCVR uses**

Sort values descending. Assign each index i the probability:
```
p_i = i / (n-1)   [equivalent to linspace(0,1,n)]
```
Index 0 (highest value) → p=0. Index n-1 (lowest value) → p=1.

```
Pros:
  + No distributional assumptions
  + Simplest possible implementation: one line of numpy
  + Fully auditable — every probability is explicit
  + Handles unequal baseline/future lengths automatically via normalization
  + Area = E[X] exactly as n → ∞ (see box below)

Cons:
  − Assigns p=0 to the maximum, p=1 to minimum (boundary values)
  − Slightly over-weights the extreme tails vs Weibull positions
```

**Why linspace wins for SCVR:** Because SCVR is a *relative ratio* (area_future / area_baseline − 1), the slight boundary bias cancels out. What matters is **consistency** — use the same convention for baseline and future, and the ratio is well-defined and reproducible regardless of which convention you pick.

---

### 3c. What the area integral converges to (and why it matters)

The SCVR area is a trapezoid approximation of:

```
∫₀¹ Q(p) dp   [where Q(p) is the quantile function — the inverse CDF]
```

By the quantile representation theorem, this integral is **exactly equal to E[X]** for any distribution. So the true limiting value of the SCVR area is the mean of the variable.

But the trapezoid rule on finite n points is only an approximation of that integral. The exact trapezoid formula is:

```
area_trapz = (1/(n−1)) × [sum(v) − (v_max + v_min)/2]
E[X]       = sum(v) / n

These are NOT the same for finite n.
```

Example with {42, 40, 38, 35, 30}:
```
area_trapz = 37.25   (from the trapezoid calculation above)
E[X]       = 185/5 = 37.00

Difference: 0.25 — about 0.67% of the area
```

As n grows, the correction term (v_max + v_min)/(2(n−1)) shrinks and area_trapz → E[X]. At n=65,700, the difference is < 0.003°C — completely negligible.

**Why this matters for SCVR:** SCVR is measuring the fractional change in this area — which is approximately the fractional change in E[X], the mean. This makes it interpretable: a SCVR of +0.084 means the mean of the daily distribution is about 8.4% higher in the future. The exceedance curve captures the full distribution, not just the mean, but the summary statistic converges to the mean.

---

### 3d. Numerical comparison: does the choice of approach actually change SCVR?

Using the same 5-value example. **Baseline** = [42, 40, 38, 35, 30], **Future** = [45, 43, 41, 38, 33]:

**linspace(0,1,5):** probs = [0.00, 0.25, 0.50, 0.75, 1.00] — integrates over full [0,1]
```
Baseline area = 37.25,  Future area = 40.25,  SCVR = +0.0806
```

**Weibull i/(n+1):** probs = [1/6, 2/6, 3/6, 4/6, 5/6] ≈ [0.17, 0.33, 0.50, 0.67, 0.83] — integrates over [1/6, 5/6] only
```
Baseline area = 24.83,  Future area = 26.83,  SCVR = +0.0806
```

**True mean E[X]** (exact ratio):
```
Baseline mean = 37.00,  Future mean  = 40.00,  ratio = +0.0811
```

The absolute areas look very different (37.25 vs 24.83) because the integration intervals differ. But **SCVR — the ratio — is essentially the same** across all three conventions.

This is the key result: because SCVR is a relative change (future/baseline − 1), the systematic bias in any convention cancels out in the numerator and denominator. At n=65,700, all three give SCVR to 4+ decimal places of agreement.

**Takeaway:** For large n the convention choice is numerically irrelevant. Linspace is preferred for auditability: every probability value is explicit and reproducible with one numpy call.

---

### 3e. Why we don't use KDE or distributional fitting

**KDE (Kernel Density Estimation):** Fits a smooth density using a kernel bandwidth parameter. Can give a smooth exceedance curve at any x. But:
- Requires choosing bandwidth (there is no single right answer)
- Different bandwidth → different SCVR
- The area under a KDE-based exceedance curve isn't a clean formula
- Adds complexity with no accuracy benefit at n=65,700

**GEV / GPD tail fitting:** Used in flood hydrology and extreme value theory to estimate rare return periods (e.g., 1-in-100-year events). Appropriate for extrapolating beyond the data range.

For SCVR, we don't need to extrapolate beyond observed data — we have 65,700 daily values. The 99.9th percentile is fully covered empirically. GEV fitting would add parametric uncertainty without benefit.

**The rule of thumb:** Use parametric fitting when you need to estimate beyond your data. Use empirical when your data is sufficient. 65,700 points is more than sufficient.

---

## 4. Discrete Data, Continuous Approximation

### 4a. The fundamental nature of the exceedance curve

The exceedance curve is **inherently discrete**: you have n data points, you sort them, you get n (probability, value) pairs. There is no curve between those points — only the straight lines the trapezoidal rule draws.

```
n = 5 example:

Value
 45│    •                  ← (p=0.00, v=45) — highest value
   │     \
 43│      •                ← (p=0.25, v=43)
   │       \
 41│        •              ← (p=0.50, v=41)
   │         \
 38│          •            ← (p=0.75, v=38)
   │           \
 33│            •          ← (p=1.00, v=33) — lowest value
   └──────────────────────► p (exceedance probability)
    0    0.25  0.5  0.75  1
```

The shaded area under these connected dots is what `np.trapezoid()` computes exactly.

---

### 4b. Is the trapezoid approximation accurate enough?

For a smooth underlying function f(p), the trapezoid rule error is:

```
Error ≈ (b−a)³/(12n²) × f''(ξ)   for some ξ in [a,b]
```

With n=65,700 points over [0,1], the term 1/n² ≈ 2.3 × 10⁻¹⁰. Even if f'' is large (a peaked distribution), the trapezoid error is negligible.

In practice, comparing trapezoid area vs true E[X] for our distributions:

```
n = 30   (annual means):  error can be ~1-2% of area
n = 730  (2 years daily): error ~0.01%
n = 65,700 (6 models × 30yr daily): error < 0.0001%
```

This is why the "daily not annual" rule matters twice:
1. More data → better tail estimation
2. More data → trapezoid approximation is exact

---

### 4c. Options we considered and why we rejected them

| Approach | What it is | Why we didn't use it |
|---|---|---|
| Raw daily empirical (linspace) | What we use | ✓ Simple, auditable, sufficient |
| Weibull plotting positions | i/(n+1) instead of i/(n-1) | Negligible difference at n=65,700 |
| KDE smoothed | Kernel density → smooth curve | Adds bandwidth hyperparameter |
| Fitted GEV | Extreme value distribution | Adds parametric uncertainty, needed only for extrapolation |
| Annual means | 30 points/period | Too few — tail structure destroyed |
| Monthly means | 360 points/period | Still too few — seasonal structure lost |
| Pooled models | All models concatenated | ✓ This is what we do — increases n, more robust |
| Per-model separate | SCVR per model, then average | Less robust, doesn't leverage full ensemble |

---

## 5. Numerical Example (By Hand)

Using 5 values each to keep it simple:

**Baseline** (historical tasmax in °C, sorted descending):
```
Values:   [42, 40, 38, 35, 30]
Exc prob: [0.0, 0.25, 0.5, 0.75, 1.0]

Area = trapz([42,40,38,35,30], [0, 0.25, 0.5, 0.75, 1.0])
     = (42+40)/2 × 0.25 + (40+38)/2 × 0.25 + (38+35)/2 × 0.25 + (35+30)/2 × 0.25
     = 10.25 + 9.75 + 9.125 + 8.125
     = 37.25
```

**Future** (same variable, warmer climate):
```
Values:   [45, 43, 41, 38, 33]
Exc prob: [0.0, 0.25, 0.5, 0.75, 1.0]

Area = (45+43)/2×0.25 + (43+41)/2×0.25 + (41+38)/2×0.25 + (38+33)/2×0.25
     = 11.0 + 10.5 + 9.875 + 8.875
     = 40.25
```

**SCVR**:
```
SCVR = (40.25 - 37.25) / 37.25 = 3.0 / 37.25 = +0.0806

→ +8.1% shift in exceedance area
→ "Low" category (below 0.10)
```

---

## 6. The Actual Code

From `notebook_analysis/01_hayhurst_solar_scvr.ipynb` (cell `fe500174`), ported to `03_integrated_scvr_cmip6.ipynb`:

```python
def compute_scvr(baseline_values: np.ndarray, future_values: np.ndarray) -> dict:
    # Step 1: Remove NaNs and sort descending
    b = np.sort(baseline_values[~np.isnan(baseline_values)])[::-1].astype(float)
    f = np.sort(future_values[~np.isnan(future_values)])[::-1].astype(float)

    # Step 2: Create exceedance probability axis
    exc_b = np.linspace(0, 1, len(b))
    exc_f = np.linspace(0, 1, len(f))

    # Step 3: Compute trapezoid area under each curve
    area_b = float(np.trapezoid(b, exc_b))
    area_f = float(np.trapezoid(f, exc_f))

    # Step 4: Fractional change
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
- Takes exactly **2 numpy arrays** — no threshold parameter, no direction flag
- Works on **daily values** — never aggregate to annual before calling this
- Handles different array lengths via `linspace` normalization
- The old `generate_03.py` script incorrectly called it with 4 arguments (threshold, direction) — that was a bug from a different SCVR implementation

---

## 7. Why Daily Data — Not Annual Means

This is the most important design decision in the whole SCVR system.

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

65,700 daily values give a statistically robust exceedance curve.
30 annual means give only 30 points — too few to estimate tails reliably.

---

## 8. Per-Model vs Ensemble SCVR

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

## 9. Interpreting SCVR Values

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

## 10. Edge Cases and Caveats

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

## 11. Common Misconceptions

| You might think... | But actually... |
|---|---|
| SCVR is a probability | No — it's a ratio of areas under sorted value curves, not a probability itself |
| Higher SCVR always means more risk | Not always — `hurs` declining (negative SCVR) reduces Peck's aging rate for solar |
| SCVR works on annual means | No — annual aggregation destroys the tail structure SCVR measures |
| SCVR = 0 means no climate change | No — it means the *distribution shape* didn't change. Mean shift alone may not move the area much if spread doesn't change |
| All variables have same direction | No — tasmax positive is bad for heat stress; tasmin positive reduces frost damage |
| rsds SCVR tells you about solar performance | No — rsds absolute values (not SCVR) drive solar generation; see guide 05 |

---

## Next

- [05 - Variables and Use Cases](05_variables_and_use_cases.md) — What SCVR means per variable, and real asset walkthroughs
- [11 - Distribution Shift Methods](11_distribution_shift_methods.md) — How SCVR relates to Wasserstein W1, CVaR, and AAL
