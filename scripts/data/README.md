# scripts/data/ — CMIP6 Data Pipeline

## What This Does

`fetch_cmip6.py` is the canonical script for downloading daily climate data from
NASA's [NEX-GDDP-CMIP6](https://www.nccs.nasa.gov/services/data-collections/land-based-products/nex-gddp-cmip6)
dataset via the THREDDS NCSS (NetCDF Subset Service).

It consolidates fetch logic previously duplicated across:

| Previous location | Issue |
|---|---|
| `scripts/shared/scvr_utils.py` | Basic fetch — hardcoded `r1i1p1f1/gn` only |
| `scripts/presentation/ensemble_exceedance.py` | Enhanced variant discovery, but tightly coupled to plotting |
| `notebook_analysis/03_integrated_scvr_cmip6.ipynb` | Inline copy of fetch functions |
| `scripts/experiments/annual_scvr_test.py` | Outdated copy, no variant discovery |

**Key features:**

- Smart caching — skips download if the file already exists on disk (size > 500 bytes)
- Variant discovery — tries 5 realizations x 4 grids x 2 filename versions per model
- Persistent caches — `model_variant_cache.json` and `model_probe_cache.json` survive across runs
- Resume-friendly — interrupt and restart without re-downloading
- Dry-run mode — inspect cache state without touching the network
- Integrity check — validate cached NetCDF files can be opened

---

## Quick Start

```bash
# Show cache state for Hayhurst Solar (default site), don't download
python scripts/data/fetch_cmip6.py --dry-run

# Fetch all P1_core variables for Hayhurst Solar
python scripts/data/fetch_cmip6.py --site hayhurst_solar

# Fetch a single model/variable/year (good for testing)
python scripts/data/fetch_cmip6.py --models ACCESS-CM2 --variables tasmax --future 2026 2026

# Discover which of the 34 models are available on THREDDS
python scripts/data/fetch_cmip6.py --discover-only

# Validate all cached files can be opened with xarray
python scripts/data/fetch_cmip6.py --dry-run --integrity

# Fetch for the wind site
python scripts/data/fetch_cmip6.py --site maverick_wind

# Skip probing (assume all models exist), show verbose progress
python scripts/data/fetch_cmip6.py --skip-probe --verbose
```

---

## CLI Flags

| Flag | Default | Description |
|---|---|---|
| `--site SITE_ID` | `hayhurst_solar` | Site from `data/schema/sites.json` |
| `--models MODEL [...]` | all 34 (filtered by probe) | Specific CMIP6 models to fetch |
| `--variables VAR [...]` | P1_core from `variables.json` | Climate variables to fetch |
| `--scenarios SCN [...]` | `ssp245 ssp585` | SSP scenarios |
| `--baseline START END` | `1985 2014` | Historical baseline year range (inclusive) |
| `--future START END` | `2026 2055` | Future projection year range (inclusive) |
| `--max-workers N` | `6` | Parallel download threads |
| `--dry-run` | off | Show fetch plan, don't download |
| `--integrity` | off | Validate cached `.nc` files with xarray |
| `--discover-only` | off | Only probe model availability |
| `--skip-probe` | off | Skip probing, assume all models exist |
| `--verbose` | off | Print per-file progress |

---

## Output Folder Structure

```
data/
├── schema/                                  # Committed — source of truth for data contracts
│   ├── sites.json                           # Pilot site registry (lat/lon, capacity, etc.)
│   ├── variables.json                       # Climate variable definitions (priority, units, API params)
│   ├── cmip6_raw_schema.json                # Column spec for raw CMIP6 Parquet files
│   ├── noaa_schema.json                     # Column spec for NOAA GHCN-D observations
│   ├── scvr_schema.json                     # SCVR output spec + methodology
│   ├── VARIABLES.md                         # Human-readable variable reference
│   └── README.md                            # Schema usage guide
│
├── cache/                                   # Not committed — THREDDS download cache
│   └── thredds/
│       ├── *.nc                             # Cached NetCDF files (one per model/scenario/variable/year/location)
│       ├── model_variant_cache.json         # Discovered realization+grid per model|scenario
│       ├── model_probe_cache.json           # Boolean availability per model|scenario|variable|year|location
│       └── fetch_report_*.json              # Timestamped fetch run summaries
│
├── raw/                                     # Not committed — ingested climate data
│   ├── cmip6/
│   │   └── <site_id>/                       # One subdirectory per site
│   │       ├── historical_EC_Earth3P_HR_1980_2014.parquet
│   │       └── ssp245_EC_Earth3P_HR_2015_2049.parquet
│   └── noaa/                                # NOAA GHCN-D station observations
│       └── <county>_<station_id>_<start>_<end>.parquet
│
└── processed/                               # Not committed — computed outputs
    ├── scvr/
    │   └── <site_id>/
    │       ├── cmip6_ensemble_scvr.parquet   # Pooled SCVR across all models
    │       ├── <scenario>_<model>_scvr.parquet
    │       ├── cmip6_scvr_decade.parquet     # Decade-resolved SCVR
    │       ├── cmip6_shape_metrics.parquet   # Distribution shape metrics per decade
    │       └── figures/                      # PNG plots (150 dpi)
    ├── presentation/
    │   └── <site_id>/
    │       └── <variable>/                   # Variable-specific analysis outputs
    │           ├── exceedance_curves_<var>.png
    │           ├── scvr_decomposition_<var>.png
    │           └── ensemble_stats_<var>.csv
    └── hcr/
        └── <site_id>/
            ├── hcr_results.json
            └── hcr_summary.parquet
```

