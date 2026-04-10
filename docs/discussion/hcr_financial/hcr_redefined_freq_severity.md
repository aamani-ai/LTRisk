---
title: "Discussion — Redefining HCR: From Frequency-Only to Expected Damage Ratio"
type: discussion
domain: climate-risk / methodology / first-principles
created: 2026-04-09
updated: 2026-04-10
status: draft — foundational rethink, pending team decision
context: >
  HCR currently measures frequency change only. This doc proposes
  redefining it to capture both frequency AND severity change. It also
  maps out honestly which hazards have baseline BI data (from the hazards
  repo) vs which only have EAL (from NRI), and documents the linearity
  assumption required when applying a damage-level ratio to BI.
relates-to:
  - docs/discussion/hcr_financial/hcr_top_down_reframe.md
  - docs/discussion/hcr_financial/pathway_defensibility.md
  - docs/discussion/architecture/pipeline_complementarity.md
  - docs/discussion/bi_methodology/01_what_is_bi.md
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
---

# Redefining HCR: From Frequency-Only to Expected Damage Ratio

> **The problem:** HCR currently counts how many more events cross a threshold.
> It misses that each event may also be MORE INTENSE. For hurricane, a
> frequency-only metric says "7.5% fewer" when actual damage INCREASES
> 7-43%.

> **The proposal:** Keep the HCR name but redefine what it measures — from
> "change in event count" to "change in expected annual damage." Then
> connect it to the hazards repo's baseline BI to compute climate-driven
> additional losses — with honest acknowledgment of where data exists,
> where it doesn't, and what assumptions are required.

---

## 1. Important Definitions — BI vs EAL

These are different things. Mixing them up leads to wrong formulas.

```
BI (Business Interruption):
  Revenue lost because the plant could not produce during downtime.
  Computed from: forced_outage_hours + (damage% × recovery_hours) × hourly_revenue
  The hazards repo computes this for: Hail, Tornado, Strong Wind (3 hazards)

EAL (Expected Annual Loss):
  TOTAL economic loss from a hazard — includes property damage, BI,
  indirect costs, and everything else.
  FEMA NRI computes this for: all 18 hazard types at county level.

  EAL ≠ BI.
  EAL includes BI but also includes property damage (often the larger part).
  BI is a FRACTION of EAL.

  For hail on solar: the panel replacement cost (property damage) may be
  $200K. The lost revenue during 3-month repair (BI) may be $50K.
  EAL ≈ $250K. BI ≈ $50K. BI/EAL ≈ 20%.
```

**Throughout this doc, BI means BI and EAL means EAL. Never interchanged.**

---

## 2. What HCR Should Measure (Redefined)

### Old Definition (frequency only)

```
HCR = (future_event_count - baseline_event_count) / baseline_event_count

  "20% more heat wave days"
  Step-function damage assumption: every event above threshold is equally bad.
```

### New Definition (expected damage ratio)

```
HCR = (future_expected_damage - baseline_expected_damage) / baseline_expected_damage

  "20% more expected annual damage from heat"
  Uses a realistic damage function D(intensity).
  Captures BOTH more events AND worse events.
```

### Same Name, Same Structure

```
                    OLD HCR              NEW HCR
                    ──────────           ──────────
Name:               HCR                  HCR (unchanged)
Structure:          Fractional change    Fractional change
Captures frequency: YES                  YES
Captures severity:  NO                   YES
What it measures:   Event count change   Expected damage change
```

### Why Severity Matters

```
HAZARD          OLD HCR (freq)   WHAT OLD HCR MISSES         CORRECTED ESTIMATE
Heat Wave       +20%             Events also hotter/longer   +30 to +50%
Hurricane       -7.5%            Wind +5% → damage +16-55%  +7% to +43%
Wildfire        ~0% (count flat) Area per fire up to 6×      +100 to +600%
Hail            -25% (fewer)     Large stones +15-75%        0% to +50%?
Riverine Flood  +3%              Intensity +7-14%/°C         +10 to +30%
```

For 4 of 10 canonical hazards, frequency-only HCR tells the wrong
financial story. The redefined HCR fixes this.

---

## 3. How Redefined HCR Connects to BI — Three Scenarios

