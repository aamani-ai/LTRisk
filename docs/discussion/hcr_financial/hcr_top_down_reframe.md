---
title: "Discussion — Reframing HCR Around Canonical Hazard Definitions"
type: discussion
domain: climate-risk / methodology / architecture
created: 2026-04-09
status: draft — foundational reframe, pending team discussion
context: >
  The LTRisk HCR computation was built bottom-up: "what hazards can we
  derive from our 7 CMIP6 variables?" This created threshold subjectivity,
  an orchestrator routing problem, and a disconnect from the hazards team's
  canonical hazard list. This doc proposes the reverse: start from the
  hazards team's 10 canonical hazards (which already have historical
  frequency-severity distributions) and ask "what can LTRisk say about
  each one's future frequency?" The answer varies by hazard — from gold
  standard (heat wave) to fully blocked (tornado) — and that's honest.
relates-to:
  - docs/discussion/architecture/pipeline_complementarity.md
  - docs/discussion/architecture/top_down_meets_bottom_up.md
  - docs/discussion/hcr_financial/pathway_defensibility.md
  - docs/learning/C_financial_translation/06b_climate_risk_orchestrator.md
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
---

# Reframing HCR Around Canonical Hazard Definitions

> **The shift:** Instead of "what hazards can we derive from our climate
> variables?", ask "for each of InfraSure's 10 canonical hazards, what
> can LTRisk say about how climate change shifts its frequency?"

---

## 1. Why Reframe?

### What We've Been Doing (Bottom-Up)

```
Start:   "We have tasmax, tasmin, pr, hurs, sfcWind from CMIP6"
Then:    "What hazards can we derive from these variables?"
Result:  10 hazard definitions WE invented
         (heat_wave, extreme_precip, freeze_thaw, fire_weather, etc.)
Problem: These are OUR definitions, OUR thresholds
         They don't match the hazards team's canonical list
         They created the orchestrator routing confusion
         They required threshold subjectivity debates (2.5× vs 26×)
```

### What We Should Do (Top-Down)

```
Start:   "The hazards team has 10 canonical hazards with NOAA definitions"
         (Hail, Tornado, Strong Wind, Winter Weather, Ice Storm,
          Wildfire, Hurricane, Heat Wave, Riverine Flood, Coastal Flood)
Then:    "For each, what can LTRisk say about future frequency?"
Result:  An HCR estimate (or honest "we can't") for each canonical hazard
         Using the BEST available method per hazard:
           - Published scaling where peer-reviewed research exists
           - Direct computation from CMIP6 where variables permit
           - Literature-based direction estimate where data is limited
           - Documented "not projectable" where we genuinely can't
```

### What This Resolves

1. **No more inventing hazard definitions** — we use the hazards team's
   canonical definitions. No threshold subjectivity.
2. **No more orchestrator confusion** — the canonical list IS the routing.
   Each hazard gets the best available method.
3. **Natural pipeline complementarity** — hazards team has historical
   frequency-severity. LTRisk provides the climate change delta.
   Together: `future_risk = historical_baseline × (1 + HCR)`.
4. **Honest coverage assessment** — we say "here's what we can project,
   here's what we can't, and here's the confidence for each."

---

## 2. The 10 Canonical Hazards — What Can LTRisk Say About Each?

### Tier 1: Strong Science, Defensible HCR

These have published scaling factors or are directly computable from
CMIP6 with high confidence.

#### Heat Wave — GOLD STANDARD

```
Canonical definition: ≥3 consecutive days at or above 90°F (32°C)
                      (NOAA: "Heat" + "Excessive Heat" event types)

What LTRisk can say:
  HCR ≈ SCVR_tasmax × 2.5
  Published scaling: Diffenbaugh et al. 2017 (PNAS), Cowan et al. 2017
  Cross-validated: NB04a Pathway B implied scaling = 2.7× (within 8%)

  Recent research STRENGTHENS this:
  - Kirchengast et al. 2026: 10× increase in heat extremity in Europe
  - Nature Geoscience 2025: heat wave duration increases NONLINEARLY
  - PNAS 2024: observed trends OUTPACE CMIP6 models (conservative)

  Direction: STRONGLY INCREASING
  Magnitude: ~2.5× amplification per unit of mean shift
  Confidence: HIGH — peer-reviewed, validated against our data

  Hayhurst result: HCR = +20% (SSP585)
```

