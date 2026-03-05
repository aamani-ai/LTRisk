# Data Pipeline — THREDDS, NetCDF, and Point Extraction

> How climate data gets from NASA's servers into our notebook, including THREDDS, NetCDF format, caching, unit conversion, and the full request lifecycle.

---

## 1. The Big Picture

```
NASA NCCS Servers                      Our Notebook
(Greenbelt, Maryland)                  (your laptop)
┌─────────────────────┐               ┌──────────────────────┐
│                     │  HTTP GET     │                      │
│  THREDDS Data       │ <──────────── │  build_thredds_url() │
│  Server             │               │                      │
│                     │ ──────────>   │  fetch_year()        │
│  ~50 TB of NetCDF   │  ~5 KB       │  parse_station_nc()  │
│  files (global,     │  (one point,  │                      │
│  daily, per model)  │   one year)   │  unit_convert()      │
│                     │               │                      │
└─────────────────────┘               │  pd.Series           │
                                      │  (365 daily values)  │
                                      └──────────────────────┘
```

**Key insight**: Each global daily NetCDF file is ~500 MB. We don't download the file. THREDDS NCSS (NetCDF Subset Service) extracts **just one grid point** server-side and sends back ~5 KB. This is what makes the pipeline feasible on a laptop.

---

## 2. What Is THREDDS?

**THREDDS** = Thematic Real-time Environmental Distributed Data Services

It's a Java web application that sits in front of NetCDF files and provides several access methods:

```
THREDDS DATA SERVER (TDS)
┌──────────────────────────────────────────────────┐
│                                                  │
│  OPeNDAP   ← for subsetting by dimension        │
│  NCSS      ← for point/region extraction  <──── WE USE THIS
│  WMS       ← for map tile visualization          │
│  WCS       ← for gridded subsets                 │
│  HTTP      ← for raw file download               │
│                                                  │
│  All methods access the SAME underlying files    │
└──────────────────────────────────────────────────┘
```

**NCSS** (NetCDF Subset Service) is perfect for our use case:
- We give it: latitude, longitude, time range, variable name
- It returns: a tiny NetCDF with just that point's data
- Server does all the heavy lifting (reading the 500 MB file, extracting the grid cell)

---

## 3. The URL Structure

Our base URL:
```
https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6
```

A complete request URL:
```
https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6
  /ACCESS-CM2                          <- model name
  /ssp245                             <- scenario
  /r1i1p1f1                           <- ensemble member
  /tasmax                             <- variable
  /tasmax_day_ACCESS-CM2_ssp245_r1i1p1f1_gn_2040.nc  <- filename
  ?var=tasmax                          <- which variable to extract
  &latitude=31.816                     <- our site latitude
  &longitude=-104.085                  <- our site longitude
  &time_start=2040-01-01T00:00:00Z    <- year start
  &time_end=2040-12-31T23:59:59Z      <- year end
  &accept=netCDF                       <- response format
```

### The v2.0 vs v1 Naming Issue

Some models have updated files with a `_v2.0.nc` suffix, others don't. We try both:

```python
def build_thredds_url(model, scenario, variable, year, lat, lon):
    fname_v2 = f"{variable}_day_{model}_{scenario}_r1i1p1f1_gn_{year}_v2.0.nc"
    fname_v1 = f"{variable}_day_{model}_{scenario}_r1i1p1f1_gn_{year}.nc"
    # Returns BOTH URLs — fetch_year tries v2 first, falls back to v1
    return (url_v2, url_v1)
```

---

## 4. What Is NetCDF?

**NetCDF** = Network Common Data Form. It's the standard file format for climate data:

```
NETCDF FILE STRUCTURE

  ┌─────────────────────────────────────────┐
  │ GLOBAL ATTRIBUTES                        │
  │   title: "CMIP6 daily tasmax"           │
  │   source: "ACCESS-CM2"                  │
  │   calendar: "proleptic_gregorian"       │
  │                                         │
  │ DIMENSIONS                              │
  │   time: 365                             │
  │   station: 1       (point extraction)   │
  │   obs: 365         (alias for time)     │
  │                                         │
  │ VARIABLES                               │
  │   time(obs):        [0, 1, 2, ..., 364] │
  │     units: "days since 2040-01-01"      │
  │     calendar: "noleap"                  │
  │                                         │
  │   tasmax(station, obs): [305.2, 303.8,  │
  │                          308.1, ...]    │
  │     units: "K"   <-- Kelvin!            │
  │                                         │
  │   latitude(station):  [31.875]          │
  │   longitude(station): [-104.0625]       │
  └─────────────────────────────────────────┘
```

