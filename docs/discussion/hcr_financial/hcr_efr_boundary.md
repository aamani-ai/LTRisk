---
title: "Discussion — HCR/EFR Boundary: Which Hazards Belong in Which Channel?"
type: discussion
domain: climate-risk / financial-translation / architecture
created: 2026-03-31
status: draft — proposed reclassification, pending team review
context: >
  Reviewing NB04 HCR output revealed that 10 hazards are all routed through
  the same BI_loss formula (HCR x baseline_BI_pct x Revenue), but several
  hazards don't cause business interruption — they cause equipment stress
  (EFR territory) or represent probabilistic risk indicators. This doc
  proposes reclassifying hazards by their actual financial mechanism.
relates-to:
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/learning/C_financial_translation/08_efr_equipment_degradation.md
  - docs/learning/C_financial_translation/09_nav_impairment_chain.md
  - docs/discussion/hcr_financial/cashflow_integration.md
  - docs/discussion/architecture/framework_architecture.md
---

# Discussion — HCR/EFR Boundary

> **The question:** The current framework routes all 10 hazards through
> `HCR -> BI_loss`. But do all 10 actually cause business interruption?
> Or are some of them equipment degradation inputs (EFR) or probabilistic
> risk indicators that need different treatment?

---

## 1. The Current Architecture

The framework defines two independent financial channels:

```
Channel 1 (Business Interruption):
  SCVR -> HCR(10 hazards) -> BI_loss = HCR x baseline_BI_pct x Revenue
  Mechanism: hazard events cause shutdowns/downtime
  Character: per-year loss, not cumulative

Channel 2 (Equipment Degradation):
  SCVR -> EFR (Peck's, Coffin-Manson, Palmgren-Miner) -> generation decline
  Mechanism: climate stress accelerates material aging
  Character: cumulative, life-shortening
```

The docs say these channels are "independent and parallel" (doc 09, S3;
doc 08, line 742). EFR uses SCVR directly; it does not consume HCR output.
HCR feeds BI_loss; it does not feed EFR.

**This separation is clean in principle. The problem is how the 10 hazards
are defined.**

---

## 2. The Problem: Not All "Hazards" Cause Business Interruption

The 10 HCR hazards are defined by their **climate threshold** (what
combination of variables and exceedances defines the event), not by their
**financial mechanism** (how they affect cash flows). This creates three
problems:

1. Some hazards don't cause BI — they cause equipment stress (EFR territory)
2. Some hazards are risk indicators, not deterministic events
3. The daily counting infrastructure (Pathway B) serves both channels but
   is currently framed as purely HCR

---

## 3. Worked Examples: Three Hazards, Three Different Realities

### 3A. Heat Wave — Genuine BI Event

```
Climate definition:
  3+ consecutive days where tasmax > per-DOY P90 AND tasmin > per-DOY P90

What happens physically:
  Inverters hit thermal protection limits -> forced shutdown
  Panel output drops under extreme cell temperature (derating)
  Plant is CAPABLE of producing, but safety systems prevent it

Financial mechanism:
  Lost generation during shutdown/derating hours
  This IS business interruption: operational downtime from an event

BI conversion:
  22 additional shutdown hours/yr x 24.8 MW x 0.85 CF x $40/MWh
  = ~$18K/yr additional revenue loss

Does HCR x baseline_BI_pct x Revenue make sense here?
  YES. More events -> more shutdown hours -> more lost revenue.
  The formula correctly captures the financial mechanism.

What about Peck's (EFR)?
  Peck's captures the continuous thermal aging from sustained
  elevated MEAN temperature (even on non-heat-wave days).
  HCR captures discrete shutdown events during extremes.
  These are different physical phenomena -> no double counting.
```

**Verdict: Heat wave belongs in HCR (Channel 1).** The BI conversion
is straightforward and well-defined.

---

### 3B. Freeze-Thaw — NOT a BI Event