#### Wildfire — STRONG SCIENCE

```
Canonical definition: Uncontrolled fire in wildland vegetation
                      (NOAA: "Wildfire" event type)

What LTRisk can say:
  Canadian FWI system computable from NEX-GDDP daily data:
    FWI = f(tasmax, hurs, sfcWind, pr)
  Published: Abatzoglou & Williams 2016 (PNAS) — anthropogenic climate
    change nearly DOUBLED western US forest fire area 1984-2015.
  Quilcaille et al. 2023 (ESSD) — pre-computed FWI from all CMIP6
    models 1850-2100, robust increases under all SSPs.
  Nature Comms 2025: extreme fire weather years 88-152% more likely
    in contemporary vs pre-industrial climate.

  Direction: STRONGLY INCREASING
  Magnitude: roughly doubles per ~1.5°C of warming (burned area)
  Confidence: MODERATE-HIGH — FWI computable, strong literature
  Caveat: FWI was calibrated for Canadian forests. Regional
    calibration for Texas needed. FWI measures CONDITIONS, not
    actual fire occurrence (P(fire|high FWI) << 1).

  Status: Currently flagged as risk indicator. Could be upgraded
  to Tier 1 HCR with regional FWI calibration.
```

#### Riverine Flood — WELL-GROUNDED

```
Canonical definition: River overflow from sustained rainfall/snowmelt
                      (NOAA: "Flood" + "Flash Flood" + "Heavy Rain")

What LTRisk can say:
  Rx5day (max 5-day rolling precipitation) computable from daily pr.
  Published: Clausius-Clapeyron ~6.5-7%/°C for extreme precipitation
    intensity (Tabari 2020, Sci. Reports).
  Super-C-C: convective precipitation can exceed 7%/°C (Nature
    Geoscience 2025).
  BUT: precipitation ≠ flooding — catchment properties mediate
    (Brunner et al. 2021).

  Direction: INCREASING (extreme precipitation intensifies)
  Magnitude: ~6.5-7% per °C thermodynamically
  Confidence: MODERATE — precipitation trend clear, but flood response
    is site-dependent (soil, drainage, topography)
  Method: Direct counting (Pathway B) — mandatory because mean
    SCVR_pr ≈ 0 (Jensen's inequality)

  Hayhurst result: HCR = +2.6% (SSP585, Rx5day)
```

#### Ice Storm — FEASIBLE

```
Canonical definition: Freezing rain producing ≥0.25" ice accumulation
                      (NOAA: "Ice Storm" event type)

What LTRisk can say:
  Compound threshold computable: tasmin < 0°C AND hurs > 85%
  Published: Jeong et al. 2019 (NHESS) — 50-member CanRCM4 ensemble:
    design ice loads DECREASE below 40°N, INCREASE above 40°N.

  Direction: DECREASING for southern US sites (benefit)
  Magnitude: -20 to -50% by late century (below 40°N)
  Confidence: MODERATE — compound threshold is a surface proxy,
    not the vertical temperature profile that actually causes icing
  Method: Direct counting (Pathway B)

  Hayhurst result: HCR = -44.5% (SSP585, strongly negative = benefit)
```

### Tier 2: Feasible With Published External Data

These aren't computable from CMIP6 directly, but published research
provides defensible scaling factors.

#### Hurricane — PUBLISHED CONSENSUS

