---
title: "Discussion — From HCR to CIR: Capturing Both Frequency and Severity"
type: discussion
domain: climate-risk / methodology / first-principles
created: 2026-04-09
status: draft — foundational rethink, pending team decision
context: >
  HCR (Hazard Change Ratio) only captures FREQUENCY change — how many more
  events cross a threshold. But climate change also changes SEVERITY — each
  event may be more intense. For some hazards (hurricane, hail, wildfire),
  severity change dominates frequency change, making frequency-only metrics
  misleading. This doc proposes evolving toward a Climate Impact Ratio (CIR)
  that captures both, grounded in how the insurance industry actually
  quantifies climate-adjusted risk.
relates-to:
  - docs/discussion/hcr_financial/hcr_top_down_reframe.md
  - docs/discussion/hcr_financial/pathway_defensibility.md
  - docs/discussion/architecture/pipeline_complementarity.md
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
---

# From HCR to CIR: Capturing Both Frequency and Severity

> **The problem:** HCR counts how many more events cross a threshold.
> It misses that each event may also be MORE INTENSE. For hurricane,
> a frequency-only metric says "7.5% fewer storms" when actual damage
> INCREASES 7-43% because storms are fiercer.

> **The proposal:** Evolve from HCR (frequency-only) toward CIR
> (Climate Impact Ratio) — the ratio of future-to-baseline expected
> annual damage. This naturally captures both frequency and severity.

---

## 1. The Gap: What HCR Misses

### What Climate Change Does to Annual Loss

```
Annual_loss = how_often × how_bad_each_time
            = frequency × severity_per_event

Climate change can:
  1. Change FREQUENCY (more/fewer events)        ← HCR captures this
  2. Change SEVERITY (each event more/less bad)   ← HCR misses this
  3. Change BOTH simultaneously
  4. Change them in OPPOSITE directions           ← HCR gets this WRONG
```

### Where Frequency-Only Fails

```
HAZARD          HCR SAYS           ACTUAL DAMAGE IMPACT
──────────────  ──────────────     ─────────────────────
Hurricane       -7.5% (fewer)      +7% to +43% (fiercer storms,
                                    damage scales as wind^3 to wind^9)

Hail            -25% (fewer small)  LIKELY INCREASING (fewer small stones
                                    but +15-75% more large ones, which
                                    cause disproportionate damage)

Wildfire        ~flat (count)       UP TO 6× (area burned per fire
                                    increasing dramatically)

Heat Wave       +150% (more)        +200-300% (events also HOTTER
                                    and LONGER — cumulative heat doubles)
```

**For 4 of 10 canonical hazards, HCR tells the wrong financial story.**

---

## 2. How the Insurance Industry Handles This

### They Don't Separate Frequency and Severity

The CAT modeling industry (Verisk, RMS, Munich Re) computes
**climate-adjusted Expected Annual Loss (AAL)** from the full future
loss distribution — not "frequency × average severity."

```
AAL_future = ∫ loss × f_future(loss) d(loss)

The ratio AAL_future / AAL_baseline automatically captures BOTH
frequency and severity changes because it integrates over the
entire loss distribution.
```

This is the methodological template we should follow.

### The Damage Convolution

The fundamental risk equation:

```
Expected Annual Damage = ∫ P(intensity) × D(intensity) d(intensity)

Where:
  P(intensity) = probability density of hazard intensity
  D(intensity) = damage function (intensity → loss)

When climate shifts P(intensity):
  - More values exceed a threshold (frequency ↑)
  - Values that exceed are further above (severity ↑)
  - D(intensity) amplifies the severity change nonlinearly
```

### Why Damage Function Shape Matters

```
HURRICANE WIND DAMAGE:
  D(V) ∝ V^n, where n = 3 to 9

  If V increases 5%:
    n=3 (engineering cube law):   damage increases 15.8%
    n=9 (empirical, Mendelsohn): damage increases 55%

  This is why "5% more wind" doesn't mean "5% more damage."
  The damage function AMPLIFIES the severity change.
  A frequency-only metric misses this entirely.
```

---

## 3. The Proposal: Climate Impact Ratio (CIR)

### Definition

