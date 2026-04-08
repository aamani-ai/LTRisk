---
title: "Discussion — Pipeline Complementarity: How Hazards Repo BI and LTRisk HCR Work Together"
type: discussion
domain: climate-risk / architecture / integration
created: 2026-04-02
status: draft — foundational integration design, pending team review
context: >
  InfraSure has two pipelines that quantify hazard/climate risk. They cover
  DIFFERENT hazards with almost no overlap. This doc explains what each does,
  where they complement each other, and how they should connect.
relates-to:
  - docs/learning/C_financial_translation/06b_climate_risk_orchestrator.md
  - docs/discussion/hcr_financial/channel_1_bi_calculation.md
  - docs/discussion/hcr_financial/hcr_efr_boundary.md
  - docs/discussion/architecture/framework_architecture.md
---

# Pipeline Complementarity

> **The situation:** InfraSure has two separate pipelines that both quantify
> risk to renewable energy assets. They were built independently and cover
> different hazards. This doc explains how they fit together.

---

## 1. The Two Pipelines — What Each Does

### Pipeline A: Hazards Repo (Historical, Backward-Looking)

```
WHAT IT DOES:
  Takes NOAA storm event records (1996-2024)
  → Counts events near each asset site (spatially adjusted)
  → Applies damage curves (damage % per event magnitude)
  → Computes forced outage hours + recovery hours per event
  → Averages across 29 years
  → Produces: Expected Annual BI in dollars

INPUT:   NOAA Storm Events Database + FEMA NRI
OUTPUT:  Annual BI ($) per hazard per site
PERIOD:  Historical (1996-2024)
HAZARDS: Hail, Tornado, Strong Wind (3 hazards with full BI calc)
```

**The key formula:**
```
Annual BI = Spatial_Frequency × Avg_BI_per_event

Where:
  Avg_BI_per_event = (forced_hours + damage% × recovery_hours) × hourly_revenue
```

### Pipeline B: LTRisk (Forward-Looking, Climate Projections)

```
WHAT IT DOES:
  Takes CMIP6 climate model data (28 models, 2026-2055)
  → Computes SCVR (how much the climate distribution shifted)
  → Computes HCR (how many MORE hazard events per year)
  → Computes EFR (how much FASTER equipment degrades)
  → Translates to NAV impairment

INPUT:   NASA NEX-GDDP-CMIP6 (daily climate data)
OUTPUT:  HCR (% change in hazard frequency), EFR (degradation acceleration)
PERIOD:  Future projections (2026-2055 vs 1985-2014 baseline)
HAZARDS: Heat Wave, Extreme Precip, Flood, Icing (Channel 1 BI)
         Thermal aging, Freeze-thaw fatigue (Channel 2 EFR)
         Wildfire, Dry spell (Risk indicators)
```

---

## 2. What Each Pipeline Covers — The Coverage Map

```
HAZARD              Pipeline A         Pipeline B         Who covers it?
                    (Hazards Repo)     (LTRisk)
════════════════    ════════════════   ════════════════   ═══════════════
Hail                ✅ Full BI          ❌ Gap             A only
Tornado             ✅ Full BI          ❌ Gap             A only
Strong Wind         ✅ Full BI          ⚠️ Proxy           A (main) + B
Heat Wave (BI)      ❌ Not yet          ✅ Full HCR        B only
Extreme Precip      ❌ Not yet          ✅ Full HCR        B only
Icing (BI)          ❌ Not yet          ⚠️ Proxy HCR      B only
Thermal aging       ❌ N/A              ✅ Full EFR        B only
Freeze-thaw         ❌ N/A              ✅ Full EFR        B only
Wildfire            ❌ (NRI EAL only)   ⚠️ FWI proxy      Both (partial)
Riverine Flood      ❌ (NRI EAL only)   ✅ Rx5day HCR     Both (partial)
Coastal Flood       ❌ (NRI EAL only)   ❌ Gap             Neither fully
Hurricane           ✅ Full BI          ❌ Gap             A only
```

**The key observation:** They're almost perfectly complementary.
Pipeline A covers the acute event hazards (hail, tornado, wind).
Pipeline B covers the chronic/climate-shift hazards (heat, degradation).
Very little overlap.

---

## 3. What Each Pipeline Answers — Different Questions

The two pipelines answer fundamentally different questions:

```
PIPELINE A (Hazards Repo) answers:
  "How much does this asset lose PER YEAR to hazard events
   based on HISTORICAL frequency and severity?"

  Example: "Hayhurst loses ~$24K/yr to hail based on
           29 years of NOAA storm records near the site."

  This is the BASELINE — what happens under today's climate.


PIPELINE B (LTRisk) answers:
  "How much will climate change SHIFT hazard frequency
   and equipment degradation over the next 30 years?"

  Example: "Heat wave days increase by 18.5% by 2040 (HCR).
           Panel aging accelerates by 9.4% (EFR)."

  This is the DELTA — how climate change modifies the baseline.
```

**Neither answers the full question alone:**

```
THE FULL QUESTION:
  "What is the TOTAL climate-adjusted annual risk to this asset?"

  = Baseline risk (from Pipeline A) + Climate change delta (from Pipeline B)
  = Historical BI ($)              + Forward HCR/EFR adjustment
```

