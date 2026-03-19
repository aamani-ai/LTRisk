---
title: "Discussion — LTRisk Framework Architecture"
type: discussion
domain: climate-risk / project-finance / architecture
created: 2026-03-19
status: proposed framework — structure is established, dollar estimates are theoretical pending NB04/NB05
context: >
  This doc consolidates the high-level LTRisk framework into one place.
  The two-channel structure, variable routing, notebook pipeline, and NAV
  rollup are documented in detail across learning docs 07-09, several
  discussion docs, and the whitepaper. This is the architectural overview
  that ties them together — the "system map" you hand someone so they
  immediately understand how the pieces connect.
relates-to:
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/learning/C_financial_translation/08_efr_equipment_degradation.md
  - docs/learning/C_financial_translation/09_nav_impairment_chain.md
  - docs/discussion/discussion_ltrisk_cashflow_integration.md
  - docs/discussion/discussion_scvr_performance_adjustment.md
  - docs/discussion/discussion_hcr_pathway_a_vs_b.md
  - docs/discussion/discussion_scvr_method_equivalence.md
---

# LTRisk Framework Architecture

> **Purpose:** One-page system map. Shows the two financial channels, how
> SCVR feeds each, which variables matter, and how everything rolls into NAV.
> For deep dives, follow the cross-references to specific docs.

---

## 1. The Core Insight

Climate change for renewable assets affects two things: **equipment degradation
under heat stress** and **hazard event frequency**. Our initial SCVR results
also show that the resource itself (sun, wind) is largely stable at these sites
— but the relative importance of each channel is an open question that NB04/NB05
will quantify.

```
  WHAT CLIMATE CHANGE DOES               WHERE IT DOESN'T ACT DIRECTLY
  ──────────────────────────             ─────────────────────────────
  Temperatures rise (strong signal)       Solar irradiance: ~stable (SCVR ≈ 0)
  Extreme events intensify               Wind speeds: ~stable (SCVR ≈ 0)
  Equipment ages faster under stress      The "fuel supply" itself stays put
  More heat waves, floods, hail

  BUT: generation DOES decline — through equipment aging (Channel 2),
  not through resource change (Channel 3). The sun keeps arriving;
  the panels receiving it degrade faster under heat stress.

  There are also small secondary performance effects from temperature:
    Solar thermal derating: ~0.3% by 2050 (panels less efficient when hot)
    Wind air density loss:  ~0.5% (warmer air is less dense)
    Wind icing reduction:   ~0.5% (fewer shutdowns — nearly cancels density)
  Initial estimates suggest these are much smaller than EFR life-shortening,
  but actual ratios will come from NB04/NB05 computation.
  See: discussion_scvr_performance_adjustment.md for the full analysis.

  Year-to-year weather VARIABILITY (which drives DSCR P10/P90 spread)
  is handled separately by the bootstrap in project_finance (40yr ERA5
  through PVLib/PyWake). SCVR measures distribution SHIFT, not WIDTH.
```

This shapes the framework: climate risk is expected to enter the financial
model through **equipment degradation** (Channel 2) and **business interruption**
(Channel 1). Direct resource change (Channel 3) appears negligible at these
sites based on SCVR results. The relative weight of Channel 1 vs Channel 2
is a key question for NB04/NB05 to answer — initial theoretical estimates
(doc 09) suggest Channel 2 may be larger, but this needs validation with
actual computed HCR and EFR values.

---

## 2. The Two Channels

Climate risk flows to asset value through two independent financial channels,
each with its own mechanism and driver metric:

```
                      ┌─────────────────────────────────────────────────────┐
                      │          CHANNEL 1: BUSINESS INTERRUPTION            │
                      │                                                     │
                      │  Mechanism:  Hazard events cause shutdowns/downtime │
                      │  Driver:     HCR (Hazard Change Ratio)              │
                      │  Math:       CFADS -= BI_loss(t)    [additive]      │
                      │  Examples:   Heat wave curtailment, flood downtime, │
                      │              hail damage, icing                     │
                      │  Variables:  pr, hurs, tasmax (via thresholds)      │
                      │  Character:  Per-year loss, not cumulative          │
                      └─────────────────────────────────────────────────────┘

                      ┌─────────────────────────────────────────────────────┐
                      │          CHANNEL 2: EQUIPMENT DEGRADATION            │
                      │                                                     │
                      │  Mechanism:  Climate stress accelerates aging       │
                      │  Driver:     EFR (Equipment Failure Ratio)          │
                      │  Math:       CFADS *= (1 - degrad(t)) [multiplicat.]│
                      │              + truncation at IUL      [life cut]    │
                      │  Models:     Peck's thermal aging                   │
                      │              Coffin-Manson thermal cycling           │
                      │              Palmgren-Miner wind fatigue             │
                      │  Variables:  tasmax, tasmin, tas, hurs              │
                      │  Character:  Cumulative + life-shortening           │
                      └─────────────────────────────────────────────────────┘
```

