**CLIMATE RISK ASSESSMENT FRAMEWORK**

*NAV Impairment Analysis for Renewable Infrastructure Assets*

# **EXECUTIVE SUMMARY**

This framework provides a comprehensive methodology for assessing Net Asset Value (NAV) impairment of renewable infrastructure assets under various climate scenarios. The approach integrates climate variability, business interruption, equipment degradation, and catastrophic hazards to quantify impacts on asset performance, useful life, and financial returns.

**Key Framework Components:**

* Climate variability analysis using CMIP6 projections  
* Asset performance modeling under climate stress  
* Business interruption from chronic and acute hazards  
* Equipment degradation and useful life impairment  
* Catastrophic event impact assessment  
* Uncertainty quantification and validation

# **OBJECTIVE**

Assess potential impairment to Net Asset Value, Useful Life, and Asset Performance of infrastructure assets to help:

* Equity investors assess equity returns under climate risk  
* Lenders assess Loan-to-Value ratios and credit risk  
* Asset owners optimize resilience investments  
* Stakeholders meet TCFD disclosure requirements

# **ANALYTICAL FRAMEWORK OVERVIEW**

The following flowchart illustrates the complete framework, showing data inputs, analytical processes, interim outputs, and the final NAV impairment calculation.

**Figure 1: Climate Risk Assessment Framework Flow**

| DATA INPUTS • CMIP6 Climate Projections (RCP4.5, RCP8.5) • Historical Weather Data (Ground Stations) • Asset Specifications (Capacity, Location, Technology) • InfraSure Performance Models & BI Estimates |
| ----- |

↓

| STEP 1: CLIMATE VARIABILITY ANALYSIS Process: • Downscale CMIP6 data to asset locations • Calculate Severe Climate Variability Ratings (SCVR) • Analyze heat waves, cold waves, freeze events, precipitation extremes, wind patterns, dry spells Output: → SCVR Tables (2025-2050, monthly Years 1-5, annual Years 6-50) |
| ----- |

↓

| STEP 2: ASSET PERFORMANCE MODELING Process: • Generate solar irradiation & wind speed data • Run InfraSure performance models for Base & Climate Scenarios • Apply climate zone-specific factors (arid/semi-arid) Output: → Revenue Projections (Base Scenario with P10/P50/P90 envelopes) |
| ----- |

↓

| STEP 3: BUSINESS INTERRUPTION A. Develop HCR Tables • Map hazard risk to SCVR • Flood, hail, icing, dust, wildfire B. Calculate BI Losses *BI \= InfraSure\_BI × HCR* (InfraSure BI already scaled by SCVR) C. Catastrophic Events • Frequency × severity modeling Output: → BI Revenue Losses → Cat Event Losses |  | STEP 4: EQUIPMENT DEGRADATION A. Develop EFR Tables • Climate zone-specific models • Asset-type mechanisms B. Solar Degradation • Heat, humidity, UV, soiling • Freeze-thaw cycling C. Wind Degradation • Icing (rime & glaze) • Blade erosion, fatigue Output: → Impaired Useful Life (IUL) → Degradation Losses |
| ----- | :---- | ----- |

↓

| STEP 5: NAV IMPAIRMENT CALCULATION *Asset Performance (Climate) \= Revenue\_base \- BI\_loss \- Cat\_loss \- Degradation\_loss* *NPV\_Climate \= Σ \[Asset Performance\_t / (1+WACC)^t\] over IUL* *NPV\_Base \= Σ \[Revenue\_base\_t / (1+WACC)^t\] over EUL* Uncertainty Quantification: • Monte Carlo simulations (1000+ iterations) • Sensitivity analysis on key parameters • Validation against benchmarks |
| ----- |

↓

| FINAL OUTPUT NAV Impairment Ratio \= NPV\_Climate / NPV\_Base *With P10/P50/P90 Confidence Intervals* Supporting Outputs: Loan-to-Value Impact • Equity Return Projections • TCFD Disclosure Metrics |
| :---: |

# **DETAILED ANALYTICAL FRAMEWORK**

## **Core NAV Impairment Calculation**

For a given Climate Scenario, the Net Asset Value (NAV) Impairment Ratio is defined as:

