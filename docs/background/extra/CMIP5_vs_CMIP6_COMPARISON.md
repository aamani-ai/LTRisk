# CMIP5 vs CMIP6: Comparison for Long-Term Climate Risk Modeling

*Technical comparison of climate data sources for the NAV Impairment Framework*

**Created:** February 1, 2026  
**Purpose:** Guide for selecting appropriate climate data source for InfraSure's long-term risk pilot

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What is CMIP?](#what-is-cmip)
3. [Variable Availability](#variable-availability)
4. [Downscaled Products](#downscaled-products)
5. [Scenario Comparison (RCP vs SSP)](#scenario-comparison-rcp-vs-ssp)
6. [Recommendation for Our Use Case](#recommendation-for-our-use-case)
7. [Mitigation Strategies](#mitigation-strategies)

---

## Executive Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         QUICK RECOMMENDATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FOR THIS PILOT: Use NEX-GDDP-CMIP6 (SSP2-4.5)                             │
│                                                                              │
│  WHY:                                                                       │
│  ✅ All required variables available (including rsds for solar)            │
│  ✅ Bias-corrected against historical observations                         │
│  ✅ Downscaled to 0.25° daily (~25km) - ready for site-specific analysis  │
│  ✅ Consistent global coverage                                              │
│  ✅ SSP scenarios provide socioeconomic context for investor communication │
│  ✅ IPCC AR6 (2021) is based on CMIP6                                      │
│                                                                              │
│  Team's original choice (CORDEX-CMIP5) is NOT wrong, but NEX-GDDP-CMIP6   │
│  is better suited for this specific use case.                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## What is CMIP?

**CMIP (Coupled Model Intercomparison Project)** is an international framework for coordinating climate model experiments. Multiple modeling centers worldwide run standardized experiments, producing ensemble projections of future climate.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CMIP VERSIONS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CMIP5 (Phase 5)                                                            │
│  ───────────────                                                             │
│  • Released: 2013                                                           │
│  • Scenarios: RCP (Representative Concentration Pathways)                   │
│  • Used in: IPCC AR5 (2013-2014)                                           │
│  • Models: ~40 models from ~20 modeling centers                            │
│  • Resolution: Typically 1-2° (~100-200km)                                 │
│                                                                              │
│  CMIP6 (Phase 6)                                                            │
│  ───────────────                                                             │
│  • Released: 2019-2021                                                      │
│  • Scenarios: SSP (Shared Socioeconomic Pathways) + RCP forcing            │
│  • Used in: IPCC AR6 (2021-2022)                                           │
│  • Models: ~100 models from ~50 modeling centers                           │
│  • Resolution: Typically 0.5-1° (~50-100km)                                │
│  • Improvements: Better aerosols, clouds, carbon cycle, ice sheets         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Variable Availability

### Required Variables for NAV Impairment Framework

| Variable | Purpose | CMIP5 Raw | CMIP6 Raw | CORDEX (CMIP5) | NEX-GDDP-CMIP6 |
|----------|---------|-----------|-----------|----------------|----------------|
| **rsds** (Solar Irradiance) | Solar PV generation | ✅ Yes | ✅ Yes | ⚠️ Varies by domain | ✅ Yes |
| **tas** (Temperature mean) | Heat stress, efficiency | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **tasmax** (Temperature max) | Heat waves | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **tasmin** (Temperature min) | Freeze events | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **pr** (Precipitation) | Flood risk | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **sfcWind** (Wind speed) | Wind generation | ✅ Yes | ✅ Yes | ⚠️ Varies | ✅ Yes |
| **hurs** (Relative humidity) | Degradation models | ✅ Yes | ✅ Yes | ⚠️ Varies | ✅ Yes |

### Key Insight: Raw vs Downscaled Products

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RAW CMIP vs DOWNSCALED PRODUCTS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  RAW CMIP5/CMIP6:                                                           │
│  ─────────────────                                                           │
│  • Resolution: 1-2° (~100-200km)                                            │
│  • TOO COARSE for site-specific analysis                                    │
│  • A 100km grid cell covers multiple climate zones in Texas                │
│  • Contains systematic biases vs observations                               │
│  • NOT recommended for direct use in asset-level analysis                  │
│                                                                              │
│  DOWNSCALED PRODUCTS:                                                       │
│  ────────────────────                                                        │
│  • Higher resolution (10-50km)                                              │
│  • Bias-corrected against historical observations                          │
│  • More suitable for site-specific analysis                                │
│  • Options: CORDEX, NEX-GDDP, LOCA, etc.                                   │
│                                                                              │
│  ⚠️ IMPORTANT: You should NOT use raw CMIP data directly.                  │
│     Always use a downscaled, bias-corrected product.                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Downscaled Products

### CORDEX (Coordinated Regional Climate Downscaling Experiment)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CORDEX (CMIP5-based)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  WHAT IT IS:                                                                │
│  • Regional climate models (RCMs) driven by global CMIP5 models            │
│  • Dynamical downscaling (runs physics at higher resolution)               │
│  • Organized by regional domains (North America, Europe, etc.)             │
│                                                                              │
│  SPECIFICATIONS:                                                            │
│  • Resolution: ~25-50km (varies by domain)                                 │
│  • Temporal: Daily                                                          │
│  • Scenarios: RCP2.6, RCP4.5, RCP8.5                                       │
│                                                                              │
│  STRENGTHS:                                                                 │
│  ✅ Dynamical downscaling captures regional climate features               │
│  ✅ Well-established, widely used                                          │
│  ✅ Good coverage for Europe, parts of North America                       │
│                                                                              │
│  WEAKNESSES:                                                                │
│  ❌ Variable availability varies by domain and model                       │
│  ❌ rsds (solar) NOT consistently available for all domains                │
│  ❌ NA-CORDEX (North America) has limited model ensemble                   │
│  ❌ May still have systematic biases                                       │
│  ❌ Based on older CMIP5 models                                            │
│                                                                              │
│  ACCESS:                                                                    │
│  • ESGF: https://esgf-node.llnl.gov/                                       │
│  • World Bank Climate Portal (aggregated stats)                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### NEX-GDDP-CMIP6 (NASA Earth Exchange Global Daily Downscaled Projections)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       NEX-GDDP-CMIP6 (CMIP6-based)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  WHAT IT IS:                                                                │
│  • NASA product that takes raw CMIP6 outputs                               │
│  • Applies bias correction against ERA5 observations                       │
│  • Statistical downscaling to 0.25° resolution                             │
│  • Consistent global coverage                                               │
│                                                                              │
│  SPECIFICATIONS:                                                            │
│  • Resolution: 0.25° (~25km)                                               │
│  • Temporal: Daily                                                          │
│  • Period: 1950-2100                                                        │
│  • Scenarios: SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5                       │
│  • Models: 35 CMIP6 models                                                  │
│                                                                              │
│  AVAILABLE VARIABLES:                                                       │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Variable   │  Description                        │  Units        │    │
│  ├─────────────┼─────────────────────────────────────┼───────────────┤    │
│  │  rsds       │  Surface Downwelling Shortwave      │  W/m²         │    │
│  │             │  (≈ GHI for solar models)           │               │    │
│  │  tas        │  Near-Surface Air Temperature       │  K            │    │
│  │  tasmax     │  Daily Maximum Temperature          │  K            │    │
│  │  tasmin     │  Daily Minimum Temperature          │  K            │    │
│  │  pr         │  Precipitation                      │  kg/m²/s      │    │
│  │  hurs       │  Near-Surface Relative Humidity     │  %            │    │
│  │  sfcWind    │  Near-Surface Wind Speed            │  m/s          │    │
│  └─────────────┴─────────────────────────────────────┴───────────────┘    │
│                                                                              │
│  STRENGTHS:                                                                 │
│  ✅ ALL required variables consistently available globally                 │
│  ✅ rsds (solar irradiance) included - critical for our use case          │
│  ✅ Bias-corrected against ERA5 (reduces systematic errors)               │
│  ✅ Consistent 0.25° grid globally                                         │
│  ✅ 35 model ensemble for uncertainty quantification                       │
│  ✅ Well-documented, easy to access                                        │
│  ✅ Based on newer CMIP6 models (better physics)                           │
│                                                                              │
│  WEAKNESSES:                                                                │
│  ❌ Statistical downscaling (not dynamical like CORDEX)                    │
│  ❌ May not capture local topographic effects as well                      │
│  ❌ Newer product (less track record than CORDEX)                          │
│                                                                              │
│  ACCESS:                                                                    │
│  • NASA NCCS: https://www.nccs.nasa.gov/services/data-collections/        │
│               land-based-products/nex-gddp-cmip6                           │
│  • AWS Open Data: s3://nex-gddp-cmip6/                                     │
│  • Google Earth Engine                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Head-to-Head Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CORDEX vs NEX-GDDP-CMIP6                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Criteria               │ CORDEX (CMIP5)     │ NEX-GDDP-CMIP6              │
│  ───────────────────────┼────────────────────┼─────────────────────────────│
│  Base data              │ CMIP5              │ CMIP6                        │
│  Downscaling method     │ Dynamical          │ Statistical                  │
│  Resolution             │ 25-50km            │ 25km (0.25°)                │
│  rsds (solar)           │ ⚠️ Varies          │ ✅ Always available         │
│  Bias correction        │ ⚠️ Varies          │ ✅ Yes (ERA5)               │
│  Global coverage        │ ❌ Regional         │ ✅ Yes                      │
│  Scenarios              │ RCP                │ SSP                          │
│  IPCC basis             │ AR5 (2013)         │ AR6 (2021)                  │
│  Texas coverage         │ NA-CORDEX (limited)│ ✅ Full coverage            │
│  Ease of access         │ Moderate           │ Easy (AWS, GEE)             │
│                                                                              │
│  FOR OUR USE CASE:      │                    │ ✅ RECOMMENDED              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Scenario Comparison (RCP vs SSP)

### RCP (CMIP5) → SSP (CMIP6) Mapping

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RCP to SSP MAPPING                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  RCP = Radiative forcing only (W/m² by 2100)                               │
│  SSP = Socioeconomic pathway + Radiative forcing                           │
│                                                                              │
│  ┌─────────────┬─────────────┬───────────────────────────────────────────┐ │
│  │ CMIP5 (RCP) │ CMIP6 (SSP) │ Description                               │ │
│  ├─────────────┼─────────────┼───────────────────────────────────────────┤ │
│  │ RCP2.6      │ SSP1-2.6    │ Sustainability, low emissions             │ │
│  │ RCP4.5      │ SSP2-4.5    │ Middle of the road, moderate emissions    │ │
│  │ RCP6.0      │ SSP4-6.0    │ Inequality, medium-high emissions         │ │
│  │ RCP8.5      │ SSP5-8.5    │ Fossil-fueled development, high emissions │ │
│  └─────────────┴─────────────┴───────────────────────────────────────────┘ │
│                                                                              │
│  TEAM'S CHOICE: RCP4.5 → Equivalent to SSP2-4.5                            │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  WHY SSP IS BETTER FOR INVESTOR COMMUNICATION:                             │
│                                                                              │
│  RCP4.5 tells investor:                                                     │
│    "This assumes 4.5 W/m² radiative forcing by 2100"                       │
│    → Meaningless to non-climate expert                                     │
│                                                                              │
│  SSP2-4.5 tells investor:                                                   │
│    "This assumes a 'middle of the road' world where:                       │
│     - Population peaks mid-century                                         │
│     - Economic growth continues at historical rates                        │
│     - Some climate policy but not aggressive                               │
│     - Technology improves gradually                                        │
│     - Resulting in moderate warming (~2.4°C by 2100)"                      │
│    → Provides context for 25-35 year infrastructure decisions             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Recommendation for Our Use Case

### Why NEX-GDDP-CMIP6 is Better for the NAV Impairment Framework

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              RECOMMENDATION: NEX-GDDP-CMIP6 (SSP2-4.5)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  OUR REQUIREMENTS:                          NEX-GDDP-CMIP6 DELIVERS:        │
│  ──────────────────                         ─────────────────────────        │
│                                                                              │
│  1. Solar irradiance for pvlib           →  ✅ rsds available daily        │
│                                                                              │
│  2. Temperature for heat stress          →  ✅ tas, tasmax, tasmin          │
│                                                                              │
│  3. Wind for wind models                 →  ✅ sfcWind (10m)                │
│                                                                              │
│  4. Humidity for Peck's degradation      →  ✅ hurs available               │
│                                                                              │
│  5. Precipitation for flood HCR          →  ✅ pr available                 │
│                                                                              │
│  6. Site-specific (Culberson, Concho TX) →  ✅ 0.25° resolution sufficient │
│                                                                              │
│  7. 2030-2050 projections                →  ✅ 1950-2100 coverage           │
│                                                                              │
│  8. Multiple ensembles for uncertainty   →  ✅ 35 models available          │
│                                                                              │
│  9. Investor-friendly scenario naming    →  ✅ SSP narratives               │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CORDEX (CMIP5) GAPS FOR OUR USE CASE:                                     │
│  ─────────────────────────────────────                                      │
│  ❌ rsds not consistently available for NA-CORDEX                          │
│  ❌ Limited model ensemble for North America                               │
│  ❌ RCP scenarios less intuitive for investors                             │
│  ❌ Based on older CMIP5 physics                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Mitigation Strategies

### If Using CORDEX (CMIP5)

If the team decides to proceed with CORDEX-CMIP5 (e.g., for comparison or specific regional needs):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              MITIGATION: IF USING CORDEX (CMIP5)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ISSUE 1: rsds (Solar Irradiance) May Not Be Available                     │
│  ─────────────────────────────────────────────────────                      │
│                                                                              │
│  Mitigation Options:                                                        │
│                                                                              │
│  A) Derive GHI from other variables                                        │
│     • Use clearness index models (Angstrom-Prescott)                       │
│     • Input: sunshine hours, cloud cover, temperature range                │
│     • Limitation: Adds uncertainty, requires additional calibration        │
│                                                                              │
│  B) Use historical GHI + delta method                                      │
│     • Take ERA5 historical GHI as baseline                                 │
│     • Apply temperature-cloud-based adjustment for future                  │
│     • Limitation: Assumes relationship between T and radiation holds      │
│                                                                              │
│  C) Hybrid approach                                                         │
│     • Use CORDEX for temperature, precipitation, wind                      │
│     • Use NEX-GDDP-CMIP6 rsds (scaled to match CORDEX scenarios)          │
│     • Limitation: Scenario inconsistency                                   │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ISSUE 2: Limited Ensemble for NA-CORDEX                                   │
│  ───────────────────────────────────────                                    │
│                                                                              │
│  Mitigation:                                                                │
│  • Use all available models (typically 5-10 for NA-CORDEX)                │
│  • Supplement with LOCA2 (another CMIP5 downscaled product for US)        │
│  • Acknowledge wider uncertainty in NAV impairment range                   │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ISSUE 3: Bias in Raw Data                                                 │
│  ─────────────────────────                                                  │
│                                                                              │
│  Mitigation:                                                                │
│  • Apply quantile mapping bias correction against ERA5                    │
│  • Validate against PRISM or Daymet for US sites                          │
│  • Document bias correction methodology                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### If Using NEX-GDDP-CMIP6

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              MITIGATION: IF USING NEX-GDDP-CMIP6                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ISSUE 1: Statistical (not Dynamical) Downscaling                          │
│  ─────────────────────────────────────────────────                          │
│                                                                              │
│  Concern: May not capture local topographic or coastal effects as well     │
│                                                                              │
│  Mitigation:                                                                │
│  • For Texas sites, topography is relatively flat - less concern           │
│  • Validate against local station data (NSRDB for solar, ASOS for temp)   │
│  • If validation shows bias, apply site-specific correction                │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ISSUE 2: Newer Product (Less Validation History)                          │
│  ─────────────────────────────────────────────────                          │
│                                                                              │
│  Concern: Less track record than CORDEX                                    │
│                                                                              │
│  Mitigation:                                                                │
│  • NASA has published validation papers                                    │
│  • Compare historical period (1980-2014) against ERA5, PRISM              │
│  • Document validation results in pilot report                             │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ISSUE 3: rsds is GHI, Not DNI/DHI                                         │
│  ─────────────────────────────────                                          │
│                                                                              │
│  Concern: pvlib needs GHI, DNI, DHI; CMIP6 only provides rsds (≈ GHI)     │
│                                                                              │
│  Mitigation:                                                                │
│  • Use decomposition models (e.g., DISC, DIRINT, Erbs) in pvlib           │
│  • These models derive DNI/DHI from GHI using solar geometry              │
│  • Well-established methodology, adds minimal uncertainty                  │
│                                                                              │
│  Example pvlib code:                                                        │
│  ```python                                                                  │
│  from pvlib.irradiance import erbs                                         │
│  dni, dhi, kt = erbs(ghi, solar_zenith, datetime_index)                   │
│  ```                                                                        │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ISSUE 4: Wind at 10m, Need Hub Height (~80-100m)                          │
│  ─────────────────────────────────────────────────                          │
│                                                                              │
│  Concern: sfcWind is 10m; wind turbines are at 80-100m                     │
│                                                                              │
│  Mitigation:                                                                │
│  • Apply logarithmic wind profile extrapolation                            │
│  • Use surface roughness appropriate for site (grassland, etc.)           │
│  • This is standard practice, same as what would be done with CORDEX      │
│                                                                              │
│  Formula:                                                                   │
│  v_hub = v_10m × ln(z_hub / z_0) / ln(10 / z_0)                           │
│                                                                              │
│  Where z_0 = surface roughness length (~0.03m for grassland)              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DECISION MATRIX                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Use NEX-GDDP-CMIP6 (SSP2-4.5) IF:                                         │
│  ─────────────────────────────────                                          │
│  ✅ You need consistent rsds (solar irradiance)                            │
│  ✅ You want bias-corrected, ready-to-use data                             │
│  ✅ You need global or US-wide coverage                                    │
│  ✅ You want investor-friendly scenario narratives (SSP)                   │
│  ✅ This is new work with no legacy CMIP5 pipelines                        │
│                                                                              │
│  Use CORDEX (CMIP5, RCP4.5) IF:                                            │
│  ────────────────────────────                                               │
│  ⚠️ You have existing CMIP5-based workflows to maintain                    │
│  ⚠️ You specifically need dynamical downscaling for complex terrain       │
│  ⚠️ You need to match a previous study using CMIP5                        │
│  ⚠️ You're comparing against other CMIP5-based analyses                   │
│                                                                              │
│  FOR THIS PILOT: None of the "Use CORDEX if" conditions apply.             │
│  RECOMMENDATION: Switch to NEX-GDDP-CMIP6 (SSP2-4.5)                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start: Accessing NEX-GDDP-CMIP6

```python
# Example: Access NEX-GDDP-CMIP6 via AWS Open Data
import xarray as xr
import s3fs

# Connect to AWS S3
fs = s3fs.S3FileSystem(anon=True)

# Example: Get rsds (solar irradiance) for SSP2-4.5 from one model
model = "ACCESS-CM2"
scenario = "ssp245"
variable = "rsds"

# Path pattern
path = f"s3://nex-gddp-cmip6/NEX-GDDP-CMIP6/{model}/{scenario}/r1i1p1f1/{variable}/"

# List available files
files = fs.ls(path)
print(f"Available files: {len(files)}")

# Open one year of data
ds = xr.open_dataset(fs.open(files[0]))

# Subset to Texas region
texas_ds = ds.sel(lat=slice(25, 37), lon=slice(-107, -93))

# Extract for Hayhurst Solar site (31.82°N, -104.09°W)
site_data = ds.sel(lat=31.82, lon=-104.09, method='nearest')
```

---

## References

1. **NEX-GDDP-CMIP6 Documentation:**
   https://www.nccs.nasa.gov/services/data-collections/land-based-products/nex-gddp-cmip6

2. **CORDEX Documentation:**
   https://cordex.org/

3. **CMIP6 Variable List:**
   https://docs.google.com/spreadsheets/d/1UUtoz6Ofyjlpx5LdqhKcwHFz2SGoTQV2_yekHyMfL9Y

4. **SSP Scenario Descriptions:**
   https://www.carbonbrief.org/explainer-how-shared-socioeconomic-pathways-explore-future-climate-change

5. **pvlib Decomposition Models:**
   https://pvlib-python.readthedocs.io/en/stable/reference/irradiance.html

---

*End of CMIP5 vs CMIP6 Comparison Guide*
