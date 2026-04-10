---
title: "LTRisk Framework Architecture"
type: discussion
domain: climate-risk / project-finance / architecture
created: 2026-03-19
updated: 2026-04-10
status: >
  Architecture established and aligned with current framework.
  SCVR pipeline production. HCR redefined as expected damage ratio
  (frequency × severity). Canonical hazards from InfraSure hazards repo.
  Severity integration documented with double-counting caveat.
  NB04a/b implemented with 30/30 + 8/8 checks passing.
relates-to:
  - docs/learning/B_scvr_methodology/04_scvr_methodology.md
  - docs/learning/C_financial_translation/06b_climate_risk_orchestrator.md
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/learning/C_financial_translation/08_efr_equipment_degradation.md
  - docs/learning/C_financial_translation/09_nav_impairment_chain.md
  - docs/discussion/hcr_financial/hcr_redefined_freq_severity.md
  - docs/discussion/hcr_financial/hcr_top_down_reframe.md
  - docs/discussion/hcr_financial/severity_sensitivity.md
  - docs/discussion/hcr_financial/pathway_defensibility.md
  - docs/discussion/architecture/pipeline_complementarity.md
  - docs/discussion/bi_methodology/01_what_is_bi.md
---

# LTRisk Framework Architecture

> **Purpose:** One-page system map. Shows how SCVR feeds the orchestrator,
> how the orchestrator routes each canonical hazard to the correct
> computation and financial channel, and where open questions remain.

---

## 1. The Core Insight

Climate change for renewable assets affects two things: **equipment degrades
faster under heat stress** (Channel 2) and **hazard events become more
frequent AND more intense** (Channel 1). The resource itself (sun, wind)
is largely stable.

```
WHAT CLIMATE CHANGE DOES                WHAT IT DOESN'T DO
──────────────────────────              ──────────────────
Temperatures rise (strong SCVR)         Solar irradiance: stable (SCVR ≈ 0)
Events get more frequent AND intense    Wind speeds: stable (SCVR ≈ 0)
Equipment ages faster under stress      The "fuel supply" stays put

CONFIRMED:
  Channel 2 (equipment degradation) >> Channel 1 (business interruption)
  by roughly 50-250× at our pilot sites.

  The dominant risk is NOT more shutdowns.
  The dominant risk IS that panels die 2-4 years early.
  IUL shortening accounts for ~86% of total NAV impairment.

  Channel 1 HCR now captures BOTH frequency AND severity changes.
  For heat wave: frequency +20%, severity +48% → combined range +20-34%.
```

LTRisk covers PART of the risk picture. InfraSure's hazards repo covers
historical acute events (hail, tornado, strong wind) that LTRisk cannot
project from CMIP6. Together, the two pipelines cover more than either
alone. See [pipeline_complementarity.md](pipeline_complementarity.md).

---

## 2. The Architecture

```
                        SCVR Report
                        (7 variables, 6+ metrics each,
                         Tail Confidence per variable,
                         Severity diagnostic)
                              │
                              ▼
                    ┌───────────────────┐
                    │   ORCHESTRATOR    │
                    │                   │
                    │ 10 canonical      │  ← From InfraSure hazards repo
                    │ hazards           │
                    │                   │
                    │ For each:         │
                    │  Published        │  ← Scaling where peer-reviewed
                    │  scaling?         │    factor exists (heat wave 2.5×)
                    │  Or direct        │  ← Computation from daily CMIP6
                    │  computation?     │    where it doesn't (flood, ice)
                    │                   │
                    │  Severity         │  ← freq × severity (expected
                    │  integrated?      │    shortfall decomposition)
                    │                   │
                    │  Baseline BI      │  ← From hazards repo (3 hazards)
                    │  available?       │    or NRI EAL proxy (others)
                    └────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        CHANNEL 1      CHANNEL 2      RISK FLAGS
        (HCR → BI)     (EFR)          + GAPS
              │              │              │
        Additional_BI  climate_degrad  Direction
        = baseline_BI  + IUL trunc.    + magnitude
          × HCR        (multiplicat.)  (no $ yet)
        (additive)           │              │
              │              │         Hail, tornado:
              └──────┬───────┘         use hazards repo
                     ▼                 historical BI
             CFADS_adjusted(t)
             = Revenue × (1-EFR)
               - baseline_BI_total
               - Additional_climate_BI
               - OpEx
```

