---
title: "Discussion — Channel 1: How HCR Becomes Dollar Losses"
type: discussion
domain: climate-risk / financial-translation / business-interruption
created: 2026-04-02
status: draft — consolidates BI conversion approaches, pending team decision on baseline_BI_pct
context: >
  The HCR-to-dollar conversion is the financial translation for Channel 1.
  Three approaches exist (top-down, bottom-up, benchmarks) but the critical
  input — baseline_BI_pct per hazard — is unknown for our pilot assets.
  This doc consolidates the calculation options, works through each with
  real Hayhurst numbers, and frames the baseline_BI_pct as a decision
  the team needs to make.
relates-to:
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/learning/C_financial_translation/09_nav_impairment_chain.md
  - docs/discussion/hcr_financial/cashflow_integration.md
  - docs/discussion/hcr_financial/hcr_efr_boundary.md
---

# Channel 1: How HCR Becomes Dollar Losses

> **The question:** HCR_heat(2040) = +0.185. How many dollars does the
> asset actually lose?

> **The honest answer:** It depends on baseline_BI_pct — the fraction of
> revenue historically lost to each hazard — which we don't have yet for
> our pilot assets. This doc lays out the options.

---

## 1. The General Formula

All three approaches share the same structure:

```
BI_loss(t) = Σ_hazards [ HCR_h(t) × baseline_BI_h × Revenue(t) ]

Where:
  HCR_h(t)       = hazard change ratio for hazard h in year t (from NB04)
  baseline_BI_h   = baseline fraction of revenue lost to hazard h (THE UNKNOWN)
  Revenue(t)      = annual revenue in year t ($)

This gives: additional BI loss in year t from climate change
            (not total BI — just the EXTRA caused by warming)
```

The formula is simple. The difficulty is `baseline_BI_h`.

---

## 2. Three Approaches to Compute BI_loss

### Approach A: Top-Down (% of Revenue)

```
FORMULA:
  BI_loss_h(t) = Revenue(t) × baseline_BI_pct_h × HCR_h(t)

INPUT NEEDED:
  baseline_BI_pct_h = historical fraction of revenue lost to hazard h
  This is an aggregate number: "what % of revenue does heat cost us?"

EXAMPLE (Hayhurst 2040, SSP5-8.5):
  Revenue(2040)       = $2.17M (after standard degradation)
  baseline_BI_heat    = 1.0% (assumed — see §4)
  HCR_heat(2040)      = 0.185

  BI_loss_heat(2040)  = $2.17M × 0.01 × 0.185 = $4,015/yr

PROS:
  + Simple — one multiplication per hazard
  + Scales naturally with asset size
  + Easy sensitivity analysis (vary %)

CONS:
  - baseline_BI_pct is unknown and hard to validate
  - Lumps all mechanisms (shutdown, derating, partial output) into one %
  - No physical grounding — why 1.0% and not 0.5%?
```

### Approach B: Bottom-Up (Hours x Capacity x Price)

```
FORMULA:
  BI_loss_h(t) = additional_hours_h(t) × capacity_MW × CF_during_event × price

  additional_hours_h(t) = baseline_hours_h × HCR_h(t)

INPUT NEEDED:
  baseline_hours_h = historical annual shutdown/derating hours from hazard h
  CF_during_event  = capacity factor during the period (may be <1 if partial)
  price            = revenue per MWh

EXAMPLE (Hayhurst 2040, SSP5-8.5 — Heat):
  baseline_shutdown_hours = 120 hrs/yr (inverter protection shutdowns)
  HCR_heat(2040) = 0.185
  additional_hours = 120 × 0.185 = 22.2 hrs

  Shutdown BI:
    22.2 hrs × 24.8 MW × 0.85 CF × $40/MWh = $18,710/yr

  PLUS derating BI (panels less efficient when hot):
    baseline_derating_loss = 2.1% of summer generation
    additional_derating = 2.1% × 0.185 = 0.39%
    summer_gen = 30,000 MWh
    derating_BI = 30,000 × 0.0039 × $40 = $4,680/yr

  Total heat BI = $18,710 + $4,680 = $23,390/yr

PROS:
  + Physics-grounded — each component is measurable
  + Separates shutdown from derating (different mechanisms)
  + Validatable against O&M records

CONS:
  - Needs asset-specific baseline data (shutdown hours, derating curves)
  - More complex (multiple sub-calculations per hazard)
  - Baseline hours may not be available for new assets
```

### Approach C: Industry Benchmarks

