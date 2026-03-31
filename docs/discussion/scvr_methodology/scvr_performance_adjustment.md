---
title: "Discussion — Can SCVR Inform Performance Adjustment?"
type: discussion
domain: climate-risk / performance-modeling
created: 2026-03-06
status: draft
context: >
  This is a working discussion document evaluating whether SCVR outputs
  can meaningfully adjust year-over-year asset performance projections,
  or whether SCVR's primary value lies in degradation (EFR) and hazard
  (HCR) channels. Prompted by reviewing actual ensemble SCVR results
  for Hayhurst Solar and Maverick Creek Wind, which show near-zero
  signal on the primary generation-driving variables (rsds, sfcWind).
relates-to:
  - 01_what_is_scvr.md
  - 03_solar_use_case.md
  - 04_wind_use_case.md
  - LT_Risk_Evolution_Framework.md
  - discussion_scaling_1yr_to_multiyear.md
---

# Discussion — Can SCVR Inform Performance Adjustment?

> **The central question:** SCVR measures distributional shift in climate
> variables. Can that shift meaningfully adjust generation performance
> projections year-over-year? Or is SCVR's real value limited to
> degradation and hazard channels?

> **Short answer:** The data says SCVR is primarily a degradation and
> hazard tool, not a performance adjustment tool. The variables that
> drive generation (GHI, wind speed) show near-zero SCVR. The variables
> that show meaningful SCVR (temperature, humidity) primarily affect
> equipment aging and hazard frequency, not direct power output.

---

## 1. What the Data Actually Shows

From the multi-model ensemble SCVR results (6 CMIP6 models, pooled)
for Hayhurst Texas Solar:

```
SCVR RESULTS — HAYHURST TEXAS SOLAR (ENSEMBLE)

  Variable     Name              SSP2-4.5    SSP5-8.5    Rating
  ──────────   ────────────────  ──────────  ──────────  ────────
  tasmin       Daily Min Temp    +0.1435     +0.1634     Moderate
  tas          Daily Mean Temp   +0.0854     +0.0991     Low
  tasmax       Daily Max Temp    +0.0734     +0.0832     Low
  pr           Precipitation     +0.0478     +0.0233     Low
  hurs         Humidity          −0.0327     −0.0424     Low
  sfcWind      Wind Speed        −0.0149     −0.0110     Low
  rsds         Solar Radiation   +0.0022     +0.0005     Low
```

Now separate these into what drives generation vs what drives degradation:

```
PRIMARY GENERATION DRIVERS:
───────────────────────────
  rsds (solar irradiance)  →  SCVR: +0.0005 to +0.0022
  sfcWind (wind speed)     →  SCVR: −0.0110 to −0.0149

  Both are ESSENTIALLY ZERO.
  The resource itself is not changing in any meaningful way.


DEGRADATION / HAZARD DRIVERS:
─────────────────────────────
  tasmin (night temperature) →  SCVR: +0.1435 to +0.1634  ← REAL SIGNAL
  tasmax (day temperature)   →  SCVR: +0.0734 to +0.0832  ← Modest signal
  tas (mean temperature)     →  SCVR: +0.0854 to +0.0991  ← Modest signal
  hurs (humidity)            →  SCVR: −0.0327 to −0.0424  ← Small signal
  pr (precipitation)         →  SCVR: +0.0233 to +0.0478  ← Small signal

  Temperature variables show real shifts.
  But temperature primarily affects:
    → Peck's aging (EFR — equipment life)
    → Coffin-Manson fatigue (EFR — thermal cycling)
    → Hazard frequency (HCR — heat waves, icing)
  NOT direct power output hour-to-hour.
```

This is the fundamental finding: **the climate is changing in ways that
break equipment faster and trigger hazards more often, but the resource
that generates the electricity is essentially stable.**

---

## 2. The Honest Assessment — Where SCVR Has Real Value

