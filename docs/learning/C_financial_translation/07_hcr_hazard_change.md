# HCR — Hazard Change Ratio
 
**HCR translates a climate distribution shift (SCVR) into a hazard-specific impact ratio.** It answers: *"If the temperature distribution shifted +8%, how many more heat wave days does that produce?"*
 
The answer is not 8%. A small shift in the mean can cause a large change in threshold exceedances — this non-linear amplification is what HCR captures.
 
---
 
## 1. The Simple Version
 
SCVR tells you *"the distribution shifted."* HCR tells you *"that shift created this many more hazard events."*
 
```
SCVR says:                                HCR says:
  "tasmax distribution area               "that means 21% more heat wave days,
   grew 8.4%"                              13% more tropical nights, and
                                            a Fire Weather Index increase of 15%"
 
  It's a single number about              It's a per-hazard number that connects
  the whole distribution.                  to specific damage mechanisms.
```
 
**Why the multiplier isn't 1.0:**
 
```
Temperature (°C)
    ▲
 45 │                                    ╭─── Future
    │                               ╭────╯
 43 │─ ─ ─ ─ ─ ─ ─THRESHOLD─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─ ─ ─
    │                          ╭────╯  ╭─── Baseline
 41 │                     ╭────╯  ╭────╯
    │                ╭────╯  ╭────╯
 39 │           ╭────╯  ╭────╯
    │      ╭────╯  ╭────╯
 37 │ ╭────╯  ╭────╯
    │─╯  ╭────╯
 35 │────╯
    └──────────────────────────────────────────►
       0%     5%     10%    15%    20%    25%
                  Exceedance probability
 
  Baseline days above threshold: ████         (~8% of days)
  Future days above threshold:   ████████████  (~19% of days)
 
  Distribution shifted ~8% (SCVR) but days above threshold
  increased ~140% — a 2.5× amplification.
 
  This is the non-linear tail effect that HCR captures.
```
 
A small mean shift pushes more days past a fixed threshold because the tail of the distribution is thin — many values are clustered just below the threshold, and a small nudge moves them above it.
 
**Annual framing:** HCR is computed **per year**, not per epoch. As SCVR(t) evolves year by year, HCR(t) tracks it:
 
```
Year:    2030   2031   2032   ...   2040   ...   2050
SCVR(t): 0.03   0.03   0.04  ...   0.07   ...   0.12
HCR(t):  0.08   0.08   0.10  ...   0.18   ...   0.30
         ^^^^                       ^^^^         ^^^^
         small                     moderate      large
```
 
Each year's HCR maps directly to that year's cash flow adjustment in the CFADS model.
 
---
 
## 2. Variables vs Hazards — The Mapping
 
Climate variables are **measurements**. Hazards are **damage events**.
 
```
MEASUREMENTS                        DAMAGE EVENTS
(what the models output)            (what breaks equipment)
─────────────────────               ────────────────────────
 
  tasmax (°C)  ─────────────────►  Heat Wave
               ─────────────────►  Summer Days (>25°C)
 
  tasmin (°C)  ─────────────────►  Frost Days (tasmin < 0°C)
               ─────────────────►  Cold Wave
               ─────────────────►  Tropical Nights (>20°C)
 
  tasmax + tasmin ──────────────►  Heat Wave             ← COMPOUND: both required
  (BOTH variables required)        (tasmax > P90 AND tasmin > P90, 3+ consecutive days)
 
  tasmax + tasmin ──────────────►  Cold Wave             ← COMPOUND: both required
  (BOTH variables required)        (tasmax < P10 AND tasmin < P10, 3+ consecutive days)
 
  tasmax + tasmin ──────────────►  Freeze-Thaw Cycles
                                   (tasmin < 0 AND tasmax > 0)
 
  tas (°C)     ─────────────────►  Cooling/Heating Degree Days
 
  pr (mm/day)  ─────────────────►  Extreme Precipitation (Rx5day)
               ─────────────────►  Dry Spells (consecutive pr < 1mm)  ← threshold is <1mm, not =0
 
  sfcWind (m/s) ────────────────►  Extreme Wind Events
                ────────────────►  Cut-Out Events (>25 m/s)
 
  hurs (%)     ─────────────────►  Humidity Stress
 
  tasmax + hurs + sfcWind + pr ─►  Fire Weather Index (FWI)   ← tasmax not tas; see note below
 
  tasmin + hurs ────────────────►  Icing Conditions
                                   (T < 0°C AND RH > 90%)     ← corrected from 75%; see note below
```
 
> **Note on FWI temperature input:** The Canadian FWI system uses noon temperature because
> that is when fire danger peaks. `tasmax` (daily maximum) is a much closer approximation
> to noon conditions than `tas` (daily mean). Using `tas` systematically underestimates fire
> danger. All FWI computations in this framework use `tasmax` as the temperature input.
> Source: Van Wagner (1987), Canadian Forestry Service.
 
> **Note on Icing RH threshold:** The 75% threshold used in earlier versions of this document
> is too low. Meaningful blade icing (supercooled droplet accretion) requires near-saturated
> conditions. IEC 61400-1 (wind turbine design standard) and wind energy industry practice
> use RH ≥ 90% as the threshold for icing-relevant conditions. Using 75% systematically
> overstates icing event frequency and inflates the negative HCR benefit from warming.
 
### Hazard Definitions — From Team Framework
 
These definitions are drawn from the team's [LT Risk Evolution Framework](../background/drive_docs/LT%20Risk%20Evolution%20Framework.md) Appendix 1, with literature sources noted.
 
| Hazard | Definition | Source Variables | Literature |
|--------|-----------|-----------------|------------|
| **Heat Wave** | 3+ consecutive days where T_max **AND** T_min **both** exceed the 90th percentile of the historical baseline | tasmax **AND** tasmin (compound) | Copernicus EDO factsheet |
| **Cold Wave** | 3+ consecutive days where T_max **AND** T_min **both** fall below the 10th percentile of the historical baseline | tasmax **AND** tasmin (compound) | Copernicus EDO factsheet |
| **Frost Days** | Days where T_min < 0°C | tasmin | ClimPACT indices |
| **Icing Days** | Days where T_max < 0°C | tasmax | ClimPACT indices |
| **Extreme Precip** | Maximum rolling 5-day precipitation total (Rx5day) | pr | ClimPACT indices |
| **Dry Spell** | Maximum consecutive days with **pr < 1mm** *(corrected from pr = 0; climate models rarely produce exact zero)* | pr | WMO / ClimPACT standard |
| **Wind Extreme** | Daily mean as proxy for storm intensity | sfcWind | PMC/12586526 |
| **Wildfire (FWI)** | Fire Weather Index = f(**T_max**, RH, wind, pr) *(corrected: tasmax not tas)* | **tasmax**, hurs, sfcWind, pr | PMC/11737286; Van Wagner (1987) |
| **Icing Conditions** | T < 0°C AND **RH > 90%** *(corrected from 75%; IEC 61400-1 standard for blade icing)* | tasmin, hurs | IEC 61400-1; (compound) |
 
### Additional Indices (Derivable from Current Variables)
 
| Index | Definition | Use Case |
|-------|-----------|----------|
| Tropical Nights | Days where T_min > 20°C | Peck's aging — no nighttime relief |
| Summer Days | Days where T_max > 25°C | Solar efficiency drop-off threshold |
| Cooling Degree Days | Σ max(0, T_mean − 18.33°C) | Substation/inverter cooling loads |
| Heating Degree Days | Σ max(0, 18.33°C − T_mean) | Facility heating costs |
| Dry Spells | Max consecutive days with **pr < 1mm** *(corrected from pr = 0)* | Wildfire fuel drying, solar soiling |
 
### What's Directly Computable vs Proxy
 