```
CIR(hazard, t) = E[annual_damage(hazard, t)] / E[annual_damage(hazard, baseline)]

Where:
  annual_damage(hazard, t) = Σ_days D(intensity(day))
  D(intensity) = damage function mapping hazard intensity to loss

  CIR > 1.0: climate change INCREASES expected damage
  CIR < 1.0: climate change DECREASES expected damage
  CIR = 1.0: no change
```

### CIR Decomposes Cleanly

```
CIR = frequency_ratio × severity_ratio

Where:
  frequency_ratio = N_future_events / N_baseline_events = (1 + HCR)
  severity_ratio  = E[D | event, future] / E[D | event, baseline]

This decomposition is exact. You can report both components
for transparency while using CIR as the primary metric.
```

### CIR vs HCR Comparison

```
              HCR                         CIR
              ─────────────               ─────────────
Measures:     Threshold crossing count    Expected damage ratio
Captures:     Frequency only              Frequency + severity
Requires:     Threshold definition        Threshold + damage function
Nonlinear     
damage:       NO (step function)          YES (arbitrary D(intensity))
Hurricane:    -7.5% (wrong story)         +7% to +43% (correct)
Hail:         -25% (wrong story)          Likely positive (correct)
Wildfire:     ~0% (wrong story)           +100-600% (correct)
Heat wave:    +20% (understates)          +30-50% (better estimate)
```

---

## 4. What This Means for Each Canonical Hazard

### Heat Wave — CIR > HCR

```
HCR says:  +20% (more events)
CIR adds:  Each event is HOTTER and LONGER
  - Peak temperature: +1:1 with mean warming
  - Duration: increases super-linearly (1.5-2× rate of frequency)
  - Cumulative heat: roughly doubles
  
For solar BI:
  D(tasmax) = derating_curve(tasmax) × hours_above_threshold
  A hotter heat wave causes MORE derating for MORE hours
  CIR ≈ 1.3-1.5 (vs HCR ≈ 1.2)

Published: Kirchengast et al. 2026 — 10× increase in heat "extremity"
  (a combined intensity-duration metric, not just frequency)
```

### Hurricane — CIR ≠ HCR direction

```
HCR says:  -7.5% (fewer storms — financial IMPROVEMENT?)
CIR says:  +7% to +43% (fiercer storms — financial WORSENING)

The damage function flips the story:
  D(V) ∝ V^3 to V^9
  Fewer storms × (much higher damage per storm) = more total damage

Published: Mendelsohn et al. 2012 — climate change roughly DOUBLES
  global TC damage despite frequency decrease
Published: Knutson et al. 2020 — wind +5%, rain +14%, Cat4-5 +13%
```

### Hail — CIR captures the dichotomy

```
HCR says:  -25% (fewer events — financial IMPROVEMENT?)
CIR says:  LIKELY POSITIVE (larger stones cause disproportionate damage)

The "hailstone size dichotomy" (npj CAS 2024):
  Small stones (<4cm): -25% frequency
  Large stones (>4cm): +15-75% frequency
  
Since D(hail_diameter) is highly nonlinear (a 5cm stone shatters
a panel that a 3cm stone merely dents), the increase in large stones
more than compensates for the decrease in small stones.

Published: Raupach et al. 2021 — severity increase in North America
```

### Wildfire — CIR >> HCR

```
HCR says:  ~0% (fire COUNT flat)
CIR says:  +100-600% (area burned per fire dramatically increases)

"The amount of land burned each year has increased as wildfires have
grown larger, while the number of fires each year has remained fairly
constant." — NOAA

Abatzoglou & Williams 2016: anthropogenic warming nearly DOUBLED
western US forest fire area 1984-2015.

For infrastructure: a fire that burns 100 acres vs 10,000 acres
has radically different financial impact, even if both are "one fire."
```

### Riverine Flood — CIR amplifies HCR

```
HCR says:  +2.6% (based on Rx5day counting)
CIR adds:  Each flood event is MORE intense (super-Clausius-Clapeyron)
  - Extreme rainfall: +7-14%/°C
  - Flood damage: nonlinear in depth (USACE depth-damage curves)
  - A 10% increase in rainfall depth can mean 30%+ increase in damage

CIR ≈ 1.1-1.3 (vs HCR ≈ 1.03)
```