The clean formula everyone wants is:

```
Additional_climate_BI = baseline_BI × HCR
```

But this requires TWO things for the SAME hazard:
1. **baseline_BI** from the hazards repo (historical BI in $/yr)
2. **HCR** from LTRisk (the climate change multiplier)

For most hazards, we have ONE but not BOTH.

### Scenario A: Both Exist (IDEAL — but currently NO hazard has this)

```
Hazards repo has baseline_BI + LTRisk has HCR for the SAME hazard.

  Additional_BI = baseline_BI × HCR
  future_BI = baseline_BI × (1 + HCR)

  This is clean, defensible, and uses known inputs.
  
  CURRENT STATUS: No hazard has both pieces today.
    - Hail/Tornado/Strong Wind: hazards repo has BI, but LTRisk CANNOT compute HCR
    - Heat/Flood/Ice/Wildfire: LTRisk can compute HCR, but hazards repo has NO BI
```

### Scenario B: Hazards Repo Has BI, LTRisk Cannot Compute HCR

```
Hazards: Hail, Tornado, Strong Wind

  We have: baseline_BI from hazards repo (computed, known)
  We lack: HCR from LTRisk (CMIP6 cannot project these hazards)

  What to report:
    "Historical BI: $24K/yr (from 29 years of NOAA data)"
    "Climate change projection: NOT AVAILABLE"
    "Assume: historical frequency persists (HCR = 0)"
    
  future_BI = baseline_BI × (1 + 0) = baseline_BI
  
  This is honest. We report what we have and flag what we can't project.
  
  For hail: literature suggests damage LIKELY INCREASES (larger stones)
  but we cannot quantify from CMIP6. Flag as directional estimate.
```

### Scenario C: LTRisk Has HCR, No Baseline BI Exists

```
Hazards: Heat Wave, Riverine Flood, Ice Storm, Wildfire, etc.

  We have: HCR from LTRisk (climate change ratio, computed)
  We lack: baseline_BI from hazards repo (not computed for these hazards)
  We have: NRI EAL (total economic loss, not BI specifically)
  
  THREE OPTIONS:
  
  Option C1: Use NRI EAL as a proxy for BI
    Additional_BI ≈ NRI_EAL × (BI_fraction) × HCR
    
    Requires: estimating what fraction of EAL is BI (not property damage)
    Assumption: BI/EAL ratio is stable under climate change (LINEARITY)
    Defensibility: WEAK — BI_fraction is unknown for most hazards
    
  Option C2: Develop BI methodology for these hazards in the hazards repo
    Add forced_outage_hours and recovery_hours for heat wave, flood, etc.
    Then: baseline_BI computed from NOAA events, just like hail/tornado/wind
    This closes the gap and enables Scenario A.
    Defensibility: STRONG — but requires hazards team work
    
  Option C3: Compute BI directly in LTRisk using damage functions
    Define D(intensity) → BI for each hazard (e.g., heat derating curve)
    Compute both baseline_BI AND future_BI from CMIP6 daily data
    HCR = (future_BI - baseline_BI) / baseline_BI
    Additional_BI = baseline_BI_from_LTRisk × HCR
    Defensibility: MODERATE — self-consistent but not cross-validated
    against historical NOAA data
```

### The Coverage Gap — Honest Table

```
HAZARD          HAS BASELINE BI?        HAS HCR?         CAN COMPUTE
                (hazards repo)          (LTRisk)          Additional_BI?
═══════════════ ═══════════════════     ═══════════════   ═══════════════
Hail            YES (full BI calc)      NO (blocked)      NO (no HCR)
Tornado         YES (full BI calc)      NO (blocked)      NO (no HCR)
Strong Wind     YES (full BI calc)      ~0 (trivial)      YES (~$0)
Heat Wave       NO                      YES               NO (no baseline BI)
Riverine Flood  NO (NRI EAL only)       YES               PARTIAL (see C1-C3)
Ice Storm       NO (NRI EAL only)       YES               PARTIAL
Wildfire        NO (NRI EAL only)       YES               PARTIAL
Hurricane       NO (NRI EAL only)       YES (published)   PARTIAL
Coastal Flood   NO (NRI EAL only)       YES (SLR)         PARTIAL
Winter Weather  NO (NRI EAL only)       YES               PARTIAL

HONEST SUMMARY:
  Clean Additional_BI (Scenario A):  0 out of 10 hazards
  Baseline BI known but no HCR:     3 (hail, tornado, strong wind)
  HCR computable but no baseline BI: 7 (heat, flood, ice, wildfire, etc.)

  THE TWO PIPELINES COVER DIFFERENT HAZARDS.
  The clean formula works when BOTH pieces exist for the same hazard.
  Currently: they don't overlap.
```

