# Discussion: SCVR Method Equivalence — Why Three Methods Give the Same Answer

*Draft — 2026-03-13*

---

## 1. The Question

Our pipeline computes SCVR three different ways and saves all three in the JSON output:

```json
{
  "scvr_method_comparison": {
    "ssp245": {
      "empirical_trapezoid": -0.033334,
      "normal_parametric":   -0.033334,
      "direct_mean_ratio":   -0.033334
    }
  }
}
```

All three agree to 6 decimal places. This raises a fundamental question:

> **If the "empirical trapezoid" gives the same answer as a simple mean ratio,
> why do we bother with exceedance curves and trapezoid integration at all?
> Can we just compute `(mean_future - mean_baseline) / mean_baseline` and be done?**

This document answers that question by examining the math behind each method,
proving why they converge, identifying when they diverge, and explaining why the
exceedance curve representation is retained despite the numerical equivalence.

**References:** Whitepaper §B1 (Mathematical Definition), §B3 (Empirical vs Parametric)

---

## 2. How the Exceedance Curves Are Built — Before Any Math

Before diving into why the methods agree, it helps to understand **what data goes into
the exceedance curves** — because the most common first reaction is: *"The methods agree
because we're averaging somewhere."* We are not.

### 2a. Data Source

Each model provides one daily value per grid cell per day. For tasmax at Hayhurst Solar:

```
NEX-GDDP-CMIP6 via THREDDS
  → 28 models × 30 years × 365 days ≈ 306,600 daily values (baseline)
  → 28 models × 30 years × 365 days ≈ 306,600 daily values (future per scenario)
```

Each model's daily series is stored separately:

```python
baseline_daily = {
    "ACCESS-CM2":     pd.Series([34.2, 33.8, 35.1, ...]),   # 10,950 daily values
    "ACCESS-ESM1-5":  pd.Series([33.5, 34.1, 34.9, ...]),   # 10,950 daily values
    "CESM2":          pd.Series([35.0, 34.3, 33.5, ...]),   # 10,950 daily values
    ...                                                       # 28 models total
}
```

### 2b. The Pooling Step — Concatenation, NOT Averaging

The critical line of code:

```python
base_pool = np.concatenate([s.values for s in baseline_daily.values()])
fut_pool  = np.concatenate([s.values for s in fut_dict.values()])
```

**This is `np.concatenate()`, not `np.mean()`.** Every daily value from every model
is placed into one flat array. Nothing is averaged. Nothing is discarded.

```
NEX-GDDP THREDDS
    │
    ▼
┌───────────────────────────────────────────────────────┐
│  baseline_daily = {                                    │
│    "ACCESS-CM2":     [34.2, 33.8, 35.1, ...],         │  ← 10,950 values
│    "ACCESS-ESM1-5":  [33.5, 34.1, 34.9, ...],         │  ← 10,950 values
│    "CESM2":          [35.0, 34.3, 33.5, ...],         │  ← 10,950 values
│    ...               ...28 models total...             │
│  }                                                     │
└───────────────────────────────────────────────────────┘
    │
    ▼  np.concatenate() — NOT np.mean()
    │
┌───────────────────────────────────────────────────────┐
│  base_pool = [34.2, 33.8, 35.1, ..., 33.5, 34.1,     │
│               34.9, ..., 35.0, 34.3, 33.5, ...]       │
│                                                        │
│  One flat array: ~306,600 values                       │
│  Every daily value from every model preserved          │
│  Model identity lost — but nothing averaged away       │
└───────────────────────────────────────────────────────┘
    │
    ▼  np.sort(...)[::-1]  (descending)
    │
┌───────────────────────────────────────────────────────┐
│  sorted = [45.4, 45.3, 45.2, ..., 10.1, 9.9]         │
│  probs  = [0.000, 0.000003, 0.000007, ..., 1.000]     │
│                                                        │
│  This IS the exceedance curve.                         │
│  Trapezoid integral of this curve = area = mean.       │
└───────────────────────────────────────────────────────┘
```

### 2c. What This Means

The exceedance curve represents the full empirical distribution of **ALL daily values
across ALL models and ALL years**. It contains the tails, the extremes, the outliers —
every data point is there. The only thing lost is model identity (which model produced
each value) and temporal structure (which day it came from).

**Pool sizes by variable at Hayhurst Solar:**