**What gets committed:** Only `data/schema/`. Everything else is in `.gitignore`.

---

## Cache Details

### NetCDF File Naming

Each cached file is one year of daily data for one model/scenario/variable/location:

```
{MODEL}_{SCENARIO}_{VARIABLE}_{YEAR}_{LAT:.4f}_{LON:.4f}.nc
```

Examples:
```
ACCESS-CM2_historical_tasmax_1985_31.8160_-104.0853.nc
MIROC6_ssp245_pr_2040_31.2625_-99.8440.nc
EC-Earth3_ssp585_hurs_2055_31.8160_-104.0853.nc
```

A file is considered **valid** if it exists and is > 500 bytes. Files below this threshold
are treated as corrupt downloads and re-fetched.

### `model_variant_cache.json`

Maps `model|scenario` to the discovered realization and grid label. This avoids
re-probing all 40 URL variants on subsequent runs.

```json
{
  "ACCESS-CM2|historical": {"realization": "r1i1p1f1", "grid": "gn"},
  "EC-Earth3|ssp245":      {"realization": "r1i1p1f1", "grid": "gr"},
  "IPSL-CM6A-LR|ssp585":   {"realization": "r1i1p1f1", "grid": "gr"},
  "GFDL-ESM4|historical":  {"realization": "r1i1p1f1", "grid": "gr1"}
}
```

**Variant search order:** For each model, the script tries combinations of:
- **Realizations:** `r1i1p1f1`, `r1i1p1f2`, `r1i1p1f3`, `r3i1p1f1`, `r4i1p1f1`
- **Grids:** `gn`, `gr`, `gr1`, `gr2`
- **Filename versions:** `_v2.0.nc`, `.nc`

Once a working variant is found, it's cached and used for all future requests
for that model+scenario.

### `model_probe_cache.json`

Boolean cache of whether a model/scenario/variable combination exists on THREDDS.
Prevents redundant HTTP probes.

```json
{
  "ACCESS-CM2|ssp245|tasmax|2041|31.8160|-104.0853": true,
  "CESM2-LENS|ssp245|tasmax|2041|31.8160|-104.0853": false
}
```

Key format: `{model}|{scenario}|{variable}|{probe_year}|{lat:.4f}|{lon:.4f}`

### `fetch_report_*.json`

Timestamped summary saved after each fetch run:

```json
{
  "timestamp": "2026-03-19T16:44:34.457682",
  "site": "hayhurst_solar",
  "lat": 31.815992,
  "lon": -104.0853,
  "summary": {
    "total_tasks": 18360,
    "already_cached": 18180,
    "fetched": 150,
    "failed": 30
  },
  "models_unavailable": ["CESM2-LENS", "GFDL-CM4_gr2", "HadGEM3-GC31-MM"],
  "failed_tasks": [
    {
      "model": "CESM2-LENS",
      "scenario": "ssp245",
      "variable": "tasmax",
      "year": 2030,
      "error": "all URLs failed"
    }
  ]
}
```

---

## Schema Reference

All schema files live in `data/schema/` and are committed to version control.

### A. `sites.json` — Site Registry

Registers pilot assets with coordinates and metadata.