---

## 4. The Linearity Assumption

If we use NRI EAL as a proxy for BI (Option C1), or if we apply a
damage-level HCR to BI, we're assuming:

```
ASSUMPTION: BI changes proportionally to total damage.

  If total damage increases 30%, BI also increases 30%.
  This means: BI/EAL ratio stays constant under climate change.

WHY THIS MAY NOT HOLD:

  Heat wave:
    BI component: shutdown hours (INCREASES with hotter events)
    Property damage: near-zero (heat doesn't break panels)
    → BI grows FASTER than EAL → linearity assumption UNDERESTIMATES BI change
  
  Hail:
    BI component: recovery downtime (proportional to damage%)
    Property damage: panel replacement cost (grows with stone size)
    → Property damage may grow faster than BI → linearity OVERESTIMATES BI change
  
  Flood:
    BI component: site inaccessibility (days, depends on depth)
    Property damage: equipment submersion (depends on depth)
    → Both grow together → linearity roughly holds
  
  Hurricane:
    BI component: cleanup + repair downtime
    Property damage: wind + surge structural damage
    → Damage grows as V^3 to V^9, BI grows more linearly
    → linearity OVERESTIMATES BI change

DOCUMENTING THIS:
  Gen.1: Apply HCR uniformly to BI, noting the linearity assumption.
  Gen.2: Decompose HCR into frequency component and severity component,
         apply the frequency ratio to BI directly (since each additional
         event causes its own BI) and the severity ratio separately
         (since severity affects property damage and BI differently).
```

---

## 5. The Path to Closing the Gap

### Short-Term: Expand Hazards Repo BI Coverage

The most defensible path is to add BI computation to the hazards repo
for the hazards LTRisk can project:

```
Add to hazards repo:
  Heat Wave:      forced_outage_hours (from inverter specs),
                  recovery_hours = 0 (no physical damage)
  Riverine Flood: already has EAL, add BI decomposition
  Ice Storm:      already has EAL + damage curve, add BI decomposition
  Wildfire:       already has EAL, add BI decomposition

Once hazards repo has baseline_BI for these:
  Additional_BI = baseline_BI × HCR (Scenario A, clean)
```

### Medium-Term: Redefine HCR to Compute BI Directly

For hazards where we have daily CMIP6 data, LTRisk can compute
BI-specific damage functions:

```
For heat wave:
  D_BI(tasmax) = lost_generation(tasmax) × hourly_revenue
  
  This gives baseline_BI AND future_BI from the same CMIP6 data.
  HCR = (future_BI - baseline_BI) / baseline_BI
  Additional_BI = baseline_BI × HCR
  
  Self-consistent: both baseline and delta come from the same framework.
  Cross-validate against hazards repo BI when it becomes available.
```

### Long-Term: Full Pipeline Integration

```
For each canonical hazard:

  1. Hazards repo provides: baseline_BI (historical, from NOAA events)
  2. LTRisk provides: HCR (climate change damage ratio, captures freq+severity)
  3. Combined: future_BI = baseline_BI × (1 + HCR)
  4. Additional_climate_BI = baseline_BI × HCR
  5. Feed into CFADS: subtract Additional_climate_BI from cash flow
  
  For hazards where LTRisk can't compute HCR (hail, tornado):
    future_BI = baseline_BI (assume no climate change, document gap)
  
  For hazards where hazards repo doesn't have BI yet:
    Option C2 (expand hazards repo) or C3 (compute BI in LTRisk)
```

---

## 6. How HCR Is Computed (Redefined)

### The Damage Convolution