```
SCVR VALUE MAP — WHERE THE SIGNAL ACTUALLY LIVES

                           SCVR Signal Strength
                    None/Tiny        Small         Moderate
                    (< 0.01)       (0.01–0.05)    (> 0.05)
                    ─────────      ───────────    ──────────
                         │              │              │
  Channel 1:             │              │              │
  Hazard (HCR)           │         pr (+0.02–0.05)    │
  Flood, hail,           │         hurs (−0.03–0.04)  │
  wildfire, icing        │              │              │
                         │              │              │
  Channel 2:             │              │         tasmin (+0.14–0.16)
  Degradation (EFR)      │              │         tas (+0.09–0.10)
  Peck's, Coffin-        │              │         tasmax (+0.07–0.08)
  Manson, Palmgren-      │              │              │
  Miner                  │              │              │
                         │              │              │
  Channel 3:        rsds (+0.00–0.00)   │              │
  Performance       sfcWind (−0.01)     │              │
  (direct gen)           │              │              │
                         │              │              │
                    ─────────      ───────────    ──────────
                    NO VALUE       SOME VALUE     HIGH VALUE
                    for perf       for hazard     for degrad.

  The strongest SCVR signals (temperature) map to degradation.
  The performance-relevant variables (rsds, sfcWind) have no signal.
  This is not a modeling failure — it is a physical finding.
```

### 2.1 Why This Makes Physical Sense

Solar irradiance and wind speed are driven by large-scale atmospheric circulation
patterns, orbital geometry, and aerosol loading — processes that change very slowly
or not at all under the emission scenarios we're considering over a 30-year horizon.

Temperature, on the other hand, responds directly and monotonically to greenhouse
gas concentrations. The physics is straightforward: more CO₂ → more trapped
longwave radiation → higher surface temperatures. This is why temperature SCVR
is the dominant signal across virtually all sites and scenarios.

```
WHAT CLIMATE CHANGE DOES vs DOESN'T DO (simplified)

  Changes significantly (30-year horizon):
    ✓ Surface temperature (direct greenhouse effect)
    ✓ Precipitation intensity (warmer air holds more moisture)
    ✓ Humidity patterns (regional drying/wetting)
    ✓ Extreme event frequency (driven by temperature thresholds)

  Changes very little (30-year horizon):
    ✗ Total solar irradiance at surface (cloud changes uncertain, small)
    ✗ Mean wind speed distributions (circulation changes are weak signal)
    ✗ Diurnal/seasonal cycles (driven by orbital mechanics, unchanged)

  This is why SCVR finds:
    Temperature variables: real, meaningful shifts
    Generation drivers (rsds, sfcWind): essentially flat
```

### 2.2 What This Means for the Three-Channel Framework

The LT Risk Evolution Framework defines NAV impairment through three channels.
SCVR's contribution is concentrated in Channels 1 and 2:

| Channel | What it captures | SCVR variables involved | Signal strength |
|---|---|---|---|
| **1. HCR** (hazard frequency) | More floods, hail, wildfire, icing events | pr, hurs, tas, tasmax | Small to moderate |
| **2. EFR** (equipment life) | Accelerated aging, fatigue, material degradation | tasmin, tas, tasmax, hurs | **Moderate to high** |
| **3. Performance** (generation output) | Direct change in MWh produced per hour | rsds, sfcWind | **Near zero** |

**Channel 3 is where SCVR has the least to offer.** This is an honest finding,
not a limitation of the methodology. The climate variables that drive generation
are simply not shifting enough to warrant a year-over-year performance adjustment
based on SCVR data alone.

---

## 3. The Secondary Temperature Effect — Real but Small

There IS a legitimate second-order pathway from temperature SCVR to generation
performance. It's worth understanding, documenting, and then putting in
proper perspective.

### 3.1 Solar Thermal Derating

PVLib's temperature coefficient model:

```
P_actual = P_rated × [1 + γ × (T_cell − 25°C)]

where γ ≈ −0.004 /°C (crystalline silicon)
```

Temperature is rising (tasmax SCVR: +0.0832 under SSP5-8.5). This means more
hours above 25°C and higher cell temperatures during those hours. Panels produce
slightly less power when hotter.

**But how much less?**

