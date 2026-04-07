---
title: "Discussion — Top-Down Meets Bottom-Up: Two Approaches to Climate Risk Quantification"
type: discussion
domain: climate-risk / architecture / methodology
created: 2026-04-02
status: draft — foundational thinking document
context: >
  The LTRisk framework was built bottom-up: start with climate variables,
  derive what we can measure, route outputs to financial models. This doc
  argues that a complementary top-down approach (start with what threatens
  the asset, then ask what we can quantify) is necessary — and that the
  two approaches must be married through an explicit coverage map and
  prioritization framework.
relates-to:
  - docs/discussion/architecture/framework_architecture.md
  - docs/discussion/hcr_financial/hcr_efr_boundary.md
  - docs/plan/plan_climate_risk_orchestrator.md
  - docs/plan/plan_asset_risk_profiles.md
---

# Top-Down Meets Bottom-Up

> **The question:** We built LTRisk from the climate data upward. Should we
> also build it from the asset downward? And if so, how do the two
> perspectives connect?

> **Short answer:** Yes. Bottom-up tells us what we CAN measure. Top-down
> tells us what we SHOULD measure. Neither alone is sufficient. Together
> they produce a coverage map that honestly shows where we're strong, where
> we're blind, and where to invest next.

---

## 1. The Two Approaches

### Bottom-Up: "What can our data tell us?"

This is how LTRisk was built. The logic flows from data to impact:

```
START: We have 7 climate variables from 28 CMIP6 models
       (tasmax, tasmin, tas, pr, sfcWind, hurs, rsds)
              │
              ▼
DERIVE: What signals can we extract?
        → SCVR (mean shift per variable)
        → Report Card (tail confidence, companion metrics)
        → Daily threshold exceedances (Pathway B counts)
              │
              ▼
MAP: Which hazards can we compute from these signals?
     → Heat waves (tasmax + tasmin compound)
     → Frost/freeze-thaw (tasmin threshold)
     → Extreme precip / flood (pr Rx5day)
     → FWI proxy (4-variable composite)
     → Wind extremes (sfcWind, poor proxy)
              │
              ▼
TRANSLATE: How do these hazards affect asset value?
           → HCR × baseline_BI_pct → Channel 1 (BI)
           → Peck's / Coffin-Manson → Channel 2 (EFR)
              │
              ▼
OUTPUT: NAV impairment estimate
```

**Strengths of bottom-up:**
- Rigorous — every number traces back to observed/modeled data
- Reproducible — same inputs → same outputs
- Honest — we only claim what we can compute
- Defensible — the math is documented end-to-end

**Weaknesses of bottom-up:**
- **Blind to what we can't measure.** If NEX-GDDP doesn't have a variable,
  the associated risk is invisible — not absent, just invisible.
- **Biased toward temperature.** Temperature has the strongest SCVR signal,
  so it dominates the output. But is temperature the biggest RISK for a
  solar farm? Or just the biggest signal in our DATA?
- **Asset-agnostic.** The same hazard list is applied regardless of whether
  the asset is a utility-scale solar farm, a rooftop PV system, an offshore
  wind turbine, or a battery storage facility. Their risk profiles are very
  different.
- **No prioritization signal.** Everything we can compute gets computed.
  But stakeholders need to know: "What's the #1 risk for MY asset?"

### Top-Down: "What threatens this asset?"

The logic flows from the asset to the data:

```
START: We have a 24.8 MW solar farm in West Texas
              │
              ▼
ASK: What events can damage this asset or disrupt its revenue?
     (From insurance claims, O&M records, industry knowledge)
              │
              ▼
     1. Thermal aging (Peck's — continuous, cumulative)
     2. Hail damage (equipment destruction — catastrophic)
     3. Inverter heat shutdown (operational — BI)
     4. Transformer flooding (operational — BI + damage)
     5. Wildfire smoke/fire (operational + damage — catastrophic)
     6. Grid curtailment during extreme heat (market — BI)
     7. Panel soiling from dust/drought (performance — gradual)
     8. Freeze-thaw solder fatigue (degradation — cumulative)
     9. Supply chain disruption from regional disaster (indirect)
    10. Regulatory response to climate events (indirect)
              │
              ▼
CLASSIFY: For each event, what's the financial mechanism?
          → BI (shutdown/curtailment)
          → Degradation (cumulative aging/fatigue)
          → Catastrophic (replacement/major repair)
          → Performance (gradual output reduction)
          → Indirect (supply chain, regulatory, market)
              │
              ▼
QUANTIFY: For each event, what data do we need?
          → Can we get it from CMIP6? → Yes: connect to SCVR pipeline
          → Can we get it from ERA5/reanalysis? → Partial: historical only
          → Can we get it from insurance data? → Yes: frequency × severity
          → Can we get it at all? → No: documented gap
              │
              ▼
OUTPUT: Prioritized risk profile with coverage assessment
```