```
For each canonical hazard, with damage function D(intensity):

  annual_damage = Σ_days D(intensity(day))
  
  baseline_damage = mean across baseline years
  future_damage   = mean across future years
  
  HCR = (future_damage - baseline_damage) / baseline_damage
```

### Where Do Damage Functions Come From?

```
The hazards repo already has damage functions for most hazards:

  Hail (solar):     Thirza et al. 2024 — hail diameter → loss ratio
  Tornado:          Feuerstein et al. 2010 — wind speed → loss ratio
  Strong Wind:      Unanwa et al. — wind speed → loss ratio
  Ice Storm:        PNNL-33587 — ice accumulation → loss ratio
  Wildfire:         First Street 2023 — flame length → loss ratio
  Hurricane:        PNNL/Climada — wind speed → loss ratio
  Riverine Flood:   HAZUS/JRC — flood depth → loss ratio
  Winter Weather:   Ederen et al. 2024 — severity index → loss ratio
  
  IMPORTANT: These are TOTAL DAMAGE functions (property + BI + indirect).
  They are NOT BI-specific damage functions.
  
  To compute HCR for BI specifically, we would need:
    D_BI(intensity) = BI portion of total damage at that intensity
    
  Gen.1: Use total damage functions. Apply resulting HCR to BI.
         Document the linearity assumption (Section 4).
  Gen.2: Develop BI-specific damage functions per hazard.

  For heat wave: NO damage function exists in the hazards repo.
    LTRisk can define D_BI(tasmax) from inverter derating/shutdown curves.
    This is BI-specific by nature (heat doesn't cause property damage).
```

### Implementation Phases

```
PHASE 1 — Diagnostic (zero code change):
  Alongside current HCR (event count), compute from daily data:
    Mean Excess: E[X - T | X > T] baseline vs future
    "Events are 2.3°C hotter above the threshold on average"
  Report both for comparison. Does not replace HCR yet.

PHASE 2 — Redefined HCR:
  Apply D(intensity) to daily data:
    HCR = (mean future_damage - mean baseline_damage) / mean baseline_damage
  Uses hazards repo damage functions where available.
  Defines new D_BI(tasmax) for heat wave.

PHASE 3 — Full pipeline:
  Additional_climate_BI(hazard, t) = baseline_BI(hazard) × HCR(hazard, t)
  baseline_BI from hazards repo (expanded to cover all 10 hazards)
  HCR from LTRisk (redefined, captures freq + severity)
```

---

## 7. The Complete CFADS Formula (Honest Version)

```
CFADS_adjusted(t) = Revenue(t) × (1 - EFR(t))
                    - baseline_BI_total
                    - Σ_hazards [baseline_BI_h × HCR_h(t)]
                    - OpEx(t)

Where:
  Revenue(t) × (1 - EFR(t))     = generation adjusted for climate degradation
  baseline_BI_total               = sum of historical BI from hazards repo
  baseline_BI_h × HCR_h(t)       = ADDITIONAL climate-driven BI per hazard
  OpEx(t)                         = operating expenses

CURRENTLY AVAILABLE:
  Revenue(t):        Known (from asset model)
  EFR(t):            Computed (NB04b — Peck's + Coffin-Manson)
  OpEx(t):           Known (from financial model)
  
  baseline_BI_total: PARTIALLY known
    Hail + Tornado + Strong Wind: computed by hazards repo
    Heat + Flood + others: NOT YET COMPUTED (gap)
  
  HCR_h(t):          PARTIALLY computable
    Heat + Flood + Ice + Wildfire: from CMIP6 (LTRisk can do)
    Hail + Tornado: BLOCKED (can't project from CMIP6)
    Hurricane + Coastal Flood: from published external data

  → The formula is complete IN STRUCTURE.
  → The data to fill it is PARTIALLY available.
  → Closing the gap requires expanding hazards repo BI coverage
    OR computing baseline BI within LTRisk.
```

---

## 8. What About EFR?

EFR stays exactly as-is. Unchanged by the HCR redefinition.