```
Canonical definition: Tropical cyclone with sustained winds ≥74 mph
                      (NOAA: "Hurricane" + "Tropical Storm")

What LTRisk can say:
  NOT computable from NEX-GDDP (needs SST, ocean dynamics).
  BUT: strong published consensus exists.
  
  Knutson et al. 2020 (BAMS) — WMO consensus for 2°C warming:
    Frequency: DECREASES (most models agree)
    Cat 4-5 proportion: +13%
    Lifetime maximum wind: +5% (range 1-10%)
    TC precipitation: +14%
    
  Lee et al. 2024 (Science Advances): 75% of 20 CMIP6 models
    show decreasing TC frequency.
  
  "FEWER BUT FIERCER" is the consensus.

  Direction: Frequency SLIGHTLY DECREASING, intensity INCREASING
  Magnitude: Freq -5 to -10% per 2°C; wind +5%; rain +14%
  Confidence: MODERATE — consensus exists but models disagree on
    magnitude. The "fewer" part is less certain than "fiercer."
  Method: Published scaling (Pathway A from Knutson 2020)

  For financial impact: combined effect is roughly NEUTRAL to
  INCREASING (intensity outweighs frequency for damage).
  Jewson 2022 (QJRMS) provides North Atlantic landfall translation.

  Hayhurst (inland TX): Low hurricane exposure regardless of trend.
```

#### Coastal Flood — PUBLISHED SLR PROJECTIONS

```
Canonical definition: Seawater inundation from surge/tides/SLR
                      (NOAA: "Coastal Flood" + "Storm Surge/Tide")

What LTRisk can say:
  NOT computable from NEX-GDDP (needs sea level, tides, surge).
  BUT: strong published science on SLR → flood frequency.
  
  Buchanan et al. 2020 (Sci. Reports): SLR EXPONENTIALLY
    increases coastal flood frequency. 100-year events become
    10-year events at 1/3 of US coastal sites by 2050.
  Vitousek et al. 2017: frequency doubles every ~5 years
    at many sites.
  NOAA 2022: US SLR projections +0.6m (low) to +2.2m (high).
  Amplification factors: 10× to 1000× for 0.5m of SLR.

  Direction: STRONGLY INCREASING (exponential)
  Magnitude: 10-1000× amplification per 0.5m SLR
  Confidence: HIGH for the science, site-specific for application
    (needs elevation + distance-to-coast)
  Method: Published SLR projections × exponential amplification

  Hayhurst (inland TX): NOT EXPOSED — HCR not applicable.
  Relevant for: coastal solar/wind assets.
```

#### Winter Weather — FEASIBLE

```
Canonical definition: Snow/sleet/freezing rain compound event
                      (NOAA: "Winter Storm" + "Winter Weather" + "Heavy Snow")

What LTRisk can say:
  Compound threshold computable: pr > threshold AND tasmin < 0°C
  Cannot distinguish snow/sleet/freezing rain (no precipitation
    phase in NEX-GDDP), but "wintry precipitation day" is trackable.
  Published: 64% of US stations show less snowfall than 1970s
    (Climate Central). Frost season shortens up to 3.3 months
    under SSP5-8.5 by 2100.

  Direction: DECREASING (below ~45°N)
  Magnitude: Substantial frequency decline at southern US sites
  Confidence: MODERATE — direction is clear, magnitude uncertain
  Method: Direct counting (Pathway B) — compound threshold

  Not currently implemented in NB04a but FEASIBLE to add.
```

### Tier 3: Blocked — Cannot Project From Available Data

#### Hail — BLOCKED

```
Canonical definition: Ice pellets ≥0.75" from convective storms
                      (NOAA: "Hail" event type)

What LTRisk can say:
  NOT computable from NEX-GDDP (requires CAPE, vertical wind shear,
    upper-level temperature profiles — none in surface daily data).
  
  Published science is AMBIGUOUS for the US:
    Raupach et al. 2021 (Nature Reviews): frequency expected to
    DECREASE in North America, but severity (stone size) INCREASES.
    Competing mechanisms: more CAPE (more convection) vs higher
    melting level (stones melt before reaching ground) vs less
    wind shear (less supercell organisation).
    
  Direction: AMBIGUOUS (fewer events, larger stones)
  Magnitude: Unknown — no defensible single scaling
  Confidence: LOW
  
  What to report: "Hail climate projection NOT AVAILABLE from
  LTRisk. Use hazards repo historical frequency (NOAA 1996-2024)
  as baseline. Literature suggests frequency may decrease but
  severity may increase under warming — net financial impact uncertain."
  
  This is the #2 financial risk for solar (from insurance data).
  The gap matters. Future work: convective proxy indices from
  ERA5 or high-resolution climate models.
```

