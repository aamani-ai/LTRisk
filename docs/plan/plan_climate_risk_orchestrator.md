# Climate Risk Orchestration Layer — Discussion & Design Plan

**Status:** Draft plan — needs iteration before execution
**Created:** 2026-04-02
**Related:** [hcr_efr_boundary.md](../discussion/hcr_financial/hcr_efr_boundary.md), [framework_architecture.md](../discussion/architecture/framework_architecture.md)

---

## Context

The LTRisk pipeline currently has: SCVR Report (Layer 1) → HCR/EFR (Layer 2) → Financial (Layer 3). But the routing logic between these layers is scattered across 4+ docs with no centralized orchestration. We need an explicit layer that sits between the SCVR Report and the downstream applications — an "orchestrator" that:

1. Holds the knowledge base of hazard/event definitions
2. Routes each climate signal to the right channel (BI vs degradation vs risk indicator)
3. Selects which SCVR metric matters (mean shift vs tail behavior) per variable/hazard
4. Provides a signal from the Report Card about what to trust and what not to

This is a design discussion doc, not code implementation yet.

---

## The Problem: Routing Is Currently Implicit & Scattered

Today, routing decisions happen in at least 5 places:

1. **Report Card** (04_scvr_methodology.md §4) → classifies Tail Confidence per variable
2. **Variable→Channel table** (framework_architecture.md §4) → hard-coded routing
3. **Pathway A vs B** (07_hcr_hazard_change.md §11) → per-hazard, implied by confidence
4. **Hazard definitions** (07_hcr_hazard_change.md §2B) → what counts as a hazard
5. **3-category reclassification** (hcr_efr_boundary.md) → proposed but not integrated

Nobody owns the complete decision tree. If you want to answer "For precipitation at Hayhurst, what metric feeds what model through what channel?", you need to read 4 docs.

---

## What the Orchestration Layer Should Be

### The Three Responsibilities

```
RESPONSIBILITY 1: HAZARD/EVENT KNOWLEDGE BASE
  "What climate phenomena exist, how are they defined,
   and what variables drive them?"

  This is a structured taxonomy, not just a list.
  Each entry has:
    - Climate definition (thresholds, compound logic)
    - Input variables (which SCVR metrics it needs)
    - Physical mechanism (what it does to equipment/operations)
    - Financial mechanism (BI, degradation, or risk indicator)
    - Proxy quality (HIGH/MODERATE/LOW for our data)
    - Computability (fully computable / proxy only / not computable)

RESPONSIBILITY 2: METRIC SELECTION
  "Given this hazard and this variable's Report Card,
   which SCVR metric should feed the computation?"

  The Report Card already computes 6+ metrics per variable.
  The orchestrator decides which one matters:
    - Mean SCVR for Peck's thermal aging (continuous stress)
    - P95/CVaR for extreme precipitation hazards (tail events)
    - Direct daily counts for freeze-thaw (Coffin-Manson cycles)
    - Period-average for low-signal variables (sfcWind, rsds)

RESPONSIBILITY 3: CHANNEL ROUTING
  "Where does each hazard's output flow in the financial model?"

  Three destinations:
    Channel 1 (BI): HCR → shutdown hours → lost revenue
    Channel 2 (EFR): degradation rate → life shortening → lost lifetime revenue
    Risk Flag: probabilistic indicator → flagged, not forced into $ formula
```

### What This Looks Like Concretely

```
                    SCVR Report
                    (7 variables, 6+ metrics each)
                         │
                         ▼
              ┌─────────────────────┐
              │   ORCHESTRATOR      │
              │                     │
              │  Hazard Taxonomy    │  ← "What exists"
              │  Metric Selector    │  ← "What to trust"
              │  Channel Router     │  ← "Where it flows"
              │                     │
              └──────┬──────────────┘
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
     Channel 1   Channel 2   Risk Flags
     (BI/HCR)    (EFR)       (Indicators)
```

### The Routing Matrix (Core Artifact)

The orchestrator's main output is a routing matrix — one row per hazard, showing exactly what feeds it and where it goes:

