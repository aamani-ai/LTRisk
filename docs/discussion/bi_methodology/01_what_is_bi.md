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

Business Interruption (BI) is **revenue lost because the asset could not
produce electricity during a period when it otherwise would have.**

```
BI = Revenue_expected - Revenue_actual

  Revenue_expected = what the asset WOULD have produced (no event)
  Revenue_actual   = what the asset DID produce (during/after event)
  
  BI is always measured in DOLLARS LOST.
  It is always tied to a TIME PERIOD of lost production.
  It is always caused by a SPECIFIC EVENT or CONDITION.
```

### What BI IS

- Revenue lost because inverters shut down during a heat wave (hours)
- Revenue lost because panels are being replaced after hail (weeks)
- Revenue lost because the site is flooded and inaccessible (days)
- Revenue lost because blades are iced over and turbine is stopped (hours)
- Revenue lost because grid operator curtails output during extreme demand (hours)

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

### The Bright Line Test

```
Can the asset physically produce electricity RIGHT NOW?

  YES, but it's not → BI (something is stopping it)
  YES, and it is     → Not BI (may be performance loss, but not interruption)
  NO, permanently    → Asset damage / end-of-life (EFR territory)
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

## 7. Open Questions

1. **Partial operation during Category A repair:** If 22% of panels are
   being replaced, does the plant run at 78% capacity? Or does the repair
   disrupt adjacent sections too? The hazards repo assumes the damaged
   fraction produces $0. Is that right?

2. **Curtailment derating vs full shutdown:** Heat wave curtailment — does
   the inverter shut down completely (0% output) or derate to 50%? This
   changes the BI calculation significantly.

3. **Revenue rate timing:** Should BI use average annual hourly revenue
   (simple, current approach) or seasonal hourly revenue (more accurate,
   needs hourly price data)? Summer heat BI is worth 3-4x more than
   winter equivalent.

4. **Minimum threshold for BI:** The hazards repo uses `BI_MIN_DAMAGE_PCT
   = 10%`. Below 10% damage, no BI is computed. Should curtailment (Cat B)
   and environmental (Cat C) have similar thresholds? E.g., "less than
   2 hours of heat curtailment per event → no BI."

5. **Insurance vs self-insured losses:** Category A BI is typically insured
   (business interruption insurance covers lost revenue during repair).
   Categories B and C are typically NOT insured (curtailment, soiling).
   Does this distinction matter for how we model them?

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