#### Tornado — BLOCKED

```
Canonical definition: Rotating column EF0-EF5
                      (NOAA: "Tornado" event type)

What LTRisk can say:
  NOT computable (mesoscale phenomenon, requires upper-air data).
  
  Published: Diffenbaugh et al. 2013 (PNAS) — severe thunderstorm
    ENVIRONMENTS increase ~40-100% over eastern US by late 21st
    century. But environments ≠ tornadoes. The conversion efficiency
    (what fraction of favourable environments produce an actual
    tornado) is unknown.
  Woods et al. 2023 (GRL): future intensity may increase, but
    frequency projections remain highly uncertain.
    
  Direction: UNCERTAIN (environments increase, actual counts unknown)
  Magnitude: Unknown
  Confidence: LOW
  
  What to report: "Tornado climate projection NOT AVAILABLE.
  Use SPC historical data as baseline. Environment frequency
  increases ~40-100% but translation to actual tornado counts
  is unresolved in the literature."
```

### Strong Wind — TRIVIAL

```
Canonical definition: Sustained winds ≥58 mph
                      (NOAA: "Thunderstorm Wind" + "Strong Wind" + "High Wind")

What LTRisk can say:
  SCVR_sfcWind ≈ 0 at pilot sites. No change projected.
  Published: Global "stilling" trend — near-surface wind DECREASING
    slightly under warming. More light-wind days, fewer strong-wind.
    
  Direction: FLAT to slight decrease
  Magnitude: ~0% at most sites
  Confidence: MODERATE (for "no change")
  Method: HCR = SCVR_sfcWind × 1.0 ≈ 0

  This hazard is important in the HISTORICAL pipeline (NOAA events)
  but NOT a climate change driver at these sites.
```

---

## 3. The Complete Picture — One Table

```
CANONICAL       DIRECTION     BEST HCR         METHOD              CONFIDENCE
HAZARD          UNDER         ESTIMATE
                WARMING       (per 2°C)
═══════════════ ════════════  ═══════════════   ════════════════    ══════════

TIER 1 — Directly computable or published:
Heat Wave       ↑↑ Strong     +2.5× amplif.    Published scaling   HIGH
Wildfire        ↑↑ Strong     ~doubles          CMIP6 FWI          MOD-HIGH
Riverine Flood  ↑ Moderate    +6.5-7%/°C        CMIP6 Rx5day       MODERATE
Ice Storm       ↓ Decreasing  -20 to -50%       CMIP6 compound     MODERATE
                (below 40°N)

TIER 2 — Feasible from published external data:
Hurricane       ↓ Freq, ↑ Int  Freq -5-10%     Published (Knutson) MODERATE
Coastal Flood   ↑↑↑ Exponential 10-1000×/0.5m   Published (SLR)    HIGH
Winter Weather  ↓ Decreasing   Substantial      CMIP6 compound     MODERATE

TIER 3 — Blocked or trivial:
Strong Wind     → Flat         ~0%              SCVR (trivial)     MOD (no Δ)
Hail            ? Ambiguous    Unknown          BLOCKED            LOW
Tornado         ? Uncertain    Unknown          BLOCKED            LOW
```

---

## 4. What Changes in the Framework

### Before (Bottom-Up)