| Variable | Models | Pool size (baseline) | Pool size (future per scenario) |
|----------|-------:|---------------------:|--------------------------------:|
| tasmax   |     28 |            ~306,600  |                      ~306,600   |
| tasmin   |     28 |            ~306,600  |                      ~306,600   |
| tas      |     24 |            ~262,800  |                      ~262,800   |
| pr       |     31 |            ~339,450  |                      ~339,450   |
| sfcWind  |     31 |            ~339,450  |                      ~339,450   |
| hurs     |     29 |            ~317,550  |                      ~317,550   |
| rsds     |     31 |            ~339,450  |                      ~339,450   |

### 2d. FAQ — Addressing the Averaging Concern

> **"Is the three-method equivalence because we average across models?"**
>
> No. We concatenate all raw daily values. No averaging happens before SCVR.

> **"Would using model means instead change SCVR?"**
>
> No — and here is why. If all models contribute equal sample sizes (they do: each
> contributes ~10,950 daily values), then the mean of the pooled array equals the
> mean of the model means:
>
> ```
> mean(concatenate([A, B, C])) = mean([mean(A), mean(B), mean(C)])
>                                   when |A| = |B| = |C|
> ```
>
> So even if we had averaged first, SCVR would be the same number. The equivalence
> is not caused by our pooling strategy — it is a mathematical identity about the
> relationship between area under a sorted curve and the mean (see §3).

> **"Then why does area under the curve = mean?"**
>
> It is a theorem about ANY dataset, regardless of how it was assembled. If you sort
> any list of numbers from largest to smallest, assign equally-spaced probabilities,
> and integrate — the area equals the arithmetic mean. This is true for 5 numbers, for
> 300,000 numbers, for data from one model or thirty models. The proof is in §3 below.

---

## 3. The Math Behind Each Method

### 3a. Method 1 — Empirical Trapezoid (what `compute_scvr()` does)

**Code:** `scripts/shared/scvr_utils.py` lines 157-191

```python
b = np.sort(values)[::-1]           # Step 1: sort DESCENDING
p = np.linspace(0, 1, len(b))       # Step 2: assign probabilities
area = np.trapezoid(b, p)           # Step 3: integrate
```

**What this does mathematically:**

Step 1 creates the empirical quantile function. When values are sorted descending
and probabilities run from 0 to 1:

```
Q(p) = "the value at exceedance probability p"

  p = 0     → highest value (rarest event)
  p = 0.5   → median value
  p = 1     → lowest value (most common to exceed)
```

Step 2 assigns equally-spaced probabilities via `linspace(0, 1, n)`:

```
p_i = (i - 1) / (n - 1)    for i = 1, 2, ..., n
```

Step 3 integrates Q(p) over [0, 1] using the trapezoid rule:

```
Area = ∫₀¹ Q(p) dp  ≈  Σ_{i=1}^{n-1}  (p_{i+1} - p_i) × (v_i + v_{i+1}) / 2
```

Since the p_i are equally spaced with gap Δp = 1/(n-1):

```
Area ≈ Δp × [ v₁/2 + v₂ + v₃ + ... + v_{n-1} + vₙ/2 ]
     = (1/(n-1)) × [ Σ_{i=1}^{n} v_i  -  (v₁ + vₙ)/2 ]
```

**The key identity — why this equals the mean:**

```
Area = ∫₀¹ Q(p) dp = E[X]
```

This is a fundamental theorem of probability: the integral of the quantile function
(inverse CDF) from 0 to 1 equals the expected value for ANY distribution. It is not
an approximation — it is exact for the continuous case.

For the empirical (discrete) case, the trapezoid rule introduces an error term:

```
Error = O(Δp²) = O(1/(n-1)²)
```

At n = 142,399 (our tasmax pool), this error is:

```
Error ≈ 1 / (142,398)² ≈ 5 × 10⁻¹¹
```

That is 0.000000005% — effectively zero. The trapezoid integral IS the mean at our
sample sizes.

**SCVR from this method:**

```
SCVR_trapezoid = (Area_future - Area_baseline) / Area_baseline
               = (E[X_future] - E[X_baseline]) / E[X_baseline]
               ≈ (μ_future - μ_baseline) / μ_baseline
```

---

### 3b. Method 2 — Normal Parametric (MLE fit)

**Code:** `scripts/presentation/ensemble_exceedance.py` step 3b

```python
b_mu, b_sig = scipy.stats.norm.fit(base_clean)   # MLE fit
f_mu, f_sig = scipy.stats.norm.fit(fut_clean)
norm_scvr = (f_mu - b_mu) / b_mu
```

**What this does mathematically:**

`scipy.stats.norm.fit()` computes the Maximum Likelihood Estimate (MLE) for a
Normal distribution N(μ, σ²). For the Normal family, the MLE of μ is:

```
μ̂_MLE = (1/n) Σ_{i=1}^{n} x_i = x̄  (the sample mean)
```

