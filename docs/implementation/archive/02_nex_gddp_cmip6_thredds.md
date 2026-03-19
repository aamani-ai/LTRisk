# NASA NEX-GDDP-CMIP6 Multi-Model Ensemble Analysis

## Overview
This notebook (`NEX_GDDP_CMIP6_THREDDS.ipynb`) performs a high-efficiency multi-model ensemble analysis of climate data using the **NASA NEX-GDDP-CMIP6** dataset. The primary focus is generating a historical baseline versus future SSP (Shared Socioeconomic Pathway) scenario comparison for specific geographic point locations (energy assets).

Instead of relying on heavy static files, it establishes a workflow for programmatic climate risk screening out to the end of the century.

---

## Why these Time Periods? (1985–2014 vs 2070–2099)

### The Historical Baseline: 1985–2014
The notebook uses 1985–2014 as the "historical" baseline. This is a very specific standard in modern climate science for CMIP6 models:
1. **CMIP6 Historical Cutoff**: In the CMIP6 framework, "historical" simulations (which are driven by observed, real-world atmospheric concentrations) end precisely in **2014**. Anything from 2015 onwards is considered a "future projection" driven by SSP scenarios. 
2. **The 30-Year Climatology Rule**: Climate science typically uses a 30-year period to establish a baseline "climatology." A 30-year window is long enough to average out natural, short-term anomalies (like El Niño/La Niña), but short enough to isolate a specific climate state.
3. **Avoiding Scenario Overlap**: Choosing a 30-year block that ends exactly when the historical data ends (1985 + 30 years = 2014) gives us the most up-to-date representation of our *current* climate without bleeding into the speculative future.

### The Future Projection: Climate Science vs. Asset Reality

When determining what future time window to analyze, you essentially have two paths depending on your goal: **Scientific Standardization** vs **Financial Asset Reality**.

**1. The Strict Climate Science Standard (IPCC / WMO)**
If you are publishing a whitepaper or adhering strictly to international climate literature, you must use predefined blocks so your data aligns with the rest of the world.
* **IPCC AR6 Standard (20-year blocks):** `2021–2040` (Near-term) or `2041–2060` (Mid-term).
* **WMO Standard (30-year blocks):** `2020–2049` (calculated in standard decades).

**2. The Infrastructure / Financial Reality (Dynamic Matching)**
You bring up an extremely valid point: it's 2026. If you use the IPCC's `2021-2040` block for a brand new solar farm, you are completely missing the years 2041–2056. This is a massive blind spot because those later years are precisely when climate impacts will be more severe *and* when the physical hardware is most degraded and vulnerable.

For an advanced infrastructure screening tool like **Riskik**, **your honest competitive advantage is to completely ignore rigid IPCC blocks and dynamically match the exact timeline of the asset.** 
This custom approach is heavily championed by the financial sector (e.g., UNEP FI, NGFS, and Zurich Resilience) over standard climate baseline periods.

If a commercial developer inputs:
* **Construction Start:** 2026
* **Operational Lifespan:** 30 years

Your code should accurately query CMIP6 for exactly **2026–2055**. 

**What if the asset was built in the past (e.g., 2010 or 2020)?**
This dynamic framework works flawlessly for existing assets, and in fact, highlights its superiority over static 30-year blocks. If a solar farm was built in 2010 with a 30-year lifespan, its true hazard exposure runs from **2010–2039**.
* Because CMIP6 "Historical" data ends in 2014, your engine will simply pull the `historical` forcing data for 2010–2014.
* It will then seamlessly switch to pulling the SSP scenario data (e.g., `ssp245` or `ssp585`) for the years 2015–2039.
* You fuse those two arrays together to represent the *true* exact hazard lifecycle of the asset.
A static framework (like using an IPCC 2021-2040 block) would be totally blind to the first 11 years of that specific asset's life.

**Why this is better for LTRisk:**
* **Accuracy over Dogma:** You aren't writing an IPCC report; you are estimating the probability of a physical failure or insurance payout during the time the asset actually exists. Neglecting asset-level lifespan granularity is widely cited by financial regulators as a primary reason physical climate losses are underestimated.
* **Financial Modeling:** Net Present Value (NPV) and Return on Investment (ROI) models require exact year-over-year operational degradation timelines.
* **Non-Stationary Risk:** What was a 1-in-100 year event in 2020 might be a 1-in-20 year event by 2050. Averaging this out over a generic 2021-2040 block dilutes the extreme tail-risk hitting the asset at the end of its life.

**Conclusion:** Do not force a 2026 project into a 2021-2040 box. Change `FUTURE_YEARS` dynamically to perfectly wrap the specific lifetime of the asset being evaluated (e.g., `FUTURE_YEARS = (2026, 2055)`).
* **The Solution**: The notebook uses the **NCCS THREDDS NetCDF Subset Service (NCSS)**. This server-side capability allows the code to pass exact latitude and longitude coordinates in a URL. The server processes the request and sends back a tiny payload (a few kilobytes) containing only the time-series data for that specific coordinate.
* **Threading**: It uses Python's `ThreadPoolExecutor` to fetch these years concurrently, parsing the NCCS requests rapidly and caching them locally in a `cmip6_cache` directory so subsequent runs are instant.

### 2. Model Discovery and Parameterization
* The notebook defines `SITES` as an array of dictionaries containing Asset Names, Lat/Lons, and Target Variables (e.g., `tasmax` for Daily Max Temperature, `sfcWind` for Wind Speed).
* It tests all 34 available CMIP6 models by sending a trial request to see which models actually contain the requested variable for the requested baseline and future scenarios. It caps the selection at `MAX_MODELS = 6` to keep processing fast during testing.

### 3. Data Normalization
Because climate models are built by different global institutions, they have quirks:
* **Calendars**: Some models use standard calendars (365/366 days), while others use `noleap` (always 365 days) or `360_day` (twelve 30-day months) calendars to simplify math. The notebook uses the `cftime` library to decode these diverse calendars into standard Pandas Datetime indexes.
* **Units**: It automatically converts Kelvin to Celsius (if the mean temperature > 200) and transforms precipitation flux (`kg/m²/s`) into standard `mm/day`.
* **Aggregation**: Daily data is too noisy. The notebook aggregates the data based on user configuration (`TIME_AGG = "annual_mean"`).

### 4. Statistical Analysis & Enveloping
The core output of the notebook is generating risk envelopes. It computes exactly how the distribution of weather events shifts between the 1985-2014 baseline and the future timeframe. It evaluates the models two ways:

1. **Pooled Method**: It flattens all arrays. For 6 models and 30 years, it turns a `(30, 6)` matrix into a flat array of 180 data points for the baseline, and 180 for the future. It then finds the real ensemble probability percentiles (P10, P50 Median, P90) across this merged distribution. 
2. **Per-Model Method**: It runs the same statistics *independently* for every single model. This is critical for uncertainty analysis because it allows the user to see if the models agree with each other or if one rogue model is skewing the Pooled results.

### 5. Outputs
The script outputs styled Pandas DataFrames showing exact numerical shifts ($\Delta$) in:
* Mean, Median (P50), Std Dev, Mins, Maxes
* **P10 to P90 Spreads**: Shows how the "tails" of the extreme weather distributions are widening or shifting under climate change.
