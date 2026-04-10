---
title: "Discussion — Severity Ratio Sensitivity: What It Depends On and How It Evolves"
type: discussion
domain: climate-risk / methodology / severity
created: 2026-04-10
status: draft
context: >
  The severity ratio (mean_excess_future / mean_excess_baseline) captures
  how much more intense hazard events become under climate change. But it
  is NOT a fixed physical constant — it depends on the threshold definition
  (our choice) and data quality (which improves over time). This doc
  explores both dependencies and the Gen.1→2→3 evolution path.
relates-to:
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/discussion/hcr_financial/hcr_redefined_freq_severity.md
  - docs/discussion/hcr_financial/pathway_defensibility.md
---

# Severity Ratio Sensitivity

> **The question:** The severity ratio for heat wave at Hayhurst is 1.48
> (+48% more intense events). Is this a stable number, or does it change
> depending on how we define and compute it?

> **The answer:** It depends on two things — the threshold definition (our
> choice) and the data quality (which evolves). It IS our best current
> estimate, but it will refine as methods improve.

---

## 1. What Severity Ratio Measures

```
severity_ratio = E[X - T | X > T, future] / E[X - T | X > T, baseline]

  = "mean excess above threshold in future" / "same in baseline"
  = "how far above the threshold are events, on average" (future vs baseline)

For heat wave at Hayhurst (SSP5-8.5, per-DOY P90 threshold):
  Baseline: events exceed P90 by 1.29°C on average
  Future:   events exceed P90 by 1.91°C on average
  severity_ratio = 1.91 / 1.29 = 1.48

This says: when events DO occur, they're 48% more intense above
the threshold than in the baseline climate.
```

---

## 2. Dependency 1: Threshold Definition

The threshold determines WHERE on the distribution you're measuring.
Different thresholds give different severity ratios from the SAME data.

### Why Higher Thresholds Give Larger Severity Ratios

```
When the distribution shifts right:

  Lower threshold (P75):
    Many days exceed it in both baseline and future.
    The excess above P75 changes modestly.
    Severity ratio: ~1.1-1.2

  Medium threshold (P90):
    Fewer days exceed it. Those that do are in the tail.
    The tail shifts more than the body.
    Severity ratio: ~1.4-1.5  ← what we use

  Higher threshold (P99):
    Very few days exceed it. Deep in the tail.
    Small distribution shift moves a lot of mass across.
    Severity ratio: potentially >2.0

  The deeper into the tail you measure, the more sensitive
  the severity ratio is to the distribution shift.
```

### Illustrative Examples (Hayhurst heat wave, SSP5-8.5)

```
THRESHOLD        BASELINE EXCESS    FUTURE EXCESS    SEVERITY RATIO
                 E[X-T | X>T]      E[X-T | X>T]
═══════════      ═══════════════    ═════════════    ══════════════
Per-DOY P75      ~2.8°C             ~3.4°C           ~1.21
Per-DOY P90      1.29°C             1.91°C           1.48  ← current
Per-DOY P95      ~0.7°C             ~1.2°C           ~1.71
Absolute 40°C    ~3.5°C             ~5.0°C           ~1.43

NOTE: These are ESTIMATES based on the shape of the tail.
Exact values require recomputing from daily data at each threshold.
The pattern is clear: higher thresholds → larger severity ratios.
```

### This Is the Same Subjectivity Problem as Frequency

```
Just as frequency HCR depends on threshold definition
(2.5× for compound heat wave vs 26× for simple P90 exceedance),
the severity ratio also depends on threshold definition.

For frequency: we resolved this by using published scaling (2.5×)
  where available, and direct counting where necessary.

For severity: we don't have published severity ratios.
  We compute from our data using per-DOY P90.
  This is a reasonable choice but IS a choice.
```

---

## 3. Dependency 2: Data Quality

### What We Currently Have

