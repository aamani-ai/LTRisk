# Distribution Shift Quantification — Where SCVR Sits in a Larger Landscape

> SCVR answers one question: "By what fraction did this climate distribution shift?" This is
> not a novel question. Finance, insurance, hydrology, machine learning, and information theory
> all ask it. This doc maps the full landscape — every major method, what it measures, and
> exactly where SCVR fits.

---

## 1. The Core Problem

A distribution changed. By how much? In what direction? Does it matter?

```
BEFORE (baseline):          AFTER (future):

     ****                        ****
   **    **                    **    **
  *        *                  *        *
 *          *                *          *
*            *            *               *
─────────────────────    ───────────────────────
  10   20   30   40        12   22   32   42   52

         Both are valid distributions.
         The second shifted right.
         How do you put a number on that?
```

The same question appears in every quantitative field, just with different labels:

| Field | "Distribution" | "Shift" |
|---|---|---|
| Climate risk | Daily temperature, precipitation | Historical → future under warming |
| Finance | Daily P&L, asset returns | Normal market → stressed market |
| Insurance | Annual losses | Historical losses → climate-adjusted losses |
| Hydrology | Annual flood peaks | Stationary → non-stationary under warming |
| Credit scoring | Borrower feature distributions | Training data → deployment data |
| ML / AI | Model input features | Training distribution → production distribution |
| Engineering | Load cycles, thermal stress | Design conditions → future operating conditions |

The methods differ in three ways:
1. **What they integrate** — a point (single quantile), the tail, or the full distribution
2. **Whether they normalize** — absolute distance or fractional change
3. **Parametric vs empirical** — fit a model to the data or use the data directly

---

## 2. Information Theory — The Most General Foundation

Information theory defines distance between distributions at the most abstract level, with no
assumption about what the distributions represent.

### The four main divergences

| Method | Core operation | Symmetric? | Handles non-overlapping support? |
|---|---|---|---|
| KL Divergence | Σ P(x) log(P(x)/Q(x)) | No | No — undefined if Q(x)=0 where P(x)>0 |
| Jensen-Shannon (JSD) | Average of two KL divergences | Yes | Yes |
| Total Variation | max\|P(A) − Q(A)\| over all events A | Yes | Yes |
| Wasserstein W1 | ∫\|F_P(x) − F_Q(x)\| dx | Yes | Yes |

### Wasserstein W1 — the closest relative to SCVR

Wasserstein W1 is also called the "Earth Mover's Distance": how much earth (probability mass)
do you need to move, and how far, to transform distribution P into distribution Q?

```
F_baseline(x):                      F_future(x):
        ┌──────────────────         ┌──────────────────
1.0─────┘                   1.0─────┘
                                         (shifted right)

        Area between the two CDFs = W1 distance

        ┌──────────────────
1.0──┐  │  ← F_baseline   ← F_future
     │  │  ██████████████
     │  │  ██████████████   ← shaded area = W1
     │  │  ██████████████
0.0──┘──┘──────────────────────────
     x_min                x_max
```

**SCVR is a normalized, signed Wasserstein W1 distance:**

```
W1 (unsigned) = ∫|F_baseline(x) - F_future(x)| dx

SCVR (signed) = (area_future - area_baseline) / area_baseline

Where area = ∫ value d(exceedance_probability)
           = ∫₀¹ Q(p) dp      (quantile representation)
           ≈ E[X]              (at large n)
```

The sign matters for SCVR: a positive SCVR means the distribution shifted toward higher values.
For temperature that's a warming signal; for relative humidity that's a drying signal (negative).
Wasserstein W1 discards the sign by taking the absolute area — SCVR preserves direction.

See [04_scvr_methodology.md](04_scvr_methodology.md) for the full SCVR formula and
the empirical vs theoretical exceedance discussion.

---

## 3. Finance and Risk Management

Finance independently developed its own distribution shift tools, focused on loss distributions
rather than physical variables. The math converges with information theory.

### VaR — a single quantile shift

Value at Risk asks: "What is the loss at the 99th percentile?"

```
Loss distribution:

          P(loss > x)
    1.0  ┤
         │ ████
    0.5  ┤ ██████
         │ █████████
    0.1  ┤─────────────── ← VaR(99%) = $X
         │              ████
    0.0  ┤─────────────────────────── loss ($)
                        ^
                      VaR threshold
```

