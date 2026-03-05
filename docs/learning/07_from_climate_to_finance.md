# From Climate to Finance — The SCVR -> HCR -> EFR -> NAV Chain

> How a shift in temperature distribution eventually becomes a dollar amount of asset impairment. This is the full translation chain from climate physics to financial risk.

---

## 1. The Full Pipeline at a Glance

```
CLIMATE DATA                 CLIMATE RISK                  FINANCIAL IMPACT
─────────────                ───────────                   ─────────────────

  Daily tasmax,              SCVR                          NAV Impairment
  tasmin, pr,        ──>     (per variable    ──>          ($ million)
  sfcWind, hurs              per scenario)

  Notebook 01-03             Notebook 03           Notebook 04          Notebook 05+
  ┌──────────────┐          ┌──────────┐         ┌──────────────┐     ┌──────────────┐
  │ Fetch daily  │          │ Compute  │         │ HCR: Hazard  │     │ BI losses    │
  │ climate data │ ──SCVR──>│ exceedance│──SCVR──>│ Change Ratio │     │ IUL change   │
  │ from THREDDS │          │ area     │         │              │     │ Depreciation │
  └──────────────┘          │ shift    │         │ EFR: Equip   │──>  │ adjustment   │
                            └──────────┘         │ Failure Ratio│     │              │
                                                 └──────────────┘     │ -> NAV delta │
                                                                      └──────────────┘
```

---

## 2. Layer 1: SCVR (What We Built in Notebook 03)

**Input**: Daily climate values for baseline and future periods
**Output**: A single fractional change number per variable per scenario

```
SCVR EXAMPLE OUTPUT

  Site: Hayhurst Solar
  ┌───────────┬──────────┬──────────┐
  │ Variable  │ SSP2-4.5 │ SSP5-8.5 │
  ├───────────┼──────────┼──────────┤
  │ tasmax    │  +0.052  │  +0.084  │
  │ tasmin    │  +0.041  │  +0.069  │
  │ tas       │  +0.049  │  +0.079  │
  │ pr        │  +0.016  │  +0.031  │
  │ sfcWind   │  -0.002  │  -0.002  │
  │ hurs      │  +0.009  │  +0.015  │
  └───────────┴──────────┴──────────┘

  These numbers say:
  "tasmax distribution shifted +5.2% under SSP2-4.5"
  "tasmax distribution shifted +8.4% under SSP5-8.5"
```

**What SCVR does NOT tell you**: How much money this costs. A +5% shift in temperature might cause $100K in losses or $10M — SCVR doesn't know. That's what the next layers do.

---

## 3. Layer 2: HCR (Hazard Change Ratio) — Notebook 04

**Purpose**: Translate the generic SCVR into **hazard-specific impact ratios** using published damage functions.

### What Are Hazards?

Climate variables don't damage equipment directly. **Hazards** do:

```
VARIABLE -> HAZARD MAPPING

  Variable     Hazards Derived
  ─────────    ──────────────────────────────────
  tasmax   ->  Heat wave days (consecutive days > threshold)
               Icing days (tasmax < 0C)

  tasmin   ->  Frost days (tasmin < 0C)
               Cold wave days
               Freeze-thaw cycles (tasmin < 0, tasmax > 0)

  pr       ->  Extreme precipitation (Rx5day = max 5-day total)
               Dry spell length (max consecutive days with pr < 1mm)

  sfcWind  ->  Wind cut-out days (sfcWind > 25 m/s for turbines)
               Extreme wind events

  hurs     ->  Icing conditions (T < 0 AND hurs > 75%)
               Humidity stress (heat x humidity interaction)

  Combined ->  Fire Weather Index (FWI): uses tas, pr, sfcWind, hurs
```

### How HCR Uses SCVR

```
HCR CONCEPT

  HCR_heat = SCVR_tasmax  x  damage_scaling_factor_heat

  Where damage_scaling_factor comes from published literature:
  - "A 1% increase in extreme heat frequency causes X% increase
     in heat-related equipment failures" (from engineering papers)

  Example:
    SCVR_tasmax = +0.084 (8.4% more extreme heat under SSP5-8.5)
    damage_scaling_factor = 2.5 (from literature: heat damage
                                  amplifies ~2.5x the climate shift)
    HCR_heat = 0.084 x 2.5 = 0.21

  Meaning: "Heat hazard is 21% worse than baseline"
```

### HCR Is Hazard-Specific

```
HCR OUTPUT (one row per hazard per scenario)

  Hazard              SSP2-4.5  SSP5-8.5
  ──────────────────  ────────  ────────
  Heat stress          0.13      0.21
  Freeze-thaw          -0.05    -0.03    (fewer freeze events = less damage)
  Extreme precip       0.04      0.08
  Wind extreme         0.01      0.01
  Icing                -0.08    -0.06
  Fire weather         0.07      0.12

  Note: Negative HCR means the hazard DECREASES.
  Warming reduces icing and freeze risk (for this location).
```

