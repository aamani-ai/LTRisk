# Distribution Shift Quantification — Where SCVR Sits in a Larger Landscape

> SCVR answers one question: "By what fraction did the mean of this climate distribution shift?"
> This is not a novel question. Finance, insurance, hydrology, machine learning, and information
> theory all ask it. This doc maps the full landscape — every major method, what it measures,
> and exactly where SCVR fits — with an honest assessment of what SCVR captures and what it doesn't.

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
1. **What they summarize** — a point (single quantile), the tail, the mean, or the full shape
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

### Wasserstein W1 — related to SCVR but not the same

Wasserstein W1 is also called the "Earth Mover's Distance": how much earth (probability mass)
do you need to move, and how far, to transform distribution P into distribution Q?

```
W1 = ∫₀¹ |Q_future(p) - Q_baseline(p)| dp

    = integral of ABSOLUTE quantile-by-quantile difference
    = captures both location shift AND shape change
    = unsigned (always ≥ 0)
```

W1 is a true distance metric — it's sensitive to every difference between two distributions,
including changes in variance, skewness, and kurtosis.

### How SCVR relates to (but differs from) W1

SCVR uses the same quantile integral representation but computes something different:

```
W1   = ∫₀¹ |Q_future(p) - Q_baseline(p)| dp     ← absolute difference of quantiles
                                                     (shape-aware, unsigned)

SCVR = (∫₀¹ Q_future(p) dp  -  ∫₀¹ Q_baseline(p) dp)  /  ∫₀¹ Q_baseline(p) dp
     = (       E[X_future]   -        E[X_baseline]  )  /        E[X_baseline]
     = (    mean_future      -      mean_baseline     )  /      mean_baseline

     ← difference of integral means (NOT shape-aware, signed)
```

**The key difference:** W1 computes `|difference of quantiles|` — it measures how far apart
the distributions are at every point. SCVR computes `difference of integrals` — it measures
how the overall mean shifted. These are NOT equivalent:

```
Example where they disagree:

  Distribution A: mean = 30°C, std = 5°C     }  SCVR = 0  (same mean)
  Distribution B: mean = 30°C, std = 10°C    }  W1   > 0  (shape changed)

  Distribution C: mean = 30°C                }  SCVR = +0.067  (mean shifted)
  Distribution D: mean = 32°C                }  W1   = 2°C     (also detects it)
```

SCVR detects location shifts (the mean moved) but is blind to shape changes that preserve the
mean. W1 detects both. SCVR is a weaker metric than W1 — but for our use case, this is
acceptable (see Section 9 for why).

The sign matters: SCVR preserves direction (positive = warmer/wetter, negative = cooler/drier).
W1 discards direction by taking absolute values.

**Previous versions of this doc** described SCVR as a "normalized, signed Wasserstein W1 distance."
This was imprecise. SCVR is **related** to W1 (both use quantile integrals) but is not W1.
It is more accurately described as: *fractional change in the distribution mean, computed via the
exceedance curve area integral*.

See [04_scvr_methodology.md](../B_scvr_methodology/04_scvr_methodology.md) §3c for the full
derivation of why exceedance area = mean.

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

VaR is a **point measure** — it tells you one quantile, not the overall shift.
SCVR is a **mean measure** — it summarizes the net shift across all quantiles into one number.
Neither captures the full distributional shape on its own.

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

**Analogy:** CVaR measures the mean of the tail. SCVR measures the mean of the full distribution.
Both are mean-based metrics, just over different ranges.

### Stress testing — deterministic shift

Regulatory stress tests (Basel III, DFAST) apply a fixed scenario: "What if rates rise 300bp?"
This is a single-point distribution shift, not a distributional comparison. It is the finance
equivalent of the "delta method" in hydrology — simple, transparent, but assumes a uniform shift.

### Extreme Value Theory (EVT)

EVT fits a Generalized Extreme Value (GEV) or Generalized Pareto Distribution (GPD) to the
tail and extrapolates to unobserved return periods (500-year, 1000-year events).

```
EVT workflow:
  Data → fit GEV parameters (μ, σ, ξ) → extrapolate return period curve
```

EVT is parametric and tail-focused. SCVR is empirical and mean-focused. At n ≈ 306,000 daily
values (28 models × 30 years × ~365 days) the empirical mean is already well-converged. EVT
adds value when you need tail extrapolation beyond your data — SCVR doesn't attempt that.

---

## 4. Insurance and CAT Modeling

The insurance industry built its own version of the same mean integral for pricing
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

      Same structure. Different x-axis.