VaR is a **point measure** — it tells you one quantile, not the shape of the shift.
For climate risk this is insufficient: a distribution can shift its mean while its
99th percentile stays constant, or vice versa. SCVR integrates the full shape.

### CVaR / Expected Shortfall — tail area integral

Conditional Value at Risk answers: "Given that we exceed VaR, what is the expected loss?"

```
CVaR = E[loss | loss > VaR]
     = ∫_VaR^∞ x · f(x) dx  /  P(loss > VaR)
     = area under the tail  /  tail probability
```

CVaR is structurally the same integral as SCVR, but:
- Restricted to the tail (above VaR threshold)
- Not normalized by the baseline distribution
- Absolute dollars, not fractional shift

**Analogy:** CVaR measures the shifted tail. SCVR measures the shifted full distribution.

### Stress testing — deterministic shift

Regulatory stress tests (Basel III, DFAST) apply a fixed scenario: "What if rates rise 300bp?"
This is a single-point distribution shift, not a distributional comparison. It is the finance
equivalent of the "delta method" in hydrology — simple, transparent, but loses the full
distributional shape.

### Extreme Value Theory (EVT)

EVT fits a Generalized Extreme Value (GEV) or Generalized Pareto Distribution (GPD) to the
tail and extrapolates to unobserved return periods (500-year, 1000-year events).

```
EVT workflow:
  Data → fit GEV parameters (μ, σ, ξ) → extrapolate return period curve
```

EVT is parametric. SCVR is empirical. At n=65,700 daily values the empirical approach
is already converged — the added complexity of EVT fitting is not needed.

---

## 4. Insurance and CAT Modeling

The insurance industry built its own equivalent of the Wasserstein integral for pricing
catastrophe risk. They called it the Average Annual Loss.

### Exceedance Probability (EP) curves

The standard CAT model output is an EP curve: P(annual loss > x) vs x. This is exactly
the exceedance curve SCVR uses, but for loss amounts rather than physical climate variables.

```
EP curve (CAT model):         Exceedance curve (SCVR):
  P(loss > x)                   P(value > x)
  1.0 ┤                         1.0 ┤
      │  baseline                    │  baseline
  0.5 ┤     future               0.5 ┤     future
      │       (shifted)              │       (shifted right)
  0.0 ┤──────────────────        0.0 ┤──────────────────
         loss ($)                       value (°C, mm, etc)

      Same shape. Different x-axis.
```

### Average Annual Loss (AAL)

AAL = ∫ loss · f(loss) d(loss) = E[annual loss] = area under loss EP curve.

This is the actuarial world's version of our area = E[X] integral. Insurers price policies
using AAL. A climate-adjusted model computes AAL_future > AAL_baseline and charges a
higher premium.

**SCVR = (AAL_future − AAL_baseline) / AAL_baseline** — just applied to physical climate
variables instead of dollar losses.

The insurance and information theory communities independently converged on the same integral
because integrating the full exceedance curve is the right summary statistic for a shifted
distribution.

### Probable Maximum Loss (PML)

PML is the 250-year or 500-year return period loss — a single tail quantile. Like VaR, it
is a point measure, not an area measure. Simpler to communicate, but loses distributional shape.

### Return period shift

"The 100-year flood is now a 50-year flood." This expresses the shift as a change in
exceedance probability at a fixed value. Related to SCVR but local (single point) rather
than global (full distribution).

---

## 5. Hydrology and Civil Engineering

Hydrology has the longest history of working with non-stationary climate distributions,
driven by infrastructure design standards (dams, levees, drainage) that must remain safe
for 50-100 year lifespans.

### Non-stationary frequency analysis

Fit a GEV distribution where the parameters are functions of time (or CO2 concentration):

```
μ(t) = μ₀ + μ₁ × t       (location = mean drifts with time)
σ(t) = σ₀ × exp(σ₁ × t)  (scale = variability changes with time)
```

This captures a continuously shifting distribution, not just baseline vs future.
More flexible than SCVR, but requires fitting and assumes a parametric form.

### Mann-Kendall trend test

Non-parametric test for a monotonic trend in a time series of annual extremes (e.g. annual
maximum daily temperature). Tells you whether the distribution is shifting, not by how much.

### Delta method / quantile mapping