**Station format**: When THREDDS does point extraction, the result has `station` and `obs` dimensions instead of `lat/lon/time`. This is why our `parse_station_nc()` function does `.squeeze()` — to remove the size-1 station dimension.

---

## 5. The Calendar Problem

Different climate models use different calendars:

```
CALENDAR TYPES IN CMIP6

  Standard (Gregorian):     365 or 366 days/year (leap years)
  Proleptic Gregorian:      Same but extended before 1582
  noleap (365_day):         Always 365 days (no Feb 29)
  360_day:                  12 months x 30 days = 360 days
  all_leap (366_day):       Always 366 days (every year is leap)

  MODEL             CALENDAR        DAYS/YEAR
  ACCESS-CM2        proleptic       365/366
  MIROC6            noleap          365
  HadGEM3-GC31      360_day         360
  MRI-ESM2-0        proleptic       365/366
```

**Why this matters**: Python's `datetime` doesn't understand `noleap` or `360_day`. You can't just convert "day 60 of a noleap calendar" to a standard date.

**Solution**: We use `cftime` library:

```python
import cftime

# Raw time values from NetCDF: [0, 1, 2, ..., 364]
# Units: "days since 2040-01-01"
# Calendar: "noleap"

cf_dates = cftime.num2date(num_times, units=units, calendar=calendar)
# Returns cftime objects that understand the noleap calendar

# Convert to standard Python datetimes for pandas
times = pd.to_datetime([f"{d.year}-{d.month}-{d.day}" for d in cf_dates])
```

This is why we open NetCDF with `decode_times=False` and handle time decoding manually.

---

## 6. The Caching System

### Two Levels of Cache

```
LEVEL 1: NetCDF File Cache (fetch_year)
─────────────────────────────────────────
  Location: data/cache/thredds/
  Key:      {model}_{scenario}_{variable}_{year}_{lat}_{lon}.nc
  Example:  ACCESS-CM2_ssp245_tasmax_2040_31.8160_-104.0853.nc
  Size:     ~5 KB per file
  Saves:    ~15-60 seconds per HTTP request

  Total for full run:
    2 sites x 7 vars x 2 scenarios x 6 models x 60 years = ~10,080 files
    ~10,080 x 5 KB = ~50 MB of cache

LEVEL 2: Probe Cache (probe_model_cached)
─────────────────────────────────────────
  Location: data/cache/thredds/model_probe_cache.json
  Key:      {model}|{scenario}|{variable}|{year}|{lat}|{lon}
  Value:    true or false
  Saves:    Entire model discovery step (~15 min -> instant)

  Total entries: ~34 models x 2 scenarios x 7 vars x 2 sites x 2 (ssp+hist) = ~1,900
```

### Cache Flow

```
fetch_year() called for ACCESS-CM2, ssp245, tasmax, 2040

  1. Build cache key: "ACCESS-CM2_ssp245_tasmax_2040_31.8160_-104.0853.nc"
  2. Check: does file exist in data/cache/thredds/?
     |
     |── YES (and size > 500 bytes):
     |     Parse the cached .nc file
     |     Return pd.Series
     |     (FAST: ~10ms)
     |
     └── NO:
           Try URL v2.0 -> HTTP GET -> if 200 and size > 500:
             Save .nc to cache
             Parse and return
           Try URL v1 -> same
           Retry up to 3 times with exponential backoff
           Return None if all fail
           (SLOW: 15-60 seconds)
```

---

## 7. Unit Conversion

CMIP6 stores data in SI units. We convert to human-readable units:

```
UNIT CONVERSIONS

  Variable    CMIP6 Unit              Our Unit       Conversion
  ─────────   ─────────────────       ──────────     ──────────────────────
  tasmax      Kelvin (K)              Celsius (C)    subtract 273.15
  tasmin      Kelvin (K)              Celsius (C)    subtract 273.15
  tas         Kelvin (K)              Celsius (C)    subtract 273.15
  pr          kg/m2/s (flux)          mm/day         multiply by 86400
  sfcWind     m/s                     m/s            no conversion needed
  hurs        %                       %              no conversion needed
  rsds        W/m2                    MJ/m2/day      context-dependent
```