```
DIRECTLY COMPUTABLE (from NEX-GDDP daily data):
  ✓ Heat wave days      ✓ Frost days       ✓ Tropical nights
  ✓ Summer days         ✓ Icing days       ✓ Dry spell length (pr < 1mm)
  ✓ Rx5day              ✓ CDD/HDD         ✓ Wind cut-out events (proxy)
  ✓ FWI (using simplified Canadian FWI with tasmax)
  ✓ Cold wave days      ✓ Freeze-thaw cycles
 
PROXY ONLY (need variables not in NEX-GDDP):
  ~ Wind gusts (have daily mean, not instantaneous max)
  ~ SCS / Hail / Tornado (no CAPE or wind shear in NEX-GDDP — surface proxy only)
  ~ Wildfire (full FWI needs VPD, soil moisture, fuel load)
  ~ Ice Storm (requires vertical temperature profile, not available in NEX-GDDP)
 
NOT AVAILABLE:
  ✗ Lightning frequency
  ✗ Tornado events (CAPE and SRH unavailable)
  ✗ Coastal flooding / storm surge (sea level, SST unavailable)
  ✗ Hurricane (SST, upper-air profiles unavailable)
  ✗ Earthquake (not a climate hazard — HCR = 0)
```
 
**NB01 already computes many of these.** The annual climate indices in Notebook 01 — `heat_wave_days`, `frost_days`, `rx5day`, `fwi_mean` — are exactly the hazard counts that HCR measures. NB04 should build on this existing infrastructure.
 
---
 
## 2B. Company Hazard Definitions — Quantitative Equations
 
> **Scope note:** The company's active hazard list for the pilot covers:
> Heat Wave, Cold Wave, Wildfire, Riverine Flooding, Strong Wind, Ice Storm,
> Winter Weather, Severe Convective Storms (SCS), Coastal Flooding, Hurricane,
> Tornado, Earthquake.
>
> Hazards from earlier sections of this document that are **not part of the
> company's active hazard list** (Frost Days, Icing Days, Extreme Precip,
> Dry Spell, Wind Extreme as standalone items, Icing Conditions, Freeze-Thaw
> as standalone items) are retained above for reference and because they feed
> as sub-components into the company hazards listed here.
 
---
 
### NEX-GDDP-CMIP6 Available Variables (reference)
 
All equations below reference only variables available in NEX-GDDP via THREDDS:
 
| Variable | Description | Units |
|---|---|---|
| `tasmax` | Daily maximum near-surface air temperature | K |
| `tasmin` | Daily minimum near-surface air temperature | K |
| `tas` | Daily mean near-surface air temperature | K |
| `pr` | Daily mean precipitation rate | kg m⁻² s⁻¹ → multiply × 86400 for mm/day |
| `sfcWind` | Daily mean near-surface wind speed at 10m | m/s |
| `hurs` | Near-surface relative humidity | % |
| `huss` | Near-surface specific humidity | kg/kg |
| `rsds` | Surface downwelling shortwave radiation | W/m² |
| `rlds` | Surface downwelling longwave radiation | W/m² |
 
**Not available in NEX-GDDP:** pressure-level profiles, CAPE, wind shear, SST, sea level pressure, soil moisture, snow water equivalent, wind gusts, vertical temperature profiles.
 
---
 
### 1. Heat Wave ✅ Fully Computable
 
**NEX-GDDP variables:** `tasmax`, `tasmin`
 
**Relationship type:** Non-linear (threshold exceedance — strongly superlinear in tail)
 
**Equation:**
 
```
Step 1 — Baseline thresholds (computed from 1985-2014, per calendar day ± 15-day window):
  P90_max(doy) = 90th percentile of tasmax across baseline years at that day-of-year
  P90_min(doy) = 90th percentile of tasmin across baseline years at that day-of-year
 
Step 2 — Daily flag:
  HW_flag(d) = 1  if tasmax(d) > P90_max(doy(d))
                  AND tasmin(d) > P90_min(doy(d))
             = 0  otherwise
 
Step 3 — Annual count (only runs of ≥ 3 consecutive flagged days qualify):
  HW_days(year) = Σ HW_flag(d) for d in all runs of ≥ 3 consecutive HW_flag = 1
 
HCR (Pathway B):
  HCR_heatwave = [mean(HW_days, future_period) − mean(HW_days, baseline_period)]
                 / mean(HW_days, baseline_period)
```
 
**Pathway A scaling factor:** 2.0–3.0× SCVR_tasmax (base: 2.5). Derived from tail amplification
at P90: a 0.5σ mean shift nearly doubles exceedances above μ+1σ.
*(Source: Diffenbaugh et al. 2013, PNAS; Cowan et al. 2018, Scientific Reports)*
 
**Quantitative benchmark:** +4 to +34 extra heat wave days per season per 1°C of global warming.
*(Source: Cowan et al. 2018, Scientific Reports)*
 
---
 
### 2. Cold Wave ✅ Fully Computable
 
**NEX-GDDP variables:** `tasmax`, `tasmin`
 
**Relationship type:** Non-linear threshold exceedance (same logic as heat wave, opposite tail).
HCR will be **negative** under warming — fewer cold waves is a financial benefit.
 
**Equation:**
 
```
Step 1 — Baseline thresholds:
  P10_max(doy) = 10th percentile of tasmax at that day-of-year
  P10_min(doy) = 10th percentile of tasmin at that day-of-year
 
Step 2 — Daily flag:
  CW_flag(d) = 1  if tasmax(d) < P10_max(doy(d))
                  AND tasmin(d) < P10_min(doy(d))
             = 0  otherwise
 
Step 3 — Annual count (runs of ≥ 3 consecutive days only):
  CW_days(year) = Σ CW_flag(d) for runs of ≥ 3 consecutive CW_flag = 1
 
HCR (Pathway B):
  HCR_coldwave = [mean(CW_days, future) − mean(CW_days, baseline)]
                 / mean(CW_days, baseline)
  → Expected to be negative (−0.25 to −0.40 by mid-century SSP5-8.5)
```
 
**Pathway A scaling factor:** −0.25 to −0.40 × SCVR_tasmin (beneficial reduction).
*(Source: IPCC AR6 Chapter 11; Linking hydroclimate indices, ScienceDirect 2024)*
 
**Quantitative benchmark:** Cold spell duration index approaches near-zero by 2060 under
SSP5-8.5; ice days reduce by ~90 days by end of century.
*(Source: Linking hydroclimate indices to projected warming, ScienceDirect 2024)*
 
---
 
### 3. Wildfire ✅ Computable as Approximation (Canadian FWI)
 
**NEX-GDDP variables:** `tasmax` (proxy for noon T), `hurs`, `sfcWind`, `pr`
 
**Relationship type:** Non-linear compound (multiplicative interaction of all four variables).
Increasing temperature and drying amplify each other super-additively.
 
**Caveat:** FWI is calibrated for noon observations. Daily NEX-GDDP values introduce
systematic error of 5–10% (overestimate). Flag outputs accordingly.
*(Source: Vitolo et al. 2025, npj Climate and Atmospheric Science)*
 
**Equation (Canadian FWI system, Van Wagner 1987):**
 