### Ice Storm — CIR ≈ HCR (decreasing)

```
HCR says:  -44.5% (fewer icing events)
CIR says:  ~-40-50% (severity per event unclear, but frequency dominates)

This is a case where frequency-only is probably adequate — 
the financial story is "fewer icing events = benefit."
```

---

## 5. Implementation Path

### Phase 1 — Minimal Change, Maximum Insight

**Add two severity diagnostics alongside existing HCR.** Zero architecture
change. Same Pathway B loop, just compute two extra numbers:

```
For each hazard, in addition to counting threshold exceedances:

  1. MEAN EXCESS ABOVE THRESHOLD
     E[X - T | X > T] for baseline vs future
     = "how far above the threshold are events, on average?"
     = the severity component

  2. EXPECTED EXCESS
     E[max(0, X - T)] for baseline vs future
     = frequency × mean_excess
     = combined frequency + severity metric
     = CIR with a LINEAR damage function above threshold

These require ZERO additional data — computed from the same
daily values already being processed in Pathway B.
```

**What this gives us:** For heat wave, instead of just "+20% more events,"
we can say "+20% more events AND each event exceeds the threshold by 15%
more on average, giving +38% expected excess above threshold."

### Phase 2 — CIR with Damage Functions

```
For each canonical hazard, define D(intensity):
  Heat wave:   D(tasmax) = derating_loss_curve(tasmax)
  Flood:       D(precip) = depth_damage_curve(precip)
  Wind:        D(sfcWind) = wind_damage_cube_law(sfcWind)
  Wildfire:    D(FWI) = P(fire|FWI) × E[damage|fire]
  Hurricane:   D(V) = V^3 × exposure (from Knutson/Mendelsohn)

Compute CIR from daily data:
  CIR = mean(Σ_days D(intensity_future)) / mean(Σ_days D(intensity_baseline))
```

### Phase 3 — Full Integration

```
Replace HCR in the financial model:
  BEFORE: BI_loss = HCR × baseline_BI_pct × Revenue
  AFTER:  BI_loss = (CIR - 1) × baseline_EAL

Where baseline_EAL comes from the hazards repo.
This ALSO resolves the baseline_BI_pct calibration problem —
the damage function replaces the empirical percentage.
```

---

## 6. Naming

The insurance industry uses several terms:

```
OPTION                      USED BY                    NOTES
──────────────────────      ─────────────              ──────
Climate Adjustment Factor   Verisk, RMS                Industry standard
Climate Change Factor       CAT modeling literature    Same concept
Climate Expected Loss       Munich Re                  Product name
Climate Impact Ratio        Proposed (this doc)        More intuitive

RECOMMENDATION:
  Use "Climate Adjustment Factor (CAF)" externally (industry recognises it)
  Use "CIR" internally (more descriptive of what we compute)
  The math is the same: future_EAL / baseline_EAL
```

---

## 7. What This Means for the Top-Down Reframe

The top-down reframe (hcr_top_down_reframe.md) asked: "for each canonical
hazard, what can LTRisk say about future frequency?" The CIR evolution
makes this better: "for each canonical hazard, what can LTRisk say about
future expected damage?"

```
UPDATED SUMMARY:

HAZARD          FREQ CHANGE   SEVERITY CHANGE    CIR ESTIMATE   CONFIDENCE
Heat Wave       ↑↑ +150%      ↑ hotter, longer   1.3-1.5×       HIGH
Wildfire        → flat        ↑↑ area 2-6×       2.0-7.0×       MOD-HIGH
Riverine Flood  ↑ +7%/°C      ↑ intensity +7-14% 1.1-1.3×       MODERATE
Hurricane       ↓ -7.5%       ↑↑ wind^3 to wind^9 1.1-1.4×      MODERATE
Hail            ↓ -25%(small) ↑ large stones      1.0-1.5×?      LOW
Ice Storm       ↓↓ -40-50%    ? unclear            0.5-0.6×       MODERATE
Winter Weather  ↓ decreasing  ? may intensify      0.5-0.8×       LOW-MOD
Coastal Flood   ↑↑↑ exponential ↑ SLR compound    10-1000×       HIGH
Strong Wind     → flat        → flat               1.0×           MOD
Tornado         ? uncertain   ? may increase        ?              LOW
```