```
FORMULA:
  Same as Approach A, but baseline_BI_pct comes from published data

INPUT NEEDED:
  Industry-reported BI rates by hazard type and climate zone

PUBLISHED RANGES:
  Solar heat-related BI:     0.5 – 2.0% of annual revenue
  Solar flood BI:            0.2 – 1.0%
  Solar hail BI:             0.1 – 0.5%
  Wind icing BI:             1.0 – 5.0% (cold climate sites)
  Wind turbine fault BI:     2.0 – 4.0% (all causes)

EXAMPLE (Hayhurst 2040, SSP5-8.5):
  Revenue = $2.17M
  
  Heat benchmark:  1.5% (upper range — extreme heat site)
    BI_heat = $2.17M × 0.015 × 0.185 = $6,022/yr

  Flood benchmark: 0.3% (low — arid region)
    BI_flood = $2.17M × 0.003 × 0.020 = $130/yr

  Total BI = $6,152/yr

PROS:
  + Uses real-world data (insurance, industry surveys)
  + Available for new projects (no operating history needed)
  + Provides a reasonable range for sensitivity analysis

CONS:
  - Benchmarks are broad (0.5-2.0% is a 4× range!)
  - Regional variation large (TX desert ≠ Florida coast)
  - May not separate climate-specific BI from all-cause BI
```

---

## 3. Side-by-Side Comparison — Same HCR, Different $

```
ALL THREE APPROACHES — Hayhurst 2040, SSP5-8.5, Heat Hazard

  HCR_heat(2040) = 0.185 (same input for all three)

  Approach A (top-down, 1.0%):      $4,015/yr
  Approach B (bottom-up, 120 hrs):  $23,390/yr
  Approach C (benchmark, 1.5%):     $6,022/yr

  RANGE: $4K to $23K per year
  That's a 6× spread — driven entirely by baseline_BI_pct.

  Over 23-year IUL (NPV at 10%):
  Approach A: ~$35K total
  Approach B: ~$200K total
  Approach C: ~$52K total
```

**Why Approach B is so much higher:** It separately counts shutdown hours
(120 hrs × 22.2 additional) AND derating losses. Approaches A and C lump
them together in one percentage, which may undercount if derating is
significant.

**But Approach B requires data we don't have:** We don't know Hayhurst's
actual baseline shutdown hours or derating curves.

---

## 4. The baseline_BI_pct Problem

This is **the single most critical unknown** in Channel 1. Every approach
needs it (directly or indirectly):

```
WHERE COULD baseline_BI_pct COME FROM?

Source 1: O&M Records (best, but we don't have them)
  InfraSure/asset operator records showing:
    - Hours of heat-related inverter shutdown per year
    - Revenue lost to weather events per year
    - Breakdown by cause (heat, flood, hail, wind)
  STATUS: NOT AVAILABLE for pilot assets

Source 2: Insurance Claims Data (good proxy)
  Insurance databases (IBHS, NFIP) showing:
    - Claim frequency by hazard type for solar/wind in TX
    - Average claim size relative to annual revenue
  STATUS: ACCESSIBLE but broad; not site-specific

Source 3: Industry Surveys (available)
  Published reports (IEA PVPS, BNEF, Wood Mackenzie):
    - Asset-class-level BI rates by region
    - Performance ratio decomposition
  STATUS: AVAILABLE — broad ranges, not site-specific

Source 4: Engineering Estimates (fallback)
  Calculate from physical models:
    - Inverter thermal protection triggers at 65°C module temp
    - Count baseline hours above 65°C from ERA5 weather data
    - Convert to lost generation
  STATUS: COULD BE COMPUTED from existing ERA5 data in project_finance
```

### Recommended Ranges for Phase 1

```
HAYHURST SOLAR (West Texas desert, 24.8 MW)

Hazard          Low     Mid     High    Rationale
──────────      ────    ────    ────    ─────────────────────
Heat (BI)       0.5%    1.0%    2.0%    Extreme heat site but modern inverters
Flood           0.1%    0.3%    0.5%    Arid — minimal baseline flood risk
Wind cutout     0.0%    0.0%    0.1%    15 m/s threshold never exceeded
Icing shutdown  0.0%    0.1%    0.2%    Rare at this latitude
──────────      ────    ────    ────
TOTAL           0.6%    1.4%    2.8%    of annual revenue


MAVERICK WIND (Concho County TX, 491.6 MW)

Hazard          Low     Mid     High    Rationale
──────────      ────    ────    ────    ─────────────────────
Icing shutdown  0.5%    1.5%    3.0%    Historical icing events (30-50 frost days)
Heat (nacelle)  0.1%    0.2%    0.5%    Electronics cooling issues
Flood (access)  0.1%    0.2%    0.3%    Elevated turbines, road access risk
Wind cutout     0.0%    0.0%    0.1%    SCVR_sfcWind ≈ 0
──────────      ────    ────    ────
TOTAL           0.7%    1.9%    3.9%    of annual revenue
```

### Sensitivity: How baseline_BI_pct Changes NAV

```
NAV IMPAIRMENT FROM CHANNEL 1 (BI only, Hayhurst SSP5-8.5)

  baseline_BI_total    Annual BI_loss (2040)    NPV over IUL    % of $60M NAV
  ─────────────────    ────────────────────    ────────────    ────────────
  0.6% (low)           $2,400/yr               ~$20K           0.03%
  1.4% (mid)           $5,600/yr               ~$48K           0.08%
  2.8% (high)          $11,200/yr              ~$96K           0.16%

  For comparison, Channel 2 (EFR/IUL) = ~$5.1M = 8.5% of NAV

  CHANNEL 1 IS 50-250× SMALLER THAN CHANNEL 2 AT THESE ASSUMPTIONS.
  
  Even at the HIGH estimate, BI is < 0.2% of NAV.
  Equipment degradation (Channel 2) dominates overwhelmingly.
```

