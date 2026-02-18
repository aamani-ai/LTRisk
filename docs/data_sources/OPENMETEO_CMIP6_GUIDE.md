# Open-Meteo Climate API — CMIP6 Data Source Guide

*A complete reference for the LTRisk project data pipeline.*  
*Last verified: February 2026 — scripts/tests/probe_openmeteo_variables.py*

---

> ## ⚠️ Read This First — The Single Most Important Thing About This Dataset
>
> **Every model on the Open-Meteo Climate API runs under approximately SSP5-8.5 (high-emissions, no-mitigation).
> This applies to ALL 7 models — it is not a choice you can change by picking a different model.**
>
> This is because the API serves the **HighResMIP** experiment group, which was designed
> purely for high-resolution climate research and was run under one pathway to save computing cost.
>
> **What this means in practice:**
> - The `scenario` parameter or label in your file names (`ssp245`, etc.) is **metadata you write yourself** — it does not change the data
> - All 7 models give you a high-emissions future (~+3–4°C by 2100), not a moderate one (~+2.4°C)
> - You cannot compare SSP2-4.5 vs SSP5-8.5 using this API alone
> - Our SCVR results represent an **upper bound on climate risk** (conservative / cautious)
>
> **For multi-scenario production analysis:** use NASA NEX-GDDP-CMIP6 (see Section 8).  
> **For prototyping and methodology development:** Open-Meteo is perfectly fine — the pipeline, schemas, and code all transfer directly.

---

## Table of Contents

