---
title: "Discussion — What Is Business Interruption? Definitions, Boundaries, and Mechanisms"
type: discussion
domain: climate-risk / business-interruption / foundations
created: 2026-04-02
status: draft — foundational definitions for BI modeling
context: >
  Before building a BI model, we need to define what BI is, what it isn't,
  and how different types of events cause it through different mechanisms.
  This is the first of a series of BI methodology discussions that establish
  the conceptual foundation before any calculation is attempted.
relates-to:
  - docs/discussion/hcr_financial/hcr_efr_boundary.md
  - docs/discussion/architecture/pipeline_complementarity.md
  - docs/learning/C_financial_translation/06b_climate_risk_orchestrator.md
  - docs/discussion/hcr_financial/channel_1_bi_calculation.md
---

# What Is Business Interruption?

> **Before we calculate anything, we need to agree on what we're calculating.**

---

## 1. Definition

Business Interruption (BI) is **revenue lost because the asset produced
less electricity than it would have without the event.**

BI is NOT a binary on/off. A hail-damaged solar farm doesn't go to zero —
78% of panels may be fine while 22% are being replaced. The plant produces
at reduced capacity during recovery. BI is the GAP between expected and
actual production over time:

```
BI = ∫ [capacity_expected(t) - capacity_actual(t)] × price(t) dt

  capacity_expected(t) = what the plant WOULD produce (no event)
  capacity_actual(t)   = what the plant DOES produce (during/after event)
  price(t)             = revenue per MWh at time t
  
  BI = the area between the two curves, converted to dollars.
```

```
PRODUCTION DURING A HAIL RECOVERY (22% damage)

  Output (%)
  100 │████████████████████████████████████████████████████████████ Expected
      │
   90 │                    ╭────────────────────────── Actual
      │               ╭────╯
   80 │          ╭────╯      ← Gradual recovery as panels replaced
      │     ╭────╯
   78 │─────╯ ← Immediate: 22% of panels offline, 78% still producing
      │
      │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ← Shaded area = BI
      │
      └───────────────────────────────────────────────────────────────
      Event   Week 2    Week 4    Week 6    Week 8    Week 10   Restored

  BI = shaded area × price(t)
  NOT: "plant at 0% for X hours"
  BUT: "plant at (100% - loss%) for Y weeks, loss% decreasing over time"
```

### Three Levels of Modeling This (Complexity vs Accuracy)

```
LEVEL 1 — Binary (simplest, current hazards repo approach)
  BI = damage% × full_recovery_hours × hourly_revenue
  Assumes: damaged fraction produces $0, undamaged produces 100%
  Accuracy: ±30-50% (overestimates for partial damage, underestimates for
            cascading failures)
  Good enough for: Gen.1 screening, order-of-magnitude estimates
  
LEVEL 2 — Linear Recovery Curve (moderate complexity)
  BI = ∫₀ᵗʳ [damage%(1 - s/t_r)] × capacity × price ds
  Assumes: output loss starts at damage% and linearly recovers to 0
  Accuracy: ±15-25% (better shape, still assumes linear)
  Good enough for: Gen.1 production model, annual BI estimates

LEVEL 3 — Empirical Recovery Profile (most accurate)
  BI = ∫₀ᵗʳ loss_profile(s) × capacity × price(s) ds
  Where loss_profile is fitted from actual O&M recovery data:
    Week 1-2: ~damage% (assessment, ordering parts)
    Week 3-6: ~damage%×0.7 (partial replacement underway)
    Week 7-10: ~damage%×0.3 (most sections restored)
    Week 11+: ~damage%×0.05 (punch list, commissioning)
  Accuracy: ±5-10%
  Good enough for: Gen.2 when O&M data is available

RECOMMENDATION:
  Gen.1: Level 1 (binary) for Category A damage events
         Level 2 for Category B curtailment (hours, not weeks)
  Gen.2: Level 2 or 3 when recovery profile data exists
```

### What BI IS

- Revenue lost because inverters shut down during a heat wave (hours, partial)
- Revenue lost because panels are being replaced after hail (weeks, partial — 78% still runs)
- Revenue lost because the site is flooded and inaccessible (days, near-total)
- Revenue lost because blades are iced over and turbine is stopped (hours, full shutdown)
- Revenue lost because grid operator curtails output during extreme demand (hours, partial)