```
HCR (redefined):  Change in expected DAMAGE from hazard EVENTS
  Mechanism:      Events cause operational shutdown/curtailment
  Financial:      Additional_BI = baseline_BI × HCR

EFR (unchanged):  Acceleration of equipment DEGRADATION rate
  Mechanism:      Continuous climate stress ages equipment faster
  Financial:      climate_degrad = EFR × std_degrad × t + IUL truncation

THEY DON'T OVERLAP:
  HCR: "the plant was shut down for 4 hours during a heat event"
  EFR: "the panels aged 11% faster this year from sustained heat"
  
  One is about discrete EVENTS (temporary).
  The other is about continuous STRESS (permanent).
```

---

## 9. Open Questions

1. **Heat wave baseline BI:** Neither pipeline computes it today. Should the
   hazards repo add forced_outage_hours for heat (Option C2)? Or should
   LTRisk define D_BI(tasmax) independently (Option C3)?

2. **Linearity assumption tolerance:** How wrong is the assumption that
   BI ∝ total damage? For heat wave, it may dramatically UNDERESTIMATE
   BI change (since heat BI is mostly shutdown hours, not property damage).
   For hail, it may OVERESTIMATE. Is this acceptable for Gen.1?

3. **BI-specific damage functions:** Do we need D_BI(intensity) separate
   from D_total(intensity)? For Gen.1, probably not — the linearity
   assumption is documented. For Gen.2, yes — especially for heat wave.

4. **Phase 1 timing:** Adding Mean Excess diagnostic requires zero code
   change. Should we do this immediately in NB04a?

5. **The non-overlap problem:** The two pipelines cover different hazards.
   The clean formula only works when both pieces (baseline_BI + HCR) exist
   for the same hazard. What's the fastest path to overlap?
   a) Expand hazards repo to cover heat/flood/ice BI
   b) Use NRI EAL proxy with linearity assumption
   c) Compute baseline_BI in LTRisk from CMIP6 historical data

---

## 10. Gen.1 Assumptions — "Good Enough" and How to Improve

Every Gen.1 assumption below is documented, defensible for a first pass,
and has a concrete path to resolution.

```
#  ASSUMPTION                     WHY "GOOD ENOUGH"              PATH TO RESOLUTION
─  ─────────────────────────────  ─────────────────────────────  ─────────────────────────────

1  BI changes proportionally      For most hazards, BI and       Develop BI-specific damage
   to total damage                total damage move in the       functions D_BI(intensity)
   (linearity: BI ∝ EAL)         same direction. The ratio      per hazard. For heat wave:
                                  may shift 20-50% but not       D_BI is purely shutdown hours
                                  change sign. Order of          (no property damage), so
                                  magnitude is preserved.        compute directly from derating
                                                                 curve — bypasses assumption.

2  Severity stays constant        For heat wave and flood,       Redefine HCR using damage
   within old HCR                 frequency is the dominant      function D(intensity) applied
   (old HCR = frequency only)     signal (~70% of change).       to daily data (Phase 2).
                                  Missing severity adds           Same Pathway B loop, different
                                  ~30-50% underestimate,         function. Computationally
                                  not order of magnitude.        trivial once D is defined.
                                  Exception: hurricane/wildfire
                                  where severity dominates.

3  Damage functions from          These are published, peer-     Calibrate against InfraSure
   hazards repo are correct       reviewed curves (Thirza,       field data. The hazards repo
   for our asset types            HAZUS, Unanwa). They're        already has subsystem-level
                                  the best available. Used by    decomposition and stow-angle
                                  the entire insurance industry. adjustments for solar.

4  CMIP6 models adequately        28-model ensemble reduces      Cross-validate against ERA5
   represent future climate       individual model bias.         reanalysis for the baseline
                                  NEX-GDDP is bias-corrected    period (1985-2014). SCVR
                                  and downscaled. This is the    Report Card already flags
                                  standard for climate risk.     model disagreement via IQR.

5  Hazards with no HCR            For hail and tornado:          For hail: literature suggests
   (blocked from CMIP6)           the historical frequency IS    damage likely increases
   use HCR = 0                    the best estimate when we      (larger stones). Flag as
                                  can't project. This is         directional estimate from
                                  conservative for hazards       Raupach 2021. For tornado:
                                  where risk is increasing.      genuinely unknown.

6  NRI EAL used as proxy          NRI EAL is the most            Expand hazards repo BI
   for baseline BI where          comprehensive public dataset   methodology to cover heat,
   hazards repo BI doesn't        for hazard losses. BI is a     flood, ice, wildfire.
   exist (Scenario C1)            fraction of EAL (~10-40%       Once available, replace
                                  depending on hazard). Using    NRI proxy with actual BI.
                                  EAL × estimated BI_fraction
                                  gets order of magnitude.

7  Published scaling factors      2.5× for heat wave is from     Cross-validate at every site
   (e.g., 2.5× for heat wave)    PNAS (Diffenbaugh 2017).       using Pathway B direct
   apply at our specific sites    Global/regional average may    counting. Hayhurst: implied
                                  differ from site-specific.     scaling 2.7× (within 8%).
                                  Cross-validation addresses     Expand to Maverick and
                                  this.                          future sites.

8  The "fewer but fiercer"        Using published consensus      Phase 2: compute CIR with
   pattern for hurricane is       (Knutson 2020) is standard.    wind-damage power law to
   adequately captured by         For inland TX sites,           capture nonlinear intensity
   published scaling              hurricane exposure is low       effect. Phase 3: Emanuel-
                                  regardless. Matters more       style synthetic TC
                                  for coastal assets.            downscaling.

9  Three-year anchor linear       For temperature-driven         Phase 2: test nonlinear fits
   fit for annual HCR             hazards (R² > 0.97), linear   (quadratic through 6 anchors).
   interpolation                  is excellent. For precip       For precipitation: report
                                  (R² = 0.59), period-average   decade values only, don't
                                  is used instead.               interpolate.

10 EFR and HCR are independent   Physically different            Phase 2: check for
   channels — no interaction      mechanisms (continuous stress   interaction effects.
                                  vs discrete events). A heat    Example: does faster aging
                                  event doesn't make panels      (EFR) make panels MORE
                                  age AND shut down as one       vulnerable to hail (HCR)?
                                  combined effect in the model.  Likely second-order.
```