This is not a coincidence — it is a well-known property of the Normal distribution.
The MLE of the mean IS the sample mean. So:

```
SCVR_normal = (μ̂_future - μ̂_baseline) / μ̂_baseline
            = (x̄_future - x̄_baseline) / x̄_baseline
```

This is **exactly** the direct mean ratio (Method 3). The Normal fit adds nothing
beyond what `np.mean()` already gives — it just does it through a more expensive
code path that also estimates σ (which we discard).

**Why include it?** It tests whether a parametric distributional assumption changes
the answer. For Normal, it doesn't (because MLE μ̂ = sample mean). For other
distributions (e.g., GEV, GPD), MLE of the mean is NOT the sample mean — the fit
reshapes the distribution and can shift the mean. We tested GEV daily fit and found
it gave wildly wrong answers (-0.185 vs +0.069 for tasmax), which is why it was
excluded from the comparison.

---

### 3c. Method 3 — Direct Mean Ratio (arithmetic)

**Code:** `scripts/presentation/ensemble_exceedance.py` step 3b

```python
mean_scvr = (np.nanmean(fut_clean) - np.nanmean(base_clean)) / np.nanmean(base_clean)
```

**What this does mathematically:**

```
SCVR_direct = (x̄_future - x̄_baseline) / x̄_baseline
```

where x̄ = (1/n) Σ x_i is the simple arithmetic mean.

No sorting, no integration, no fitting. The most direct estimator of E[X] is the
sample mean, and the sample mean is what all three methods converge to.

---

## 4. Why They Must Agree — The Convergence Theorem

All three methods estimate the **same mathematical quantity**:

```
SCVR = (E[X_future] - E[X_baseline]) / E[X_baseline]
```

Here is why:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    The Fundamental Identity                              │
│                                                                          │
│   For ANY random variable X with finite mean:                            │
│                                                                          │
│              ∫₀¹ Q(p) dp  =  E[X]  =  μ                                │
│                                                                          │
│   Where Q(p) is the quantile function (inverse CDF).                     │
│                                                                          │
│   Proof: Let F(x) = P(X ≤ x) be the CDF, Q = F⁻¹.                     │
│   By integration by parts:                                               │
│       ∫₀¹ Q(p) dp = ∫₋∞^∞ x dF(x) = E[X]                             │
│                                                                          │
│   This holds for Normal, GEV, Gamma, Uniform — ANY distribution.        │
└──────────────────────────────────────────────────────────────────────────┘
```

The three methods are therefore:

```
Method 1:  SCVR = ( ∫₀¹ Q_f(p) dp  -  ∫₀¹ Q_b(p) dp ) / ∫₀¹ Q_b(p) dp
                               ↕                  ↕                  ↕
Method 3:  SCVR = (       μ_f        -        μ_b       ) /      μ_b

Method 2:  SCVR = (      μ̂_MLE_f    -       μ̂_MLE_b   ) /     μ̂_MLE_b
                   (= sample mean     = sample mean       = sample mean)
```

All three compute (μ_future - μ_baseline) / μ_baseline. They MUST agree at large n.

---

## 5. Visual Proof — How Trapezoid Area = Mean

### 5a. Small Example (n = 5)

Consider 5 daily temperature values: {38, 35, 30, 25, 20}°C

```
  Q(p)                   Sorted descending: [38, 35, 30, 25, 20]
  (°C)                   Probabilities:     [0,  0.25, 0.5, 0.75, 1.0]
  40 ┤■
     │ ╲
  35 ┤   ■─────┐
     │         │
  30 ┤         ■─────┐      Area under curve (trapezoid):
     │               │
  25 ┤               ■──┐   = 0.25 × (38+35)/2      [panel 1]
     │                  │     + 0.25 × (35+30)/2     [panel 2]
  20 ┤                  ■     + 0.25 × (30+25)/2     [panel 3]
     │                        + 0.25 × (25+20)/2     [panel 4]
     └──┬───┬───┬───┬──┤
        0  0.25 0.5 0.75 1   = 0.25 × (36.5 + 32.5 + 27.5 + 22.5)
                     p        = 0.25 × 119
                              = 29.75

  Arithmetic mean:  (38 + 35 + 30 + 25 + 20) / 5 = 148 / 5 = 29.6

  Difference:  29.75 vs 29.6  →  0.5% error at n = 5
               (trapezoid over-estimates by O(1/n²))
