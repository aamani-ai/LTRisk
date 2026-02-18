# data/

Stores all climate and asset data for the LTRisk project.
Nothing in `raw/` or `processed/` is committed to version control (add to `.gitignore`).
`schema/` is always committed — it is the source of truth for data contracts.

---

## Folder Layout

```
data/
├── raw/
│   ├── cmip6/            # Daily CMIP6 climate projections per site (Parquet, wide format)
│   └── noaa/             # NOAA GHCN daily observations for baseline validation (Parquet)
├── processed/
│   └── scvr/             # Computed SCVR tables and output figures per site
└── schema/               # JSON schema files and site/variable registries (committed)
```

---

## File Naming Conventions

### `raw/cmip6/<site_id>/`

```
baseline_ERA5_<start>_<end>.parquet          # ERA5-calibrated historical baseline
<scenario>_<model>_<start>_<end>.parquet     # Future CMIP6 projections
```

Examples:
- `hayhurst_solar/baseline_ERA5_1980_2014.parquet`
- `hayhurst_solar/ssp245_MRI-ESM2-0_2015_2050.parquet`

### `raw/noaa/<county>_<station_id>_<start>_<end>.parquet`

Example: `culberson_USC00412019_2000_2024.parquet`

### `processed/scvr/<site_id>/`

```
<scenario>_<model>_scvr.parquet     # SCVR table (variable × center_year)
figures/                            # PNG plots saved from notebooks (150 dpi)
```

---

## Column Schemas

See `schema/cmip6_raw_schema.json`, `schema/noaa_schema.json`, and `schema/scvr_schema.json`
for full column definitions, dtypes, and units.

---

## Adding a New Site

1. Add the site entry to `schema/sites.json`.
2. Run the data acquisition section of the relevant notebook with the new `site_id`.
3. Raw files land in `raw/cmip6/<site_id>/` automatically.

---

## Climate Data Source

Raw CMIP6 projections come from the **Open-Meteo Climate API**
(https://open-meteo.com/en/docs/climate-api), which serves pre-extracted
NEX-GDDP-CMIP6 point data. No API key required.

Historical baseline uses ERA5-calibrated data from the same API
(period 1980–2014 unless otherwise noted).