---

## Key References

| Paper | Finding | DOI |
|-------|---------|-----|
| Mendelsohn et al. 2012 | Hurricane damage scales V^3 to V^9 | [doi:10.1038/nclimate1357](https://doi.org/10.1038/nclimate1357) |
| Prahl et al. 2016 | Damage function framework for climate hazards | [doi:10.5194/nhess-16-1189-2016](https://doi.org/10.5194/nhess-16-1189-2016) |
| Knutson et al. 2020 | Hurricane: fewer but fiercer | [doi:10.1175/BAMS-D-18-0194.1](https://doi.org/10.1175/BAMS-D-18-0194.1) |
| WTW 2023 | Freq-severity adjustments underestimate tail risk | [wtwco.com](https://www.wtwco.com/en-us/insights/2023/06/why-relying-on-frequency-severity-adjustments-could-underestimate-your-tail-risk-from-climate-change) |
| Swiss Re sigma 2025 | NatCat: both frequency AND severity rising | [swissre.com](https://www.swissre.com/institute/research/sigma-research/sigma-2025-01-natural-catastrophes-trend.html) |
| npj CAS 2024 | Hailstone size dichotomy | [doi:10.1038/s41612-024-00728-9](https://doi.org/10.1038/s41612-024-00728-9) |
| Abatzoglou & Williams 2016 | Wildfire area doubled | [doi:10.1073/pnas.1607171113](https://doi.org/10.1073/pnas.1607171113) |
| Hsiang et al. 2017 | US climate damage functions by sector | [doi:10.1126/science.aal4369](https://doi.org/10.1126/science.aal4369) |

## Cross-References

| Topic | Doc |
|-------|-----|
| Top-down canonical hazard reframe | [hcr_top_down_reframe.md](hcr_top_down_reframe.md) |
| Pipeline complementarity | [pipeline_complementarity.md](../architecture/pipeline_complementarity.md) |
| BI methodology foundations | [01_what_is_bi.md](../bi_methodology/01_what_is_bi.md) |
| HCR methodology (current) | [07_hcr_hazard_change.md](../../learning/C_financial_translation/07_hcr_hazard_change.md) |
| EFR methodology (unchanged) | [08_efr_equipment_degradation.md](../../learning/C_financial_translation/08_efr_equipment_degradation.md) |