NAV Impairment Ratio \= NPV(IUL, Climate Scenario) / NPV(EUL, Base Scenario)

## **Asset Performance Model**

Asset Performance under climate scenarios is calculated as:

*AP \= Revenue\_base \- BI\_loss \- Cat\_loss \- Degradation\_loss*

Where:

* **Revenue\_base**: Average of projected revenue simulations from InfraSure's asset-specific performance models across all ensembles  
* **BI\_loss**: Business Interruption loss \= Σ(InfraSure\_BI × HCR) across all non-catastrophic hazards. InfraSure BI estimates already incorporate increased outage frequency through SCVR scaling.  
* **Cat\_loss**: Catastrophic event losses \= Σ(Event\_Frequency × Event\_Severity × Duration) for hurricanes, extreme ice storms, and wildfires  
* **Degradation\_loss**: Revenue loss from accelerated equipment degradation due to climate stress

## **Impaired Useful Life Calculation**

Impaired Useful Life (IUL) accounts for accelerated equipment failure:

*IUL \= EUL × \[1 \- Σ(EFR\_i × SCVR\_i)\] × \[1 \- Cat\_Damage\_Factor\]*

This formulation accounts for both chronic climate stress (via EFR and SCVR) and catastrophic damage impacts on asset lifespan.

# **FRAMEWORK ASSUMPTIONS AND PARAMETERS**

## **Asset Specifications**

* **Asset Types:** Utility-scale, grid-connected, contracted PV Solar and Wind Turbine assets  
* **Expected Useful Life (EUL):** 25 years for Solar PV, 35 years for Wind Turbines  
* **Discount Rate:** 10% annual (Weighted Average Cost of Capital \- WACC)  
* **Pilot Sample Sites:**

   \- Hayhurst Texas Solar: Culberson County, TX (24.8 MW, 31.82°N, \-104.09°W)  
   \- Maverick Creek Wind: Concho County, TX (491.6 MW, 31.26°N, \-99.84°W)

## **Climate Data Specifications**

* **Climate Model Framework:** CMIP6 (Coupled Model Intercomparison Project Phase 6\)  
* **Scenarios:** RCP4.5 (moderate emissions) and RCP8.5 (high emissions)  
* **Downscaling Method:** Perfect-prognosis statistical downscaling using Random Forest or Quantile Regression Forest  
* **Temporal Resolution:** Monthly timesteps for Years 1-5 (validation period), Annual timesteps for Years 6-50  
* **Validation:** Cross-validated against NOAA ground station observations in Culberson and Concho Counties, Texas (2000-2024)

## **Scope \- Included in Analysis**

* Climate variability impacts (chronic stress)  
* Business interruption from increased hazard frequency  
* Catastrophic events (simplified methodology using historical frequency × climate multipliers)  
* Equipment degradation and accelerated aging  
* Useful life impairment  
* Energy drought periods (extended low generation)  
* Uncertainty quantification via Monte Carlo simulation

## **Scope \- Excluded from Analysis**

The following elements are deferred to Phase 1 implementation:

* Physical damage repair costs and capital expenditure  
* Market price impacts from regional climate-driven supply changes  
* Operating and maintenance expense escalation beyond implicit degradation  
* Grid interdependency and transmission network resilience modeling  
* Adaptation investment scenarios and resilience measures  
* Transition risk (policy changes, technology shifts, market evolution)

# **IMPLEMENTATION WORK PLAN**

**Timeline:** 3 weeks

## **WEEK 1: Climate Data & Variability Analysis**

### **Step 1A: Climate Scenario Data Acquisition (Days 1-2)**

**Objectives:**

* Acquire CMIP6 ensemble data for RCP4.5 and RCP8.5 scenarios  
* Extract trends and variability for temperature, precipitation, wind, relative humidity  
* Validate model outputs against Texas ground station historical data (2000-2024)

**Data Sources:**

