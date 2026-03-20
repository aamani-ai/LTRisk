# From NASA Data to SCVR — The Full Pipeline

> A non-technical walkthrough of how we download climate model data, what it contains, and how we turn it into the SCVR numbers that feed the financial model.

---

## 1. The Pipeline at a Glance

```
NASA THREDDS Server          Our Pipeline              Outputs
(Greenbelt, Maryland)
                          ┌─────────────────┐
  500 MB global files     │  fetch_cmip6.py │     ~30,000 small files
  (we never download      │                 │     (~5 KB each, ~50 MB total)
   these directly)        │  Downloads just  │     Cached in data/cache/thredds/
           │              │  ONE grid cell   │
           │              │  per request     │          │
           ▼              └─────────────────┘          ▼
                                                ┌──────────────────┐
  34 climate models                             │ compute_scvr.py  │
  × 2 scenarios (SSP2-4.5, SSP5-8.5)           │                  │
  × 6 variables                                 │ Pools all models │
  × 60 years (30 baseline + 30 future)          │ into one big     │
  = ~24,000 daily time series                   │ ensemble, builds │
                                                │ exceedance curves│
                                                └──────────────────┘
                                                        │
                                                        ▼
                                                 scvr_report.json
                                                 (the master output)
                                                        │
                                                        ▼
                                                 NB04: HCR computation
                                                 NB05: EFR (future)
                                                 NB06: NAV impairment (future)
```

**In one sentence**: We download daily weather data from 34 climate model simulations, measure how much the distribution of extremes shifts between past and future, and express that shift as a single number (SCVR) per variable.

---

## 2. Where the Data Comes From

### The Dataset: NEX-GDDP-CMIP6

**NEX-GDDP-CMIP6** is a publicly available dataset produced by NASA. It takes raw output from 34 global climate models (part of the international CMIP6 project) and refines it:

```
Raw CMIP6 Model Output            NASA NEX-GDDP-CMIP6
(~100 km grid, some biases)       (25 km grid, bias-corrected)

  ┌─────────────────┐             ┌─────────────────┐
  │  ░░░░░░░░░░░░░  │   BCSD      │  ▓▓▓▓▓▓▓▓▓▓▓▓▓  │
  │  ░░░░░░░░░░░░░  │  -------->  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓  │
  │  ░░░░░░░░░░░░░  │  Bias       │  ▓▓▓▓▓▓▓▓▓▓▓▓▓  │
  │  ░░░░░░░░░░░░░  │  Correction │  ▓▓▓▓▓▓▓▓▓▓▓▓▓  │
  └─────────────────┘  + Spatial   └─────────────────┘
                       Downscaling
  Coarse grid (~100km)             Fine grid (~25km)
  May be too warm/cold             Adjusted to match
  in some regions                  observed climate patterns
```

**BCSD** (Bias Correction Spatial Disaggregation) is NASA's method for:
1. **Bias correction**: Adjusting the model output so that the historical period matches observed climate (from ERA5/GMFD reanalysis)
2. **Spatial downscaling**: Increasing resolution from ~100 km to ~25 km using observed spatial patterns

This means we get daily values that are physically consistent with the model's climate projections but corrected for known systematic errors.

**Reference**: Thrasher, B., Wang, W., Michaelis, A. et al. NASA Global Daily Downscaled Projections, CMIP6. *Scientific Data* **9**, 262 (2022). https://doi.org/10.1038/s41597-022-01393-4

### What's in the Dataset

**34 climate models** — each developed by a different research centre worldwide:

| # Models | Research Centres | Examples |
|----------|-----------------|----------|
| 7 | Europe | EC-Earth3, CNRM-CM6-1, IPSL-CM6A-LR, UKESM1-0-LL, ... |
| 8 | North America | GFDL-ESM4, GISS-E2-1-G, CESM2, CanESM5, ... |
| 9 | Asia-Pacific | MIROC6, MRI-ESM2-0, ACCESS-CM2, BCC-CSM2-MR, ... |
| 10 | Other | NorESM2-LM, MPI-ESM1-2-HR, INM-CM5-0, KIOST-ESM, ... |

Each model is an independent simulation of Earth's climate. They agree on the big picture (warming) but disagree on details (how much rain in Texas in 2040). Using 34 models captures this **structural uncertainty** — the spread across models tells us how confident the projection is.

### One Realization Per Model

