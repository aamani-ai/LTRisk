---
title: "LTRisk Framework Architecture"
type: discussion
domain: climate-risk / project-finance / architecture
created: 2026-03-19
updated: 2026-04-09
status: >
  Architecture established. SCVR pipeline and dashboard are production.
  Orchestrator, HCR reclassification, and EFR two-mode architecture are
  documented. Financial channel calculations are defined with open
  questions on BI parameters. NB04 implementation pending.
context: >
  This doc is the "system map" — the one document you hand someone so they
  immediately understand how the LTRisk pieces connect. It consolidates
  the two-channel structure, the orchestrator routing layer, variable
  routing, the notebook pipeline, and how LTRisk complements InfraSure's
  hazards repo pipeline.
relates-to:
  - docs/learning/B_scvr_methodology/04_scvr_methodology.md
  - docs/learning/C_financial_translation/06b_climate_risk_orchestrator.md
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/learning/C_financial_translation/08_efr_equipment_degradation.md
  - docs/learning/C_financial_translation/09_nav_impairment_chain.md
  - docs/discussion/hcr_financial/hcr_efr_boundary.md
  - docs/discussion/hcr_financial/channel_1_bi_calculation.md
  - docs/discussion/efr_degradation/efr_two_modes.md
  - docs/discussion/efr_degradation/channel_2_efr_financial.md
  - docs/discussion/architecture/pipeline_complementarity.md
  - docs/discussion/architecture/top_down_meets_bottom_up.md
  - docs/discussion/bi_methodology/01_what_is_bi.md
  - docs/discussion/uncertainty/FIDUCEO-Style Uncertainty Mapping_ LTRisk.md
---

# LTRisk Framework Architecture

> **Purpose:** One-page system map. Shows how SCVR feeds the orchestrator,
> how the orchestrator routes signals to two financial channels, how each
> channel translates climate to dollars, and where open questions remain.

---

## 1. The Core Insight

Climate change for renewable assets affects two things: **equipment degrades
faster under heat stress** (Channel 2) and **hazard events become more
frequent** (Channel 1). The resource itself (sun, wind) is largely stable.

```
WHAT CLIMATE CHANGE DOES                WHAT IT DOESN'T DO
──────────────────────────              ──────────────────
Temperatures rise (strong SCVR)         Solar irradiance: stable (SCVR ≈ 0)
Extreme events intensify                Wind speeds: stable (SCVR ≈ 0)
Equipment ages faster under stress      The "fuel supply" stays put
More heat waves, floods

FINDING (confirmed):
  Channel 2 (equipment degradation) >> Channel 1 (business interruption)
  by roughly 50-250× at our pilot sites.

  The dominant risk is NOT more shutdowns.
  The dominant risk IS that panels die 2-4 years early.
  IUL shortening accounts for ~86% of total NAV impairment.
```

The framework also recognises that LTRisk covers only PART of the risk
picture. InfraSure's hazards repo covers historical acute events (hail,
tornado, strong wind) that LTRisk cannot project from CMIP6. Together,
the two pipelines cover more than either alone. See
[pipeline_complementarity.md](pipeline_complementarity.md).

---

## 2. The Architecture — SCVR → Orchestrator → Channels

```
                        SCVR Report
                        (7 variables, 6+ metrics each,
                         Tail Confidence per variable)
                              │
                              ▼
                    ┌───────────────────┐
                    │   ORCHESTRATOR    │
                    │                   │
                    │ Hazard Taxonomy   │  ← What climate events exist
                    │ Metric Selector   │  ← Which SCVR metric to trust
                    │ Channel Router    │  ← Where output flows
                    │ Coverage Map      │  ← What we cover vs gaps
                    │                   │
                    │ Routing rule:     │
                    │  Tail Conf. HIGH  │  → Mode/Pathway A (SCVR-based)
                    │  Tail Conf. DIV   │  → Mode/Pathway B (daily data)
                    └────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        CHANNEL 1      CHANNEL 2      RISK FLAGS
        (BI / HCR)     (EFR)          + GAPS
              │              │              │
         ┌────┴────┐   ┌────┴────┐         │
         │         │   │         │         │
       Path A   Path B Mode A  Mode B     Flagged
       SCVR×    Daily  SCVR→   Daily      (no det.
       scaling  count  physics integr.    $ yet)
         │         │   │         │         │
         ▼         ▼   ▼         ▼         ▼
      BI_loss(t)   climate_degrad(t)    Direction
      (additive)   + IUL truncation    + magnitude
                   (multiplicative)
              │              │
              └──────┬───────┘
                     ▼
             CFADS_adjusted(t) = Revenue × (1-EFR) - BI_loss - OpEx
             If t > IUL: CFADS = 0
                     │
                     ▼
             NAV impairment = Σ [CFADS_base - CFADS_adj] / (1+r)^t
```