---

## 5. Calculation Frequency and Timing

```
PHASE 1 (current):
  HCR computed annually (one value per hazard per year)
  BI_loss computed annually
  Applied uniformly across all months of each year

  BI_loss(2040) = $5,600/yr → $467/month (uniform)

PHASE 2 (future — seasonal):
  Heat BI concentrated in June-September (4 months = 80% of heat BI)
  Flood BI concentrated in March-May (spring storms)
  Icing BI concentrated in December-February

  Would require seasonal HCR or seasonal baseline_BI distribution.
  More accurate for quarterly DSCR testing.

DSCR INTEGRATION:
  Annual HCR from LTRisk → project_finance quarterly model
  Apply: BI_loss_annual / 4 to each quarter (Phase 1)
  Or: BI_loss_annual × seasonal_weight_q (Phase 2)
```

---

## 6. Multi-Hazard Aggregation

```
PHASE 1 (additive, conservative):
  BI_loss(t) = BI_heat(t) + BI_flood(t) + BI_wind(t) + BI_icing(t)

  Assumes hazards are independent.
  Correct when events don't overlap in time.
  Conservative (underestimates) when they DO overlap:
    e.g., heat wave + drought simultaneously.

PHASE 2 (compound interactions):
  BI_loss(t) = BI_heat(t) + BI_flood(t) + BI_compound_heat_drought(t) + ...

  Compound terms capture:
    Heat + drought → both reduce generation AND soiling worsens
    Flood + wind → structural + BI compounding
    
  These interactions are non-linear and require event co-occurrence data.
```

---

## 7. Recommendation for Phase 1

```
1. USE APPROACH A (top-down) with MID baseline_BI_pct estimates:
     Heat: 1.0%, Flood: 0.3%, Total: ~1.4%

2. REPORT SENSITIVITY RANGE:
     LOW (0.6%) to HIGH (2.8%) in all outputs
     Flag that Channel 1 is small relative to Channel 2

3. CROSS-CHECK against Approach C (benchmarks):
     If our Approach A estimate falls within published ranges, confidence is high
     If outside, investigate why

4. DEFER Approach B to Phase 2:
     Requires O&M data we don't have
     When data becomes available, switch to bottom-up (most accurate)

5. DOCUMENT that Channel 1 < Channel 2 by ~50-250×:
     This is a finding, not a limitation
     The asset's climate risk is dominated by equipment degradation, not BI
```

---

## 8. The Complete Chain — ASCII Flow

```
HCR PER HAZARD (from NB04)                    BASELINE BI (the unknown)
┌────────────────────────┐                     ┌──────────────────────┐
│ HCR_heat(2040) = 0.185 │                     │ baseline_BI_heat     │
│ HCR_flood(2040)= 0.020 │                     │ = 1.0% of revenue   │
│ HCR_wind(2040) = 0.000 │                     │ baseline_BI_flood    │
│ HCR_icing(2040)= -0.04 │                     │ = 0.3% of revenue   │
└───────────┬────────────┘                     └──────────┬───────────┘
            │                                              │
            └──────────────┬───────────────────────────────┘
                           │
                           ▼ multiply per hazard
            ┌──────────────────────────────────┐
            │ BI_heat  = $2.17M × 1.0% × 0.185│
            │         = $4,015/yr               │
            │ BI_flood = $2.17M × 0.3% × 0.020│
            │         = $130/yr                 │
            │ BI_wind  = $0/yr (HCR = 0)       │
            │ BI_icing = $0/yr (negative = ben) │
            └───────────┬──────────────────────┘
                        │
                        ▼ sum all hazards
            ┌──────────────────────────────────┐
            │ BI_loss(2040) = $4,145/yr        │
            └───────────┬──────────────────────┘
                        │
                        ▼ subtract from CFADS
            ┌──────────────────────────────────┐
            │ CFADS(2040) = Revenue × (1-EFR)  │
            │             - BI_loss             │
            │             - OpEx               │
            │            = $2.02M × 0.993      │
            │             - $4,145    ← Ch. 1  │
            │             - $704K              │
            │            = $1.30M              │
            └──────────────────────────────────┘

  Channel 1 contribution at year 2040: ~$4K/yr
  Channel 2 contribution at year 2040: ~$41K/yr (from EFR)
  Channel 2 dominates by ~10×
```

---

## Cross-References

| Topic | Doc |
|-------|-----|
| HCR computation | [07_hcr_hazard_change.md](../../learning/C_financial_translation/07_hcr_hazard_change.md) |
| NAV impairment chain | [09_nav_impairment_chain.md](../../learning/C_financial_translation/09_nav_impairment_chain.md) |
| Cashflow integration | [cashflow_integration.md](cashflow_integration.md) |
| HCR/EFR boundary | [hcr_efr_boundary.md](hcr_efr_boundary.md) |
| Channel 2 financial | [channel_2_efr_financial.md](../efr_degradation/channel_2_efr_financial.md) |