Each model contributes a **single simulation run** (called a "realization"). Some models (like CanESM5) have 50+ runs in the raw CMIP6 archive, but NASA downscaled just one per model to keep the dataset manageable.

Each run is identified by a **variant label** like `r1i1p1f1`:

```
r1 i1 p1 f1
│  │  │  │
│  │  │  └─ f = forcing variant (which aerosol/land-use dataset was used)
│  │  └──── p = physics version (which sub-grid parameterization scheme)
│  └─────── i = initialization method (how the simulation was started)
└────────── r = realization number (different initial conditions → different weather)
```

Most models use `r1i1p1f1` (realization 1, default everything). But some centres chose a different primary run:

| Variant | Models | Why |
|---------|--------|-----|
| `r1i1p1f1` | 24 models (most) | Default — first realization, standard forcing |
| `r1i1p1f2` | CNRM-CM6-1, CNRM-ESM2-1, GISS-E2-1-G, MIROC-ES2L, UKESM1-0-LL | Different forcing dataset (f2) — centre's recommended run |
| `r1i1p1f3` | HadGEM3-GC31-LL, HadGEM3-GC31-MM | Different forcing (f3) |
| `r3i1p1f1` | FGOALS-g3, CESM2-WACCM | Third realization (r3) |
| `r4i1p1f1` | CESM2 | Fourth realization (r4) |

**Key point**: These are NOT multiple runs from the same model. NASA provides **exactly one realization per model** in NEX-GDDP-CMIP6. The different labels just identify which single run each centre chose as its primary submission.

This means the spread across our 34 models captures **structural uncertainty** (different models disagree) but not **internal variability** (different weather trajectories within the same model). For our 30-year windows, this is acceptable — internal variability averages out over decades.

Our download script (`fetch_cmip6.py`) handles variant discovery automatically: it tries `r1i1p1f1` first, then falls back to f2, f3, r3, r4 until it finds the one that exists on the THREDDS server for each model.

### Data Format: NetCDF

Each file NASA provides is in **NetCDF** (Network Common Data Form) — a binary format designed for array-oriented scientific data. After our NCSS point extraction, each cached file contains:

```
data/cache/thredds/ACCESS-CM2_ssp245_tasmax_2030_31.8160_-104.0853.nc
│                  │          │      │      │    │
│                  │          │      │      │    └─ Longitude
│                  │          │      │      └────── Latitude
│                  │          │      └───────────── Year
│                  │          └──────────────────── Variable
│                  └─────────────────────────────── Scenario
└────────────────────────────────────────────────── Model name

Contents (~5 KB):
  ┌──────────────────────────────────┐
  │ time: [2030-01-01, ..., 2030-12-30]  │  ← 365 daily timestamps
  │ tasmax: [308.2, 305.1, 311.4, ...]   │  ← daily values (Kelvin)
  │ lat: 31.8160                         │  ← grid cell latitude
  │ lon: -104.0853                       │  ← grid cell longitude
  │ calendar: "noleap"                   │  ← model's calendar type
  └──────────────────────────────────┘
```

**Calendar quirk**: Climate models use different calendar systems — some have 365 days (noleap), some 360 days (360_day), some include leap years (proleptic_gregorian). Our pipeline handles all of these using the `cftime` library, converting everything to standard pandas timestamps.

**Unit conversion** happens at load time:
- Temperature: Kelvin → Celsius (subtract 273.15)
- Precipitation: kg/m²/s → mm/day (multiply by 86,400)
- Other variables: used as-is

**9 variables available**:

| Variable | What It Is | Units (raw → our units) |
|----------|-----------|------------------------|
| **tasmax** | Daily maximum temperature | K → °C |
| **tasmin** | Daily minimum temperature | K → °C |
| **tas** | Daily mean temperature | K → °C |
| **pr** | Precipitation | kg/m²/s → mm/day |
| **hurs** | Relative humidity | % |
| **sfcWind** | Near-surface wind speed | m/s |
| huss | Specific humidity | kg/kg |
| rsds | Solar radiation (downwelling shortwave) | W/m² |
| rlds | Longwave radiation | W/m² |

We currently use the **top 6** (bold) as our P1 core variables. The bottom 3 (huss, rsds, rlds) are available but not yet integrated.

---

## 3. What We Download

### Not the Whole Globe — Just One Point