```python
def unit_convert(series, variable):
    # Temperature: detect Kelvin by checking if mean > 200
    if variable.startswith("ta") and series.mean() > 200:
        series = series - 273.15

    # Precipitation: flux (kg/m2/s) -> mm/day
    if variable == "pr":
        series = series * 86400

    return series
```

**Why check `mean > 200`?** Some models might already serve data in Celsius (after bias correction). If the mean temperature is 22C, we don't want to subtract 273.15. If the mean is 295K, we do.

---

## 8. The Model Discovery (Probing)

Not all 34 models have data for every variable/scenario combination. Before fetching, we need to find out which models are available:

```
PROBING PROCESS

  For each (site, variable, scenario):

    Step 1: Parallel-probe all 34 models for SSP availability
    ┌──────────────────────────────────────────────┐
    │  ThreadPoolExecutor(max_workers=12)           │
    │                                              │
    │  ACCESS-CM2 ──> HEAD request ──> 200? yes    │
    │  ACCESS-ESM1-5 ──> HEAD ──> 200? yes         │
    │  BCC-CSM2-MR ──> HEAD ──> 404? no            │
    │  ...                                         │
    │  (all 34 in parallel, ~15 sec total)         │
    └──────────────────────────────────────────────┘
    Found: [ACCESS-CM2, ACCESS-ESM1-5, CanESM5, ...]

    Step 2: Parallel-probe found models for historical availability
    ┌──────────────────────────────────────────────┐
    │  (only models from step 1, in parallel)       │
    │  ACCESS-CM2 historical ──> 200? yes           │
    │  ACCESS-ESM1-5 historical ──> 200? yes        │
    │  ...                                         │
    └──────────────────────────────────────────────┘
    Confirmed: [ACCESS-CM2, ACCESS-ESM1-5, ...]

    Step 3: Sort alphabetically, cap at MAX_MODELS (6)
    Final: first 6 alphabetically
```

**Why probe?** Because attempting to fetch 30 years of data from a model that doesn't exist wastes enormous time (30 x 60-second timeouts = 30 minutes wasted per model).

---

## 9. The Full Fetch Loop

For each (site, variable, scenario):

```
1. Get AVAILABLE_MODELS[(site, var, scenario)]  e.g., 6 models

2. For each model:
   a. Fetch baseline: historical, years 1985-2014
      - fetch_model_years() with ThreadPoolExecutor(max_workers=4)
      - 30 parallel HTTP requests (one per year)
      - Each returns pd.Series with ~365 daily values
      - Concatenate into one long Series (~10,950 values)

   b. Fetch future: ssp245 or ssp585, years 2026-2055
      - Same parallel fetch
      - Since 2026 > 2014, all years come from SSP experiment

   c. Unit convert both series

   d. Store in DATA dict:
      DATA[(site, var, scenario)] = {
          "models": [...],
          "baseline_daily": {model: pd.Series, ...},
          "future_daily":   {model: pd.Series, ...},
      }
```

**Runtime estimate** (with warm cache):
- Cache hit: ~10ms per year -> 60 years x 6 models = ~3.6 seconds per combo
- Cache miss: ~30 sec per year -> 60 years x 6 models = ~3 hours per combo (first run only!)

This is why the cache is so important. First run is slow; every run after is fast.

---

## 10. Data Quality Checks

After loading, we verify:

```
QUALITY CHECK TABLE

  site              variable  scenario  model         base_days  nan%  fut_days  nan%
  hayhurst_solar    tasmax    ssp245    ACCESS-CM2    10950      0.0   10950     0.0
  hayhurst_solar    tasmax    ssp245    MIROC6        10875      0.0   10875     0.0
  ...

  Flag if:
  - nan% > 10%  (too many missing values)
  - base_days < 9000  (missing multiple years)
  - value ranges physically impossible (tasmax > 80C, pr < 0)
```

**Why MIROC6 has 10,875 instead of 10,950?** It uses the `noleap` calendar: 30 years x 365 days = 10,950. But some years might have been partially available, giving slightly fewer values. This is normal.

---

## Next

- [06 - Baseline vs Future](06_baseline_vs_future.md) — Why we split time the way we do