```
THERMAL DERATING ESTIMATE — HAYHURST SOLAR

  tasmax SCVR: +0.0832 (SSP5-8.5)

  This corresponds to a mean shift in the tasmax distribution
  of roughly +1.5 to +2.5°C (converting SCVR area change to °C
  is site-dependent; this is the Hayhurst estimate).

  Additional derating during peak production hours:
    Extra °C × γ × fraction of hours affected
    ≈ 2.0°C × 0.004 × 0.35 (35% of annual hours are >25°C)
    ≈ 0.28% annual generation reduction

  At Hayhurst (24.8 MW, ~25% CF):
    Annual gen: ~54,200 MWh
    Loss: ~152 MWh/yr
    At $40/MWh: ~$6,100/yr

  Compare this to the EFR impact (Peck's aging shortening
  useful life by ~3 years):
    Lost revenue from 3 fewer years of operation
    ≈ 3 × 54,200 MWh × $40/MWh = ~$6.5M

  The thermal derating is ~$6K/yr.
  The EFR life-shortening is ~$6.5M total.

  RATIO: The degradation impact is roughly 30-50x larger
  than the performance impact, depending on discount rate.
```

### 3.2 Wind Air Density

Warmer air is less dense. Wind power is proportional to air density (P ∝ ρ × v³).

```
AIR DENSITY ESTIMATE — MAVERICK WIND

  tas SCVR: +0.0991 (SSP5-8.5)
  Estimated mean warming: ~1.5°C

  Air density change: Δρ/ρ ≈ −ΔT/T_kelvin
    = −1.5 / 291 = −0.52%

  Generation impact: −0.52% (approximately linear)

  At Maverick (491.6 MW, ~35% CF):
    Annual gen: ~1,507,000 MWh
    Loss: ~7,800 MWh/yr
    At $35/MWh: ~$273,000/yr

  This is a real number — $273K/yr is not trivial for a
  single asset. But it's also within the noise band of
  normal inter-annual weather variability (σ ≈ 6-10% for wind).

  And the offsetting icing reduction (fewer shutdown days)
  recovers roughly +0.5%, nearly canceling the density loss.
```

### 3.3 Putting Secondary Effects in Context

| Asset | Performance Δ from SCVR | Annual $ impact | EFR/HCR $ impact | Ratio |
|---|---|---|---|---|
| Hayhurst Solar | −0.28% (thermal derating) | −$6K/yr | −$6.5M (life shortening) | ~1:50 |
| Hayhurst Solar | +0.05% (rsds, negligible) | +$1K/yr | — | — |
| Maverick Wind | −0.52% (air density) | −$273K/yr | −$1.5M (minor EFR) | ~1:5 |
| Maverick Wind | +0.55% (icing reduction) | +$290K/yr | — | — |

For solar: the performance effect is negligible compared to degradation.
For wind: the performance effects approximately cancel each other, and the
net is near-zero.

**This is why a year-over-year performance adjustment from SCVR is not
well-justified by the data.** The signal is either too small (solar thermal
derating), too uncertain (wind icing model), or self-canceling (wind density
vs icing).

---

## 4. What SCVR CANNOT Tell Us About Performance

The multi-year scaling document (discussion_scaling_1yr_to_multiyear.md)
identifies several factors that drive year-over-year generation variability.
Most of these are NOT captured by SCVR:

```
PERFORMANCE VARIABILITY DRIVERS — WHAT SCVR SEES vs DOESN'T

  Driver                           SCVR signal?    Notes
  ──────────────────────────────   ────────────    ──────────────────
  Inter-annual weather variability NO              SCVR measures the
  (the ±6-10% year-to-year                        SHIFT in distribution,
  bounce in wind/solar resource)                   not the VARIABILITY
                                                   within a period

  Climate regime persistence       NO              SCVR doesn't capture
  (ENSO, AMO, PDO cycles that                     serial correlation
  create multi-year clusters)                      (see HMM in scaling doc)

  Capture price dynamics           NO              SCVR is about climate
  (when you generate vs when                      variables, not market
  prices are high/low)                            structure

  Curtailment trends               NO              Grid-driven, not
  (increasing renewable penetration                climate-driven
  → more negative pricing)

  Equipment degradation spec       PARTIALLY       EFR captures climate-
  (panels/turbines losing                         accelerated aging,
  efficiency over time)                           but not baseline spec

  Extreme weather events           PARTIALLY       HCR captures frequency
  (wildfire smoke, ice storms,                    change, but the
  hail damage)                                    EVENT OCCURRENCE is
                                                   stochastic per path

  Mean resource shift              BARELY          rsds: +0.0005
  (is there more/less sun or                      sfcWind: −0.011
  wind on average?)                               Both negligible
```