```

### Average Annual Loss (AAL)

AAL = ∫ loss · f(loss) d(loss) = E[annual loss] = area under loss EP curve.

This is the actuarial world's version of our area = E[X] integral. **AAL is a mean.** Insurers
price policies using AAL. A climate-adjusted model computes AAL_future > AAL_baseline and
charges a higher premium.

**SCVR = (AAL_future − AAL_baseline) / AAL_baseline** — just applied to physical climate
variables instead of dollar losses. Both are fractional changes in means computed via
exceedance curve areas.

This is SCVR's strongest cross-industry analogy: the insurance industry has used mean-based
exceedance area integrals for decades. The math is identical.

### Probable Maximum Loss (PML)

PML is the 250-year or 500-year return period loss — a single tail quantile. Like VaR, it
is a point measure, not an area measure. Simpler to communicate, but loses the distributional
picture.

### Return period shift

"The 100-year flood is now a 50-year flood." This expresses the shift as a change in
exceedance probability at a fixed value. Related to SCVR but local (single threshold) rather
than global (distribution mean).

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
More flexible than SCVR — it can detect both location and scale changes. But it requires
fitting and assumes a parametric form.

### Mann-Kendall trend test

Non-parametric test for a monotonic trend in a time series of annual extremes (e.g. annual
maximum daily temperature). Tells you whether the distribution is shifting, not by how much.

### Delta method / quantile mapping

The simplest approach: shift the future distribution by the difference in means.

```
Future value = baseline value + (future mean − baseline mean)
```

Used for bias-correcting climate model output. **SCVR is mathematically equivalent to the
delta method's fractional form** — both measure the change in mean. The difference is
implementation: SCVR computes the mean via exceedance area integration over pooled empirical
data, while the delta method typically uses parametric or model-specific means.

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
(degradation given climate) is constant. SCVR measures the mean of the covariate shift.

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
to compute from binned data and easy to explain to non-quants. Unlike SCVR, PSI is sensitive
to shape changes (it compares bin-by-bin proportions, not just means).

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
  SCVR compares the means (total areas under each curve).
```

KS is used for hypothesis testing (are these two distributions the same?). SCVR is not a
hypothesis test — it quantifies the magnitude and direction of mean shift.

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

The connection: SCVR quantifies how much the mean of the climate variable shifted.
The HCR step translates that mean shift into hazard-specific impact ratios. Engineering
models then translate those ratios into physical damage. See
[07_hcr_hazard_change.md](07_hcr_hazard_change.md) and [08_efr_equipment_degradation.md](08_efr_equipment_degradation.md) for the full chain.

---

## 8. Where SCVR Sits — Full Comparison

> **Honest framing for technical counterparties:** "SCVR is the fractional change in the
> distribution mean, computed empirically via exceedance curve area integration. It is
> related to the Wasserstein W1 distance (both use quantile integrals) but is a weaker
> metric — it captures location shift, not shape change. The same integral appears in
> the actuarial AAL framework used for catastrophe pricing."

| Method | Field | What it measures | Normalized? | Sign preserved? | Shape-aware? |
|---|---|---|---|---|---|
| KL Divergence | Information theory | Log-ratio divergence (full shape) | No | No | Yes |
| Wasserstein W1 | Information theory | Quantile-by-quantile distance (full shape) | No | No (absolute) | Yes |
| KS statistic | Statistics | Max CDF gap (single point) | No | No | No |
| VaR | Finance | Single tail quantile | No | Yes | No |
| CVaR / ES | Finance | Tail mean | No | Yes | Tail only |
| AAL | Insurance | Distribution mean (= SCVR equivalent) | No | Yes | No |
| PSI | Credit/ML | Binned divergence (full shape) | No | No | Yes |
| Delta method | Hydrology | Mean shift (= SCVR equivalent) | No | Yes | No |
| GEV non-stationary | Hydrology | Parametric location + scale | Optional | Yes | Yes |
| **SCVR** | **Climate risk** | **Distribution mean (fractional change)** | **Yes (÷ baseline)** | **Yes** | **No** |

SCVR combines:
- **Normalized** (fractional shift, comparable across variables and sites)
- **Sign-preserving** (direction of shift matters)
- **Empirical** (no parametric assumptions)
- **Mean-based** (captures location shift, not shape change)

The last point is a limitation, not a feature — see Section 10 for what SCVR misses
and how LTRisk handles it.

---

## 9. Why SCVR's Specific Choices Are Defensible

### Choice 1: Empirical, not parametric

SCVR does not fit a GEV, Normal, or any other distribution. It uses the data directly.

**Why:** At n ≈ 306,000 daily values (28 models × 30 years × ~365 days), the empirical mean
is converged to high precision. The trapezoid integration error vs the true mean is
< 0.003°C (see [04_scvr_methodology.md](../B_scvr_methodology/04_scvr_methodology.md) §3c).
Fitting a parametric model adds distributional assumptions without improving the mean estimate,
and introduces risk of misspecification.

### Choice 2: Normalized ratio, not absolute distance

SCVR = (mean_future − mean_baseline) / mean_baseline.

**Why:** Absolute mean shift is not comparable across variables or sites.
A +2°C shift at a hot desert site (tasmax baseline mean ~38°C) has different
physical consequences than a +2°C shift at a cold mountain site (baseline mean ~5°C).
Normalizing converts absolute shift into fractional shift, making SCVR dimensionless
and comparable:

```
Hot site (baseline mean = 38°C):  SCVR = 2/38 ≈ 0.053  → 5.3% shift
Cold site (baseline mean = 5°C):  SCVR = 2/5  ≈ 0.40   → 40% shift — physically correct
```