```
Daily inputs:
  T(d)   = tasmax(d) − 273.15          [°C]
  H(d)   = hurs(d)                     [%]
  W(d)   = sfcWind(d) × 3.6            [km/h]
  r_0(d) = pr(d) × 86400               [mm/day]
 
FFMC (Fine Fuel Moisture Code — 1-day memory):
  m_0 = 147.2 × (101 − F_0) / (59.5 + F_0)    [yesterday's FFMC → moisture]
  [rain adjustment, drying/wetting to equilibrium moisture, convert back to FFMC]
  → F(d) = 59.5 × (250 − m) / (147.2 + m)
 
ISI (Initial Spread Index — combines wind and FFMC):
  f_W = exp(0.05039 × W)
  f_F = 91.9 × exp(−0.1386 × m) × (1 + m^5.31 / 4.93e7)
  ISI = 0.208 × f_W × f_F
 
DMC, DC → BUI (Build-Up Index):
  BUI = 0.8 × DMC × DC / (DMC + 0.4 × DC)    [if DMC ≤ 0.4 × DC]
 
FWI (Fire Weather Index):
  f_BUI = 0.626 × BUI^0.809 + 2.0             [if BUI ≤ 80]
  S     = 0.1 × ISI × f_BUI
  FWI   = exp(0.987 × ln(S) − 0.450)          [if S > 1]
 
High_FWI_days(year) = count(FWI(d) > threshold)
  [threshold is site-specific; 15–19 = "high", 19–30 = "very high", >30 = "extreme"]
 
HCR (Pathway B):
  HCR_wildfire = [mean(High_FWI_days, future) − mean(High_FWI_days, baseline)]
                 / mean(High_FWI_days, baseline)
```
 
**Quantitative benchmark:** Extreme FWI days increased ~65% globally over 1980–2023; +35%
likelihood of extreme FWI events under 1.3°C warming vs pre-industrial.
*(Source: Vitolo et al. 2025, npj Clim. Atmos. Sci.; World Weather Attribution LA fires 2025)*
 
---
 
### 4. Riverine Flooding ⚠️ Partially Computable
 
**NEX-GDDP variables:** `pr` (precipitation component — computable). Soil moisture and
snowpack — **NOT in NEX-GDDP** (compound component approximable via water balance model).
 
**Relationship type:** Super-linear at the extreme tail (super-Clausius-Clapeyron for
short-duration events); compound amplification with antecedent soil moisture.
 
**Equation — Precipitation component (primary, directly computable):**
 
```
pr_mm(d) = pr(d) × 86400                    [mm/day]
 
Rx5day(year) = max over all d of: Σ pr_mm(i) for i in [d, d+4]
               [rolling 5-day maximum annual precipitation sum]
 
HCR_flood_precip = [mean(Rx5day, future) − mean(Rx5day, baseline)]
                   / mean(Rx5day, baseline)
```
 
**Equation — Soil moisture compound component (approximation via water balance):**
 
```
PET(d) = 0.0023 × (tasmax − tasmin)^0.5 × (tas − 273.15 + 17.8) × Ra(d)
         [Hargreaves PET; Ra = extraterrestrial radiation from latitude + doy]
 
SM(d) = min(SM(d-1) + pr_mm(d) − min(PET(d), SM(d-1) + pr_mm(d)), SM_max)
        [SM_max ≈ 150mm field capacity — site specific]
 
Compound flag:
  Flood_compound(d) = 1 if pr_mm(d) > P95_pr(baseline) AND SM(d-1) > 0.8 × SM_max
```
 
**Pathway A scaling factor:** 1.5–2.0× SCVR_pr (midpoint 1.75). Grounded in
Clausius-Clapeyron: extreme precipitation grows ~7%/°C, but at the 99th percentile
amplification is 2–3× the C-C rate.
*(Source: IPCC AR6 Chapter 11 — high confidence; Tabari 2020, Scientific Reports)*
 
**Quantitative benchmark:** Rx1day increases ~7%/°C globally (Clausius-Clapeyron);
range 4–8%/°C across CMIP6 models. In humid regions: 6.3%/K; semi-arid: 5.5%/K.
*(Source: IPCC AR6 Chapter 11; Tabari 2020, Scientific Reports)*
 
**Note:** 51.6% of global flood events are multi-driver — joint rainfall + antecedent
soil moisture is the dominant compound category. Precipitation-only estimate can underestimate
flood magnitude by up to 2× in soil-saturated conditions.
*(Source: Zscheischler et al. 2024, PMC10971417)*
 
---
 
### 5. Strong Wind ⚠️ Poor Proxy — Daily Mean Only
 
**NEX-GDDP variables:** `sfcWind` (daily mean at 10m). Wind gusts and sub-daily
variability — **NOT in NEX-GDDP**.
 
**Relationship type:** Approximately linear for mean wind changes; non-linear (v²) for
structural loading, but gust data is unavailable.
 
**Critical limitation:** Wind turbine cut-out (typically 25 m/s) is triggered by
instantaneous or 10-minute gust speeds, not daily means. A day with steady 8 m/s mean
can have gusts > 25 m/s during convective events. The daily mean proxy will
systematically underestimate cut-out event frequency.
 
**Equation — Hub-height extrapolation (required before any threshold application):**
 
```
V_hub(d) = sfcWind(d) × ln(z_hub / z_0) / ln(10 / z_0)
           [log profile; z_0 ≈ 0.03m grassland; z_hub ≈ 80–100m]
           → V_hub ≈ sfcWind × 1.36 for 80m hub, open terrain
 
Extreme wind proxy:
  Extreme_days(year) = count(V_hub(d) > V_threshold)
  [V_threshold = 15 m/s daily mean as proxy for gust-prone conditions]
 
HCR_wind = [mean(Extreme_days, future) − mean(Extreme_days, baseline)]
           / mean(Extreme_days, baseline)
```
 
**Gust factor correction (if ERA5 available for the site):**
 
```
G = V_gust_ERA5 / V_mean_ERA5    [historical gust factor; typically 1.5–2.0 open terrain]
V_gust_proxy(d) = V_hub(d) × G
Cut_out_days(year) = count(V_gust_proxy(d) > 25 m/s)
```
 
**At Maverick Creek:** sfcWind SCVR ≈ 0 → wind structural HCR ≈ 0 → Palmgren-Miner
EFR ≈ 0. This is **why wind farms are ~10× less climate-impaired than solar**.
 
**Confidence:** Low for cut-out events. Medium for mean structural loading.
*(Source: HCR document NB03 ensemble output; IEC 61400-1)*
 
---
 
### 6. Ice Storm ⚠️ Poor Proxy — Vertical Temperature Profile Missing
 
**NEX-GDDP variables:** `tasmin`, `tasmax`, `pr`, `hurs`
 
**Relationship type:** Non-linear threshold event. Frequency decreases under warming
for Texas/southern sites (fewer days in the −10 to 0°C surface window).
 
**Limitation:** Full ice storm diagnosis requires a **vertical temperature profile** —
a warm layer (> 0°C) aloft with a sub-freezing surface layer. This is not available
in NEX-GDDP surface variables. The proxy below captures surface conditions only.
 
**Equation — Surface proxy:**
 
```
FRP(d) = 1  if tasmin(d) < 273.15 K       [surface sub-freezing at night]
             AND tasmax(d) > 273.15 K      [above freezing during day: in the transition window]
             AND pr_mm(d) > 0.5            [precipitation present]
             AND hurs(d) > 85%             [near-saturated: warm moist air overhead]
         0  otherwise
 
HCR_icestorm = [mean(FRP_days, future) − mean(FRP_days, baseline)]
               / mean(FRP_days, baseline)
→ Expected to be negative for Texas sites under warming
```
 
**Fallback if precision required:** Use ERA5 pressure-level data to compute the
Bourgouin (2000) precipitation-type algorithm historically, derive a correction factor
for the NEX-GDDP proxy, and apply to future projections.
*(Source: Jeong et al. 2019, NHESS; Klima & Morgan 2015, Climatic Change)*
 
**Quantitative benchmark:** Freezing rain frequency declines in southern regions as warming
reduces days in the −10 to 0°C surface window. Texas-specific: expected decline consistent
with SSP warming trajectories. Northern regions may see increases as rain-snow line shifts poleward.
*(Source: NHESS Jeong et al. 2019; GLISA Freezing Rain resource)*
 
---
 
### 7. Winter Weather ⚠️ Partially Computable
 
**NEX-GDDP variables:** `tasmin`, `tasmax`, `tas`, `pr`, `hurs`
 