The multi-year scaling document already has a comprehensive framework for
handling the performance variability that matters most — and SCVR is not
the tool for most of it:

| Performance challenge | Right tool | SCVR role |
|---|---|---|
| Year-to-year generation bounce | Bootstrap from 40yr ERA5 | None |
| Multi-year bad regimes | HMM regime sampler (Stage 3) | None |
| Capture price / shape risk | Hourly block sampling (Stage 2) | None |
| Tail events (P95-P99) | EVT fitting (Stage 4) | None |
| Climate-driven resource drift | CMIP delta / quantile mapping | **Marginal** |
| Equipment life shortening | EFR from SCVR | **Primary** |
| Hazard frequency increase | HCR from SCVR | **Primary** |

---

## 5. So What IS the Right Way to Adjust Performance Over Project Life?

The multi-year scaling document already answers this question through its
staged approach. Here's where each stage gets its performance adjustment
from — and where SCVR fits (and doesn't):

### 5.1 Stages 1-2: Bootstrap Is Sufficient

For years 1-20 of a project life under Stages 1 and 2 of the multi-year
extension, the performance distribution comes from resampling 40+ years
of ERA5 weather through PVLib/PyWake. This already captures:

- Full inter-annual variability (P10-P90)
- Seasonal structure within each year
- Weather-price correlation (via block sampling)
- Non-normal distribution shape (empirical, not fitted)

No SCVR adjustment is needed for the body of the distribution. The resource
(rsds, sfcWind) isn't changing, so the historical distribution IS the
future distribution for generation purposes.

```
STAGES 1-2: PERFORMANCE FROM BOOTSTRAP (NO SCVR NEEDED)

  Year 1                Year 5                Year 15
  ┌────────────┐        ┌────────────┐        ┌────────────┐
  │ Bootstrap   │        │ Bootstrap   │        │ Bootstrap   │
  │ 40yr ERA5   │        │ 40yr ERA5   │        │ 40yr ERA5   │
  │ × PVLib     │        │ × PVLib     │        │ × PVLib     │
  │             │        │             │        │             │
  │ P10──P50──P90        │ P10──P50──P90        │ P10──P50──P90
  └──────┬─────┘        └──────┬─────┘        └──────┬─────┘
         │                     │                     │
         ▼                     ▼                     ▼
  Gen × (1−degrad)⁰    Gen × (1−degrad)⁴    Gen × (1−degrad)¹⁴
  × Price(yr1)          × Price(yr5)          × Price(yr15)

  The distribution shape is the SAME every year.
  Only degradation (from spec + EFR) and price change.
  No SCVR performance adjustment needed or justified.
```

### 5.2 Stage 3: Regime-Aware — Still No SCVR Performance Adjustment

Stage 3 adds the HMM regime sampler for serial correlation. This changes
WHICH years are sampled (consecutive bad years cluster together) but
doesn't change the underlying generation distribution. The resource
is still drawn from ERA5 history.

SCVR contributes here through HCR (regime affects hazard frequency) and
EFR (climate-conditioned degradation rate), but NOT through direct
performance adjustment.

### 5.3 Stage 4: Climate-Adjusted — Where SCVR Could Contribute (Marginally)

Stage 4 is the only stage where a SCVR-driven performance adjustment is
even conceptually justified. Here, you're projecting 20-30 years out and
asking: "Is the resource itself different?"

The answer from the data: **barely.**

```
STAGE 4: THE HONEST CLIMATE PERFORMANCE ADJUSTMENT

  What the data supports:
  ──────────────────────
  rsds SCVR: +0.0005 to +0.0022  →  +0.05% to +0.22% generation change
  sfcWind SCVR: −0.011 to −0.015 →  negligible (flat part of power curve)

  What temperature adds (second-order):
  ──────────────────────────────────────
  Solar thermal derating: ~−0.3% by 2050
  Wind air density loss:  ~−0.5% by 2050
  Wind icing reduction:   ~+0.5% by 2050

  NET PERFORMANCE ADJUSTMENT (if you compute it):
    Solar: approximately −0.2% to +0.0% (within noise)
    Wind:  approximately −0.1% to +0.1% (self-canceling)

  Compare to:
    Inter-annual variability: ±3-10% (σ_annual)
    EFR life shortening:      −10 to −15% of total NPV (solar)
    HCR BI losses:            −2 to −5% of total NPV

  THE PERFORMANCE ADJUSTMENT IS LOST IN THE NOISE.
```

### 5.4 The Recommended Approach

Given the data, here's what we should actually do:

```
RECOMMENDATION BY CHANNEL

  Channel 1 — HCR (hazard frequency):
  ✅ USE SCVR. Real signal in pr, hurs, temperature.
     This is well-designed and the framework handles it.

  Channel 2 — EFR (equipment degradation):
  ✅ USE SCVR. Strong signal in tasmin, tas, tasmax.
     Peck's aging, Coffin-Manson — this is where SCVR
     delivers its highest value.

  Channel 3 — Performance (direct generation):
  ⚠️  DOCUMENT THE FINDING, DON'T FORCE AN ADJUSTMENT.

     The honest approach:
     1. Note that rsds and sfcWind SCVR are near-zero
     2. Note that this means the resource is stable
     3. Acknowledge the second-order temperature effects
        (thermal derating, air density) as real but small
     4. Do NOT apply a year-over-year performance scalar
        from SCVR — it's not justified by the signal strength
     5. Let the bootstrap handle performance variability
        (it already does this well with 40yr ERA5)
     6. Let EFR handle the generation decline that comes
        from equipment aging (this IS SCVR-driven)

  The performance adjustment from SCVR is not zero —
  but it's small enough that forcing it into the model
  adds complexity without adding accuracy.
```

---

## 6. When WOULD SCVR Performance Adjustment Be Justified?

The finding above is site-specific and scenario-specific. There are
conditions under which SCVR COULD show meaningful performance signals:

### 6.1 Different Geographies

```
SITES WHERE rsds OR sfcWind SCVR MIGHT BE LARGER

  High-latitude sites:
    Climate models show more disagreement on cloud cover changes
    at high latitudes. rsds SCVR could be larger (positive or
    negative) for solar farms in northern Europe or northern US.

  Coastal/offshore wind:
    Some models project changes in jet stream position and
    storm track frequency that could shift sfcWind distributions
    more than inland Texas sites.

  Monsoon-affected regions:
    Precipitation pattern changes could significantly alter
    seasonal cloud cover → rsds variability.

  For Hayhurst (desert, inland, low latitude):
    rsds is dominated by clear-sky radiation → very stable.
    This is why the SCVR is near-zero.

  For Maverick (inland Texas wind belt):
    Wind patterns are driven by continental pressure gradients
    that CMIP6 models agree are relatively stable through 2055.
```

### 6.2 Longer Time Horizons

Over 50-100 year horizons (not relevant for project finance but relevant
for infrastructure planning), cumulative resource shifts could become
material. The current 30-year project life sits in a window where
temperature changes are significant but resource changes are not.

### 6.3 If Future CMIP Generations Show Different Signals

CMIP6 models show high agreement on temperature trends but lower agreement
on circulation changes (which drive wind) and cloud feedbacks (which drive
irradiance). If CMIP7 models converge on a significant wind or irradiance
signal, SCVR performance adjustment would become justified.

---

## 7. What the Multi-Year Scaling Doc Should Say

Given this analysis, the "CLIMATE ADJUST" step in the multi-year scaling
pipeline (Section 3.2 and Stage 4) should be reframed:

### 7.1 Current Framing (Too Broad)

```
Current (from discussion_scaling_1yr_to_multiyear.md, Section 3.2):

  Gen_adjusted(t) = Gen_bootstrap(t) × CMIP_factor(t, scenario)

  Example (SSP2-4.5, solar):
    Years 1-10:  CMIP_factor = 0.99  (−1% GHI drift)
    Years 11-20: CMIP_factor = 0.97  (−3% cumulative)
```

This implies a 1-3% generation drift that the SCVR data does not support.
rsds SCVR is +0.0005 to +0.0022, which translates to +0.05% to +0.22%
generation change — not −1% to −3%.

### 7.2 Recommended Reframing

```
Revised approach:

  Gen_adjusted(t) = Gen_bootstrap(t)
                    × (1 − standard_degradation)^t     ← from spec
                    × (1 − climate_degradation(t))      ← from EFR/SCVR
                    × (1 − hazard_BI_loss(t))            ← from HCR/SCVR

  WHERE:
    standard_degradation: 0.5%/yr solar, 0.1-0.3%/yr wind (from manufacturer)
    climate_degradation(t): ADDITIONAL aging from SCVR-driven EFR
    hazard_BI_loss(t): revenue lost from SCVR-driven HCR events

  NOTE: No separate "CMIP_factor" on the resource itself.
    The resource (rsds, sfcWind) is effectively stable (SCVR ≈ 0).
    The generation decline comes from:
      (a) standard equipment degradation (spec)
      (b) climate-accelerated equipment degradation (EFR from SCVR)
      (c) business interruption from hazard events (HCR from SCVR)
    NOT from a change in the underlying resource.
```

This is cleaner, more honest, and better supported by the data. The
"CLIMATE ADJUST" box in the Stage 4 pipeline becomes an EFR+HCR
adjustment layer, not a resource perturbation layer.

```
REVISED STAGE 4 PIPELINE

  ┌──────────────────┐
  │ REGIME SAMPLER    │  HMM transition → which regime?
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │ YEAR SELECTOR     │  Sample 8760 weather year from regime pool
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │ GENERATION MODEL  │  PVLib / PyWake on ORIGINAL weather
  │ (no perturbation) │  (resource is stable — SCVR confirms this)
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │ EFR ADJUSTMENT    │  Climate-accelerated degradation from SCVR
  │ (Channel 2)       │  tasmin, tas, tasmax → Peck's, Coffin-Manson
  │                   │  → Additional annual degradation rate
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │ HCR OVERLAY       │  Hazard events from SCVR-adjusted frequencies
  │ (Channel 1)       │  pr, hurs, FWI → flood, hail, wildfire, icing
  │                   │  → BI losses subtracted from generation
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │ SECOND-ORDER      │  IF desired (optional, small):
  │ TEMP EFFECTS      │  - Solar thermal derating: ~−0.3% by 2050
  │ (documented but   │  - Wind air density: ~−0.5% by 2050
  │  not required)    │  - Wind icing benefit: ~+0.5% by 2050
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │ PRICING           │  Hourly market curves (block-sampled)
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │ REVENUE → CFADS   │  Revenue − OpEx − Reserves
  │ → DSCR            │
  └──────────────────┘

  Key change: No "CLIMATE ADJUST" box between YEAR SELECTOR
  and GENERATION MODEL. The weather inputs to PVLib/PyWake
  are NOT perturbed. Climate effects enter AFTER generation,
  through EFR (degradation) and HCR (hazard events).
```

---

## 8. The Options We Considered and Where They Stand Now

In earlier discussions, we evaluated four options for SCVR-driven
performance adjustment. Here's the updated assessment given the data:

| Option | Description | Original assessment | Revised assessment |
|---|---|---|---|
| **1** | Flat generation scalar from SCVR | "Easy but physically wrong" | **Not needed.** The scalar would be <0.3% — within noise. |
| **2** | Channel-decomposed analytical | "Medium accuracy, good interim" | **Useful for documentation**, not for model adjustment. Shows the work, confirms the signal is small. |
| **3** | Quantile-mapped weather perturbation | "Target architecture" | **Over-engineered for this signal.** Quantile-mapping rsds by +0.0005 SCVR is not meaningful. Only justified if future data shows larger resource shifts. |
| **4** | Direct CMIP through physics model | "Anti-pattern" | **Still wrong.** Nothing changes here. |

The channel decomposition (Option 2) remains valuable as an **analytical
exercise** — it's how we proved the performance signal is small. But it
shouldn't become a production model component given the signal magnitude.

### 8.1 What Option 2 Analysis Taught Us

The channel-by-channel decomposition was not wasted work. It produced
three important findings:

```
FINDING 1: Solar performance adjustment is dominated by irradiance,
           which has near-zero SCVR. The thermal derating channel
           (from tasmax) is real but ~0.3% — an order of magnitude
           smaller than the EFR impact.

FINDING 2: Wind performance adjustment self-cancels. Icing reduction
           (+0.5%) approximately offsets air density loss (−0.5%).
           Net is near-zero. This is a genuine finding, not a
           modeling artifact.

FINDING 3: The cross-correlation concern (temperature × irradiance
           concentrated in peak hours) is theoretically valid but
           practically irrelevant at this signal magnitude. A 28%
           error on a 0.3% adjustment is a 0.08% absolute error.
```

### 8.2 When to Revisit Option 3 (Quantile Mapping)

Option 3 (quantile-mapped weather perturbation through PVLib/PyWake)
should be revisited if any of these conditions change:

- rsds SCVR exceeds ±0.02 (order of magnitude larger than current)
- sfcWind SCVR exceeds ±0.03 for wind assets
- New CMIP generation shows significantly different cloud/circulation signals
- Analysis moves to sites where resource variability is higher
  (high-latitude, coastal, monsoon-affected)
- Time horizon extends beyond 2060 where cumulative shifts may grow

Until then, the quantile mapping infrastructure is worth building
as part of the SCVR computation pipeline (it's essentially free —
the exceedance curves already exist) but should not be activated
for performance adjustment in the production model.

---

## 9. Summary

### What SCVR Is Good For

```
✅ Equipment degradation (EFR):
   tasmin SCVR +0.16 → Peck's aging acceleration → IUL shortening
   This is the DOMINANT impact. ~10-15% NAV impairment for solar.

✅ Hazard frequency (HCR):
   pr, hurs, temperature SCVRs → flood, hail, wildfire, icing changes
   Real but smaller impact. ~2-5% NAV impairment.

✅ Understanding which climate variables matter:
   The finding that rsds and sfcWind are stable is ITSELF valuable.
   It tells investors: "Your resource is secure; your equipment is not."
```

### What SCVR Is Not Good For

```
⚠️ Year-over-year performance adjustment:
   rsds SCVR: +0.0005 → not enough signal to justify adjustment
   sfcWind SCVR: −0.011 → not enough signal to justify adjustment
   Second-order temperature effects: real but ~0.3% (within noise)

   The multi-year scaling bootstrap (40yr ERA5 through PVLib/PyWake)
   already handles performance variability well. SCVR doesn't add
   meaningful information to this channel.
```

### The Key Insight for Investors

The most important thing SCVR tells us about performance is
**what it DOESN'T find**: the resource itself is stable.

This is actually good news. It means:

- Solar farms will receive approximately the same irradiance in 2050 as today
- Wind farms will experience approximately the same wind speeds in 2050 as today
- The generation decline over project life comes from equipment aging
  (which SCVR quantifies through EFR) and hazard events (which SCVR
  quantifies through HCR), NOT from resource disappearing

The risk is to the hardware, not to the fuel supply. And hardware risk
is insurable, manageable, and quantifiable — which is exactly what the
LT Risk Evolution Framework is designed to do.

---

**Previous →** [04 — Wind Use Case](04_wind_use_case.md)