---

## 4. Layer 3: EFR (Equipment Failure Ratio) — Notebook 04

**Purpose**: Translate hazard changes into **equipment-specific degradation** using engineering models.

### The Three Engineering Models

#### Model A: Peck's Model (Thermal + Humidity Aging)

```
PECK'S MODEL — for solar panel degradation

  Acceleration Factor = exp(Ea/k * (1/T_ref - 1/T_stress)) * (RH_stress/RH_ref)^n

  Where:
    Ea  = activation energy (0.7 eV for encapsulant degradation)
    k   = Boltzmann constant
    T   = absolute temperature (K)
    RH  = relative humidity (%)
    n   = humidity exponent (~2.5 for PV modules)

  In plain English:
    "For every 10C increase in operating temperature,
     the degradation rate roughly DOUBLES."

  How SCVR feeds in:
    SCVR_tas tells us how much mean temperature shifts
    SCVR_hurs tells us how much humidity shifts
    -> These shift T_stress and RH_stress in Peck's model
    -> Output: factor by which panel aging accelerates
```

```
EXAMPLE:

  Baseline mean temp:  22C (295K)
  Future mean temp:    24C (297K)  (SCVR_tas = +0.05 implies ~2C shift)

  Peck's acceleration factor:
    exp(0.7/8.617e-5 * (1/295 - 1/297)) = ~1.18

  Meaning: panels degrade 18% faster than baseline expectations.
  A 25-year expected useful life might effectively become ~21 years.
```

#### Model B: Coffin-Manson (Thermal Cycling Fatigue)

```
COFFIN-MANSON — for solder joints, connectors, structural fatigue

  N_f = C * (delta_T)^(-beta)

  Where:
    N_f     = number of cycles to failure
    delta_T = temperature swing magnitude (tasmax - tasmin)
    C, beta = material constants
    beta    ~ 2-3 for typical solder joints

  In plain English:
    "Larger daily temperature swings cause faster fatigue failure.
     If the swing increases by 20%, cycles-to-failure drops by ~50%."

  How SCVR feeds in:
    SCVR_tasmax and SCVR_tasmin tell us if the range is widening
    -> Larger future swings -> fewer cycles to failure
    -> Output: change in expected fatigue life
```

#### Model C: Palmgren-Miner (Cumulative Wind Damage)

```
PALMGREN-MINER — for wind turbine structural fatigue

  Damage = SUM( n_i / N_i )

  Where:
    n_i = number of cycles at stress level i (from wind speed distribution)
    N_i = number of cycles to failure at stress level i (from S-N curve)
    Failure when Damage >= 1.0

  In plain English:
    "Each wind gust uses up a fraction of the turbine's fatigue life.
     Stronger/more frequent gusts use up life faster."

  How SCVR feeds in:
    SCVR_sfcWind tells us if wind extremes are changing
    -> Shifted wind distribution -> different n_i values
    -> Output: change in cumulative fatigue damage rate
```

### EFR Output

```
EFR = weighted combination of engineering model outputs

  EFR_solar = w1 * Peck's_factor + w2 * Coffin_Manson_factor
  EFR_wind  = w1 * Palmgren_Miner_factor + w2 * icing_factor

  Example:
    EFR_solar (SSP2-4.5) = 0.15  (15% faster degradation)
    EFR_solar (SSP5-8.5) = 0.24  (24% faster degradation)
```

---

## 5. Layer 4: Financial Impact — NAV Impairment

**Purpose**: Convert physical degradation into **dollars**.

### Two Channels of Financial Impact

```
CHANNEL 1: BUSINESS INTERRUPTION (BI) LOSSES
─────────────────────────────────────────────

  More extreme heat -> more hours above panel derating threshold
  More extreme wind -> more turbine cut-out hours
  More extreme rain -> more flood-related downtime

  BI_loss = SUM(hazard_hours * capacity_MW * electricity_price)

  Example:
    50 additional heat-derate hours/year x 24.8 MW x $40/MWh
    = ~$49,600/year additional BI loss
    Over 30 years: ~$1.5M


CHANNEL 2: USEFUL LIFE SHORTENING (IUL)
───────────────────────────────────────

  Faster degradation -> asset reaches end-of-life sooner
  This means less lifetime revenue AND accelerated depreciation

  IUL_change = EFR * base_useful_life

  Example:
    Base useful life: 25 years
    EFR: 0.15 (15% faster degradation)
    Effective useful life: 25 / 1.15 = 21.7 years
    Lost years: 3.3 years
    Revenue per year: ~$4M
    Lost revenue: ~$13.2M (undiscounted)
```

### NAV Impairment Calculation

```
NAV IMPAIRMENT = sum of all financial impacts

  ┌──────────────────────────────────────────────────┐
  │                                                  │
  │  NAV_impairment = BI_losses                      │
  │                 + IUL_revenue_loss                │
  │                 + accelerated_depreciation        │
  │                 - salvage_value_adjustment        │
  │                 - insurance_recovery              │
  │                                                  │
  │  Discounted to present value at appropriate rate  │
  │                                                  │
  └──────────────────────────────────────────────────┘
```