| Field | Type | Description |
|---|---|---|
| `name` | str | Human-readable name |
| `asset_type` | str | `solar_pv` or `wind_turbine` |
| `technology` | str | `crystalline_silicon`, `horizontal_axis`, etc. |
| `lat` | float | Latitude (decimal degrees) |
| `lon` | float | Longitude (decimal degrees, negative = west) |
| `capacity_mw` | float | Nameplate capacity in MW |
| `eul_years` | int | Expected useful life in years |
| `installation_year` | int | Year commissioned |
| `climate_zone` | str | Koppen-style label (`arid_desert`, `semi_arid`) |
| `county` | str | US county |
| `state` | str | US state code |
| `noaa_station_id` | str | Nearest GHCN-D station for validation |
| `open_meteo_model` | str | Open-Meteo Climate API model ID |
| `notes` | str | Site-specific climate and risk notes |

**Current sites:**

| Site ID | Name | Lat | Lon | Type | Capacity |
|---|---|---|---|---|---|
| `hayhurst_solar` | Hayhurst Texas Solar | 31.8160 | -104.0853 | Solar PV | 24.8 MW |
| `maverick_wind` | Maverick Creek Wind | 31.2625 | -99.8440 | Wind | 491.6 MW |

### B. `variables.json` — Climate Variable Definitions

Single source of truth for all climate variables used in the pipeline.

**Priority tiers:**

| Tier | Variables | When Needed |
|---|---|---|
| **P1 — Core** | `tasmax`, `tasmin`, `tas`, `pr`, `sfcWind`, `hurs` | SCVR computation (default for fetch) |
| **P2 — Performance** | `rsds` | Solar generation modeling (pvlib) |
| **P3 — Additional** | `wind_speed_10m_max`, `noaa_tmax` | Validation, future HCR calibration |

**Field structure per variable:**

| Field | Type | Description |
|---|---|---|
| `priority` | str | `P1_core`, `P2_performance`, or `P3_additional` |
| `full_name` | str | Long descriptive name |
| `unit` | str | Physical unit (`degC`, `mm/day`, `m/s`, `percent`, `MJ/m2/day`) |
| `source` | str | `api` (Open-Meteo) or `noaa_api` (GHCN-D) |
| `open_meteo_param` | str | Open-Meteo API parameter name |
| `api_confirmed` | bool | Verified working on Open-Meteo |
| `confirmed_models` | list | Models confirmed to provide this variable |
| `cmip6_standard_name` | str | CF conventions standard name |
| `cmip6_cell_methods` | str | Temporal aggregation method |
| `scvr_indices` | list | SCVR indices derived from this variable |
| `downstream` | list | Downstream applications (HCR, EFR, generation models) |
| `scvr_direction` | str | Whether higher or lower values indicate worse risk |
| `notes` | str | Usage notes and caveats |

**P1 core variables detail:**

| Variable | Unit | CMIP6 Name | SCVR Direction | Key Downstream Use |
|---|---|---|---|---|
| `tasmax` | degC | air_temperature (daily max) | higher is worse | Heat wave SCVR, EFR temperature coefficient |
| `tasmin` | degC | air_temperature (daily min) | lower is worse for freeze | Frost days, cold wave SCVR, freeze-thaw EFR |
| `tas` | degC | air_temperature (daily mean) | higher is worse | Peck's aging model, general trend |
| `pr` | mm/day | precipitation_flux | extremes both directions | Flood HCR (Rx5day), dry spell (soiling, fire) |
| `sfcWind` | m/s | wind_speed | higher extremes worse | Wind cut-out days, Palmgren-Miner fatigue |
| `hurs` | % | relative_humidity | context dependent | Peck's model (heat x humidity), icing HCR |

**Unit conversions (handled by consumers, not fetch script):**
- Temperature: CMIP6 stores in Kelvin — subtract 273.15 if mean > 200
- Precipitation: CMIP6 stores as kg/m^2/s — multiply by 86400 for mm/day

### C. `cmip6_raw_schema.json` — Raw CMIP6 Parquet Columns

Wide-format Parquet files in `data/raw/cmip6/<site_id>/`.

**File naming:** `{scenario}_{model}_{start_year}_{end_year}.parquet`