The simplest approach: shift the future distribution by the difference in means.

```
Future value = baseline value + (future mean − baseline mean)
```

Used for bias-correcting climate model output. SCVR does not use this — it compares
pooled empirical distributions directly, preserving changes in variance and shape.

### Design standard recalibration

"This dam was designed for the 1% AEP (Annual Exceedance Probability) flood under 1950
climate. Under 2050 climate, what was a 1% event is now a 2.5% event."

This is a return period shift analysis — the same concept as SCVR but expressed as
a change in exceedance probability at a fixed threshold rather than a change in expected value.

---

## 6. Machine Learning — Distribution Shift Detection

In ML, when a model is trained on distribution P and deployed on distribution Q,
performance degrades. Detecting and measuring this shift is a major research area.

```
ML distribution shift taxonomy:

   Training data distribution P(X, Y)
         |
         | shifts to
         v
   Production data distribution Q(X, Y)

   Three types:
   ┌─────────────────────────────────────────┐
   │ Covariate shift:  P(X) ≠ Q(X)          │
   │                   P(Y|X) = Q(Y|X)      │
   │                   (inputs drift)        │
   ├─────────────────────────────────────────┤
   │ Concept drift:    P(X) = Q(X)           │
   │                   P(Y|X) ≠ Q(Y|X)      │
   │                   (relationship changes) │
   ├─────────────────────────────────────────┤
   │ Dataset shift:    both change            │
   └─────────────────────────────────────────┘
```

**Climate risk framing:** Climate change is covariate shift — the input distribution P(X)
(temperature, rainfall, wind) shifts, but the engineering failure physics P(Y|X)
(degradation given climate) is constant. SCVR measures exactly the covariate shift.

### Population Stability Index (PSI)

Credit scoring and banking use PSI to monitor whether a population has drifted since
a model was built:

```
PSI = Σ (Actual_i − Expected_i) × ln(Actual_i / Expected_i)

Where i = bins of the distribution.

Rule of thumb:
  PSI < 0.10  → no significant shift
  PSI 0.10–0.25 → moderate shift, investigate
  PSI > 0.25  → major shift, rebuild model
```

PSI is a discretized, asymmetric version of KL divergence. Widely used because it's simple
to compute from binned data and easy to explain to non-quants.

### Kolmogorov-Smirnov (KS) statistic

KS measures the maximum vertical gap between two CDFs:

```
CDF comparison:
  1.0 ┤      ┌──────── F_future
      │  ┌───┘    ← KS stat = max|F_1(x) - F_2(x)|
      │  │                    = largest vertical gap
  0.0 ┤──┘  F_baseline
         x_min        x_max

  KS focuses on the single worst point of divergence.
  Wasserstein sums the entire area between the curves.
  SCVR is a signed, normalized Wasserstein.
```

KS is used for hypothesis testing (are these two distributions the same?). SCVR is not a
hypothesis test — it quantifies the magnitude and direction of shift unconditionally.

### Maximum Mean Discrepancy (MMD)

MMD maps both distributions into a kernel (feature) space and measures the distance between
their mean embeddings. Widely used in deep learning for domain adaptation. Not interpretable
in physical units, unlike Wasserstein and SCVR.

---

## 7. Engineering Reliability

Engineering reliability models do not measure distribution shift — they consume the shift
as an input to compute physical damage accumulation. These are the downstream models in
LTRisk's HCR → EFR → IUL chain.

| Model | What it takes as input | What it outputs |
|---|---|---|
| Peck's (solar aging) | Temperature × humidity distribution | Module degradation rate per year |
| Coffin-Manson (thermal fatigue) | Freeze-thaw cycle distribution | Crack propagation rate |
| Palmgren-Miner (wind fatigue) | Wind speed distribution | Cumulative structural damage fraction |
| Weibull / ALT | Stress level distribution | Time-to-failure distribution |

The connection: SCVR quantifies how much the climate variable distribution shifted.
Engineering models translate that shift into physical damage. See
[07_hcr_hazard_change.md](07_hcr_hazard_change.md) and [08_efr_equipment_degradation.md](08_efr_equipment_degradation.md) for the full chain.

---

## 8. Where SCVR Sits — Full Comparison

