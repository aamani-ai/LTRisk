# Discussion: HCR Pathways A & B — From Basics

*2026-03-19 — A single reference for the two ways to compute Hazard Change Ratio (HCR),
why they exist, how they work, and when to use which.*

---

## 1. The Setup: What HCR Needs to Answer

HCR answers: *"How many more hazard events does climate change produce?"*

For example: if the baseline climate produces 15 heat wave days per year, and the
future climate produces 18, that's a 20% increase in the hazard. HCR = +0.20.

The question is: **how do you get from climate data to that 20% number?**

There are two routes. Both start from the same daily climate data (NEX-GDDP-CMIP6,
~300K pooled daily values per variable). They diverge in how they use that data.

```
           Same input data
           (daily climate values from ~30 CMIP6 models)
                    │
          ┌─────────┴──────────┐
          │                    │
     PATHWAY A            PATHWAY B
     (indirect)           (direct)
          │                    │
  SCVR first,            Count hazard
  then scale             events directly
          │                    │
    HCR ≈ SCVR × k       HCR = (count_fut - count_base)
                                  / count_base
          │                    │
          └─────────┬──────────┘
                    │
              Same goal: HCR
```

---

## 2. Pathway A — The Indirect Route (Via SCVR)

### How it works

1. Compute SCVR = `(mean_future - mean_baseline) / mean_baseline`
   This tells you how much the **entire distribution** shifted.

2. Multiply by a **scaling factor** to estimate how that distribution shift
   translates into hazard threshold crossings.

```
HCR_heat ≈ SCVR_tasmax × 2.5

Where:
  SCVR_tasmax = +0.069  (distribution shifted 6.9%)
  scaling = 2.5         (tail amplification factor)
  HCR_heat ≈ 0.173     (17.3% more heat wave days)
```

### Why the scaling factor isn't 1.0

A small shift in the mean causes a **larger** change in threshold crossings.
This is because hazard events live in the tail of the distribution, where values
are densely packed near the threshold.

```
Temperature distribution:

                    ┌──┐
                 ┌──┤  │
              ┌──┤  │  │
           ┌──┤  │  │  │
        ┌──┤  │  │  │  │
     ┌──┤  │  │  │  │  ├──┐
  ───┴──┴──┴──┴──┴──┴──┴──┴───── 43°C threshold
  20  25  30  35  40  45  50

  Many days cluster between 40-43°C.
  A +2°C mean shift pushes ALL of them above 43°C.

  The mean shifted ~7%. But days above 43°C increased ~17%.
  → Amplification factor ≈ 2.5×
```

### The scaling factors (current working estimates)

| Hazard | Variable | Scaling Factor | Source |
|--------|----------|:--------------:|--------|
| Heat stress — compound HW (3+ consec. days, tasmax+tasmin > P90) | tasmax | 2.0–3.0× (base: 2.5) | Tail amplification; NB01 cross-check gives ~2.9 |
| Heat stress — P90 per-DOY single-day exceedance (tasmax only) | tasmax | ~26× | NB04 empirical (2026-03-19) |
| Cold reduction (frost days) | tasmin | −0.25 to −0.40× | Beneficial — fewer frost events |
| Flood risk (rx5day, extreme precip) | pr | 1.5–2.0× (base: 1.75) | Extreme precipitation amplification |
| Fire weather (FWI) | tasmax + pr + hurs + sfcWind | Compound — TBD | Multi-variable interaction |
| Wind fatigue | sfcWind | ~1.0× | Small signal, near-linear |
| Corrosion / mould (humidity) | hurs | 0.5–1.5× | Threshold-dependent |

*(Source: [07_hcr_hazard_change.md](../learning/C_financial_translation/07_hcr_hazard_change.md) §2B)*

### Pros