See [06b_climate_risk_orchestrator.md](../../learning/C_financial_translation/06b_climate_risk_orchestrator.md) for the full routing matrix, hazard taxonomy, and YAML schema.

---

## 3. Channel 1 — Business Interruption (HCR)

### What It Captures

Revenue lost because the asset could not produce electricity during a
period when it otherwise would have. Caused by operational shutdowns,
curtailment, or site inaccessibility from hazard events.

### Three Categories of Hazard Events

Not all hazards flow through Channel 1. The framework classifies hazards
into three categories based on financial mechanism (see [hcr_efr_boundary.md](../hcr_financial/hcr_efr_boundary.md)):

```
CATEGORY 1 — BI Events (Channel 1):
  Heat wave curtailment    → Pathway A (SCVR × 2.5)
  Extreme precipitation    → Pathway B (daily counting, mandatory)
  Flood (Rx5day)           → Pathway B (mandatory)
  Wind cut-out             → Pathway A (SCVR × 1.0)
  Icing shutdown           → Pathway B (compound threshold)

CATEGORY 2 — Degradation (→ Channel 2 instead):
  Freeze-thaw cycles       → EFR Mode B (Coffin-Manson)
  Frost days               → EFR Mode B (cold stress)
  Cold wave                → EFR Mode B (thermal shock)
  These do NOT cause BI — the plant operates normally.
  They cause cumulative material fatigue.

CATEGORY 3 — Risk Indicators (flagged, no $ formula):
  Fire weather (FWI)       → Direction + magnitude flagged
  Dry spell                → Soiling risk flagged
  High FWI day ≠ actual fire. Deterministic $ formula
  gives false precision for probabilistic events.
```

### Two Computation Pathways

```
Pathway A: HCR = SCVR × scaling_factor (fast, parametric)
  Used when: Tail Confidence HIGH (temperature hazards)
  Example:   HCR_heat = 0.080 × 2.5 = +0.200 (+20% more heat days)

Pathway B: HCR = (count_future - count_baseline) / count_baseline
  Used when: Tail Confidence DIVERGENT (precipitation) or compound thresholds
  Example:   HCR_flood from Rx5day daily counting = +0.020
  Mandatory for pr because Pathway A gives wrong sign (Jensen's inequality)
```

### Financial Translation (Open Questions)

```
BI_loss(t) = Σ_hazards [HCR_h(t) × baseline_BI_h × Revenue(t)]

OPEN: baseline_BI_h is the critical unknown.
  Three approaches documented (see channel_1_bi_calculation.md):
    A. Top-down: % of revenue (assumed, 0.5-2.0%)
    B. Bottom-up: shutdown hours × capacity × price (needs O&M data)
    C. Benchmarks: industry-reported rates
  
  Hazards repo EAL may provide baseline for hail/tornado/wind.
  Heat/flood/icing baseline not yet available from either pipeline.

OPEN: BI definition (three options in 01_what_is_bi.md):
    A. Deterministic counterfactual (simplest)
    B. Weather-conditional (captures seasonality)
    C. Probabilistic (produces distribution of BI)

CONFIRMED: Channel 1 BI is ~50-250× smaller than Channel 2 EFR
  at Hayhurst Solar. Equipment degradation dominates.
```