```
Climate definition:
  A day where tasmin < 0 C AND tasmax > 0 C (same day)

What happens physically:
  Water in panel encapsulant/solder joints expands when freezing,
  contracts when thawing. Each cycle propagates microcracks in
  solder joints and delamination in encapsulant layers.

Does the plant shut down?  NO.
Does generation get curtailed?  NO.
The panels produce power normally during a freeze-thaw day.

Financial mechanism:
  CUMULATIVE MATERIAL FATIGUE over many cycles
  This is exactly what Coffin-Manson models:
    N_f = C x (delta_T)^(-beta)
  where each freeze-thaw day IS a fatigue cycle.

BI conversion:
  BI_loss = Revenue x baseline_BI_pct x HCR_freeze_thaw
  But baseline_BI_pct for freeze-thaw should be ~0%
  because freeze-thaw doesn't cause operational downtime.
  So: BI_loss = Revenue x 0% x (-25%) = $0

  The HCR number is physically correct (fewer cycles with warming)
  but it's feeding the WRONG CHANNEL.

Where should this data go?
  The freeze-thaw cycle count from Pathway B should be a DIRECT
  INPUT to Coffin-Manson in EFR (Channel 2), not to BI_loss.
```

**Verdict: Freeze-thaw does NOT belong in HCR.** It's a Coffin-Manson
input for EFR. The daily counting infrastructure in NB04 is doing
valuable work — but the output should route to Channel 2.

---

### 3C. Fire Weather (FWI) — A Risk Indicator, Not a BI Event

```
Climate definition:
  Composite index: 0.3 x norm(tasmax) + 0.3 x (1 - norm(hurs))
                 + 0.2 x norm(sfcWind) + 0.2 x (1 - norm(pr))
  Days where FWI exceeds baseline P90

What happens physically:
  Conditions are FAVORABLE for wildfire.
  But no fire necessarily occurs on any given high-FWI day.

Financial mechanism:
  If no fire occurs:   $0 (elevated risk, no actual event)
  If fire occurs:      potentially catastrophic
                       (weeks of downtime, smoke soiling, equipment damage)

  P(fire | high FWI day) << 1     (very small probability)
  Impact(fire) >> Impact(avg BI)  (very high severity)

  This is a LOW-FREQUENCY, HIGH-SEVERITY risk.
  It cannot be modeled as: "12% more high FWI days -> 12% more fire BI"
  because the relationship between risk-days and actual events is
  non-linear and probabilistic.

  A 12% increase in risky days might mean:
    - 0 additional fires over 30 years, OR
    - 1 additional fire (a binary, catastrophic event)

BI conversion:
  HCR x baseline_BI_pct doesn't work here.
  This needs either:
    (a) Probabilistic event modeling: P(fire|FWI) x E[loss|fire]
    (b) Insurance-style treatment: frequency x severity
    (c) Flagging as a risk indicator without deterministic $ conversion
```

**Verdict: Fire weather is a risk indicator, not a deterministic BI
event.** It needs different treatment from the HCR x baseline_BI_pct
formula.

---

## 4. Proposed Reclassification

### Category 1 — BI Events (stay in HCR -> Channel 1)

These cause **operational shutdown or curtailment**. The plant could
produce but doesn't because of the event. The BI conversion formula
(HCR x baseline_BI_pct x Revenue) works correctly.

| Hazard | Why it's BI | BI mechanism |
|--------|------------|--------------|
| **Heat wave** | Inverter thermal shutdown, panel derating | Lost generation hours |
| **Extreme precip / flooding** | Site access loss, pad submersion | Downtime days |
| **Wind cut-out** | Above rated speed -> forced shutdown | Lost generation hours |
| **Icing shutdown** | Blade/panel icing -> forced shutdown | Downtime days |

### Category 2 — Degradation Inputs (move to EFR -> Channel 2)

These cause **material stress that accumulates over time**. The plant
operates normally during these days. The damage is cumulative fatigue,
not lost revenue.

| Hazard | Why it's degradation | EFR model it feeds |
|--------|---------------------|-------------------|
| **Freeze-thaw cycles** | Solder joint microcracks, encapsulant delamination | Coffin-Manson (cycle count) |
| **Frost days** | Sub-zero thermal stress on materials | Coffin-Manson (cold stress) |
| **Cold wave** | Extended cold exposure -> thermal shock | Coffin-Manson (sustained cold) |

**Key change:** Instead of computing `HCR_freeze_thaw` and routing it
through `BI_loss`, the freeze-thaw cycle count from Pathway B becomes
a direct input to Coffin-Manson:

```
Current (wrong channel):
  freeze_thaw_count -> HCR -> BI_loss = Revenue x 0% x HCR = $0
  Coffin-Manson uses SCVR_tasmax, SCVR_tasmin (mean approximation)

Proposed (correct channel):
  freeze_thaw_count -> Coffin-Manson directly (actual cycle count)
  No HCR computation needed for this hazard
  BI_loss doesn't include freeze-thaw (because BI_pct = 0 anyway)
```

This also means Coffin-Manson gets **better data**. Instead of
estimating delta_T from SCVR mean shift, it uses actual 0 C crossing
counts from daily model output.

### Category 3 — Probabilistic Risk Indicators (separate treatment)

These modify the **probability of rare, high-impact events** rather
than causing deterministic BI or degradation per day.

| Hazard | Why it's probabilistic | Suggested treatment |
|--------|----------------------|-------------------|
| **Fire weather (FWI)** | High FWI != fire. Low-freq, high-severity. | Frequency x severity model, or flag as risk indicator |
| **Dry spell** | Contributes to fire risk + soiling buildup | Soiling portion -> performance; fire portion -> probabilistic |

These cannot be modeled as `HCR x baseline_BI_pct` because:
- The baseline_BI_pct is not a stable fraction (it's 0 most years,
  catastrophic in rare years)
- The relationship between indicator days and actual events is non-linear
- Insurance-style treatment (expected annual loss from frequency x severity)
  would be more appropriate

**For Phase 1:** Report these as risk indicators with direction and
magnitude. Flag in the dashboard without forcing a deterministic $
conversion. For Phase 2, explore probabilistic event modeling or
insurance benchmarks.

---

## 5. Revised Data Flow

```
                        SCVR(t)
                          |
            +-------------+-------------+
            |             |             |
            v             v             v
    BI Events (4)    Degradation    Risk Indicators (2)
    Channel 1        Channel 2      Flagged
            |             |             |
            v             v             v
    HCR(t) per     EFR(t) from:    Report as
    hazard via     - Peck's (SCVR   direction +
    Pathway A/B      continuous)    magnitude,
            |      - Coffin-Manson   no $ conversion
            |        (cycle counts   in Phase 1
            |        from Pathway B)
            |      - Palmgren-Miner
            |        (SCVR continuous)
            |             |
            v             v
    BI_loss(t)     climate_degrad(t)
    = sum(HCR_h    = weighted EFR
      x base_BI_h    x std_degrad
      x Revenue)     x t (cumulative)
            |             |
            +------+------+
                   |
                   v
          CFADS_adjusted(t)
          = Revenue x (1 - climate_degrad)
            - BI_loss
            - OpEx
```

### What changes in NB04

The Pathway B daily counting infrastructure **stays** — it's valuable.
But its outputs get routed differently:

```
Pathway B daily counting
    |
    +-- heat_wave_count     -> HCR -> BI_loss (Channel 1)
    +-- extreme_precip_count -> HCR -> BI_loss (Channel 1)
    +-- wind_cutout_count    -> HCR -> BI_loss (Channel 1)
    +-- icing_shutdown_count -> HCR -> BI_loss (Channel 1)
    |
    +-- freeze_thaw_count   -> Coffin-Manson input (Channel 2)
    +-- frost_day_count     -> Coffin-Manson input (Channel 2)
    +-- cold_wave_count     -> Coffin-Manson input (Channel 2)
    |
    +-- fwi_high_days       -> Risk indicator (flagged, no $ yet)
    +-- dry_spell_max       -> Risk indicator (flagged, no $ yet)
```

---

## 6. Impact on Existing Results

### What stays the same
- SCVR computation (unchanged)
- Peck's thermal aging (still uses SCVR_tas, SCVR_hurs continuously)
- Palmgren-Miner wind fatigue (still uses SCVR_sfcWind)
- Heat wave HCR (correctly in Channel 1, validated scaling 2.5x)
- Precipitation HCR (correctly in Channel 1 via Pathway B)
- The daily counting code in NB04 (still runs, outputs still computed)

### What changes
- Freeze-thaw, frost, cold wave **removed from HCR annual table**
  (their BI contribution was effectively $0 anyway since baseline_BI_pct ~ 0)