```
Hazard          | Input Vars  | SCVR Metric Used    | Confidence | Channel  | Pathway
──────────────  | ──────────  | ──────────────────  | ────────── | ──────── | ────────
Heat wave       | tasmax+min  | Mean SCVR (HIGH)    | HIGH       | Ch1 (BI) | A (2.5×)
Extreme precip  | pr          | P95/CVaR (DIVERG.)  | MODERATE   | Ch1 (BI) | B (count)
Flood Rx5day    | pr          | P95/CVaR (DIVERG.)  | MODERATE   | Ch1 (BI) | B (count)
Wind cut-out    | sfcWind     | Mean SCVR (MOD)     | LOW        | Ch1 (BI) | A (1.0×)
Icing shutdown  | tasmin+hurs | Mean SCVR (MOD)     | MODERATE   | Ch1 (BI) | B (count)
Thermal aging   | tas, hurs   | Mean SCVR (HIGH)    | HIGH       | Ch2 (EFR)| Peck's
Thermal cycling | tasmax+min  | Direct cycle count  | HIGH       | Ch2 (EFR)| Coffin-M
Wind fatigue    | sfcWind     | Mean SCVR (MOD)     | LOW        | Ch2 (EFR)| P-Miner
Fire weather    | 4 vars      | Composite FWI       | LOW        | Flag     | Indicator
Dry spell       | pr          | Period-average       | LOW        | Flag     | Indicator
Hail/SCS        | tas,hurs,w  | Surface proxy       | VERY LOW   | Flag     | Not comp.
Coastal flood   | —           | External (IPCC SLR) | N/A        | Flag     | Not comp.
Hurricane       | —           | External (TC tracks) | N/A        | Flag     | Not comp.
Tornado         | —           | External (STP)      | N/A        | Flag     | Not comp.
```

### Why This Matters

1. **Single source of truth** — one place to see every routing decision and its justification
2. **Data-driven switching** — the Report Card's Tail Confidence flag DRIVES which metric is selected, not human judgment scattered across docs
3. **Extensible** — adding a new site, hazard, or variable means adding a row, not editing 4 docs
4. **Auditable** — for NPL/FIDUCEO, you can point to the routing matrix and say "here's why precipitation uses P95 not mean"

---

## Design Decisions (Confirmed)

1. **Scope:** Full taxonomy — ALL known climate hazards for renewables, marked with computability status (fully computable / proxy only / not computable from NEX-GDDP)
2. **Format:** Discussion doc + draft hazard_taxonomy.yaml schema sketch at the end
3. **Location:** `docs/discussion/architecture/climate_risk_orchestrator.md`

## Open Design Questions (To Surface in Doc)

1. **Metric selection granularity:** Per-variable? Per-variable-per-scenario? Per-variable-per-decade?
2. **Compound hazard confidence:** Heat wave needs tasmax (HIGH) AND tasmin (MODERATE). What confidence does the compound get? Min? Weighted?
3. **Site-specificity:** Does the routing matrix change per site, or is it universal? (e.g., Hayhurst has 0 wind cut-out days — should wind hazards be suppressed?)
4. **When does the YAML become code?** Discussion doc first, then implement in NB04 when we're confident in the taxonomy

---

## Implementation Plan (When Ready to Execute)

### Step 1: Write the discussion doc
**File:** `docs/discussion/architecture/climate_risk_orchestrator.md`

Contents:
1. Frame the problem (routing is scattered across 5 places)
2. Propose the 3-responsibility architecture
3. Full hazard taxonomy table (ALL hazards, including non-computable)
4. Full routing matrix for Hayhurst Solar (concrete values)
5. Metric selection rules (when to use mean vs tail vs direct count)
6. Address the 4 open design questions
7. Connection to FIDUCEO uncertainty mapping
8. Draft hazard_taxonomy.yaml schema sketch

### Step 2: Update framework architecture
**File:** `docs/discussion/architecture/framework_architecture.md`

Add a reference to the orchestrator doc in the pipeline section and cross-references table.

### Step 3: Review with team
Share with Prashant/Jung for feedback on:
- Hazard taxonomy completeness
- Routing matrix correctness
- Metric selection rules
- Whether the YAML schema is the right format

---

## Files Involved

- NEW: `docs/discussion/architecture/climate_risk_orchestrator.md`
- UPDATE: `docs/discussion/architecture/framework_architecture.md` (add reference)
- REFERENCE: `docs/discussion/hcr_financial/hcr_efr_boundary.md`
- REFERENCE: `docs/learning/B_scvr_methodology/04_scvr_methodology.md`
- REFERENCE: `docs/discussion/uncertainty/FIDUCEO-Style Uncertainty Mapping_ LTRisk.md`

## Verification
- [ ] Discussion doc captures all 3 responsibilities clearly
- [ ] Full hazard taxonomy covers computable + non-computable hazards
- [ ] Routing matrix covers all hazards with concrete Hayhurst values
- [ ] Open questions are surfaced for team discussion
- [ ] YAML schema sketch is included
- [ ] Cross-references to existing docs are correct
- [ ] Framework architecture doc updated with pointer to orchestrator
