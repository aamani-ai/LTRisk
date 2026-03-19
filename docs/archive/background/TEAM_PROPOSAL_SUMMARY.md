# Team Proposals: Long-Term Risk Evolution Analysis

*Summary of Team's Proposed Approach to Project Lifetime Risk Modeling*

**Document Purpose:** This document synthesizes what the team has proposed across various documents for long-term (15-30 year) project lifetime risk analysis.

**Created:** February 1, 2026  
**Status:** Summary for Review

---

## Table of Contents

1. [Overview: What the Team is Proposing](#overview-what-the-team-is-proposing)
2. [Current Short-Term Approach (1-3 Years)](#current-short-term-approach-1-3-years)
3. [Proposed Long-Term Extensions](#proposed-long-term-extensions)
4. [Use Cases: Where Project Lifetime Analysis is Needed](#use-cases-where-project-lifetime-analysis-is-needed)
5. [Technical Approach Proposed](#technical-approach-proposed)
6. [ASCII Visualizations from Documentation](#ascii-visualizations-from-documentation)
7. [Key Assumptions & Parameters](#key-assumptions--parameters)
8. [What's Missing or Unclear](#whats-missing-or-unclear)

---

## Overview: What the Team is Proposing

The team has documented a **phased approach** to extending InfraSure's risk modeling from short-term (1-3 year) forecasting to **project lifetime (15-30 year)** analysis:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RISK MODELING TIME HORIZON EVOLUTION                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CURRENT (Gen 1-2)          PLANNED (Subsequent)         ASPIRATIONAL       │
│  ══════════════════          ═══════════════════         ═══════════        │
│                                                                              │
│  1-36 month forecasts        15-20 year projections      Full asset life    │
│  ├─ Weather analog           ├─ CMIP climate scenarios  ├─ 25-30 years     │
│  ├─ Historical bootstrap     ├─ Climate-state weighted  ├─ NPV/IRR calcs   │
│  ├─ P50/P90/P99 distrib.     ├─ Trend adjustments       ├─ Degradation     │
│  └─ Validated vs EIA         └─ Scenario-based          └─ Financing models│
│                                                                              │
│  ✅ IN PRODUCTION            📋 ROADMAP                  📋 CONCEPT          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Insight from Team Docs:**
> "If our core 1-3 year forecast is strong and validated, it becomes the foundation for 15-20 year projections — more defensible than pure climatology."

---

## Current Short-Term Approach (1-3 Years)

### What's Working (Gen 1)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   SHORT-TERM FORECASTING (1-36 MONTHS)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INPUT                        PROCESS                      OUTPUT            │
│                                                                              │
│  Historical Weather    ──►    Physics-based         ──►   P50/P90/P99      │
│  (ERA5, 40+ years)            Generation Models            Generation       │
│                               ├─ Solar (pvlib)             (MWh/year)       │
│  Site Registry        ──►     ├─ Wind (PyWake)                              │
│  (EIA, USWTDB)                └─ ML Calibration     ──►   P50/P90/P99      │
│                                                            Revenue           │
│  Price History        ──►    Block Sampling                ($/year)         │
│  (GridStatus, 8+ yrs)         (Gen × Price together)                        │
│                               ├─ Uniform Analog                             │
│                               └─ Weather-Conditioned                        │
│                                                                              │
│  VALIDATION: Backtested against EIA actuals (CRPS, Coverage, Bias)         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Accuracy:**
- Solar Model: 5-15% gap vs EIA actuals (Gen 1) → 5-8% with ML calibration (Gen 2)
- Wind Model: 10-20% gap vs EIA actuals (Gen 1) → 5-10% with ML calibration (Gen 2)

**Forecast Horizon:** 1-36 months (validated, production-ready)

---

## Proposed Long-Term Extensions

### From Documentation: gen1_gen2_subsequent.md

The team proposes extending to **15-20 year horizons** in the "Subsequent" generation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              SUBSEQUENT — Extended Horizons + Climate Integration            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Climate-State Conditioning:                                                │
│    • ENSO phase weighting for 1-3 year forecasts                            │
│    • Learn inter-annual patterns from climate signals                       │
│                                                                              │
│  Long-Term Projections (15-20 years):                                       │
│    • CMIP climate scenarios (RCP/SSP)                                       │
│    • Defensible basis from validated 1-3 year skill                         │
│    • Applications: PPA structuring, project finance, asset valuation        │
│                                                                              │
│  Joint Price Forecasting:                                                   │
│    • Integrated generation-price scenario modeling                          │
│    • Forward revenue projections                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Source:** `local_docs/plans/modeling_taxonomy_and_structure.md`, `docs/layer_2/performance_modeling/gen1_gen2_subsequent.md`

---

## Use Cases: Where Project Lifetime Analysis is Needed

### 1. Investment Screening (Workflow 1)

From `infrasure_user_workflows.md`:

```
SCENARIO: Developer evaluating Site #3 vs Site #1

Site #3 Analysis:
├─ EAL: $10.7M/year
├─ Project Life: 25 years ← PROJECT LIFETIME PARAMETER
├─ Total Expected Losses: $267M (present value over 25 years)
├─ Project NPV without risk: $300M
└─ Risk-Adjusted NPV: $33M (barely viable)

COMPARE TO: Site #1 (Low-risk alternative)
├─ EAL: $500K/year
├─ Total Expected Losses: $12M over 25 years
├─ Project NPV without risk: $280M
└─ Risk-Adjusted NPV: $268M (much better!)

DECISION: ELIMINATE Site #3, PURSUE Site #1

KEY CALCULATION:
  Total Expected Losses = EAL × Project Life (with PV discount)
  $267M = $10.7M/year × 25 years × discount_factor
```

**Implication:** The team is already using **25-year project lifetime** as a parameter in risk-adjusted NPV calculations.

**Question:** How is this $267M calculated? 
- Simple: `$10.7M × 25 = $267.5M` (no discounting)
- PV-adjusted: `NPV($10.7M/year, discount_rate, 25 years)`

---

### 2. Asset Valuation (DCF Models)

From `forecast_simulation_model.md`:

```
Use Cases:

- **Project finance** — Debt sizing over asset lifetime (P90 revenue under 
                         different climate paths)
- **Asset valuation** — DCF models with probabilistic generation scenarios
- **Long-term insurance** — Multi-year parametric products with climate 
                            trend adjustment
```

**Workflow:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DCF VALUATION WITH RISK                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Year 1  │  Year 2  │  Year 3  │  ...  │  Year 20  │  Year 25              │
│  ────────┼──────────┼──────────┼───────┼───────────┼─────────              │
│          │          │          │       │           │                        │
│  Gen P50 │  Gen P50 │  Gen P50 │  ...  │  Gen P50  │  Gen P50              │
│  ×Price  │  ×Price  │  ×Price  │       │  ×Price   │  ×Price               │
│  -OpEx   │  -OpEx   │  -OpEx   │       │  -OpEx    │  -OpEx                │
│  -Insur. │  -Insur. │  -Insur. │       │  -Insur.  │  -Insur.              │
│  -EAL    │  -EAL    │  -EAL    │  ...  │  -EAL     │  -EAL                 │
│  ────────┼──────────┼──────────┼───────┼───────────┼─────────              │
│  = CF₁   │  = CF₂   │  = CF₃   │  ...  │  = CF₂₀   │  = CF₂₅               │
│          │          │          │       │           │                        │
│  ────────────────────────────────────────────────────────────────          │
│                             │                                                │
│                             ▼                                                │
│                   NPV = Σ (CFₜ / (1+r)ᵗ)                                    │
│                                                                              │
│  KEY QUESTION: How do Gen P50, Price, and EAL evolve over 25 years?        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**What the Team Needs:**
1. **Generation trajectory:** How does P50/P90 change over 25 years?
   - Degradation (panels lose 0.5%/year efficiency)
   - Climate trends (temperature rise, wind pattern shifts)

2. **Price trajectory:** How do electricity prices evolve?
   - Renewable penetration impact (merit order effect)
   - Market structure changes

3. **Risk trajectory:** How does EAL change over time?
   - Climate change (increasing hazard frequency/severity?)
   - Asset aging (more vulnerable to damage?)

---

### 3. Insurance Renewal (Workflow 2)

From `infrasure_user_workflows.md`:

```
Context:
  Owner of 2,762 MW renewable energy portfolio (20 assets)
  90 days before insurance renewal
  
Analysis:
  ├─ Total EAL: $286M   ← ANNUAL expected loss
  ├─ Total VaR 95%: $149M
  └─ Top Risk: Coastal Flooding

Premium Calculation (typical):
  Annual Premium = (EAL × Load Factor) + Administrative Costs
  $343M = ($286M × 1.2) + admin

Multi-Year Policy:
  3-year policy: $343M × 3 = $1,029M?
  
KEY QUESTION: Does EAL stay constant over 3 years, or evolve?
```

**Current Approach (from docs):** EAL is calculated for a single year, then extrapolated.

**Proposed Enhancement:** Model how EAL changes year-over-year due to:
- Climate trends (CMIP scenarios)
- Asset degradation
- Market changes

---

## Technical Approach Proposed

### 1. Climate Scenario Integration (CMIP)

From `gen1_gen2_subsequent.md`:

```
Long-Term Projections (15-20 years):
  • CMIP climate scenarios (RCP/SSP)
  • Defensible basis from validated 1-3 year skill
  • Applications: PPA structuring, project finance, asset valuation
```

**CMIP (Coupled Model Intercomparison Project):**
- Provides climate model projections for 21st century
- Scenarios: RCP 2.6, 4.5, 6.0, 8.5 (Representative Concentration Pathways)
- Or: SSP1-2.6, SSP2-4.5, SSP5-8.5 (Shared Socioeconomic Pathways)

**Proposed Approach:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                CLIMATE SCENARIO-BASED LONG-TERM MODELING                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STEP 1: Select Climate Scenario                                            │
│  ────────────────────────────────                                            │
│  • RCP 2.6 (aggressive mitigation)                                          │
│  • RCP 4.5 (moderate mitigation) ← Likely baseline                          │
│  • RCP 8.5 (business as usual)                                              │
│                                                                              │
│  STEP 2: Adjust Historical Weather Data                                     │
│  ────────────────────────────────────────                                    │
│  For each year t in [2026, 2027, ..., 2050]:                               │
│    • Apply CMIP temperature delta: T(t) = T_historical + ΔT(t)             │
│    • Apply CMIP precipitation delta: P(t) = P_historical × (1 + ΔP(t))     │
│    • Apply CMIP wind speed delta (if available)                             │
│                                                                              │
│  STEP 3: Run Physics Models with Adjusted Weather                           │
│  ─────────────────────────────────────────────────                          │
│  • Solar model: Adjusted GHI/DNI/DHI → Generation                           │
│  • Wind model: Adjusted wind speeds → Generation                            │
│  • Include degradation: Gen(t) = Gen_base × (1 - 0.005)^t                  │
│                                                                              │
│  STEP 4: Generate Probabilistic Scenarios                                   │
│  ──────────────────────────────────────────                                 │
│  • Block sampling from climate-adjusted historical years                    │
│  • P50/P90/P99 for each future year                                         │
│                                                                              │
│  OUTPUT: Year-by-year generation distributions (2026-2050)                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Visual Concept:**

```
Generation (MWh/year)
      │
200K  │  ●●●●●●●●●●●●●●●●●●●●●●●●●● P50 (RCP 4.5)
      │  ░░░░░░░░░░░░░░░░░░░░░░░░░░
      │  ░░░░░░░░░░░░░░░░░░░░░░░░░░ P10-P90 band
      │  ░░░░░░░░░░░░░░░░░░░░░░░░░░
150K  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░
      │  
      │  Degradation: -0.5%/year
      │  Climate trend: +1.5°C by 2050 (reduces solar CF slightly)
      │  
      └────────────────────────────────────────────────► Year
         2026  2030  2035  2040  2045  2050
```

---

### 2. Degradation Modeling

From `layer_2_research_references.csv`:

```
Reference: Jordan & Kurtz (2013) - Photovoltaic Degradation Rates
  Analysis of 2000+ degradation studies (median 0.5%/yr)
  Basis for three-phase degradation model parameters
```

**Current Implementation (Gen 1):**

```python
# From solar_deterministic_performance_model.md
# Three-phase degradation model:

Year 1:       -2.5%  (initial stabilization)
Years 2-25:   -0.5%/year (linear degradation)
After Year 25: -1.0%/year (accelerated aging)

Generation(t) = Generation_base × Degradation_Factor(t)

Example:
  Year 1:  200,000 MWh × 0.975 = 195,000 MWh
  Year 10: 200,000 MWh × 0.975 × 0.995^9 = 186,500 MWh
  Year 25: 200,000 MWh × 0.975 × 0.995^24 = 172,000 MWh
```

**Visualization:**

```
Generation (% of nameplate)
      │
100%  │  ●
      │   ╲____
 97.5%│        ●────●────●────●────●────●────●────●─── Years 2-25 
      │                                           ╲    (-0.5%/yr)
      │                                            ╲
      │                                             ●─── Year 26+
      │                                                  (-1.0%/yr)
      │
      └────────────────────────────────────────────────────────────► Year
         1    5    10   15   20   25   30
```

---

### 3. Risk Evolution Over Time

**Proposed Approach (Not Explicitly in Docs, but Implied):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RISK EVOLUTION: EAL OVER PROJECT LIFE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FACTORS AFFECTING EAL OVER TIME:                                           │
│                                                                              │
│  1. GENERATION DECLINE (Degradation)                                        │
│     ├─ Lower generation → Lower absolute shortfall (MWh)                    │
│     └─ But: Threshold also based on lower generation                        │
│     └─ Net effect: Unclear without calculation                              │
│                                                                              │
│  2. CLIMATE CHANGE (Hazard Frequency/Severity)                              │
│     ├─ Hail: Increasing frequency? (climate research unclear)               │
│     ├─ Flooding: Increasing (AR6 high confidence)                           │
│     ├─ Wind: Regional variations                                            │
│     └─ Wildfire: Increasing in arid regions                                 │
│                                                                              │
│  3. ASSET AGING (Physical Vulnerability)                                    │
│     ├─ Older panels more fragile to hail                                    │
│     ├─ Mounting systems degrade (wind vulnerability)                        │
│     └─ Drainage systems clog (flood vulnerability)                          │
│                                                                              │
│  4. MARKET EVOLUTION (Price Dynamics)                                       │
│     ├─ Renewable penetration → Merit order effect                           │
│     ├─ Price volatility may increase                                        │
│     └─ Revenue risk changes even if generation stable                       │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  EAL TRAJECTORY SCENARIOS:                                                  │
│                                                                              │
│  EAL ($/year)                                                               │
│      │                                                                       │
│  12M │                        ╱●●●●  Scenario C: Increasing risk            │
│      │                    ╱●●●      (climate change + aging)                │
│  10M │              ●●●●●●                                                   │
│      │         ●●●●●          Scenario B: Stable risk                       │
│   8M │    ●●●●●               (climate offsets degradation)                 │
│      │  ●●                                                                   │
│   6M │●●                      Scenario A: Decreasing risk                   │
│      │  ●●●●●●●●●●●●          (degradation dominant)                        │
│   4M │                                                                       │
│      │                                                                       │
│      └────────────────────────────────────────────────────────────────────► │
│        2026  2030  2035  2040  2045  2050                                   │
│                                                                              │
│  CURRENT ASSUMPTION (Implicit): EAL is constant                             │
│  PROPOSED: Model EAL(t) as function of time                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ASCII Visualizations from Documentation

### 1. Evolution Roadmap (from gen1_gen2_subsequent.md)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EVOLUTION ROADMAP                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GEN 1 (CURRENT)              GEN 2 (NEXT)            SUBSEQUENT           │
│  ───────────────              ────────────            ──────────           │
│                                                                             │
│  ✅ Foundation                🎯 Calibration          📋 Scale + Extend    │
│                                                                             │
│  • Physics-based solar/       • ML calibration        • SCADA integration  │
│    wind generation models       (close the 5-20% gap)  • 15-20yr projections│
│  • Uniform + Weather-Cond.    • Rigorous validation   • All US markets     │
│    forecast simulation          vs EIA actuals        • Climate scenarios  │
│  • Block sampling (preserves  • Climate-state tiered    (CMIP)             │
│    gen-price correlation)       forecasting (ENSO)                         │
│  • 40+ years weather,                                                      │
│    8+ years price data                                                     │
│                                                                             │
│  STATUS: Production           STATUS: In Progress     STATUS: Planned      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Performance Modeling Pipeline (from infrasure_performance_modeling.md)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              PERFORMANCE MODELING PIPELINE                                       │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│                                    DATA SOURCES                                                  │
│                                                                                                  │
│    ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐                      │
│    │  WEATHER DATA   │       │  SITE REGISTRY  │       │   PRICE DATA    │                      │
│    │                 │       │                 │       │                 │                      │
│    │  • ERA5         │       │  • EIA (plant)  │       │  • GridStatus   │                      │
│    │  • Hydronos API │       │  • USPVDB/USWTDB│       │  • 5 major ISOs │                      │
│    │                 │       │  • CEC database │       │  • DA + RT mkts │                      │
│    │  40+ yrs hourly │       │    (equipment)  │       │  8+ yrs hourly  │                      │
│    └────────┬────────┘       └────────┬────────┘       └────────┬────────┘                      │
│             │                         │                         │                               │
│             │         ┌───────────────┴───────────────┐         │                               │
│             │         ▼                               ▼         │                               │
│             │   ┌───────────────┐             ┌───────────────┐ │                               │
│             └──▶│  SOLAR MODEL  │             │  WIND MODEL   │◀┘                               │
│                 │  (pvlib)      │             │  (PyWake)     │                                 │
│                 └───────┬───────┘             └───────┬───────┘                                 │
│                         │                             │                                         │
│                         └──────────────┬──────────────┘                                         │
│                                        ▼                                                        │
│                          ┌─────────────────────────────┐                                        │
│                          │    GENERATION HISTORY       │                                        │
│                          │    (Hourly MW, 40+ yrs)     │                                        │
│                          └──────────────┬──────────────┘                                        │
│                                         │                                                       │
│                                         ▼                                                       │
│                    ┌─────────────────────────────────────────────┐                             │
│                    │       FORECAST SIMULATION ENGINE            │                             │
│                    │                                             │                             │
│                    │  Block sampling: Gen × Price TOGETHER       │                             │
│                    │  → 1,000+ scenario paths                    │                             │
│                    │  → P50/P90/P99 distributions                │                             │
│                    └──────────────────┬──────────────────────────┘                             │
│                                       │                                                        │
│                                       ▼                                                        │
│                    ┌─────────────────────────────────────────────┐                             │
│                    │  P50/P90/P99 GENERATION & REVENUE           │                             │
│                    └─────────────────────────────────────────────┘                             │
│                                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Workflow Example (from infrasure_user_workflows.md)

```
DECISION LOGIC:

Site #3 Analysis:
├─ EAL: $10.7M/year
├─ Project Life: 25 years
├─ Total Expected Losses: $267M (present value)
├─ Project NPV without risk: $300M
└─ Risk-Adjusted NPV: $33M (barely viable)

COMPARE TO: Site #1 (Low-risk alternative)
├─ EAL: $500K/year
├─ Total Expected Losses: $12M
├─ Project NPV without risk: $280M
└─ Risk-Adjusted NPV: $268M (much better!)

DECISION: ELIMINATE Site #3, PURSUE Site #1
```

---

### 4. Risk Exposure Calculation (from RISK_EXPOSURE_DETAILED.md)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FREQUENCY-SEVERITY RISK MODEL                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FREQUENCY: 5% of scenarios have shortfall                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐│
│  │  5% ███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 95% ││
│  └────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  SEVERITY: Distribution when loss occurs (excluding zeros)                  │
│  ┌────────────────────────────────────────────────────────────────────────┐│
│  │                    P5        P50       Mean              P95           ││
│  │                     │         │          │                │            ││
│  │              ╱╲     │         │          │                │            ││
│  │             ╱  ╲    │         │          │                │            ││
│  │            ╱    ╲   │         │          │                │            ││
│  │           ╱      ╲  │         │          │                │            ││
│  │  ────────╱────────╲─┴─────────┴──────────┴────────────────┴────────── ││
│  │        0                                                       $400K   ││
│  └────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  EAL = Frequency × Severity                                                 │
│  $8.2K/year = 5% × $164K                                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Assumptions & Parameters

### 1. Project Lifetime Parameters (from various docs)

| Parameter | Value | Source |
|-----------|-------|--------|
| **Solar Asset Lifetime** | 25-30 years | Industry standard |
| **Wind Asset Lifetime** | 20-25 years | Industry standard |
| **Degradation Rate (Solar)** | 0.5%/year (median) | Jordan & Kurtz 2013 |
| **Degradation Rate (Wind)** | Not specified | To be determined |
| **Discount Rate** | Not specified | User input (typical: 6-10%) |
| **Climate Scenario** | RCP 4.5 (assumed) | To be determined |

### 2. Risk Parameters (from RISK_EXPOSURE_DETAILED.md)

| Parameter | Typical Value | Notes |
|-----------|---------------|-------|
| **VaR Percentile** | P5, P10, P20, P30 | P5 = 95% confidence |
| **Analysis Frequency** | Annual, Quarterly, Monthly | Higher granularity = higher EAL |
| **Settlement Price** | $50/MWh (default) | User configurable |
| **Policy Tenor** | 1-3 years | Multi-year extension proposed |

---

## What's Missing or Unclear

### 1. NPV Calculation Details

**Current State:**
- Docs show: "Total Expected Losses: $267M (present value)"
- Formula not explicitly stated

**Questions:**
```
Is it:
  A) Simple multiplication?
     $267M = $10.7M/year × 25 years (no discounting)
     
  B) Present Value?
     PV = Σ(EAL_t / (1+r)^t) for t=1 to 25
     
  C) Risk-adjusted with climate scenarios?
     PV = Σ(EAL_t(scenario) / (1+r)^t) 
     where EAL_t changes over time
```

**Recommendation Needed:**
- Should EAL be constant or time-varying?
- What discount rate to use?
- How to handle climate scenario uncertainty?

---

### 2. Climate Scenario Selection

**Current State:**
- Docs mention "CMIP climate scenarios (RCP/SSP)"
- No guidance on which scenario to use as baseline

**Questions:**
```
Which scenario for baseline analysis?
  • RCP 2.6: Optimistic (2°C warming by 2100)
  • RCP 4.5: Moderate (3°C warming) ← Most likely?
  • RCP 8.5: Pessimistic (4°C warming)

Should we:
  A) Use single scenario (e.g., RCP 4.5)?
  B) Show range across scenarios?
  C) Allow user to select?
```

**Implications:**
- RCP 2.6 vs RCP 8.5 could show 20-30% difference in long-term risk
- Need guidance for investor reports ("What scenario did you assume?")

---

### 3. Hazard Evolution Over Time

**Current State:**
- Hazard models (hail, flood, wind, wildfire) calculate EAL for current climate
- No explicit modeling of how hazard frequency/severity changes over 25 years

**Questions:**
```
How do hazards evolve under climate change?

Hail:
  • Research inconclusive (some studies show increase, others flat)
  • Assumption: Constant frequency? Conservative +10%/decade?

Flooding:
  • AR6 projects increased precipitation extremes
  • Assumption: +5-10% frequency per degree warming?

Wind:
  • Regional variations (some areas more, some less)
  • Assumption: Constant? Regional adjustments?

Wildfire:
  • Clear increasing trend in western US
  • Assumption: Exponential growth? Linear?
```

**Current Approach (Implicit):**
- Hazard EAL is calculated for a single year
- Assumed constant over project life (?)

**Proposed Enhancement:**
- EAL_hazard(t) = EAL_base × Climate_Adjustment_Factor(t)
- Needs research to define adjustment factors

---

### 4. Price Forecasting Over 25 Years

**Current State:**
- Price model uses historical data (8+ years GridStatus)
- Block sampling preserves historical gen-price correlation
- No long-term price forecasting

**Questions:**
```
How do electricity prices evolve over 25 years?

Merit Order Effect:
  • As renewable penetration increases, daytime prices fall
  • Could see 20-30% price decline in high-solar regions by 2040
  • How to model this?

Battery Storage:
  • Grid-scale storage flattens price curves
  • Reduces peak/off-peak spread
  • Impact on revenue?

Market Structure:
  • Some ISOs may shift to capacity markets
  • Nodal vs zonal pricing changes
  • Regulatory changes?
```

**Current Approach (Implicit):**
- Use historical price distribution, assume stationary
- Block sampling from past 8 years

**Proposed Enhancement:**
- Price scenarios (low/med/high penetration)
- Trend adjustments based on renewable build-out forecasts
- Separate price model for long-term projections

---

### 5. Correlation Structure Over Time

**Current State:**
- Gen-price correlation preserved via block sampling (brilliant!)
- Works for 1-3 year forecasts using historical blocks

**Questions:**
```
How does gen-price correlation change over 25 years?

Current Approach:
  • Sample historical blocks where gen & price co-occurred
  • Preserves correlation structure from past

Future Reality:
  • Gen-price correlation may weaken (more solar → lower peak prices)
  • Storage decouples generation from price
  • Need forward-looking correlation model?

Example:
  Historical (2020): High solar gen → High prices (still ramping up)
  Future (2045): High solar gen → Low prices (oversupply)
```

**Proposed Enhancement:**
- Correlation adjustment factor based on renewable penetration forecasts
- Scenario-based correlation (optimistic/pessimistic storage adoption)

---

### 6. Validation for Long-Term Projections

**Current State:**
- Gen 1 validated against EIA actuals (1-3 year hindcasts)
- CRPS, Coverage, Bias metrics

**Questions:**
```
How do we validate 25-year projections?

Challenge:
  • Can't backtest 25 years (only 8 years EIA data available)
  • Climate change means historical distributions may not hold
  • No ground truth for 2050

Options:
  A) Trust short-term validation + climate science
  B) Validate components separately:
     - Degradation: Compare predicted vs actual aging
     - Climate trends: Compare CMIP vs observations
  C) Scenario analysis: Show range of outcomes
  D) Regular recalibration: Update projections every 2-3 years
```

**Recommendation Needed:**
- Accept that long-term projections are inherently uncertain
- Focus on **relative comparisons** (Site A vs Site B) rather than absolute accuracy
- Transparent uncertainty bands (P10-P90 widening over time)

---

## Summary: What the Team Has Proposed

### ✅ Clear Proposals

1. **15-20 year projection horizon** for project finance and asset valuation
2. **CMIP climate scenarios** (RCP/SSP) for weather trend adjustments
3. **Three-phase degradation model** for solar (validated research basis)
4. **Block sampling** extended to climate-adjusted historical years
5. **Use case integration**: NPV calculations with 25-year project life

### ⚠️ Needs Clarification

1. **NPV calculation formula**: How to compute "Total Expected Losses over 25 years"?
2. **Climate scenario selection**: Which RCP/SSP as baseline? Range or single?
3. **Hazard evolution**: How do hail/flood/wind/wildfire change under climate change?
4. **Price trajectory**: How to forecast electricity prices 25 years out?
5. **Correlation evolution**: How does gen-price correlation change with storage/renewable penetration?
6. **Validation approach**: How to validate 25-year projections without 25 years of data?
7. **EAL time-series**: Is EAL constant or does it evolve (EAL_t)?
8. **Discount rate**: What rate to use for PV calculations? User input or standard?

---

## Next Steps for Review

### Phase 1: Technical Clarifications

1. **Define NPV calculation method**
   - Document formula with worked example
   - Specify discount rate assumptions
   - Show EAL constant vs time-varying scenarios

2. **Select baseline climate scenario**
   - Research team recommendation: RCP 4.5?
   - Define when to show scenario range (uncertainty quantification)

3. **Model EAL evolution**
   - Research hazard trends under climate change
   - Define adjustment factors (e.g., flood +5% per °C)
   - Implement EAL_t = EAL_base × f(climate, aging, degradation)

### Phase 2: Implementation Planning

4. **Climate data integration**
   - Access CMIP6 data for project regions
   - Define downscaling method (spatial resolution)
   - Validate against observed trends (1980-2020)

5. **Long-term price model**
   - Research renewable penetration forecasts (EIA AEO)
   - Define merit order effect adjustments
   - Scenario analysis (low/med/high storage adoption)

6. **Validation framework**
   - Component-level validation (degradation, climate trends)
   - Scenario-based uncertainty quantification
   - Regular recalibration schedule (every 2-3 years)

---

*End of Summary*

**Next Action:** Review this summary, then provide feedback on:
1. What's correct in the team's proposals?
2. What needs to be changed or clarified?
3. Which of the "unclear" items are highest priority to resolve?

