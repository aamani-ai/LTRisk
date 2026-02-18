# Long-Term Climate Risk Framework for Infrastructure Assets

*A Comprehensive Guide to Assessing NAV Impairment Under Climate Change Scenarios*

**Version:** 1.1  
**Created:** February 1, 2026  
**Last Updated:** February 1, 2026  
**Status:** Pilot Framework (2-week implementation)

> ⚠️ **NOTE:** This document contains several TODO sections marking gaps that need to be resolved during the pilot. See Appendix D for a consolidated list.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Master Framework](#2-the-master-framework)
3. [Pathway A: Hazards → Business Interruption](#3-pathway-a-hazards--business-interruption)
4. [Pathway B: Climate → Generation Performance](#4-pathway-b-climate--generation-performance)
5. [Pathway C: Climate Stress → Equipment Life](#5-pathway-c-climate-stress--equipment-life)
6. [Bringing It Together: NAV Impairment](#6-bringing-it-together-nav-impairment)
7. [Implementation](#7-implementation)
8. [Assessment](#8-assessment)
9. [Appendices](#9-appendices)

---

# 1. Executive Summary

## 1.1 The Problem We're Solving

Infrastructure investors and lenders face a critical question:

> **"How will climate change affect the value of my renewable energy assets over their 25-35 year lifetime?"**

This is not a hypothetical concern. Climate change is already:
- Increasing extreme heat events (affecting solar efficiency and equipment life)
- Changing precipitation patterns (affecting flood and hail risk)
- Altering wind patterns (affecting generation and structural fatigue)

**Without quantification, investors cannot:**
- Price climate risk into acquisition decisions
- Assess whether loan collateral will retain value
- Compare assets in different climate zones
- Meet emerging climate disclosure requirements

## 1.2 What This Framework Delivers

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         THE DELIVERABLE                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   INPUT:  A renewable energy asset (solar farm or wind farm)                    │
│           + Climate scenario (e.g., RCP 4.5 / SSP2-4.5)                         │
│                                                                                  │
│   OUTPUT: NAV Impairment %                                                      │
│           "Climate change reduces this asset's value by X%"                     │
│                                                                                  │
│   USE CASES:                                                                    │
│   ┌─────────────────────────────┐  ┌─────────────────────────────┐             │
│   │     EQUITY INVESTORS        │  │         LENDERS             │             │
│   ├─────────────────────────────┤  ├─────────────────────────────┤             │
│   │ "My IRR drops from 12% to   │  │ "My LTV goes from 70% to    │             │
│   │  9% under climate stress.   │  │  85% under climate stress.  │             │
│   │  Is this still attractive?" │  │  Is my loan still secured?" │             │
│   └─────────────────────────────┘  └─────────────────────────────┘             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 1.3 The Conceptual Foundation: Baseline vs. Climate Scenario

### What is a "Baseline"?

The baseline represents **what we expect under historical climate conditions** - essentially, "business as usual" if climate didn't change.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         BASELINE SCENARIO                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ASSUMPTION: Climate stays like the historical period (1980-2010)              │
│                                                                                  │
│   For a 25 MW solar farm in Texas:                                              │
│                                                                                  │
│   • Expected Useful Life (EUL): 25 years                                        │
│   • Annual Generation: Based on historical weather patterns                     │
│   • Business Interruption: Based on current hazard frequencies                  │
│   • Degradation: Standard 0.5%/year                                             │
│                                                                                  │
│   NPV_base = Σ [Revenue(t) / (1+WACC)^t]  for t = 1 to 25                      │
│            = $22.8M (example)                                                   │
│                                                                                  │
│   This is what investors currently model. It's the "expected" value.           │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### What is a "Climate Scenario"?

A climate scenario represents **what happens under a specific pathway of future emissions** - how the world might change if we follow a particular trajectory.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         CLIMATE SCENARIO                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   SCENARIO: RCP 4.5 / SSP2-4.5 ("Middle of the Road")                          │
│   - Global warming of ~2.4°C by 2100                                            │
│   - Emissions peak around 2040, then decline                                    │
│   - Represents "moderate mitigation" pathway                                    │
│                                                                                  │
│   For the same 25 MW solar farm in Texas:                                       │
│                                                                                  │
│   CHANNEL 1: Lower Generation                                                   │
│   • Higher temperatures → Panels run hotter → Efficiency drops                 │
│   • Changed irradiance patterns → Slightly different solar resource            │
│   • Annual revenue: -3% compared to baseline                                    │
│                                                                                  │
│   CHANNEL 2: More Hazard Losses                                                 │
│   • More extreme precipitation → More flood events → More downtime             │
│   • More hail events → More panel damage                                        │
│   • Annual BI losses: +21% compared to baseline                                 │
│                                                                                  │
│   CHANNEL 3: Shorter Life                                                       │
│   • Heat + humidity accelerates panel degradation (Peck's Model)               │
│   • Asset reaches end-of-life in 22 years, not 25                              │
│   • Impaired Useful Life (IUL): 22 years                                        │
│                                                                                  │
│   NPV_climate = Σ [Revenue_net(t) / (1+WACC)^t]  for t = 1 to 22              │
│               = $16.5M (example)                                                │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### The Comparison: NAV Impairment

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         NAV IMPAIRMENT CALCULATION                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                    NPV_base         NPV_climate                                 │
│                    ─────────        ────────────                                │
│                      $22.8M           $16.5M                                    │
│                                                                                  │
│   NAV_Impairment = (1 - NPV_climate / NPV_base) × 100%                         │
│                  = (1 - 16.5 / 22.8) × 100%                                    │
│                  = 27.6%                                                        │
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                         │  │
│   │   "Under RCP 4.5 climate scenario, this asset's value is impaired     │  │
│   │    by approximately 28% compared to baseline expectations."            │  │
│   │                                                                         │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│   WHERE DOES THE 28% COME FROM?                                                 │
│   ────────────────────────────────                                              │
│   • Lower generation:      ~8% of total impairment                             │
│   • Higher BI losses:      ~5% of total impairment                             │
│   • Shorter life:         ~15% of total impairment ← BIGGEST DRIVER            │
│                                                                                  │
│   The 3-year life reduction (25→22) is the single largest impact because      │
│   you lose 3 full years of revenue at end of life.                             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 1.4 Why This Framework? The Three-Pathway Approach

Climate change affects infrastructure assets through **three distinct channels**. Modeling them separately and then combining them provides:

1. **Scientific rigor** - Each channel uses appropriate physics/engineering models
2. **Transparency** - Stakeholders can see which effects dominate
3. **Flexibility** - Can update one channel without rebuilding everything
4. **Defensibility** - Each component is backed by peer-reviewed science

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    THE THREE PATHWAYS (PREVIEW)                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   PATHWAY A: HAZARDS → BUSINESS INTERRUPTION                                    │
│   ──────────────────────────────────────────                                    │
│   "Climate change increases extreme events → More downtime → Lost revenue"     │
│                                                                                  │
│   Climate Variables → SCVR (area under exceedance) → HCR → BI                  │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   PATHWAY B: CLIMATE → GENERATION PERFORMANCE                                   │
│   ─────────────────────────────────────────────                                  │
│   "Changed weather → Different generation patterns → Different revenue"        │
│                                                                                  │
│   Climate Variables → Physics Models (pvlib/PyWake) → MWh → Revenue            │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   PATHWAY C: CLIMATE STRESS → EQUIPMENT LIFE                                    │
│   ───────────────────────────────────────────                                    │
│   "Climate stress accelerates degradation → Shorter useful life"               │
│                                                                                  │
│   Climate Variables → SCVR (area under exceedance) → EFR → IUL                 │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 1.5 What Data Makes This Possible?

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DATA FOUNDATION                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   CLIMATE PROJECTIONS: CMIP6 / NEX-GDDP-CMIP6                                   │
│   ──────────────────────────────────────────────                                 │
│   • 35+ climate models providing multiple future scenarios                      │
│   • Variables: Temperature, Precipitation, Wind, Humidity, Solar (rsds)        │
│   • Temporal: Daily data from 2015-2100                                        │
│   • Spatial: 0.25° resolution (~25km)                                          │
│   • Scenarios: SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5                          │
│                                                                                  │
│   WHY NEX-GDDP-CMIP6 (NASA's Downscaled Product)?                               │
│   • Bias-corrected against historical observations                              │
│   • Downscaled to usable resolution                                             │
│   • Includes rsds (solar irradiance) - critical for solar modeling             │
│   • Free, publicly available                                                    │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   HISTORICAL BASELINE: ERA5                                                     │
│   ──────────────────────────                                                     │
│   • ECMWF's reanalysis product (1940-present)                                  │
│   • Provides the "baseline" climate statistics                                  │
│   • Used to calibrate what "normal" looks like                                  │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   INFRASURE EXISTING DATA:                                                      │
│   ─────────────────────────                                                      │
│   • Asset-specific performance models (validated solar/wind)                   │
│   • Baseline BI estimates per asset                                             │
│   • S2S forecasts for years 1-3 (seamless transition)                          │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 1.6 Critical Concept: SCVR (Severe Climate Variability Rating)

SCVR is the **central metric** in this framework. Everything flows from SCVR.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    SCVR: THE CORE METRIC                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   DEFINITION (from team):                                                       │
│   "Increase in the AREA UNDER THE EXCEEDANCE CURVE"                            │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   WHAT IS AN EXCEEDANCE CURVE?                                                  │
│                                                                                  │
│   Probability                                                                   │
│   of Exceeding                                                                  │
│       │                                                                         │
│   1.0 │▓▓▓▓                                                                    │
│       │▓▓▓▓▓▓▓                                                                 │
│   0.5 │▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                                          │
│       │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ ← Future (shifted right)                  │
│   0.1 │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░                                    │
│   0.0 └────────────────────────────────────→                                    │
│         30°C   35°C   40°C   45°C   50°C                                       │
│                                                                                  │
│   ▓▓▓ = Baseline     ░░░ = Additional area under future curve                  │
│                                                                                  │
│   SCVR = (Area_future - Area_baseline) / Area_baseline                         │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   WHY AREA (not just count)?                                                    │
│                                                                                  │
│   Area captures BOTH:                                                           │
│   • FREQUENCY: How often you exceed the threshold                              │
│   • SEVERITY: By how much you exceed it                                        │
│                                                                                  │
│   Example:                                                                      │
│   • Baseline: 10 days > 35°C, average temp = 37°C → Area ≈ 20 degree-days     │
│   • Future: 10 days > 35°C, average temp = 42°C → Area ≈ 70 degree-days       │
│   • Count-based: 0% change (WRONG - misses severity!)                          │
│   • Area-based: +250% change (CORRECT - captures severity!)                    │
│                                                                                  │
│   For equipment damage, SEVERITY matters. A 45°C day is much worse than 36°C. │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   SCVR IS COMPUTED FOR EACH VARIABLE/INDEX:                                    │
│                                                                                  │
│   • SCVR_temp: Temperature exceedance                                          │
│   • SCVR_wind: Wind speed exceedance                                           │
│   • SCVR_precip: Precipitation exceedance (Rx5day)                            │
│   • SCVR_heatwave: Heat wave metric exceedance                                 │
│   • SCVR_humidity: Humidity exceedance                                         │
│   • etc.                                                                        │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   HOW SCVR FLOWS TO DOWNSTREAM CALCULATIONS:                                   │
│                                                                                  │
│   SCVR ──────→ HCR (Hazard Change Ratio) ──────→ BI                           │
│          │                                                                      │
│          └───→ EFR (Equipment Failure Ratio) ──→ IUL                          │
│                                                                                  │
│   Both HCR and EFR are derived FROM SCVR using literature-based relationships. │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Summary: The Complete Flow (Team's Document, Simplified)

From the team's pilot work plan, the flow is clean and direct:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    THE TEAM'S FRAMEWORK (SIMPLIFIED)                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   STEP 1: COMPUTE SCVR FOR EACH VARIABLE/INDEX                                  │
│   ═══════════════════════════════════════════════                                │
│                                                                                  │
│   From team: "Compute increased SCVR (defined as the increase in the area      │
│   under the exceedance curves) in temperature, winds, heat wave, precipitation, │
│   severe winds."                                                                 │
│                                                                                  │
│   • SCVR_temp                                                                   │
│   • SCVR_wind                                                                   │
│   • SCVR_heatwave      ← "Heat wave" is just another index to compute SCVR for │
│   • SCVR_precip                                                                 │
│   • SCVR_severe_wind                                                            │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 2: PERFORMANCE (Pathway B - no SCVR needed)                             │
│   ═════════════════════════════════════════════════                              │
│                                                                                  │
│   From team: "Use InfraSure Climate Simulation engine to generate missing      │
│   climate variables... call InfraSure asset performance model"                  │
│                                                                                  │
│   Variables → pvlib/PyWake → MWh → Revenue                                     │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 3: HCR → BI (Pathway A)                                                 │
│   ═════════════════════════════                                                  │
│                                                                                  │
│   From team: "For a given hazard, HCR is the percentage increase in hazard     │
│   risk derived as a function of relevant SCVRs."                               │
│                                                                                  │
│   SCVR_precip  ──┐                                                              │
│   SCVR_heatwave ─┼──→ HCR (literature) ──→ BI_climate                          │
│   SCVR_wind ─────┘                                                              │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 4: EFR → IUL (Pathway C)                                                │
│   ══════════════════════════════                                                 │
│                                                                                  │
│   From team: "For a given Climate Variable, EFR is the percentage decrease     │
│   for a given Asset Type in Asset Life for a percentage increase in SCVR"      │
│                                                                                  │
│   SCVR_temp ─────┐                                                              │
│   SCVR_humidity ─┼──→ EFR (scientific models) ──→ IUL                          │
│   SCVR_wind ─────┘                                                              │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   KEY INSIGHT: SCVR is the CENTRAL metric.                                     │
│   There is NO separate "conditions" layer - SCVR is computed directly          │
│   for variables/indices, then fed into HCR and EFR calculations.               │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### TODO: SCVR Computation Methodology

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TODO: CLARIFY SCVR COMPUTATION                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   TEAM DEFINITION: "Increase in the area under the exceedance curve"           │
│                                                                                  │
│   QUESTIONS TO RESOLVE:                                                         │
│                                                                                  │
│   1. AREA-BASED vs COUNT-BASED:                                                │
│      ─────────────────────────────                                              │
│      For raw variables (temperature): Area-based is clearly intended           │
│      For count indices (heat wave days): Is it area-based on the count         │
│        distribution, or just (mean_future - mean_baseline) / mean_baseline?    │
│                                                                                  │
│      □ Clarify with team which approach to use                                 │
│      □ Document rationale for pilot                                            │
│                                                                                  │
│   2. THRESHOLD FOR EXCEEDANCE:                                                 │
│      ─────────────────────────────                                              │
│      "Area under exceedance curve" requires a threshold.                       │
│      • For temperature: Exceedance above what? P90? 35°C? Asset-specific?     │
│      • For wind: Exceedance above what? P90? Cut-in speed? 15 m/s?            │
│                                                                                  │
│      □ Define thresholds for each variable                                     │
│      □ Align with equipment specs where relevant (tolerance ranges)            │
│                                                                                  │
│   3. PERIOD DEFINITION:                                                        │
│      ─────────────────────────────                                              │
│      • Baseline period: 1980-2010 or 1985-2014?                               │
│      • Future period: 2030-2050 or centered 20-year windows?                  │
│      • How to handle transition years (e.g., 2020-2030)?                      │
│                                                                                  │
│      □ Align with CMIP/NEX-GDDP conventions                                   │
│                                                                                  │
│   4. ENSEMBLE HANDLING:                                                        │
│      ─────────────────────────────                                              │
│      • Multiple GCMs produce different futures                                 │
│      • Team says "average of ensembles" for revenue                           │
│      • But what about SCVR? Mean of SCVRs? SCVR of ensemble mean?             │
│                                                                                  │
│      □ Define ensemble aggregation method                                      │
│      □ Consider reporting ensemble spread (uncertainty)                        │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   SUGGESTED PILOT APPROACH:                                                    │
│                                                                                  │
│   • For continuous variables (temp, wind, precip):                             │
│     Use AREA-BASED with P90 threshold from baseline                           │
│                                                                                  │
│   • For count indices (heat wave days, frost days):                            │
│     Use COUNT-BASED (simpler) = (mean_future - mean_base) / mean_base         │
│     Note: For pilot, this is acceptable; Phase 1 can refine                   │
│                                                                                  │
│   • Period: 1985-2014 baseline, 2030-2050 future (align with NEX-GDDP)        │
│                                                                                  │
│   • Ensemble: Compute SCVR for each GCM, report mean and range                │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 1.7 Critical Concept: Period Averaging (Not Single Years)

A fundamental principle throughout this framework:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    PERIOD AVERAGING                                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ⚠️ "2030" does NOT mean the single year 2030!                                │
│                                                                                  │
│   Climate projections are noisy on single-year timescales (El Niño, etc.)      │
│   To extract the SIGNAL (climate trend) from the NOISE (weather variability),  │
│   we use PERIOD AVERAGES:                                                       │
│                                                                                  │
│   ┌─────────────┬──────────────────────────┬─────────────────────────────────┐  │
│   │  Label      │  Actual Period           │  Duration                       │  │
│   ├─────────────┼──────────────────────────┼─────────────────────────────────┤  │
│   │  "Baseline" │  1980-2010               │  30 years (historical)          │  │
│   │  "2030"     │  2020-2040               │  20 years (centered on 2030)    │  │
│   │  "2040"     │  2030-2050               │  20 years (centered on 2040)    │  │
│   │  "2050"     │  2040-2060               │  20 years (centered on 2050)    │  │
│   └─────────────┴──────────────────────────┴─────────────────────────────────┘  │
│                                                                                  │
│   TIMELINE VISUALIZATION:                                                       │
│                                                                                  │
│   ─────┬──────────────────┬──────┬──────────────────┬──────────────────────     │
│      1980              2010    2020              2040                2060       │
│        │                 │       │        │        │        │         │         │
│        └─────────────────┘       └────────┴────────┘        │         │         │
│              BASELINE                 "2030"                │         │         │
│             (30 years)              (20 years)              │         │         │
│                                                      └──────┴─────────┘         │
│                                                           "2050"                │
│                                                         (20 years)              │
│                                                                                  │
│   This is STANDARD PRACTICE in climate impact assessments (IPCC, etc.)         │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 1.7 Pilot Scope

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         PILOT PARAMETERS                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   TIMELINE: 2 weeks                                                             │
│                                                                                  │
│   SAMPLE ASSETS:                                                                │
│   ┌────────────────────┬────────────────────────────────────────────────────┐  │
│   │ Asset              │ Details                                            │  │
│   ├────────────────────┼────────────────────────────────────────────────────┤  │
│   │ Hayhurst Solar     │ Culberson, TX | 24.8 MW | 31.82°N, -104.09°W     │  │
│   │ Maverick Creek Wind│ Concho, TX | 491.6 MW | 31.26°N, -99.84°W        │  │
│   └────────────────────┴────────────────────────────────────────────────────┘  │
│                                                                                  │
│   KEY ASSUMPTIONS:                                                              │
│   ┌────────────────────┬────────────────────────────────────────────────────┐  │
│   │ Parameter          │ Value                                              │  │
│   ├────────────────────┼────────────────────────────────────────────────────┤  │
│   │ Discount Rate      │ 10% (WACC)                                        │  │
│   │ Solar EUL          │ 25 years                                          │  │
│   │ Wind EUL           │ 35 years                                          │  │
│   │ Climate Scenario   │ RCP 4.5 / SSP2-4.5                                │  │
│   │ Climate Data       │ NEX-GDDP-CMIP6 (recommended)                      │  │
│   └────────────────────┴────────────────────────────────────────────────────┘  │
│                                                                                  │
│   WHAT'S INCLUDED:                                                              │
│   ✅ Revenue degradation from changed climate                                   │
│   ✅ Business interruption from increased hazards (non-Cat)                    │
│   ✅ Equipment life reduction from climate stress                              │
│                                                                                  │
│   WHAT'S EXCLUDED (for pilot):                                                  │
│   ❌ Physical damage costs (only BI modeled)                                   │
│   ❌ Catastrophic events (hurricane, major wildfire)                           │
│   ❌ Price evolution from climate (stationary prices assumed)                  │
│   ❌ O&M cost changes                                                           │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 2. The Master Framework

## 2.1 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE NAV IMPAIRMENT FRAMEWORK                              │
│                                                                                          │
│                    "How Climate Change Reduces Asset Value"                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│                              ┌─────────────────────┐                                     │
│                              │   CMIP Climate Data │                                     │
│                              │  (NEX-GDDP-CMIP6)   │                                     │
│                              └──────────┬──────────┘                                     │
│                                         │                                                │
│                    Temperature, Precipitation, Wind, Humidity, rsds                      │
│                                         │                                                │
│              ┌──────────────────────────┼──────────────────────────┐                    │
│              │                          │                          │                    │
│              ▼                          ▼                          ▼                    │
│   ╔═══════════════════════╗  ╔═══════════════════════╗  ╔═══════════════════════╗      │
│   ║     PATHWAY A         ║  ║     PATHWAY B         ║  ║     PATHWAY C         ║      │
│   ║   HAZARDS → BI        ║  ║  CLIMATE → REVENUE    ║  ║  STRESS → LIFE        ║      │
│   ╠═══════════════════════╣  ╠═══════════════════════╣  ╠═══════════════════════╣      │
│   ║                       ║  ║                       ║  ║                       ║      │
│   ║  Variables            ║  ║  Variables            ║  ║  Variables            ║      │
│   ║      ↓                ║  ║      ↓                ║  ║      ↓                ║      │
│   ║  SCVR                 ║  ║  pvlib / PyWake       ║  ║  SCVR                 ║      │
│   ║  (area under curve)   ║  ║  (Physics-based)      ║  ║  (area under curve)   ║      │
│   ║      ↓                ║  ║      ↓                ║  ║      ↓                ║      │
│   ║  HCR                  ║  ║  MWh Generation       ║  ║  EFR                  ║      │
│   ║  (from literature)    ║  ║      ↓                ║  ║  (from literature)    ║      │
│   ║      ↓                ║  ║  × Price              ║  ║      ↓                ║      │
│   ║  BI_climate           ║  ║      ↓                ║  ║  IUL                  ║      │
│   ║                       ║  ║  Revenue_climate      ║  ║                       ║      │
│   ╚═══════════╤═══════════╝  ╚═══════════╤═══════════╝  ╚═══════════╤═══════════╝      │
│               │                          │                          │                   │
│               │                          │                          │                   │
│               └──────────────────────────┼──────────────────────────┘                   │
│                                          │                                              │
│                                          ▼                                              │
│                    ┌────────────────────────────────────────┐                           │
│                    │          Revenue_net (year t)          │                           │
│                    │                                        │                           │
│                    │  = Revenue_climate - BI_climate        │                           │
│                    │                                        │                           │
│                    │  (summed over IUL years, not EUL)      │                           │
│                    └────────────────────┬───────────────────┘                           │
│                                         │                                               │
│                                         ▼                                               │
│                    ┌────────────────────────────────────────┐                           │
│                    │           NPV_climate                  │                           │
│                    │                                        │                           │
│                    │  = Σ [Revenue_net(t) / (1+WACC)^t]    │                           │
│                    │    for t = 1 to IUL                    │                           │
│                    └────────────────────┬───────────────────┘                           │
│                                         │                                               │
│                                         ▼                                               │
│          ┌──────────────────────────────────────────────────────────┐                   │
│          │                                                          │                   │
│          │      NAV_Impairment_% = (1 - NPV_climate/NPV_base) × 100%│                   │
│          │                                                          │                   │
│          │      "Climate change reduces this asset's value by X%"   │                   │
│          │                                                          │                   │
│          └──────────────────────────────────────────────────────────┘                   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## 2.2 How the Three Pathways Combine

Each pathway quantifies a different mechanism by which climate change reduces asset value:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         THREE PATHWAYS - DETAILED                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   PATHWAY A: HAZARDS → BUSINESS INTERRUPTION                                            │
│   ═══════════════════════════════════════════                                            │
│   Question: "How much MORE revenue do we lose to hazards under climate change?"         │
│                                                                                          │
│   Logic:                                                                                │
│   • Climate change increases frequency/intensity of extreme events                      │
│   • More extreme precip → More floods → More downtime                                   │
│   • More heat waves → More inverter shutdowns                                           │
│   • Each hazard causes lost revenue (Business Interruption)                             │
│                                                                                          │
│   Formula:                                                                              │
│   BI_climate = Σ [BI_base_hazard × (1 + HCR_hazard)]                                   │
│                                                                                          │
│   Impact on NAV: Reduces Revenue_net each year                                          │
│                                                                                          │
│   ─────────────────────────────────────────────────────────────────────────────────────│
│                                                                                          │
│   PATHWAY B: CLIMATE → GENERATION PERFORMANCE                                           │
│   ═════════════════════════════════════════════                                          │
│   Question: "How does changed weather affect how much MWh we generate?"                 │
│                                                                                          │
│   Logic:                                                                                │
│   • Climate change alters temperature, irradiance, wind patterns                        │
│   • Higher temps → Solar panels less efficient (Temperature Coefficient)                │
│   • Changed winds → Different capacity factor                                           │
│   • Physics-based models (pvlib, PyWake) quantify this directly                        │
│                                                                                          │
│   Formula:                                                                              │
│   Revenue_climate = MWh_climate × Price                                                 │
│   (where MWh_climate comes from performance model with climate inputs)                  │
│                                                                                          │
│   Impact on NAV: Changes Revenue_gross each year                                        │
│                                                                                          │
│   ─────────────────────────────────────────────────────────────────────────────────────│
│                                                                                          │
│   PATHWAY C: CLIMATE STRESS → EQUIPMENT LIFE                                            │
│   ═══════════════════════════════════════════                                            │
│   Question: "Does climate stress cause the asset to fail earlier?"                      │
│                                                                                          │
│   Logic:                                                                                │
│   • Heat + humidity accelerates chemical degradation (Peck's Model)                    │
│   • Thermal cycling causes mechanical fatigue (Coffin-Manson)                          │
│   • Wind variability causes structural fatigue (Palmgren-Miner)                        │
│   • Asset reaches end-of-life sooner than expected                                     │
│                                                                                          │
│   Formula:                                                                              │
│   IUL = EUL × [1 - Σ(EFR_i × SCVR_i)]                                                  │
│                                                                                          │
│   Impact on NAV: Fewer years of revenue (NPV sum stops at year IUL, not EUL)           │
│                  This is often the LARGEST impact because you lose entire years.       │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## 2.3 Key Metrics Reference

| Metric | Full Name | What It Measures | Units |
|--------|-----------|------------------|-------|
| **SCVR** | Severe Climate Variability Rating | % increase in **area under exceedance curve** for a climate variable/index | % |
| **HCR** | Hazard Change Ratio | % increase in hazard risk, derived from SCVR via literature | % |
| **EFR** | Equipment Failure Ratio | % life reduction per % SCVR, derived from scientific models | % per % SCVR |
| **EUL** | Expected Useful Life | Baseline asset lifespan | Years |
| **IUL** | Impaired Useful Life | Climate-adjusted lifespan | Years |
| **BI** | Business Interruption | Revenue lost to hazards | $/year |
| **WACC** | Weighted Average Cost of Capital | Discount rate for NPV | % |
| **NAV** | Net Asset Value | Present value of asset | $ |

## 2.4 Complete Worked Example: Hayhurst Solar

Let's trace through the entire framework for Hayhurst Solar (24.8 MW, Culberson, TX):

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE EXAMPLE: HAYHURST SOLAR (24.8 MW)                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   BASELINE SCENARIO (No Climate Change)                                                 │
│   ══════════════════════════════════════                                                 │
│                                                                                          │
│   Parameters:                                                                           │
│   • EUL: 25 years                                                                       │
│   • Capacity: 24.8 MW DC                                                                │
│   • Capacity Factor: 22% (historical average)                                           │
│   • Annual Generation: 24.8 × 8760 × 0.22 = 47,800 MWh                                │
│   • PPA Price: $52/MWh (illustrative)                                                   │
│   • Year 1 Revenue: 47,800 × $52 = $2.49M                                              │
│   • Degradation: 0.5%/year                                                              │
│   • Annual BI (baseline): $95K                                                          │
│                                                                                          │
│   Year-by-Year (simplified):                                                            │
│   ┌───────┬────────────┬──────────┬─────────────┬────────────────┐                     │
│   │ Year  │ Generation │ Revenue  │ BI          │ Net Revenue    │                     │
│   ├───────┼────────────┼──────────┼─────────────┼────────────────┤                     │
│   │ 1     │ 47,800     │ $2.49M   │ $95K        │ $2.39M         │                     │
│   │ 2     │ 47,561     │ $2.47M   │ $95K        │ $2.38M         │                     │
│   │ ...   │ ...        │ ...      │ ...         │ ...            │                     │
│   │ 25    │ 42,587     │ $2.21M   │ $95K        │ $2.12M         │                     │
│   └───────┴────────────┴──────────┴─────────────┴────────────────┘                     │
│                                                                                          │
│   NPV_base (10% WACC): $22.8M                                                           │
│                                                                                          │
│   ─────────────────────────────────────────────────────────────────────────────────────│
│                                                                                          │
│   CLIMATE SCENARIO (RCP 4.5, "2040" = 2030-2050 period)                                │
│   ═══════════════════════════════════════════════════════                               │
│                                                                                          │
│   PATHWAY A: HAZARDS → BI                                                               │
│   ───────────────────────                                                               │
│   SCVR_heatwave = +66%, SCVR_precip = +24%                                             │
│                                                                                          │
│   HCR calculations:                                                                     │
│   • HCR_flood = 1.5 × 24% = +36%                                                       │
│   • HCR_hail = 0.5 × 66% + 0.3 × 10% = +36%                                            │
│   • HCR_heat_shutdown = 1.0 × 66% = +66%                                               │
│                                                                                          │
│   Baseline BI breakdown:                                                                │
│   • Flood: $30K → $30K × 1.36 = $41K                                                   │
│   • Hail: $45K → $45K × 1.36 = $61K                                                    │
│   • Heat: $20K → $20K × 1.66 = $33K                                                    │
│   • Total BI_climate: $135K/year (vs $95K baseline, +42%)                              │
│                                                                                          │
│   ───────────────────────────────────────────────────────────────────────────────────  │
│                                                                                          │
│   PATHWAY B: CLIMATE → GENERATION                                                       │
│   ──────────────────────────────────                                                    │
│   Temperature increase (2030-2050 avg): +2.1°C                                          │
│                                                                                          │
│   Temperature Coefficient effect:                                                       │
│   • Additional cell temp increase: +2.1°C ambient → +2.6°C cell                        │
│   • Efficiency loss: 2.6°C × 0.4%/°C = -1.0%                                           │
│                                                                                          │
│   Irradiance change: Slight increase (+0.5%) - partially offsets                       │
│                                                                                          │
│   Net generation impact: -0.5% annual generation                                        │
│   Revenue_climate: $2.49M × 0.995 = $2.48M (Year 1)                                    │
│                                                                                          │
│   (Note: Small effect because Texas is already hot - panels designed for it)           │
│                                                                                          │
│   ───────────────────────────────────────────────────────────────────────────────────  │
│                                                                                          │
│   PATHWAY C: CLIMATE STRESS → LIFE                                                      │
│   ────────────────────────────────────                                                  │
│   Climate stress metrics (2030-2050 period avg):                                        │
│   • SCVR_heat+humidity = +78% (Tropical Nights increase)                               │
│   • SCVR_freeze = -29% (fewer freeze cycles - BENEFIT)                                 │
│                                                                                          │
│   EFR calculations (from Peck's Model):                                                 │
│   • Heat+humidity: EFR = 0.22% per % SCVR                                              │
│     Life reduction = 78% × 0.22% = 17.2%                                               │
│   • Freeze (benefit): EFR = 0.15% per % SCVR                                           │
│     Life increase = 29% × 0.15% = 4.4%                                                 │
│                                                                                          │
│   Net life reduction = 17.2% - 4.4% = 12.8%                                            │
│                                                                                          │
│   IUL = 25 × (1 - 0.128) = 25 × 0.872 = 21.8 years ≈ 22 years                         │
│                                                                                          │
│   ─────────────────────────────────────────────────────────────────────────────────────│
│                                                                                          │
│   COMBINING THE PATHWAYS                                                                │
│   ══════════════════════                                                                 │
│                                                                                          │
│   Year-by-Year (climate scenario):                                                      │
│   ┌───────┬────────────┬──────────┬─────────────┬────────────────┐                     │
│   │ Year  │ Generation │ Revenue  │ BI_climate  │ Net Revenue    │                     │
│   ├───────┼────────────┼──────────┼─────────────┼────────────────┤                     │
│   │ 1     │ 47,561     │ $2.47M   │ $135K       │ $2.34M         │ (vs $2.39M base)   │
│   │ 2     │ 47,324     │ $2.46M   │ $135K       │ $2.32M         │                     │
│   │ ...   │ ...        │ ...      │ ...         │ ...            │                     │
│   │ 22    │ 42,800     │ $2.23M   │ $135K       │ $2.09M         │ ← LAST YEAR        │
│   │ 23-25 │ N/A        │ N/A      │ N/A         │ $0             │ ← ASSET FAILED     │
│   └───────┴────────────┴──────────┴─────────────┴────────────────┘                     │
│                                                                                          │
│   NPV_climate (10% WACC, 22 years): $16.5M                                             │
│                                                                                          │
│   ─────────────────────────────────────────────────────────────────────────────────────│
│                                                                                          │
│   FINAL RESULT                                                                          │
│   ════════════                                                                          │
│                                                                                          │
│   NAV_Impairment = (1 - NPV_climate / NPV_base) × 100%                                 │
│                  = (1 - $16.5M / $22.8M) × 100%                                        │
│                  = 27.6%                                                                │
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │   RESULT: "Under RCP 4.5, Hayhurst Solar's NAV is impaired by ~28%"           │  │
│   │                                                                                 │  │
│   │   BREAKDOWN:                                                                    │  │
│   │   • Lower generation (Pathway B): -0.5%/yr × 22 yrs =  ~5% of impairment      │  │
│   │   • Higher BI (Pathway A): +$40K/yr × 22 yrs NPV'd =  ~7% of impairment       │  │
│   │   • Shorter life (Pathway C): 3 lost years =         ~16% of impairment       │  │
│   │                                                       ─────────────────        │  │
│   │                                                       ~28% total               │  │
│   │                                                                                 │  │
│   │   KEY INSIGHT: Life reduction is the biggest driver!                           │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# 3. Pathway A: Hazards → Business Interruption

## 3.1 Overview

This pathway quantifies how climate change increases revenue losses from hazards.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    PATHWAY A: THE LOGIC FLOW                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   STEP 1: COMPUTE SCVR FOR EACH VARIABLE/INDEX                                  │
│   ═════════════════════════════════════════════                                  │
│                                                                                  │
│   CMIP Variables: tasmax, tasmin, pr, sfcWind, hurs                             │
│                                                                                  │
│   SCVR is computed for:                                                         │
│   • Temperature extremes  → SCVR_temp                                          │
│   • Precipitation (Rx5day)→ SCVR_precip                                        │
│   • Heat wave days        → SCVR_heatwave                                      │
│   • Wind speed            → SCVR_wind                                          │
│   • Severe wind           → SCVR_severe_wind                                   │
│                                                                                  │
│   NOTE: "Heat wave" is just another VARIABLE/INDEX for which we compute SCVR.  │
│         It's defined as "3+ consecutive days where T_max & T_min > P90",       │
│         but conceptually it's treated the same as temperature or precipitation.│
│                                                                                  │
│   SCVR = (Area_under_exceedance_curve_future - Area_baseline) / Area_baseline  │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 2: CONVERT SCVR → HCR (HAZARD CHANGE RATIO)                             │
│   ═════════════════════════════════════════════════                              │
│                                                                                  │
│   For each hazard, HCR is derived from relevant SCVRs using literature:        │
│                                                                                  │
│   HCR_flood = f(SCVR_precip)       "More extreme precip → more flooding"       │
│   HCR_hail = f(SCVR_precip, SCVR_temp)                                         │
│   HCR_heat = f(SCVR_heatwave)      "More heat waves → more heat shutdowns"    │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 3: COMPUTE BI_climate                                                    │
│   ══════════════════════════                                                     │
│                                                                                  │
│   BI_climate = Σ [BI_base_hazard × (1 + HCR_hazard)]                           │
│                                                                                  │
│   Example:                                                                      │
│   BI_base_flood = $30K    HCR_flood = +36%  →  BI_climate_flood = $41K        │
│   BI_base_hail = $45K     HCR_hail = +36%   →  BI_climate_hail = $61K         │
│   BI_base_heat = $20K     HCR_heat = +66%   →  BI_climate_heat = $33K         │
│   ────────────────────────────────────────────────────────────────             │
│   Total: $95K baseline → $135K climate (+42%)                                  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 3.2 Variables and Indices for SCVR Computation

This section defines the variables and derived indices for which we compute SCVR.

**IMPORTANT:** These are simply the metrics for which we calculate the "area under the exceedance curve." They are NOT a separate processing layer - SCVR is computed directly for each of these.

### 3.2.1 Heat Wave Index

**Definition:** Annual count of "3+ consecutive days where BOTH T_max AND T_min exceed the 90th percentile of the historical baseline (1980-2010)."

**Source:** Copernicus Global Drought Observatory

**Why This Index?** Heat waves cause inverter thermal shutdowns (solar) and grid stress. The 3-day threshold captures sustained heat events that overwhelm cooling systems.

**How to Compute:**
```python
def count_heat_wave_days(tasmax, tasmin, baseline_period='1980-2010'):
    """
    Count annual heat wave days.
    
    Steps:
    1. Calculate P90 thresholds for each calendar day (smoothed)
    2. Identify days exceeding BOTH thresholds
    3. Find consecutive runs of 3+ days
    4. Sum total days in heat wave events
    """
    # Calculate P90 from baseline
    p90_max = tasmax.sel(time=baseline_period).groupby('time.dayofyear').quantile(0.90)
    p90_min = tasmin.sel(time=baseline_period).groupby('time.dayofyear').quantile(0.90)
    
    # Identify exceedance days
    exceeds = (tasmax > p90_max) & (tasmin > p90_min)
    
    # Find runs of 3+ consecutive days (use scipy.ndimage.label)
    # Sum days in qualifying runs
    return heat_wave_days_per_year
```

**SCVR Calculation (Area Under Exceedance Curve):**

For heat wave index, we build an exceedance curve of annual heat wave days:

```
Probability of exceeding X heat wave days
        │
    1.0 │████                          
        │████████                       ← Baseline
    0.5 │████████████████████          
        │████████████████████████░░░░░░ ← Future (shifted right)  
    0.1 │████████████████████████████████░░░░░░░░
    0.0 └──────────────────────────────────────→
        0   5   10   15   20   25   30  Heat Wave Days

SCVR_heatwave = (Area_future - Area_baseline) / Area_baseline
```

**Worked Example (Culberson, TX):**
- Baseline (1980-2010): Area under curve ≈ 5.1 day-probability units
- Future (2030-2050): Area under curve ≈ 8.5 day-probability units
- SCVR = (8.5 - 5.1) / 5.1 = **+66%**

**Hazards Affected (used in HCR calculation):**
- Inverter/transformer overheating → BI (downtime)
- Panel efficiency loss → Performance (Pathway B)
- Accelerated degradation → Life (Pathway C)

---

### 3.2.2 Cold Wave

**Definition:** 3+ consecutive days where BOTH T_max AND T_min fall below the 10th percentile.

**Climate Change Direction:** DECREASING (warming reduces cold waves)

**Example:**
- Baseline: 8 cold wave days/year
- Future (2040): 4 cold wave days/year  
- SCVR = (4 - 8) / 8 = **-50%**

**Hazards Affected:**
- Wind turbine icing → BI + Performance
- Freeze damage → Life (though fewer events = potential benefit)

---

### 3.2.3 Freeze/Frost Days

**Definition:**
- Frost Day: T_min < 0°C (overnight frost)
- Icing Day: T_max < 0°C (entire day below freezing)
- Thermal Cycle: Day where T_min < 0°C AND T_max > 0°C (freeze-thaw)

**For Equipment Life:** Thermal cycles matter most (cause expansion/contraction stress)

**Example (Culberson, TX):**
- Baseline: 45 frost days/year, 30 thermal cycles
- Future (2040): 32 frost days (-29%), 22 thermal cycles (-27%)
- SCVR_freeze = **-29%** (a benefit for Texas sites)

---

### 3.2.4 Extreme Precipitation (Rx5day)

**Definition:** Maximum consecutive 5-day precipitation total per year.

**Why Rx5day:** Captures flood-generating rainfall events better than annual total.

**SCVR Calculation:**
```
SCVR_precip = [Rx5day(future) - Rx5day(baseline)] / Rx5day(baseline)
```

**Example:**
- Baseline: 85mm max 5-day precip
- Future (2040): 105mm max 5-day precip
- SCVR = (105 - 85) / 85 = **+24%**

**Climate Science Note:** Extreme precipitation increases ~7% per 1°C warming (Clausius-Clapeyron relationship). This is one of the more confident projections.

**Hazards Affected:**
- Pluvial flooding → BI (site access, equipment damage)
- Erosion → Infrastructure damage

---

### 3.2.5 Extreme Wind (Proxy)

**Challenge:** CMIP provides daily MEAN wind, not gusts. Daily mean ≠ maximum.

**Best Available Proxy:**
```
Extreme_Wind_Days = count(sfcWind_daily_mean > 15 m/s at 10m)
```

**Correction for Hub Height:**
```
v_hub = v_10m × ln(z_hub / z_0) / ln(10 / z_0)
```
For 80m hub, z_0 = 0.03m: v_hub ≈ v_10m × 1.36

**Uncertainty:** This SCVR is less reliable than temperature/precipitation. Recommend using wide range in sensitivity analysis.

---

### 3.2.6 Wildfire (FWI Proxy)

**Definition:** Fire Weather Index computed from T_max, RH, Wind, Precipitation

**Status:** Proxy only - indicates fire WEATHER risk, not actual fire occurrence (missing fuel load, ignition sources, suppression capability)

**Pilot Scope:** Excluded from pilot (catastrophic hazard)

---

## 3.3 From SCVR to HCR

The Hazard Change Ratio translates climate variability into hazard risk:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    SCVR → HCR LINKAGE TABLE                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   │ Hazard          │ Relevant SCVR(s)      │ HCR Formula            │ Source  │
│   ├─────────────────┼───────────────────────┼────────────────────────┼─────────┤
│   │ Pluvial Flood   │ SCVR_precip           │ HCR = ?? × SCVR_p     │ TBD     │
│   │ Hail            │ SCVR_temp, SCVR_wind  │ HCR = ??×T + ??×W     │ TBD     │
│   │ Extreme Wind    │ SCVR_wind             │ HCR = ?? × SCVR_w     │ TBD     │
│   │ Heat Shutdown   │ SCVR_heatwave         │ HCR = ?? × SCVR_hw    │ TBD     │
│   │ Icing           │ SCVR_freeze           │ HCR = ?? × SCVR_f     │ TBD     │
│   │ Wildfire        │ SCVR_fwi              │ EXCLUDED (pilot)      │ N/A     │
│                                                                                  │
│   ⚠️  ALL COEFFICIENTS ARE TBD - This is a key pilot deliverable               │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.3.1 ⚠️ CRITICAL GAP: SCVR → HCR Conversion Not Defined

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    GAP ANALYSIS: SCVR → HCR                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   WHAT THE TEAM'S DOCUMENT SAYS:                                                │
│   ───────────────────────────────                                                │
│   "Develop the HCR Table based on review of published research and internal    │
│    discussions. For a given hazard, HCR is the percentage increase in hazard   │
│    risk derived as a function of relevant SCVRs."                              │
│                                                                                  │
│   WHAT THIS MEANS:                                                              │
│   • The conversion formula is NOT yet defined                                   │
│   • The coefficients are NOT yet determined                                     │
│   • This is a KEY DELIVERABLE of the pilot (Step 3 of Work Plan)              │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   WHAT NEEDS TO BE RESEARCHED:                                                  │
│                                                                                  │
│   1. FUNCTION FORM: Is HCR a linear function of SCVR?                          │
│      • Option A: HCR = k × SCVR              (linear)                          │
│      • Option B: HCR = k × SCVR^n            (power law)                       │
│      • Option C: HCR = step function         (threshold-based)                 │
│                                                                                  │
│   2. COEFFICIENTS: What is k (and n if power law)?                             │
│      • For flood: Is k = 1.0? 1.5? 2.0?                                        │
│      • This determines if BI doubles when SCVR doubles, or more/less          │
│                                                                                  │
│   3. MULTI-VARIABLE HAZARDS: How to combine SCVRs?                             │
│      • Hail depends on temp AND wind AND precip                                │
│      • HCR_hail = a×SCVR_t + b×SCVR_w + c×SCVR_p?                            │
│      • Or multiplicative: HCR = f(T) × g(W) × h(P)?                           │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   COMPARE TO EFR (Pathway C):                                                   │
│                                                                                  │
│   EFR has SCIENTIFIC MODELS with formulas:                                     │
│   • Peck's Model provides η = exp(γ0 + γ1×ln(hr) + γ2/T)                      │
│   • Coffin-Manson provides N_f = C × (Δε)^(-k)                                 │
│   • These are physics-based, peer-reviewed                                     │
│                                                                                  │
│   HCR has NO such foundation in the team's document.                           │
│   This is probably the BIGGEST research gap.                                   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.3.2 TODO: Literature Review for HCR Coefficients

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TODO: DERIVE HCR COEFFICIENTS                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   TASK: For each hazard, find literature that links climate change to hazard   │
│         frequency/intensity, and extract or derive coefficients.               │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   FLOOD (Pluvial):                                                              │
│   □ Search: IPCC AR6 Chapter on precipitation extremes                         │
│   □ Search: "climate change flood frequency [region]" papers                   │
│   □ Key question: Does 10% increase in Rx5day → 10% more floods? Or 15%?      │
│   □ Possible sources:                                                          │
│     - IPCC AR6 WG1 Chapter 11 (Weather and Climate Extreme Events)            │
│     - Hirabayashi et al. (2013) - global flood projections                    │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   HAIL:                                                                         │
│   □ Search: "climate change hail frequency solar" papers                       │
│   □ Search: "convective storm climate change" papers                           │
│   □ Note: Hail is HARD - depends on complex convective dynamics               │
│   □ Possible sources:                                                          │
│     - Allen et al. (2020) - hail in a warming climate                         │
│     - Tippett et al. (2015) - severe thunderstorm environments               │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   EXTREME WIND:                                                                 │
│   □ Search: "climate change wind speed distribution" papers                    │
│   □ Key question: Does mean wind change, or just variability?                  │
│   □ Note: Regional variation is significant                                    │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   HEAT SHUTDOWN:                                                                │
│   □ May be simplest: 1:1 mapping from SCVR_heatwave is plausible              │
│   □ Verify: Does every heat wave day = a shutdown day?                        │
│   □ Or is there a temperature threshold?                                       │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   ICING (Wind):                                                                 │
│   □ Beneficial under climate change (fewer freeze days)                        │
│   □ Search: "climate change wind turbine icing" papers                        │
│   □ HCR will be NEGATIVE (hazard decreases)                                   │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   PILOT APPROACH IF LITERATURE IS SPARSE:                                      │
│                                                                                  │
│   Option 1: Assume linear 1:1 (HCR = SCVR) as baseline                        │
│             → Transparent, simple, easy to explain                             │
│             → May underestimate for convex hazards (flood)                     │
│                                                                                  │
│   Option 2: Consult InfraSure's hazard team for internal estimates            │
│             → Leverage existing expertise                                      │
│             → Document assumptions for future refinement                       │
│                                                                                  │
│   Option 3: Run sensitivity analysis with k = [0.5, 1.0, 1.5, 2.0]            │
│             → Shows range of outcomes                                          │
│             → Identifies which hazards drive uncertainty                       │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.3.3 TODO: Baseline BI Estimates

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TODO: OBTAIN BASELINE BI ESTIMATES                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   The HCR calculation requires BI_base for each hazard.                        │
│                                                                                  │
│   From team's document:                                                         │
│   "Using the InfraSure BI estimates and the HCR values..."                     │
│                                                                                  │
│   QUESTION: Where do baseline BI estimates come from?                          │
│                                                                                  │
│   □ Does InfraSure already have BI estimates for the pilot assets?             │
│     - Hayhurst Solar: BI by hazard = ?                                         │
│     - Maverick Creek Wind: BI by hazard = ?                                    │
│                                                                                  │
│   □ If not, how to estimate?                                                   │
│     - Insurance loss history?                                                  │
│     - Industry benchmarks ($/MW/year by hazard)?                              │
│     - Monte Carlo from hazard models?                                          │
│                                                                                  │
│   □ What hazard categories to include?                                         │
│     - Flood, Hail, Wind, Heat, Icing - anything else?                         │
│     - How granular? (e.g., "flood" or "pluvial flood" vs "fluvial flood")     │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   EXAMPLE FORMAT NEEDED:                                                        │
│                                                                                  │
│   Hayhurst Solar (24.8 MW):                                                    │
│   ┌──────────────┬────────────────┬──────────────────────────────────────────┐ │
│   │ Hazard       │ BI_base ($/yr) │ Data Source                              │ │
│   ├──────────────┼────────────────┼──────────────────────────────────────────┤ │
│   │ Flood        │ $?             │ InfraSure hazard model / Insurance data  │ │
│   │ Hail         │ $?             │ InfraSure hazard model / Insurance data  │ │
│   │ Heat         │ $?             │ InfraSure hazard model / O&M records     │ │
│   │ ...          │ ...            │ ...                                      │ │
│   └──────────────┴────────────────┴──────────────────────────────────────────┘ │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Example HCR Calculation (2040 period):**

| Hazard | SCVR Input | HCR Formula | HCR Value |
|--------|------------|-------------|-----------|
| Flood | +24% (precip) | 1.5 × 24% | +36% |
| Hail | +66% (temp), +10% (wind) | 0.5×66% + 0.3×10% | +36% |
| Heat Shutdown | +66% (heatwave) | 1.0 × 66% | +66% |
| Icing | -50% (coldwave) | 1.0 × (-50%) | -50% |

## 3.4 From HCR to BI

**Formula:**
```
BI_climate_hazard = BI_base_hazard × (1 + HCR_hazard)
Total_BI_climate = Σ BI_climate_hazard
```

**⚠️ Key Assumption: Linear Scaling**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    LINEAR ASSUMPTION WARNING                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   The formula assumes: "If hazard frequency increases X%, BI increases X%"      │
│                                                                                  │
│   Reality may be NON-LINEAR:                                                    │
│   • Flood: Drainage overwhelm → Convex (worse than linear)                     │
│   • Hail: Size threshold → Step function                                        │
│   • Wind: Damage ∝ v³ → Cubic relationship                                      │
│                                                                                  │
│   IMPLICATION: Linear model may UNDERESTIMATE true impact for severe events.   │
│   Phase 1 should explore non-linear relationships.                              │
│                                                                                  │
│   VISUAL:                                                                       │
│                                                                                  │
│   BI Loss │           ╱ Non-linear (reality?)                                   │
│           │         ╱╱                                                          │
│           │       ╱╱                                                            │
│           │     ╱╱  ╱ Linear (current model)                                    │
│           │   ╱╱  ╱                                                             │
│           │ ╱╱  ╱                                                               │
│           │╱  ╱                                                                 │
│           └────────────────────                                                 │
│                   Climate Change (SCVR) →                                       │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 3.5 Complete Worked Example: Maverick Creek Wind BI

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│            MAVERICK CREEK WIND (491.6 MW) - BI CALCULATION                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   BASELINE BI (InfraSure existing estimates):                                   │
│   ┌──────────────┬────────────┬─────────────────────────────────────────────┐   │
│   │ Hazard       │ BI_base    │ What It Represents                          │   │
│   ├──────────────┼────────────┼─────────────────────────────────────────────┤   │
│   │ Flood        │ $150K/yr   │ Site access, substation damage              │   │
│   │ Hail         │  $80K/yr   │ Blade repairs, downtime                     │   │
│   │ Extreme Wind │ $120K/yr   │ Cut-out losses, minor damage                │   │
│   │ Icing        │  $60K/yr   │ Blade icing downtime                        │   │
│   ├──────────────┼────────────┼─────────────────────────────────────────────┤   │
│   │ TOTAL        │ $410K/yr   │                                             │   │
│   └──────────────┴────────────┴─────────────────────────────────────────────┘   │
│                                                                                  │
│   YEAR 2040 CLIMATE SCENARIO (RCP 4.5):                                         │
│   ┌──────────────┬────────────┬────────────┬─────────────────┐                  │
│   │ Hazard       │ BI_base    │ HCR(2040)  │ BI_climate      │                  │
│   ├──────────────┼────────────┼────────────┼─────────────────┤                  │
│   │ Flood        │ $150K      │ +36%       │ $150K×1.36=$204K│                  │
│   │ Hail         │  $80K      │ +36%       │  $80K×1.36=$109K│                  │
│   │ Extreme Wind │ $120K      │ +12%       │ $120K×1.12=$134K│                  │
│   │ Icing        │  $60K      │ -50%       │  $60K×0.50= $30K│ ← DECREASES!    │
│   ├──────────────┼────────────┼────────────┼─────────────────┤                  │
│   │ TOTAL        │ $410K/yr   │            │ $477K/yr        │                  │
│   └──────────────┴────────────┴────────────┴─────────────────┘                  │
│                                                                                  │
│   ADDITIONAL BI LOSS = $477K - $410K = $67K/year                                │
│                                                                                  │
│   Over 35-year asset life (NPV at 10% WACC): ~$600K additional BI impact       │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 4. Pathway B: Climate → Generation Performance

## 4.1 Overview

This pathway uses physics-based models to calculate how changed weather affects generation.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    PATHWAY B: THE LOGIC FLOW                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   CMIP Variables                                                                │
│   • rsds (solar irradiance / GHI)                                              │
│   • sfcWind (10m wind speed)                                                    │
│   • tasmax, tasmin (temperature)                                                │
│   • hurs (humidity)                                                             │
│         │                                                                        │
│         ▼                                                                        │
│   PHYSICS-BASED PERFORMANCE MODELS                                              │
│   • Solar: pvlib (includes Temperature Coefficient automatically)              │
│   • Wind: PyWake or similar (includes power curve, cut-out)                    │
│         │                                                                        │
│         ▼                                                                        │
│   GENERATION (MWh)                                                              │
│   • Accounts for temperature effects on efficiency                             │
│   • Accounts for icing losses (wind)                                           │
│   • Accounts for cut-out losses (wind)                                         │
│         │                                                                        │
│         ▼                                                                        │
│   REVENUE                                                                       │
│   Revenue_climate = MWh_climate × Price                                         │
│                                                                                  │
│   NOTE: Performance models ALREADY include temperature/icing/cut-out effects.  │
│   You don't need to apply these separately.                                     │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 4.2 Solar Performance Modeling

### Key Input: Solar Irradiance (rsds)

NEX-GDDP-CMIP6 provides `rsds` (Surface Downwelling Shortwave Radiation), which is essentially GHI (Global Horizontal Irradiance).

**pvlib Workflow:**
```python
import pvlib

# Load CMIP6 climate data
rsds = load_nex_gddp('rsds', lat, lon, scenario='ssp245')
temperature = load_nex_gddp('tasmax', lat, lon, scenario='ssp245')

# Define system
system = pvlib.pvsystem.PVSystem(
    module_parameters=module_params,
    inverter_parameters=inverter_params,
    temperature_model_parameters=temp_params
)

# Run model
mc = pvlib.modelchain.ModelChain(system, location)
mc.run_model(weather_data)  # weather_data includes irradiance, temp, wind

# Get output
ac_power = mc.results.ac  # Already accounts for temperature losses!
```

### Temperature Coefficient (Built Into pvlib)

**Formula:**
```
P_actual = P_rated × [1 + γ × (T_cell − 25°C)]
```

Where:
- γ = Temperature coefficient (-0.003 to -0.005 per °C)
- T_cell = Cell temperature (NOT ambient!)

**Cell Temperature Estimation:**
```
T_cell = T_ambient + (NOCT - 20) × (G / 800)
```

**Example:**
- Hot day: T_ambient = 40°C, G = 1000 W/m²
- T_cell = 40 + (45 - 20) × (1000/800) = 71.25°C
- P_actual = P_rated × [1 - 0.004 × (71.25 - 25)] = P_rated × 0.815
- **18.5% power loss** on this hot day

**Climate Impact:** If average temperature increases +2°C, expect ~1% annual generation reduction.

## 4.3 Wind Performance Modeling

### Key Effects Built Into Wind Models

| Effect | How It's Handled | Model |
|--------|------------------|-------|
| Power Curve | Turbine-specific v → P relationship | PyWake |
| Cut-Out | P = 0 when v > 25 m/s | Power curve |
| Icing | P_iced = P_normal × (1 - L_ice) | Custom factor |
| Wake Effects | Reduced wind for downstream turbines | PyWake |

### Icing Loss Model

**Condition:** Icing if T < 0°C AND RH > 75%

**Formula:**
```
P_iced = P_normal × (1 − L_ice)
```

Where L_ice = 0.2 (light) to 0.8 (severe)

**Climate Impact:** Warming → Fewer icing days → Potential INCREASE in generation for cold-climate sites. For Texas sites, icing is already minimal.

### Cut-Out Logic

**Rule:** If Wind > 25 m/s (at hub height), Power = 0

**Climate Impact:** If extreme wind events increase, more hours are lost to cut-out. However, this protects the turbine from damage (it's a feature, not a bug).

## 4.4 Revenue Calculation

```
Revenue_climate(year) = MWh_climate(year) × Price(year)
```

**Price Assumption (Pilot):** Stationary - use historical price distributions

**Phase 1 Enhancement:** Link prices to EIA AEO forecasts or model price-climate correlations

## 4.5 Complete Worked Example: Hayhurst Solar Performance

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│            HAYHURST SOLAR (24.8 MW) - GENERATION IMPACT                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   BASELINE (1980-2010 climate):                                                 │
│   • Annual GHI: 2,050 kWh/m²                                                    │
│   • Average ambient temp during daylight: 28°C                                  │
│   • Average cell temp: 52°C                                                     │
│   • Capacity factor: 22.0%                                                      │
│   • Annual generation: 47,800 MWh                                               │
│                                                                                  │
│   CLIMATE SCENARIO (2030-2050 average, SSP2-4.5):                               │
│   • Annual GHI: 2,060 kWh/m² (+0.5%)                                           │
│   • Average ambient temp: 30.1°C (+2.1°C)                                       │
│   • Average cell temp: 54.6°C (+2.6°C)                                          │
│                                                                                  │
│   TEMPERATURE COEFFICIENT IMPACT:                                               │
│   • Additional temp loss: 2.6°C × 0.4%/°C = -1.04%                             │
│   • Irradiance gain: +0.5%                                                      │
│   • Net impact: -0.54%                                                          │
│                                                                                  │
│   CLIMATE GENERATION:                                                           │
│   • Capacity factor: 22.0% × 0.9946 = 21.88%                                   │
│   • Annual generation: 47,542 MWh (vs 47,800 baseline)                         │
│   • Annual revenue impact: -$13.4K (at $52/MWh)                                │
│                                                                                  │
│   Over 22-year IUL (NPV at 10% WACC): ~$120K generation impact                 │
│                                                                                  │
│   NOTE: This is relatively SMALL compared to life reduction impact.            │
│   Texas is already hot - panels are designed for it.                           │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 5. Pathway C: Climate Stress → Equipment Life

## 5.1 Overview

This pathway quantifies how climate stress accelerates equipment degradation.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    PATHWAY C: THE LOGIC FLOW                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   CMIP Variables                                                                │
│   • Temperature (tasmax, tasmin)                                                │
│   • Humidity (hurs)                                                             │
│   • Wind (sfcWind)                                                              │
│         │                                                                        │
│         ▼                                                                        │
│   SCIENTIFIC DEGRADATION MODELS                                                 │
│                                                                                  │
│   Solar PV:                                                                     │
│   • Peck's Model (heat + humidity → accelerated aging)                         │
│   • Coffin-Manson (freeze/thaw → mechanical fatigue)                           │
│                                                                                  │
│   Wind:                                                                         │
│   • Palmgren-Miner (wind variability → structural fatigue)                     │
│         │                                                                        │
│         ▼                                                                        │
│   LIFE REDUCTION                                                                │
│   "Climate stress causes X% reduction in useful life"                          │
│         │                                                                        │
│         ▼                                                                        │
│   EFR (Equipment Failure Ratio)                                                 │
│   A linearized summary: "X% life reduction per % SCVR"                         │
│   (Allows quick lookup without running full models each time)                   │
│         │                                                                        │
│         ▼                                                                        │
│   IUL (Impaired Useful Life)                                                    │
│   IUL = EUL × [1 - Σ(EFR_i × SCVR_i)]                                          │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 5.2 The Scientific Models

### 5.2.1 Peck's Model (Solar PV - Heat + Humidity)

**Purpose:** Estimate accelerated aging from heat and humidity exposure

**Physics:** High temperature and humidity accelerate chemical degradation of EVA encapsulant, causing delamination, yellowing, and power loss.

**Formula (Arrhenius-Peck form):**
```
η = A × RH^n × exp(-Ea / (R × T))
```

Where:
- η = Aging acceleration factor
- RH = Relative humidity (%)
- T = Module temperature (Kelvin)
- A, n, Ea/R = Material constants

**Interpretation:**
- η = 1.0: Normal aging
- η = 1.5: Panel ages 1.5 years per calendar year (50% faster)
- η = 2.0: Panel ages 2 years per calendar year (100% faster)

**Converting to EFR:**
```
If η_climate / η_baseline = 1.2 (20% faster aging):
  Life reduction = (25 - 25/1.2) / 25 = 16.7%
  If SCVR_heat+humidity = 78%:
  EFR = 16.7% / 78% = 0.21% per % SCVR
```

---

### 5.2.2 Coffin-Manson Model (Solar PV - Thermal Cycling)

**Purpose:** Estimate cycles to failure from freeze/thaw thermal stress

**Physics:** Temperature swings cause expansion/contraction, creating mechanical stress at solder joints and cell interconnects.

**Formula:**
```
N_f = C × (Δε_p)^(-k)
```

Where:
- N_f = Number of cycles to failure
- Δε_p = Plastic strain amplitude ∝ ΔT × CTE
- C, k = Material constants

**Climate Impact:**
- Warming → Fewer freeze events → Fewer thermal cycles
- But remaining cycles may have larger ΔT (more extreme)
- Net effect depends on location

**For Texas (Hayhurst Solar):**
- Thermal cycling is NOT the limiting degradation mechanism
- N_f >> 25 years worth of cycles
- Climate impact on this factor is small

---

### 5.2.3 Palmgren-Miner Rule (Wind - Structural Fatigue)

**Purpose:** Estimate cumulative fatigue damage from wind load cycles

**Physics:** Fluctuating wind creates cyclic stress on blades, tower, gearbox. Damage accumulates until component fails.

**Formula:**
```
D = Σ (n_i / N_i)

Where:
  D = Cumulative damage (D = 1 means failure)
  n_i = Actual cycles at stress level i
  N_i = Cycles to failure at stress level i (from S-N curve)
```

**Wind Speed → Stress:**
```
Aerodynamic load ∝ v² (wind speed squared)
```

Higher wind speeds cause disproportionately more damage!

**Climate Impact:**
- Increased wind variability → More time in high-stress bins
- Small increase in extreme wind → Large increase in fatigue damage
- This is often the LARGEST life impact for wind assets

---

## 5.3 The EFR Table

The EFR table provides a linearized summary for quick IUL calculations:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    EFR TABLE (Pilot Values - To Be Calibrated)                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   SOLAR PV:                                                                     │
│   ┌─────────────────────┬─────────────────────┬─────────────────────────────┐   │
│   │ Climate Variable    │ EFR (% per % SCVR)  │ Source Model                │   │
│   ├─────────────────────┼─────────────────────┼─────────────────────────────┤   │
│   │ Heat + Humidity     │ 0.20 - 0.25%        │ Peck's Model                │   │
│   │ Thermal Cycling     │ 0.10 - 0.15%        │ Coffin-Manson               │   │
│   │ Humidity alone      │ 0.05 - 0.10%        │ Encapsulant degradation     │   │
│   └─────────────────────┴─────────────────────┴─────────────────────────────┘   │
│                                                                                  │
│   WIND:                                                                         │
│   ┌─────────────────────┬─────────────────────┬─────────────────────────────┐   │
│   │ Climate Variable    │ EFR (% per % SCVR)  │ Source Model                │   │
│   ├─────────────────────┼─────────────────────┼─────────────────────────────┤   │
│   │ Wind Variability    │ 1.5 - 2.0%          │ Palmgren-Miner              │   │
│   │ Icing Events        │ 0.3 - 0.5%          │ Ice damage accumulation     │   │
│   │ Extreme Wind        │ 0.2 - 0.4%          │ Gearbox/bearing stress      │   │
│   └─────────────────────┴─────────────────────┴─────────────────────────────┘   │
│                                                                                  │
│   ⚠️ NOTE: Wind EFR is HIGH because fatigue is non-linear with wind speed.    │
│   Small SCVR changes in extreme wind bins have large life impacts.             │
│                                                                                  │
│   These values will be calibrated against literature in Step 4.                 │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 5.3.1 ⚠️ EFR: Better Defined, But Still Needs Calibration

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    GAP ANALYSIS: EFR CALIBRATION                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   GOOD NEWS vs HCR:                                                             │
│   • Team's Appendix 2 provides SCIENTIFIC MODELS (Peck's, C-M, P-M)            │
│   • These are peer-reviewed, physics-based                                      │
│   • The formulas are well-defined                                              │
│                                                                                  │
│   GAP: MATERIAL CONSTANTS ARE NOT PROVIDED                                     │
│   ─────────────────────────────────────────                                     │
│                                                                                  │
│   Peck's Model: η = A × RH^n × exp(-Ea / (R × T))                             │
│   • A = ? (pre-exponential factor)                                             │
│   • n = ? (humidity exponent)                                                  │
│   • Ea/R = ? (activation energy / gas constant)                               │
│   • These depend on PV module chemistry (EVA type, backsheet, etc.)           │
│                                                                                  │
│   Coffin-Manson: N_f = C × (Δε_p)^(-k)                                        │
│   • C = ? (material constant)                                                  │
│   • k = ? (fatigue exponent, typically 1.5-2.5)                               │
│   • Δε_p depends on material CTE and ΔT                                       │
│                                                                                  │
│   Palmgren-Miner: D = Σ (n_i / N_i)                                           │
│   • N_i = f(stress_i) requires S-N curve for turbine components               │
│   • S-N curves are typically proprietary to turbine manufacturers              │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   HOW TO CALIBRATE (OPTIONS):                                                  │
│                                                                                  │
│   Option 1: LITERATURE-BASED                                                   │
│   □ Find papers with calibrated Peck's model for crystalline silicon PV       │
│   □ Find IEC standards (IEC 61215, 61730) with test parameters                │
│   □ Find wind turbine fatigue studies with published S-N curves               │
│                                                                                  │
│   Option 2: MANUFACTURER DATA                                                  │
│   □ Request degradation curves from PV module manufacturers                    │
│   □ Request fatigue life data from turbine OEMs (likely proprietary)          │
│                                                                                  │
│   Option 3: EMPIRICAL CALIBRATION                                              │
│   □ Use InfraSure's historical performance data                               │
│   □ Compare observed degradation in hot/humid vs mild climates                │
│   □ Fit model parameters to actual data                                       │
│                                                                                  │
│   Option 4: INDUSTRY BENCHMARKS                                                │
│   □ Use generic values from NREL reports, IEA PVPS studies                    │
│   □ Apply safety factors for uncertainty                                       │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 5.3.2 TODO: EFR Parameter Literature Search

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TODO: CALIBRATE EFR PARAMETERS                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   PECK'S MODEL (Heat + Humidity):                                              │
│   □ Search: "Peck model PV degradation parameters" papers                      │
│   □ Search: IEC 61215 accelerated aging test data                             │
│   □ Key ref: Osterwald et al. (NREL) - PV degradation rates                   │
│   □ Key ref: Jordan et al. (2017) - compendium of degradation rates           │
│   □ Extract: A, n, Ea values for crystalline silicon                          │
│                                                                                  │
│   COFFIN-MANSON (Thermal Cycling):                                             │
│   □ Search: "PV solder joint thermal cycling" papers                          │
│   □ Key ref: Guyenot et al. (2011) - solder fatigue in PV                     │
│   □ Extract: C, k values for typical cell interconnects                       │
│   □ Note: May be less critical for TX location (few freeze cycles)            │
│                                                                                  │
│   PALMGREN-MINER (Wind Fatigue):                                               │
│   □ Search: "wind turbine fatigue life climate change" papers                 │
│   □ Key ref: Ziegler et al. (2018) - climate impact on turbine fatigue       │
│   □ Extract: Sensitivity of fatigue life to wind variability                  │
│   □ Note: S-N curves are proprietary; use generic IEC 61400 values            │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   DELIVERABLE FORMAT:                                                          │
│                                                                                  │
│   ┌───────────────┬───────────┬───────────┬──────────────────────────────────┐ │
│   │ Model         │ Parameter │ Value     │ Source / Citation                │ │
│   ├───────────────┼───────────┼───────────┼──────────────────────────────────┤ │
│   │ Peck's        │ A         │ ?         │ [Paper/Standard]                 │ │
│   │ Peck's        │ n         │ ?         │ [Paper/Standard]                 │ │
│   │ Peck's        │ Ea/R      │ ?         │ [Paper/Standard]                 │ │
│   │ Coffin-Manson │ C         │ ?         │ [Paper/Standard]                 │ │
│   │ Coffin-Manson │ k         │ ?         │ [Paper/Standard]                 │ │
│   │ Palmgren-Miner│ S-N curve │ Generic   │ IEC 61400 / [Paper]              │ │
│   └───────────────┴───────────┴───────────┴──────────────────────────────────┘ │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 5.4 IUL Calculation

**Formula:**
```
IUL = EUL × [1 - Σ(EFR_i × SCVR_i)]
```

**⚠️ Key Assumption: Linear Scaling**

Same caveat as HCR - the scientific models are non-linear, but we're linearizing for simplicity. This is acceptable for moderate SCVR changes but may break down at extremes.

## 5.5 Complete Worked Example: Hayhurst Solar Life Reduction

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│            HAYHURST SOLAR (24.8 MW) - IUL CALCULATION                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   BASE PARAMETERS:                                                              │
│   • EUL = 25 years                                                              │
│   • Location: Culberson, TX (hot, semi-arid)                                    │
│                                                                                  │
│   CLIMATE STRESS (2030-2050 period average under RCP 4.5):                      │
│   ┌────────────────────┬────────────┬─────────────────────────────────────────┐ │
│   │ Variable           │ SCVR       │ Interpretation                          │ │
│   ├────────────────────┼────────────┼─────────────────────────────────────────┤ │
│   │ Heat + Humidity    │ +78%       │ 78% more tropical nights                │ │
│   │ Freeze/Thaw        │ -29%       │ 29% fewer thermal cycles (benefit!)     │ │
│   │ Humidity alone     │ +15%       │ 15% more high-humidity days             │ │
│   └────────────────────┴────────────┴─────────────────────────────────────────┘ │
│                                                                                  │
│   EFR APPLICATION:                                                              │
│   ┌────────────────────┬────────────┬────────────┬────────────────────────────┐│
│   │ Variable           │ SCVR       │ EFR        │ Life Impact                ││
│   ├────────────────────┼────────────┼────────────┼────────────────────────────┤│
│   │ Heat + Humidity    │ +78%       │ 0.22%      │ 78% × 0.22% = +17.2%       ││
│   │ Freeze/Thaw        │ -29%       │ 0.12%      │ -29% × 0.12% = -3.5%       ││
│   │ Humidity alone     │ +15%       │ 0.08%      │ 15% × 0.08% = +1.2%        ││
│   ├────────────────────┼────────────┼────────────┼────────────────────────────┤│
│   │ TOTAL              │            │            │ +14.9% net life reduction  ││
│   └────────────────────┴────────────┴────────────┴────────────────────────────┘│
│                                                                                  │
│   IUL CALCULATION:                                                              │
│   IUL = 25 × (1 - 0.149) = 25 × 0.851 = 21.3 years ≈ 21 years                 │
│                                                                                  │
│   INTERPRETATION:                                                               │
│   "Climate stress reduces Hayhurst Solar's life from 25 to ~21 years"          │
│   That's 4 years of lost revenue at end of life.                               │
│                                                                                  │
│   NPV IMPACT:                                                                   │
│   • Years 22-25 revenue (base): ~$8.6M undiscounted, ~$2.8M NPV               │
│   • This is ~12% of total NPV_base                                             │
│   • Life reduction is the SINGLE BIGGEST contributor to NAV impairment!       │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 6. Bringing It Together: NAV Impairment

## 6.1 The Complete Calculation

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE MATHEMATICAL FORMULATION                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   STEP 1: BASELINE NPV                                                          │
│   ══════════════════════                                                         │
│                                                                                  │
│   For t = 1 to EUL:                                                             │
│     Revenue_base(t) = MWh_base(t) × Price(t)                                   │
│     BI_base(t) = Σ BI_base_hazard                                              │
│     Net_base(t) = Revenue_base(t) - BI_base(t)                                 │
│                                                                                  │
│   NPV_base = Σ [Net_base(t) / (1 + WACC)^t]                                    │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 2: CLIMATE SCENARIO NPV                                                  │
│   ══════════════════════════════                                                 │
│                                                                                  │
│   Calculate IUL:                                                                │
│     Total_life_reduction = Σ [EFR_v × SCVR_v]                                  │
│     IUL = EUL × (1 - Total_life_reduction)                                     │
│                                                                                  │
│   For t = 1 to IUL:                                                             │
│     Revenue_climate(t) = MWh_climate(t) × Price(t)  (from Pathway B)           │
│     HCR_h(t) = f(SCVR_relevant)  for each hazard h                             │
│     BI_climate(t) = Σ [BI_base_h × (1 + HCR_h(t))]  (from Pathway A)          │
│     Net_climate(t) = Revenue_climate(t) - BI_climate(t)                        │
│                                                                                  │
│   NPV_climate = Σ [Net_climate(t) / (1 + WACC)^t]                              │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 3: NAV IMPAIRMENT                                                        │
│   ══════════════════════                                                         │
│                                                                                  │
│   NAV_Impairment_% = (1 - NPV_climate / NPV_base) × 100%                       │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   INTERPRETATION SCALE:                                                         │
│   • 0-10%:   Low climate risk - Minimal adjustment needed                      │
│   • 10-25%:  Moderate climate risk - Factor into pricing                       │
│   • 25-50%:  High climate risk - Significant value haircut                     │
│   • >50%:    Severe climate risk - Asset may be unfinanceable                  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 6.2 Sensitivity Analysis: What Matters Most?

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    SENSITIVITY ANALYSIS                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   For Hayhurst Solar (24.8 MW), varying one input at a time:                   │
│                                                                                  │
│   ┌─────────────────────────────┬────────────────────┬───────────────────────┐  │
│   │ Parameter                   │ Variation          │ NAV Impairment Change │  │
│   ├─────────────────────────────┼────────────────────┼───────────────────────┤  │
│   │ EFR_heat+humidity           │ 0.15% → 0.30%      │ 22% → 35%             │  │
│   │ SCVR_heat+humidity          │ +50% → +100%       │ 22% → 32%             │  │
│   │ HCR_flood coefficient       │ 1.0 → 2.0          │ 28% → 31%             │  │
│   │ Generation loss             │ -0.5% → -2%        │ 28% → 30%             │  │
│   │ WACC                        │ 10% → 6%           │ 28% → 32%             │  │
│   │ Wind EUL assumption         │ 35yr → 25yr        │ (Wind) +8%            │  │
│   └─────────────────────────────┴────────────────────┴───────────────────────┘  │
│                                                                                  │
│   KEY FINDING:                                                                  │
│   ─────────────                                                                 │
│   EFR (Equipment Failure Ratio) is the MOST SENSITIVE parameter.               │
│   Small changes in EFR calibration → Large changes in NAV impairment.          │
│                                                                                  │
│   This is because:                                                              │
│   1. EFR affects LIFE, which means LOSING ENTIRE YEARS of revenue              │
│   2. Those lost years are at end of life (lower discount, but still big $)     │
│   3. EFR uncertainty is high (depends on material constants)                   │
│                                                                                  │
│   RECOMMENDATION:                                                               │
│   Present NAV impairment as a RANGE, not a point estimate.                     │
│   E.g., "NAV impairment: 22-35% under RCP 4.5"                                 │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 6.3 Final Results: Pilot Assets

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    PILOT RESULTS SUMMARY                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   HAYHURST SOLAR (24.8 MW, Culberson TX)                                        │
│   ═══════════════════════════════════════                                        │
│   • EUL: 25 years → IUL: 21 years                                              │
│   • BI increase: +42% ($95K → $135K/year)                                      │
│   • Generation impact: -0.5%/year                                               │
│   • NPV_base: $22.8M → NPV_climate: $16.5M                                     │
│   • NAV Impairment: 27.6% [22-35% range]                                       │
│                                                                                  │
│   Breakdown:                                                                    │
│   • Life reduction: ~16% of impairment                                         │
│   • BI increase: ~7% of impairment                                             │
│   • Generation loss: ~5% of impairment                                         │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   MAVERICK CREEK WIND (491.6 MW, Concho TX)                                     │
│   ═══════════════════════════════════════════                                    │
│   • EUL: 35 years → IUL: 27 years (illustrative)                               │
│   • BI increase: +16% ($410K → $477K/year)                                     │
│   • Generation impact: +1% (more wind, fewer icing days)                       │
│   • NPV_base: $XXX → NPV_climate: $XXX                                         │
│   • NAV Impairment: ~25% [18-35% range]                                        │
│                                                                                  │
│   Breakdown:                                                                    │
│   • Life reduction: ~22% of impairment (Palmgren-Miner dominant)               │
│   • BI increase: ~5% of impairment                                             │
│   • Generation change: -2% of impairment (slight benefit)                      │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   KEY INSIGHT: Life reduction is the biggest driver for BOTH assets.           │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 7. Implementation

## 7.1 Work Plan (4 Steps, 2 Weeks)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    WORK PLAN MAPPED TO THREE PATHWAYS                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   STEP 1: Climate Data & SCVR (Days 1-3)                                        │
│   ═══════════════════════════════════════                                        │
│   Feeds: ALL THREE PATHWAYS                                                     │
│                                                                                  │
│   Tasks:                                                                        │
│   • Download NEX-GDDP-CMIP6 for sample site locations                          │
│   • Extract variables: tasmax, tasmin, pr, sfcWind, hurs, rsds                 │
│   • Compute climate conditions (Heat Wave, etc.)                               │
│   • Calculate SCVR for each condition by period                                │
│                                                                                  │
│   Output: SCVR tables (2030, 2040, 2050)                                       │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 2: Asset Performance Simulation (Days 4-5)                               │
│   ═══════════════════════════════════════════════                               │
│   Feeds: PATHWAY B (Generation)                                                 │
│                                                                                  │
│   Tasks:                                                                        │
│   • Run pvlib/PyWake with climate scenario inputs                              │
│   • Generate MWh projections (baseline vs climate)                             │
│   • Calculate Revenue_climate                                                   │
│   • First 3 years: Use InfraSure S2S forecasts                                 │
│                                                                                  │
│   Output: Year-by-year generation and revenue (P10/P50/P90)                    │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 3: HCR & BI Calculation (Days 6-7)                                       │
│   ═══════════════════════════════════════                                        │
│   Feeds: PATHWAY A (Hazards)                                                    │
│                                                                                  │
│   Tasks:                                                                        │
│   • Literature review for SCVR → HCR relationships                             │
│   • Derive HCR table with documented sources                                   │
│   • Calculate BI_climate from HCR × BI_base                                    │
│                                                                                  │
│   Output: HCR table, BI projections                                            │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 4: EFR & IUL Calculation (Days 8-9)                                      │
│   ═══════════════════════════════════════                                        │
│   Feeds: PATHWAY C (Equipment Life)                                             │
│                                                                                  │
│   Tasks:                                                                        │
│   • Calibrate Peck's Model parameters from literature                          │
│   • Apply Coffin-Manson (if relevant for site)                                 │
│   • Apply Palmgren-Miner for wind fatigue                                      │
│   • Derive EFR table                                                           │
│   • Calculate IUL                                                              │
│                                                                                  │
│   Output: EFR table, IUL values                                                │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   STEP 5: Final NPV & NAV Impairment (Day 10)                                   │
│   ═══════════════════════════════════════════                                    │
│                                                                                  │
│   Tasks:                                                                        │
│   • Combine all pathways                                                        │
│   • Calculate NPV_base and NPV_climate                                         │
│   • Compute NAV Impairment %                                                   │
│   • Sensitivity analysis                                                        │
│   • Prepare investor-ready output                                              │
│                                                                                  │
│   Output: NAV Impairment % with uncertainty range                              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 7.2 Data Sources

| Data Type | Source | Resolution | Variables |
|-----------|--------|------------|-----------|
| Climate Projections | NEX-GDDP-CMIP6 | 0.25° daily | tasmax, tasmin, pr, sfcWind, hurs, rsds |
| Historical Baseline | ERA5 | 0.25° hourly | All standard met variables |
| Performance Models | InfraSure | Site-specific | MWh, Revenue |
| Baseline BI | InfraSure | Asset-specific | BI per hazard |
| S2S Forecasts | InfraSure | 1-36 months | Weather, Generation |

## 7.3 Technical Requirements

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TECHNICAL STACK                                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   PYTHON PACKAGES:                                                              │
│   • xarray, dask - Climate data handling                                        │
│   • pvlib - Solar performance modeling                                          │
│   • numpy, pandas - Data manipulation                                           │
│   • scipy - Statistical calculations                                            │
│   • matplotlib, plotly - Visualization                                          │
│                                                                                  │
│   DATA ACCESS:                                                                  │
│   • NASA Earthdata (NEX-GDDP-CMIP6)                                            │
│   • CDS API (ERA5)                                                              │
│   • InfraSure internal APIs                                                     │
│                                                                                  │
│   COMPUTE:                                                                      │
│   • Local workstation sufficient for 2 sites                                   │
│   • Cloud (GCP) for scaling to full portfolio                                  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 8. Assessment

## 8.1 Strengths

| Strength | Why It Matters |
|----------|----------------|
| **Clear business value** | NAV impairment % directly answers investor questions |
| **Three-pathway structure** | Transparent, defensible, modular |
| **Scientific foundation** | Peck's, Coffin-Manson, Palmgren-Miner are peer-reviewed |
| **Builds on InfraSure** | Reuses validated performance models and BI estimates |
| **Solar irradiance available** | NEX-GDDP-CMIP6 rsds enables direct solar modeling |
| **Reasonable scope** | 2 sites, 1 scenario, clear exclusions |
| **Transparent assumptions** | WACC, EUL, exclusions all documented |

## 8.2 Concerns and Limitations

| Concern | Severity | Mitigation |
|---------|----------|------------|
| HCR values uncertain | Medium | Literature review + sensitivity range |
| EFR calibration needed | High | Use Jordan & Kurtz, field validation |
| 35-year Wind EUL optimistic | Medium | Show 25-year sensitivity |
| Linear assumptions | Medium | Acceptable for pilot; Phase 1 non-linear |
| No price evolution | Low (pilot) | Add in Phase 1 |
| 10% WACC may be high | Low | Show 6-8% sensitivity |
| S2S → CMIP transition | Low | Validate continuity at year 3-4 |

## 8.3 Recommendations

### For the Pilot (2 Weeks)

**HIGH PRIORITY:**
1. Use NEX-GDDP-CMIP6 for climate data (rsds available)
2. Allocate 3-4 days for HCR literature review (Step 3)
3. Work through full Peck's Model calibration example
4. Present NAV impairment as RANGE, not point estimate

**MEDIUM PRIORITY:**
5. Show sensitivity to key parameters (EFR, WACC, EUL)
6. Document all assumptions transparently
7. Validate S2S → CMIP transition at year 3-4

### For Phase 1 Implementation

1. **Price evolution model** - Link to EIA AEO or model price-climate correlations
2. **Non-linear relationships** - Explore convex HCR for flood, wind
3. **Manufacturer data** - Get actual S-N curves for Palmgren-Miner
4. **Field validation** - Compare model vs observed degradation
5. **Third-party review** - Climate scientist + materials engineer

---

# 9. Appendices

## Appendix A: Key Equations Summary

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    EQUATION REFERENCE                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   SCVR:                                                                         │
│   SCVR = [Metric(future) - Metric(baseline)] / Metric(baseline)                │
│                                                                                  │
│   HCR:                                                                          │
│   HCR_hazard = f(SCVR_relevant)                                                │
│                                                                                  │
│   BI:                                                                           │
│   BI_climate = Σ [BI_base_h × (1 + HCR_h)]                                     │
│                                                                                  │
│   EFR:                                                                          │
│   EFR = Life_reduction / SCVR                                                   │
│                                                                                  │
│   IUL:                                                                          │
│   IUL = EUL × [1 - Σ(EFR_i × SCVR_i)]                                          │
│                                                                                  │
│   NPV:                                                                          │
│   NPV = Σ [Net_Revenue(t) / (1 + WACC)^t]                                      │
│                                                                                  │
│   NAV Impairment:                                                               │
│   NAV_Impairment_% = (1 - NPV_climate / NPV_base) × 100%                       │
│                                                                                  │
│   Peck's Model:                                                                 │
│   η = A × RH^n × exp(-Ea / (R × T))                                            │
│                                                                                  │
│   Coffin-Manson:                                                                │
│   N_f = C × (Δε_p)^(-k)                                                        │
│                                                                                  │
│   Palmgren-Miner:                                                               │
│   D = Σ (n_i / N_i), failure when D = 1                                        │
│                                                                                  │
│   Temperature Coefficient:                                                      │
│   P_actual = P_rated × [1 + γ × (T_cell − 25°C)]                               │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Appendix B: CMIP6 vs CMIP5

See `CMIP5_vs_CMIP6_COMPARISON.md` for detailed comparison.

**Summary:** Recommend NEX-GDDP-CMIP6 for pilot because:
- Includes rsds (solar irradiance) directly
- Bias-corrected and downscaled
- SSP scenarios better for investor communication

## Appendix C: Terminology

See `TERMINOLOGY.md` for comprehensive glossary.

## Appendix D: Comprehensive TODO List and Gap Analysis

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    PILOT TODO LIST - CONSOLIDATED                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   PRIORITY 1: CRITICAL GAPS (Must resolve for pilot to work)                   │
│   ═══════════════════════════════════════════════════════════                   │
│                                                                                  │
│   □ 1.1 SCVR → HCR CONVERSION (Step 3)                                         │
│     ────────────────────────────────────                                        │
│     Status: NOT DEFINED in team's document                                      │
│     What's needed:                                                              │
│     □ Literature review for each hazard-SCVR relationship                      │
│     □ Define functional form (linear? power law?)                              │
│     □ Extract/estimate coefficients                                            │
│     □ Document sources                                                          │
│                                                                                  │
│     Hazards to cover:                                                           │
│     □ Pluvial Flood ↔ SCVR_precip                                             │
│     □ Hail ↔ SCVR_temp, SCVR_wind, SCVR_precip                               │
│     □ Extreme Wind ↔ SCVR_wind                                                │
│     □ Heat Shutdown ↔ SCVR_heatwave                                           │
│     □ Icing ↔ SCVR_freeze                                                     │
│                                                                                  │
│     FALLBACK: If literature is sparse, use HCR = 1.0 × SCVR (linear 1:1)      │
│     and document as conservative assumption.                                    │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   □ 1.2 BASELINE BI ESTIMATES (Step 3)                                         │
│     ──────────────────────────────────                                          │
│     Status: Team says "InfraSure BI estimates" but not specified               │
│     What's needed:                                                              │
│     □ Obtain BI breakdown by hazard for Hayhurst Solar                         │
│     □ Obtain BI breakdown by hazard for Maverick Creek Wind                    │
│     □ Confirm source (existing model? insurance? benchmark?)                   │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   □ 1.3 EFR PARAMETER CALIBRATION (Step 4)                                     │
│     ─────────────────────────────────────                                       │
│     Status: Scientific models provided, but constants missing                  │
│     What's needed:                                                              │
│     □ Peck's Model: A, n, Ea/R for crystalline silicon PV                     │
│     □ Coffin-Manson: C, k for solder joints                                   │
│     □ Palmgren-Miner: S-N curve or sensitivity factor                         │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   PRIORITY 2: METHODOLOGY CLARIFICATIONS                                        │
│   ═══════════════════════════════════════                                        │
│                                                                                  │
│   □ 2.1 SCVR COMPUTATION METHOD                                                │
│     □ Confirm: Area-based for all, or count-based for indices?                │
│     □ Define thresholds for exceedance (P90? equipment specs?)                │
│     □ Define baseline period (1985-2014 recommended)                          │
│     □ Define future periods (2030-2050 centered)                              │
│                                                                                  │
│   □ 2.2 ENSEMBLE HANDLING                                                      │
│     □ How many GCMs to include?                                               │
│     □ Equal weighting or performance-based?                                    │
│     □ Report mean SCVR or run full analysis per GCM?                         │
│     □ How to represent uncertainty (P10/P90)?                                 │
│                                                                                  │
│   □ 2.3 PERIOD INTERPRETATION                                                  │
│     □ Confirm: "2030" means 2020-2040 average, "2040" means 2030-2050?       │
│     □ How to handle years 1-3 (transition from S2S)?                         │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   PRIORITY 3: DATA AND INFRASTRUCTURE                                          │
│   ═══════════════════════════════════                                           │
│                                                                                  │
│   □ 3.1 CLIMATE DATA ACCESS                                                    │
│     □ Set up NASA Earthdata account for NEX-GDDP-CMIP6                        │
│     □ Download data for Culberson and Concho counties                         │
│     □ Verify rsds (solar) variable is present and usable                      │
│                                                                                  │
│   □ 3.2 INFRASURE INTEGRATION                                                  │
│     □ Confirm access to performance models (pvlib-based?)                     │
│     □ Confirm access to baseline BI estimates                                 │
│     □ Confirm S2S forecast format for years 1-3                              │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│   PRIORITY 4: QUESTIONS FOR TEAM                                               │
│   ═══════════════════════════════                                               │
│                                                                                  │
│   1. Do you have specific literature sources for SCVR → HCR?                  │
│   2. What are the Peck's Model γ parameters you plan to use?                  │
│   3. Do you have baseline BI estimates per hazard for pilot sites?            │
│   4. Should we use count-based or area-based SCVR for heat wave days?        │
│   5. How many GCMs should the pilot include?                                  │
│   6. Do you have S-N curves for Maverick Creek turbine model?                 │
│   7. Is Coffin-Manson relevant for the TX sites (limited freeze cycles)?      │
│   8. Confirm: Performance models already integrated with pvlib?               │
│   9. What's the format for S2S forecasts (years 1-3)?                        │
│   10. Any preference for uncertainty representation (P10/P90 vs std dev)?     │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Appendix E: Gap Summary Table

| Gap | Impact | Effort | Priority |
|-----|--------|--------|----------|
| SCVR → HCR formula | HIGH - affects all BI calculations | HIGH - literature review needed | 1 |
| Baseline BI estimates | HIGH - required input | LOW - likely exists internally | 1 |
| EFR parameters | HIGH - affects IUL calculation | MEDIUM - literature available | 1 |
| SCVR computation method | MEDIUM - affects consistency | LOW - design decision | 2 |
| Ensemble handling | MEDIUM - affects uncertainty | LOW - design decision | 2 |
| Climate data access | MEDIUM - blocks data steps | LOW - administrative | 3 |

---

*End of Document*

**Document History:**
- v1.0 (Feb 1, 2026): Initial unified framework document
- v1.1 (Feb 1, 2026): Added comprehensive TODO list and gap analysis