**Strengths of top-down:**
- **Comprehensive** — captures ALL risks, not just the ones our data measures
- **Asset-specific** — different assets have different risk profiles
- **Prioritized** — ranks risks by financial materiality, not data availability
- **Honest about gaps** — explicitly shows what we can't quantify
- **Stakeholder-friendly** — answers "what should I worry about?" directly

**Weaknesses of top-down:**
- **Less rigorous for items we can't quantify** — "hail is a big risk" is
  true but not a number
- **Requires domain expertise** — the risk inventory comes from industry
  knowledge, not automated computation
- **Harder to reproduce** — expert judgment varies
- **Risk of overreach** — tempting to claim coverage we don't have

---

## 2. Why Both Are Necessary

Neither approach alone gives a complete picture:

```
BOTTOM-UP ALONE                    TOP-DOWN ALONE
─────────────────                  ──────────────────
"We can compute heat wave          "Hail is the #2 risk for
 HCR with HIGH confidence"         Texas solar"

But: is heat wave actually         But: we have no data to
the biggest risk? Or just          quantify hail from CMIP6.
the easiest to measure?            So what do we DO with this?

Risk of: FALSE PRECISION           Risk of: UNGROUNDED CLAIMS
Precise answer to the              Right question, but no
wrong question.                    rigorous answer.
```

**The marriage of both approaches produces something neither can alone: a
coverage map with honest confidence levels.**

```
COVERAGE MAP (what marrying both approaches gives you)

  Risk Event          | Financial    | Top-Down    | Bottom-Up    | Coverage
                      | Impact Rank | Priority    | Quantifiable | Status
  ──────────────────  | ─────────── | ─────────── | ──────────── | ────────
  Thermal aging       | #1 (solar)  | HIGH        | YES (Peck's) | ██████████ FULL
  Hail damage         | #2 (solar)  | HIGH        | NO (no CAPE) | ░░░░░░░░░░ GAP
  Heat wave shutdown  | #3 (solar)  | HIGH        | YES (HCR)    | ██████████ FULL
  Flooding            | #4 (solar)  | MODERATE    | PARTIAL (pr) | █████░░░░░ PARTIAL
  Wildfire            | #5 (solar)  | MODERATE    | PROXY (FWI)  | ███░░░░░░░ PROXY
  Freeze-thaw fatigue | #6 (solar)  | MODERATE    | YES (counts) | ██████████ FULL
  Panel soiling       | #7 (solar)  | LOW-MOD     | PROXY (dry)  | ██░░░░░░░░ PROXY
  Grid curtailment    | #8 (solar)  | LOW         | NO (market)  | ░░░░░░░░░░ GAP
  Supply chain        | #9 (solar)  | LOW         | NO (indirect)| ░░░░░░░░░░ GAP
  Regulatory response | #10 (solar) | LOW         | NO (indirect)| ░░░░░░░░░░ GAP

  COVERAGE SUMMARY:
    FULL quantification:     3/10 risks (thermal aging, heat wave, freeze-thaw)
    PARTIAL quantification:  1/10 risks (flooding)
    PROXY only:              2/10 risks (wildfire, soiling)
    DOCUMENTED GAP:          4/10 risks (hail, curtailment, supply chain, regulatory)

    By financial materiality: we cover #1, #3, #6 fully.
    We MISS #2 (hail) entirely — and it's high priority.
```

**This is enormously valuable.** Without the top-down view, we'd report our
bottom-up results and a stakeholder might think "you've covered everything."
With the coverage map, they know "you've covered the 3 biggest quantifiable
risks, but hail — the #2 risk — is a documented gap."

