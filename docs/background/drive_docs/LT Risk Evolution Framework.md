**Initial Pilot Framework and Work Plan**

**Goal**: 

Assess potential impairment to Net Asset Value, Useful Life and Asset Performance of infrastructure assets to help i) equity investors assess equity returns and ii) lenders assess Loan-To-Value, under various long-term Climate Scenarios.

**Framework**: 

For a given Climate Scenario:

Net Asset Value (NAV) Impairment Ratio would be defined as the ratio of:  
i) NPV of Asset Performance over the Impaired Useful Life (IUL) in Climate Scenario, to   
ii) NPV of Asset Performance over the Expected Useful Life (EUL) in Base Scenario.

Where, 

Asset Performance would be:  
i) Average of projected revenue simulations from InfraSure’s asset-specific performance models for all the ensembles, *LESS*,   
ii) Revenues lost from interruption from Forced Outages and Recovery Period (Business Interruption) across all \[non-Cat\] hazards. For each hazard, this is calculated as the product of InfraSure BI estimates for the asset and Hazard Change Ratio (refer to HCR Table definition).

Impaired Useful Life is defined as the product of,   
i) EUL,  
ii) % increase in Severe Climate Variability Rating  across temperature, precipitation, and winds \[outside equipment’s defined tolerance range\], and   
iii) asset-type/climate-variable specific Equipment Failure Ratio (refer to EFR Table definition).

**Assumptions**:

The following assumptions and parameters are used for the Initial Pilot, with further improvements in Phase 1 implementation.

* Focus on utility-scale, grid-connected, contracted PV Solar and Wind Turbine assets  
* \[10%\] is used as the annual discount rate for NPV calculations, representing the Weighted Average Cost of Capital (WACC).   
* Expected Useful Life will be 25 years for Solar and 35 years for Wind  
* Expected Performance will be the Revenues estimated by the InfraSure asset-specific performance models for the Base Scenario under the CORDEX down-scaled CMIP5 framework.  
* Sample sites:  
  * Hayhurst Texas Solar Culberson, TX Capacity (MW) 24.8 31.815992 \-104.0853  
  * Maverick Creek Wind Concho, TX Capacity (MW) 491.6 31.262546 \-99.84396  
* Not included in Pilot Phase:  
  * Impact of physical damages due to increased hazards, only increased business interruption and increased equipment failure.   
  * Impact of increase in catastrophic hazard events (such as, hurricane, wildfire)  
  * Impact on market prices from climate variability and hazards is not incorporated.  
  * Impact of operating and maintenance capex expenses is not incorporated.

 

**Initial Pilot Work Plan** (2 weeks)

Step1