| Column | dtype | Unit | Valid Range | Priority |
|---|---|---|---|---|
| `date` | datetime64[ns] | — | — | — |
| `year` | int16 | — | — | — |
| `month` | int8 | — | 1–12 | — |
| `doy` | int16 | — | 1–366 | — |
| `tasmax` | float32 | degC | [-60, 60] | P1 |
| `tasmin` | float32 | degC | [-80, 50] | P1 |
| `tas` | float32 | degC | [-70, 55] | P1 |
| `pr` | float32 | mm/day | [0, 1000] | P1 |
| `sfcWind` | float32 | m/s | [0, 120] | P1 |
| `hurs` | float32 | % | [0, 100] | P1 |
| `rsds` | float32 | MJ/m^2/day | [0, 50] | P2 |
| `site_id` | str | — | — | — |
| `scenario` | str | — | historical, ssp245, ssp585 | — |
| `model` | str | — | — | — |

**Invariant checks:**
- `tasmin <= tas <= tasmax` for all rows
- `pr >= 0`, `sfcWind >= 0`, `0 <= hurs <= 100`, `rsds >= 0`
- No duplicate dates per `(site_id, scenario, model)`

**Note:** `tas` can be derived as `(tasmax + tasmin) / 2` if the API does not return it.

### D. `noaa_schema.json` — NOAA GHCN-D Observations

Ground-station observations for cross-validating CMIP6 historical data.

**Source:** NOAA Global Historical Climatology Network Daily (GHCN-D)

**File naming:** `{county}_{station_id}_{start_year}_{end_year}.parquet`

| Column | dtype | Unit | Valid Range | Notes |
|---|---|---|---|---|
| `date` | datetime64[ns] | — | — | Local station time |
| `year` | int16 | — | — | — |
| `month` | int8 | — | 1–12 | — |
| `doy` | int16 | — | 1–366 | — |
| `tmax` | float32 | degC | [-50, 60] | GHCN-D element: TMAX |
| `tmin` | float32 | degC | [-60, 50] | GHCN-D element: TMIN |
| `prcp` | float32 | mm/day | [0, 1000] | GHCN-D element: PRCP |
| `awnd` | float32 | m/s | [0, 100] | Often missing — not all stations record wind |
| `station_id` | str | — | — | e.g., `USC00412019` |
| `county` | str | — | — | Lowercase with underscores |

**Important notes:**
- NOAA data has gaps — do not assume daily completeness
- Relative humidity (`hurs`) and solar radiation (`rsds`) are NOT available from GHCN-D
- Raw GHCN-D temperatures are in tenths of degrees C — convert on ingestion
- Null handling: keep as NaN, do not interpolate without documenting

### E. `scvr_schema.json` — SCVR Output Specification

Long-format Parquet files in `data/output/scvr/<site_id>/`.

**File naming:** `{scenario}_{model}_scvr.parquet`

#### Methodology

| Item | Detail |
|---|---|
| **Definition** | SCVR = fractional increase in area under empirical exceedance curve |
| **Formula** | `SCVR = (area_future - area_baseline) / area_baseline` |
| **Exceedance area** | Trapezoidal rule over rank-sorted daily values |
| **Baseline** | 1980–2014 (ERA5-calibrated) |
| **Future windows** | 20-year windows centered on target years |
| **Target years** | 2030, 2035, 2040, 2045, 2050 |

#### Interpretation

| SCVR Value | Meaning |
|---|---|
| `= 0` | No change from baseline |
| `> 0` | Extremes more frequent or intense (e.g., more hot days) |
| `< 0` | Extremes less frequent (e.g., fewer freeze days under warming) |
| `0.00–0.10` | Low change |
| `0.10–0.30` | Moderate change |
| `0.30–0.60` | High change |
| `> 0.60` | Very high change — review carefully, may indicate tail sensitivity |

#### Columns

| Column | dtype | Description |
|---|---|---|
| `site_id` | str | Site identifier from `sites.json` |
| `scenario` | str | `ssp245` or `ssp585` |
| `model` | str | CMIP6 model identifier |
| `center_year` | int16 | Center of the 20-year future window |
| `variable` | str | Climate variable or derived index |
| `scvr` | float32 | SCVR value (valid range: -1.0 to 10.0) |
| `area_baseline` | float32 | Baseline exceedance curve area |
| `area_future` | float32 | Future exceedance curve area |
| `window_start_year` | int16 | First year of future window (`center_year - 10`) |
| `window_end_year` | int16 | Last year of future window (`center_year + 10`) |
| `n_baseline_days` | int32 | Valid baseline days used |
| `n_future_days` | int32 | Valid future days used |