---

## 3. How the Two Approaches Connect

### The Orchestrator as the Meeting Point

The orchestrator (plan_climate_risk_orchestrator.md) is where top-down meets
bottom-up. It needs BOTH perspectives:

```
TOP-DOWN                         BOTTOM-UP
"What risks exist?"              "What signals can we measure?"
(demand side)                    (supply side)
         │                                │
         ▼                                ▼
  Asset Risk Profile              SCVR Report Card
  (full inventory,                (7 variables, 6 metrics,
   ranked by impact)               tail confidence flags)
         │                                │
         └──────────┬─────────────────────┘
                    │
                    ▼
             ORCHESTRATOR
             ┌────────────────────────────┐
             │  Match demand to supply:   │
             │                            │
             │  For each risk event:      │
             │    Can we quantify it?     │
             │    → YES: route to channel │
             │    → PARTIAL: flag + route │
             │    → NO: document as gap   │
             │                            │
             │  For each signal:          │
             │    Which risks does it     │
             │    serve? Is it the RIGHT  │
             │    metric for that risk?   │
             └────────────────────────────┘
                    │
          ┌─────────┼──────────┐
          │         │          │
          ▼         ▼          ▼
     Channel 1  Channel 2  Risk Flags
     (BI)       (EFR)      + Gaps
```

### The Prioritization Signal

The top-down view provides something the bottom-up can't: **prioritization.**

Today, NB04 computes HCR for 10 hazards and presents them all equally. But
a stakeholder doesn't need to know about wind cut-out HCR at Hayhurst (it's
zero — 0 baseline days). They need to know:

```
"Your #1 climate risk is thermal aging (we quantify it: ~10% NAV hit).
 Your #2 climate risk is hail (we CAN'T quantify it — documented gap).
 Your #3 climate risk is heat wave shutdown (we quantify it: ~2% NAV hit)."
```

This prioritization comes from the asset risk profile, not from the data.
The bottom-up tells you the numbers; the top-down tells you which numbers
matter most.

---

## 4. What This Means for the Framework

### Current Architecture (Bottom-Up Only)

```
CMIP6 data → SCVR → HCR/EFR → CFADS → NAV
             (all 7 vars, all computable hazards)
```

### Proposed Architecture (Both Approaches Married)

```
                Asset Risk Profile (top-down)
                "What threatens this asset?"
                         │
                         ▼ demand
              ┌─────────────────────┐
              │    ORCHESTRATOR     │
              │                     │
              │  Coverage map       │
              │  Metric selection   │
              │  Channel routing    │
              │  Gap documentation  │
              └─────────────────────┘
                         ▲ supply
                         │
                SCVR Report Card (bottom-up)
                "What can our data measure?"
                         │
                         ▼
              Channel 1 + Channel 2 + Risk Flags + Documented Gaps
```

### What Changes in Practice

1. **Hazard list becomes asset-specific.** A solar farm in Texas gets a
   different prioritized risk inventory than an offshore wind farm in the
   North Sea. The SCVR pipeline is the same; the orchestrator's routing is
   different.

2. **Gaps become first-class outputs.** "We can't quantify hail" is as
   important as "thermal aging causes 10% NAV hit." Gaps are reported
   alongside quantified risks, not hidden.

3. **Prioritization is explicit.** The top 3 risks by financial materiality
   are highlighted. Low-priority computable risks (e.g., wind extreme at a
   solar site) get deprioritized rather than treated equally.

4. **New data sources have a home.** If we later get hail data (e.g., from
   ERA5 CAPE + shear), the top-down profile already has the demand entry
   waiting. We just flip the coverage status from "GAP" to "PARTIAL" or
   "FULL."

---

## 5. Why Now?

Three things have converged that make this the right time:

1. **The SCVR Report is stable.** We have a proven, documented, dashboard-deployed
   bottom-up pipeline. The foundation is solid.

2. **The HCR/EFR boundary discussion revealed the routing problem.** We
   discovered that not all "hazards" are BI events — some are degradation
   inputs, some are risk indicators. This forced the question: who decides
   what goes where?

3. **We're about to build the orchestrator.** Before we design the routing
   matrix, we need to know what it's routing. The top-down asset risk
   profiles provide the demand side that the orchestrator needs.