---

## 8. Open Questions

1. **Damage functions:** Where do they come from? The hazards repo already
   has some (Thirza for hail, HAZUS for flood, Unanwa for wind). Can we
   reuse those? They were designed for physical damage, not BI — is that
   the right D(intensity) for our purpose?

2. **Phase 1 vs Phase 2 priority:** Phase 1 (mean excess above threshold)
   requires zero code changes but gives a crude severity estimate. Phase 2
   (full CIR with damage functions) is more accurate but needs D(intensity)
   per hazard. Which first?

3. **How does CIR connect to the hazards repo's EAL?** If the hazards repo
   computes baseline_EAL and LTRisk computes CIR, then
   `future_EAL = baseline_EAL × CIR`. This is the pipeline complementarity
   we've been trying to achieve. Does it work cleanly?

4. **EFR vs CIR boundary:** CIR captures BI-related damage changes. EFR
   captures degradation-related damage. Do they overlap? For heat wave:
   CIR captures the shutdown/derating BI, EFR (Peck's) captures the
   long-term aging. They're still separate mechanisms.

5. **Naming convention:** Use CIR internally and CAF externally? Or just
   pick one? The hazards team may prefer "Climate Adjustment Factor" since
   it's industry standard.

---

## Key References

| Paper | Finding | DOI |
|-------|---------|-----|
| Mendelsohn et al. 2012 | TC damage scales V^9; climate doubles damage | [doi:10.1038/nclimate1357](https://doi.org/10.1038/nclimate1357) |
| Prahl et al. 2016 | Damage function framework for climate hazards | [doi:10.5194/nhess-16-1189-2016](https://doi.org/10.5194/nhess-16-1189-2016) |
| WTW 2023 | Freq-severity adjustments underestimate tail risk | [wtwco.com](https://www.wtwco.com/en-us/insights/2023/06/why-relying-on-frequency-severity-adjustments-could-underestimate-your-tail-risk-from-climate-change) |
| Swiss Re sigma 2025 | NatCat losses: both frequency AND severity rising | [swissre.com](https://www.swissre.com/institute/research/sigma-research/sigma-2025-01-natural-catastrophes-trend.html) |
| Knutson et al. 2020 | Hurricane: fewer but fiercer consensus | [doi:10.1175/BAMS-D-18-0194.1](https://doi.org/10.1175/BAMS-D-18-0194.1) |
| npj CAS 2024 | Hailstone size dichotomy | [doi:10.1038/s41612-024-00728-9](https://doi.org/10.1038/s41612-024-00728-9) |
| Abatzoglou & Williams 2016 | Wildfire area doubled under warming | [doi:10.1073/pnas.1607171113](https://doi.org/10.1073/pnas.1607171113) |
| Hsiang et al. 2017 | US climate damage functions by sector | [doi:10.1126/science.aal4369](https://doi.org/10.1126/science.aal4369) |
| Kirchengast et al. 2026 | 10× heat extremity (intensity × duration) | [doi:10.1016/j.wace.2026.100855](https://doi.org/10.1016/j.wace.2026.100855) |
| Nature Geoscience 2025 | Super-Clausius-Clapeyron for extreme precip | [doi:10.1038/s41561-025-01686-4](https://doi.org/10.1038/s41561-025-01686-4) |

## Cross-References

| Topic | Doc |
|-------|-----|
| Top-down canonical hazard reframe | [hcr_top_down_reframe.md](hcr_top_down_reframe.md) |
| Pipeline complementarity | [pipeline_complementarity.md](../architecture/pipeline_complementarity.md) |
| Published scaling defensibility | [pathway_defensibility.md](pathway_defensibility.md) |
| BI methodology foundations | [01_what_is_bi.md](../bi_methodology/01_what_is_bi.md) |
| HCR methodology (current) | [07_hcr_hazard_change.md](../../learning/C_financial_translation/07_hcr_hazard_change.md) |
