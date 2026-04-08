# Plan: Update Framework Architecture Doc

**Status:** Ready to execute
**Created:** 2026-04-02
**File:** `docs/discussion/architecture/framework_architecture.md`

---

## Why Now

The framework architecture doc was written 2026-03-19 — before the following discussions and decisions:

1. **3-category hazard reclassification** (hcr_efr_boundary.md) — only BI events stay in HCR; degradation inputs move to EFR; risk indicators flagged separately
2. **EFR two modes** (efr_two_modes.md) — Mode A (SCVR-based) vs Mode B (daily data), mirroring HCR's Pathway A/B
3. **Channel 1 is 50-250x smaller than Channel 2** (channel_1_bi_calculation.md) — equipment degradation dominates overwhelmingly
4. **Orchestrator concept** (plan_climate_risk_orchestrator.md) — centralized routing layer proposed
5. **Top-down meets bottom-up** (top_down_meets_bottom_up.md) — coverage map, prioritization
6. **SCVR Report Card as unified router** (04_scvr_methodology.md revamp) — Tail Confidence drives Mode A/B for BOTH channels

## What Needs to Change

### Section 1 (Core Insight)
- Update to reflect confirmed finding: Channel 2 > Channel 1 by ~50-250x (no longer a hypothesis)
- Add the top-down/bottom-up framing (coverage is partial — hail is #2 risk but undocumented gap)

### Section 2 (Two Channels)
- Channel 1 examples: remove "hail damage" (documented gap), add note about 3-category split
- Channel 2: add Mode A/B for EFR, note Coffin-Manson uses Mode B (daily counts)
- Add note about Channel 1 being much smaller than Channel 2 at pilot sites

### Section 3 (End-to-End Pipeline)
- Update pipeline diagram to show:
  - Mode A/B branching for both HCR and EFR
  - 3-category split (BI events, degradation inputs, risk indicators)
  - Orchestrator sitting between SCVR Report and downstream channels
- Update dollar breakdown to note the 50-250x Channel split

### Section 4 (Variable → Channel Routing)
- Update routing table to reflect:
  - Unified Mode A/B logic (same Tail Confidence criteria for both channels)
  - Hazards reclassified (freeze-thaw → EFR, fire weather → risk indicator)
- Add note about the routing matrix concept from orchestrator plan

### Section 5 (Notebook Pipeline)
- Update NB04 status (HCR Part A done, EFR section + reclassification in progress)
- Add reference to Mode B Coffin-Manson

### Section 7 (Report Card as Router)
- Expand to show Report Card routing BOTH channels (not just HCR)
- Add Mode A/B decision tree for EFR alongside Pathway A/B for HCR

### Cross-References
- Add ALL new discussion docs:
  - hcr_efr_boundary.md
  - efr_two_modes.md
  - channel_1_bi_calculation.md
  - channel_2_efr_financial.md
  - top_down_meets_bottom_up.md
  - plan_climate_risk_orchestrator.md

### Relates-to frontmatter
- Add the new discussion docs to the relates-to list

---

## Approach

Complete rewrite of sections 1-4 and 7. Light updates to sections 5-6 and 8. Add new cross-references. Keep the same structure (8 sections) — don't reorganize, just update content to match current state.

## Verification

- [ ] Section 2 Channel 1 doesn't mention hail as example (documented gap)
- [ ] Section 2 Channel 2 mentions Mode A/B
- [ ] Section 3 pipeline shows 3-category split and orchestrator concept
- [ ] Section 4 routing table reflects unified Mode A/B logic
- [ ] Section 7 shows Report Card routing both channels
- [ ] All new discussion docs cross-referenced
- [ ] Dollar breakdown notes Channel 2 >> Channel 1
- [ ] No contradictions with updated docs 07, 08, or new discussion docs