### Choice 3: Daily granularity, not annual

SCVR is computed from ~306,000 daily values, not from 30 annual means.

**Why:** Daily granularity gives a more precise mean estimate (larger n). But more importantly,
the daily data is preserved for the downstream HCR step, where we DO count tail exceedances
directly (Pathway B). SCVR itself doesn't use the tail information — it collapses to the
mean — but the same daily data feeds both SCVR and the direct counting pathway.

```
Annual means:   30.1°C   vs   30.1°C   → SCVR = 0, but Pathway B can still detect
                                           20 days >40°C vs 0 days >40°C
```

### Choice 4: Why a mean metric is sufficient

For **temperature variables** (tasmax, tasmin, tas), climate change primarily shifts the
entire distribution rightward — a location shift. The mean captures 90%+ of the signal.
Shape changes (variance, skewness) are secondary and largely consistent across models.
SCVR works well here.

For **precipitation and wind**, the mean shift is small and unreliable, but the shape
changes matter — more intense extremes even if the average barely moves. SCVR fails here,
which is exactly why LTRisk routes precipitation hazards through **Pathway B** (direct
threshold counting) instead of Pathway A (SCVR × scaling factor). See
[07_hcr_hazard_change.md](07_hcr_hazard_change.md) for the routing logic.

This design decision — using SCVR where it works (temperature) and bypassing it where
it doesn't (precipitation) — is more honest than claiming SCVR captures everything.

---

## 10. What SCVR Does NOT Capture

Being transparent about limitations strengthens the methodology. SCVR is blind to:

### Variance changes

If the distribution widens (more extreme days in both directions) but the mean stays
constant, SCVR = 0.

```
Baseline:  mean = 30°C, std = 5°C    ← narrow distribution
Future:    mean = 30°C, std = 8°C    ← wider (more extremes), but same mean

SCVR = (30 - 30) / 30 = 0          ← misses the change entirely
W1 > 0                              ← would catch it
Pathway B: counts days >40°C        ← would catch it (more exceedances)
```

### Skewness and kurtosis changes

If the right tail fattens (more extreme heat days) but the left tail thins by the same
amount (fewer cold days), the mean can stay constant while the risk profile changes
dramatically. SCVR = 0.

### Compensating shifts

If temperatures rise in summer but fall in winter by the same amount, the annual mean
is unchanged but the seasonal risk profile is very different. SCVR = 0.

### How LTRisk handles this

1. **Pathway A** (SCVR × scaling): Used for temperature hazards where mean shift dominates.
   The scaling factor translates the mean shift into hazard-specific impact.

2. **Pathway B** (direct counting): Used for precipitation, wind, and any hazard where
   shape changes matter more than mean changes. Bypasses SCVR entirely — counts threshold
   exceedances directly from the daily data.

3. **Companion metrics**: The `scvr_report.json` includes per-model SCVR, standard
   deviation changes, percentile shifts, and tail confidence flags. These supplement the
   headline SCVR number with shape information for review.

---

## 11. References

**Optimal transport and Wasserstein distance:**
- Villani, C. (2009). *Optimal Transport: Old and New*. Springer. — Definitive reference for Wasserstein distances.
- Panaretos, V.M. & Zemel, Y. (2019). "Statistical Aspects of Wasserstein Distances." *Annual Review of Statistics and Its Application*, 6, 405-431. — Accessible review of W1 properties and applications.

**The area = mean identity:**
- This is a standard result in probability theory: ∫₀¹ F⁻¹(p) dp = E[X], where F⁻¹ is the quantile function. See Billingsley, P. (1995). *Probability and Measure*, 3rd ed. Wiley. §21.

**Insurance exceedance curves and AAL:**
- Grossi, P. & Kunreuther, H. (2005). *Catastrophe Modeling: A New Approach to Managing Risk*. Springer. — EP curves, AAL, and PML as used in the CAT modeling industry.

**Climate model projections (our data source):**
- Thrasher, B., Wang, W., Michaelis, A. et al. (2022). "NASA Global Daily Downscaled Projections, CMIP6." *Scientific Data* 9, 262. https://doi.org/10.1038/s41597-022-01393-4

---

## Cross-References

- [04_scvr_methodology.md](../B_scvr_methodology/04_scvr_methodology.md) — the SCVR formula step by step, area = mean proof (§3c), trapezoid error analysis
- [03_scenarios_and_time_windows.md](03_scenarios_and_time_windows.md) — why 1985-2014 baseline and 2026-2055 future
- [07_hcr_hazard_change.md](07_hcr_hazard_change.md) — Pathway A vs B routing, how SCVR translates to hazard-specific impact ratios
- [08_efr_equipment_degradation.md](08_efr_equipment_degradation.md) — Peck's, Coffin-Manson, Palmgren-Miner deep dives
- [09_nav_impairment_chain.md](09_nav_impairment_chain.md) — the complete SCVR → NAV chain

---

*Next: [07_hcr_hazard_change.md](07_hcr_hazard_change.md) — how a SCVR number
translates into hazard ratios and then dollar figures on the balance sheet.*