```
SCVR Report → Invent 10 hazard definitions → Compute HCR for each
  → Orchestrator routes to Channel 1/2/flags
  → BI_loss = HCR × baseline_BI_pct × Revenue
  
Problems: threshold subjectivity, routing confusion,
  disconnect from hazards team's canonical list
```

### After (Top-Down)

```
Hazards team's 10 canonical hazards (with NOAA definitions)
  → For each: "What can LTRisk say about future frequency?"
  → Use the BEST available method per hazard:
      Published scaling (heat wave, hurricane)
      CMIP6 computation (flood, ice storm, wildfire, winter weather)
      Documented "blocked" (hail, tornado)
      Trivial (strong wind: ~0 change)
  → HCR per canonical hazard per year
  → Combine with hazards repo historical baseline:
      future_risk = baseline_EAL × (1 + HCR)

Benefits: uses established definitions, honest about gaps,
  natural pipeline integration, no threshold subjectivity for
  published scaling hazards
```

### The Orchestrator Simplifies

```
BEFORE: Complex routing matrix with 3 categories, 2 pathways, mode A/B

AFTER: Simple lookup per canonical hazard:

  Hazard          Best available method    Source
  ──────────────  ──────────────────────  ──────────────────
  Heat Wave       SCVR × 2.5              Diffenbaugh 2017
  Wildfire        FWI from CMIP6 daily     Quilcaille 2023
  Riverine Flood  Rx5day from CMIP6 daily  Tabari 2020
  Ice Storm       Compound from CMIP6      Jeong 2019
  Hurricane       Published consensus      Knutson 2020
  Coastal Flood   SLR projections          IPCC AR6 / NOAA
  Winter Weather  Compound from CMIP6      Literature
  Strong Wind     SCVR × 1.0 (≈0)         Global stilling
  Hail            NOT PROJECTABLE          Gap
  Tornado         NOT PROJECTABLE          Gap

  No more "Pathway A vs B" debate per hazard.
  No more "is this BI or degradation?"
  Just: "what's the best answer we can give?"
```

---

## 5. What About EFR (Channel 2)?

EFR is separate from this reframe. EFR measures equipment DEGRADATION
from continuous climate stress — not hazard event frequency. It doesn't
map to the canonical hazard list in the same way.

```
EFR stays as-is:
  Peck's (thermal aging):    SCVR_tas → Arrhenius → EFR
  Coffin-Manson (cycling):   Daily freeze-thaw counts → EFR
  Palmgren-Miner (wind):     SCVR_sfcWind → EFR (≈0)

These are degradation MECHANISMS, not hazard EVENTS.
The hazards team's canonical list is about EVENTS (hail, tornado, etc.)
EFR is about continuous STRESS (temperature, cycling, fatigue).
Different questions, different frameworks.
```

---

## 6. Implications for NB04a

### What Changes

1. **The hazard list** aligns with canonical names (not our invented ones)
2. **Published scaling** used wherever a peer-reviewed factor exists
3. **Direct computation** used where CMIP6 can answer the question
4. **Published external data** used for hurricane and coastal flood
5. **"Not projectable"** honestly documented for hail and tornado
6. **EFR inputs** (freeze-thaw counts) are computed as a byproduct,
   not as a separate "hazard" routed to a different channel

### What Stays

- The CMIP6 daily data loading infrastructure
- The hazard counter functions (they compute useful things)
- The SCVR Report Card (still tells us when mean-based methods work)
- The cross-validation approach (published scaling vs direct counting)
- The EFR computation (NB04b, separate from this reframe)

---

## 7. Open Questions

1. **How to handle hurricane and coastal flood** — these need external
   data (SST, SLR projections) not currently in the LTRisk pipeline.
   Do we compute them in NB04a or create a separate mechanism?

2. **Wildfire upgrade path** — currently flagged as risk indicator. The
   science supports Tier 1 (FWI from daily data, strong literature).
   Should NB04a compute FWI-based HCR for wildfire?

3. **Winter weather** — not currently implemented. Add compound threshold
   (pr > X AND tasmin < 0°C) to NB04a?

