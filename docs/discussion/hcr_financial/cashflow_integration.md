---
title: "Discussion — Integrating LTRisk Climate Parameters into Project Finance Cash Flows"
type: discussion
domain: climate-risk / project-finance / integration
created: 2026-03-11
status: draft — needs team review before NB04/NB05 implementation
context: >
  Two repos approach the same problem from opposite directions. project_finance
  has a working CFADS/DSCR model (Gen1) with a 4-stage roadmap. LTRisk has
  SCVR→HCR→EFR parameter pipeline with concrete numbers. This doc bridges
  them — mapping LTRisk outputs to project_finance inputs, clarifying the BI
  conversion question, and defining what "Stage 4" should actually look like.
relates-to:
  - project_finance/docs/cashflow_dscr_methodology.md
  - project_finance/docs/extra/discussions/discussion_scaling_1yr_to_multiyear.md
  - project_finance/docs/extra/discussions/project_finance_opex.md
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/learning/C_financial_translation/08_efr_equipment_degradation.md
  - docs/learning/C_financial_translation/09_nav_impairment_chain.md
  - docs/discussion/scvr_methodology/scvr_performance_adjustment.md
  - docs/discussion/scvr_methodology/annual_scvr_methodology.md
---

# Discussion — Integrating LTRisk into Project Finance Cash Flows

> **The question:** LTRisk produces annual climate parameters (SCVR, HCR, EFR).
> project_finance has a working CFADS/DSCR model. How exactly do these connect?
> What does "18.5% more heat stress" cost in dollars? And where in the CFADS
> waterfall does it show up?

> **Why this matters:** Until the two repos are connected, LTRisk produces
> climate metrics that don't touch a dollar amount, and project_finance
> produces cash flows that assume climate is stationary. Both are incomplete.

> **Decision needed before:** NB04 (HCR/EFR computation) and any climate
> overlay work in project_finance.

---

## 1. The Two-Repo Problem

```
  project_finance                              LTRisk
  ───────────────                              ──────
  Revenue (1000 paths, P10-P90)                SCVR(t) per variable
  OpEx ($22-25/kW-yr solar)                    HCR(t) per hazard
  Debt Service (amortization schedule)         EFR(t) per mechanism
  CFADS = Revenue - OpEx                       IUL = shortened life
  DSCR = CFADS / DS                            NAV impairment (theoretical)
  │                                            │
  │  Gen1: CFADS is FLAT (repeat Year 1)       │  Phase A: parameters computed
  │  Degradation: 0.5%/yr parameter            │  Phase B: apply to cash flows
  │  Climate: NONE (stationarity assumed)       │  Cash flow model: NONE
  │                                            │
  └──── Stage 4 says: "someday add CMIP" ──────┘  Doc 09 says: "overlay on CFADS"
                         │
                         ▼
              THIS DOCUMENT FILLS THE GAP
```

**What project_finance has that LTRisk needs:**
- A working cash flow model with 1000+ probabilistic revenue paths
- Quarterly/semi-annual periodicity matching real loan covenants
- OpEx benchmarks by technology ($22-25/kW-yr solar, $43-48/kW-yr wind)
- DSCR thresholds by rating agency (1.20x solar, 1.30-1.40x wind)
- Amortization structures (level, sculpted)