**Relationship type:** Mixed. Cold indices (frost, icing days) are directly and cleanly
computable. Snow frequency and ice storm components are approximations only.
 
**Equation — Frost days (fully computable):**
 
```
Frost_days(year) = count(tasmin(d) < 273.15 K)
 
HCR_frost = [mean(Frost_days, future) − mean(Frost_days, baseline)]
            / mean(Frost_days, baseline)
→ Negative under warming
```
 
**Equation — Thermal cycling days (fully computable):**
 
```
ThermCycle(year) = count(tasmin(d) < 273.15 K AND tasmax(d) > 273.15 K)
[Freeze-thaw transitions — primary input to Coffin-Manson EFR]
```
 
**Equation — Snow day probability (approximation):**
 
```
P_snow(d) = 1 / (1 + exp(−(−3.0 + 0.27 × (tas(d) − 273.15))))
            [Jennings et al. 2018 logistic regression]
Snow_days(year) = Σ P_snow(d) × I(pr_mm(d) > 0.5)
```
 
**Quantitative benchmark:** Under SSP1-2.6, frost season shortens by ~23 days by 2100;
under SSP5-8.5, shortens by ~101 days (3.3 months). Cold spell duration index approaches
near-zero by 2060 under high warming.
*(Source: Linking hydroclimate indices, ScienceDirect 2024; USGS CMIP6-LOCA2 dataset)*
 
**Not captured by these proxies:** Polar vortex disruption events (e.g. February 2021
Texas Winter Storm Uri). These are tail-risk events driven by Arctic amplification
dynamics that CMIP6 surface variables do not resolve. Flag as an excluded
catastrophic hazard consistent with the LT Framework pilot assumptions.
 
---
 
### 8. Severe Convective Storms (SCS) ⚠️ Surface Proxy Only — Key Variables Missing
 
> **Why SCS is a single hazard category in this framework:**
> Hail, tornado, and strong convective wind are treated as a single **Severe Convective
> Storms (SCS)** bucket rather than as three separate hazards. This decision was made
> for three reasons:
>
> 1. **Physical co-occurrence:** These three phenomena share the same convective storm
>    environment and predominantly co-occur. Attempting to separate them introduces
>    false precision.
> 2. **Same missing data:** All three require CAPE and vertical wind shear (S06) which
>    are unavailable in NEX-GDDP. There is no principled basis to distinguish between
>    them from surface variables alone.
> 3. **Modelling tractability:** A single SCS environment proxy is more defensible and
>    auditable than three weak proxies pretending to be distinct hazards.
>
> Prior to this decision, hail, tornado, and strong wind were listed as separate hazards
> with individual scaling factors. Those entries are retained in Section 3 for reference
> but are flagged as superseded.
 
**NEX-GDDP variables:** `tas`, `tasmax`, `hurs`, `huss`, `sfcWind`
 
**Key variables NOT in NEX-GDDP:**
- CAPE (Convective Available Potential Energy) — primary instability driver
- Vertical wind shear S06 (0–6km) — determines storm organisation into supercells
- Storm-relative helicity (SRH) — determines tornado potential
- Freezing level height — determines hail size at ground
 
**Relationship type:** Non-linear compound. CAPE and wind shear interact multiplicatively.
Increasing CAPE (driven by warming and moistening) competes with decreasing shear
(driven by weakening meridional temperature gradient). Net effect on SCS frequency is
**uncertain but likely increasing** due to CAPE dominating.
 
**Equation — Surface thermodynamic instability proxy (best available from NEX-GDDP):**
 
```
# Equivalent potential temperature: proxy for boundary layer CAPE-supporting conditions
e_s(d) = 0.6108 × exp(17.27 × (tas(d) − 273.15) / (tas(d) − 35.85))
          [saturation vapour pressure, kPa]
 
θ_e(d) = tas(d) × exp(2.5e6 × huss(d) / (1005 × tas(d)))
          [equivalent potential temperature — proxy for moist static energy]
 
SCS_proxy_days(year) = count(θ_e(d) > θ_e_threshold AND sfcWind(d) > wind_threshold)
  [thresholds calibrated against ERA5 historical SCS occurrence at the site]
 
HCR_SCS = [mean(SCS_proxy_days, future) − mean(SCS_proxy_days, baseline)]
          / mean(SCS_proxy_days, baseline)
```
 
**⚠️ This proxy captures only the thermodynamic (instability) side of SCS formation.
It cannot capture the kinematic (wind shear) side. Use with low confidence.**
 
**Preferred approach (if CMIP6 pressure-level data from ESGF is accessible):**
 
```
Compute CAPE and S06 from 3D pressure-level CMIP6 outputs
SCS_environment_days = count(CAPE(d) × S06(d) > threshold)
  [Lepore et al. 2021 severe weather proxy approach]
HCR_SCS = (future count − baseline count) / baseline count
```
 
**Quantitative benchmark:** CAPE increases +5 to +20% per 1°C of global warming, driven
by increasing low-level moisture. Wind shear (S06) decreases modestly (~5–10%) due to
weakening meridional temperature gradient. Net result: severe thunderstorm environments
increase robustly; supercell frequency projected +6.6% and strongest supercell area +25.8%
under moderate warming.
*(Source: Lepore et al. 2021, Earth's Future — CMIP6; Diffenbaugh et al. 2013, PNAS;
Ashley et al. 2023, BAMS)*
 
**Consultation required:** Before finalising SCS equations, consult S (gen-2 model)
who is building models connecting climate variables to convective storm risk — her variable
choices and functional forms should feed directly into this mapping.
 
---
 
### 9. Coastal Flooding ❌ Not Computable from NEX-GDDP
 
**Required variables NOT in NEX-GDDP:** Sea level pressure, sea surface temperature (SST),
sea level rise projections, storm surge (requires hydrodynamic model).
 
**Why not computable:**
 
```
ESL = GMSL_rise + storm_surge + tide + wave_setup
 
None of these components are in NEX-GDDP:
  GMSL_rise  → from IPCC AR6 scenarios (external lookup)
  storm_surge → requires ADCIRC/SLOSH hydrodynamic model driven by
                TC tracks and storm-scale winds
  tide        → tidal harmonic analysis (site-specific)
  wave_setup  → wave model output
```
 
**Relationship type:** Superlinear compound — sea level rise (linear in time) multiplied
by storm intensity (non-linear in SST). Compound flooding from co-occurring storm surge
and extreme precipitation further amplifies risk non-linearly.
 
**Fallback approach:** Use IPCC AR6 regional sea level rise projections as external HCR
input directly. For storm surge, use published compound flood return period tables.
*(Source: IPCC SROCC; PMC/9285431 CMIP6 SLR-TC analysis)*
 
**Quantitative benchmark:** IPCC AR6 projects 0.43m SLR under SSP1-2.6 to 0.84m under
SSP5-8.5 by 2100. TC rainfall increases ~14% (+6 to +22%) within 100km at 2°C warming.
*(Source: IPCC SROCC; GFDL Global Warming and Hurricanes)*
 
**Note for Texas sites (Hayhurst/Maverick):** Coastal flooding is **not a relevant hazard**
for either inland Texas site. Include in framework only for future assets near coasts.
 
---
 
### 10. Hurricane ❌ Not Computable from NEX-GDDP
 
**Required variables NOT in NEX-GDDP:** SST, upper-tropospheric temperature profiles,
vertical wind shear (requires 3D atmospheric data).
 
**Why not computable:** Maximum Potential Intensity (Emanuel 1988) requires:
 
```
V_max² = (C_k / C_D) × (T_s / T_0) × CAPE*
  where T_s = SST, T_0 = outflow temperature (upper troposphere)
  None derivable from NEX-GDDP surface variables.
```
 
**Relationship type:** Non-linear with SST. TC intensity scales as ~5–7% per °C of SST
warming. TC rainfall intensity scales with Clausius-Clapeyron (~7%/°C).
 