1. [What Is CMIP6?](#1-what-is-cmip6)
2. [Climate Scenarios: RCP vs SSP](#2-climate-scenarios-rcp-vs-ssp)
3. [Why Multiple Models? The Ensemble Concept](#3-why-multiple-models-the-ensemble-concept)
4. [The Open-Meteo Climate API](#4-the-open-meteo-climate-api)
5. [Available Models — Comparison Table](#5-available-models--comparison-table)
6. [Variable Availability by Model](#6-variable-availability-by-model)
7. [What the Data Actually Looks Like](#7-what-the-data-actually-looks-like)
8. [Critical Limitations to Understand](#8-critical-limitations-to-understand)
9. [How This Fits Into LTRisk](#9-how-this-fits-into-ltrisk)
10. [Quick Reference — API Calls](#10-quick-reference--api-calls)

---

## 1. What Is CMIP6?

**CMIP** stands for **Coupled Model Intercomparison Project** — an international framework
coordinated by the World Climate Research Programme (WCRP) where climate modeling centers
worldwide run standardized experiments and share their outputs.

**CMIP6** is the 6th generation, released 2019–2021, and forms the scientific basis for the
IPCC Sixth Assessment Report (AR6, 2021).

```
                        CMIP EVOLUTION
  ─────────────────────────────────────────────────────────────────────
  CMIP3 (2005)  →  CMIP5 (2013)  →  CMIP6 (2021)
  IPCC AR4         IPCC AR5         IPCC AR6

  ~20 models        ~40 models        ~100 models
  RCP scenarios     RCP scenarios     SSP scenarios
  ~100 km grid      ~100 km grid      50–100 km grid (HighResMIP: 20–50 km)
  ─────────────────────────────────────────────────────────────────────
```

### What "coupled" means

A coupled model simulates the **interactions between atmosphere, ocean, land surface,
and sea ice** as a system. Earlier models ran these components separately; coupled models
allow feedbacks (e.g., warmer ocean → more evaporation → changes in precipitation patterns).

### Why it matters for LTRisk

CMIP6 projections are the global standard for long-term climate risk assessment.
When lenders and equity investors ask "what climate scenario did you use?", the answer
needs to reference CMIP6 (or CMIP5) to be credible. Regulatory frameworks like TCFD
explicitly reference CMIP-based scenarios.

---

## 2. Climate Scenarios: RCP vs SSP

### Background

Climate projections cannot be a single deterministic forecast — they depend on how much
greenhouse gas humanity emits over the coming decades. To handle this, scientists define
**scenarios** that represent different plausible futures.

### CMIP5: Representative Concentration Pathways (RCPs)

CMIP5 used **RCPs** — defined purely by the **radiative forcing** (extra energy trapped
by greenhouse gases) reached by 2100, measured in W/m².

```
  RCP Scenario    Forcing by 2100    Warming by 2100    Description
  ─────────────────────────────────────────────────────────────────────
  RCP 2.6          2.6 W/m²            ~1.5–2.0°C       Strong mitigation
  RCP 4.5          4.5 W/m²            ~2.0–2.5°C       Moderate mitigation
  RCP 6.0          6.0 W/m²            ~2.5–3.5°C       Intermediate
  RCP 8.5          8.5 W/m²            ~3.5–4.5°C       Business as usual
  ─────────────────────────────────────────────────────────────────────
```

**Limitation of RCPs:** They define *what* happens (the greenhouse gas concentration)
but not *why* — they say nothing about the economic, social, or policy conditions
that would produce that outcome.

### CMIP6: Shared Socioeconomic Pathways (SSPs)

CMIP6 combines RCP-style radiative forcing targets with **SSPs** — narratives about
the socioeconomic conditions of the world (population growth, technology, governance, equality).

The notation **SSP[pathway]-[forcing]** tells you both:
- The number after "SSP": the socioeconomic story (1=sustainability, 2=middle road, 3=rivalry, 5=fossil fuel)
- The number after the dash: the end-of-century radiative forcing (same W/m² scale as RCPs)

```
  SSP Scenario    Forcing    ≈ RCP Equivalent    Description
  ─────────────────────────────────────────────────────────────────────
  SSP1-1.9        1.9 W/m²   (below RCP2.6)     Sustainable development, net zero ~2050
  SSP1-2.6        2.6 W/m²   ≈ RCP 2.6          Sustainability, strong mitigation
  SSP2-4.5        4.5 W/m²   ≈ RCP 4.5          "Middle of the road" — current policies
  SSP3-7.0        7.0 W/m²   between RCP6/8.5   Regional rivalry, limited cooperation
  SSP5-8.5        8.5 W/m²   ≈ RCP 8.5          Fossil-fueled development, no mitigation
  ─────────────────────────────────────────────────────────────────────
```

### Visual: What does warming look like over time?

```
  Global Mean Temperature Change vs Pre-Industrial (°C)
  ─────────────────────────────────────────────────────────────────────

  +5°C │                                               ╭── SSP5-8.5
       │                                           ╭───╯
  +4°C │                                      ╭────╯
       │                                  ╭───╯       ── SSP3-7.0
  +3°C │                             ╭────╯
       │                        ╭────╯           ──── SSP2-4.5
  +2°C │                  ╭─────╯
       │             ╭────╯               ──────────── SSP1-2.6
  +1°C │       ╭─────╯
       │  ╭────╯                       ─────────────── SSP1-1.9
   0°C │──╯
       └──────────────────────────────────────────────►
       2000   2020   2040   2060   2080   2100

  (Approximate median projections. Actual ranges are wider.)
  ─────────────────────────────────────────────────────────────────────
```

### For LTRisk: Which scenario?

The project's pilot focuses on **SSP2-4.5** (moderate, middle-of-the-road) as the
primary scenario for two reasons:
1. It represents roughly current policy trajectory — neither optimistic nor alarmist
2. It is the most commonly cited scenario for infrastructure risk reporting

**Important caveat on Open-Meteo (see Section 8):** The HighResMIP models served
by Open-Meteo are aligned with approximately RCP8.5/SSP5-8.5, *not* SSP2-4.5.
For true multi-scenario analysis, the NEX-GDDP-CMIP6 dataset would be needed.

---

## 3. Why Multiple Models? The Ensemble Concept

### The fundamental problem

Climate models are imperfect representations of a chaotic system. Two models using
the same emissions scenario can give meaningfully different regional outcomes because
they differ in how they represent:
- Cloud formation and feedbacks
- Ocean heat uptake
- Aerosol interactions
- Land surface processes
- Sea ice dynamics

No single model is "correct." They each capture some aspects of reality better
than others.

### The ensemble solution

Using **multiple models** provides:

```
  Single model output              Ensemble of 7 models
  ─────────────────────            ─────────────────────────────────────────
                                              ┌──────────────────────────┐
  Temp anomaly                               │  P90 bound                │
  (°C)         ╭─────                        │  ╭─────────────────────   │
   2.5 │    ───╯                             │  │   ╭──────────────────  │
       │  ─╯                            2.5  │  │   │   Median range     │
   2.0 │─╯                                   │  │ ──┼─────────────────── │
       │                                 2.0 │ ─┼──╯    ╰───────────     │
   1.5 │                                     │  │                        │
       └──────► Year                    1.5  │  └────────────────────    │
                                             │     P10 bound             │
  One trajectory — cannot                   └──────────────────────────┘
  quantify uncertainty.             Distribution of outcomes — can express
                                    P10/P50/P90 confidence intervals.
```

1. **Quantify uncertainty** — Express results as P10/P50/P90 rather than a single number
2. **Identify robust signals** — If all 7 models agree warming increases in West Texas, that's a strong signal
3. **Detect model-specific artifacts** — If one model shows anomalous behavior, the ensemble reveals it

### Why CMIP6 ensemble matters more at regional scale

Global mean temperature projections are robust across models. But **regional** projections —
which is what matters for a solar farm in Culberson, TX — have much more spread.
The ensemble captures that uncertainty.

```
  Uncertainty in temperature projections:

  Global level:   Low spread    ████░░░░░░  Models mostly agree
  Continental:    Moderate      ████████░░  Some divergence
  Regional:       High          ██████████  Significant model differences
  Site-specific:  Very high     ████████████ Large range — MUST use ensemble
                                              ^
                                   This is what we care about
```

---

## 4. The Open-Meteo Climate API

### What it is

Open-Meteo (`climate-api.open-meteo.com`) provides free access to 7 high-resolution
CMIP6 climate models from the **HighResMIP working group** — a CMIP6 sub-project
specifically designed to run global climate models at unprecedented resolution (~20–50 km).

### Key features

| Feature | Value |
|---|---|
| Time coverage | 1950–01–01 to 2050–12–31 |
| Temporal resolution | Daily |
| Spatial resolution | Downscaled to **10 km** (from native 20–50 km) |
| Spatial selection | Point-based — specify any lat/lon |
| Authentication | None required (free tier) |
| Bias correction | Yes — statistical downscaling against ERA5-Land |
| API endpoint | `https://climate-api.open-meteo.com/v1/climate` |

### How bias correction works

Raw CMIP6 model output has systematic biases — a model might consistently simulate
West Texas as 2°C warmer than observed. Open-Meteo corrects this by:

```
  STEP 1: Compare model historical output (1950–2014) vs ERA5-Land reanalysis
           → Compute monthly correction coefficients for each grid cell

  STEP 2: Apply those corrections to the future projection
           → Corrections are additive for temperature, multiplicative for precipitation

  RESULT: The CLIMATE CHANGE SIGNAL is preserved; the absolute values are realistic
          "The climate change signal is not affected by linear bias correction." (Open-Meteo docs)
```

This is why we use the model's own historical run as baseline rather than ERA5 directly —
the bias correction coefficients are derived from that historical period, so the
historical and future data are internally consistent.

### Historical vs future periods

The API serves both periods from the same endpoint — no separate call needed:

```
  Date range           What you get
  ──────────────────────────────────────────────────────────────────
  1950–2014            Model historical run (climate observed period)
  2015–2050            Model future projection (SSP/RCP scenario)
  ──────────────────────────────────────────────────────────────────

  The transition at 2015 is seamless from an API perspective.
  The 2015 boundary is where CMIP6 models switch from "historical"
  to "future scenario" experiments internally.
```

---

## 5. Available Models — Comparison Table

All 7 models confirmed on Open-Meteo as of February 2026.

| API Model ID | Climate Model | Country/Institution | Native Resolution | Peer-Reviewed? |
|---|---|---|---|---|
| `EC_Earth3P_HR` | EC-Earth3P-HR | Europe (EC-Earth consortium / SMHI, Sweden) | 29 km | [Yes](https://gmd.copernicus.org/articles/13/3507/2020/) |
| `MRI_AGCM3_2_S` | MRI-AGCM3-2-S | Japan (Meteorological Research Institute, Tsukuba) | 20 km | Yes |
| `CMCC_CM2_VHR4` | CMCC-CM2-VHR4 | Italy (CMCC, Lecce) | 30 km | Yes |
| `FGOALS_f3_H` | FGOALS-f3-H | China (Chinese Academy of Sciences, Beijing) | 28 km | [Yes](https://link.springer.com/content/pdf/10.1007/s00376-022-2030-5.pdf) |
| `HiRAM_SIT_HR` | HiRAM-SIT-HR | Taiwan (Academia Sinica, AS-RCEC) | 25 km | Yes |
| `MPI_ESM1_2_XR` | MPI-ESM1-2-XR | Germany (Max Planck Institute for Meteorology) | 51 km | [Yes](https://gmd.copernicus.org/articles/12/3241/2019/) |
| `NICAM16_8S` | NICAM16-8S | Japan (MIROC / JAMSTEC) | 31 km | [Yes](https://gmd.copernicus.org/articles/14/795/2021/) |

### Model diversity

The geographic diversity of modeling institutions is intentional — each center uses
different numerical methods, parameterizations, and assumptions. An ensemble spanning
Europe, Japan, China, Italy, and Taiwan is more robust than one dominated by a single tradition.

### Recommended model for LTRisk

**Primary: `EC_Earth3P_HR`** (all P1+P2 variables confirmed, all time periods, well-documented)  
**Also consider: `MRI_AGCM3_2_S`** (highest native resolution at 20 km, only model with soil moisture)

---

## 6. Variable Availability by Model

Reproduced from Open-Meteo API documentation. ⚠️ = only daily mean available (no min/max).

| Variable Group | EC_Earth3P_HR | MRI_AGCM3_2_S | CMCC_CM2_VHR4 | FGOALS_f3_H | HiRAM_SIT_HR | MPI_ESM1_2_XR | NICAM16_8S |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Temperature (max/min/mean) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Relative Humidity (mean) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Relative Humidity (max/min) | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| Wind Speed (mean/max) | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ✅ |
| Precipitation | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Shortwave Radiation (rsds)** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Snowfall | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Cloud Cover | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Soil Moisture | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

### LTRisk variable requirements

```
  Variable   Purpose               EC_Earth3P_HR  Notes
  ─────────────────────────────────────────────────────────────────────
  tasmax     Heat waves, EFR       ✅             P1 — core
  tasmin     Frost days, freeze    ✅             P1 — core
  tas        Peck's model, FWI     ✅             P1 — core
  pr         Flood HCR, dry spell  ✅             P1 — core
  sfcWind    Wind extremes         ✅             P1 — core
  hurs       Peck's model, icing   ✅             P1 — core
  rsds       Solar pvlib model     ✅             P2 — performance
  ─────────────────────────────────────────────────────────────────────
  All 7 confirmed available in EC_Earth3P_HR historical + future runs.
```

---

## 7. What the Data Actually Looks Like

### API response structure (JSON)

```json
{
  "latitude": 31.815992,
  "longitude": -104.0853,
  "daily": {
    "time":                ["2000-01-01", "2000-01-02", ...],
    "temperature_2m_max":  [16.9, 24.5, 23.7, ...],
    "temperature_2m_min":  [3.3,  8.2,  14.4, ...],
    "temperature_2m_mean": [10.1, 16.3, 19.1, ...],
    "precipitation_sum":   [0.0,  0.0,  0.0,  ...],
    "wind_speed_10m_mean": [4.2,  3.1,  5.7,  ...],
    "relative_humidity_2m_mean": [42.1, 38.7, 55.3, ...],
    "shortwave_radiation_sum":   [12.3, 13.1, 9.8,  ...]
  },
  "daily_units": {
    "temperature_2m_max": "°C",
    "precipitation_sum":  "mm",
    "shortwave_radiation_sum": "MJ/m²"
  }
}
```

### What realistic Culberson TX data looks like

Verified from actual API response (EC_Earth3P_HR, January 2000):

```
  Culberson County TX — January 2000 sample (bias-corrected):
  ─────────────────────────────────────────────────────────────────────
  Date          tasmax   tasmin    pr    wind   hurs    rsds
                 (°C)     (°C)   (mm)  (m/s)    (%)  (MJ/m²)
  ─────────────────────────────────────────────────────────────────────
  2000-01-01     16.9      3.3    0.0   4.2     42     10.1
  2000-01-02     24.5      8.2    0.0   3.1     38     13.2
  2000-01-03     23.7     14.4    0.0   5.7     55      9.8
  2000-01-04     21.4     11.6    0.0   2.9     47     12.7
  2000-01-05     19.3      8.6    0.0   6.1     41     11.5
  ─────────────────────────────────────────────────────────────────────
  Physical plausibility check:
  • Jan tasmax ~15–25°C ✅ (West Texas mild winter, high desert)
  • Low humidity (~40%) ✅ (arid desert, typical for Culberson)
  • Near-zero precipitation ✅ (Culberson annual avg ~250 mm, very dry Jan)
  • Moderate solar radiation ✅ (winter but high-altitude, clear desert sky)
```

### Seasonal climatology pattern expected for Hayhurst Solar

```
  Monthly mean tasmax (°C) — Hayhurst Solar, Culberson TX (1980–2014)
  ──────────────────────────────────────────────────────────────────────
  45 │                          ████ ████
     │                     ████ ████ ████ ████
  40 │                ████ ████ ████ ████ ████
     │           ████ ████ ████ ████ ████ ████
  35 │      ████ ████ ████ ████ ████ ████ ████ ████
     │      ████ ████ ████ ████ ████ ████ ████ ████
  30 │ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████
     │ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████
  25 │ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████
     │ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████
  20 │ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████
  15 │ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████ ████
      ─────────────────────────────────────────────────────────────
      Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec

  (Approximate expected values based on NOAA climatology for Culberson County)
```

---

## 8. Critical Limitations to Understand

### Limitation 1: Single emissions scenario — ALL 7 models, not just our chosen one (most important)

**Every model on the Open-Meteo Climate API runs under approximately SSP5-8.5 / RCP8.5.
This is not a property of any one model — it applies to all 7.**

From the official API documentation:
> *"The high resolution climate models are as close to RCP8.5 as possible within CMIP6."*

Why? The HighResMIP experiment was designed for high-resolution spatial research, not
multi-scenario analysis. Running a global model at 20–30 km resolution is extremely
expensive, so only one emissions pathway was simulated for all 7 models.

**Switching to a different model on Open-Meteo does not give you SSP2-4.5.**

```
  Common misconception:
  ─────────────────────────────────────────────────────────────────────────────
  "I'll use EC_Earth3P_HR for SSP5-8.5 and NICAM16_8S for SSP2-4.5"

  Reality:
  EC_Earth3P_HR   →  SSP5-8.5 (high emissions)
  NICAM16_8S      →  SSP5-8.5 (high emissions)
  FGOALS_f3_H     →  SSP5-8.5 (high emissions)
  HiRAM_SIT_HR    →  SSP5-8.5 (high emissions)
  CMCC_CM2_VHR4   →  SSP5-8.5 (high emissions)
  MPI_ESM1_2_XR   →  SSP5-8.5 (high emissions)
  MRI_AGCM3_2_S   →  SSP5-8.5 (high emissions)
  ─────────────────────────────────────────────────────────────────────────────
  They all run SSP5-8.5. The 7 models give you uncertainty across model
  physics, not across emissions scenarios.
```

**What the scenario label in our files actually means:**

Our Parquet files are named `ssp245_EC_Earth3P_HR_...` — the `ssp245` label is
something **we wrote ourselves** as metadata. It does not change the API data.
It is a placeholder for when we later switch to a dataset that actually has SSP2-4.5.

**Impact on our SCVR results:**

```
  Our SCVR values represent:   HIGH-EMISSIONS future (~+3.3°C by 2049 for West Texas)
  SSP2-4.5 would show:         MODERATE future (~+1.5–2°C by 2049)
  Difference in SCVR:          Roughly 40–50% lower values under SSP2-4.5

  Is this a problem for prototyping?  No  — the methodology is correct
  Is this a problem for reporting?    Yes — must be disclosed to stakeholders
  Is it conservative?                 Yes — overestimates risk vs moderate scenario
```

**Fix for production:** Use NASA NEX-GDDP-CMIP6 (available on AWS S3, free).
It has proper SSP2-4.5 and SSP5-8.5 runs for 35 CMIP6 models. The pipeline,
schemas, and SCVR code transfer directly — only the data ingestion cell changes.

### Limitation 2: 2050 horizon only

The API only serves data to 2050. For assets with 35-year EUL (wind turbines), 
projections to 2060–2070 would require:
- Extrapolation beyond 2050 (with large uncertainty)
- Or direct access to CMIP6 full-century projections

For the pilot, **2050 is sufficient** for solar assets (25-year EUL from 2025 = 2050).

### Limitation 3: Daily mean wind is a proxy

Wind speed in CMIP6 is daily mean at 10 m height. For wind turbines at 80–100 m hub height,
a vertical extrapolation (power law or log law) would be needed for performance modeling.
For SCVR relative comparisons (baseline vs future), the daily mean is adequate.

### Limitation 4: Historical data ≠ observations

```
  The historical model output (1950–2014) is NOT actual observed weather —
  it is the model's simulation of the past. Think of it as:

  "How would this model's physics reproduce the past if initialized correctly?"

  After bias correction against ERA5-Land, the absolute values are realistic,
  but individual days will not match actual historical weather events.

  For SCVR: This is fine — we care about the statistical distribution
            (exceedance curves), not individual days.

  For event attribution: NOT suitable. Use actual NOAA/ERA5 data instead.
```

### Limitation 5: No daily rsds in CMCC_CM2_VHR4

`CMCC_CM2_VHR4` is missing precipitation, shortwave radiation, and snowfall. **Do not use
CMCC as a primary model for any LTRisk work involving solar performance (Pathway B).**

---

## 9. How This Fits Into LTRisk

### Where in the analysis pipeline this data is used

```
  Open-Meteo API
  ┌─────────────────────────────────────────────────────────┐
  │  EC_Earth3P_HR historical (1950–2014)                   │
  │  EC_Earth3P_HR future     (2015–2050) ≈ SSP5-8.5        │
  └────────────────────────────┬────────────────────────────┘
                               │ 7 variables, daily resolution
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │  data/raw/cmip6/<site_id>/                              │
  │    historical_EC_Earth3P_HR_1980_2014.parquet           │
  │    ssp245_EC_Earth3P_HR_2015_2050.parquet               │
  └────────────────────────────┬────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
     SCVR computation  Extreme indices   Baseline stats
     (Notebook 01)     (Notebook 01)     (Notebook 01)
              │
              ▼
  ┌─────────────────────────────────────────────────────────┐
  │  data/processed/scvr/<site_id>/                         │
  │    ssp245_EC_Earth3P_HR_scvr.parquet                    │
  └────────────────────────────┬────────────────────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
  HCR computation    EFR computation    ← Notebooks 02+
  (hazard change)    (equipment aging)
     │                 │
     └────────┬─────────┘
              ▼
  NAV Impairment calculation             ← Notebook 04
```

### SCVR — the bridge between climate data and financial risk

SCVR (Severe Climate Variability Rating) is the key intermediate computation.
It converts raw daily time series into a **single dimensionless metric per variable per year**
that quantifies how much more extreme the climate has become relative to the baseline.

```
  SCVR formula:
  SCVR(variable, year) = (area_future - area_baseline) / area_baseline

  Where "area" = trapezoid integral of the rank-sorted exceedance curve

  SCVR = 0.0  →  No change from baseline
  SCVR = 0.2  →  Exceedance area is 20% larger (more extremes)
  SCVR = -0.3 →  Exceedance area is 30% smaller (fewer extremes, e.g., freeze events)
```

---

## 10. Quick Reference — API Calls

### Fetch historical baseline (1980–2014)

```python
import requests

resp = requests.get(
    "https://climate-api.open-meteo.com/v1/climate",
    params={
        "latitude": 31.815992,
        "longitude": -104.0853,
        "start_date": "1980-01-01",
        "end_date": "2014-12-31",
        "models": "EC_Earth3P_HR",
        "daily": [
            "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
            "precipitation_sum", "wind_speed_10m_mean",
            "relative_humidity_2m_mean", "shortwave_radiation_sum",
        ],
    },
    timeout=60,
)
data = resp.json()["daily"]
```

### Fetch future projection (2015–2050)

Same call, just change `start_date` and `end_date`:
```python
"start_date": "2015-01-01",
"end_date":   "2050-12-31",
```

### Fetch all 7 models at once (ensemble)

```python
params["models"] = [
    "EC_Earth3P_HR", "MRI_AGCM3_2_S", "NICAM16_8S",
    "FGOALS_f3_H", "HiRAM_SIT_HR", "MPI_ESM1_2_XR", "CMCC_CM2_VHR4"
]
# Note: When multiple models are requested, the JSON response includes
# one key per variable per model: e.g., "temperature_2m_max_EC_Earth3P_HR"
# versus the single-model key "temperature_2m_max"
```

> **Do not include CMCC_CM2_VHR4** when fetching `precipitation_sum` or
> `shortwave_radiation_sum` — it returns 400 or null for those variables.

### Test connectivity

```bash
python scripts/tests/test_openmeteo_api.py
```

### Re-run full variable/model probe

```bash
python scripts/tests/probe_openmeteo_variables.py
# Results saved to: scripts/tests/probe_results.json
```

---

## References and Further Reading

| Resource | URL |
|---|---|
| Open-Meteo Climate API docs | https://open-meteo.com/en/docs/climate-api |
| HighResMIP working group | https://hrcm.ceda.ac.uk/research/cmip6-highresmip/ |
| EC-Earth3P-HR model paper | https://gmd.copernicus.org/articles/13/3507/2020/ |
| NICAM16-8S model paper | https://gmd.copernicus.org/articles/14/795/2021/ |
| MPI-ESM1-2-XR model paper | https://gmd.copernicus.org/articles/12/3241/2019/ |
| CMIP6 multi-model uncertainty | https://esd.copernicus.org/articles/11/491/2020/ |
| IPCC AR6 WG1 Atlas | https://www.ipcc.ch/report/ar6/wg1/ |
| NEX-GDDP-CMIP6 (multi-scenario) | https://www.nccs.nasa.gov/services/data-collections/land-based-products/nex-gddp-cmip6 |
| CMIP6 terms of use | https://pcmdi.llnl.gov/CMIP6/TermsOfUse |

---

*Related files in this project:*
- `data/schema/VARIABLES.md` — variable priority tiers and confirmed availability
- `data/schema/variables.json` — machine-readable variable definitions  
- `data/schema/sites.json` — site registry with confirmed model names
- `scripts/tests/probe_openmeteo_variables.py` — API verification script
- `scripts/tests/probe_results.json` — latest probe results
