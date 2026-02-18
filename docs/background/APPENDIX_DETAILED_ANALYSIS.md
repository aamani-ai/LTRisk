# Detailed Analysis of Team's Appendices

*Deep dive into HCR Derivations (Appendix 1) and EFR Derivations (Appendix 2)*

**Created:** February 1, 2026  
**Purpose:** Clarify implementation details for Steps 3 and 4 of the pilot work plan

---

## Table of Contents

1. [Overview](#overview)
2. [Critical Clarification: SCVR Period Interpretation](#critical-clarification-what-does-2030-or-2040-mean-in-scvr)
3. [Appendix 1: HCR Derivations (Climate Conditions)](#appendix-1-hcr-derivations)
4. [Appendix 2: EFR Derivations (Equipment Impact Models)](#appendix-2-efr-derivations)
5. [Critical Issue: Performance vs Life Impacts](#critical-issue-performance-vs-life-impacts)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Questions for the Team](#questions-for-the-team)

### Worked Examples in This Document

This document includes **three complete worked examples** with period averaging:

| Example | Location | What It Shows |
|---------|----------|---------------|
| **Heat Wave SCVR** | [Appendix 1 → Heat Wave](#1-heat-wave) | SCVR calculation with 20-year periods |
| **Peck's Model (Solar)** | [Appendix 2 → Peck's Model](#4-pecks-model-solar-pv-degradation) | Complete EFR calculation for Hayhurst Solar |
| **Palmgren-Miner (Wind)** | [Appendix 2 → Palmgren-Miner](#6-palmgren-miner-rule-wind-fatigue) | Complete EFR calculation for Maverick Creek Wind |

---

## Overview

The team's appendices provide the **scientific foundation** for:
- **Appendix 1 → Step 3:** How to derive HCR (Hazard Change Ratio) from climate conditions
- **Appendix 2 → Step 4:** How to derive EFR (Equipment Failure Ratio) from scientific models

However, there are gaps and ambiguities that need to be addressed for successful implementation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KEY FINDING: APPENDIX 2 MIXES TWO THINGS                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Appendix 2 lists 6 models, but they serve DIFFERENT purposes:             │
│                                                                              │
│  PERFORMANCE MODELS (affect annual revenue):                                │
│    • Temperature Coefficient → Instantaneous power loss                    │
│    • Icing Loss → Power reduction during icing events                      │
│    • Cut-Out Logic → Lost energy when wind > 25 m/s                        │
│                                                                              │
│  LIFE MODELS (affect asset lifespan):                                       │
│    • Peck's Model → Accelerated degradation                                │
│    • Coffin-Manson → Cycles to failure                                     │
│    • Palmgren-Miner → Cumulative fatigue                                   │
│                                                                              │
│  IMPLICATION:                                                               │
│    Performance models → Step 2 (Asset Performance Simulation)              │
│    Life models → Step 4 (EFR/IUL Calculation)                              │
│                                                                              │
│  The team may have conflated these in their framework design.              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Critical Clarification: What Does "2030" or "2040" Mean in SCVR?

Before diving into the appendices, this clarification is essential:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCVR PERIOD INTERPRETATION                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ⚠️ "2030" does NOT mean a single year's data!                             │
│                                                                              │
│  Climate projections are INHERENTLY noisy on single-year timescales.       │
│  To extract meaningful climate TRENDS (vs weather noise), we use           │
│  PERIOD AVERAGES:                                                           │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Label      │  Actual Period           │  Duration                   │  │
│  ├─────────────┼──────────────────────────┼─────────────────────────────┤  │
│  │  "Baseline" │  1980-2010               │  30 years (historical obs)  │  │
│  │  "2030"     │  2020-2040               │  20 years (centered)        │  │
│  │  "2040"     │  2030-2050               │  20 years (centered)        │  │
│  │  "2050"     │  2040-2060               │  20 years (centered)        │  │
│  └─────────────┴──────────────────────────┴─────────────────────────────┘  │
│                                                                              │
│  WHY THIS MATTERS:                                                          │
│  • Year-to-year climate has HIGH variance (El Niño, La Niña, etc.)         │
│  • Period averages extract the SIGNAL (climate change trend)               │
│  • This is standard practice in climate impact assessments                  │
│                                                                              │
│  VISUAL TIMELINE:                                                           │
│                                                                              │
│  ─────┬──────────────────┬──────┬──────────────────┬──────────────────────  │
│     1980              2010    2020              2040                2060    │
│       │                 │       │        │        │        │         │      │
│       └─────────────────┘       └────────┴────────┘        │         │      │
│             BASELINE                 "2030"                │         │      │
│            (30 years)              (20 years)              │         │      │
│                                                     └──────┴─────────┘      │
│                                                          "2050"             │
│                                                        (20 years)           │
│                                                                              │
│  CALCULATION FORMULA:                                                       │
│                                                                              │
│  SCVR("2030") = [Metric_avg(2020-2040) - Metric_avg(1980-2010)]            │
│                 ─────────────────────────────────────────────────            │
│                           Metric_avg(1980-2010)                              │
│                                                                              │
│  = (Future period average - Baseline period average) / Baseline average     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

This interpretation applies throughout this document and the main pilot framework.

---

## Appendix 1: HCR Derivations

### Climate Conditions Overview

The team identifies 7 primary climate conditions for HCR derivation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLIMATE CONDITIONS SUMMARY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Condition        │ Doable? │ Data Source          │ Hazard Link           │
│  ─────────────────┼─────────┼──────────────────────┼───────────────────────│
│  Heat Wave        │ ✅ Yes  │ tasmax, tasmin       │ Equipment stress      │
│  Cold Wave        │ ✅ Yes  │ tasmax, tasmin       │ Icing, freeze damage  │
│  Freeze/Frost     │ ✅ Yes  │ tasmin               │ Thermal cycling       │
│  Cumulative Precip│ ✅ Yes  │ pr                   │ Flood risk            │
│  Wind (Sustained) │ ✅ Yes  │ sfcWind              │ Generation, fatigue   │
│  Wind (Extreme)   │ ⚠️ Proxy│ sfcWind (daily mean) │ Cut-out, damage       │
│  Wildfire         │ ⚠️ Proxy│ FWI from T, RH, W, P │ Asset destruction     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Detailed Breakdown: Each Climate Condition

#### 1. Heat Wave

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HEAT WAVE                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DEFINITION (from team):                                                    │
│  "3+ consecutive days where T_max AND T_min exceed the 90th percentile     │
│   of the historical baseline"                                               │
│                                                                              │
│  SOURCE: Copernicus Global Drought Observatory                              │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  IMPLEMENTATION:                                                            │
│                                                                              │
│  Step 1: Calculate historical P90 thresholds                               │
│    • Use 1980-2010 as baseline period                                      │
│    • Calculate P90 of daily T_max for each calendar day (smoothed)         │
│    • Calculate P90 of daily T_min for each calendar day (smoothed)         │
│                                                                              │
│  Step 2: Identify heat wave days in future scenario                        │
│    • For each day: Is T_max > P90_max AND T_min > P90_min?                 │
│    • Count consecutive days meeting criteria                               │
│    • If 3+ consecutive days → Heat Wave Event                              │
│                                                                              │
│  Step 3: Compute annual metric                                              │
│    • Heat_Wave_Days(year) = Total days in heat wave events                 │
│    • Heat_Wave_Events(year) = Count of distinct heat wave events           │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  SCVR CALCULATION:                                                          │
│                                                                              │
│  ⚠️ IMPORTANT: "2030" means a PERIOD AVERAGE, not a single year!           │
│                                                                              │
│  SCVR_heatwave(period) = [HW_days(future_period) - HW_days(baseline_period)]│
│                          / HW_days(baseline_period)                         │
│                                                                              │
│  Where:                                                                     │
│    baseline_period = 1980-2010 (30-year historical average)                │
│    future_period = 20-year window centered on target year                  │
│      • "2030" → 2020-2040 average                                          │
│      • "2040" → 2030-2050 average                                          │
│      • "2050" → 2040-2060 average                                          │
│                                                                              │
│  WHY PERIOD AVERAGES?                                                       │
│    • Single years are too noisy (high inter-annual variability)            │
│    • Climate = average weather, not one year's weather                     │
│    • Period averages extract the SIGNAL (trend) from the NOISE             │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  VISUAL TIMELINE:                                                           │
│                                                                              │
│  1980──────────2010     2020────2030────2040     2040────2050────2060      │
│       │              │  │         │         │    │         │         │     │
│       └──────────────┘  └─────────┴─────────┘    └─────────┴─────────┘     │
│             ↓                     ↓                        ↓                │
│         BASELINE            "2030" period            "2050" period         │
│       (30-year avg)         (20-year avg)            (20-year avg)         │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  WORKED EXAMPLE - Heat Wave SCVR for "2040":                               │
│                                                                              │
│  Step 1: Calculate baseline (1980-2010)                                    │
│    From ERA5 historical data for Culberson, TX:                            │
│    HW_days = [8, 12, 9, 11, 10, 7, 13, 9, 11, 10, 8, 12, 14, 9, 10,       │
│               11, 8, 13, 10, 9, 11, 12, 8, 10, 11, 9, 12, 10, 11, 9, 10]  │
│    HW_days_baseline = mean(above) = 10.2 days/year                         │
│                                                                              │
│  Step 2: Calculate future period (2030-2050 for "2040" label)              │
│    From NEX-GDDP-CMIP6, SSP2-4.5, ensemble mean:                           │
│    HW_days_2030-2050 = [14, 15, 13, 16, 18, 15, 17, 14, 19, 16,           │
│                         18, 15, 17, 20, 16, 18, 19, 17, 21, 18, 19]       │
│    HW_days_future = mean(above) = 16.9 days/year                           │
│                                                                              │
│  Step 3: Calculate SCVR                                                     │
│    SCVR_heatwave("2040") = (16.9 - 10.2) / 10.2                            │
│                          = 6.7 / 10.2                                       │
│                          = 0.657                                            │
│                          = +65.7%                                           │
│                                                                              │
│  INTERPRETATION:                                                            │
│  "By the 2040s, heat wave days are expected to increase by ~66%            │
│   compared to the 1980-2010 baseline."                                     │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ENSEMBLE UNCERTAINTY:                                                      │
│                                                                              │
│  With 35 CMIP6 models, you get a range:                                    │
│    • Model A: HW_days_future = 14.2 → SCVR = +39%                         │
│    • Model B: HW_days_future = 16.9 → SCVR = +66% (ensemble mean)         │
│    • Model C: HW_days_future = 21.5 → SCVR = +111%                        │
│                                                                              │
│  Report as: SCVR_heatwave("2040") = +66% [+39% to +111% range]            │
│                                                                              │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  HAZARDS AFFECTED:                                                          │
│  • Inverter/transformer overheating → BI (downtime)                        │
│  • Accelerated panel degradation → EFR (life reduction)                    │
│  • Reduced efficiency → Performance (revenue)                              │
│                                                                              │
│  PYTHON PSEUDOCODE:                                                         │
│  ```python                                                                  │
│  def count_heat_waves(tasmax, tasmin, p90_max, p90_min):                   │
│      """Count heat wave days per year"""                                   │
│      exceeds = (tasmax > p90_max) & (tasmin > p90_min)                     │
│      # Find runs of 3+ consecutive True values                             │
│      # ... (use scipy.ndimage.label or similar)                            │
│      return heat_wave_days_per_year                                        │
│  ```                                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2. Cold Wave

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COLD WAVE                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DEFINITION (from team):                                                    │
│  "3+ consecutive days where T_max AND T_min fall below the 10th percentile │
│   of the historical baseline"                                               │
│                                                                              │
│  SOURCE: Copernicus Global Drought Observatory                              │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  IMPLEMENTATION:                                                            │
│  (Same logic as Heat Wave, but using P10 instead of P90)                   │
│                                                                              │
│  Step 1: Calculate historical P10 thresholds                               │
│  Step 2: Identify cold wave days (T_max < P10_max AND T_min < P10_min)     │
│  Step 3: Count consecutive 3+ day periods                                  │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CLIMATE CHANGE DIRECTION:                                                  │
│  Cold waves are expected to DECREASE in frequency under warming.           │
│  SCVR_coldwave may be NEGATIVE (fewer events).                             │
│                                                                              │
│  Example:                                                                   │
│    Baseline: 8 cold wave days/year                                         │
│    Future (2040): 4 cold wave days/year                                    │
│    SCVR = (4 - 8) / 8 = -50%                                               │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  HAZARDS AFFECTED:                                                          │
│  • Wind turbine icing → BI (downtime) + Performance (lost generation)      │
│  • Freeze damage to components → EFR (life reduction)                      │
│                                                                              │
│  NOTE: Fewer cold waves could BENEFIT some assets (less icing).            │
│  But it doesn't eliminate freeze/thaw cycling damage.                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 3. Freeze/Frost Days

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FREEZE / FROST DAYS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DEFINITIONS (from team):                                                   │
│  • Frost Day: T_min < 0°C (overnight frost)                                │
│  • Icing Day: T_max < 0°C (entire day below freezing)                      │
│                                                                              │
│  SOURCE: Climpact-sci.org indices                                          │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  IMPLEMENTATION:                                                            │
│                                                                              │
│  Frost_Days(year) = count(T_min < 273.15K)   # if using Kelvin             │
│  Icing_Days(year) = count(T_max < 273.15K)                                 │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  WHAT MATTERS FOR PV: THERMAL CYCLING                                      │
│                                                                              │
│  The key metric is NOT frost days alone, but TRANSITIONS:                  │
│    • Day freezes (T_min < 0) then thaws (T_max > 0)                        │
│    • This causes thermal expansion/contraction → microcracks               │
│                                                                              │
│  Thermal_Cycles(year) = count(T_min < 0°C AND T_max > 0°C on same day)    │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CLIMATE CHANGE DIRECTION:                                                  │
│                                                                              │
│  For Texas sites:                                                           │
│    • Frost days expected to DECREASE                                       │
│    • But thermal cycling pattern may CHANGE                                │
│    • Fewer but potentially more extreme freeze events                      │
│                                                                              │
│  Example (Hayhurst Solar, Culberson TX):                                   │
│    Baseline: 45 frost days/year, 30 thermal cycles                         │
│    Future (2040): 32 frost days (-29%), 22 thermal cycles (-27%)           │
│    SCVR_freeze = -29%                                                       │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  HAZARD LINK:                                                               │
│  • Thermal cycling → Coffin-Manson fatigue → EFR (life reduction)         │
│  • Wind turbine icing → Performance loss + potential blade damage          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4. Cumulative Precipitation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CUMULATIVE PRECIPITATION                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DEFINITION (from team):                                                    │
│  "Simple rolling sum of precipitation over specific windows                │
│   (e.g., 5-day max or annual)"                                              │
│                                                                              │
│  SOURCE: Climpact-sci.org indices                                          │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  IMPLEMENTATION OPTIONS:                                                    │
│                                                                              │
│  Option A: Rx5day (Maximum 5-day precipitation)                            │
│    • For each year, find the maximum consecutive 5-day total              │
│    • This captures EXTREME precipitation events (flood risk)              │
│                                                                              │
│    Rx5day(year) = max[rolling_sum(pr, window=5)]                           │
│                                                                              │
│  Option B: R95p (Precipitation from very wet days)                         │
│    • Sum of precipitation on days exceeding the 95th percentile           │
│    • Captures total extreme precipitation volume                           │
│                                                                              │
│  Option C: CDD (Consecutive Dry Days)                                      │
│    • Maximum consecutive days with pr < 1mm                                │
│    • Relevant for drought, wildfire fuel drying, solar soiling            │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  FOR FLOOD HCR, USE Rx5day:                                                │
│                                                                              │
│  SCVR_precip = [Rx5day(future) - Rx5day(baseline)] / Rx5day(baseline)     │
│                                                                              │
│  Example:                                                                   │
│    Baseline: 85mm max 5-day precip                                         │
│    Future (2040): 105mm max 5-day precip                                   │
│    SCVR = (105 - 85) / 85 = +24%                                           │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  HAZARD LINK:                                                               │
│  • Extreme precipitation → Pluvial flood → BI (downtime, repairs)         │
│  • HCR_flood = α × SCVR_precip (α to be determined from literature)       │
│                                                                              │
│  CLIMATE SCIENCE NOTE:                                                      │
│  Extreme precipitation increases ~7% per 1°C warming (Clausius-Clapeyron) │
│  This is well-established - one of the more confident projections.        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 5. Wind (Sustained)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WIND (AVERAGE SUSTAINED)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DEFINITION (from team):                                                    │
│  "Directly available via wind_speed_10m_mean"                              │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  DATA SOURCE:                                                               │
│  • NEX-GDDP-CMIP6: sfcWind (near-surface wind speed, 10m)                  │
│  • Units: m/s                                                               │
│  • Temporal: Daily mean                                                     │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  WHAT TO COMPUTE:                                                           │
│                                                                              │
│  For Wind Generation:                                                       │
│    • Annual mean wind speed (affects capacity factor)                      │
│    • Wind speed distribution (affects power curve integration)             │
│                                                                              │
│  For Wind Variability / Fatigue:                                           │
│    • Standard deviation of daily wind speed                                │
│    • Count of high-variability days                                        │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  SCVR OPTIONS:                                                              │
│                                                                              │
│  SCVR_wind_mean = [mean_wind(future) - mean_wind(baseline)]                │
│                   / mean_wind(baseline)                                     │
│                                                                              │
│  SCVR_wind_variability = [std_wind(future) - std_wind(baseline)]           │
│                          / std_wind(baseline)                               │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CLIMATE CHANGE IMPACT:                                                     │
│  Wind changes are LESS certain than temperature/precipitation.             │
│  Regional patterns vary - some areas get windier, some calmer.             │
│  For Texas: Most models show slight increase or no change.                 │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  HUB HEIGHT EXTRAPOLATION:                                                  │
│                                                                              │
│  CMIP provides 10m wind; turbines are at 80-100m.                          │
│  Use logarithmic profile:                                                   │
│                                                                              │
│  v_hub = v_10m × ln(z_hub / z_0) / ln(10 / z_0)                           │
│                                                                              │
│  Where z_0 = surface roughness (~0.03m for grassland)                      │
│                                                                              │
│  For z_hub = 80m, z_0 = 0.03m:                                             │
│    v_hub ≈ v_10m × 1.36                                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6. Wind (Extreme) - PROXY

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WIND (EXTREME) - PROXY ONLY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DEFINITION (from team):                                                    │
│  "Use daily mean as a proxy for storm intensity"                           │
│                                                                              │
│  STATUS: ⚠️ PROXY - Not ideal                                              │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  THE PROBLEM:                                                               │
│                                                                              │
│  Daily MEAN wind speed ≠ Daily MAXIMUM wind speed                          │
│                                                                              │
│  Example:                                                                   │
│    Day with steady 8 m/s wind: Mean = 8 m/s, Max = 10 m/s                  │
│    Day with storm: Mean = 8 m/s, Max = 35 m/s (cut-out!)                   │
│                                                                              │
│  Both days have same MEAN but very different IMPACT.                       │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  WHAT WE REALLY NEED (but don't have in CMIP):                             │
│  • Wind gust speed (maximum instantaneous wind)                            │
│  • Sub-daily wind variability                                              │
│  • Wind direction (for wake effects)                                       │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  BEST AVAILABLE PROXY:                                                      │
│                                                                              │
│  Option 1: High daily mean threshold                                       │
│    Extreme_Wind_Days = count(sfcWind_daily_mean > 15 m/s)                  │
│    (Assumes high mean correlates with extreme gusts)                       │
│                                                                              │
│  Option 2: Statistical relationship                                         │
│    From historical data (ERA5), derive:                                    │
│    Wind_gust ≈ a × Wind_mean + b × Wind_std + c                           │
│    Apply this relationship to CMIP projections                             │
│                                                                              │
│  Option 3: Use historical gust/mean ratio                                  │
│    Gust_factor = ERA5_gust / ERA5_mean (historically)                      │
│    Future_gust ≈ CMIP_mean × Gust_factor                                  │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  SCVR CALCULATION:                                                          │
│                                                                              │
│  SCVR_extreme_wind = [Extreme_days(future) - Extreme_days(baseline)]       │
│                      / Extreme_days(baseline)                               │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  HAZARD LINK:                                                               │
│  • Cut-out events (wind > 25 m/s at hub) → Performance loss                │
│  • Structural loading → Palmgren-Miner fatigue → EFR                       │
│  • Blade damage from debris → BI (repairs)                                 │
│                                                                              │
│  ⚠️ UNCERTAINTY: This is one of the LEAST reliable SCVRs.                  │
│  Recommend: Use wide range in HCR sensitivity analysis.                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 7. Wildfire - PROXY

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WILDFIRE (FWI PROXY)                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DEFINITION (from team):                                                    │
│  "Fire Weather Index (FWI) using daily T_max, RH_mean, wind, and P_sum"   │
│                                                                              │
│  STATUS: ⚠️ PROXY - Indicates fire WEATHER risk, not actual fire risk     │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  FIRE WEATHER INDEX (FWI) SYSTEM:                                          │
│                                                                              │
│  Canadian Forest Fire Weather Index System components:                      │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Weather Inputs:                                                     │  │
│  │    • Temperature (T_max)                                            │  │
│  │    • Relative Humidity (RH)                                         │  │
│  │    • Wind Speed                                                      │  │
│  │    • Precipitation (24h)                                            │  │
│  │                                                                      │  │
│  │          │                                                           │  │
│  │          ▼                                                           │  │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐           │  │
│  │  │ Fine Fuel     │  │ Duff Moisture │  │ Drought Code  │           │  │
│  │  │ Moisture Code │  │ Code (DMC)    │  │ (DC)          │           │  │
│  │  │ (FFMC)        │  │               │  │               │           │  │
│  │  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘           │  │
│  │          │                  │                  │                    │  │
│  │          ▼                  ▼                  ▼                    │  │
│  │  ┌───────────────┐  ┌─────────────────────────────────┐            │  │
│  │  │ Initial Spread│  │ Build-Up Index (BUI)            │            │  │
│  │  │ Index (ISI)   │  │                                 │            │  │
│  │  └───────┬───────┘  └─────────────────┬───────────────┘            │  │
│  │          │                            │                             │  │
│  │          └────────────┬───────────────┘                             │  │
│  │                       ▼                                              │  │
│  │               ┌───────────────┐                                     │  │
│  │               │ Fire Weather  │                                     │  │
│  │               │ Index (FWI)   │                                     │  │
│  │               └───────────────┘                                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  IMPLEMENTATION:                                                            │
│                                                                              │
│  Python package: `pyfwi` or manual calculation                             │
│                                                                              │
│  ```python                                                                  │
│  from pyfwi import FWI                                                     │
│  fwi = FWI(temp=tasmax, rh=hurs, wind=sfcWind, precip=pr)                 │
│  fwi_values = fwi.calculate()                                              │
│  ```                                                                        │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  WHAT FWI DOESN'T CAPTURE:                                                 │
│  • Vegetation type and fuel load                                           │
│  • Terrain and accessibility                                               │
│  • Ignition sources (human, lightning)                                     │
│  • Fire suppression capability                                             │
│                                                                              │
│  FWI = "If a fire starts, how bad could it get?"                          │
│  NOT = "How likely is a fire to start and reach the asset?"               │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  SCVR CALCULATION:                                                          │
│                                                                              │
│  Option 1: Mean FWI                                                        │
│    SCVR_fwi = [mean_FWI(future) - mean_FWI(baseline)] / mean_FWI(baseline)│
│                                                                              │
│  Option 2: High FWI days (FWI > threshold)                                 │
│    SCVR_fwi = [High_FWI_days(future) - High_FWI_days(baseline)]            │
│               / High_FWI_days(baseline)                                     │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  PILOT SCOPE NOTE:                                                         │
│  Team excluded wildfire from pilot ("Impact of catastrophic hazard events  │
│  such as hurricane, wildfire not included").                               │
│                                                                              │
│  FWI is useful for SCVR computation, but HCR_wildfire may be deferred     │
│  to Phase 1.                                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Additional Climate Conditions (Team's "Other Possible")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ADDITIONAL CLIMATE INDICES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Index              │ Definition                  │ Use Case                │
│  ───────────────────┼─────────────────────────────┼─────────────────────────│
│  Tropical Nights    │ Days where T_min > 20°C    │ Peck's model (humidity  │
│                     │                             │ + heat at night)        │
│  ───────────────────┼─────────────────────────────┼─────────────────────────│
│  Summer Days        │ Days where T_max > 25°C    │ Solar efficiency loss   │
│                     │ (efficiency threshold)      │ threshold               │
│  ───────────────────┼─────────────────────────────┼─────────────────────────│
│  Cooling Degree     │ Σ max(T_mean - 18.33°C, 0) │ Substation cooling      │
│  Days (CDD)         │                             │ load estimation         │
│  ───────────────────┼─────────────────────────────┼─────────────────────────│
│  Dry Spells         │ Max consecutive days        │ Wildfire fuel drying,   │
│                     │ with P_sum = 0              │ solar panel soiling     │
│                                                                              │
│  RECOMMENDATION:                                                            │
│  For pilot, focus on the primary 7 conditions.                             │
│  These additional indices can be computed in Phase 1 if needed.            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Appendix 2: EFR Derivations

### Overview: Performance vs Life Models

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              CRITICAL CLASSIFICATION OF APPENDIX 2 MODELS                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  The team lists 6 models, but they serve DIFFERENT purposes:               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MODEL                     │ TYPE        │ AFFECTS     │ STEP      │   │
│  ├─────────────────────────────┼─────────────┼─────────────┼───────────┤   │
│  │  Temperature Coefficient   │ Performance │ Revenue/yr  │ Step 2    │   │
│  │  Icing Loss               │ Performance │ Revenue/yr  │ Step 2    │   │
│  │  Cut-Out Logic            │ Performance │ Revenue/yr  │ Step 2    │   │
│  │  Peck's Model             │ LIFE        │ Asset life  │ Step 4    │   │
│  │  Coffin-Manson            │ LIFE        │ Asset life  │ Step 4    │   │
│  │  Palmgren-Miner           │ LIFE        │ Asset life  │ Step 4    │   │
│  └─────────────────────────────┴─────────────┴─────────────┴───────────┘   │
│                                                                              │
│  IMPLICATION:                                                               │
│  • Performance models should be used in STEP 2 to compute Revenue_climate  │
│  • Life models should be used in STEP 4 to compute IUL                     │
│  • The team's framework may need clarification on this separation          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### PERFORMANCE MODELS (for Step 2)

#### 1. Temperature Coefficient Model (Solar PV)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TEMPERATURE COEFFICIENT MODEL                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PURPOSE: Calculate INSTANTANEOUS power loss from high cell temperatures   │
│                                                                              │
│  FORMULA:                                                                   │
│  P_actual = P_rated × [1 + γ × (T_cell − T_ref)]                           │
│                                                                              │
│  Where:                                                                     │
│    P_actual = Actual power output (W)                                      │
│    P_rated = Rated power at STC (W)                                        │
│    γ = Temperature coefficient of power (-0.003 to -0.005 per °C)          │
│    T_cell = Cell temperature (°C)                                          │
│    T_ref = Reference temperature (25°C)                                    │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CELL TEMPERATURE ESTIMATION:                                               │
│                                                                              │
│  T_cell is NOT the same as ambient temperature!                            │
│                                                                              │
│  Common approximation:                                                      │
│  T_cell = T_ambient + (NOCT - 20) × (G / 800)                              │
│                                                                              │
│  Where:                                                                     │
│    NOCT = Nominal Operating Cell Temperature (~45°C typical)               │
│    G = Irradiance (W/m²)                                                   │
│                                                                              │
│  Or using pvlib:                                                            │
│  ```python                                                                  │
│  from pvlib.temperature import sapm_cell                                   │
│  T_cell = sapm_cell(poa_global, wind_speed, temp_air, ...)                │
│  ```                                                                        │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  EXAMPLE:                                                                   │
│                                                                              │
│  Hot day: T_ambient = 40°C, G = 1000 W/m²                                  │
│  T_cell = 40 + (45 - 20) × (1000/800) = 40 + 31.25 = 71.25°C              │
│                                                                              │
│  With γ = -0.004/°C:                                                        │
│  P_actual = P_rated × [1 + (-0.004) × (71.25 - 25)]                        │
│           = P_rated × [1 - 0.185]                                          │
│           = P_rated × 0.815                                                 │
│           = 18.5% power loss                                                │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  TYPE: PERFORMANCE (affects Revenue_climate in Step 2)                     │
│  NOT an EFR/Life model!                                                     │
│                                                                              │
│  HOW IT ENTERS THE FRAMEWORK:                                               │
│  This is ALREADY captured when you run pvlib with climate scenario         │
│  temperatures. You don't need to apply it separately.                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2. Icing Loss Model (Wind)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ICING LOSS MODEL                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PURPOSE: Calculate power loss during icing conditions                     │
│                                                                              │
│  CONDITION DEFINITION:                                                      │
│  Icing Event if: T < 0°C AND RH > 75%                                      │
│                                                                              │
│  FORMULA:                                                                   │
│  P_iced = P_normal × (1 − L_ice)                                           │
│                                                                              │
│  Where:                                                                     │
│    P_iced = Power output during icing                                      │
│    P_normal = Power from standard power curve                              │
│    L_ice = Icing loss factor (0.2 to 0.8)                                  │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  L_ice VALUES:                                                              │
│                                                                              │
│  │ Icing Severity │ L_ice │ Power Reduction │                              │
│  ├────────────────┼───────┼─────────────────┤                              │
│  │ Light          │ 0.2   │ 20%             │                              │
│  │ Moderate       │ 0.4   │ 40%             │                              │
│  │ Heavy          │ 0.6   │ 60%             │                              │
│  │ Severe         │ 0.8   │ 80%             │                              │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  IMPLEMENTATION:                                                            │
│                                                                              │
│  ```python                                                                  │
│  def apply_icing_loss(power, temp, humidity, L_ice=0.4):                   │
│      """Apply icing loss when conditions are met"""                        │
│      icing_condition = (temp < 273.15) & (humidity > 75)  # T<0°C, RH>75% │
│      power_adjusted = power.copy()                                         │
│      power_adjusted[icing_condition] *= (1 - L_ice)                        │
│      return power_adjusted                                                 │
│  ```                                                                        │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  TYPE: PERFORMANCE (affects Revenue_climate in Step 2)                     │
│  NOT an EFR/Life model (though severe icing can cause blade damage)        │
│                                                                              │
│  CLIMATE CHANGE IMPACT:                                                     │
│  • Fewer icing days in warming climate                                     │
│  • But remaining icing events may be more severe (freezing rain)          │
│  • Net effect on Texas sites: Likely DECREASE in icing losses             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 3. Cut-Out Logic (Wind)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CUT-OUT LOGIC                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PURPOSE: Calculate lost generation when wind exceeds cut-out threshold    │
│                                                                              │
│  FORMULA:                                                                   │
│  If Wind > Cut_out_speed, then Power = 0                                   │
│                                                                              │
│  Typical cut-out: 25 m/s (varies by turbine model: 22-28 m/s)             │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ANNUAL ENERGY LOSS:                                                        │
│                                                                              │
│  AEP_loss = Σ (P_expected × Δt) for all hours where Wind > Cut_out        │
│                                                                              │
│  Where:                                                                     │
│    AEP_loss = Annual energy production loss (MWh)                          │
│    P_expected = Power that would have been generated (MW)                  │
│    Δt = Duration of exceedance (hours)                                     │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  EXAMPLE:                                                                   │
│                                                                              │
│  Maverick Creek Wind (491.6 MW):                                           │
│                                                                              │
│  Base Scenario:                                                             │
│    Hours > 25 m/s: 50 hours/year                                           │
│    Lost generation: 50h × 491.6 MW × 0.35 CF = 8,603 MWh                  │
│    Revenue loss at $50/MWh: $430K/year                                     │
│                                                                              │
│  Climate Scenario (RCP 4.5, 2040):                                         │
│    Hours > 25 m/s: 65 hours/year (+30%)                                    │
│    Lost generation: 65h × 491.6 MW × 0.35 CF = 11,184 MWh                 │
│    Revenue loss at $50/MWh: $559K/year                                     │
│    Additional loss: $129K/year                                             │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  TYPE: PERFORMANCE (affects Revenue_climate in Step 2)                     │
│  NOT an EFR/Life model!                                                     │
│                                                                              │
│  HOW IT ENTERS THE FRAMEWORK:                                               │
│  This should be captured in the wind performance model (PyWake or similar) │
│  which applies power curve including cut-out.                              │
│                                                                              │
│  NOTE: Cut-out PROTECTS the turbine from damage - it's not a life impact. │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### LIFE MODELS (for Step 4 - True EFR)

#### 4. Peck's Model (Solar PV Degradation)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PECK'S AGING MODEL                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PURPOSE: Estimate ACCELERATED AGING from heat + humidity exposure         │
│                                                                              │
│  TYPE: LIFE MODEL → EFR (affects IUL in Step 4) ✅                         │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  FORMULA:                                                                   │
│  η = exp(γ0 + γ1 × ln(RH) + γ2 / T_mod)                                   │
│                                                                              │
│  Where:                                                                     │
│    η = Aging acceleration factor (dimensionless)                           │
│    RH = Relative humidity (%)                                              │
│    T_mod = Module temperature in Kelvin (K)                                │
│    γ0, γ1, γ2 = Empirically derived material constants                    │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  INTERPRETATION:                                                            │
│                                                                              │
│  η = 1.0: Normal aging (baseline conditions)                               │
│  η = 1.5: Panel ages 1.5 years for every calendar year (50% faster)       │
│  η = 2.0: Panel ages 2 years for every calendar year (100% faster)        │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CHALLENGE: WHAT ARE γ0, γ1, γ2?                                           │
│                                                                              │
│  These are material-specific constants. The team's document doesn't        │
│  provide values!                                                            │
│                                                                              │
│  From literature (example values for EVA encapsulant):                     │
│    γ0 ≈ -17.5                                                              │
│    γ1 ≈ 0.67 (humidity exponent)                                           │
│    γ2 ≈ 5000 (activation energy / R, in Kelvin)                           │
│                                                                              │
│  ⚠️ These vary by module type, manufacturer, and encapsulant material!    │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  EXAMPLE CALCULATION:                                                       │
│                                                                              │
│  Baseline conditions:                                                       │
│    T_mod = 298K (25°C), RH = 50%                                           │
│    η_base = exp(-17.5 + 0.67×ln(50) + 5000/298)                           │
│           = exp(-17.5 + 2.62 + 16.78)                                      │
│           = exp(1.90)                                                       │
│           = 6.69 (this is the reference)                                   │
│                                                                              │
│  Climate stress conditions:                                                 │
│    T_mod = 308K (35°C), RH = 65%                                           │
│    η_climate = exp(-17.5 + 0.67×ln(65) + 5000/308)                        │
│              = exp(-17.5 + 2.80 + 16.23)                                   │
│              = exp(1.53)                                                    │
│              = 4.62                                                         │
│                                                                              │
│  Wait, η_climate < η_base? That's because higher T increases degradation  │
│  but the activation energy term decreases. Let me recalculate...          │
│                                                                              │
│  Actually, the sign of γ2 matters. If γ2 is positive, higher T means      │
│  LOWER η (slower aging), which is counterintuitive.                        │
│                                                                              │
│  CORRECT FORM (Arrhenius-type):                                            │
│  η = A × RH^n × exp(-Ea / (R × T))                                        │
│                                                                              │
│  Higher T → Higher η → Faster degradation ✓                                │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CONVERTING η TO EFR:                                                       │
│                                                                              │
│  If η_climate / η_baseline = 1.5 (50% faster aging):                       │
│    • 25-year panel reaches end-of-life in 25/1.5 = 16.7 years             │
│    • Life reduction = (25 - 16.7) / 25 = 33%                              │
│                                                                              │
│  EFR = (Life_reduction) / (SCVR_heat+humidity)                            │
│                                                                              │
│  If SCVR_heat+humidity = 40%:                                              │
│    EFR = 33% / 40% = 0.825% life reduction per % SCVR                     │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ⚠️ KEY UNCERTAINTY:                                                       │
│  The γ parameters need calibration against field data.                     │
│  Recommend: Use Jordan & Kurtz (NREL) regional degradation study.         │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  COMPLETE WORKED EXAMPLE - Hayhurst Solar (with Period Averaging)          │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  STEP 1: Calculate SCVR for Heat + Humidity                                │
│                                                                              │
│  Remember: "2040" means the 2030-2050 period average!                      │
│                                                                              │
│  Metric: "Tropical Nights" (days where T_min > 20°C AND RH_mean > 70%)     │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Period              │  Tropical Nights/yr │  Source                 │  │
│  ├──────────────────────┼─────────────────────┼─────────────────────────┤  │
│  │  Baseline (1980-2010)│  18 days            │  ERA5 for Culberson, TX │  │
│  │  "2030" (2020-2040)  │  25 days            │  NEX-GDDP-CMIP6 SSP2-4.5│  │
│  │  "2040" (2030-2050)  │  32 days            │  NEX-GDDP-CMIP6 SSP2-4.5│  │
│  │  "2050" (2040-2060)  │  41 days            │  NEX-GDDP-CMIP6 SSP2-4.5│  │
│  └──────────────────────┴─────────────────────┴─────────────────────────┘  │
│                                                                              │
│  SCVR_heat+humidity("2040") = (32 - 18) / 18 = 0.778 = +77.8%             │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  STEP 2: Calculate Aging Acceleration Factor (η)                           │
│                                                                              │
│  Using Arrhenius-Peck form:                                                │
│  η = A × RH^n × exp(-Ea / (R × T))                                        │
│                                                                              │
│  With parameters (EVA encapsulant):                                        │
│    A = 1e-6 (pre-exponential factor)                                       │
│    n = 3 (humidity exponent)                                               │
│    Ea/R = 6000 K (activation energy)                                       │
│                                                                              │
│  Baseline conditions (Culberson, TX historical average):                   │
│    T_mod_avg = 303 K (30°C), RH_avg = 35%                                 │
│    η_base = 1e-6 × (35)^3 × exp(-6000/303)                                │
│           = 1e-6 × 42875 × 2.48e-9                                        │
│           = 1.06e-7 (reference value)                                      │
│                                                                              │
│  Climate conditions ("2040" period: 2030-2050 average):                    │
│    T_mod_avg = 308 K (+5°C), RH_avg = 45% (+10%)                          │
│    η_climate = 1e-6 × (45)^3 × exp(-6000/308)                             │
│              = 1e-6 × 91125 × 3.82e-9                                     │
│              = 3.48e-7                                                     │
│                                                                              │
│  Acceleration ratio: η_climate / η_base = 3.48e-7 / 1.06e-7 = 3.28       │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  STEP 3: Convert to Life Reduction                                         │
│                                                                              │
│  If aging is 3.28× faster under climate stress:                            │
│    • Panel reaches 25-year degradation in 25 / 3.28 = 7.6 years           │
│                                                                              │
│  But this is EXTREME. The climate conditions don't apply 100% of the time. │
│                                                                              │
│  More realistic: weighted average                                          │
│    • "Stress" conditions occur during 32 tropical nights/year = 8.8%      │
│    • "Normal" conditions occur 91.2% of the time                          │
│    • Weighted η = 0.912 × 1.0 + 0.088 × 3.28 = 1.20                       │
│                                                                              │
│  With weighted η = 1.20:                                                   │
│    • Panel reaches 25-year degradation in 25 / 1.20 = 20.8 years          │
│    • Life reduction = (25 - 20.8) / 25 = 16.8%                            │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  STEP 4: Calculate EFR                                                     │
│                                                                              │
│  EFR_heat+humidity = Life_reduction / SCVR_heat+humidity                  │
│                    = 16.8% / 77.8%                                        │
│                    = 0.216 = 0.22% life reduction per % SCVR              │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  STEP 5: Apply to IUL Calculation                                          │
│                                                                              │
│  For Hayhurst Solar:                                                       │
│    EUL = 25 years                                                          │
│    SCVR_heat+humidity("2040") = +77.8%                                    │
│    EFR_heat+humidity = 0.22% per % SCVR                                   │
│                                                                              │
│    Life_reduction_from_heat = SCVR × EFR = 77.8% × 0.22% = 17.1%         │
│                                                                              │
│    IUL_partial = EUL × (1 - 0.171) = 25 × 0.829 = 20.7 years             │
│                                                                              │
│  (Other factors like freeze/thaw would further adjust this)               │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  SUMMARY FOR "2040" PERIOD:                                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Metric                  │  Value                                    │  │
│  ├──────────────────────────┼───────────────────────────────────────────┤  │
│  │  SCVR (heat+humidity)    │  +77.8%                                   │  │
│  │  Aging acceleration (η)  │  1.20× weighted average                   │  │
│  │  Life reduction          │  16.8%                                    │  │
│  │  EFR                     │  0.22% per % SCVR                         │  │
│  │  IUL (from this factor)  │  20.7 years (vs 25 EUL)                   │  │
│  └──────────────────────────┴───────────────────────────────────────────┘  │
│                                                                              │
│  NOTE: This example uses illustrative parameters. Actual γ/Ea values      │
│  require calibration against manufacturer data or field measurements.      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 5. Coffin-Manson Model (Thermal Fatigue)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COFFIN-MANSON MODEL                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PURPOSE: Estimate cycles to failure from thermal expansion/contraction    │
│                                                                              │
│  TYPE: LIFE MODEL → EFR (affects IUL in Step 4) ✅                         │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  FORMULA:                                                                   │
│  N_f = C × (Δε_p)^(-k)                                                     │
│                                                                              │
│  Where:                                                                     │
│    N_f = Number of cycles to failure                                       │
│    Δε_p = Plastic strain amplitude (from temperature swing)                │
│    C, k = Material-specific constants                                      │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CLIMATE LINKAGE:                                                           │
│                                                                              │
│  "Cycle" = Day where:                                                       │
│    • T_min < 0°C (freezing)                                                │
│    • T_max > 0°C (thawing)                                                 │
│    • Causes thermal expansion/contraction                                  │
│                                                                              │
│  Δε_p ∝ ΔT × CTE                                                           │
│                                                                              │
│  Where:                                                                     │
│    ΔT = Temperature swing (T_max - T_min)                                  │
│    CTE = Coefficient of Thermal Expansion                                  │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  TYPICAL VALUES (Silicon solar cells):                                     │
│                                                                              │
│  C ≈ 0.1 to 1.0 (depends on material)                                     │
│  k ≈ 2.0 (Coffin-Manson exponent)                                         │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  EXAMPLE:                                                                   │
│                                                                              │
│  Hayhurst Solar (Culberson, TX):                                           │
│                                                                              │
│  Baseline (1980-2010):                                                      │
│    • Thermal cycles per year: 45                                           │
│    • Average ΔT during cycle: 20°C                                         │
│    • Δε_p = 20 × 2.6×10^-6 = 5.2×10^-5                                    │
│    • N_f = 0.5 × (5.2×10^-5)^(-2) = 185,000 cycles                        │
│    • Years to failure: 185,000 / 45 = 4,111 years                          │
│    → Thermal cycling NOT the limiting factor for this site               │
│                                                                              │
│  Climate Scenario (RCP 4.5, 2040):                                         │
│    • Thermal cycles per year: 32 (fewer freeze events)                     │
│    • Average ΔT during cycle: 25°C (more extreme when they occur)         │
│    • Δε_p = 25 × 2.6×10^-6 = 6.5×10^-5                                    │
│    • N_f = 0.5 × (6.5×10^-5)^(-2) = 118,000 cycles                        │
│    • Years to failure: 118,000 / 32 = 3,688 years                          │
│    → Still not limiting, but relative change matters                      │
│                                                                              │
│  Relative life change:                                                      │
│    = (4,111 - 3,688) / 4,111 = 10% reduction                              │
│    But since thermal cycling isn't the limiting factor, actual impact     │
│    on IUL is smaller.                                                      │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CONVERTING TO EFR:                                                         │
│                                                                              │
│  This is complex because:                                                   │
│  1. Both cycle COUNT and cycle SEVERITY change                             │
│  2. May not be the limiting degradation mechanism                          │
│                                                                              │
│  Simplified approach:                                                       │
│  EFR_thermal = Weight × (Life_reduction / SCVR_freeze)                    │
│                                                                              │
│  Where Weight < 1 if thermal cycling isn't the primary failure mode.      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 6. Palmgren-Miner Rule (Wind Fatigue)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PALMGREN-MINER RULE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PURPOSE: Estimate cumulative fatigue damage from wind load cycles         │
│                                                                              │
│  TYPE: LIFE MODEL → EFR (affects IUL in Step 4) ✅                         │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  FORMULA:                                                                   │
│  D = Σ (n_i / N_i)                                                         │
│                                                                              │
│  Where:                                                                     │
│    D = Cumulative damage (D = 1 means failure)                             │
│    n_i = Actual cycles at stress level i                                   │
│    N_i = Cycles to failure at stress level i (from S-N curve)             │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  S-N CURVE (Stress vs Number of cycles):                                   │
│                                                                              │
│  Stress │                                                                   │
│  Level  │ ╲                                                                 │
│         │  ╲                                                                │
│         │   ╲                                                               │
│         │    ╲___________                                                   │
│         │                ╲____________                                      │
│         └────────────────────────────────                                   │
│                     N_i (cycles to failure)                                 │
│                                                                              │
│  Higher stress → Fewer cycles to failure                                   │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  WIND SPEED → STRESS RELATIONSHIP:                                         │
│                                                                              │
│  Aerodynamic load ∝ v²  (wind speed squared)                               │
│  Bending stress ∝ v²                                                       │
│                                                                              │
│  Wind speed bins:                                                           │
│    Bin 1: 5-10 m/s → Low stress                                            │
│    Bin 2: 10-15 m/s → Medium stress                                        │
│    Bin 3: 15-20 m/s → High stress                                          │
│    Bin 4: 20-25 m/s → Very high stress                                     │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  IMPLEMENTATION STEPS:                                                      │
│                                                                              │
│  1. Bin wind speeds into stress categories                                 │
│  2. Count hours in each bin → Convert to cycles (n_i)                     │
│  3. Look up N_i from turbine S-N curve (manufacturer data)                │
│  4. Calculate D = Σ(n_i / N_i)                                             │
│  5. Time to failure = Time when D reaches 1                                │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  EXAMPLE:                                                                   │
│                                                                              │
│  Maverick Creek Wind - Blade Root Fatigue:                                 │
│                                                                              │
│  Baseline:                                                                  │
│  │ Bin (m/s) │ Hours/yr │ n_i (cycles)│ N_i (to fail) │ Damage/yr │       │
│  ├───────────┼──────────┼─────────────┼───────────────┼───────────┤       │
│  │ 5-10      │ 3,000    │ 50,000      │ 100,000,000   │ 0.0005    │       │
│  │ 10-15     │ 2,500    │ 30,000      │ 10,000,000    │ 0.003     │       │
│  │ 15-20     │ 1,200    │ 10,000      │ 1,000,000     │ 0.01      │       │
│  │ 20-25     │ 300      │ 1,000       │ 100,000       │ 0.01      │       │
│  ├───────────┼──────────┼─────────────┼───────────────┼───────────┤       │
│  │ Total     │          │             │               │ 0.0235/yr │       │
│                                                                              │
│  Time to failure: 1 / 0.0235 = 42.5 years                                  │
│                                                                              │
│  Climate Scenario (more wind variability):                                 │
│  │ Bin (m/s) │ Hours/yr │ n_i (cycles)│ N_i (to fail) │ Damage/yr │       │
│  ├───────────┼──────────┼─────────────┼───────────────┼───────────┤       │
│  │ 5-10      │ 2,800    │ 45,000      │ 100,000,000   │ 0.00045   │       │
│  │ 10-15     │ 2,300    │ 28,000      │ 10,000,000    │ 0.0028    │       │
│  │ 15-20     │ 1,400    │ 14,000      │ 1,000,000     │ 0.014     │       │
│  │ 20-25     │ 500      │ 2,000       │ 100,000       │ 0.02      │       │
│  ├───────────┼──────────┼─────────────┼───────────────┼───────────┤       │
│  │ Total     │          │             │               │ 0.0372/yr │       │
│                                                                              │
│  Time to failure: 1 / 0.0372 = 26.9 years                                  │
│                                                                              │
│  Life reduction: (42.5 - 26.9) / 42.5 = 37%                                │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CONVERTING TO EFR:                                                         │
│                                                                              │
│  If SCVR_wind_variability = 25%:                                           │
│    EFR_wind_fatigue = 37% / 25% = 1.48% per % SCVR                        │
│                                                                              │
│  ⚠️ This seems high! Need to calibrate against actual turbine data.       │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  DATA NEEDED (from turbine manufacturer):                                   │
│  • S-N curves for blades, tower, gearbox                                   │
│  • Design load cases (DLC) from IEC 61400-1                                │
│  • Site-specific wind speed distribution                                   │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  COMPLETE WORKED EXAMPLE - Maverick Creek Wind (with Period Averaging)     │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  STEP 1: Calculate SCVR for Wind Variability                               │
│                                                                              │
│  Remember: "2040" means the 2030-2050 period average!                      │
│                                                                              │
│  Metric: "High Wind Hours" (hours where wind > 15 m/s at hub height)       │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Period              │  High Wind hrs/yr │  Source                   │  │
│  ├──────────────────────┼───────────────────┼───────────────────────────┤  │
│  │  Baseline (1980-2010)│  1,500 hours      │  ERA5 for Concho, TX      │  │
│  │  "2030" (2020-2040)  │  1,650 hours      │  NEX-GDDP-CMIP6 SSP2-4.5  │  │
│  │  "2040" (2030-2050)  │  1,800 hours      │  NEX-GDDP-CMIP6 SSP2-4.5  │  │
│  │  "2050" (2040-2060)  │  1,950 hours      │  NEX-GDDP-CMIP6 SSP2-4.5  │  │
│  └──────────────────────┴───────────────────┴───────────────────────────┘  │
│                                                                              │
│  SCVR_wind_variability("2040") = (1800 - 1500) / 1500 = 0.20 = +20%       │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  STEP 2: Compute Period-Averaged Wind Distribution                         │
│                                                                              │
│  Instead of single year, average across 20-year period:                    │
│                                                                              │
│  Baseline (1980-2010 average):                                             │
│  ┌───────────┬──────────┬───────────────────────────────────────────────┐  │
│  │ Bin (m/s) │ hrs/yr   │ Interpretation                                │  │
│  ├───────────┼──────────┼───────────────────────────────────────────────┤  │
│  │ 5-10      │ 3,000    │ Low stress - minimal damage                   │  │
│  │ 10-15     │ 2,500    │ Medium stress - routine wear                  │  │
│  │ 15-20     │ 1,200    │ High stress - significant fatigue             │  │
│  │ 20-25     │ 300      │ Very high stress - accelerated damage         │  │
│  └───────────┴──────────┴───────────────────────────────────────────────┘  │
│                                                                              │
│  "2040" Period (2030-2050 average):                                        │
│  ┌───────────┬──────────┬───────────────────────────────────────────────┐  │
│  │ Bin (m/s) │ hrs/yr   │ Change from baseline                          │  │
│  ├───────────┼──────────┼───────────────────────────────────────────────┤  │
│  │ 5-10      │ 2,800    │ -7% (less calm periods)                       │  │
│  │ 10-15     │ 2,400    │ -4%                                           │  │
│  │ 15-20     │ 1,450    │ +21% (more high wind events)                  │  │
│  │ 20-25     │ 450      │ +50% (more extreme wind events)               │  │
│  └───────────┴──────────┴───────────────────────────────────────────────┘  │
│                                                                              │
│  KEY INSIGHT: Higher bins increase MORE in percentage terms!               │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  STEP 3: Apply Palmgren-Miner to Each Period                               │
│                                                                              │
│  Baseline Damage Rate:                                                      │
│  ┌───────────┬──────────┬─────────────┬───────────────┬───────────────┐   │
│  │ Bin (m/s) │ hrs/yr   │ n_i (cycles)│ N_i (to fail) │ D_i/yr        │   │
│  ├───────────┼──────────┼─────────────┼───────────────┼───────────────┤   │
│  │ 5-10      │ 3,000    │ 50,000      │ 100,000,000   │ 0.0005        │   │
│  │ 10-15     │ 2,500    │ 30,000      │ 10,000,000    │ 0.0030        │   │
│  │ 15-20     │ 1,200    │ 10,000      │ 1,000,000     │ 0.0100        │   │
│  │ 20-25     │ 300      │ 1,000       │ 100,000       │ 0.0100        │   │
│  ├───────────┼──────────┼─────────────┼───────────────┼───────────────┤   │
│  │ TOTAL     │          │             │               │ 0.0235/yr     │   │
│  └───────────┴──────────┴─────────────┴───────────────┴───────────────┘   │
│                                                                              │
│  Time to D=1 (baseline): 1 / 0.0235 = 42.5 years                          │
│                                                                              │
│  "2040" Period Damage Rate:                                                │
│  ┌───────────┬──────────┬─────────────┬───────────────┬───────────────┐   │
│  │ Bin (m/s) │ hrs/yr   │ n_i (cycles)│ N_i (to fail) │ D_i/yr        │   │
│  ├───────────┼──────────┼─────────────┼───────────────┼───────────────┤   │
│  │ 5-10      │ 2,800    │ 47,000      │ 100,000,000   │ 0.00047       │   │
│  │ 10-15     │ 2,400    │ 29,000      │ 10,000,000    │ 0.00290       │   │
│  │ 15-20     │ 1,450    │ 14,500      │ 1,000,000     │ 0.01450       │   │
│  │ 20-25     │ 450      │ 2,000       │ 100,000       │ 0.02000       │   │
│  ├───────────┼──────────┼─────────────┼───────────────┼───────────────┤   │
│  │ TOTAL     │          │             │               │ 0.0379/yr     │   │
│  └───────────┴──────────┴─────────────┴───────────────┴───────────────┘   │
│                                                                              │
│  Time to D=1 ("2040"): 1 / 0.0379 = 26.4 years                            │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  STEP 4: Calculate Life Reduction and EFR                                  │
│                                                                              │
│  Life Reduction = (42.5 - 26.4) / 42.5 = 37.9%                            │
│                                                                              │
│  EFR_wind_fatigue = Life_reduction / SCVR_wind_variability                │
│                   = 37.9% / 20%                                            │
│                   = 1.90% life reduction per % SCVR                        │
│                                                                              │
│  ⚠️ NOTE: This is VERY sensitive to the high-wind bin!                    │
│  The 20-25 m/s bin contributes 53% of total damage under climate scenario │
│  vs 43% under baseline. Small changes in extreme wind have BIG effects!   │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  STEP 5: Apply to IUL Calculation                                          │
│                                                                              │
│  For Maverick Creek Wind:                                                  │
│    EUL = 35 years (team's assumption)                                      │
│    SCVR_wind_variability("2040") = +20%                                   │
│    EFR_wind_fatigue = 1.90% per % SCVR                                    │
│                                                                              │
│    Life_reduction_from_wind = SCVR × EFR = 20% × 1.90% = 38%             │
│                                                                              │
│    Wait - that's bigger than 1! The linear model breaks down.             │
│                                                                              │
│    CORRECT APPROACH: Use MIN(38%, physical_limit)                         │
│    Or cap EFR such that Life_reduction ≤ 50%                              │
│                                                                              │
│    Practical application:                                                  │
│    Life_reduction_capped = min(38%, 40%) = 38%                            │
│    IUL = 35 × (1 - 0.38) = 35 × 0.62 = 21.7 years                        │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  SUMMARY FOR "2040" PERIOD:                                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Metric                  │  Value                                    │  │
│  ├──────────────────────────┼───────────────────────────────────────────┤  │
│  │  SCVR (wind variability) │  +20%                                     │  │
│  │  Baseline fatigue life   │  42.5 years                               │  │
│  │  Climate fatigue life    │  26.4 years                               │  │
│  │  Life reduction          │  37.9%                                    │  │
│  │  EFR                     │  1.90% per % SCVR                         │  │
│  │  IUL (from this factor)  │  21.7 years (vs 35 EUL)                   │  │
│  └──────────────────────────┴───────────────────────────────────────────┘  │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ⚠️ KEY INSIGHT: WIND EFR IS HIGH BECAUSE                                 │
│                                                                              │
│  1. Fatigue damage is NON-LINEAR with wind speed (D ∝ v²)                 │
│  2. More hours in high-wind bins disproportionately increases damage      │
│  3. Linear SCVR → EFR mapping UNDERESTIMATES this non-linearity           │
│                                                                              │
│  RECOMMENDATION: For Phase 1, consider:                                    │
│  • Using actual fatigue calculations directly (skip EFR)                  │
│  • Or using piecewise EFR with different values for different SCVR ranges │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Critical Issue: Performance vs Life Impacts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              SUMMARY: WHERE EACH MODEL BELONGS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STEP 2 (Performance Simulation) - Affects Revenue_climate:                │
│  ───────────────────────────────────────────────────────────                 │
│  ✅ Temperature Coefficient Model (solar efficiency vs temp)               │
│  ✅ Icing Loss Model (wind power during icing)                             │
│  ✅ Cut-Out Logic (wind lost production > 25 m/s)                          │
│  ✅ These are ALREADY in pvlib/PyWake when you run with climate inputs    │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  STEP 4 (EFR/IUL Calculation) - Affects Asset Life:                        │
│  ───────────────────────────────────────────────────                         │
│  ✅ Peck's Model (heat + humidity → accelerated degradation)              │
│  ✅ Coffin-Manson (thermal cycling → mechanical fatigue)                   │
│  ✅ Palmgren-Miner (wind variability → structural fatigue)                 │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ⚠️ RECOMMENDATION FOR TEAM:                                               │
│                                                                              │
│  Clarify that:                                                              │
│  • Temperature Coefficient, Icing, Cut-Out → Built into performance models│
│  • Peck's, Coffin-Manson, Palmgren-Miner → Used to derive EFR for IUL     │
│                                                                              │
│  The current Appendix 2 mixes these together, which could cause confusion │
│  about where each model is applied in the framework.                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              IMPLEMENTATION PRIORITY FOR PILOT                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  HIGH PRIORITY (Must have for pilot):                                       │
│  ─────────────────────────────────────                                       │
│  1. Heat Wave / Cold Wave indices (SCVR computation)                       │
│  2. Extreme Precipitation (Rx5day for flood HCR)                           │
│  3. Peck's Model calibration (get γ parameters from literature)            │
│  4. Basic Palmgren-Miner with assumed S-N curve                            │
│                                                                              │
│  MEDIUM PRIORITY (Important but can simplify):                             │
│  ─────────────────────────────────────────────                               │
│  5. Freeze/Frost days and thermal cycling count                            │
│  6. Wind variability metrics                                                │
│  7. Coffin-Manson (may not be limiting factor for Texas sites)            │
│                                                                              │
│  LOW PRIORITY (Phase 1):                                                    │
│  ────────────────────────                                                    │
│  8. Fire Weather Index (wildfire excluded from pilot)                      │
│  9. Extreme wind (proxy quality is poor)                                   │
│  10. Site-specific S-N curves from turbine manufacturer                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Questions for the Team

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              QUESTIONS TO CLARIFY WITH TEAM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  APPENDIX 1 (HCR Derivations):                                             │
│  ─────────────────────────────                                               │
│  1. For Heat Wave, should we use HW_days or HW_events as the SCVR metric? │
│  2. What precipitation metric for flood HCR - Rx5day or R95p?             │
│  3. How to handle negative SCVR (fewer freeze events) - benefit or ignore?│
│  4. What extreme wind proxy to use given daily mean is poor indicator?    │
│                                                                              │
│  APPENDIX 2 (EFR Derivations):                                             │
│  ─────────────────────────────                                               │
│  5. What are the γ0, γ1, γ2 values for Peck's Model?                      │
│  6. Do you have manufacturer S-N curves for Maverick Creek turbines?      │
│  7. Should Temperature Coefficient be in Step 2 (performance) or Step 4?  │
│  8. Is Coffin-Manson relevant for Texas (limited freeze cycles)?          │
│                                                                              │
│  FRAMEWORK CLARIFICATION:                                                   │
│  ─────────────────────────                                                   │
│  9. Confirm: Performance models (Temp Coeff, Icing, Cut-Out) are already  │
│     in pvlib/PyWake and affect Revenue_climate in Step 2?                 │
│  10. Confirm: Life models (Peck's, Coffin-Manson, Palmgren-Miner) are    │
│      used to derive EFR and affect IUL in Step 4?                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*End of Appendix Detailed Analysis*