```

At n = 5, the trapezoid and mean differ by 0.5%. At n = 142,399 (our actual data),
the error shrinks to 10⁻¹¹. They are numerically identical.

### 5b. Why the Area IS the Mean (Intuition)

```
       Value
  40 ┤ ██
     │ ██ ██
  35 ┤ ██ ██ ██                Each bar has width = 1/n
     │ ██ ██ ██ ██             Each bar has height = v_i
  30 ┤ ██ ██ ██ ██ ██
     │ ██ ██ ██ ██ ██          Total area = Σ (1/n × v_i)
  25 ┤ ██ ██ ██ ██ ██ ██                   = (1/n) × Σ v_i
     │ ██ ██ ██ ██ ██ ██ ██               = sample mean
  20 ┤ ██ ██ ██ ██ ██ ██ ██
     └──┴──┴──┴──┴──┴──┴──┤
      v1 v2 v3 v4 v5 v6 v7

  The area under the quantile function = sum of rectangles = mean.
  The trapezoid rule replaces rectangles with trapezoids (smoother),
  but the total area converges to the same value as n → ∞.
```

### 5c. Baseline vs Future — The SCVR Gap

```
  P(X > x)
  1.0 ┤
      │╲
      │ ╲ ╲                   Baseline (solid)
      │  ╲  ╲                 Future   (dashed)
  0.5 ┤   ╲   ╲
      │    ╲    ╲ ░░░░░░░░    ░ = area gap between curves
      │     ╲ ░░░╲░░░░░░░
      │      ╲░░░░ ╲░░░░░
      │       ░░░░░  ╲░░░
  0.0 ┤────────────────────
      └───────────────────▶
            Climate value (°C)

  Area_baseline = ∫ (baseline curve) = E[X_baseline] = μ_b
  Area_future   = ∫ (future curve)   = E[X_future]   = μ_f
  Shaded gap    = Area_future - Area_baseline = μ_f - μ_b

  SCVR = gap / Area_baseline = (μ_f - μ_b) / μ_b