- Fast: SCVR is already computed. Multiply by one number.
- Works without annual hazard count data (e.g., for new variables where
  Pathway B hasn't been set up yet).
- Consistent with the SCVR framework — everything flows from the distribution
  shift metric.

### Cons

- **The scaling factor is uncertain.** It's the biggest uncertainty in the chain.
  The range between low and high estimates can change NAV by +/- $2M.
- **Assumes a linear relationship between SCVR and HCR.** This is only approximately
  true when SCVR is small (< 0.15). For larger shifts, the relationship is non-linear.
- **Jensen's inequality:** Hazard thresholds are non-linear functions of the
  distribution. The mean shift (SCVR) doesn't tell you how the tail changes.
  See [discussion_jensen_inequality_hcr_scvr.md](discussion_jensen_inequality_hcr_scvr.md)
  for the full explanation.

### When Pathway A fails

```
SCVR_pr = -0.001  (precipitation mean barely changed)

HCR_flood ≈ (-0.001) × 1.75 = -0.00175  → "flood risk decreased 0.2%"

But actual extreme rain days INCREASED.
The mean missed the tail signal entirely.
Pathway A gives the WRONG SIGN for precipitation.
```

This happens because:
- SCVR captures the **mean** of the distribution
- Hazards depend on **threshold crossings in the tail**
- For some variables (precipitation), the mean and the tail move independently

---

## 3. Pathway B — The Direct Route (Counting Hazard Events)

### How it works

1. For each day in the daily data, apply the hazard threshold:
   *"Is this day a heat wave day? Is this day's rainfall extreme?"*

2. Count how many days exceed the threshold, separately for baseline and future.

3. HCR = `(count_future - count_baseline) / count_baseline`

```
Example — heat wave days (threshold: daily max temp > 35°C for 3+ consecutive days)

Baseline pool (28 models × 30 years):
  Total days above 35°C: 127,890 out of 306,600
  Heat wave events: 4,500 (averaged across models/years → ~15/year)

Future pool (28 models × 30 years, SSP2-4.5):
  Total days above 35°C: 152,400 out of 306,600
  Heat wave events: 5,400 (→ ~18/year)

HCR_heat = (5400 - 4500) / 4500 = +0.20  (20% more heat wave days)
```

### Why this avoids Jensen's inequality

Pathway B applies the hazard function h(x) to **each day individually**, then averages:

```
Pathway B computes:   E[h(X)]   (average of "is this day a hazard?" across all days)

Pathway A computes:   h(E[X])   (apply hazard function to the average day)

Jensen's inequality says:   E[h(X)] ≠ h(E[X])   when h is non-linear

Hazard thresholds (h(x) = 1 if x > threshold, else 0) are maximally non-linear.

Pathway B evaluates h first, then averages → correct.
Pathway A averages first, then applies h → wrong (Jensen's gap).
```

### What NB01 already computes

The pipeline already has Pathway B infrastructure for several hazards:

```
NB01 Annual Climate Indices       Corresponding Hazard
──────────────────────────        ────────────────────
heat_wave_days(t)            →    Heat stress HCR
frost_days(t)                →    Freeze-thaw HCR
rx5day(t)                    →    Flood risk HCR (5-day max precip)
fwi_mean(t)                  →    Fire weather HCR
tropical_nights(t)           →    Heat stress HCR (nighttime)
```

These are annual hazard counts per model. To get HCR:

```
HCR = (mean_annual_count_future - mean_annual_count_baseline)
      / mean_annual_count_baseline
```

### Pros

- **Physically correct.** No scaling factor assumptions. No Jensen's inequality
  problem. The threshold function is applied to individual data points, not to
  a summary statistic.
- **Works for precipitation.** The tail signal that SCVR misses is captured
  directly because you're counting extreme events, not measuring mean shift.
- **NB01 already has the infrastructure** for several key hazards.

### Cons

- Requires full daily data for both baseline and future periods.
- Requires defining exact hazard thresholds (what temperature counts as a
  "heat wave day"? what precipitation rate counts as "extreme"?).
- Annual counts can be noisy for rare events — need multi-model averaging.
- More computationally expensive than a simple multiplication.

---

## 4. Side-by-Side Comparison

| | Pathway A | Pathway B |
|---|---|---|
| **Input** | SCVR (single number) | Daily climate data (~300K values) |
| **Method** | HCR ≈ SCVR × scaling_factor | HCR = (count_fut − count_base) / count_base |
| **Assumptions** | Linear SCVR-to-HCR relationship; constant scaling | Hazard threshold correctly defined |
| **Jensen's problem** | Yes — mean ≠ tail behavior | No — evaluates threshold per day |
| **Scaling factors** | Required (uncertain) | Not needed |
| **Speed** | Instant (one multiplication) | Moderate (needs daily data processing) |
| **Precipitation** | **Fails** (SCVR ≈ 0 → HCR ≈ 0) | Works correctly |
| **Already in pipeline** | Via SCVR from NB03 | Partially — NB01 has 5 hazard counts |
| **Best for** | Quick screening; variables with small, uniform shifts | Production HCR values; threshold-sensitive hazards |

---

## 5. Worked Example — Heat Stress at Hayhurst Solar

### Pathway A

```
From NB03:  SCVR_tasmax = +0.069  (SSP2-4.5)
Scaling:    2.5 (working estimate for heat stress)

HCR_heat = 0.069 × 2.5 = +0.173  (17.3% more heat wave days)
```

### Pathway B

```
From NB01:  Baseline heat_wave_days = ~15/year (across models)
            Future heat_wave_days   = ~18/year (SSP2-4.5, 2026-2055)

HCR_heat = (18 - 15) / 15 = +0.20  (20% more heat wave days)
```

### Cross-validation

```
Pathway A:  +17.3%
Pathway B:  +20.0%

Implied scaling factor = 0.20 / 0.069 = 2.9
  (vs our working estimate of 2.5)

Difference: Pathway A underestimates by ~14%.
  → The 2.5 scaling factor is slightly low.
  → Could revise to 2.9, or keep 2.5 as conservative.
```

This is the cross-validation loop the framework recommends. When A ≈ B, confidence
is high. When they diverge, trust B and update A's scaling factor.

### NB04 Empirical Findings (2026-03-19)

NB04 implemented Pathway B with **simple P90 per-DOY exceedance** (tasmax only,
no consecutiveness or tasmin requirement):

```
Result: HCR ≈ +177% (SSP2-4.5), +209% (SSP5-8.5)
Implied scaling ≈ 26×

This is ~10× higher than the compound heat wave result (~20%, scaling ~2.9).

Why the difference:
  Simple P90 is a much weaker filter (single day, single variable).
  By definition 10% of baseline days exceed P90, so small distribution
  shifts push many days over the threshold → large relative increase.

  Formal compound heat waves are much rarer events (~15/year = ~4% of
  days). The same distribution shift produces a smaller relative change.

Both results are correct for their respective definitions.
```

**Key insight:** Pathway A scaling factors are NOT universal — they must be
calibrated per threshold definition. The worked example above (2.5×) applies
to compound heat waves. NB04's 26× applies to simple P90 exceedance.

**Next step:** NB04 should implement the compound heat wave counter to complete
the cross-validation against the 2.5× estimate used in this document.

---

## 6. Worked Example — Precipitation (Where Pathway A Fails)

### Pathway A

```
From NB03:  SCVR_pr = -0.001  (SSP2-4.5)
Scaling:    1.75 (working estimate for flood risk)

HCR_flood = (-0.001) × 1.75 = -0.002  (0.2% fewer extreme rain events)
```

### Pathway B

```
From NB01:  Baseline rx5day = X mm
            Future rx5day   = X + Y mm  (increase in 5-day max precipitation)

Empirical HCR_flood = +0.03 to +0.05  (3-5% more extreme rain events)
```

### Why they disagree

```
SCVR says:   Mean precipitation barely changed (−0.1%)
Reality:     Mean stayed flat BUT the right tail fattened (+1.9% at P95)

Pathway A uses the mean (SCVR) → sees no change → HCR ≈ 0
Pathway B counts extreme days directly → sees the tail → HCR > 0

The SCVR decomposition confirms this:
  Mean SCVR:    -0.1%
  P95 SCVR:     +1.9%
  CVaR 95%:     +2.4%
  Model IQR:    7.8% (huge model disagreement)

SCVR is a mean. The mean misses the tail. Pathway A inherits the miss.
```

**Conclusion for precipitation:** Pathway B is mandatory. Pathway A gives the
wrong sign. No scaling factor can fix a zero (or wrong-sign) input.

---

## 7. Decision Matrix — Which Pathway for Which Hazard

| Variable | Class | Pathway A | Pathway B | Recommendation |
|----------|:-----:|:---------:|:---------:|----------------|
| tasmax → heat stress | A | Works (scaling ~2.5× compound HW; ~26× P90 per-DOY — threshold-dependent) | Works (NB01 has heat_wave_days) | **Use both. Cross-validate. Specify threshold definition.** |
| tasmin → frost/freeze | A | Works (scaling ~ −0.3×) | Works (NB01 has frost_days) | **Use both.** |
| pr → flood risk | B | **Fails** (SCVR ≈ 0) | Works (NB01 has rx5day) | **Pathway B only.** |
| hurs → corrosion/mould | C | Approximate (overstates) | Needs implementation | **Pathway A with caveat.** Implement B when possible. |
| sfcWind → structural | C | Works (small signal) | Needs implementation | **Pathway A adequate.** |
| rsds → solar performance | B | Signal is tiny | Not threshold-based — feeds performance model directly | **Neither.** rsds feeds Pathway B of the *framework* (generation performance), not HCR. |
| Compound (FWI) | — | Multi-variable — complex | Works (NB01 has fwi_mean) | **Pathway B only.** |

---

## 8. The Relationship to Jensen's Inequality

The full mathematical explanation is in
[discussion_jensen_inequality_hcr_scvr.md](discussion_jensen_inequality_hcr_scvr.md).
Here is the one-paragraph version:

Jensen's inequality says: **E[f(X)] ≠ f(E[X])** for non-linear f. Hazard thresholds
are non-linear (step functions). SCVR gives E[X] (the mean). Pathway A applies the
hazard function to E[X] — i.e., computes f(E[X]). Pathway B applies the hazard function
to each daily value first, then averages — i.e., computes E[f(X)]. Jensen says these
are different. Pathway B is the correct one.

The gap between Pathway A and B is the **Jensen's gap**. It's small when SCVR is small
and the distribution shape doesn't change (temperature). It's large — even infinite in
relative terms — when the mean and tail diverge (precipitation).

---

## 9. The Relationship to the Framework's Three Pathways

**Important naming note:** The LT Risk Framework document uses "Pathway A/B/C" for a
*different* concept:

```
FRAMEWORK level:
  Pathway A: Hazards → Business Interruption (BI)
  Pathway B: Climate → Generation Performance
  Pathway C: Regulatory & Market

HCR level (WITHIN Framework Pathway A):
  Pathway A: HCR from SCVR × scaling
  Pathway B: HCR from direct hazard counting
```

The HCR Pathways A and B are **sub-routes within the framework's Pathway A**. The
framework's Pathway B (generation performance) doesn't use HCR at all — it feeds
climate variables directly into physics-based performance models (e.g., rsds → solar
panel output).

When this document says "Pathway A" or "Pathway B," it always means the **HCR-level**
pathways unless explicitly noted otherwise.

---

## 10. Summary

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   Pathway A:  SCVR → multiply by scaling → HCR                     │
│               Fast. Approximate. Fails for precipitation.           │
│                                                                      │
│   Pathway B:  Daily data → count threshold crossings → HCR          │
│               Correct. Avoids Jensen's inequality.                  │
│               NB01 already has infrastructure for 5 hazards.        │
│                                                                      │
│   Recommendation:                                                    │
│     Use BOTH where possible. Cross-validate.                        │
│     When A ≈ B → confidence is high, scaling factor is good.        │
│     When A ≠ B → trust B, investigate the scaling factor.           │
│     For precipitation → Pathway B only (A gives wrong answer).      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

*Cross-references:*
- *[07_hcr_hazard_change.md](../learning/C_financial_translation/07_hcr_hazard_change.md) §10 — HCR two-pathway summary and calibration example*
- *[discussion_jensen_inequality_hcr_scvr.md](discussion_jensen_inequality_hcr_scvr.md) — Why E[f(X)] ≠ f(E[X]) and its empirical evidence*
- *[discussion_scvr_method_equivalence.md](discussion_scvr_method_equivalence.md) §11 — SCVR decomposition showing mean vs tail divergence*
- *[discussion_scvr_method_equivalence.md](discussion_scvr_method_equivalence.md) §13 — Companion metrics discussion*
- *[LONG_TERM_RISK_FRAMEWORK.md](../background/LONG_TERM_RISK_FRAMEWORK.md) §3-4 — Framework-level Pathways A/B/C*