### What BI is NOT

- **Equipment degradation** — panels producing 1% less per year because
  they aged faster. This is gradual, permanent, cumulative. This is EFR
  (Channel 2), not BI. The plant IS producing — just less efficiently.

- **Performance loss from normal weather** — a cloudy week reduces solar
  output. This is weather variability, not BI. It's already in the
  generation model's P10-P90 range.

- **Market/price risk** — electricity price drops. The plant IS producing
  at full capacity, but revenue is lower. This is market risk, not BI.

- **OpEx increase** — maintenance costs go up. The plant IS producing.
  This is a cost increase, not revenue loss from interrupted production.

### The Boundary Test — Spectrum, Not Binary

```
Instead of a hard "is it BI or not?" we recognize a spectrum:

  CLEARLY BI                    GREY AREA                 CLEARLY NOT BI
  ──────────                    ─────────                 ──────────────
  Inverter full                 Heat derating             Peck's thermal
  shutdown (0%)                 (output at 90%)           aging (1%/yr
                                                          permanent loss)
  
  Site flooded,                 Cracked panel still       Cloudy week
  inaccessible (0%)            producing at 85%          (normal weather)
  
  Turbine blade                 Light icing, turbine      Wind SCVR ≈ 0
  destroyed (0%)               at 60% output             (no change)

  Grid curtailment             Dust soiling at           Electricity price
  to 0% (forced)               -3% after dry spell       drops (market)

FOR EACH GREY AREA, WE NEED A DECISION:

  Option A: Include with a threshold
    "Derating below 90% = BI. Above 90% = normal variability."
    
  Option B: Include all as partial BI
    "Any output reduction from a climate event = BI, scaled by magnitude."
    
  Option C: Exclude from BI, capture elsewhere
    "Derating is performance loss, modeled in generation. Only full
     shutdown events are BI."

  Gen.1 recommendation: Option A with conservative thresholds.
  Gen.2: Option B with continuous production-loss curves.
```

---

## 2. How BI Differs from EFR

This is the boundary established in [hcr_efr_boundary.md](../hcr_financial/hcr_efr_boundary.md), but it's worth restating from the BI perspective:

```
                    BI (Channel 1)              EFR (Channel 2)
                    ──────────────              ───────────────
Mechanism:          Production STOPPED          Production REDUCED
Duration:           Hours to months             Permanent (cumulative)
Reversibility:      Yes (plant resumes)         No (damage accumulates)
Cause:              Specific event              Continuous stress
Financial math:     SUBTRACTED from CFADS       MULTIPLIED on generation
                    (additive loss)             (rate of decline)
Examples:           Heat shutdown (4 hrs)        Peck's aging (+9%/yr)
                    Hail repair (3 months)       Coffin-Manson fatigue
                    Flood access (5 days)        Palmgren-Miner wear

KEY TEST:
  Does the plant RESUME normal operation after the cause passes?
    YES → BI (temporary interruption)
    NO  → EFR (permanent degradation)
```

### The Grey Area: Hail