The sequence should be:

```
Step 1: This document (why both approaches matter)           ← YOU ARE HERE
Step 2: Asset risk profiles (top-down, per asset type)       ← NEXT
Step 3: Orchestrator design (where top-down meets bottom-up) ← PLANNED
Step 4: NB04 updates (implement routing in code)             ← LATER
```

---

## 6. What the Bottom-Up Gave Us (Credit Where Due)

The bottom-up approach wasn't wrong — it was the right starting point. It
produced several foundational insights that the top-down approach can't:

1. **"The resource is stable."** SCVR proved that rsds and sfcWind barely
   change. The risk is to the equipment, not the fuel supply. No amount of
   top-down expert judgment would have produced this finding with the same
   precision.

2. **"Precipitation mean hides tail risk."** The DIVERGENT classification for
   pr was discovered empirically — the Report Card caught the mean/tail
   divergence. This is a data-driven insight that changed how we route
   precipitation to downstream models.

3. **"Temperature is the dominant driver."** SCVR showed tasmin at +16.4%,
   while wind and radiation are near zero. This shapes the entire financial
   impact: EFR (temperature-driven degradation) dominates over HCR
   (event-driven BI).

4. **"Three methods agree to 6 decimal places."** The mathematical proof that
   SCVR = mean ratio gives the framework credibility that top-down expert
   judgment can't match.

These findings are foundational. The top-down approach builds ON them, not
instead of them.

---

## 7. What the Top-Down Will Add

The top-down approach will provide:

1. **Risk completeness** — the full inventory of what can go wrong, including
   things our data can't measure (hail, grid curtailment, supply chain)

2. **Financial materiality ranking** — which risks matter most in dollar terms,
   regardless of data availability

3. **Asset specificity** — different risk profiles for solar vs wind vs battery
   vs data center

4. **Coverage honesty** — explicit gaps, not silent omissions

5. **Prioritization for development** — "if we want to improve coverage,
   acquiring hail data is higher priority than refining wind extreme proxies"

6. **Stakeholder communication** — "here's what we cover, here's what we
   don't, and here's why the things we don't cover still appear in your
   risk report as flags"

---

## 8. The Deliverables (Sequence)

```
DOCUMENT 1: This document (done)
  "Why we need both approaches and how they connect"

DOCUMENT 2: Asset Risk Profiles (next)
  Per asset type: solar, wind, (battery, data center — future)
  Full risk inventory, financial mechanism, climate linkage,
  quantifiability assessment, coverage gap map

DOCUMENT 3: Orchestrator Design (planned)
  The routing matrix where top-down meets bottom-up
  Hazard taxonomy, metric selection, channel routing,
  draft hazard_taxonomy.yaml schema

DOCUMENT 4: Implementation (later)
  NB04 updates, dashboard integration, production pipeline
```

---

## Cross-References

| Topic | Doc | What It Covers |
|-------|-----|---------------|
| Current framework architecture | [framework_architecture.md](framework_architecture.md) | Two-channel system map (bottom-up only today) |
| HCR/EFR boundary (routing problem) | [hcr_efr_boundary.md](../hcr_financial/hcr_efr_boundary.md) | Why all 10 hazards shouldn't go through BI_loss |
| SCVR Report Card (bottom-up metrics) | [04_scvr_methodology.md](../../learning/B_scvr_methodology/04_scvr_methodology.md) | What the bottom-up produces: 6 companion metrics, tail confidence |
| Orchestrator plan | [plan_climate_risk_orchestrator.md](../../plan/plan_climate_risk_orchestrator.md) | Where top-down meets bottom-up (design plan, not yet executed) |
| Asset risk profiles plan | [plan_asset_risk_profiles.md](../../plan/plan_asset_risk_profiles.md) | Top-down risk inventories per asset type (planned) |
| FIDUCEO uncertainty mapping | [FIDUCEO uncertainty mapping](../uncertainty/FIDUCEO-Style%20Uncertainty%20Mapping_%20LTRisk.md) | Uncertainty propagation through the equation chain |
| Reference landscape | [LTRisk-Reference-Landscape.md](../../reference/LTRisk-Reference-Landscape.md) | Academic grounding for each pipeline layer |
