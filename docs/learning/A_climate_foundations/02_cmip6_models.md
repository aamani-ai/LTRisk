# CMIP6 and Climate Models

> How scientists simulate future climate, what CMIP6 is, why we use multiple models, and how NASA NEX-GDDP-CMIP6 makes it accessible.

---

## 1. What Is a Climate Model?

A climate model is a giant physics simulation of the entire Earth system:

```
EARTH SYSTEM MODEL (ESM) — What Gets Simulated
============================================================

  ATMOSPHERE             OCEAN              LAND SURFACE
  ┌────────────┐        ┌────────────┐     ┌────────────┐
  │ Wind       │        │ Currents   │     │ Vegetation │
  │ Temperature│ <----> │ Temperature│<--->│ Soil       │
  │ Humidity   │        │ Salinity   │     │ Rivers     │
  │ Clouds     │        │ Sea ice    │     │ Snow/Ice   │
  │ Radiation  │        │ Depth      │     │ Albedo     │
  └────────────┘        └────────────┘     └────────────┘
        ^                     ^                  ^
        |                     |                  |
        v                     v                  v
  ┌─────────────────────────────────────────────────────┐
  │              CARBON CYCLE / CHEMISTRY                │
  │  CO2, CH4, aerosols, ozone — driven by emissions    │
  └─────────────────────────────────────────────────────┘
```

**How it works**:
1. The Earth is divided into a 3D grid (atmosphere + ocean + land)
2. At each grid cell, the model solves physics equations (fluid dynamics, thermodynamics, radiation)
3. Time steps forward (typically 15-30 minutes of simulated time per step)
4. The model runs for centuries of simulated time

**Grid resolution of NEX-GDDP-CMIP6**: 0.25 x 0.25 degrees (~25 km at the equator)

```
WHAT THE GRID LOOKS LIKE (zoomed into Texas)

         -106    -104    -102    -100     -98
    33  ┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
        │   │   │   │   │   │   │   │   │   │
    32  ├───┼───┼───┼───┼───┼───┼───┼───┼───┤
        │   │ H │   │   │   │ M │   │   │   │  H = Hayhurst Solar
    31  ├───┼───┼───┼───┼───┼───┼───┼───┼───┤  M = Maverick Wind
        │   │   │   │   │   │   │   │   │   │
    30  ├───┼───┼───┼───┼───┼───┼───┼───┼───┤  Each box is ~25km x 25km
        │   │   │   │   │   │   │   │   │   │  We extract the single grid
    29  └───┴───┴───┴───┴───┴───┴───┴───┴───┘  cell closest to our coordinates
```

---

## 2. What Is CMIP6?

**CMIP** = Coupled Model Intercomparison Project

It's an international collaboration where ~50 climate modeling centers worldwide all run the **same experiments** with their **different models**, then compare results:

```
CMIP HISTORY

  CMIP1 (1995)    CMIP3 (2004)     CMIP5 (2011)      CMIP6 (2019)
     |                |                 |                  |
     v                v                 v                  v
  ~5 models       ~25 models        ~40 models         ~100 models
  Coarse grid     ~100km grid       ~100km grid        ~25-100km grid
  Basic physics   Better clouds     Aerosol chemistry  Earth system
                                    Used in IPCC AR5   Used in IPCC AR6
                                    RCP scenarios      SSP scenarios
                                                       <-- WE USE THIS
```

**CMIP6** is the latest generation (used in the IPCC Sixth Assessment Report, AR6):
- Over 100 model variants from 49 modeling groups
- Better representation of clouds, aerosols, and carbon cycle feedbacks
- Higher resolution
- New scenario framework (SSPs instead of RCPs)

**Key principle**: No single model is "right." Each model makes different approximations for sub-grid processes (clouds, turbulence, convection). By using **multiple models**, we capture the range of plausible futures.

---

## 3. The 34 NEX-GDDP-CMIP6 Models