**Allowed variable values:** `tasmax`, `tasmin`, `tas`, `pr`, `sfcWind`, `hurs`, `rsds`,
`heat_wave_days`, `frost_days`, `icing_days`, `rx5day`, `max_dry_spell_days`,
`wind_cutout_days`, `fwi_mean`

#### Decade-Resolved Output

Additional files for temporal progression analysis:

**`cmip6_scvr_decade.parquet`** — SCVR per 10-year window (all models pooled):
- Columns: `site_id`, `scenario`, `variable`, `decade` (e.g., `2026-2035`), `scvr`, `area_baseline`, `area_future`, `n_future_days`

**`cmip6_shape_metrics.parquet`** — Distribution shape metrics per decade:
- Columns: `site_id`, `scenario`, `variable`, `period`, `mean`, `variance`, `skewness`, `p95`, `p99`, `gev_shape`, `gev_loc`, `gev_scale`

#### Variable Strategy for Decade SCVR

| Strategy | Variables | Method |
|---|---|---|
| **anchor_3_linear** | `tasmax`, `tasmin`, `tas` | 3 decade anchors → linear trend → annual interpolation |
| **period_average** | `pr`, `hurs`, `sfcWind`, `rsds` | Decade-level SCVR directly (too noisy for linear fitting) |

#### Downstream Use

| Consumer | What it takes from SCVR |
|---|---|
| **HCR** (Hazard Change Ratio) | SCVR → hazard-specific scaling factors → business interruption loss |
| **EFR** (Equipment Failure Ratio) | SCVR → Peck's, Coffin-Manson, Palmgren-Miner → equipment degradation |
| **NAV** (Net Asset Value) | HCR + EFR → CFADS adjustment → impaired NAV |

---

## Model Coverage

### All 34 NEX-GDDP-CMIP6 Models

```
ACCESS-CM2       ACCESS-ESM1-5    BCC-CSM2-MR      CanESM5
CESM2            CESM2-LENS       CMCC-CM2-SR5     CMCC-ESM2
CNRM-CM6-1       CNRM-ESM2-1      EC-Earth3        EC-Earth3-Veg-LR
FGOALS-g3        GFDL-CM4         GFDL-CM4_gr2     GFDL-ESM4
GISS-E2-1-G      HadGEM3-GC31-LL  HadGEM3-GC31-MM  IITM-ESM
INM-CM4-8        INM-CM5-0        IPSL-CM6A-LR     KACE-1-0-G
KIOST-ESM        MIROC6           MPI-ESM1-2-HR    MPI-ESM1-2-LR
MRI-ESM2-0       NESM3            NorESM2-LM       NorESM2-MM
TaiESM1          UKESM1-0-LL
```

### Current Cache State (Hayhurst Solar)

- **31 models** cached across 3 scenarios (historical, ssp245, ssp585)
- **7 variables** cached (tasmax, tasmin, tas, pr, sfcWind, hurs, rsds)
- **30 years** per scenario (historical: 1985–2014, future: 2026–2055)
- **~18,180 files** total

**3 models NOT available on THREDDS:**
- `CESM2-LENS`
- `GFDL-CM4_gr2`
- `HadGEM3-GC31-MM`

**Known variable gaps (11 models):**

| Model | Missing Variables |
|---|---|
| BCC-CSM2-MR | hurs |
| CESM2 | tasmax, tasmin |
| CMCC-CM2-SR5 | tas, tasmax, tasmin |
| CNRM-CM6-1 | tas |
| GISS-E2-1-G | tas |
| HadGEM3-GC31-LL | tas |
| IITM-ESM | tasmax, tasmin |
| INM-CM5-0 | tas |
| IPSL-CM6A-LR | tas |
| NESM3 | hurs |
| UKESM1-0-LL | tas |

These gaps are per-variable, across all scenarios. 20 models have complete coverage
of all 7 variables.

---

## Adding a New Site

1. Add the site entry to `data/schema/sites.json` with all required fields
   (lat, lon, asset_type, capacity_mw, eul_years, etc.)

2. Run a dry-run to verify the site is recognized:
   ```bash
   python scripts/data/fetch_cmip6.py --site your_new_site --dry-run --skip-probe
   ```

3. Discover available models:
   ```bash
   python scripts/data/fetch_cmip6.py --site your_new_site --discover-only
   ```

4. Fetch all data:
   ```bash
   python scripts/data/fetch_cmip6.py --site your_new_site
   ```

5. Run downstream notebooks (SCVR, HCR) with the new `SITE_ID`.