---

## 4. How They Connect — Three Scenarios

### Scenario 1: Pipeline A has BI, Pipeline B has HCR

*Hazard covered by BOTH pipelines (currently: none fully, but Strong Wind is close)*

```
The ideal combination formula:

  BI_climate_adjusted = BI_baseline_from_A × (1 + HCR_from_B)

Example (hypothetical, if both covered heat):
  Pipeline A: baseline heat BI = $15K/yr (from NOAA events + damage curve)
  Pipeline B: HCR_heat(2040) = +0.185 (18.5% more heat events)

  Climate-adjusted heat BI = $15K × (1 + 0.185) = $17,775/yr
  Additional BI from climate change = $2,775/yr
```

**This is where we want to get for all hazards.** But currently, no hazard
has BOTH a Pipeline A BI calculation AND a Pipeline B HCR projection.

### Scenario 2: Pipeline A has BI, Pipeline B does NOT

*Hazards: Hail, Tornado, Hurricane*

```
Pipeline A gives us: BI_hail = $24K/yr (historical)
Pipeline B gives us: nothing (can't project hail from CMIP6)

What to report:
  "Historical hail BI: $24K/yr based on 1996-2024 NOAA events.
   Climate change projection: NOT AVAILABLE (documented gap).
   Assume no change in frequency for now."

The baseline BI IS the estimate. No climate delta applied.
```

### Scenario 3: Pipeline B has HCR, Pipeline A does NOT

*Hazards: Heat Wave, Extreme Precip, Icing*

```
Pipeline B gives us: HCR_heat(2040) = +0.185 (18.5% more events)
Pipeline A gives us: nothing (no heat BI methodology yet)

The formula needs baseline_BI to scale:
  BI_loss = baseline_BI × HCR = ??? × 0.185 = ???

Without Pipeline A's baseline, we fall back to:
  Option 1: Industry benchmarks (0.5-2.0% of revenue — broad range)
  Option 2: Engineering estimates (shutdown hours × capacity × price)
  Option 3: Wait until Pipeline A adds heat BI methodology

This is the current situation for LTRisk's Channel 1.
```

---

## 5. The Path Forward — Closing the Gaps

### Gap 1: Heat Wave BI in Pipeline A

The hazards repo has Heat Wave in the HAZARDS list but says: *"No
magnitude-based damage curves are in production for these hazards."*

**What's needed to add heat BI to Pipeline A:**
- Forced outage hours for inverter thermal shutdown (e.g., 2-4 hrs/event)
- Recovery hours (likely 0 — heat is performance loss, not physical damage)
- A damage/derating curve: temperature → generation loss %
- NOAA event count for Heat/Excessive Heat at each site

**Once Pipeline A has heat BI:** LTRisk's HCR can scale it forward:
`heat_BI_2040 = heat_BI_baseline × (1 + 0.185)`

### Gap 2: Hail/Tornado HCR in Pipeline B

LTRisk can't project hail or tornado from CMIP6 (requires CAPE, wind shear).

**Options:**
- Accept as a documented gap (current approach)
- Use literature-based trend estimates (e.g., "hail frequency +X% per °C"
  from IPCC AR6) as a crude HCR proxy
- Eventually: use higher-resolution models or ERA5-derived proxies

### Gap 3: Degradation Has No Pipeline A Equivalent

Pipeline A computes BI (operational downtime). LTRisk computes EFR
(equipment aging). These are different financial mechanisms:

```
Pipeline A BI: "The plant was OFF for 466 hours due to hail recovery"
               → Revenue lost during downtime

LTRisk EFR:    "Panels age 9.4% faster due to heat stress"
               → Revenue lost from reduced output + shorter life

These don't overlap. They ADD together in the financial model:
  CFADS_adjusted = Revenue × (1-EFR) - BI_loss_A - BI_loss_B - OpEx
                              ^^^^^^^^   ^^^^^^^^   ^^^^^^^^
                              LTRisk     Pipeline A  LTRisk
                              Channel 2  historical  Channel 1
                                         BI          climate delta
```

---

## 6. The Combined Financial Model

Putting it all together for one asset:

```
HAYHURST SOLAR — TOTAL CLIMATE-ADJUSTED RISK

Source              Hazard           Type        Annual Impact
──────────────      ──────────       ────        ─────────────
Pipeline A (hist.)  Hail BI          BI          $24K/yr (est.)
Pipeline A (hist.)  Tornado BI       BI          $X/yr
Pipeline A (hist.)  Strong Wind BI   BI          $X/yr
Pipeline B (fwd.)   Heat Wave HCR    BI delta    $4K/yr (additional)
Pipeline B (fwd.)   Flood HCR        BI delta    $0.1K/yr (additional)
Pipeline B (fwd.)   Peck's EFR       Degradation $17K/yr + IUL
Pipeline B (fwd.)   Coffin-Manson    Degradation (negative — benefit)
Pipeline B (fwd.)   Wildfire FWI     Risk flag   Direction: increasing
Pipeline B (fwd.)   Dry spell        Risk flag   Direction: increasing

TOTAL ANNUAL BI (historical):    Pipeline A sum = ~$30K/yr (est.)
ADDITIONAL BI (climate delta):   Pipeline B HCR = ~$4K/yr
DEGRADATION (climate):           Pipeline B EFR = ~$17K/yr + IUL shortening

BIGGEST IMPACT:
  Pipeline B EFR (IUL shortening): ~$3-5M NPV  ← DOMINATES
  Pipeline A historical BI:        ~$300K NPV   ← material but smaller
  Pipeline B HCR (climate delta):  ~$40K NPV    ← smallest
```