See [06b_climate_risk_orchestrator.md](../../learning/C_financial_translation/06b_climate_risk_orchestrator.md) for the full routing matrix and YAML schema.

---

## 3. Channel 1 — Business Interruption (HCR)

### What HCR Measures

HCR = change in expected annual damage (frequency × severity).
Computed for InfraSure's 10 canonical hazards where data allows.

```
HCR = (1 + frequency_ratio) × severity_ratio - 1

  Where:
    frequency_ratio = change in how often events cross the threshold
    severity_ratio  = change in how far above the threshold (mean excess)
    
  This is the expected shortfall identity — mathematically exact.
```

### Computation Methods

```
Published scaling (where peer-reviewed factor exists):
  Heat wave:    SCVR_tasmax × 2.5 (Diffenbaugh 2017, PNAS)
  Strong wind:  SCVR_sfcWind × 1.0 (trivial, ≈ 0)
  Hurricane:    Knutson 2020 consensus
  Coastal flood: IPCC SLR × exponential amplification
  
  Published scaling IS empirical counting done by other researchers.

Direct computation (where no published scaling exists):
  Riverine flood: Rx5day + daily P95 exceedance from daily pr
  Ice storm:      Compound threshold counting
  Wildfire:       FWI composite from daily data
  Winter weather: Compound threshold counting
  
  For direct counting, severity IS genuinely missing — safe to add
  via expected shortfall decomposition.

BLOCKED (not computable from CMIP6):
  Hail, tornado — use hazards repo historical BI (no climate delta)
```

### Severity Integration

```
For direct counting hazards (flood, etc.):
  HCR_combined = (1 + HCR_freq) × severity_ratio - 1
  No double-counting risk.

For published scaling hazards (heat wave):
  Published 2.5× may already embed severity.
  Report as RANGE: +20% (scaling alone) to +34% (× severity)
  See severity_sensitivity.md for dependencies.

For compound thresholds (ice storm):
  Severity ambiguous for multi-variable conditions.
  Keep frequency-only.
```

### BI Connection

```
Additional_climate_BI = baseline_BI × HCR

  baseline_BI: from hazards repo (when available — Hail, Tornado, Strong Wind)
  HCR: from LTRisk (when computable — Heat, Flood, Ice, Wildfire)
  
  BI ≠ EAL. BI = lost revenue from downtime. EAL = total economic loss.
  Applying HCR (damage-level) to BI assumes linearity (documented assumption).
  
  Current gap: 0/10 hazards have BOTH baseline_BI + HCR.
  Hazards repo has BI for 3 hazards LTRisk can't project.
  LTRisk can project 7 hazards the repo has no BI for.
```

---

## 4. Channel 2 — Equipment Degradation (EFR)

### What EFR Measures

EFR = fractional acceleration of equipment degradation rate.
Produces TWO financial effects:
- Effect 1: Annual generation reduction (gradual, ~14% of NAV impact)
- Effect 2: IUL life truncation (terminal, ~86% of NAV impact)

### Three Physics Models

```
Peck's Thermal Aging (dominant for solar):
  Published Arrhenius equation: AF = exp(Ea/k × (1/T_ref - 1/T_stress))
  Input: SCVR_tas (mean temperature shift)
  EFR_peck ≈ +15.6% (SSP585, Hayhurst)

Coffin-Manson Thermal Cycling:
  Direct freeze-thaw cycle counts from daily data
  Published mean approximation gives wrong direction — direct counts mandatory
  EFR_coffin ≈ -30.1% (SSP585, fewer cycles = benefit)

Palmgren-Miner Wind Fatigue:
  Published S-N framework from SCVR_sfcWind
  SCVR_sfcWind ≈ 0 → EFR_palmgren ≈ 0 (wind distribution unchanged)

Combined: EFR = 80% × Peck's + 20% × Coffin-Manson
  ≈ +6.5% (SSP585), IUL = 23.4 years (EUL=25, 1.6 years lost)
```

---

## 5. The Routing Logic

### For Each Canonical Hazard

```
1. Can LTRisk compute an HCR?
   → Published scaling exists? Use it.
   → No published scaling? Compute from daily CMIP6 data.
   → Data not available? Documented gap.

2. Is severity integrated?
   → Direct counting: yes (combined freq × severity)
   → Published scaling: report as range (may embed severity)
   → Compound threshold: no (severity ambiguous)

3. Does baseline BI exist?
   → Hazards repo has full BI: Hail, Tornado, Strong Wind
   → NRI EAL only (≠ BI): Heat, Flood, Ice, Wildfire, etc.
   → Neither: gaps
```