4. **Hail as #2 financial risk** — the gap matters. Are there convective
   proxy indices from ERA5 that could provide a crude estimate?

5. **How does this affect the dashboard?** — instead of "5 BI hazards +
   risk indicators + gaps", show "10 canonical hazards with HCR where
   available and 'historical only' where not"?

6. **Naming alignment** — our "extreme_precip" and "flood_rx5day" both
   map to the canonical "Riverine Flood". Our "icing_shutdown" maps to
   "Ice Storm". Align names?

---

## 8. Recommended Next Steps

```
STEP 1: Align on this reframe (this doc + team discussion)

STEP 2: Revise NB04a to compute HCR per canonical hazard name:
  - Heat Wave:       SCVR × 2.5 (unchanged, rename to canonical)
  - Riverine Flood:  Rx5day counting (unchanged, merge extreme_precip + flood_rx5day)
  - Ice Storm:       Compound counting (unchanged, rename icing_shutdown)
  - Wildfire:        FWI counting (upgrade from risk indicator to HCR)
  - Winter Weather:  Compound counting (new implementation)
  - Strong Wind:     SCVR × 1.0 (unchanged)
  - Hurricane:       Published scaling from Knutson 2020 (new, Pathway A)
  - Coastal Flood:   Published SLR × amplification (new, external data)
  - Hail:            Flag "not projectable" (document gap)
  - Tornado:         Flag "not projectable" (document gap)

STEP 3: Update dashboard to show all 10 canonical hazards

STEP 4: Connect to hazards repo baseline:
  future_risk = baseline_EAL × (1 + HCR) per canonical hazard
```

---

## Cross-References

| Topic | Doc |
|-------|-----|
| Pipeline complementarity | [pipeline_complementarity.md](../architecture/pipeline_complementarity.md) |
| Top-down meets bottom-up | [top_down_meets_bottom_up.md](../architecture/top_down_meets_bottom_up.md) |
| Published scaling defensibility | [pathway_defensibility.md](pathway_defensibility.md) |
| Orchestrator (current, to be simplified) | [06b_climate_risk_orchestrator.md](../../learning/C_financial_translation/06b_climate_risk_orchestrator.md) |
| Hazards team canonical definitions | External: `hazard_types_definitions.docx` |
| HCR methodology (current) | [07_hcr_hazard_change.md](../../learning/C_financial_translation/07_hcr_hazard_change.md) |

## Key References

| Paper | Finding | DOI |
|-------|---------|-----|
| Diffenbaugh et al. 2017 | Heat wave 2.5× amplification | [doi:10.1073/pnas.1618082114](https://doi.org/10.1073/pnas.1618082114) |
| Abatzoglou & Williams 2016 | Wildfire area doubled from climate change | [doi:10.1073/pnas.1607171113](https://doi.org/10.1073/pnas.1607171113) |
| Tabari 2020 | Extreme precip +6.5-7%/°C | [doi:10.1038/s41598-020-70816-2](https://doi.org/10.1038/s41598-020-70816-2) |
| Jeong et al. 2019 | Ice loads decrease below 40°N | [doi:10.5194/nhess-19-857-2019](https://doi.org/10.5194/nhess-19-857-2019) |
| Knutson et al. 2020 | Hurricane: fewer but fiercer | [doi:10.1175/BAMS-D-18-0194.1](https://doi.org/10.1175/BAMS-D-18-0194.1) |
| Quilcaille et al. 2023 | FWI from all CMIP6 models 1850-2100 | [doi:10.5194/essd-15-2153-2023](https://doi.org/10.5194/essd-15-2153-2023) |
| Buchanan et al. 2020 | Coastal flood frequency exponential with SLR | [doi:10.1038/s41598-020-62188-4](https://doi.org/10.1038/s41598-020-62188-4) |
| Raupach et al. 2021 | Hail: fewer US events but larger stones | [doi:10.1038/s43017-020-00133-9](https://doi.org/10.1038/s43017-020-00133-9) |