NASA took the raw CMIP6 output and created **NEX-GDDP-CMIP6**: a curated, bias-corrected, downscaled dataset. All 34 models are on the same 0.25-degree grid with daily data:

```
MODEL LIST (34 models in NEX-GDDP-CMIP6)
==============================================
  ACCESS-CM2          Australia (CSIRO-ARCCSS)
  ACCESS-ESM1-5       Australia (CSIRO)
  BCC-CSM2-MR         China (BCC)
  CanESM5             Canada (CCCma)
  CESM2               USA (NCAR)
  CESM2-LENS          USA (NCAR, large ensemble)
  CMCC-CM2-SR5        Italy (CMCC)
  CMCC-ESM2           Italy (CMCC)
  CNRM-CM6-1          France (CNRM-CERFACS)
  CNRM-ESM2-1         France (CNRM-CERFACS)
  EC-Earth3            Europe (EC-Earth consortium)
  EC-Earth3-Veg-LR    Europe (EC-Earth consortium)
  FGOALS-g3           China (CAS)
  GFDL-CM4            USA (NOAA-GFDL)
  GFDL-CM4_gr2        USA (NOAA-GFDL, alt grid)
  GFDL-ESM4           USA (NOAA-GFDL)
  GISS-E2-1-G         USA (NASA-GISS)
  HadGEM3-GC31-LL     UK (Met Office)
  HadGEM3-GC31-MM     UK (Met Office, medium res)
  IITM-ESM            India (IITM)
  INM-CM4-8           Russia (INM)
  INM-CM5-0           Russia (INM)
  IPSL-CM6A-LR        France (IPSL)
  KACE-1-0-G          South Korea (NIMS-KMA)
  KIOST-ESM           South Korea (KIOST)
  MIROC6              Japan (U. Tokyo / JAMSTEC)
  MPI-ESM1-2-HR       Germany (MPI-M, high res)
  MPI-ESM1-2-LR       Germany (MPI-M, low res)
  MRI-ESM2-0          Japan (MRI)
  NESM3               China (NUIST)
  NorESM2-LM          Norway (NCC)
  NorESM2-MM          Norway (NCC, medium res)
  TaiESM1             Taiwan (RCEC)
  UKESM1-0-LL         UK (NERC)
```

**We use up to 6 models per variable/scenario** (MAX_MODELS = 6) because:
- More than 6 gives diminishing returns for ensemble statistics
- Each model requires fetching 60 years of daily data (30 baseline + 30 future)
- Runtime scales linearly with model count

---

## 4. Why Multiple Models? The Ensemble Approach

### The Problem with One Model

```
SINGLE MODEL (what Notebook 01 did)

  Temperature
  projection     EC-Earth3P-HR says: +2.8C by 2050
       |
       |         But what if EC-Earth3P-HR overestimates
       |         cloud feedbacks? Then the real answer
       |         might be +2.0C ... or +3.5C.
       v
  We have NO IDEA how uncertain that +2.8C is.
```

### The Power of Multiple Models

```
ENSEMBLE (what Notebook 03 does)

  ACCESS-CM2:      +2.3C  ─┐
  MIROC6:          +2.1C   │
  MRI-ESM2-0:      +2.6C   ├── Ensemble range: +2.1C to +3.2C
  GFDL-CM4:        +2.9C   │   Ensemble mean:  +2.6C
  CanESM5:         +3.2C   │   Spread tells us about UNCERTAINTY
  MPI-ESM1-2-HR:   +2.5C  ─┘

  Median: +2.55C
  P10-P90 range: +2.1C to +3.1C
```

**What the spread tells us**:
- If all 6 models agree (tight spread) -> high confidence in the projection
- If models disagree wildly (wide spread) -> high uncertainty, be cautious
- The Strip Plot (Plot D in Notebook 03) visualizes exactly this

### How We Pool for SCVR

Instead of computing SCVR per model then averaging, we **pool all daily values** from all models into one big bag:

```
POOLING APPROACH

  Model A:  10,950 daily baseline values  ─┐
  Model B:  10,950 daily baseline values   ├──>  Pool: 65,700 values
  Model C:  10,950 daily baseline values   │     (one giant distribution)
  Model D:  10,950 daily baseline values   │
  Model E:  10,950 daily baseline values   │     Then compute ONE SCVR
  Model F:  10,950 daily baseline values  ─┘     on this pooled data

  Why pool?
  - Smooths out individual model biases
  - More data points = more robust tail estimation
  - Single definitive SCVR per variable per scenario
```

---

## 5. Bias Correction and Downscaling

Raw CMIP6 output has biases (a model might systematically run 2C too warm). NASA NEX-GDDP-CMIP6 applies:

```
RAW CMIP6 OUTPUT                    NEX-GDDP-CMIP6
(~100km grid, biased)               (25km grid, bias-corrected)

  ┌───────────┐                     ┌──┬──┬──┬──┐
  │           │    Bias Correction  ├──┼──┼──┼──┤
  │  Too warm │  ───────────────>   ├──┼──┼──┼──┤  Matches observed
  │  by 2C    │    Downscaling      ├──┼──┼──┼──┤  statistics
  │           │                     └──┴──┴──┴──┘
  └───────────┘
  1 grid cell = 100km               16 grid cells = 25km each
```

**Method**: BCSD (Bias Correction Spatial Disaggregation)
1. Compare model historical output to observations (ERA5 reanalysis)
2. Build a statistical mapping that corrects the model's biases
3. Apply the same correction to future projections
4. Downscale from coarse to fine grid using observed spatial patterns

**This means**: When we fetch data from THREDDS, it's already been quality-controlled. We still do unit conversion (K to C, flux to mm/day) but the physics is sound.

---

## 6. Model Naming Convention

CMIP6 model names encode information:

```
MODEL NAME ANATOMY

  MPI-ESM1-2-HR
  ^^^  ^^^   ^^
  |    |     |
  |    |     └── HR = High Resolution (vs LR = Low Resolution)
  |    └──────── ESM1-2 = Earth System Model version 1.2
  └───────────── MPI = Max Planck Institute (Germany)


EXPERIMENT NAMING

  r1i1p1f1_gn
  ^ ^ ^ ^  ^^
  | | | |  |└── gn = native grid
  | | | |  └─── grid type
  | | | └────── f1 = forcing index 1
  | | └──────── p1 = physics index 1
  | └────────── i1 = initialization index 1
  └──────────── r1 = realization (ensemble member) 1

  We always use r1i1p1f1 = the first/default ensemble member.
```

---

## 7. What "Historical" vs "SSP" Means in the Data

```
CMIP6 EXPERIMENT STRUCTURE

  Experiment name    Period       What drives it
  ────────────────   ──────────   ──────────────────────────────
  historical         1850-2014    Real observed forcings (CO2, volcanic,
                                  solar, aerosols) — what actually happened

  ssp119             2015-2100    SSP1-1.9: Net zero by 2050
  ssp126             2015-2100    SSP1-2.6: Strong mitigation
  ssp245             2015-2100    SSP2-4.5: Middle of the road  <-- WE USE
  ssp370             2015-2100    SSP3-7.0: Regional rivalry
  ssp585             2015-2100    SSP5-8.5: Fossil-fueled dev   <-- WE USE
```

When we fetch data:
- `fetch_year(model, "historical", var, 2005, ...)` gets real historical simulation
- `fetch_year(model, "ssp245", var, 2040, ...)` gets SSP2-4.5 future projection

The data files on THREDDS are literally named:
```
tasmax_day_ACCESS-CM2_historical_r1i1p1f1_gn_2005.nc
tasmax_day_ACCESS-CM2_ssp245_r1i1p1f1_gn_2040.nc
```

---

## Next

- [03 - Scenarios and Time Windows](03_scenarios_and_time_windows.md) — The five future pathways in detail
