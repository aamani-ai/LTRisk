# Discussion: Jensen's Inequality — Why HCR ≠ f(SCVR)

*2026-03-19 — Explains why you cannot derive Hazard Change Ratio from SCVR alone,
and why the framework computes them via separate pathways.*

---

## 1. The Short Version

You can't compute HCR by putting SCVR into a formula because **hazard events are
non-linear functions of the distribution**, and knowing the mean shift doesn't tell
you how the tail changes.

---

## 2. The Intuition

```
SCVR says:  "mean temperature increased 8%"

But consider two futures that both have 8% higher mean:

  Future A: Everything shifts uniformly +3°C
            → 20 extra days above 43°C threshold

  Future B: Winters warm +5°C, summers warm +1.5°C
            → 5 extra days above 43°C threshold

Same SCVR. Very different HCR.
```

SCVR collapses the entire distribution into one number (the mean shift). HCR depends
on *where in the distribution* the shift happens relative to a threshold. That
information is lost when you take the mean.

---

## 3. The Math (Jensen's Inequality)

Jensen's inequality says: **for a convex function f,  E[f(X)] ≠ f(E[X])**

The hazard function is convex. Take "heat wave days" as an example:

```
h(x) = 1 if x > 43°C, else 0     ← step function (convex at threshold)

What we want:   HCR = E[h(X_future)] - E[h(X_baseline)]
                    = (fraction of days above 43°C, future)
                    - (fraction of days above 43°C, baseline)

What SCVR gives: E[X_future] - E[X_baseline]
                 = shift in the mean

Jensen says:     E[h(X)] ≠ h(E[X])

So:  "mean shifted 8%" does NOT tell you
     "threshold exceedances increased by f(8%)"
```

The step function h(x) = 1\_{x > threshold} is the extreme case. A tiny mean shift
can cause a huge change in exceedance count (because many values cluster near the
threshold), or zero change (if the threshold is far in the tail). **The amplification
depends on the shape of the distribution near the threshold — which SCVR throws away.**

### Visual: Same Mean, Different Threshold Crossings

```
  Probability density

              Future A                        Future B
         (uniform shift)                  (seasonal shift)

      ┌──┐                              ┌──┐
      │  │    Baseline                   │  │    Baseline
      │  │ ┌──┐                          │  │ ┌────────┐
      │  │ │  │ Future                   │  │ │        │ Future
      │  │ │  │                          │  │ │        │
      │  │ │  │ ┌──┐                     │  │ │        │
      │  │ │  │ │  │                     │  │ │        │ ┌──┐
  ────┴──┴─┴──┴─┴──┴── 43°C ──          ────┴──┴─┴────────┴─┴──┴── 43°C ──
                   ▲                                         ▲
               Many days                                Fewer days
            cross threshold                          cross threshold

  Both have E[X_future] = E[X_baseline] + 3°C  →  same SCVR = 8%
  But Future A has 4× more threshold exceedances than Future B.
```

---

## 4. Why This Matters — Empirical Evidence from Our Pipeline

This isn't just theory. The SCVR decomposition diagnostics we ran on all 7 variables
at Hayhurst Solar quantify exactly how large the Jensen's gap is:

| Variable | Mean SCVR | Tail P95 SCVR | Jensen's Gap |
|----------|:---------:|:-------------:|:-------------|
| tasmax   | +6.9%     | +4.9%         | Mean overstates tail by 30% |
| tasmin   | +14.4%    | +8.0%         | Mean overstates tail by 44% |
| **pr**   | **−0.1%** | **+1.9%**     | **Mean misses tail entirely — opposite sign** |
| hurs     | −3.1%     | −0.7%         | Mean overstates tail by 4× |
| sfcWind  | −2.2%     | −1.3%         | Mean overstates tail by 40% |
| rsds     | +0.5%     | −0.0%         | Tails move opposite to mean |

*(Source: `data/processed/presentation/hayhurst_solar/*/scvr_decomposition_*.json`,
SSP2-4.5 values)*

**For precipitation, Jensen's inequality bites hardest:** the mean says "no change"
but the convex threshold function (extreme rain events) sees a +2–3% increase. If you
computed flood HCR from SCVR alone, you'd get HCR ≈ 0. The actual tail-based HCR is
meaningfully positive.

---

## 5. What the Framework Does About It

That's why the HCR document defines **two pathways**:

```
PATHWAY A:  HCR ≈ SCVR × scaling_factor

  → Quick approximation. The scaling factor is a LINEAR
    correction for Jensen's gap. Works when SCVR < 0.15
    and the distribution shape doesn't change much.
  → This is where the 2.5× heat factor comes from.
  → Limitation: assumes the Jensen's gap is constant.
    It's not — it depends on how far the threshold is
    into the tail and how the shape changes.

PATHWAY B:  HCR = (hazard_count_future - hazard_count_baseline)
                  / hazard_count_baseline

  → Direct computation from daily data. No Jensen's problem
    because you're applying h(x) to each day's value FIRST,
    then averaging — i.e., computing E[h(X)] directly.
  → This is the correct approach.
  → NB01 already computes many hazard counts (heat_wave_days,
    frost_days, rx5day, fwi_mean).
```

Pathway A tries to approximate the Jensen's gap with a constant multiplier.
Pathway B avoids it entirely by computing HCR from the raw daily data, never
going through SCVR at all.

### When Pathway A Is Good Enough

```
Pathway A works when:
  1. SCVR is small (< 0.15) — linear approximation holds
  2. Distribution shape doesn't change — only shifts
  3. The scaling factor was calibrated against Pathway B

Pathway A fails when:
  1. Mean SCVR ≈ 0 but tails change (precipitation!)
  2. Seasonal structure of the shift matters (Future A vs B above)
  3. The threshold sits deep in the tail (rare events amplify more)
```

### The Recommended Approach

```
Use BOTH pathways. Cross-validate.

If Pathway A ≈ Pathway B:
  → Scaling factor is well-calibrated. Use either.

If Pathway A ≠ Pathway B:
  → Jensen's gap is non-trivial. Trust Pathway B.
  → Investigate why — shape change? seasonal structure?
  → Update the scaling factor.
```

---

## 6. Connection to SCVR Decomposition

The SCVR decomposition diagnostic (§11 of the
[SCVR method equivalence discussion](discussion_scvr_method_equivalence.md))
directly measures the Jensen's gap by comparing mean SCVR against tail-specific
metrics (P95, P99, CVaR). The "Tail P95 SCVR" column in the table above is
essentially measuring: "what does the hazard-relevant part of the distribution do,
compared to what the mean says?"

For **temperature**: Jensen's gap is modest (30–44%). The 2.5× scaling factor in
Pathway A approximately corrects for it.

For **precipitation**: Jensen's gap is infinite in relative terms (the mean and
tail have opposite signs). No constant scaling factor can fix this. Pathway B is
mandatory.

---

## 7. One-Liner Summary

> **Jensen's inequality means: the mean of a non-linear function ≠ the non-linear
> function of the mean. Hazard thresholds are non-linear. SCVR gives the mean.
> So HCR ≠ f(SCVR) — you need the full daily distribution to compute HCR correctly.**

---

*References: Jensen (1906); HCR Pathway A/B — see
[07_hcr_hazard_change.md](../learning/C_financial_translation/07_hcr_hazard_change.md) §10;
SCVR decomposition — see
[discussion_scvr_method_equivalence.md](discussion_scvr_method_equivalence.md) §11.*