**Why Channel 2 may be the larger driver (hypothesis — to be validated in NB04/NB05):**
1. Degradation **compounds** year-over-year (each year's loss cascades)
2. Life shortening **eliminates tail-year revenue** entirely
3. Peck's model doubles degradation rate every 10°C — small warming has large effects
4. Post-debt years are highest-value (after amortization) — losing them hurts most

Initial theoretical estimates (doc 09) suggest Channel 2 could account for the
majority of NAV impairment, but this is based on illustrative worked examples,
not computed results. The actual split will come from NB04 (HCR/EFR computation)
and NB05 (financial integration).

There is also a **Channel 3** (resource change — rsds/sfcWind SCVR), which
appears negligible at these sites based on near-zero SCVR values. See
[discussion_scvr_performance_adjustment.md](discussion_scvr_performance_adjustment.md) for the analysis.

---

## 3. End-to-End Pipeline

```
PHASE A — Parameter Computation (LTRisk, once per scenario)
═══════════════════════════════════════════════════════════════════════

  CMIP6 daily ──► SCVR(t) ──┬──► HCR(t) → BI_loss(t)      (Channel 1)
  (NB02+NB03)     (NB03)    │    (NB04)
                             └──► EFR(t) → IUL              (Channel 2)
                                  (NB04)

  SCVR must be computed first. Then HCR and EFR are computed
  in PARALLEL from SCVR — they are independent channels.


PHASE B — Cash Flow Adjustment (project_finance, simultaneous per year)
═══════════════════════════════════════════════════════════════════════

  For each year t in project life:

    CFADS_adjusted(t) = Revenue(t)
                        × (1 - EFR(t))        ← Channel 2: degradation
                        - BI_loss(t)           ← Channel 1: hazard shutdowns
                        - OpEx(t)

    If t > IUL: CFADS_adjusted = 0             ← Channel 2b: life truncation

    DSCR(t) = CFADS_adjusted(t) / DebtService(t)
```

### Illustrative Dollar Breakdown — Hayhurst Solar SSP5-8.5

> **Note:** These figures are from theoretical worked examples in doc 09
> (learning/09_nav_impairment_chain.md), not from computed NB04/NB05 results.
> They illustrate the *structure* of how the channels combine, not final
> numbers. Actual values will come from NB04 (HCR/EFR) and NB05 (NAV).

```
  ┌──────────────────────────────────────────────────────┐
  │  HAYHURST SOLAR SSP5-8.5  (illustrative estimates)    │
  │  Asset value: $60M                                     │
  │                                                        │
  │  Channel 2 (IUL shortening):  ~$5.1M                  │
  │  Channel 1 (Hazard BI):      ~$1.2M                  │
  │  Channel 3 (rsds upside):   ~-$0.4M                  │
  │  ─────────────────────────────────────────             │
  │  Total NAV impairment:       ~$5.9M  (~10%)           │
  │                                                        │
  │  These are initial estimates. The channel split and    │
  │  absolute values need validation through NB04/NB05.    │
  └──────────────────────────────────────────────────────┘
```

---

## 4. Variable → Channel Routing

Not all 7 climate variables feed both channels equally. The SCVR Report Card
(Tail Confidence flag) determines how each variable's SCVR is routed:

```
  Variable    SCVR Signal    Report Card    Primary Channel   Routing
  ────────    ───────────    ───────────    ───────────────   ────────────────
  tasmax      +0.069/+0.080  HIGH           Channel 2 (EFR)   SCVR → Peck's
  tasmin      +0.144/+0.174  MODERATE       Channel 2 (EFR)   SCVR → Peck's + caveat
  tas         +0.088/+0.104  HIGH           Channel 2 (EFR)   SCVR → Peck's
  pr          -0.001/-0.007  DIVERGENT      Channel 1 (HCR)   Pathway B only
  sfcWind     -0.022/-0.026  MODERATE/HIGH  Channel 1 (HCR)   SCVR → HCR scale
  hurs        -0.031/-0.036  MODERATE       Both               SCVR + P95 flagged
  rsds        +0.005/+0.003  MODERATE       Channel 3 (tiny)   Document, don't adjust
```

### How Report Card Confidence Affects Routing

```
  Confidence   Channel 2 (EFR/IUL)              Channel 1 (HCR)
  ──────────   ──────────────────────           ──────────────────────
  HIGH         Use SCVR directly in Peck's      Pathway A (SCVR × scale)
               Full trust                       + Pathway B cross-validate

  MODERATE     Use SCVR but flag uncertainty     Prefer Pathway B
               Range: SCVR ± model IQR          Pathway A as secondary

  LOW          Do not use SCVR alone             Pathway B mandatory
               Report P95 alongside             P95 alongside SCVR

  DIVERGENT    SCVR excluded from Channel 2      Pathway B only
               Mean gives wrong direction        SCVR is misleading
```

**Critical example:** Precipitation (pr) is DIVERGENT — mean SCVR says "no
change" but P95 says "extreme rainfall increasing." Using mean SCVR for flood
HCR would miss the tail risk entirely. Pathway B (count actual hazard days)
is mandatory.

---

## 5. Notebook Pipeline

```
  NB 01 ──► NB 02 ──► NB 03 ──► NB 04 ──► NB 05+
  Climate    THREDDS    SCVR       HCR+EFR   Financial
  Indices    Pipeline   Compute    Compute    Model
                                               │
                                               ▼
                                          NAV impairment
                                          DSCR trajectory

  ┌──────────────────────────────────────────────────────────────────┐
  │ NB 01: Climate Indices (annual hazard counts)                    │
  │   heat_wave_days(t), frost_days(t), rx5day(t), fwi_mean(t)     │
  │   → Used for HCR cross-validation in NB04                       │
  │                                                                  │
  │ NB 02: NEX-GDDP THREDDS Pipeline                                │
  │   Daily CMIP6 data from THREDDS, cached as NetCDF                │
  │   → Input to NB03                                                │
  │                                                                  │
  │ NB 03: SCVR Computation  ✅ BUILT                                │
  │   7 variables × 2 scenarios × 28-31 models                      │
  │   Epoch + decade SCVR, Report Card, decomposition                │
  │   → Output: scvr_summary_<var>.json per variable                 │
  │                                                                  │
  │ NB 04: HCR + EFR Computation  ✅ HCR DONE (Part A)               │
  │   SCVR(t) → HCR(t) per hazard (scaling or Pathway B)            │
  │   SCVR(t) → EFR(t) per mechanism (Peck's, Coffin-Manson, P-M)  │
  │   Cross-validate HCR against NB01 climate indices                │
  │   → Output: annual HCR + EFR tables per site per scenario        │
  │                                                                  │
  │ NB 05+: Financial Model / NAV Impairment  ◻ FUTURE              │
  │   Apply HCR + EFR to CFADS cash flow model                      │
  │   NAV impairment, DSCR trajectory, IRR adjustment                │
  │   Bridge to project_finance repo                                 │
  └──────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
  THREDDS → daily NetCDF → SCVR(t) ──┬──► HCR(t) ──┐
  (NB02)    (cache)        (NB03)     │    (NB04)    ├──► CFADS_adj(t) → NAV
                             ↑        └──► EFR(t) ──┘    (NB05)         (NB05)
                             │             (NB04)
                    NB01 climate indices (cross-validation for HCR)
```

---

## 6. Key Metrics — Compact Glossary

| Metric | What It Is | Computed In | Feeds Into |
|--------|-----------|-------------|------------|
| **SCVR** | Fractional shift in exceedance curve area (baseline → future) | NB03 | HCR, EFR |
| **HCR** | % increase in hazard events (SCVR × scaling factor or direct count) | NB04 | BI_loss → Channel 1 |
| **EFR** | Fractional acceleration of equipment degradation (Peck's, C-M, P-M) | NB04 | Generation deduction → Channel 2 |
| **IUL** | Impaired Useful Life — shortened operational lifetime | NB04 | CFADS truncation → Channel 2b |
| **BI** | Business Interruption — revenue lost to hazard downtime | NB04/05 | CFADS deduction → Channel 1 |
| **NAV** | Net Asset Value — dollar impairment from all channels combined | NB05 | Final output |
| **DSCR** | Debt Service Coverage Ratio (CFADS / debt service) | Financial model | Covenant testing |
| **CFADS** | Cash Flow Available for Debt Service | Financial model | DSCR computation |

---

## 7. The Report Card as Router

The SCVR Report Card is the "intelligence layer" that makes the framework
variable-specific rather than one-size-fits-all:

```
                    ┌──────────────┐
                    │  SCVR(var)   │
                    │  7 variables │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Report Card   │  Tail Confidence: HIGH / MODERATE /
                    │ (decompose)   │  LOW / DIVERGENT
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        HIGH/MODERATE     LOW        DIVERGENT
              │            │            │
              ▼            ▼            ▼
        Use SCVR in     Pathway B    Pathway B only
        Channel 2       mandatory    SCVR excluded
        (EFR/IUL)       Flag P95    from Channel 2
        + Pathway A     alongside
        cross-validate
```

Without the report card, you'd either trust all SCVR values equally (wrong —
pr DIVERGENT would give misleading EFR) or distrust all of them (wasteful —
tasmax HIGH is perfectly reliable). The report card enables **per-variable
routing** so each variable enters the pipeline through the right door.

---

## 8. Projected Scenario Comparison (Theoretical)

> **These are projections from initial theoretical modeling (doc 09), not
> computed results.** They represent our current hypothesis about the
> magnitude and direction of climate impacts. NB04/NB05 will produce
> the actual numbers — which may differ significantly.

### What the initial estimates suggest

```
                    No Climate    SSP2-4.5        SSP5-8.5
                    ──────────    ────────        ────────
  HAYHURST SOLAR
  NAV impairment:    $0           ~$3M (est.)     ~$6M (est.)
  IUL:               25 years     ~22-23 years    ~20-22 years

  MAVERICK WIND
  NAV impairment:    $0           ~$0 (est.)      ~$0.5M (est.)
  IUL:               25 years     ~24-25 years    ~24 years
```

**Directional expectations** (high confidence, even before NB04):
- Solar will be more impaired than wind (temperature is the dominant SCVR signal)
- SSP5-8.5 will produce larger impairment than SSP2-4.5
- Channel 2 (degradation) will likely be material for solar assets

**Open questions** (requires NB04/NB05 to answer):
- Exact channel split — how much is Channel 1 vs Channel 2?
- Absolute dollar amounts — the estimates above could be off by 2-3x
- Whether DSCR covenant breaches are real or artifacts of simplified assumptions
- Sensitivity to BI conversion approach (top-down vs bottom-up vs benchmarks)

---

## Cross-References

| Topic | Doc | What it covers |
|-------|-----|---------------|
| HCR deep dive | [07_hcr_hazard_change.md](../learning/C_financial_translation/07_hcr_hazard_change.md) | Scaling factors, annual HCR, Pathway A vs B, cross-validation |
| EFR deep dive | [08_efr_equipment_degradation.md](../learning/C_financial_translation/08_efr_equipment_degradation.md) | Peck's, Coffin-Manson, Palmgren-Miner with worked examples |
| NAV chain | [09_nav_impairment_chain.md](../learning/C_financial_translation/09_nav_impairment_chain.md) | SCVR → (HCR + EFR) → CFADS → NAV two-channel walkthrough |
| Cash flow integration | [discussion_ltrisk_cashflow_integration.md](discussion_ltrisk_cashflow_integration.md) | How LTRisk connects to project_finance, BI conversion approaches |
| Performance assessment | [discussion_scvr_performance_adjustment.md](discussion_scvr_performance_adjustment.md) | Why Channel 3 is negligible — the resource is stable |
| HCR pathways | [discussion_hcr_pathway_a_vs_b.md](discussion_hcr_pathway_a_vs_b.md) | When SCVR-based HCR (Pathway A) fails and Pathway B is needed |
| Report Card algorithm | [03_integrated_scvr_cmip6.md §3b.F](../implementation/03_integrated_scvr_cmip6.md) | Tail Confidence decision tree, guard thresholds, actual results |
| SCVR methodology | [04_scvr_methodology.md](../learning/B_scvr_methodology/04_scvr_methodology.md) | SCVR formula, exceedance curve area, empirical computation |
| Companion metrics | [discussion_scvr_method_equivalence.md §13](discussion_scvr_method_equivalence.md) | Why mean SCVR alone isn't enough, Tail Confidence design rationale |