* Primary: LLNL AIMS portal (https://aims2.llnl.gov/search) for CMIP6 datasets  
* Validation: NOAA ground stations in Culberson County and Concho County, TX  
* Supplementary: World Bank Climate Knowledge Portal for regional context

**Deliverables:**

* Raw ensemble datasets (2025-2050, monthly resolution for Years 1-5, annual for Years 6-50)  
* Validation report comparing historical model outputs vs observed data  
* Quality assurance documentation

### **Step 1B: Severe Climate Variability Rating (SCVR) Calculation (Days 3-5)**

SCVR measures the increase in area under exceedance curves for each climate variable. The framework analyzes:

| Climate Variable | Calculation Method |
| :---- | :---- |
| Heat Waves | 3+ consecutive days with T\_max and T\_min \> 90th percentile baseline |
| Cold Waves | 3+ consecutive days with T\_max and T\_min \< 10th percentile baseline |
| Freeze/Frost Events | Days with T\_min \< 0°C (Frost) or T\_max \< 0°C (Icing) |
| Extreme Precipitation | 5-day maximum rolling precipitation sums |
| Dry Spells | Maximum consecutive days with precipitation \= 0 (soiling indicator) |
| Wind Extremes | Daily mean wind speed as proxy for storm intensity, cut-out frequency |
| Energy Droughts | Multi-week periods with generation \< 50% of historical average |
| Wildfire Risk | Fire Weather Index using T\_max, RH\_mean, wind, precipitation |

**Deliverables:**

* SCVR tables for RCP4.5 and RCP8.5 (2025-2050, monthly Years 1-5, annual Years 6-50)  
* Time-series graphs showing evolution of each climate variable  
* Exceedance probability curves comparing base vs future scenarios  
* Energy drought frequency and duration analysis

## **WEEK 2: Asset Performance & Risk Modeling**

### **Step 2: Asset Performance Simulation (Days 6-8)**

**Workflow:**

* Generate solar irradiation and wind speed data using InfraSure Climate Simulation engine  
* Execute InfraSure asset performance models for Base Scenario and Climate Scenarios  
* Incorporate S2S climate forecasts for Years 1-3 (monthly granularity)  
* Apply climate zone-specific degradation factors

**Climate Zone Classification:**

* **Culberson County (Solar):** Arid/Desert \- high irradiation, extreme temperature swings, dust soiling  
* **Concho County (Wind):** Semi-arid transitional \- moderate humidity, mixed icing risk

**Deliverables:**

* Revenue projections with P10/P50/P90 envelopes for full asset life  
* Comparative graphs: Base vs RCP4.5 vs RCP8.5  
* Monthly performance profiles for Years 1-3  
* Energy generation duration curves

### **Step 3: Business Interruption & Hazard Modeling (Days 9-11)**

**3A: Hazard Change Ratio (HCR) Table Development**

HCR quantifies percentage increase in hazard frequency/severity as a function of SCVR:

| Hazard | SCVR Dependencies | Impact |
| :---- | :---- | :---- |
| Pluvial Flood | f(Precip\_SCVR) | Moderate |
| Hail | f(Temp\_SCVR, Wind\_SCVR) | High |
| Icing \- Rime | f(Freeze\_SCVR, RH\_high) | 20-40% loss |
| Icing \- Glaze | f(Freeze\_SCVR, Precip\_SCVR) | 40-80% loss |
| Dust Storms | f(DrySpell\_SCVR, Wind\_SCVR) | Soiling |
| Wildfire | f(Fire Weather Index) | Variable |

**3B: Business Interruption Calculation**

InfraSure BI estimates already incorporate increased outage frequency through SCVR scaling. The calculation is:

*BI\_loss \= Σ (InfraSure\_BI × HCR) across all hazards*

**3C: Catastrophic Event Modeling**

Simplified methodology using historical frequency × climate multipliers:

* **Hurricane/Severe Storm:** Historical Texas frequency (2000-2024) × Wind\_SCVR × Regional exposure  
* **Extreme Ice Storm:** 1-in-10 year event × ColdWave\_SCVR (Texas 2021 analog)  
* **Wildfire:** Fire Weather Index × proximity buffer analysis

**Deliverables:**

* HCR tables for all hazards (2025-2050)  
* BI revenue loss projections by hazard type  
* Catastrophic event probability matrices  
* Time-series graphs of total losses

## **WEEK 3: Equipment Degradation & NAV Analysis**

### **Step 4: Equipment Degradation Modeling (Days 12-14)**

**4A: Solar PV Degradation (Climate Zone Specific)**

| Mechanism | Model & Culberson TX Impact |
| :---- | :---- |
| Heat Loss | Temp Coefficient: P \= P\_rated × \[1 \+ γ(T\_cell \- 25°C)\], γ \= \-0.0045/°C |
| Humidity/Heat Aging | Peck's Model: η \= exp(γ0 \+ γ1×ln(RH) \+ γ2/T\_mod), moderate (low humidity) |
| Freeze-Thaw | Coffin-Manson: N\_f \= C × (Δε\_p)^(-k), moderate impact |
| UV \+ Heat | Encapsulant discoloration rate, HIGH (desert UV intensity) |
| Soiling | f(DrySpell\_days, Wind\_speed), HIGH (West Texas dust) |
| **Composite Annual** | **Typical: 0.5-0.8%/year → Projected: 1.2-1.8%/year** |

**4B: Wind Turbine Degradation**

| Mechanism | Model & Concho TX Impact |
| :---- | :---- |
| Rime Icing | 20-40% power loss, moderate frequency/short duration |
| Glaze Icing | 40-80% power loss, low frequency/HIGH impact (2021-type events) |
| Blade Erosion | Progressive roughness, cumulative 5-7% AEP loss over 20 years |
| Structural Fatigue | Palmgren-Miner: D \= Σ(n\_i/N\_i), variable wind increases cycles |
| Extreme Wind Cut-out | If Wind\>25 m/s: P=0, increasing frequency under climate scenarios |

**Deliverables:**

* EFR tables for solar and wind with climate zone adjustments  
* Calculated IUL for each climate scenario  
* Degradation curves showing efficiency decline  
* Comparative analysis across scenarios

### **Step 5: NAV Impairment Analysis & Validation (Days 15-18)**

**5A: NAV Calculations**

* Compute NPV for Base Scenario (EUL, base performance)  
* Compute NPV for Climate Scenarios (IUL, all loss components)  
* Calculate NAV Impairment Ratios  
* Sensitivity analysis on WACC (8%, 10%, 12%)

**5B: Uncertainty Quantification**

Monte Carlo simulations (1000+ iterations) varying:

* HCR values (±20% range)  
* EFR values (±15% range)  
* Catastrophic event frequencies

**5C: Validation**

* Compare projections against actual performance data (if available)  
* Benchmark against industry reports (NREL, IEA)  
* Cross-validate SCVR calculations

**Final Deliverables:**

* NAV Impairment Ratios with P10/P50/P90 confidence intervals  
* Loan-to-Value impact tables  
* Equity return projections  
* Sensitivity tornado charts  
* Validation report  
* Executive dashboard visualizations

# **APPENDIX: SCIENTIFIC REFERENCES**

## **Climate Data Standards**

* CMIP6 Multi-Model Ensemble: Provides improved representation of climate processes over CMIP5  
* Copernicus Heat/Cold Wave Index methodology for extreme temperature identification  
* Climpact indices for precipitation and temperature extremes

## **Degradation Models \- Solar PV**

* Temperature Coefficient Model: Standard manufacturer specification (γ \= \-0.003 to \-0.005/°C)  
* Peck's Aging Model: Quantifies humidity and temperature accelerated degradation  
* Coffin-Manson Model: Mechanical fatigue from thermal cycling  
* Climate zone degradation rates: Arid/desert 1.2-1.8%/yr vs typical 0.5-0.8%/yr

## **Degradation Models \- Wind Turbines**

* Icing Power Loss Models: Rime (20-40% loss) vs Glaze (40-80% loss)  
* Palmgren-Miner Rule: Cumulative fatigue damage from variable wind stress  
* Cut-out Logic: Turbine shutdown at wind speeds \>25 m/s  
* Blade Leading Edge Erosion: Progressive roughness causing 5-7% AEP loss over 20 years

## **Framework Alignment**

* **TCFD (Task Force on Climate-related Financial Disclosures):** Framework outputs support physical risk disclosure requirements  
* **PCRAM 2.0 (Physical Climate Risk Appraisal Methodology):** Standardized approach for infrastructure asset assessment  
* **Asset-Level Analysis:** Site-specific assessment rather than headquarter-based proxies

— END OF DOCUMENT —