### Variable → Channel Routing

| Variable | SCVR Signal | Tail Conf. | Primary Channel | Routing |
|---|---|---|---|---|
| tasmax | +0.080 | HIGH | Ch2 (Peck's) + Ch1 (heat wave) | Published scaling (2.5×) for HCR; Arrhenius for EFR |
| tasmin | +0.173 | MODERATE | Ch2 (Peck's + C-M) | Arrhenius + direct cycle counts |
| tas | +0.105 | HIGH | Ch2 (Peck's) | Arrhenius |
| pr | -0.007 | DIVERGENT | Ch1 (flood) | Direct counting mandatory (Jensen's) |
| sfcWind | -0.026 | MOD/HIGH | Ch1 (wind) + Ch2 (P-M) | Published (1.0×); Palmgren-Miner (≈0) |
| hurs | -0.036 | MODERATE | Both (Peck's humidity + BI) | Arrhenius humidity term + BI |
| rsds | +0.003 | MODERATE | Ch3 (negligible) | Document only |

---

## 6. Pipeline Complementarity — LTRisk + Hazards Repo

```
                    Hazards Repo              LTRisk
                    (NOAA 1996-2024)          (CMIP6 2026-2055)
                    ────────────────          ──────────────────
Question:           "What hurts today?"       "What hurts MORE tomorrow?"
Hazards:            Hail, tornado, wind       Heat, flood, degradation
Data:               NOAA storm events         28 CMIP6 models daily
Output:             Annual BI ($)             HCR (freq×sev), EFR (ratio)
Financial:          Damage curves → $         HCR×baseline → $, EFR→IUL

COMPLEMENTARITY:
  Hail:          Hazards repo FULL    │  LTRisk GAP (no CAPE in CMIP6)
  Heat wave:     Hazards repo GAP     │  LTRisk FULL (HCR + Peck's)
  Tornado:       Hazards repo FULL    │  LTRisk GAP
  Flooding:      Both (partial)       │  Cross-validate
  Degradation:   Hazards repo N/A     │  LTRisk FULL (Peck's, C-M, P-M)

COMBINED: future_risk = baseline × (1 + HCR)
  Requires BOTH baseline_BI (from hazards repo) AND HCR (from LTRisk)
  for the same hazard — currently 0/10 have both.
```

See [pipeline_complementarity.md](pipeline_complementarity.md).

---

## 7. Notebook Pipeline

```
NB 01 ──► NB 02 ──► NB 03 ──► NB 04a + 04b ──► NB 05+
Climate    THREDDS    SCVR       HCR     EFR     Financial
Indices    Pipeline   Compute    (Ch1)   (Ch2)   Model

NB 03: SCVR Computation  ✅ PRODUCTION + DASHBOARD LIVE
  7 variables × 2 scenarios × 28-31 models
  Report Card with Tail Confidence, companion metrics, severity diagnostic

NB 04a: HCR (Channel 1)  ✅ IMPLEMENTED (30/30 checks)
  10 canonical hazards (5 BI + 3 degradation + 2 risk indicators)
  Published scaling (heat wave 2.5×) + direct counting (flood, ice)
  Severity integration: freq × severity for direct counting hazards
  Canonical names: heat_wave, riverine_flood_daily/rx5day, strong_wind, ice_storm
  Saves intermediate counts for NB04b

NB 04b: EFR (Channel 2)  ✅ IMPLEMENTED (8/8 checks)
  Peck's (published Arrhenius) + Coffin-Manson (direct cycle counts)
  + Palmgren-Miner (≈ 0). Combined EFR + IUL estimate.
  Reads intermediate from NB04a (no NC loading — runs in seconds)

NB 05+: Financial Model / NAV Impairment  ◻ FUTURE
  Apply HCR + EFR to CFADS cash flow model
  Bridge to project_finance repo
```

---

## 8. Key Metrics — Compact Glossary

| Metric | What It Is | Computed In | Feeds Into |
|---|---|---|---|
| **SCVR** | Fractional mean shift in climate variable distribution | NB03 | Orchestrator |
| **Report Card** | 6 companion metrics + Tail Confidence flag per variable | NB03 | Orchestrator (routing) |
| **HCR** | Change in expected annual damage: frequency_ratio × severity_ratio - 1 | NB04a | Additional_BI → Channel 1 |
| **severity_ratio** | Mean excess above threshold (future / baseline) | NB04a | HCR_combined |
| **EFR** | Fractional acceleration of equipment degradation | NB04b | Generation decline → Channel 2 |
| **IUL** | Impaired Useful Life — shortened operational lifetime | NB04b | CFADS truncation → Channel 2 |
| **BI** | Business Interruption — lost revenue from downtime (NOT the same as EAL) | NB05 | CFADS deduction → Channel 1 |
| **EAL** | Expected Annual Loss — total economic loss (property + BI + indirect) | Hazards repo / NRI | Baseline risk |
| **NAV** | Net Asset Value impairment from all channels combined | NB05 | Final output |
| **DSCR** | Debt Service Coverage Ratio (CFADS / debt service) | Financial model | Covenant testing |
| **CFADS** | Cash Flow Available for Debt Service | Financial model | DSCR computation |

---

## 9. Open Questions

| Question | Impact | Where Documented | Status |
|---|---|---|---|
| Severity double-counting for published scaling | HIGH — 2.5× may embed severity. Report as range. | hcr_redefined_freq_severity.md | Document range (+20% to +34%) |
| Baseline BI gap | HIGH — 0/10 hazards have both baseline_BI + HCR | pipeline_complementarity.md | Need hazards repo BI expansion |
| Linearity assumption (BI ∝ damage) | MEDIUM — underestimates for heat, overestimates for hail | hcr_redefined_freq_severity.md §4 | Documented as Gen.1 assumption |
| Severity sensitivity to threshold | MEDIUM — P90 gives 1.48, P95 might give 1.71 | severity_sensitivity.md | Report sensitivity range |
| Heat wave BI parameters | HIGH — neither pipeline computes heat BI | pipeline_complementarity.md | Need forced_outage_hours defined |
| IUL threshold (80%? 85%? 12.5%?) | MEDIUM | channel_2_efr_financial.md | Option A for Phase 1 |
| EFR weights (Peck's vs C-M) | LOW-MED | 08_efr §13 | 80/20 working estimate |
| DSCR debt re-sculpting | LOW (Phase 2) | channel_2_efr_financial.md | Fixed DS for Phase 1 |

---

## Cross-References

### Learning Docs (Methodology)

| Topic | Doc |
|---|---|
| SCVR Report methodology | [04_scvr_methodology.md](../../learning/B_scvr_methodology/04_scvr_methodology.md) |
| Climate Risk Orchestrator | [06b_climate_risk_orchestrator.md](../../learning/C_financial_translation/06b_climate_risk_orchestrator.md) |
| HCR: Hazard Change Ratio | [07_hcr_hazard_change.md](../../learning/C_financial_translation/07_hcr_hazard_change.md) |
| EFR: Equipment Degradation | [08_efr_equipment_degradation.md](../../learning/C_financial_translation/08_efr_equipment_degradation.md) |
| NAV Impairment Chain | [09_nav_impairment_chain.md](../../learning/C_financial_translation/09_nav_impairment_chain.md) |

### Discussion Docs (Design Decisions)

| Topic | Doc |
|---|---|
| HCR redefined (freq + severity) | [hcr_redefined_freq_severity.md](../hcr_financial/hcr_redefined_freq_severity.md) |
| Top-down canonical reframe | [hcr_top_down_reframe.md](../hcr_financial/hcr_top_down_reframe.md) |
| Severity sensitivity | [severity_sensitivity.md](../hcr_financial/severity_sensitivity.md) |
| Published scaling defensibility | [pathway_defensibility.md](../hcr_financial/pathway_defensibility.md) |
| Pipeline complementarity | [pipeline_complementarity.md](pipeline_complementarity.md) |
| BI methodology | [01_what_is_bi.md](../bi_methodology/01_what_is_bi.md) |
| Channel 1 BI calculation | [channel_1_bi_calculation.md](../hcr_financial/channel_1_bi_calculation.md) |
| Channel 2 EFR financial | [channel_2_efr_financial.md](../efr_degradation/channel_2_efr_financial.md) |
| EFR two modes | [efr_two_modes.md](../efr_degradation/efr_two_modes.md) |
| Top-down meets bottom-up | [top_down_meets_bottom_up.md](top_down_meets_bottom_up.md) |
| FIDUCEO uncertainty | [FIDUCEO uncertainty mapping](../uncertainty/FIDUCEO-Style%20Uncertainty%20Mapping_%20LTRisk.md) |