---

## 4. Channel 2 — Equipment Degradation (EFR)

### What It Captures

Revenue lost because equipment ages faster under climate stress, leading
to (a) reduced annual generation and (b) shortened asset life (IUL).

### Three Physics Models

```
Peck's Thermal Aging (dominant for solar):
  AF = exp(Ea/k × (1/T_ref - 1/T_stress))
  INPUT: SCVR_tas, SCVR_hurs → Mode A (SCVR-based)
  OUTPUT: EFR_peck ≈ 0.11 (11% faster aging)
  Mechanism: Arrhenius — chemical degradation doubles every 10°C

Coffin-Manson Thermal Cycling:
  N_f = C × (ΔT)^(-β)
  INPUT: Daily freeze-thaw counts → Mode B (mandatory)
  OUTPUT: EFR_coffin ≈ NEGATIVE at Hayhurst (fewer cycles = benefit)
  Mechanism: Each 0°C crossing fatigues solder joints
  NOTE: Mode A gives WRONG DIRECTION (+3%). Mode B gives correct (-25%).

Palmgren-Miner Wind Fatigue:
  D = Σ(n_i / N_i)
  INPUT: SCVR_sfcWind → Mode A (SCVR ≈ 0 at pilot sites)
  OUTPUT: EFR_palmgren ≈ 0 (wind distribution unchanged)
```

### Two Computation Modes

```
Mode A: Apply physics model to SCVR mean-shifted conditions (fast)
  Used when: Tail Confidence HIGH and function is ~linear locally
  Phase 1 default for Peck's and Palmgren-Miner

Mode B: Integrate physics model over actual daily data (exact)
  Used when: Mode A gives wrong direction (Coffin-Manson)
  Mandatory for Coffin-Manson — same Jensen's inequality as HCR Pathway B
  Phase 2 upgrade for Peck's (~10% more accurate)
```

### Two Financial Effects

```
EFFECT 1: Annual Generation Reduction (gradual, every year)
  climate_degrad(t) = EFR_combined(t) × std_degrad_rate × t
  Impact: ~$0.5-1.0M NPV (~14% of Channel 2)

EFFECT 2: Life Truncation via IUL (terminal, at the NAV level)
  If t > IUL: CFADS = 0 (asset reaches end-of-life early)
  Impact: ~$2.8-5.1M NPV (~86% of Channel 2)
  This is the DOMINANT driver of total NAV impairment.

OPEN: IUL computation method
  Option A (Phase 1): IUL = EUL × (1 - avg_EFR)
  Option B (Phase 2): Cumulative degradation until threshold
  Threshold: 80% capacity (IEC)? 85%? 12.5% cumulative loss?
```

---

## 5. The Unified Routing Logic

The Report Card's Tail Confidence flag drives routing for BOTH channels
using the SAME decision criteria:

```
Tail Confidence    Channel 1 (HCR)        Channel 2 (EFR)
──────────────     ──────────────         ──────────────
HIGH               Pathway A preferred    Mode A preferred
                   (cross-validate B)     (Peck's from SCVR)

MODERATE           Pathway A + B          Mode A + B
                   (compare, flag)        (report range)

LOW                Pathway B preferred    Mode B preferred
                   (A unreliable)         (A underestimates)

DIVERGENT          Pathway B only         Mode B only
                   (A wrong sign)         (A wrong direction)
```

### Variable → Channel Routing

```
Variable    SCVR Signal    Tail Conf.   Primary Channel    Mode/Pathway
────────    ───────────    ──────────   ───────────────    ────────────
tasmax      +0.080         HIGH         Ch2 (Peck's)       Mode A
tasmin      +0.173         MODERATE     Ch2 (Peck's+C-M)   A(Peck) + B(C-M)
tas         +0.105         HIGH         Ch2 (Peck's)       Mode A
pr          -0.007         DIVERGENT    Ch1 (flood BI)      Pathway B only
sfcWind     -0.026         MOD/HIGH     Ch1 (wind BI)       Pathway A
hurs        -0.036         MODERATE     Both (Peck's+BI)    Mode A + flag
rsds        +0.003         MODERATE     Ch3 (negligible)    Document only
```