- Freeze-thaw cycle count becomes **direct input to Coffin-Manson**
  (better than current SCVR mean approximation)
- Fire weather, dry spell **flagged as risk indicators** in dashboard
  instead of forced into BI_loss formula
- Wind extreme: stays in HCR but with "low confidence" flag
  (0 baseline days at Hayhurst, poor proxy quality)

### Financial impact of reclassification
- **Minimal for Channel 1 (BI):** The removed hazards had ~$0 BI contribution
  anyway (freeze-thaw doesn't cause downtime). Removing them doesn't change
  the BI_loss number.
- **Improved for Channel 2 (EFR):** Coffin-Manson gets actual cycle counts
  instead of SCVR mean approximation. This should produce more accurate
  (and likely larger) thermal cycling fatigue estimates, since the cycle
  count captures the actual 0 C crossing frequency.

---

## 7. The Deeper Insight: Pathway B Serves Both Channels

The daily counting infrastructure in NB04 was built as "HCR computation"
but it's actually **shared climate event counting** that serves both
financial channels:

- For Channel 1: "How many more shutdown days?" (BI events)
- For Channel 2: "How many more stress cycles?" (degradation inputs)

This reframing doesn't invalidate the work done in NB04. It clarifies
what the outputs mean and where they should flow. The Pathway B code
is doing the right computation — it's the routing that needs correction.

---

## 8. Open Questions for Team

1. **Icing shutdown vs icing degradation:** Icing can cause both
   shutdown (BI) and physical damage (ice loading stress). Should icing
   be split across both channels, or treated as primarily BI?

2. **Cold wave:** Extended cold can cause both operational issues
   (frozen pipes, access problems) and material stress. Is this more
   BI or more degradation at the asset types we model?

3. **Soiling from dry spells:** Dry spells contribute to dust/soiling
   buildup that reduces generation. This is a performance effect
   (Channel 3) rather than BI or degradation. Should NB04 compute
   a soiling adjustment from dry spell length?

4. **Fire weather Phase 2:** When we move to probabilistic treatment,
   what data source provides P(fire | FWI) for Texas sites? Insurance
   loss databases? NIFC fire occurrence records?

5. **Dashboard presentation:** How should the reclassified hazards be
   shown? Separate sections for BI hazards vs degradation inputs vs
   risk indicators? Or one unified view with category badges?

---

## 9. Recommended Next Steps

1. Update NB04 routing to implement the 3-category classification
2. Feed freeze-thaw/frost/cold wave counts into Coffin-Manson (NB04 EFR section)
3. Move fire weather and dry spell to "risk indicators" in output schema
4. Update framework_architecture.md to reflect the revised data flow
5. Update doc 07 (HCR) to clarify that HCR covers BI events only
6. Dashboard: show BI hazards in Channel 1 section, degradation inputs
   in Channel 2 section, risk indicators with appropriate flagging

---

## Cross-References

| Topic | Doc | Relevance |
|-------|-----|-----------|
| HCR methodology (current) | [07_hcr_hazard_change.md](../../learning/C_financial_translation/07_hcr_hazard_change.md) | Defines 10 hazards, scaling factors, Pathway A/B |
| EFR physics models | [08_efr_equipment_degradation.md](../../learning/C_financial_translation/08_efr_equipment_degradation.md) | Peck's, Coffin-Manson, Palmgren-Miner — where degradation inputs feed |
| NAV impairment chain | [09_nav_impairment_chain.md](../../learning/C_financial_translation/09_nav_impairment_chain.md) | How BI_loss and EFR combine in CFADS |
| Cash flow integration | [cashflow_integration.md](cashflow_integration.md) | BI conversion approaches (top-down, bottom-up, benchmarks) |
| Framework architecture | [framework_architecture.md](../architecture/framework_architecture.md) | Two-channel system map (needs update after this discussion) |
| HCR pathways | [hcr_pathway_a_vs_b.md](hcr_pathway_a_vs_b.md) | Pathway B infrastructure that serves both channels |
| Jensen's inequality | [jensen_inequality_hcr_scvr.md](jensen_inequality_hcr_scvr.md) | Why Pathway A fails for precip (still applies to BI hazards) |