### What This Tells Us

1. **Equipment degradation (EFR) is the dominant climate risk** — 10-100x
   larger than BI from either pipeline. This hasn't changed.

2. **Historical BI from Pipeline A is ~10x larger than LTRisk's climate BI
   delta.** The baseline hail/tornado/wind risk ($30K/yr) exceeds the
   climate-driven heat BI increase ($4K/yr). The historical hazards matter
   more than the climate trend for Channel 1.

3. **The two pipelines together give the full picture:**
   Pipeline A = "what hurts you today" (acute events)
   Pipeline B = "what hurts you more tomorrow" (chronic shift + degradation)

---

## 7. Impact on the Orchestrator

The orchestrator (doc 06b) needs to know which pipeline provides what.
The routing matrix should include a "data source" column:

```
Hazard          Channel    Data Source         Status
──────────      ───────    ──────────────      ──────
Heat Wave BI    Ch1        LTRisk HCR          Need baseline from A or benchmarks
Hail BI         Ch1        Hazards Repo        Full (no climate delta)
Tornado BI      Ch1        Hazards Repo        Full (no climate delta)
Strong Wind BI  Ch1        Hazards Repo        Full (LTRisk proxy for delta)
Flood BI        Ch1        LTRisk HCR          Need baseline from A or benchmarks
Thermal aging   Ch2        LTRisk EFR          Full (Mode A Peck's)
Freeze-thaw     Ch2        LTRisk EFR          Full (Mode B Coffin-Manson)
Wildfire        Flag       Both (partial)      FWI proxy + NRI EAL
```

### The BI Parameters Connection

Pipeline A's BI methodology defines `forced_outage_hours` and
`full_recovery_hours` per hazard per asset type. These parameters
tell us whether a hazard causes BI at all:

```
If forced_hours + recovery_hours > 0  → It's a Channel 1 (BI) hazard
If forced_hours + recovery_hours = 0  → It's NOT BI → check if Channel 2

This aligns with the hcr_efr_boundary.md reclassification:
  Freeze-thaw: forced=0, recovery=0 → NOT BI → Channel 2 (EFR) ✓
  Hail (solar): forced=0, recovery=2160 → IS BI → Channel 1 ✓
  Heat Wave: forced=??? recovery=??? → NEEDS DEFINITION
```

---

## 8. Open Questions

1. **Should the orchestrator YAML include Pipeline A's BI parameters?**
   (forced_hours, recovery_hours, damage curve references) This would
   make the orchestrator the single config for both pipelines.

2. **Heat Wave BI parameters:** What should forced_outage_hours and
   full_recovery_hours be for heat wave events on solar and wind?
   This is the critical gap that connects Pipeline B's HCR to actual
   dollar losses.

3. **Can Pipeline A's Annual BI serve as baseline_BI_pct?**
   `baseline_BI_pct = Annual_BI_from_A / Annual_Revenue`
   This works for hail/tornado/wind. But for heat/flood/icing,
   Pipeline A doesn't have BI yet.

4. **Frequency vs severity under climate change:**
   LTRisk's HCR measures frequency change (more events). But climate
   change might also change severity (bigger hailstones, stronger
   storms). Should HCR scale only frequency, with a separate severity
   adjustment? Or is `BI × (1+HCR)` sufficient as a first approximation?

5. **Dashboard integration:** Should the dashboard show both pipeline
   outputs side by side? Historical BI from Pipeline A + climate delta
   from Pipeline B = total climate-adjusted risk?

6. **Time horizon mismatch:** Pipeline A uses 29 years of history
   (1996-2024). Pipeline B projects 30 years forward (2026-2055).
   The historical period may not represent future baseline if climate
   has already shifted. Should Pipeline A's baseline be adjusted for
   trend within the historical window?

---

## Cross-References

| Topic | Doc |
|-------|-----|
| Orchestrator (routing layer) | [06b_climate_risk_orchestrator.md](../../learning/C_financial_translation/06b_climate_risk_orchestrator.md) |
| Channel 1 BI calculation | [channel_1_bi_calculation.md](../hcr_financial/channel_1_bi_calculation.md) |
| Channel 2 EFR financial | [channel_2_efr_financial.md](../efr_degradation/channel_2_efr_financial.md) |
| HCR/EFR boundary | [hcr_efr_boundary.md](../hcr_financial/hcr_efr_boundary.md) |
| Framework architecture | [framework_architecture.md](framework_architecture.md) |
| Top-down meets bottom-up | [top_down_meets_bottom_up.md](top_down_meets_bottom_up.md) |