---

## 6. Pipeline Complementarity — LTRisk + Hazards Repo

InfraSure has TWO risk pipelines that cover DIFFERENT hazards:

```
                    Hazards Repo              LTRisk
                    (NOAA 1996-2024)          (CMIP6 2026-2055)
                    ────────────────          ──────────────────
Question:           "What hurts today?"       "What hurts MORE tomorrow?"
Hazards:            Hail, tornado, wind       Heat, flood, degradation
Data:               NOAA storm events         28 CMIP6 models daily
Output:             Annual BI ($)             HCR (% change), EFR (ratio)
Financial:          Damage curves → $         HCR×baseline → $, EFR→IUL

COMPLEMENTARITY:
  Hail:          Hazards repo FULL    │  LTRisk GAP (no CAPE in CMIP6)
  Heat wave:     Hazards repo GAP     │  LTRisk FULL (HCR + Peck's)
  Tornado:       Hazards repo FULL    │  LTRisk GAP
  Flooding:      Both (partial)       │  Cross-validate
  Degradation:   Hazards repo N/A     │  LTRisk FULL (Peck's, C-M, P-M)

COMBINED: climate-adjusted risk = baseline_EAL × (1 + HCR)
  For hazards both cover: cross-validate
  For hazards only A covers: use historical EAL (no climate delta)
  For hazards only B covers: use LTRisk projection (need baseline)
```

See [pipeline_complementarity.md](pipeline_complementarity.md) for the full analysis.

---

## 7. Notebook Pipeline

```
NB 01 ──► NB 02 ──► NB 03 ──► NB 04 ──► NB 05+
Climate    THREDDS    SCVR       HCR+EFR   Financial
Indices    Pipeline   Compute    Compute    Model

┌──────────────────────────────────────────────────────────┐
│ NB 01: Climate Indices (annual hazard counts)  ✅ BUILT  │
│   heat_wave_days, frost_days, rx5day, fwi_mean           │
│   → Used for HCR Pathway B cross-validation              │
│                                                          │
│ NB 02: NEX-GDDP THREDDS Pipeline  ✅ BUILT               │
│   Daily CMIP6 data from NASA, cached as NetCDF           │
│                                                          │
│ NB 03: SCVR Computation  ✅ BUILT + DASHBOARD LIVE        │
│   7 variables × 2 scenarios × 28-31 models               │
│   Report Card with Tail Confidence, companion metrics    │
│   Dashboard: ltrisk-*.streamlit.app                      │
│                                                          │
│ NB 04: HCR + EFR Computation  ✅ HCR Part A DONE          │
│   Pending: 3-category reclassification                   │
│   Pending: EFR Mode B for Coffin-Manson                  │
│   Pending: Regenerate outputs with corrected routing     │
│                                                          │
│ NB 05+: Financial Model / NAV Impairment  ◻ FUTURE       │
│   Apply HCR + EFR to CFADS cash flow model               │
│   Bridge to project_finance repo                         │
└──────────────────────────────────────────────────────────┘
```

---

## 8. Key Metrics — Compact Glossary

| Metric | What It Is | Computed In | Feeds Into |
|--------|-----------|-------------|------------|
| **SCVR** | Fractional mean shift in climate variable distribution | NB03 | Orchestrator |
| **Report Card** | 6 companion metrics + Tail Confidence flag per variable | NB03 | Orchestrator (routing) |
| **HCR** | % change in BI hazard event frequency | NB04 | BI_loss → Channel 1 |
| **EFR** | Fractional acceleration of equipment degradation | NB04 | Generation decline → Channel 2 |
| **IUL** | Impaired Useful Life — shortened operational lifetime | NB04 | CFADS truncation → Channel 2 |
| **BI** | Business Interruption — revenue lost to hazard events | NB04/05 | CFADS deduction → Channel 1 |
| **NAV** | Net Asset Value impairment from all channels combined | NB05 | Final output |
| **DSCR** | Debt Service Coverage Ratio (CFADS / debt service) | Financial model | Covenant testing |
| **CFADS** | Cash Flow Available for Debt Service | Financial model | DSCR computation |