NASA's THREDDS server lets us extract data for a **single grid cell** without downloading the full global file (~500 MB). This is called NCSS (NetCDF Subset Service). Each request returns ~5 KB — the daily values for one year, one model, one variable, at our site's coordinates.

```
WHAT WE REQUEST:
  "Give me daily tasmax for ACCESS-CM2 at 31.82°N, 104.09°W for 2030"

WHAT WE GET:
  365 daily values (one per day) ≈ 5 KB

WHAT WE DON'T DOWNLOAD:
  The full global grid: 720 × 1440 grid cells × 365 days ≈ 500 MB
```

### Time Windows

| Period | Years | Experiment | Purpose |
|--------|-------|-----------|---------|
| **Baseline** | 1985–2014 | historical | "What climate looked like" |
| *(gap)* | 2015–2025 | — | Not used (observed period, models diverge from reality) |
| **Future** | 2026–2055 | ssp245 / ssp585 | "What climate will look like" |

**30 years per period** ensures we capture enough natural variability (El Nino cycles, wet/dry years) to build a robust statistical picture.

**Important distinction**: "Historical" here means the models' **simulation** of past climate — not raw observations. Each model was run with observed greenhouse gas concentrations as input, producing its own version of 1985–2014 weather. This is still model output, just driven by known forcings rather than future scenarios.

Each model's run is one continuous simulation — the split at ~2014 is just where the forcing inputs switch from "what actually happened" to "what we assume will happen":

```
ACCESS-CM2:  [...1985...2000...2014]  →  [2015...2040...2055]
              ←── historical ──────→     ←──── ssp245 ──────→
              (observed GHG forcing)      (projected GHG scenario)

Same model, same physics, same realization — just different inputs.
All 28 models run both experiments, so baseline and future are an apples-to-apples comparison.
```

ERA5 (the European reanalysis dataset) enters only indirectly: NASA used it as the reference when bias-correcting the models (the BCSD step in Section 2). So the model outputs are *adjusted* to match ERA5's statistical patterns, but the daily values we download are model-generated, not observed.

### Caching

Every file is downloaded once and cached locally:

```
data/cache/thredds/
  ACCESS-CM2_historical_tasmax_1985_31.8160_-104.0853.nc
  ACCESS-CM2_historical_tasmax_1986_31.8160_-104.0853.nc
  ...
  ACCESS-CM2_ssp245_tasmax_2026_31.8160_-104.0853.nc
  ...
```

On a warm cache (all files present), the entire SCVR computation takes ~30 seconds instead of hours.

---

## 4. How We Turn Daily Data into SCVR

### Step 1: Pool All Models Together

For each variable and scenario, we concatenate daily values from **all models** into one big array:

```
31 models × 30 years × 365 days ≈ 340,000 daily values

Baseline pool:  [35.2, 36.1, 33.8, 37.5, ... ]  ← 340,000 tasmax values (1985–2014)
Future pool:    [36.4, 37.3, 35.1, 38.9, ... ]  ← 340,000 tasmax values (2026–2055)
```

This pooling approach treats all models as equally valid samples of possible climate — it captures the full range of model uncertainty in one distribution.

### Step 2: Build Exceedance Curves

Sort both pools from highest to lowest and plot:

```
Temperature (°C)
    ▲
 46 │                              ╭─── Future (shifted right = warmer)
 44 │                         ╭────╯
 42 │                    ╭────╯    ╭─── Baseline
 40 │               ╭────╯   ╭────╯
 38 │          ╭────╯   ╭────╯
 36 │     ╭────╯   ╭────╯
 34 │╭────╯   ╭────╯
    └──────────────────────────────────► Exceedance probability
      0%     25%     50%     75%    100%
     (hottest days)            (coolest days)
```

The **area under each curve** summarizes the entire distribution in one number.

### Step 3: Compute SCVR

```
SCVR = (Area_future − Area_baseline) / Area_baseline
```

That's it. SCVR is the fractional change in area under the exceedance curve.

- **SCVR = +0.08** means the future distribution has 8% more area → more extreme days
- **SCVR = −0.03** means 3% less area → fewer extreme days
- **SCVR ≈ 0.00** means little change in the distribution

### Step 4: Annual Progression

One epoch-level SCVR isn't enough — we need a value **per year** for the financial model. For temperature variables, we split the future into three 10-year windows:

```
Window 1: 2026–2035  →  SCVR₁
Window 2: 2036–2045  →  SCVR₂
Window 3: 2046–2055  →  SCVR₃

Then fit a line through the three midpoints:

SCVR
  ▲
  │              ·  SCVR₃
  │         ·
  │    ·  SCVR₂
  │  ·
  │·  SCVR₁
  └────────────────────► Year
   2026  2030  2040  2050  2055

Annual SCVR = linear interpolation → 30 values (one per year)
```

This captures the gradual progression of climate change over the asset's lifetime.

---

## 5. What Comes Out

### The Master Output: `scvr_report.json`

This JSON file contains everything downstream notebooks need:

| Section | What It Contains |
|---------|-----------------|
| **ensemble_scvr** | One SCVR per variable per scenario (the headline numbers) |
| **decade_scvr** | SCVR per decade (shows progression: 2026-35, 2036-45, 2046-55) |
| **annual_scvr** | 30 annual SCVR values per variable per scenario |
| **companion_metrics** | Per-model SCVR, tail confidence flags, model agreement |
| **shape_metrics** | Distribution statistics (mean, std, percentiles, skewness) |
| **anchor_fits** | Linear fit parameters (slope, intercept, R²) for temperature |

### Confidence Flags

Not all SCVR values are equally trustworthy. The companion metrics flag each variable:

| Flag | Meaning | Example |
|------|---------|---------|
| **HIGH** | Models agree, mean and tail shift in same direction | tasmax (clear warming signal) |
| **MODERATE** | Reasonable agreement, some model spread | tasmin, sfcWind |
| **LOW** | Large model spread, weak signal | pr under SSP2-4.5 |
| **DIVERGENT** | Mean and tail signals disagree (mean says one thing, extremes say another) | pr under SSP5-8.5 |

### What Happens Next

SCVR feeds into the rest of the impairment chain:

```
SCVR (distribution shift)
  │
  ▼
HCR (hazard change ratio) ← NB04: "SCVR says +8% shift → that means +20% more heat wave days"
  │
  ▼
EFR (equipment failure rate) ← NB05 (future): "20% more heat waves → X% faster panel degradation"
  │
  ▼
NAV impairment ← NB06 (future): "Faster degradation → $Y reduction in Net Asset Value"
```

---

## 6. Key Numbers: Hayhurst Texas Solar

Actual SCVR results for our first site (31.82°N, 104.09°W):

| Variable | SSP2-4.5 | SSP5-8.5 | Confidence | What It Means |
|----------|----------|----------|------------|---------------|
| tasmax | +0.069 | +0.080 | HIGH | Hotter extremes, strong signal |
| tasmin | +0.144 | +0.174 | MODERATE | Warmer nights, bigger shift than days |
| tas | +0.088 | +0.104 | HIGH | Mean temperature rising |
| pr | −0.001 | −0.007 | LOW / DIVERGENT | Precipitation signal unclear |
| sfcWind | −0.022 | −0.026 | MODERATE / HIGH | Slight wind decrease |
| hurs | −0.031 | −0.036 | MODERATE | Slightly drier air |

**Key takeaway**: Temperature signals are strong and consistent (HIGH confidence). Precipitation is noisy and near-zero — this is why we use Pathway B (direct counting) instead of Pathway A (SCVR scaling) for precipitation hazards in the HCR step.

---

## 7. References

**Primary dataset**:
- Thrasher, B., Wang, W., Michaelis, A. et al. NASA Global Daily Downscaled Projections, CMIP6. *Scientific Data* **9**, 262 (2022). https://doi.org/10.1038/s41597-022-01393-4

**Technical notes**:
- [NEX-GDDP-CMIP6 Tech Note v1](https://www.nccs.nasa.gov/sites/default/files/NEX-GDDP-CMIP6-Tech_Note.pdf)
- [NEX-GDDP-CMIP6 Tech Note v2](https://www.nccs.nasa.gov/sites/default/files/NEX-GDDP-CMIP6-v2-Tech_Note.pdf)
- [Google Earth Engine catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GDDP-CMIP6)

**Deeper dives in our docs**:
- [02 — CMIP6 and Climate Models](02_cmip6_models.md) — model details, bias correction, ensemble approach
- [04 — SCVR Methodology](../B_scvr_methodology/04_scvr_methodology.md) — step-by-step SCVR computation, edge cases
- [10 — Data Pipeline](../D_technical_reference/10_data_pipeline.md) — THREDDS, NetCDF, caching, fetch code details