```
Source:     NASA NEX-GDDP-CMIP6 (bias-corrected, downscaled)
Resolution: Daily values (not hourly)
Grid:       0.25° (~25km)
Models:     20 with complete coverage
Period:     30-year baseline (1985-2014) + 30-year future (2026-2055)
```

### How Data Quality Affects Severity

```
DAILY RESOLUTION:
  We measure daily max temperature, not hourly peaks.
  The actual peak during a heat wave may be 2-3°C above the daily max.
  Our severity ratio captures the daily-level shift, not the sub-daily.
  
  Impact: severity ratio may UNDERESTIMATE the true intensity change
  because daily averaging smooths the worst hours.
  
  Improvement: hourly CMIP6 data (available for some models) would give
  more precise severity, especially for short-duration events.

MODEL SPREAD:
  20 models × 30 years × 365 days = ~219,000 pooled daily values.
  The mean excess is computed from ALL days above threshold across
  all models. Individual models may disagree on severity.
  
  Impact: pooling reduces noise but obscures model disagreement.
  Some models may show larger severity shifts than others.
  
  Improvement: report per-model severity spread (IQR) alongside
  the ensemble mean. Already done for frequency (model IQR in
  SCVR Report Card). Can extend to severity.

GRID RESOLUTION:
  0.25° grid means each "daily value" represents a ~25km area average.
  Local extremes (urban heat islands, valley effects) are smoothed.
  
  Impact: severity may be underestimated for site-specific microclimates.
  
  Improvement: higher-resolution downscaling (LOCA2, ~6km) or
  station-based bias correction would sharpen the severity signal.
```

---

## 4. Gen.1 → Gen.2 → Gen.3 Evolution

### Gen.1 (Current Implementation)

```
What we compute:
  - Severity ratio per hazard per scenario (epoch-level, one number)
  - Per-DOY P90 threshold for heat wave
  - P95 wet-day threshold for precipitation
  - Computed from 20-model ensemble, pooled daily data

Characteristics:
  - CONSTANT across years (one severity ratio for entire 2026-2055)
  - Single threshold definition (P90)
  - No per-model severity spread
  - No threshold sensitivity analysis

Strengths:
  + Simple, one number per hazard
  + Mathematically exact (expected shortfall identity)
  + Uses data already computed

Limitations:
  - Severity may change decade by decade (not captured)
  - Threshold choice affects the number (not tested)
  - Model disagreement not reported
```

### Gen.2 (Planned Improvement)

```
What to add:
  - DECADE-VARYING severity (compute per-decade, not per-epoch):
      2026-2035: severity_ratio_early (e.g., 1.30)
      2036-2045: severity_ratio_mid (e.g., 1.48)
      2046-2055: severity_ratio_late (e.g., 1.65)
    → Severity likely INCREASES over time as warming accelerates
  
  - THRESHOLD SENSITIVITY analysis:
      Recompute severity ratio at P75, P90, P95, P99
      Report the range (e.g., "1.2× at P75 to 1.7× at P95")
      Document which threshold is most relevant for BI vs derating
  
  - PER-MODEL SEVERITY SPREAD:
      severity IQR across 20 models
      Flag if models disagree on severity direction

Characteristics:
  - Time-varying (tracks acceleration)
  - Multi-threshold (shows sensitivity)
  - Uncertainty-quantified (model spread)
```

### Gen.3 (Target Architecture)

```
What changes fundamentally:
  - NO SEPARATE SEVERITY RATIO — it's embedded in the damage function
  - Compute E[D(X)] directly from daily data:
      For each day: apply D(intensity) → damage
      HCR = E[D(X)_future] / E[D(X)_baseline] - 1
  
  - The damage function D(intensity) IS the severity translation:
      D maps intensity to financial loss
      Days far above threshold cause proportionally MORE damage
      The nonlinearity of D captures severity automatically
  
  - Requires: damage functions per hazard per asset type
      Heat wave: inverter derating curve (temperature → lost generation)
      Flood: depth-damage curve (HAZUS)
      Wind: V^3 power law
  
  - The severity ratio becomes a DIAGNOSTIC (decomposition of HCR)
    rather than an INPUT to HCR computation

Characteristics:
  - Physically grounded (damage functions from engineering)
  - No threshold subjectivity (D integrates over entire distribution)
  - Naturally time-varying (each year's D(X) is computed)
  - No double-counting risk (single computation, not freq × severity)
```