> **Why this matters:** If a quant reviewer, regulator, or institutional investor asks
> "what methodology is this based on?" — the answer is: normalized signed Wasserstein W1
> distance applied to empirical climate variable distributions. It has a 40-year literature
> behind it, and it converges with the actuarial AAL integral that the insurance industry
> has used for decades.

| Method | Field | What it integrates | Normalized? | Sign preserved? | Parametric? |
|---|---|---|---|---|---|
| KL Divergence | Information theory | Log-ratio weighted sum | No | No | Optional |
| Wasserstein W1 | Information theory | Full CDF area | No | No (absolute) | No |
| KS statistic | Statistics | Max point gap only | No | No | No |
| VaR | Finance | Single quantile | No | Yes | Optional |
| CVaR / ES | Finance | Tail area only | No | Yes | Optional |
| AAL | Insurance | Full loss CDF | No | Yes | Yes/No |
| PSI | Credit/ML | Binned KL-like | No | No | No |
| Delta method | Hydrology | Mean shift only | No | Yes | No |
| GEV non-stationary | Hydrology | Parametric full distribution | Optional | Yes | Yes |
| **SCVR** | **Climate risk** | **Full value CDF** | **Yes (÷ baseline)** | **Yes** | **No** |

SCVR is the only method in common use that combines:
- Full distribution (not just tail or mean)
- Normalized (fractional shift, not absolute)
- Sign-preserving (direction of shift matters)
- Empirical (no parametric assumptions)

---

## 9. Why SCVR's Specific Choices Are Defensible

### Choice 1: Empirical, not parametric

SCVR does not fit a GEV, Normal, or any other distribution. It uses the data directly.

**Why:** At n=65,700 daily values (6 models × 30 years × ~365 days), the empirical CDF
has already converged to the true distribution. The trapezoid integration error is
< 0.0001% (see [scvr/01_what_is_scvr.md](scvr/01_what_is_scvr.md) for the error analysis).
Fitting a parametric model adds distributional assumptions without improving accuracy,
and introduces risk of misspecification — especially in the tails where climate change
signal is strongest.

### Choice 2: Normalized ratio, not absolute distance

SCVR = (area_future − area_baseline) / area_baseline.

**Why:** Absolute Wasserstein distance is not comparable across variables or sites.
A +2°C shift at a hot desert site (tasmax baseline mean ~38°C) has different
physical consequences than a +2°C shift at a cold mountain site (baseline mean ~5°C).
Normalizing by the baseline area converts absolute shift into fractional shift,
making SCVR dimensionless and comparable:

```
Hot site (baseline mean = 38°C):  SCVR = 2/38 ≈ 0.053  → 5.3% shift
Cold site (baseline mean = 5°C):  SCVR = 2/5  ≈ 0.40   → 40% shift — physically correct
```

### Choice 3: Daily granularity, not annual

SCVR is computed from ~65,700 daily values, not from 30 annual means.

**Why:** Engineering failure models (Peck's, Coffin-Manson) are driven by the daily
distribution — cumulative damage depends on every cycle, not on the mean year.
Annual means collapse 365 days into one number, destroying the tail information that
drives degradation. A year with 20 days above 40°C and a year with 0 days above 40°C
can have the same annual mean. SCVR on annual means would call them identical. SCVR
on daily values captures the difference.

```
Annual means:   30.1°C   vs   30.1°C   → SCVR = 0 (same)
Daily data:     20 days >40°C  vs  0 days >40°C  → SCVR captures this
```

---

## Cross-References

- [04_scvr_methodology.md](04_scvr_methodology.md) — the SCVR formula step by step, empirical vs theoretical exceedance, trapezoid error analysis, Weibull vs linspace comparison
- [03_scenarios_and_time_windows.md](03_scenarios_and_time_windows.md) — why 1985-2014 baseline and 2026-2055 future
- [07_hcr_hazard_change.md](07_hcr_hazard_change.md) — how SCVR translates to hazard-specific impact ratios
- [08_efr_equipment_degradation.md](08_efr_equipment_degradation.md) — Peck's, Coffin-Manson, Palmgren-Miner deep dives
- [09_nav_impairment_chain.md](09_nav_impairment_chain.md) — the complete SCVR → NAV chain

---

*Next: [07_hcr_hazard_change.md](07_hcr_hazard_change.md) — how a SCVR number
translates into hazard ratios and then dollar figures on the balance sheet.*