```

The exceedance curve is just the quantile function plotted sideways (x = value,
y = exceedance probability). Its area equals the mean. The gap between two curves
equals the difference in means. SCVR normalizes by the baseline mean.

---

## 6. Proof Table — All 7 Variables at Hayhurst Solar

Data from `data/processed/presentation/hayhurst_solar/*/scvr_summary_*.json`:

### SSP2-4.5

| Variable | Empirical Trapezoid | Normal Parametric | Direct Mean Ratio | Max Divergence |
|----------|--------------------:|------------------:|------------------:|---------------:|
| tasmax   |           +0.068731 |         +0.068731 |         +0.068731 |       0.000000 |
| tasmin   |           +0.146275 |         +0.146276 |         +0.146276 |       0.000001 |
| tas      |           +0.088369 |         +0.088369 |         +0.088369 |       0.000000 |
| **pr**   |       **+0.000862** |     **+0.000884** |     **+0.000884** |   **0.000022** |
| sfcWind  |           -0.006924 |         -0.006924 |         -0.006924 |       0.000000 |
| hurs     |           -0.033334 |         -0.033334 |         -0.033334 |       0.000000 |
| rsds     |           +0.004031 |         +0.004031 |         +0.004031 |       0.000000 |

### SSP5-8.5

| Variable | Empirical Trapezoid | Normal Parametric | Direct Mean Ratio | Max Divergence |
|----------|--------------------:|------------------:|------------------:|---------------:|
| tasmax   |           +0.080661 |         +0.080661 |         +0.080661 |       0.000000 |
| tasmin   |           +0.172875 |         +0.172879 |         +0.172879 |       0.000004 |
| tas      |           +0.104614 |         +0.104614 |         +0.104614 |       0.000000 |
| **pr**   |       **-0.020700** |     **-0.020690** |     **-0.020690** |   **0.000010** |
| sfcWind  |           -0.007403 |         -0.007403 |         -0.007403 |       0.000000 |
| hurs     |           -0.045242 |         -0.045242 |         -0.045242 |       0.000000 |
| rsds     |           +0.002507 |         +0.002507 |         +0.002507 |       0.000000 |

### Summary

| Category | Variables | Agreement | Explanation |
|----------|-----------|-----------|-------------|
| Perfect (6dp) | tasmax, tas, sfcWind, hurs, rsds | All three identical | Smooth, well-behaved distributions |
| Near-perfect (5dp) | tasmin | Trapezoid differs by 0.000001-0.000004 | Larger variance → slightly larger trapezoid error |
| Slight divergence (4dp) | **pr** | Trapezoid differs by 0.000010-0.000022 | Point mass at zero (see §7) |

**Conclusion:** Across 14 comparisons (7 variables × 2 scenarios), the maximum
divergence is 0.000022 — a 2.5% relative error on pr's tiny SCVR of 0.000862.
For all practical purposes, the three methods give identical answers.

---

## 7. When Methods Diverge — The Precipitation Edge Case

Precipitation is the **only** variable where the three methods don't perfectly agree.
The reason is structural: precipitation has a **mixed distribution** — a point mass
at zero (dry days) plus a continuous positive part (wet days).

```
  Precipitation Distribution (schematic)

  Frequency
  ████
  ████                        ← ~65% of days have pr = 0 or near-zero
  ████
  ████ ██
  ████ ██ ██
  ████ ██ ██ ██ ██
  ████ ██ ██ ██ ██ ██ ██ ██ ██ ██
  ─────┬──┬──┬──┬──┬──┬──┬──┬──┬──▶
       0  2  5  10 15 20 30 40 50  mm/day

  Point mass at 0    Long right tail
  (dry days)         (heavy rain events)
```

**Why the trapezoid diverges slightly:**

When ~65% of values are exactly 0 or near-zero, the sorted array has a long flat
segment at the bottom. The trapezoid rule approximates this flat-then-rising shape
slightly differently than the arithmetic mean handles it:

```
  Sorted values (descending):
  [50, 45, 30, 20, 10, 5, 2, 0, 0, 0, 0, 0, 0, 0, 0]
                                    ─────────────────────
                                    flat segment at zero

  Trapezoid:  treats the flat→rising transition as a straight line
  Mean:       weights all values equally (including all the zeros)
```

The arithmetic mean gives more "weight" to the zeros (they're counted individually),
while the trapezoid rule interpolates between adjacent values and can slightly
under- or over-count the zero cluster depending on the probability spacing.

**Is this a problem?** No. The divergence is 0.000022 on a SCVR of 0.000862 — a
2.5% relative error on an already-negligible signal. Precipitation SCVR at this site
is effectively zero anyway (+0.09% for SSP2-4.5). The divergence has no practical
impact.

---

## 8. So Do We Need the Trapezoid?

This is the central question. The answer has two parts.

### For the financial model: No — SCVR is just the mean ratio

The LTRisk pipeline is:

```
SCVR (one number) → HCR → EFR → CFADS → NAV
```

SCVR is a single number that feeds into HCR. No downstream calculation uses the
exceedance curve shape. The curve is never consumed by any part of the financial
model. This means:

```
SCVR = (mean_future - mean_baseline) / mean_baseline
```

This one-liner gives the same answer as the full exceedance curve integration.
We could replace `compute_scvr()` with:

```python
def compute_scvr_simple(baseline_values, future_values):
    b = np.nanmean(baseline_values)
    f = np.nanmean(future_values)
    return (f - b) / b
```

And get the same SCVR values to 6 decimal places. The pipeline would produce
identical HCR, EFR, CFADS, and NAV numbers.

### For communication and review: Yes — the curve is the evidence

The exceedance curve is a **presentation and diagnostic tool**, not a computation
tool. It exists because:

1. Reviewers (like Prashant) want to *see* the distribution, not just trust a number
2. Investors need visual evidence alongside the financial impact
3. The curve reveals things the number hides (see below)

### The blind spot: SCVR misses tail risk

This is the most important implication of SCVR = mean ratio. Two distributions can
have the same mean but very different tails:

```
  Distribution A:                    Distribution B:
  (low variance — compact)           (high variance — fat tails)

  P(X>x)                             P(X>x)
  1.0 ┤╲                             1.0 ┤╲
      │ ╲                                 │  ╲
      │  ╲                                │    ╲
  0.5 ┤   ╲                          0.5 ┤      ╲
      │    ╲                              │        ╲
      │     ╲                             │          ╲
  0.0 ┤──────╲──                     0.0 ┤────────────╲─────
      30  35  40  45                      20  30  40  50  60

  Mean = 35,  SCVR = same             Mean = 35,  SCVR = same
  No days above 45°C                  Many days above 50°C
  Low equipment stress                High equipment stress
```

Both give identical SCVR. But Distribution B has extreme heat events that drive
disproportionately more equipment damage (Peck's equation is exponential in
temperature). **SCVR underestimates the HCR impact when tails fatten** — this is
the open question from whitepaper §E4 ("tail risk treatment").

The exceedance curve and GPD/GEV tail diagnostics are the tools that catch this.
The SCVR number cannot.

### What feeds the model vs what feeds the humans

| Thing | Feeds the model? | Feeds reviewers? |
|-------|:----------------:|:----------------:|
| SCVR = mean ratio (the number) | Yes → HCR | Yes |
| Exceedance curve (the shape) | No | Yes — shows the evidence |
| GPD/GEV tail fits | No | Yes — "is the tail fattening?" |
| Decade-resolved curves | No | Yes — temporal progression |
| 3-method comparison | No | Yes — proves the method works |
| KS D-statistic | No | Yes — fit quality check |

---

## 9. Connection to the Whitepaper

### Supports §B1 (Mathematical Definition)

The whitepaper states (line 274):

> "The area under the exceedance curve is exactly the expected value of the variable:
> integral from 0 to 1 of Q(p) dp = E[X]."

This document **proves** that statement with:
- The mathematical derivation (§3a)
- A numerical example (§5a)
- Empirical verification across 7 variables (§6)

### Supports §B3 (Empirical vs Parametric)

The whitepaper states (lines 448-450):

> "At n = 65,700, the empirical CDF has converged — the trapezoid integration error
> is < 0.0001%. Fitting a parametric model... adds distributional assumptions without
> improving accuracy at these sample sizes."

This document proves the convergence empirically: the Normal parametric and direct
mean methods give identical answers to the empirical trapezoid at n = 142,399.
Parametric fitting adds computational cost and distributional assumptions without
changing the SCVR value.

### Resolves an implicit gap

The whitepaper says SCVR is "area under the exceedance curve" (§B1) and also says
it "can be interpreted as the fractional change in the mean" (line 274). But it never
explicitly addresses: **if it's just the mean, why use the exceedance curve at all?**

This document closes that gap: the exceedance curve is not needed for computing
SCVR (the number). It is needed for understanding, visualizing, and diagnosing the
distributional shift that SCVR summarizes. The curve is the evidence; SCVR is the
verdict.

---

## 10. Recommendation

**Keep `compute_scvr()` using the trapezoid.** Reasons:

1. **Performance is identical.** `np.trapezoid()` and `np.mean()` are both O(n).
   No computational penalty for the exceedance-curve approach.

2. **Conceptual integrity.** The trapezoid maintains the connection between the
   SCVR number and the exceedance curve visualization. When you look at the
   exceedance plot, you are looking at the same object that produced the SCVR.

3. **Wasserstein framing.** SCVR's theoretical grounding comes from the Wasserstein
   W1 distance framework (whitepaper §B2). The exceedance curve integral is the
   natural way to express Wasserstein distance. Replacing it with `np.mean()` would
   break the theoretical link.

4. **Built-in sanity check.** The 3-method comparison table in every JSON serves as
   an automatic consistency check. If the three methods ever disagree significantly,
   something is wrong with the data.

5. **Future extensibility.** If we ever need tail-weighted SCVR (e.g., weighting the
   upper tail more heavily for extreme-event risk), the exceedance curve framework
   supports it naturally. A mean-based approach would need to be redesigned.

### What NOT to do

- Do NOT replace `compute_scvr()` with a simple mean ratio. The numerical equivalence
  is a feature (proves the method works), not a reason to simplify.
- Do NOT remove the 3-method comparison from the JSON. It's a lightweight validation
  that costs nothing to keep.
- Do NOT add more parametric methods (GEV daily fit was already tested and rejected —
  it gives wrong answers at -0.185 instead of +0.069).

---

## 11. Empirical Decomposition: What Pooled SCVR Hides

*Added 2026-03-19 — responds to senior team concern that pooled SCVR may smooth out
real signals. Five diagnostics were run on all 7 variables at Hayhurst Solar: per-model
SCVR spread, tail vs mean comparison, GEV ξ per model, variance decomposition, and
leave-one-out sensitivity.*

**Diagnostic outputs:** `data/processed/presentation/hayhurst_solar/*/scvr_decomposition_*.json`
and corresponding `_decomposition_*.png` figures.

### 11a. Cross-Variable Comparison Table

SSP2-4.5 / SSP5-8.5 values:

| Variable | Pooled SCVR | Model IQR | Tail P95 SCVR | CVaR 95% | Between-Model % | LOO Range |
|----------|:-----------:|:---------:|:-------------:|:--------:|:---------------:|:---------:|
| tasmax   | +6.9 / +8.0% | 2.6 / 2.4% | +4.9 / +5.8% | +4.8 / +5.6% | 0.24 / 0.34% | 0.0017 / 0.0025 |
| tasmin   | +14.4 / +17.4% | 5.5 / 5.0% | +8.0 / +9.8% | +7.6 / +9.4% | 0.22 / 0.39% | 0.0054 / 0.0083 |
| tas      | +8.8 / +10.4% | 3.6 / 3.4% | +6.0 / +7.2% | +5.8 / +7.0% | 0.22 / 0.37% | 0.0027 / 0.0048 |
| **pr**   | **−0.1 / −0.7%** | **7.8 / 13.7%** | **+1.9 / +2.0%** | **+2.4 / +2.9%** | 0.06 / 0.08% | **0.013 / 0.013** |
| sfcWind  | −2.2 / −2.6% | 2.2 / 2.1% | −1.3 / −1.7% | −1.1 / −1.5% | 1.15 / 1.30% | 0.0056 / 0.0052 |
| hurs     | −3.1 / −3.6% | 4.2 / 4.0% | −1.8 / −2.0% | −1.1 / −1.1% | 0.60 / 0.73% | 0.0054 / 0.0064 |
| **rsds** | **+0.5 / +0.3%** | 0.6 / 0.7% | **−0.0 / −0.1%** | **−0.0 / −0.2%** | 0.04 / 0.04% | 0.0008 / 0.0007 |

### 11b. Per-Model SCVR Spread — Is Pooling Hiding Disagreement?

**Temperature (tasmax, tasmin, tas):** Narrow IQR relative to signal. 28 models cluster
tightly around the pooled SCVR. The pooled value sits near the median. No individual
model is a clear outlier. **Verdict: models agree. Pooling is safe.**

**Precipitation (pr):** IQR is 7.8% (SSP2-4.5) and 13.7% (SSP5-8.5) — the widest of
any variable by 6×. Some models project +10% more rain, others −10%. The pooled SCVR
near zero is an average of strongly opposing signals. **Verdict: pooling actively hides
disagreement. Per-model reporting is essential for pr.**

**Surface wind (sfcWind):** Moderate IQR (2.2%). Most models agree on small negative
change. CNRM-CM6-1 is the most influential in leave-one-out analysis but not extreme.

**Humidity (hurs):** IQR of 4.2% is wider than the signal (−3.1%). KACE-1-0-G is a
strong outlier at +6.5% when 27/29 models show negative SCVR. Dropping KACE shifts
pooled SCVR from −3.1% to −3.5%.

**Solar radiation (rsds):** Tightest spread of any variable (IQR = 0.6%). 31 models
strongly agree on "barely any change." LOO range = 0.0008 — removing any single model
changes SCVR by less than 0.1%.

### 11c. Tail Divergence — Does Mean SCVR Miss Extreme Events?

For each variable, compare the mean SCVR against tail-specific SCVR metrics (P95 ratio,
P99 ratio, CVaR 95%). If these differ significantly, SCVR underreports tail risk.

**Temperature:** Tails shift LESS than the mean. P95 SCVR ≈ 70% of mean SCVR. This is
physically expected — mean temperature warms more than the extremes at this site. For
asset risk, this means SCVR slightly overstates the tail risk from temperature — a
conservative bias that is acceptable.

**Precipitation:** **Mean SCVR ≈ 0, but tail metrics are +2–3%.** This is the critical
finding: the mean-based SCVR says "no change in precipitation," but the P95, P99, and
CVaR all show the upper tail fattening. Heavy rainfall events increase even though
average precipitation barely changes. **SCVR fundamentally misses this signal for pr.**

**Humidity (hurs):** Mean SCVR = −3.1%, P99 SCVR = −0.7%. Extreme humidity events
persist even as average humidity drops. This matters for corrosion and mould risk — the
mean says "drier," but extremes barely change.

**Solar radiation (rsds):** **Tails move opposite to the mean.** Mean SCVR = +0.5%
(slight increase in average solar), but P95/CVaR = −0.0% to −0.2% (slight decrease in
extreme solar events). The effect is tiny either way. All models agree.

### 11d. GEV ξ — Is There Systematic Tail Fattening?

GEV shape parameter ξ was fitted to each model's 30 annual maxima, baseline vs future.
ξ > 0 = heavy tail; increasing ξ = tail fattening.

**Temperature:** No systematic ξ drift. Points scatter around the diagonal. Individual
models show both ξ increases and decreases. No evidence of ensemble-wide tail fattening.

**Precipitation:** High noise — fitting GEV to 30 block maxima from precipitation is
inherently noisy. No clear pattern.

**Humidity, wind, solar:** Similarly noisy with 30 data points. GEV fitting at this
block size is diagnostic only, not definitive.

### 11e. Variance Decomposition — Within-Model vs Between-Model

Between-model variance as a percentage of total variance:

| Variable | Between-Model % (SSP2-4.5 / SSP5-8.5) |
|----------|:--------------------------------------:|
| sfcWind  | 1.15 / 1.30%  ← highest               |
| hurs     | 0.60 / 0.73%                           |
| tasmax   | 0.24 / 0.34%                           |
| tas      | 0.22 / 0.37%                           |
| tasmin   | 0.22 / 0.39%                           |
| pr       | 0.06 / 0.08%                           |
| rsds     | 0.04 / 0.04%  ← lowest                |

All variables show between-model variance < 1.5% of total. This means within-model
(temporal) variability dominates — which is expected for daily data. The absolute
between-model contribution matters more than the percentage:

- **sfcWind** has the highest between-model share, consistent with known diversity in
  how GCMs parameterize surface drag and boundary-layer winds.
- **pr** has low between-model *percentage* but high between-model *absolute* spread
  (IQR = 7.8%/13.7%). The percentage is misleadingly low because within-model daily
  variance for pr is enormous (wet days vs dry days).

### 11f. Leave-One-Out Sensitivity

LOO range shows how much the pooled SCVR changes when any single model is dropped:

| Variable | LOO Range (SSP2-4.5 / SSP5-8.5) | Most Influential Model |
|----------|:--------------------------------:|:----------------------:|
| pr       | 0.013 / 0.013                    | BCC-CSM2-MR / KACE-1-0-G |
| tasmin   | 0.005 / 0.008                    | CMCC-ESM2              |
| sfcWind  | 0.006 / 0.005                    | CNRM-CM6-1             |
| hurs     | 0.005 / 0.006                    | KACE-1-0-G             |
| tas      | 0.003 / 0.005                    | IITM-ESM / CanESM5    |
| tasmax   | 0.002 / 0.002                    | FGOALS-g3 / CanESM5   |
| rsds     | 0.001 / 0.001                    | EC-Earth3-VLR / CMCC-ESM2 |

**pr** is most sensitive — dropping BCC-CSM2-MR or KACE-1-0-G shifts the SCVR by
~0.013 (the same order of magnitude as the SCVR itself). This confirms that pr's
near-zero pooled SCVR is fragile and depends on which models are included.

### 11g. Verdict — Answering the Senior Team's Question

> "Is SCVR = mean ratio a feature (real low variability) or a bug (pipeline smoothing
> out real signal)?"

**The answer is variable-dependent:**

| Variable | SCVR Adequate? | Why |
|----------|:--------------:|-----|
| tasmax   | **Yes** | Strong signal, models agree, tails move with mean |
| tasmin   | **Yes** | Same as tasmax but stronger signal |
| tas      | **Yes** | Same as tasmax |
| **pr**   | **No** | Mean ≈ 0 hides +2–3% tail fattening; huge model disagreement |
| sfcWind  | **Mostly** | Small signal, slight pooling effect from CNRM outlier |
| hurs     | **Mostly** | KACE outlier; tails thin less than mean — worth flagging |
| rsds     | **Yes** | Tiny signal, tightest model agreement, no tail concern |

**Recommendation for the team:**

1. For temperature variables: SCVR is sufficient. The exceedance curve + GEV diagnostics
   give reviewers visual confidence, but the mean-based number captures the signal.

2. For precipitation: **SCVR alone is insufficient.** The pipeline should report tail
   metrics (P95 ratio, CVaR 95%) alongside SCVR for precipitation. This is the variable
   where the senior team's concern is validated — the mean genuinely misses the signal.

3. For humidity and wind: SCVR is adequate for the financial model, but the decomposition
   figures should accompany any presentation to flag the KACE-1-0-G outlier (hurs) and
   the CNRM-CM6-1 sensitivity (sfcWind).

4. For solar radiation: SCVR is adequate. Negligible change with extremely high model
   consensus.

---

## 12. Summary

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   Three methods, one answer: (μ_future − μ_baseline) / μ_baseline       │
│                                                                          │
│   ┌──────────────────────┐                                               │
│   │  Empirical Trapezoid │── ∫₀¹ Q(p) dp = E[X] ──┐                    │
│   └──────────────────────┘                          │                    │
│   ┌──────────────────────┐                          ├── All = μ          │
│   │  Normal Parametric   │── MLE μ̂ = x̄ ───────────┤                    │
│   └──────────────────────┘                          │                    │
│   ┌──────────────────────┐                          │                    │
│   │  Direct Mean Ratio   │── (1/n) Σ xᵢ ──────────┘                    │
│   └──────────────────────┘                                               │
│                                                                          │
│   The number is the same.                                                │
│   The exceedance CURVE carries the extra information.                    │
│   Keep the trapezoid — it connects the number to the curve.             │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

*End of discussion. Code changes: `compute_cvar()` and `fit_gev_single_model()` added
to `scvr_utils.py`; `plot_scvr_decomposition()` added to `ensemble_exceedance.py`.*