---

## 9. Open Questions

These are documented in detail across discussion docs but collected here
for visibility:

| Question | Impact | Where Documented | Status |
|----------|--------|-----------------|--------|
| baseline_BI_pct per hazard | HIGH — drives all of Channel 1 | channel_1_bi_calculation.md | Open: need O&M data or hazards repo EAL |
| BI definition (deterministic vs probabilistic) | MEDIUM | 01_what_is_bi.md | Open: three options, Gen.1 recommendation pending |
| Heat wave BI parameters (forced/recovery hours) | HIGH — connects both pipelines | pipeline_complementarity.md, 01_what_is_bi.md | Open: not defined in either pipeline |
| IUL failure threshold (80%? 85%? 12.5% cumul?) | MEDIUM | channel_2_efr_financial.md | Open: Option A for Phase 1 |
| EFR weights (Peck's vs Coffin-Manson) | LOW-MED | 08_efr §13 | Open: 80/20 working estimate |
| DSCR debt re-sculpting under climate | LOW (Phase 2) | channel_2_efr_financial.md | Open: use fixed DS for Phase 1 |
| Compound hazard confidence rules | LOW (Phase 2) | 06b orchestrator §10 | Open: use lower confidence (conservative) |
| Hazards repo EAL as baseline_BI_pct source | HIGH | pipeline_complementarity.md §8 | Open: would solve Channel 1's biggest unknown |

---

## Cross-References

### Learning Docs (Methodology)
| Topic | Doc |
|-------|-----|
| SCVR Report methodology | [04_scvr_methodology.md](../../learning/B_scvr_methodology/04_scvr_methodology.md) |
| Climate Risk Orchestrator | [06b_climate_risk_orchestrator.md](../../learning/C_financial_translation/06b_climate_risk_orchestrator.md) |
| HCR: Hazard Change Ratio | [07_hcr_hazard_change.md](../../learning/C_financial_translation/07_hcr_hazard_change.md) |
| EFR: Equipment Degradation | [08_efr_equipment_degradation.md](../../learning/C_financial_translation/08_efr_equipment_degradation.md) |
| NAV Impairment Chain | [09_nav_impairment_chain.md](../../learning/C_financial_translation/09_nav_impairment_chain.md) |

### Discussion Docs (Design Decisions)
| Topic | Doc |
|-------|-----|
| HCR/EFR boundary (3-category) | [hcr_efr_boundary.md](../hcr_financial/hcr_efr_boundary.md) |
| EFR two modes (Mode A/B) | [efr_two_modes.md](../efr_degradation/efr_two_modes.md) |
| Channel 1 BI calculation | [channel_1_bi_calculation.md](../hcr_financial/channel_1_bi_calculation.md) |
| Channel 2 EFR financial | [channel_2_efr_financial.md](../efr_degradation/channel_2_efr_financial.md) |
| Pipeline complementarity | [pipeline_complementarity.md](pipeline_complementarity.md) |
| Top-down meets bottom-up | [top_down_meets_bottom_up.md](top_down_meets_bottom_up.md) |
| BI methodology foundations | [01_what_is_bi.md](../bi_methodology/01_what_is_bi.md) |
| FIDUCEO uncertainty mapping | [FIDUCEO uncertainty mapping](../uncertainty/FIDUCEO-Style%20Uncertainty%20Mapping_%20LTRisk.md) |
| SCVR performance adjustment | [scvr_performance_adjustment.md](../scvr_methodology/scvr_performance_adjustment.md) |
| HCR Pathway A vs B | [hcr_pathway_a_vs_b.md](../hcr_financial/hcr_pathway_a_vs_b.md) |
| Jensen's inequality | [jensen_inequality_hcr_scvr.md](../hcr_financial/jensen_inequality_hcr_scvr.md) |