Hail is interesting because it causes BOTH:
- **BI**: Plant operates at reduced capacity during 3-month repair → BI
- **Damage**: Panels physically broken → replacement cost (not BI, it's CapEx)

The hazards repo BI methodology captures the BI portion (lost revenue
during repair). The replacement cost is a separate insurance claim.

LTRisk doesn't model replacement cost — only revenue impact. So for
our purposes, hail BI = lost revenue during recovery period. The physical
damage cost is out of scope (insurance covers it).

---

## 3. Categories of Events That Cause BI

Not all events cause BI the same way. We identify **three distinct
mechanisms** through which an event can interrupt production:

### Category A: Damage-Driven BI

```
WHAT HAPPENS:
  Physical impact damages equipment
  → Equipment needs repair or replacement
  → Plant operates at reduced capacity during repair
  → Revenue lost = repair_duration × lost_capacity × revenue_rate

CHARACTERISTICS:
  - Damage is PHYSICAL and VISIBLE
  - Recovery takes WEEKS to MONTHS
  - Severity scales with event magnitude (bigger hail = more damage)
  - Plant may partially operate during repair (undamaged sections)
  - Insurance claim typically involved

EXAMPLES:
  Hail:         Cracks panels → 3-month replacement cycle
  Tornado:      Destroys structure → 2-6 month rebuild
  Strong Wind:  Displaces panels/blades → 2-6 month repair
  Hurricane:    Wind + surge compound damage → months

DATA NEEDED FOR MODELING:
  - Event frequency (how often does it happen at this site?)
  - Event magnitude (how big was the hail / how fast the wind?)
  - Damage curve (magnitude → % of asset damaged)
  - Recovery time (how long to repair at that damage level?)
  - Revenue during repair (partial operation or full shutdown?)

WHO HAS THIS DATA:
  ✅ Hazards repo: NOAA events, spatial frequency, damage curves, recovery hours
  ⚠️ LTRisk: Limited — can project some frequency changes via HCR but
     not the damage curves or recovery times
```

### Category B: Curtailment-Driven BI

```
WHAT HAPPENS:
  Environmental conditions force operational limits
  → Safety systems or grid operator curtail output
  → Plant is physically fine but can't produce
  → Revenue lost = curtailment_hours × lost_capacity × revenue_rate

CHARACTERISTICS:
  - NO physical damage
  - Duration is HOURS to DAYS (short)
  - Ends when conditions pass (temperature drops, ice melts, smoke clears)
  - Plant resumes FULL operation afterward
  - No insurance claim (operational, not damage)

EXAMPLES:
  Heat wave:     Inverter thermal protection → 2-6 hrs shutdown per event
  Icing:         Blade/panel ice → hours until melting
  Wildfire smoke: Reduced irradiance → days of lower output
  Grid curtailment: Operator reduces output during extreme demand/supply

DATA NEEDED FOR MODELING:
  - Number of curtailment hours per year (historical or projected)
  - Capacity during curtailment (full shutdown vs partial derating)
  - Revenue rate during curtailment period (seasonal variation matters)

WHO HAS THIS DATA:
  ✅ LTRisk: CMIP6 daily data can count threshold exceedances
     (hours where tasmax > inverter cutoff, hours where tasmin < 0 AND hurs > 90%)
  ⚠️ Hazards repo: Heat Wave in HAZARDS list but no curtailment model yet
```

### Category C: Access/Environmental BI

```
WHAT HAPPENS:
  Site conditions prevent operation or maintenance
  → Not physical damage to equipment
  → But plant can't operate or be maintained
  → Revenue lost = affected_period × output_reduction × revenue_rate

CHARACTERISTICS:
  - Equipment may be FINE but unreachable
  - Duration is DAYS to WEEKS
  - May require cleanup/drying before restart
  - Partial operation sometimes possible

EXAMPLES:
  Flooding:      Site submerged → can't access, electrical risk → days
  Snow cover:    Panels buried → reduced output until cleared → days
  Dust/soiling:  Gradual buildup during dry spell → progressive loss
  Post-fire:     Site evacuated for safety → days to weeks

DATA NEEDED FOR MODELING:
  - Number of affected days per year
  - Output reduction during affected period
  - Time to resume normal operations after conditions clear

WHO HAS THIS DATA:
  ✅ LTRisk: CMIP6 Rx5day for flood events, dry spell length for soiling
  ⚠️ Hazards repo: Flood/Flash Flood in HAZARDS but limited BI methodology
```

---

## 4. Which Hazards Cause Which Type of BI?

Mapping InfraSure's canonical hazards to BI categories:

```
HAZARD              CAT A          CAT B           CAT C          NOT BI
                    (Damage)       (Curtailment)   (Access/Env.)  (→ EFR)
═══════════════     ══════════     ═════════════   ═════════════  ════════
Hail                ✅ Primary      —               —              —
Tornado             ✅ Primary      —               —              —
Strong Wind         ✅ Primary      —               —              —
Hurricane           ✅ Primary      —               ✅ surge/flood  —
Heat Wave           —              ✅ Primary       —              —
Ice Storm           ✅ if damage    ✅ if temporary  —              —
Winter Weather      —              —               ✅ snow cover   —
Wildfire            ✅ if fire      ✅ smoke only    ✅ evacuation   —
Riverine Flood      —              —               ✅ Primary      —
Coastal Flood       —              —               ✅ Primary      —
Drought/Dry Spell   —              —               ✅ soiling      —

NOT BI (→ EFR Channel 2 instead):
  Thermal aging     —              —               —              ✅ Peck's
  Freeze-thaw       —              —               —              ✅ Coffin-M
  Wind fatigue      —              —               —              ✅ Palmgren
  Lightning         ✅ if damage    —               —              —
  Earthquake        ✅ if damage    —               —              —
```

### Some Hazards Fall in Multiple Categories

**Ice Storm** can be:
- Category A: Heavy ice accumulation damages panels/blades → repair weeks
- Category B: Light icing forces turbine shutdown → resumes when ice melts (hours)
- Depends on severity: light icing = B, heavy icing = A

**Wildfire** can be:
- Category A: Fire physically burns equipment → repair months
- Category B: Smoke reduces irradiance → days of lower solar output
- Category C: Site evacuated → days of zero production
- All three can happen in sequence from a single fire event

**Hurricane** can be:
- Category A: Wind damages structure → repair months
- Category C: Storm surge floods site → days/weeks to dry + restart
- Both happen simultaneously from the same event

The model should handle multi-category events by summing the BI from
each mechanism (with a cap to avoid double-counting overlapping hours).

---

## 5. What Determines BI Severity?

For each category, different factors drive how bad the BI is:

```
CATEGORY A (Damage):
  Severity = f(magnitude, damage_curve, recovery_time, partial_operation)
  
  Key driver: HOW MUCH was damaged?
  Secondary: How FAST can we repair? (supply chain, crew availability)
  Tertiary: Can the undamaged part keep running? (partial operation)

CATEGORY B (Curtailment):
  Severity = f(number_of_hours, capacity_during_curtailment, revenue_rate)
  
  Key driver: HOW MANY HOURS was the plant curtailed?
  Secondary: Was it full shutdown or partial derating?
  Tertiary: What was the electricity worth during those hours?
            (summer afternoon >> winter night)

CATEGORY C (Access/Environmental):
  Severity = f(affected_days, output_reduction, time_to_resume)
  
  Key driver: HOW MANY DAYS was the site affected?
  Secondary: Could it still produce partially? (flooded but elevated panels?)
  Tertiary: How long to restart after conditions clear?
```

---

## 6. Why This Framework Matters for LTRisk

### It Tells the Orchestrator What to Route Where

```
Orchestrator receives: "tasmax crossed P90 for 3 consecutive days"

Step 1: Which hazard? → Heat Wave
Step 2: Which BI category? → Category B (Curtailment)
Step 3: What mechanism? → Inverter thermal shutdown
Step 4: What data? → Count curtailment hours from daily CMIP6 data
Step 5: What formula? → curtailment_hrs × derated_capacity × seasonal_revenue
Step 6: Which channel? → Channel 1 (BI) — temporary, reversible
```

### It Tells Us What Data We Need Per Hazard

```
Category A hazards → Need: damage curves, recovery times, spatial frequency
                     Source: Hazards repo (has these for hail, tornado, wind)

Category B hazards → Need: curtailment hour counts, derating factors
                     Source: LTRisk CMIP6 daily data (can count these)

Category C hazards → Need: affected day counts, output reduction factors
                     Source: LTRisk CMIP6 + site characteristics
```

### It Defines What Gen.1 Can Cover

```
GEN.1 (buildable now):
  Category A: USE hazards repo output for hail/tornado/wind
  Category B: BUILD from CMIP6 data for heat wave and icing
  Category C: PARTIAL for flooding (Rx5day), FLAG for soiling/wildfire

GEN.2 (needs more data):
  Category A: Add climate adjustment (HCR × baseline frequency)
  Category B: Add seasonal revenue weighting
  Category C: Add wildfire smoke model, snow cover model
  Cross-category: Compound event interaction (heat + drought + fire)
```

---

## 7. Grey Areas — Design Decisions Needed

Each grey area has options ranging from simple (Gen.1) to complex (Gen.2).
The choice affects what gets counted as BI and what doesn't.

### Grey Area 1: Cracked Panels Still Producing

```
Hail cracks a panel but doesn't kill it. It produces at ~85%.

  Option A (Gen.1 simple): Count as damaged. BI = damage% × recovery × revenue.
    Ignore partial production from cracked panels.
    Overestimates BI slightly (cracked panels DO produce something).
    
  Option B (Gen.1 better): BI = (damage% - partial_output%) × recovery × revenue.
    Cracked panels produce at 85% → effective loss = damage% - 0.15×damage% = 0.85×damage%
    Needs: partial output factor per damage level.
    
  Option C (Gen.2): Track individual panel status over time.
    Some cracked, some replaced, some fine. Production profile is a curve.
    Needs: O&M data on real recovery trajectories.

  RECOMMENDATION: Option A for Gen.1 (simple, conservative).
```

### Grey Area 2: Heat Derating vs Heat Shutdown

```
Temperature rises through the day:
  35°C: panels at ~98% (minor derating) — is this BI?
  45°C: panels at ~92% (noticeable derating) — is this BI?
  55°C: panels at ~85% (significant derating) — is this BI?
  65°C: inverter trips, 0% output — clearly BI

  Option A (Gen.1 simple): Only count full shutdowns (>65°C).
    BI = shutdown_hours × full_capacity × revenue.
    Misses the derating losses (which are real but smaller).
    
  Option B (Gen.1 moderate): Count derating above a threshold.
    BI = hours_above_45°C × (capacity_expected - capacity_derated) × revenue.
    Threshold at 45°C (or whatever temperature causes >5% derating).
    Needs: temperature-derating curve for this panel type.
    
  Option C (Gen.2): Continuous integration over temperature curve.
    BI = ∫ [capacity(T_expected) - capacity(T_actual)] × price(t) dt
    Uses hourly temperature from CMIP6 or ERA5 through PVLib.
    Most accurate but requires sub-daily data.

  RECOMMENDATION: Option B for Gen.1. We have daily tasmax from CMIP6
  and can estimate hours above threshold. Captures most of the signal.
```

### Grey Area 3: Soiling — Gradual vs Event-Driven

```
Dust accumulates during 60-day dry spell:
  Day 1:  -0.1% output
  Day 30: -2% output
  Day 60: -5% output
  Rain:   back to ~100%

  Option A: NOT BI. It's gradual performance loss, like weather variability.
    Model in generation forecast, not BI.
    Simplest. Consistent with "BI = specific event caused it."
    
  Option B: BI only when soiling crosses a threshold (e.g., >3%).
    Below 3%: normal maintenance handles it (not BI).
    Above 3%: exceptional soiling from climate-driven dry spell = BI.
    
  Option C: BI when cleaning is triggered and causes downtime.
    The soiling itself isn't BI. But if the O&M team does emergency
    cleaning and takes sections offline, THAT downtime = BI.

  RECOMMENDATION: Option A for Gen.1 (exclude soiling from BI).
  Soiling is better handled as a performance adjustment in the
  generation model, not as business interruption.
```

### Grey Area 4: Climate-Related vs Market-Related Grid Curtailment

```
Grid operator curtails output:
  Case 1: Extreme heat → everyone's AC on → grid stressed → curtailment
  Case 2: Sunny afternoon → too much solar → negative pricing → curtailment

  Option A: ALL curtailment is out of scope (it's market risk, not climate risk).
    Simplest. Consistent with "BI = physical event."
    
  Option B: Climate-correlated curtailment = BI. Market curtailment = out.
    Heat-driven curtailment IS climate risk (warming → more extreme demand).
    Oversupply curtailment is market structure (not climate).
    Needs: way to distinguish the two (correlation with temperature?).
    
  Option C: All curtailment in scope, weighted by climate attribution.
    "30% of this curtailment was caused by climate-driven demand."
    Most accurate. Most complex. Needs: attribution model.

  RECOMMENDATION: Option A for Gen.1 (exclude grid curtailment).
  It's real revenue loss but hard to attribute to climate vs market.
  Revisit in Gen.2 when grid modeling is available.
```

### Grey Area 5: Cascading Events (Heat → Drought → Fire)

```
Connected sequence over weeks:
  Heat wave → drought → wildfire → smoke → evacuation → fire damage

  Option A (Gen.1): Model each mechanism independently.
    Heat derating = Category B BI (hours)
    Fire damage = Category A BI (months)
    Don't attribute the fire to the heat wave.
    Simple. May undercount (misses compounding).
    
  Option B: Track the cascade, attribute downstream BI to root cause.
    "This $500K fire BI was ultimately caused by the heat wave."
    More informative for risk management.
    But: attribution is subjective and debatable.
    
  Option C (Gen.2): Conditional probability model.
    P(fire | drought AND high_FWI) × E[BI | fire]
    Captures the cascade probabilistically.
    Needs: conditional event data.

  RECOMMENDATION: Option A for Gen.1. Model each mechanism independently.
  The total BI is the sum. Don't try to trace causal chains yet.
```

---

## 8. Summary: Gen.1 vs Gen.2 Roadmap

```
                            GEN.1                       GEN.2
                            (build now)                 (when data allows)
                            ─────────────               ──────────────────
BI DEFINITION:
  Production model          Binary (on/off or %)        Recovery curve
  Threshold for BI          Conservative (clear events) Continuous (any loss)
  Revenue rate              Annual average hourly       Seasonal/hourly

CATEGORY A (Damage):
  Source                    Hazards repo output         Climate-adjusted freq.
  Recovery model            Level 1 (linear)            Level 2-3 (profile)
  Hazards                   Hail, tornado, wind         + hurricane compound

CATEGORY B (Curtailment):
  Source                    CMIP6 daily thresholds      Sub-daily integration
  Derating model            Threshold-based (>45°C)     Continuous temp curve
  Hazards                   Heat wave, icing            + smoke, grid curtail.

CATEGORY C (Environmental):
  Source                    CMIP6 Rx5day counts         + site topography
  Model                    Assumed days per event       Flood depth model
  Hazards                   Flooding (partial)          + snow, soiling

GREY AREAS:
  Cracked panels            Count as damaged (simple)   Partial output model
  Soiling                   Exclude from BI             Threshold-based BI
  Grid curtailment          Exclude (market risk)       Climate-attributed
  Cascading events          Independent mechanisms      Conditional probability

CROSS-PIPELINE:
  Baseline from Haz. repo   Use directly (Cat A)        Validate with O&M
  Climate delta from LTRisk HCR × baseline (where avail) Full integration
  Frequency vs severity     Frequency only (HCR)        Both (HCR + intensity)
```

---

## 9. Open Questions

1. **Partial operation during Category A repair:** If 22% of panels are
   being replaced, does the plant run at 78% capacity? Or does the repair
   disrupt adjacent sections too? The hazards repo assumes the damaged
   fraction produces $0. Gen.1: accept this simplification. Gen.2: model
   partial operation.

2. **Heat derating threshold:** At what temperature does derating become BI?
   45°C? 50°C? This determines how many curtailment hours we count from
   CMIP6 data. Needs input from the engineering team.

3. **Revenue rate timing:** Should BI use average annual hourly revenue
   (simple) or seasonal hourly revenue (more accurate)?
   Gen.1: annual average. Gen.2: seasonal. The difference is 3-4× for
   summer heat events.

4. **Minimum threshold for BI:** The hazards repo uses `BI_MIN_DAMAGE_PCT
   = 10%`. Should curtailment (Cat B) and environmental (Cat C) have
   similar thresholds? E.g., "less than 2 hours of heat curtailment
   per event → no BI."

5. **Insurance perspective:** Category A BI is typically insured.
   Categories B and C are typically NOT. Does this distinction matter
   for how we model them, or is it just a reporting label?

6. **Frequency vs severity under climate change:** LTRisk HCR measures
   frequency change. But climate may also change severity (bigger hail,
   hotter heat waves). Gen.1: scale frequency only. Gen.2: add intensity
   adjustment. How much does this matter quantitatively?

---

## Next in This Series

```
01_what_is_bi.md          ← YOU ARE HERE
02_bi_by_hazard.md        Per-hazard BI modeling (detailed mechanism for each)
03_bi_data_sources.md     What data each category needs, where to get it
04_bi_calculation.md      The actual formulas and worked examples
05_bi_climate_adjustment.md  How HCR adjusts historical baseline forward
```

---

## Cross-References

| Topic | Doc |
|-------|-----|
| Channel 1 BI (current approach) | [channel_1_bi_calculation.md](../hcr_financial/channel_1_bi_calculation.md) |
| HCR/EFR boundary | [hcr_efr_boundary.md](../hcr_financial/hcr_efr_boundary.md) |
| Pipeline complementarity | [pipeline_complementarity.md](../architecture/pipeline_complementarity.md) |
| Orchestrator routing | [06b_climate_risk_orchestrator.md](../../learning/C_financial_translation/06b_climate_risk_orchestrator.md) |
| Hazards repo BI methodology | External: hazards repo `Business_Interruption_Estimation_Methodology.md` |
