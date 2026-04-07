# Asset Risk Profiles — Top-Down Climate Risk Inventories

**Status:** Planned — depends on top_down_meets_bottom_up.md (discussion doc)
**Created:** 2026-04-02
**Prerequisite:** [top_down_meets_bottom_up.md](../discussion/architecture/top_down_meets_bottom_up.md)

---

## Purpose

Create per-asset-type risk profiles that inventory ALL climate-related threats
(not just the ones our CMIP6 data can measure), ranked by financial materiality,
with explicit coverage assessment showing what we quantify, what we approximate,
and what remains a documented gap.

## Asset Types to Cover

### Phase 1 (Current Pilot Assets)
- **Utility-scale Solar PV** (Hayhurst Texas Solar — 24.8 MW)
- **Onshore Wind** (Maverick Creek Wind — 491.6 MW)

### Phase 2 (Future Extension)
- Battery Energy Storage Systems (BESS)
- Data Centers
- Offshore Wind
- Rooftop/Distributed Solar

## Per Asset Type, Document:

1. **Risk event inventory** — everything that can go wrong, from industry
   knowledge, insurance claims, and O&M records
2. **Financial mechanism per event** — BI, degradation, catastrophic,
   performance, indirect
3. **Climate linkage** — is it climate-sensitive? Which variables drive it?
4. **Quantifiability** — CMIP6? ERA5? Insurance data? Not quantifiable?
5. **Priority ranking** — by estimated financial materiality
6. **Coverage map** — FULL / PARTIAL / PROXY / GAP for each risk

## Depends On
- [top_down_meets_bottom_up.md](../discussion/architecture/top_down_meets_bottom_up.md) — foundational justification
- [plan_climate_risk_orchestrator.md](plan_climate_risk_orchestrator.md) — where these profiles feed into