---

## 5. Practical Implications

### For Decision-Making Today

```
The current severity ratio (1.48 for heat wave) is:
  ✓ Our best estimate from the data we have
  ✓ Mathematically sound (expected shortfall identity)
  ✓ Computed from 20 peer-reviewed climate models
  
  ⚠ Dependent on per-DOY P90 threshold definition
  ⚠ Constant across all 30 future years (no time variation)
  ⚠ May be underestimated (daily resolution, grid smoothing)

For reporting:
  "Events are approximately 48% more intense above the heat threshold
   under SSP5-8.5, based on 20 CMIP6 model ensemble. This estimate
   depends on the threshold definition and may evolve with improved
   data and methods."
```

### For Planning Future Improvements

```
PRIORITY 1 (highest value, moderate effort):
  Decade-varying severity. Compute per-decade instead of per-epoch.
  Shows whether severity accelerates — important for late-life years.

PRIORITY 2 (moderate value, low effort):
  Threshold sensitivity. Recompute at P75/P90/P95/P99.
  One additional loop in NB04a. Shows the range.

PRIORITY 3 (high value, high effort):
  Full damage function integration (Gen.3).
  Requires defining D(intensity) per hazard from engineering specs.
  Eliminates threshold subjectivity entirely.
```

---

## 6. Sensitivity Test

How much does the combined HCR change if severity ratio moves ±20%?

```
HEAT WAVE (HCR_freq = +20%, published scaling):

  Severity    severity_ratio    HCR_combined    vs current
  ─────────   ──────────────    ────────────    ──────────
  -20%        1.18              +41.6%          -36.4 pp
  -10%        1.33              +59.6%          -18.0 pp
  Current     1.48              +77.6%          baseline
  +10%        1.63              +95.6%          +18.0 pp
  +20%        1.78              +113.6%         +36.0 pp

  A ±20% shift in severity ratio moves HCR_combined by ~±36 pp.
  The severity ratio contributes SUBSTANTIAL sensitivity.
  
  Compare: a ±20% shift in the 2.5× FREQUENCY scaling moves
  HCR_freq by only ±4 pp (from +16% to +24%).
  
  → Severity is MORE sensitive than frequency scaling for heat wave.
     Getting severity right matters MORE than getting the scaling right.


RIVERINE FLOOD DAILY (HCR_freq = +5.5%, direct counting):

  Severity    severity_ratio    HCR_combined    vs current
  ─────────   ──────────────    ────────────    ──────────
  -20%        0.85              -10.3%          (flips sign!)
  -10%        0.96              +1.3%           -11.2 pp
  Current     1.065             +12.4%          baseline
  +10%        1.17              +23.5%          +11.1 pp
  +20%        1.28              +35.0%          +22.6 pp

  For flood, a -20% severity shift could FLIP THE SIGN of HCR.
  This hazard is particularly sensitive to severity accuracy.
```

---

## Cross-References

| Topic | Doc |
|-------|-----|
| HCR methodology (with severity) | [07_hcr_hazard_change.md](../../learning/C_financial_translation/07_hcr_hazard_change.md) |
| HCR redefined (freq + severity) | [hcr_redefined_freq_severity.md](hcr_redefined_freq_severity.md) |
| Published scaling defensibility | [pathway_defensibility.md](pathway_defensibility.md) |
| SCVR Report Card (tail metrics) | [04_scvr_methodology.md](../../learning/B_scvr_methodology/04_scvr_methodology.md) |