**What LTRisk has that project_finance needs:**
- Annual SCVR(t) for 7 climate variables (experiment-validated)
- HCR scaling factors mapping climate shift → hazard amplification
- EFR engineering models (Peck's, Coffin-Manson, Palmgren-Miner)
- IUL computation (asset life shortening)
- Concrete numbers: Hayhurst SSP5-8.5 → ~$5.9M impairment (9.8%)

---

## 2. The End-to-End Pipeline

```
PHASE A — Parameter Computation (LTRisk, sequential, once per scenario)
═══════════════════════════════════════════════════════════════════════

  CMIP6 daily data ──► SCVR(t) ──► HCR(t) ──► EFR(t) ──► IUL
  (NB02+NB03)          (NB03)      (NB04)     (NB04)     (NB04)

  Each step DEPENDS on the previous. Cannot compute in parallel.

  Output: annual parameter tables (2026-2055)
    ┌─────────────────────────────────────────────────┐
    │  Year  SCVR_tasmax  HCR_heat  EFR_peck  ...    │
    │  2026  0.048        0.120     0.024     ...    │
    │  2027  0.050        0.125     0.025     ...    │
    │  ...                                           │
    │  2050  0.118        0.295     0.059     ...    │
    └─────────────────────────────────────────────────┘


PHASE B — Cash Flow Adjustment (project_finance, simultaneous per year)
═══════════════════════════════════════════════════════════════════════

  CFADS_base(t) ──► Apply 3 channels ──► CFADS_adjusted(t) ──► DSCR(t)

  The 3 channels act SIMULTANEOUSLY on each year's cash flow:

    ┌─────────────────────────────────────────────────────────────────┐
    │                                                                 │
    │  Channel 1 — Hazard BI (additive loss)                         │
    │    "More heat events → more shutdown hours → less revenue"     │
    │    CFADS -= BI_loss(t)                                         │
    │                                                                 │
    │  Channel 2 — Equipment Degradation (multiplicative)            │
    │    "Faster aging → output declines faster each year"           │
    │    CFADS *= (1 - additional_climate_degradation(t))            │
    │                                                                 │
    │  Channel 2b — Life Shortening (truncation)                     │
    │    "Asset dies at year 21 instead of 25"                       │
    │    CFADS(year 22-25) = 0                                       │
    │                                                                 │
    │  Channel 3 — Resource Change (multiplicative, ~0)              │
    │    "Solar/wind resource itself shifts"                          │
    │    Negligible at these sites (SCVR_rsds ≈ 0, SCVR_sfcWind ≈ 0)│
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 3. The BI Conversion Question — From HCR to Dollars

This is the key gap. LTRisk produces:

```
HCR_heat(2040) = 0.185    "Heat hazard is 18.5% worse than baseline"
```

project_finance needs:

```
BI_loss(2040) = $63,500    "Revenue lost to heat-related downtime this year"
```

How do we bridge this? Three approaches:

### Approach A — Top-Down (% of Revenue)

```
METHOD:
  BI_loss(t) = Revenue(t) × BI_fraction(t)
  BI_fraction(t) = Σ_hazards [ HCR_h(t) × baseline_BI_pct_h ]

WHERE:
  baseline_BI_pct = fraction of annual revenue lost to each hazard historically

EXAMPLE (Hayhurst Solar, Year 2040):
  Revenue = $3.2M/yr
  Baseline heat BI = 1.0% of revenue ($32K/yr — shutdowns, derating)
  HCR_heat(2040) = 0.185
  Additional heat BI = $32K × 0.185 = $5,920/yr

  Baseline flood BI = 0.5% of revenue ($16K/yr)
  HCR_flood(2040) = 0.12
  Additional flood BI = $16K × 0.12 = $1,920/yr

  Total additional BI(2040) = $7,840/yr

PROS:
  + Simple, works with any revenue profile
  + Scales naturally with project size
  + Easy to implement in project_finance

CONS:
  - baseline_BI_pct is the unknown — where does 1.0% come from?
  - Lumps all heat effects (shutdown + derating + O&M) into one number
  - Different assets have very different BI profiles
```

### Approach B — Bottom-Up (Hours × Capacity × Price)

```
METHOD:
  BI_loss_heat(t) = additional_shutdown_hours(t) × capacity_MW × CF × price

  additional_shutdown_hours(t) = baseline_shutdown_hours × HCR_heat(t)

EXAMPLE (Hayhurst Solar, Year 2040):
  Baseline heat shutdown: 120 hours/yr (high-temp inverter curtailment)
  HCR_heat(2040) = 0.185
  Additional hours = 120 × 0.185 = 22.2 hours
  Capacity = 24.8 MW AC
  Capacity factor during heat events = 0.85 (daylight hours, good irradiance)
  Price = $40/MWh (PPA)

  BI_loss_heat(2040) = 22.2 × 24.8 × 0.85 × $40 = $18,710/yr

  Heat derating (separate):
  Baseline derating loss: 2.1% of summer generation
  Additional derating: 2.1% × 0.185 = 0.39% of summer gen
  Summer gen = ~30,000 MWh
  BI_loss_derating(2040) = 30,000 × 0.0039 × $40 = $4,680/yr

  Total heat BI(2040) = $18,710 + $4,680 = $23,390/yr

PROS:
  + Physics-grounded — each component has a clear mechanism
  + Can be validated against O&M records
  + Separates shutdown from derating from O&M cost

CONS:
  - Requires asset-specific data (baseline shutdown hours, derating curves)
  - Data may not be available for a new project (no operating history)
  - More complex to implement
```

### Approach C — Industry Benchmark

```
METHOD:
  Use insurance/industry data for baseline BI rates by hazard type and region

BENCHMARKS (from available sources):
  Solar heat-related BI:     0.5-2.0% of annual revenue (varies by climate zone)
  Solar flood BI:            0.2-1.0% of annual revenue
  Solar hail BI:             0.1-0.5% of annual revenue (highly regional)
  Wind icing BI:             1.0-5.0% of annual revenue (cold climate sites)
  Wind turbine fault BI:     2.0-4.0% of annual revenue (all causes)

EXAMPLE (Hayhurst Solar — arid West Texas):
  Heat BI benchmark: 1.5% (upper range — extreme heat site)
  Flood BI benchmark: 0.3% (low — arid, minimal flood exposure)
  Hail BI benchmark: 0.2% (moderate — Texas hail corridor south of site)

  Revenue = $3.2M/yr
  Total baseline BI = (1.5% + 0.3% + 0.2%) × $3.2M = $64K/yr

  Climate-adjusted BI(2040):
  Heat: $48K × (1 + 0.185) = $56.9K
  Flood: $9.6K × (1 + 0.12) = $10.8K
  Hail: $6.4K × (1 + 0.08) = $6.9K
  Total BI(2040) = $74.6K  (vs $64K baseline → +$10.6K additional)

PROS:
  + Uses real-world data
  + Available for new projects (no operating history needed)
  + Consistent with insurance pricing

CONS:
  - Benchmarks are broad ranges, not precise
  - Regional variation is large
  - Insurance data may not be publicly available
```

### Recommendation: Hybrid (A for Phase 1, B for Phase 2)

```
PHASE 1 (NB04 — get something working):
  Use Approach A (top-down) with conservative baseline_BI_pct estimates
  Sensitivity analysis: run at low/mid/high BI assumptions
  Report: "Heat BI adds $X-$Y to annual costs, depending on baseline assumption"

PHASE 2 (NB05 — connect to project_finance):
  Use Approach B (bottom-up) where asset data exists
  Fall back to Approach C (benchmarks) where it doesn't
  Calibrate against actual O&M data if available from InfraSure
```

---

## 4. How the Integration Actually Works — Concrete Example

Take Hayhurst Solar, Year 10 (2036), SSP5-8.5:

```
PROJECT_FINANCE Gen1 (no climate):
  Revenue(2036)  = $3.2M × (1 - 0.005)^10 = $3.04M    [0.5%/yr std degradation]
  OpEx(2036)     = $550K × (1.025)^10 = $704K           [2.5%/yr escalation]
  CFADS(2036)    = $3.04M - $704K = $2.34M
  DS(2036)       = $1.80M                                [level payment]
  DSCR(2036)     = 2.34 / 1.80 = 1.30x                  [passes 1.25x covenant]


LTRISK PARAMETERS (from NB03/NB04):
  SCVR_tasmax(2036) = 0.074
  HCR_heat(2036)    = 0.074 × 2.5 = 0.185
  EFR_peck(2036)    = 0.07                               [7% additional degradation]
  BI_loss(2036)     = $3.04M × 0.015 × 0.185 = $8,436   [1.5% baseline × HCR]


CLIMATE-ADJUSTED (project_finance × LTRisk):
  Revenue_adj(2036) = $3.04M × (1 - 0.07) = $2.83M      [EFR applied]
  BI_deduction      = $8,436
  CFADS_adj(2036)   = $2.83M - $704K - $8.4K = $2.12M
  DSCR_adj(2036)    = 2.12 / 1.80 = 1.18x               [BREACHES 1.25x covenant]

                     ┌───────────────────────────────────┐
                     │  DSCR dropped from 1.30x to 1.18x │
                     │  EFR is the main driver (-$210K)   │
                     │  BI is small (-$8.4K)              │
                     └───────────────────────────────────┘
```

**Key insight:** BI (Channel 1) is small in dollar terms. EFR/degradation
(Channel 2) is the dominant driver. This matches the NAV impairment breakdown:
Channel 2 = 86% of total, Channel 1 = 20%, Channel 3 = offset.

---

## 5. What This Looks Like on the DSCR Hero Chart

```
THE DSCR HERO CHART — project_finance's primary output

WITHOUT CLIMATE (Gen1):

  DSCR
  2.0x │ ██████████
  1.8x │ ███████████████
  1.6x │ ██████████████████████
  1.4x │ ██████████████████████████████
  1.2x │──────────────────────────────────── covenant (1.25x)
  1.0x │
       └──────────────────────────────────
       Y1    Y5    Y10    Y15    Y18

  P50 DSCR improves steadily as debt amortizes.
  P10 stays above covenant through full tenor.
  Project looks safe.


WITH CLIMATE OVERLAY (Gen1 + LTRisk):

  DSCR
  2.0x │ ██████████
  1.8x │ ██████████████
  1.6x │ ████████████████████
  1.4x │ ██████████████████████████
  1.2x │──────────────────────────────────── covenant (1.25x)
  1.0x │                  ░░░░░░░░░░░░░░░░  ← P10 breaches by Y10
  0.8x │                           ░░░░░░░  ← IUL truncation at Y21
       └──────────────────────────────────
       Y1    Y5    Y10    Y15    Y18

  P50 still passes, but margin thins faster (EFR steepens decline).
  P10 breaches covenant by ~Year 10 under SSP5-8.5.
  Project is riskier than Gen1 suggests.

  THE THREE VISIBLE EFFECTS:
    1. Steeper slope   → EFR accelerates degradation (0.5%/yr → ~0.6%/yr)
    2. Occasional dips → BI events in bad years (not visible at annual level)
    3. Earlier cutoff  → IUL truncation (if loan tenor > IUL, debt goes unpaid)
```

---

## 6. The project_finance Stage 4 — What It Should Actually Be

The `discussion_scaling_1yr_to_multiyear.md` currently describes Stage 4 as:

```
Gen_adjusted(t) = Gen_bootstrap(t) × CMIP_factor(t, scenario)

Example: Years 1-10: CMIP_factor = 0.99 (-1% GHI drift)
         Years 11-20: CMIP_factor = 0.97 (-3% cumulative)
```

This is Channel 3 only (resource change). With LTRisk data, we now know:

```
WHAT STAGE 4 SHOULD ACTUALLY DO:

  For each revenue path (of 1000):
    For each year t:

      1. Apply EFR (Channel 2 — DOMINANT):
         Rev_adj *= (1 - EFR_climate(t))
         This is the Peck's/Coffin-Manson degradation acceleration.
         NOT a resource change — equipment degradation under heat stress.

      2. Apply BI (Channel 1 — secondary):
         Rev_adj -= BI_loss(t)
         Revenue lost to additional hazard shutdowns/derating.
         Small in $ terms but important for tail risk.

      3. Apply resource shift (Channel 3 — negligible):
         Rev_adj *= (1 + resource_delta(t))
         GHI/wind speed drift from CMIP.
         ≈ 0 at Texas sites. Might matter at other locations.

      4. Truncate at IUL if applicable:
         If t > IUL: Rev_adj = 0
         Only relevant if loan tenor > IUL (rare for solar, possible for wind).

    Recompute: CFADS_adj, DSCR_adj for this path

  Recompute percentiles: P10, P25, P50, P75, P90 of DSCR_adj

  The key difference from the original Stage 4 description:
    - CMIP_factor is NOT just GHI drift
    - The dominant channel is EFR (equipment aging), not resource change
    - This comes from LTRisk's SCVR→HCR→EFR pipeline, not from CMIP directly
```

---

## 7. Timeline Alignment

```
                    project_finance              LTRisk
                    ───────────────              ──────
  Time horizon:     Loan tenor (18yr)            Asset life (30yr)
  Start year:       CoD (varies)                 2026
  End year:         CoD + 18                     2055
  Periodicity:      Quarterly/semi-annual        Annual
  Revenue paths:    1000 probabilistic           Deterministic (per scenario)
  Scenarios:        P10/P25/P50/P75/P90          SSP2-4.5, SSP5-8.5

  ALIGNMENT:
    - LTRisk provides SCVR/HCR/EFR for years 2026-2055
    - project_finance needs adjustments for years CoD to CoD+18
    - If CoD = 2026, LTRisk covers the full loan tenor
    - If CoD = 2028, LTRisk years 2028-2046 map to loan years 1-18

  PERIODICITY:
    - LTRisk produces annual parameters (SCVR, HCR, EFR)
    - project_finance tests DSCR quarterly or semi-annually
    - Solution: apply annual LTRisk parameters uniformly within each year
    - BI losses may be seasonal (heat = summer, flood = spring) — future refinement
```

---

## 8. What the User Sees — The Dashboard Integration Vision

```
  ┌────────────────────────────────────────────────────────────────┐
  │  HAYHURST SOLAR — DSCR Dashboard                              │
  │                                                                │
  │  Scenario: [SSP2-4.5 ▼]  [SSP5-8.5]  [No Climate]           │
  │                                                                │
  │  ┌────────────────────────────────────────────────────────┐   │
  │  │                                                        │   │
  │  │   DSCR Hero Chart (18 years × 4 quarters)             │   │
  │  │   Color = DSCR percentile band                         │   │
  │  │                                                        │   │
  │  │   [heatmap changes when scenario toggle is clicked]    │   │
  │  │                                                        │   │
  │  └────────────────────────────────────────────────────────┘   │
  │                                                                │
  │  Summary:                                                      │
  │  ┌─────────────────────────────────────────────────────┐      │
  │  │ No Climate    │ SSP2-4.5     │ SSP5-8.5            │      │
  │  │ Y1 P10: 1.32x │ Y1 P10: 1.28x │ Y1 P10: 1.24x    │      │
  │  │ Y10 P10: 1.45x│ Y10 P10: 1.32x│ Y10 P10: 1.18x   │      │
  │  │ Min: 1.30x     │ Min: 1.22x    │ Min: 1.05x       │      │
  │  │ Breach: Never  │ Breach: Y16   │ Breach: Y10       │      │
  │  └─────────────────────────────────────────────────────┘      │
  │                                                                │
  │  Climate Risk Heatmap:                                         │
  │  ┌────────────────────────────────────────────────────────┐   │
  │  │ tasmax  [░░░░░▒▒▒▒▓▓▓▓▓████████]  SCVR: +4.8% → +11.8│   │
  │  │ tasmin  [░░░░▒▒▒▒▒▓▓▓▓▓▓████████]  SCVR: +9.2% → +18.4│   │
  │  │ pr      [░░░░░░░░░░░░░░░░░░░░░░░]  SCVR: ~0% (noisy)  │   │
  │  │ sfcWind [░░░░░░░░░░░░░░░░░░░░░░░]  SCVR: ~0%          │   │
  │  └────────────────────────────────────────────────────────┘   │
  │                                                                │
  │  Impact Breakdown (SSP5-8.5 vs No Climate):                    │
  │    Channel 2 (Equipment aging):  -$5.1M (86%)                 │
  │    Channel 1 (Hazard BI):        -$1.2M (20%)                 │
  │    Channel 3 (Resource upside):  +$0.4M (-7%)                 │
  │    ──────────────────────────────────────                      │
  │    Total NAV impairment: $5.9M (9.8% of $60M)                │
  │                                                                │
  └────────────────────────────────────────────────────────────────┘
```

---

## 9. Implementation Order

```
STEP 1 — NB04 (LTRisk): Annual HCR + EFR computation
  Depends on: NB03 annual SCVR refactoring (anchor approach)
  Produces: annual HCR(t) and EFR(t) tables in Parquet
  Status: blocked on annual SCVR methodology decision

STEP 2 — Integration bridge: Export LTRisk parameters to project_finance
  Simple: Parquet/JSON file with annual SCVR, HCR, EFR per scenario
  One file per site, consumed by project_finance as a climate overlay

STEP 3 — project_finance Gen2: Apply climate overlay to CFADS
  Modify the revenue extension loop:
    Rev_adj(t, path) = Rev(t, path) × (1 - EFR(t)) - BI_loss(t)
  Recompute DSCR percentiles with climate-adjusted CFADS
  Add scenario toggle to dashboard (No Climate / SSP2-4.5 / SSP5-8.5)

STEP 4 — Validation and sensitivity
  Compare NB04 NAV impairment against project_finance DSCR impact
  Run sensitivity on HCR scaling factors and baseline BI assumptions
  Calibrate against actual asset O&M data if available
```

---

## 10. Open Questions for Team

1. **Baseline BI rates:** What fraction of revenue is currently lost to weather
   events at Hayhurst? At Maverick? Do we have O&M records showing downtime
   hours by cause? This is the critical input for Channel 1 dollar conversion.

2. **Which approach for BI conversion?** Top-down (% of revenue) is easiest
   but least precise. Bottom-up (hours × capacity × price) is more defensible
   but needs data. Industry benchmarks are a middle ground.

3. **Loan tenor vs asset life:** The project_finance model runs 18 years (loan
   tenor). LTRisk runs 30 years (asset life). Should we model the full 30-year
   life for equity perspective, or only the 18-year loan tenor for lender
   perspective? Or both?

4. **Sculpted vs level payment under climate:** With sculpted debt, the DS is
   shaped to maintain target DSCR. If CFADS declines faster under climate
   (EFR), should we re-sculpt the DS to the lower trajectory? Or keep the
   original sculpting and show that climate causes covenant breach?

5. **Probabilistic vs deterministic climate:** project_finance has 1000 revenue
   paths (probabilistic). LTRisk produces deterministic annual parameters per
   scenario. Should climate parameters also be probabilistic (e.g., per-model
   SCVR spread → SCVR confidence interval → probabilistic EFR)?

6. **When does this matter for lenders?** The DSCR impact is most visible at
   P10 in later years. For Hayhurst SSP5-8.5, P10 DSCR breaches ~Year 10.
   Under SSP2-4.5, breach ~Year 16. Under no-climate, never. Is this enough
   of a difference to change debt sizing decisions?

---

## 11. Summary

```
THE INTEGRATION IN ONE DIAGRAM

  LTRisk (NB03+NB04)                  project_finance (Gen2)
  ══════════════════                  ════════════════════════

  CMIP6 daily data                    Revenue (1000 paths)
       │                                    │
       ▼                                    │
  SCVR(t) per variable                      │
       │                                    │
       ▼                                    │
  HCR(t) per hazard ──────────────┐         │
       │                          │         │
       ▼                          │         │
  EFR(t) per mechanism ──────┐    │         │
       │                     │    │         │
       ▼                     │    │         │
  IUL (life shortening) ─┐  │    │         │
                          │  │    │         │
                          ▼  ▼    ▼         ▼
                     ┌──────────────────────────────┐
                     │  CFADS_adj(t) =               │
                     │    Revenue(t)                  │
                     │    × (1 - EFR(t))    ← Ch. 2  │
                     │    - BI_loss(t)      ← Ch. 1  │
                     │    - OpEx(t)                   │
                     │                                │
                     │  Truncate at IUL     ← Ch. 2b │
                     │                                │
                     │  DSCR(t) = CFADS_adj / DS     │
                     └──────────────────────────────┘
                                │
                                ▼
                     DSCR Hero Chart (scenario toggle)
                     NAV impairment ($, %)
                     Channel breakdown
```

**The critical finding:** Channel 2 (EFR/equipment aging) dominates at 86% of
total impairment. The BI conversion question (Channel 1) matters for
completeness but is not the main financial driver. The integration should
**prioritise getting EFR into the CFADS model first**, then layer on BI.

---

*This document should be reviewed alongside:*
- *`discussion_scaling_1yr_to_multiyear.md` (project_finance Stage 4 roadmap)*
- *`../scvr_methodology/annual_scvr_methodology.md` (how annual SCVR values are computed)*
- *`09_nav_impairment_chain.md` (full SCVR→NAV walkthrough)*