**Fallback approach:** Use published probabilistic TC track datasets (Emanuel synthetic
tracks driven by CMIP6 SST) or the STORM dataset. These are pre-computed external products.
 
**Quantitative benchmark:** TC intensity increases 1–10% at 2°C global warming (GFDL);
5–7%/°C increase in maximum potential wind speed (CMIP6 ensemble). TC rainfall increases
+14% (+6 to +22%) within 100km at 2°C. Frequency of Cat 4–5 storms increases ~13% at 2°C.
*(Source: GFDL Global Warming and Hurricanes; Baatsen et al. 2023, Environmental Processes;
IPCC AR6 Chapter 11)*
 
**Note:** Excluded from pilot scope per LT Framework assumptions ("Impact of increase in
catastrophic hazard events such as hurricane not included").
 
---
 
### 11. Tornado ❌ Not Computable from NEX-GDDP
 
**Required variables NOT in NEX-GDDP:** CAPE, storm-relative helicity (SRH 0–1km),
vertical wind shear (S06 and S01), LCL height.
 
**Why not computable:** The Significant Tornado Parameter (Thompson et al. 2003) requires:
 
```
STP = (MLCAPE / 1500 J/kg) × (SHR6 / 20 m/s) × (2000 − MLLCL / 1500 m) × (SRH1 / 150 m²/s²)
Every component requires 3D atmospheric profile data. Not available in NEX-GDDP.
```
 
**Relationship type:** Highly uncertain. CAPE increases (bad) but wind shear decreases
(good). Net effect on tornado frequency cannot be reliably quantified at climate model
resolution — CMIP6 (~100 km) is too coarse to resolve tornadic mesocyclones.
 
**Confidence:** Cannot be quantified. Keep as NOT AVAILABLE.
 
**Quantitative benchmark (for context only):** Severe thunderstorm environments
(a necessary but not sufficient condition for tornadoes) increase robustly with warming.
Supercell frequency +6.6%, strongest supercell area +25.8% under moderate warming.
The specific tornado signal within this is unresolvable from current data.
*(Source: NOAA State of Science Fact Sheet on Tornadoes, Sept. 2023;
Ashley et al. 2023, BAMS)*
 
**Note:** Treated as part of the SCS bucket for framework purposes. Not separately
computable. See Section 8 (SCS).
 
---
 
### 12. Earthquake ❌ Not Applicable — HCR = 0
 
**Climate connection:** None meaningful at the site and timescale relevant to
infrastructure asset management.
 
**Why HCR = 0:**
 
```
Earthquake drivers: tectonic stress on fault systems
Climate pathways to seismicity:
  - Glacial isostasy (operates on geological timescales — millennia)
  - Groundwater extraction (stress change ~0.05–0.15 kPa/yr vs
    tectonic stress drops of 1–10 MPa — orders of magnitude smaller)
  - Reservoir level fluctuations (highly localised near large dams)
 
For Texas PV/Wind sites on stable crustal geology:
  HCR_earthquake = 0  (unconditionally, independent of climate scenario)
```
 
**Recommendation:** Exclude from climate HCR framework. Treat as a static hazard
modelled by site-specific seismic hazard analysis (PSHA) independent of climate scenario.
*(Source: NASA Science climate-earthquake explainer; USGS groundwater-seismicity studies)*
 
---
 
### Summary Table — Company Hazard List
 
| Hazard | Computable from NEX-GDDP? | Primary Variables | Relationship Type | Confidence | HCR Direction |
|---|---|---|---|---|---|
| Heat Wave | ✅ Fully | `tasmax`, `tasmin` | Non-linear (threshold) | High | ↑ Increases |
| Cold Wave | ✅ Fully | `tasmax`, `tasmin` | Non-linear (threshold) | High | ↓ Decreases (benefit) |
| Wildfire | ✅ Approx. (FWI) | `tasmax`, `hurs`, `sfcWind`, `pr` | Non-linear compound | Medium | ↑ Increases |
| Riverine Flooding | ⚠️ Partial | `pr` (Rx5day) + soil moisture approx. | Super-linear at tail | Medium-High | ↑ Increases |
| Strong Wind | ⚠️ Poor proxy | `sfcWind` (daily mean only) | Linear (mean); v² (loading) | Low-Medium | ≈0 for TX sites |
| Ice Storm | ⚠️ Poor proxy | `tasmin`, `tasmax`, `pr`, `hurs` | Non-linear threshold | Low | ↓ Decreases (TX) |
| Winter Weather | ⚠️ Partial | `tasmin`, `tasmax`, `tas`, `pr` | Mixed (linear cold counts) | Medium | ↓ Decreases overall |
| SCS (Hail+Tornado+Wind) | ⚠️ Surface proxy only | `tas`, `huss`, `sfcWind` + CAPE/S06 missing | Non-linear compound | Low | ↑ Likely increases |
| Coastal Flooding | ❌ Not computable | SLR + storm surge (external) | Super-linear compound | N/A for TX | ↑↑ Significantly increases |
| Hurricane | ❌ Not computable | SST, upper-air (not in NEX-GDDP) | Non-linear with SST | N/A | ↑ More intense, fewer |
| Tornado | ❌ Not computable | CAPE, SRH (not in NEX-GDDP) | Uncertain | Unknown | Unknown |
| Earthquake | ❌ Not applicable | None | None | HCR = 0 | None |
 
---
 
## 3. HCR Formula — Annual Computation
 
### The Phase 1 Formula (Linear)
 
```
HCR_hazard(t) = SCVR_variable(t) × scaling_factor
 
Where:
  t              = year (2026, 2027, ..., 2055)
  SCVR_variable  = annual SCVR for the relevant input variable
  scaling_factor = hazard-specific amplification constant
```
 
This is a **linear approximation** — Phase 1 of the implementation. Future phases may use power-law or lookup-table HCR functions.
 
### Why Scaling ≠ 1.0
 
Three physical reasons justify amplification:
 
**1. Tail amplification (threshold exceedance)**
 
When a distribution shifts by δ, the fraction of values exceeding a fixed threshold changes by much more than δ. For a normal distribution:
 
```
If the mean shifts by 0.5σ:
  - Values above μ+1σ increase from 15.9% to 30.9% (nearly doubled)
  - Values above μ+2σ increase from 2.3% to 6.7% (nearly tripled)
 
The further into the tail, the larger the amplification.
 
This is why heat scaling > 1: a small mean temperature shift
causes a disproportionate increase in extreme heat days.
```
 
**2. Clausius-Clapeyron for precipitation**
 
The atmosphere holds ~7% more water vapor per °C of warming. This amplifies extreme precipitation events even when mean precipitation changes little:
 
```
+1°C warming → +7% atmospheric moisture capacity
  → Extreme storm events draw from a richer moisture pool
  → Rx5day (extreme 5-day precipitation) grows ~7%/°C
  → But mean precipitation may grow only ~2%/°C
 
The extreme:mean ratio ≈ 3.5× amplification
This is why precipitation HCR scaling > 1
```
 
**3. Compound effects**
 
Some hazards depend on multiple variables acting together:
 
```
Icing = (T < 0°C) AND (RH > 90%)
  - If T warms (fewer days below 0°C)
  - AND humidity drops (fewer days above 90%)
  - Both effects reduce icing → compound reduction
 
Fire = f(high T, low RH, wind, dry fuel)
  - Warming + drying act together → compound amplification
  - The combined effect exceeds the sum of individual effects
```
 
### Current Scaling Factors
 
| Hazard | Scaling Factor | Input Variable(s) | Status | Basis |
|--------|---------------|-------------------|--------|-------|
| Heat stress (compound HW: 3+ consec. days, tasmax+tasmin > P90) | 2.0–3.0 (base: 2.5) | tasmax SCVR | Working estimate | Tail amplification; NB01 cross-check gives ~2.9 |
| Heat stress (P90 per-DOY single-day exceedance, tasmax only) | ~26 | tasmax SCVR | NB04 empirical | Per-DOY P90 counting on pooled daily data — see §4 NB04 check |
| Flood (extreme precip) | 1.5–2.0 | pr SCVR (high tail) | Preliminary range | Clausius-Clapeyron ~7%/°C |
| Hail | ~~1.0~~ **NOT COMPUTABLE** | ~~pr SCVR + sfcWind SCVR~~ | ~~Placeholder~~ **Superseded — merged into SCS bucket; pr+sfcWind has no physical basis for hail (requires CAPE, S06, freezing level — not in NEX-GDDP)** | See Section 2B SCS |
| Soiling/dust | 0.8 | pr SCVR (dry days) | Preliminary | Indirect: fewer rain days → more dust |
| Fire weather | Complex | tasmax + pr + hurs + sfcWind | Framework only | Multi-variable FWI interaction |
| Freeze-thaw | 1.0–1.5 | tasmin SCVR (inverse) | Working estimate | Linear threshold crossing |
| Icing | Compound | tasmin + hurs (RH > **90%**) | Working estimate — *threshold corrected from 75%* | Dual-threshold logic; IEC 61400-1 |
 
> **Confidence note:** These scaling factors are the **largest source of uncertainty** in the entire SCVR→NAV chain. The physics (Peck's, Coffin-Manson) are well-established, but the climate-to-hazard amplification factors are working estimates that need validation against observed hazard frequency data. See Section 9.
 
### Linear vs Non-Linear HCR
 
Phase 1 uses `HCR = SCVR × constant` (linear). This is appropriate when:
- SCVR is small (<0.15) — the linear approximation holds
- We don't have enough data to calibrate a non-linear function
 
For future phases, a power-law form may be more physical:
 
```
Phase 1 (current):    HCR = SCVR × α
Phase 2+ (future):    HCR = α × SCVR^β
 
Where β > 1 captures accelerating tail effects.
Example: β = 1.3 means a doubling of SCVR more than doubles HCR.
```
 
For the SCVR range we observe (0.03–0.16), the linear and power-law forms differ by <15%. The linear form is adequate for Phase 1.
 
---
 
## 4. Worked Example: Heat Stress at Hayhurst Solar
 
### Setup
 
Hayhurst Solar, SSP5-8.5, heat stress hazard.
 
From NB03 ensemble SCVR (using annual values from the team framework's annual approach):
 
```
Year:      2030    2035    2040    2045    2050
SCVR_tasmax: 0.042   0.056   0.074   0.086   0.092
```
 
Heat stress scaling factor: **2.5** (working estimate).
 
### Annual HCR Computation
 
```
HCR_heat(t) = SCVR_tasmax(t) × 2.5
 
Year     SCVR_tasmax   × 2.5   = HCR_heat    Interpretation
────     ──────────    ─────   ─────────    ──────────────
2030     0.042          2.5     0.105        10% more heat stress
2035     0.056          2.5     0.140        14% more heat stress
2040     0.074          2.5     0.185        19% more heat stress
2045     0.086          2.5     0.215        22% more heat stress
2050     0.092          2.5     0.230        23% more heat stress
```
 
### Visualising the Amplification
 
```
               SCVR (distribution shift)         HCR (hazard change)
               ─────────────────────────         ──────────────────────
2030:  ██░░░░░░░░░░░░░░░░░░  4.2%      ██████░░░░░░░░░░░░░░  10.5%
2035:  ███░░░░░░░░░░░░░░░░░  5.6%      ████████░░░░░░░░░░░░  14.0%
2040:  ████░░░░░░░░░░░░░░░░  7.4%      ██████████░░░░░░░░░░  18.5%
2045:  █████░░░░░░░░░░░░░░░  8.6%      ████████████░░░░░░░░  21.5%
2050:  █████░░░░░░░░░░░░░░░  9.2%      █████████████░░░░░░░  23.0%
 
       └── moderate shift ──┘           └── substantial hazard ─┘
       The 2.5× amplification is the non-linear tail effect.
```
 
### What HCR = 0.185 Means in Practice (Year 2040)
 
```
Baseline heat wave days per year (Hayhurst):  ~15 days
  (days where tasmax AND tasmin exceed P90 of historical)
 
Future heat wave days: 15 × (1 + 0.185) = ~17.8 days
 
Additional heat wave days: ~2.8 days/year
 
But each additional day at higher intensity:
  - Higher peak temperatures (P90 threshold itself shifts)
  - More hours above panel derating threshold (25°C STC)
  - More cumulative thermal stress for Peck's aging model
 
The 2.8 extra days × higher intensity per day = ~19% more total
heat stress, consistent with HCR = 0.185.
```
 
### Dollar Impact Per Year
 
```
Annual HCR feeds directly into CFADS:
 
  BI_heat(2040) = baseline_BI_heat × HCR_heat(2040)
                = baseline_BI_heat × 0.185
 
If baseline heat-related BI = $35K/yr:
  Additional BI from heat = $35K × 0.185 = $6,475/yr
 
  Over asset life (NPV at 8%): feeds into total NAV impairment
  See doc 09 for the complete financial chain.
```

### NB04 Empirical Check — Threshold Sensitivity (2026-03-19)

NB04 implemented Pathway B with **simple P90 per-DOY exceedance** (tasmax only, single day, no consecutiveness or tasmin requirement). This is a weaker filter than the compound heat wave definition used above.

```
NB04 Pathway B result (P90 per-DOY, tasmax only):
  Baseline P90-exceedance days:  ~36.5/year  (10% of days, by definition)
  Future P90-exceedance days:    ~101/year   (SSP2-4.5)

  HCR_heat = (101 - 36.5) / 36.5 ≈ +177%   (SSP2-4.5)
  HCR_heat ≈ +209%                           (SSP5-8.5)

  Implied scaling = HCR / SCVR = 1.77 / 0.069 ≈ 26×

Compare to compound heat wave (3+ consecutive, tasmax+tasmin > P90):
  Baseline: ~15 HW days/year
  Future:   ~18 HW days/year
  HCR ≈ +20%  →  implied scaling ≈ 2.9×

Why the 10× difference?
  - Simple P90: 10% of baseline days exceed → small shift pushes many over
  - Compound HW: ~4% of days qualify → rarer events, smaller relative change
  - Both are correct for their respective definitions
  - The threshold choice determines which BI model the HCR feeds:
      Simple P90 → hot-day derating (many days, small per-day impact)
      Compound HW → multi-day shutdown events (few events, large per-event impact)

KEY INSIGHT: Scaling factors are NOT universal — they must be
calibrated per threshold definition. The 2.5× applies to compound
heat waves; ~26× applies to simple P90 exceedance.

TODO: NB04 should implement the compound heat wave counter
to complete the cross-validation against the 2.5× estimate.
```

---

## 5. Worked Example: Precipitation → Flood Risk
 
### The Precipitation Puzzle
 
Precipitation SCVR at Hayhurst shows the inversion pattern:
 
```
Year:      2030    2035    2040    2045    2050
SCVR_pr:   +0.119  +0.056  +0.011  -0.089  -0.178
            wet ──────────── dry ──────────── dry
```
 
For flood risk, the **positive** SCVR years matter (more extreme rain events). For soiling/fire risk, the **negative** SCVR years matter (drying).
 
### HCR for Flood
 
```
HCR_flood(t) = max(0, SCVR_pr(t)) × flood_scaling
 
Where flood_scaling = 1.5-2.0 (Clausius-Clapeyron amplification)
Using midpoint 1.75:
 
Year     SCVR_pr    Clamp    × 1.75   = HCR_flood
────     ───────    ─────    ──────   ──────────
2030     +0.119     0.119     1.75     0.208
2035     +0.056     0.056     1.75     0.098
2040     +0.011     0.011     1.75     0.019
2045     −0.089     0.000     1.75     0.000   ← no flood amplification
2050     −0.178     0.000     1.75     0.000   ← drying period
```
 
**Why we clamp at zero:** Negative SCVR_pr means overall drying — fewer precipitation days. But individual storms in a drier climate can still be intense. The clamping is a simplification; Phase 2+ may separate the wet tail from the dry tail of the pr distribution.
 
### Clausius-Clapeyron Amplification
 
```
Why does flood scaling exceed 1.0?
 
The atmosphere obeys Clausius-Clapeyron:
  +1°C warming → ~7% more moisture capacity
 
What this means for storms:
 
  Historical 100mm storm event:
    Atmosphere holds X kg/m² of water vapor
    Storm dumps ~100mm
 
  Future (+2°C warmer) 100mm-equivalent storm:
    Atmosphere holds X × 1.14 kg/m² (7% × 2°C)
    Storm dumps ~114mm
 
    Same storm dynamics → 14% more rainfall
    The pr SCVR captures the distribution shift,
    but the Clausius-Clapeyron effect amplifies
    the extreme tail disproportionately.
 
  At the 99th percentile, observed amplification
  is often 2-3× the C-C rate → scaling = 1.5-2.0
```
 
---
 
## 6. Negative HCR — Warming Reduces Some Hazards
 
Not all HCR values are positive. Warming genuinely reduces some hazards:
 
```
HAZARDS THAT DECREASE WITH WARMING
 
  Frost days:
    Baseline (Maverick): ~30-50 frost days/year (Dec-Feb)
    Future (SSP585):     ~20-35 frost days/year
    HCR_frost:           NEGATIVE (~-0.25 to -0.40)
    → Fewer freeze events → less icing on turbine blades
 
  Cold wave days:
    Same direction — fewer consecutive cold days
    HCR_coldwave:        NEGATIVE
 
  Icing conditions (compound):
    Requires both T < 0°C AND RH > 90%
    Both conditions become less frequent
    HCR_icing:           NEGATIVE (~-0.30 to -0.50)
 
FINANCIAL IMPLICATION:
  Negative HCR = FEWER hazard events = LESS damage
  This shows up as a NAV UPSIDE in the financial model.
 
  For Maverick Wind:
    Icing reduction saves ~$1-3M NPV (fewer shutdowns)
    This partially offsets the (small) heat-related costs
```
 
This is one of the few cases in climate risk analysis where warming produces a genuine financial benefit — and it's specific to wind farms in regions with meaningful icing risk.
 
---
 
## 7. Compound Events — When Hazards Interact
 
### What Are Compound Events?
 
Some damage occurs only when **two or more climate conditions coincide**. The combined HCR is not simply additive:
 
```
COMPOUND EVENT EXAMPLES
 
1. DROUGHT → FLASH FLOOD
   Extended dry spell hardens soil surface
   → When rain finally arrives, reduced infiltration
   → Same rainfall event produces more surface runoff
   → Flood damage amplified by prior drought
 
   HCR_compound > HCR_drought + HCR_flood
 
2. HEAT × HUMIDITY → ACCELERATED AGING
   Peck's model: AF = f(Temperature) × f(Humidity)
   The two factors MULTIPLY, not add.
   A +10% temperature increase combined with +10% humidity
   gives more than +20% total aging acceleration.
 
   EFR captures this directly (see doc 08).
 
3. WIND × ICE → STRUCTURAL FAILURE
   High winds on iced blades create asymmetric loading
   that neither wind alone nor ice alone would cause.
   The loading is multiplicative:
 
   Load_compound = Load_wind × (1 + ice_mass_fraction)
 
   Blade icing + sustained wind = the most dangerous
   combination for turbine structural integrity.
```
 
### How Compound HCRs Interact
 
```
SIMPLE (INDEPENDENT) HAZARDS:
  HCR_total = HCR_heat + HCR_flood + HCR_wind
  (each hazard acts on a different damage pathway)
 
COMPOUND (INTERACTING) HAZARDS:
  HCR_compound = f(HCR_A, HCR_B) > HCR_A + HCR_B
  (damage pathways overlap or amplify each other)
 
Phase 1 approach: treat as independent (additive)
Phase 2+: implement compound interaction terms
 
For Phase 1, this is conservative (underestimates compound risk)
when both hazards increase, but the error is small when
SCVR values are moderate (<0.15).
```
 
---
 
## 8. HCR Output Format
 
The HCR output is an **annual table per hazard per scenario**, matching the team framework format:
 
```
HAYHURST SOLAR — SSP5-8.5
 
Hazard              2030   2031   ...   2040   ...   2050
─────────────────   ─────  ─────       ─────       ─────
Heat stress          0.11   0.11  ...   0.19   ...   0.23
Flood (extreme pr)   0.21   0.20  ...   0.02   ...   0.00
Freeze-thaw         -0.05  -0.05  ...  -0.08   ...  -0.10
Soiling/dust         0.00   0.00  ...   0.05   ...   0.14
Fire weather         0.05   0.05  ...   0.09   ...   0.14
Icing               -0.08  -0.08  ...  -0.12   ...  -0.15
 
Notes:
  - Negative values = hazard DECREASING (benefit)
  - Flood HCR falls as precipitation shifts to drying post-2040
  - Soiling HCR rises as drying intensifies
  - Heat stress grows monotonically
```
 
```
MAVERICK WIND — SSP5-8.5
 
Hazard              2030   2031   ...   2040   ...   2050
─────────────────   ─────  ─────       ─────       ─────
Heat stress          0.08   0.08  ...   0.14   ...   0.17
Wind structural      0.00   0.00  ...   0.00   ...   0.00
Icing               -0.12  -0.12  ...  -0.18   ...  -0.22
Cut-out events       0.00   0.00  ...   0.00   ...   0.00
Flood (access)       0.15   0.14  ...   0.02   ...   0.00
 
Notes:
  - sfcWind SCVR ≈ 0 → wind structural and cut-out HCRs = 0
  - Icing strongly negative = significant benefit
  - This is WHY wind is ~10× less climate-impaired than solar
```
 
### Parquet Schema for NB04 Output
 
```
Columns:
  site_id:    string    ("hayhurst_solar", "maverick_wind")
  scenario:   string    ("ssp245", "ssp585")
  year:       int       (2026, 2027, ..., 2055)
  hazard:     string    ("heat_stress", "flood", "freeze_thaw", ...)
  hcr:        float     (signed — negative = hazard decreasing)
  scvr_input: float     (the SCVR value used as input)
  scaling:    float     (the scaling factor applied)
  confidence: string    ("validated", "working_estimate", "preliminary")
```
 
---
 
## 9. Sensitivity Analysis — The Biggest Uncertainty
 
The HCR scaling factors are the **most uncertain parameters** in the SCVR→NAV chain. The physics models downstream (Peck's, Coffin-Manson) have well-established equations — but the climate-to-hazard amplification is where the real uncertainty lives.
 
### Heat Scaling Sensitivity
 
```
HAYHURST SOLAR NAV IMPAIRMENT vs HEAT SCALING FACTOR
 
  SCVR_tasmax (2040) = 0.074  (fixed — from climate models)
 
  Scaling = 2.0:   HCR = 0.148   NAV impact ≈ $4.2M  (7.0%)
  Scaling = 2.5:   HCR = 0.185   NAV impact ≈ $5.9M  (9.8%)  ← base case
  Scaling = 3.0:   HCR = 0.222   NAV impact ≈ $7.8M  (13.0%)
 
  Range: $4.2M — $7.8M  (factor of 1.9× between low and high)
 
  NAV ($M)
   8 │                                          ●  3.0
     │                                     ●
   6 │                                ●         ← 2.5 (base)
     │                           ●
   4 │                      ●                   ← 2.0
     │
   2 │
     └──────────────────────────────────────────
       1.0    1.5    2.0    2.5    3.0    3.5
                    Heat Scaling Factor
 
  A ±0.5 change in scaling factor moves NAV impairment by ~±$1.5-2M.
  This is a significant source of uncertainty.

  THRESHOLD SENSITIVITY (NB04 finding):
    For P90 per-DOY exceedance, NB04 finds scaling ~26×, but this feeds
    a different BI model (simple hot-day derating rather than multi-day
    heat wave shutdown). The financial impact routing depends on which
    threshold definition the BI model uses — see §4 NB04 check.
```
 
### Why This Matters for NB04
 
The scaling factors should be:
1. **Calibrated** where possible — compare annual hazard counts from NB01 climate indices against SCVR predictions
2. **Bounded** by physical constraints — Clausius-Clapeyron sets an upper bound for precipitation; tail statistics set bounds for temperature
3. **Reported with ranges** — present NAV under low/mid/high HCR assumptions
4. **Updated** as more literature and observational data become available

---

## 10. Connection to NB01 Climate Indices

Notebook 01 already computes **annual hazard counts** as climate indices. These are the same quantities that HCR measures:

```
NB01 ANNUAL INDICES           HCR HAZARD           RELATIONSHIP
──────────────────            ──────────            ────────────
heat_wave_days(t)      →     Heat stress      →    HCR ≈ (future - baseline) / baseline
frost_days(t)          →     Freeze-thaw      →    HCR = (future - baseline) / baseline
rx5day(t)              →     Flood risk       →    HCR ≈ (future - baseline) / baseline
fwi_mean(t)            →     Fire weather     →    HCR = (future - baseline) / baseline
```

This means NB04 has **two pathways** to compute HCR:

```
PATHWAY A: SCVR × Scaling (parametric)
  + Fast to compute
  + Consistent with SCVR framework
  + Works even without annual index data
  − Depends on scaling factor estimates

PATHWAY B: Direct Index Comparison (empirical)
  + Uses actual hazard counts (no scaling factor needed)
  + More physically grounded
  + NB01 already has the infrastructure
  − Requires full daily data processing per year
  − Annual hazard counts can be noisy (need multi-model averaging)

RECOMMENDED: Use both. Cross-validate Pathway A against Pathway B.
Where they agree, confidence is high.
Where they disagree, investigate the scaling factor.
```

**Deep dives:**
- [Pathway A vs B from basics](../../discussion/discussion_hcr_pathway_a_vs_b.md) — worked examples, decision matrix per variable, naming clarification (HCR-level vs framework-level pathways)
- [Jensen's inequality: why HCR ≠ f(SCVR)](../../discussion/discussion_jensen_inequality_hcr_scvr.md) — why Pathway A fails for precipitation and when the linear scaling approximation breaks down

### Calibrating Scaling Factors Using NB01 Data

```
Example — calibrating heat stress scaling:

1. From NB01, get annual heat_wave_days for baseline and future
   Baseline mean: 15 heat wave days/year
   Future mean (2040 window): 18 heat wave days/year
   Empirical HCR_heat = (18 - 15) / 15 = +0.20

2. From NB03, get SCVR_tasmax = 0.074

3. Implied scaling = HCR / SCVR = 0.20 / 0.074 = 2.7

   Close to our working estimate of 2.5 — validates the assumption
   for the compound heat wave definition.

NB04 cross-validation (simple P90 per-DOY exceedance):
   Implied scaling = 1.77 / 0.069 ≈ 26×
   This is for a DIFFERENT threshold definition (see §4 NB04 check).
   Both scalings are correct within their respective definitions.

   The choice of threshold definition is itself a modeling decision —
   it determines which BI model channel the HCR feeds.
```

---

## 11. Open Questions for NB04 Implementation

### Priority Research Needed

| Question | Impact | Approach |
|----------|--------|----------|
| Are heat scaling factors region-specific? | HIGH | Compare Hayhurst vs Maverick implied scaling |
| How to handle pr sign inversion for flood HCR? | MEDIUM | Separate wet-tail from dry-tail analysis |
| Is FWI computable from NEX-GDDP variables? | MEDIUM | Implement simplified Canadian FWI |
| Compound event interaction terms? | LOW (Phase 2) | Literature review — start with Zscheischler et al. |
| Non-linear HCR (power law)? | LOW (Phase 2) | Need more sites for calibration data |

### Implementation Decisions for NB04

1. **HCR Pathway B — DONE (Part A, 2026-03-19):** NB04 computed HCR via Pathway B (direct counting) for tasmax (P90 per-DOY) and precipitation (rx5day, frost days). Results saved to `data/processed/hcr/hayhurst_solar/`. NB04 used decade SCVR decomposition directly (not annual SCVR).

2. **Which threshold definition feeds the BI model?** NB04's P90 per-DOY exceedance gives ~26× scaling; compound heat waves give ~2.5-3×. The choice determines the financial routing. **This is the key open question for NB05.**

3. **Compound heat wave counter:** NB04 should implement the compound definition (3+ consecutive days, tasmax+tasmin > P90) to complete the cross-validation against the 2.5× estimate.

4. **Negative HCR handling:** Allow negative HCR values (hazard decreasing). These create NAV upsides that partially offset other impairments.

5. **Per-hazard vs aggregate HCR:** Compute HCR per hazard separately, then combine at the CFADS/NAV stage. Do not aggregate HCR values across hazards — they feed into different BI loss models. HCR feeds Channel 1 (BI); EFR feeds Channel 2 (degradation) independently.

---

## 12. Common Misconceptions
 
| You might think... | But actually... |
|---|---|
| HCR = SCVR (they're the same thing) | No — SCVR measures distribution shift; HCR measures hazard change. A +8% distribution shift can cause +21% more heat hazard (2.5× amplification) |
| SCVR feeds into HCR as a direct input | No — SCVR and HCR are computed in parallel from the same raw data. SCVR enters only as a cross-check (Pathway A calibration) and annual interpolation signal |
| HCR scaling factors are known precisely | No — they are the biggest uncertainty in the chain. The range between low and high estimates can change NAV by ±$2M |
| All hazards increase with warming | No — frost days, icing events, and cold waves decrease. HCR can be negative (a financial benefit) |
| HCR is constant over time | No — HCR(t) varies each year as SCVR(t) evolves. It maps directly to annual CFADS adjustments |
| Compound events are simply additive | No — interacting hazards can amplify each other non-linearly. Phase 1 treats them as additive (conservative simplification) |
| HCR tells you the dollar impact | No — HCR tells you hazard change. The dollar impact comes from HCR feeding Channel 1 (BI loss, doc 09) alongside the parallel Channel 2 (EFR from physics models, doc 08) |
| sfcWind SCVR ≈ 0 means wind farms have no climate risk | Not exactly — wind farms still face heat stress, icing changes, and flood risk through other variables. But the dominant structural fatigue pathway is unaffected |
| Heat wave SCVR is a valid concept | No — SCVR is computed on raw variable distributions (tasmax, tasmin), not on hazard event counts. "SCVR for heatwave" conflates the variable level with the hazard level |
| Hail can be computed as pr + sfcWind proxy | No — hail requires CAPE, wind shear (S06), and freezing level height. These are not available in NEX-GDDP. Hail is merged into the SCS bucket |
 
---

## Next

- [08 - EFR: Equipment Failure & Degradation](08_efr_equipment_degradation.md) — The engineering models that translate climate stress (SCVR) into physical equipment degradation (parallel to HCR)
- [09 - NAV Impairment Chain](09_nav_impairment_chain.md) — The complete annual pipeline from SCVR to dollar impairment
- [04 - SCVR Methodology](04_scvr_methodology.md) — How SCVR is computed (the input to this doc)

Return to [Index](00_index.md) for the full learning guide table of contents.