---

## 6. The Complete Chain — Numerical Example

```
HAYHURST SOLAR — SSP5-8.5 SCENARIO (ILLUSTRATIVE)

Step 1: Climate Data
  30 years of daily tasmax from 6 CMIP6 models
  Baseline: ~65,700 daily values
  Future:   ~65,700 daily values

Step 2: SCVR
  SCVR_tasmax = +0.084 (8.4% shift in exceedance area)

Step 3: HCR
  HCR_heat = SCVR_tasmax x scaling = 0.084 x 2.5 = 0.21
  "Heat hazard is 21% more severe"

Step 4: EFR
  Peck's model: acceleration factor = 1.18
  EFR_thermal = 0.18 (18% faster aging)

Step 5: Financial Impact
  IUL shortening: 25 years -> 21.2 years (3.8 years lost)
  Lost revenue: 3.8 years x $3.5M/year = $13.3M
  Additional BI losses: ~$2.1M over lifetime
  Total NAV impairment: ~$15.4M (undiscounted)
  Present value (@8%): ~$8.2M

  On a 24.8 MW asset valued at ~$60M:
  NAV impairment = ~13.7% of asset value

  Under SSP2-4.5:
  NAV impairment = ~8.5% of asset value

  Delta between scenarios: ~5.2 percentage points
  = "The emission pathway choice is worth ~$3.1M on this one asset"
```

**Note**: These numbers are illustrative. Actual values depend on Notebook 04's calibration against published damage functions and site-specific parameters.

---

## 7. Why This Matters for Infrastructure Investors

```
INVESTOR PERSPECTIVE

  Without climate risk adjustment:
    Asset value = $60M
    Expected return = 8%/year over 25 years
    Seems like a good investment.

  With climate risk adjustment (SSP2-4.5):
    Asset value = $60M - $5.1M climate impairment = $54.9M
    Effective return = 7.1%/year over 22.5 years
    Still investable, but lower return.

  With climate risk adjustment (SSP5-8.5):
    Asset value = $60M - $8.2M climate impairment = $51.8M
    Effective return = 6.4%/year over 21.2 years
    Marginal — might not meet hurdle rate.

  THE POINT: Climate risk is a material financial factor
  that should be priced into infrastructure valuations.
  SCVR is the foundation of that pricing.
```

---

## 8. Where Each Notebook Fits

```
NOTEBOOK MAP

  NB 01: Hayhurst Solar SCVR (single model proof of concept)
         ├── Proved SCVR methodology works
         ├── Used Open-Meteo / EC-Earth3P-HR only
         └── Output: SCVR for one model, one scenario

  NB 02: NEX-GDDP-CMIP6 THREDDS Pipeline
         ├── Built the multi-model data fetching engine
         ├── Proved THREDDS NCSS works for point extraction
         └── Output: Pipeline functions (no SCVR computation)

  NB 03: Integrated SCVR + CMIP6 Ensemble (THIS IS THE MAIN ONE)
         ├── Fuses NB01 math + NB02 pipeline
         ├── Multi-model, multi-scenario, multi-variable
         ├── Produces definitive SCVR per site
         └── Output: Parquet files at data/processed/scvr/<site>/

  NB 04: HCR + EFR (NEXT TO BUILD)
         ├── Reads SCVR Parquet from NB03
         ├── Applies damage functions for HCR
         ├── Applies engineering models for EFR
         └── Output: Hazard and equipment failure ratios

  NB 05+: Financial Impact / NAV Impairment
         ├── Reads HCR + EFR from NB04
         ├── Applies financial models (DCF, depreciation)
         └── Output: Dollar-denominated climate risk
```

---

## 9. Key Terminology Quick Reference

| Term | Full Name | What It Is |
|---|---|---|
| **SCVR** | Severe Climate Variability Rating | Fractional shift in exceedance curve area |
| **HCR** | Hazard Change Ratio | Climate-to-hazard translation via damage functions |
| **EFR** | Equipment Failure Ratio | Hazard-to-degradation translation via engineering models |
| **NAV** | Net Asset Value | Financial value of the asset |
| **BI** | Business Interruption | Revenue lost due to climate-caused downtime |
| **IUL** | Insured Useful Life | Expected operational lifetime (shortened by climate) |
| **SSP** | Shared Socioeconomic Pathway | Future emission scenario (we use SSP2-4.5 and SSP5-8.5) |
| **CMIP6** | Coupled Model Intercomparison Project Phase 6 | The climate model ensemble |
| **THREDDS** | Thematic Real-time Environmental Distributed Data Services | NASA's data server |
| **NCSS** | NetCDF Subset Service | Server-side point extraction from THREDDS |

---

## Next

Return to [Index](00_index.md) for the full learning guide table of contents.