* Pull all ensembles for a given Climate Scenario, including all variable, both trends and variability ([https://climateknowledgeportal.worldbank.org/country/united-states/trends-variability-projections](https://climateknowledgeportal.worldbank.org/country/united-states/trends-variability-projections))  
  (https://aims2.llnl.gov/search)  
* Compute increased Severe Climate Variability Rating (SCVR defined as the increase in the area under the exceedance curves) in temperature, winds, heat wave, precipitation, severe winds.


| RCP4.5 | 2030 | 2031 | …. | 2040 | …. | 2050 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Temp SCVR |  |  |  |  |  |  |
| Wind SCVR |  |  |  |  |  |  |
| …… |  |  |  |  |  |  |


* Display graphs and tables showing annual evolution of these SCVR and Climate variables

Step 2:

* Use InfraSure Climate Simulation engine to generate missing climate variables (solar irradiation and wind speeds) required to estimate asset performance  
* Call InfraSure asset performance model to generate simulations of Asset Performance in given Climate Scenario and Base Scenario  
* Display graphs and tables showing Asset Performance in Base and given Climate Scenario for Expected Asset Life with P10/90 envelope, with first 3 years being performance output from the boot-strapped S2S climate forecasts

Step 3:

* Develop the HCR Table based on review of published research and internal discussions. For a given hazard, HCR is the percentage increase in hazard risk derived as a function of relevant SCVRs. For example, Flood HCR in a given year would be a function of precipitation SCVR in that year.


| RCP4.5 | 2030 | 2031 | …. | 2040 | …. | 2050 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Pluvial Flood |  |  |  |  |  |  |
| Hail |  |  |  |  |  |  |
| …… |  |  |  |  |  |  |


* Using the InfraSure BI estimates and the HCR values compute the revenues lost in a given Climate Scenario  
* Display graphs and tables showing revenues lost in Base and given Climate Scenarios, with first 3 years being base BI estimates

Step 4:

* Develop the EFR Table based on review of published research and internal discussions. For a given Climate Variable, for a given year, EFR is the percentage decrease for a given Asset Type in Asset Life for a percentage increase in SCVR


| PV Solar | 2030 | 2031 | …. | 2040 | …. | 2050 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Temp Extreme Impact |  |  |  |  |  |  |
| Precip Extreme |  |  |  |  |  |  |
| …… |  |  |  |  |  |  |


* Compute the average of the product of EFR and SCVR across all years, and sum of the averages across all Climate Variables to estimate the IUL  
* Display table or graph of the EUL and IUL.

**Appendix 1: HCR Derivations**

[Climate Conditions](https://docs.google.com/spreadsheets/d/1Th6guC5Nv6_uC4PxwmQJ_sOcL1429s1DdcIVWW39IBM/edit?gid=0#gid=0): Scientific derivation of risk metrics

| Climate Condition | Doable? | Logic / Definition |
| :---- | :---- | :---- |
| **Heat Wave** | Yes | 3+ consecutive days where T\_max and T\_min exceed the 90th percentile of the historical baseline. [https://drought.emergency.copernicus.eu/data/factsheets/factsheet\_heatColdWaveIndex\_gdo.pdf](https://drought.emergency.copernicus.eu/data/factsheets/factsheet_heatColdWaveIndex_gdo.pdf) |
| **Cold Wave** | Yes | 3+ consecutive days where T\_max and T\_min fall below the 10th percentile of the historical baseline. [https://drought.emergency.copernicus.eu/data/factsheets/factsheet\_heatColdWaveIndex\_gdo.pdf](https://drought.emergency.copernicus.eu/data/factsheets/factsheet_heatColdWaveIndex_gdo.pdf) |
| **Freeze / Frost** | Yes | Count of days where T\_min \< 0 celsius (Frost Days) or T\_max \< 0 celsius C (Icing Days) [https://climpact-sci.org/indices/](https://climpact-sci.org/indices/) |
| **Cumulative Precip.** | Yes | Simple rolling sum of precipitation\_sum over specific windows (e.g., 5-day max or annual). [https://climpact-sci.org/indices/](https://climpact-sci.org/indices/) |
| **Wind (Avg Sustained)** | Yes	 | Directly available via wind\_speed\_10m\_mean. |
| **Wind (Extreme)** | As a Proxy, yes | Use daily mean as a proxy for storm intensity. [https://pmc.ncbi.nlm.nih.gov/articles/PMC12586526/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12586526/) |
| **Wildfire** | As a Proxy, yes | Doable as a proxy Fire Weather Index (FWI) using daily T\_max, Relative Humidity\_mean, wind, and P\_sum [https://pmc.ncbi.nlm.nih.gov/articles/PMC11737286/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11737286/) |

* *Other possible climate conditions that can be derived by current variables*

| Tropical Nights |  | Days where T\_min \> 20C |
| :---- | :---- | :---- |
| **Summer Days** |  | Days where T\_max \> 25 C (the efficiency drop-off threshold for solar) |
| **Cooling/Heating Degree days** |  | Comparing T\_mean to $18.33C to estimate internal building/substation cooling needs |
| **Dry Spells** |  | Maximum consecutive days with P\_sum \= 0 (indicator for wildfire fuel drying and solar soiling) |

* *Climate conditions that we are interested but may need additional Variables needed to define climate conditions (quantitatively, not as a proxy)*

| Wind (Extreme) |  | Wind Gust Speed (maximum instantaneous wind) and Wind Direction (to model wake effects and structural loading). |
| :---- | :---- | :---- |
| **Wildfire** |  | Vapor Pressure Deficit (VPD), Soil Moisture, and Fuel Load data (vegetation density). |

**Appendix 2: EFR Derivations**

1) **Heat Waves → Instantaneous Efficiency Loss (Temperature Coefficient Model) \*but need future irradiance**  
   During heat waves, elevated cell temperatures reduce the instantaneous power output of photovoltaic modules. The Heat Wave Index (e.g., Q90 exceedance of ambient temperature) is used to estimate the PV cell temperature (T\_cell), which feeds directly into the standard temperature coefficient model provided by manufacturers.

P\_actual \= P\_rated × \[1 \+ γ × (T\_cell − T\_ref)\]

Where:

* P\_actual \= actual PV power output (W)  
* P\_rated \= rated power at standard test conditions (STC)  
* γ \= temperature coefficient of power (typically −0.003 to −0.005 per °C)  
* T\_cell \= PV cell temperature (°C), derived from heat wave conditions  
* T\_ref \= reference temperature (usually 25 °C)

Interpretation:  As T\_cell rises above 25 °C during heat waves, the term γ × (T\_cell − T\_ref) becomes negative, reducing power output proportionally.

[https://www.greentechrenewables.com/article/how-does-heat-affect-solar-panel-efficiencies](https://www.greentechrenewables.com/article/how-does-heat-affect-solar-panel-efficiencies)

2) Heat \+ Humidity → Long-Term Degradation (Peck’s Aging Model)

Concept:  Chronic exposure to high temperatures and humidity (e.g., “Tropical Nights” combined with high mean relative humidity) accelerates chemical degradation within PV modules. Peck’s model quantifies this accelerated aging.

η \= exp(γ0 \+ γ1 × ln(hr) \+ γ2 / T\_mod)

Where:

* η \= aging acceleration factor (dimensionless)  
* hr \= relative humidity (%)  
* T\_mod \= module temperature in Kelvin (K)  
  γ0, γ1, γ2 \= empirically derived material constants

Interpretation:  Higher humidity and higher temperatures increase η, meaning that each year of operation causes more degradation than under standard conditions.

[https://www.scirp.org/journal/paperinformation?paperid=135596](https://www.scirp.org/journal/paperinformation?paperid=135596)

3) Freeze/Thaw Cycles → Mechanical Fatigue (Coffin–Manson Model)

Repeated transitions between freezing temperatures and warm daytime conditions induce thermal expansion and contraction. This causes mechanical fatigue in silicon cells and solder joints, eventually leading to microcracks.

N\_f \= C × (Δε\_p)^(-k)

Where:

* N\_f \= number of cycles to failure  
  C, k \= material-specific constants  
* Δε\_p \= plastic strain amplitude caused by temperature cycling

Climate linkage

* Freeze events: T\_min \< 0 °C

* Summer days: T\_max \> 25 °C

The frequency of these transitions determines how quickly fatigue damage accumulates.

[https://www.researchgate.net/publication/387854525\_Quantification\_of\_the\_impact\_of\_irradiance\_heat\_humidity\_and\_cyclic\_temperature\_on\_the\_aging\_of\_photovoltaic\_panels\_a\_case\_study\_in\_Algeria](https://www.researchgate.net/publication/387854525_Quantification_of_the_impact_of_irradiance_heat_humidity_and_cyclic_temperature_on_the_aging_of_photovoltaic_panels_a_case_study_in_Algeria)

**Wind**

1) Icing Conditions → Aerodynamic Power Loss

Concept:  When temperatures drop below freezing and humidity is high, ice accretes on turbine blades, degrading aerodynamic performance and increasing drag.

Condition Definition:

Icing Event if: T \< 0 °C AND RH \> 75%

P\_iced \= P\_normal × (1 − L\_ice)

Where:

* P\_iced \= power during icing

* P\_normal \= power from the standard power curve

* L\_ice \= icing loss factor (0.2 to 0.8)

Interpretation:  Severe icing can reduce power output by up to 80% during the event.

[https://pmc.ncbi.nlm.nih.gov/articles/PMC8545448/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8545448/)

2) Wind Speed Distribution → Structural Fatigue (Palmgren–Miner Rule)

**Concept**  
 Turbine components experience fatigue damage from repeated stress cycles driven by fluctuating wind speeds. By binning wind speeds into 10-minute intervals, cumulative fatigue damage can be estimated.

D \= Σ (n\_i / N\_i)

**Where:**

* D \= cumulative fatigue damage  
* n\_i \= number of load cycles at stress level i  
* N\_i \= number of cycles to failure at stress level i

**Interpretation**  
 When D ≥ 1, the component has reached its fatigue life. Higher wind variability accelerates damage accumulation.

[https://wes.copernicus.org/articles/9/799/2024/](https://wes.copernicus.org/articles/9/799/2024/)

3) Extreme Wind → Cut-Out Logic (Lost Energy Production)

**Concept**  
 To prevent catastrophic failure, wind turbines shut down when wind speeds exceed the cut-out threshold (typically around 25 m/s).

**Deterministic Power Equation:** 

If Wind\_mean \> 25 m/s, then Power \= 0

**Annual Energy Loss Calculation:**

AEP\_loss \= Σ (P\_expected × Δt) for Wind\_mean \> 25 m/s

**Where:**

* AEP\_loss \= annual energy production loss

* P\_expected \= power that would have been generated without cut-out

* Δt \= duration of extreme wind exceedance

Extreme wind events cause direct, quantifiable production losses even though they protect turbine integrity.

[https://pmc.ncbi.nlm.nih.gov/articles/PMC8545448/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8545448/)

