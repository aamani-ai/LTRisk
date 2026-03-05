# LTRisk Learning Guide

A comprehensive guide to the climate science, data engineering, and financial methodology behind the LTRisk project. Start from the top if you're new, or jump to any section.

---

## Guides

| # | Topic | What You'll Learn |
|---|---|---|
| [01](01_climate_science_fundamentals.md) | **Climate Science Fundamentals** | Climate vs weather, greenhouse effect, what warming means for assets, the 6 variables we track, extreme events, feedback loops |
| [02](02_cmip6_and_climate_models.md) | **CMIP6 and Climate Models** | What a climate model simulates, CMIP6 history, the 34 NEX-GDDP models, ensemble approach, bias correction, model naming conventions |
| [03](03_ssp_scenarios.md) | **SSP Scenarios** | Why no scenarios before 2014, all 5 pathways in detail with emissions/temperature plots, why we use SSP2-4.5 + SSP5-8.5, common misconceptions |
| [04](04_scvr_methodology.md) | **SCVR Methodology** | Step-by-step computation with numerical examples, exceedance curves, area comparison, the actual code, why daily not annual, interpretation guide |
| [05](05_data_pipeline.md) | **Data Pipeline** | THREDDS server, NCSS point extraction, NetCDF format, the calendar problem, two-level caching, unit conversion, model probing, full fetch loop |
| [06](06_baseline_vs_future.md) | **Baseline vs Future** | Why 1985-2014 baseline, why 2026-2055 future, why the gap is correct, ensemble pooling mechanics, comparison of alternative approaches |
| [07](07_from_climate_to_finance.md) | **From Climate to Finance** | The full SCVR -> HCR -> EFR -> NAV chain, Peck's model, Coffin-Manson, Palmgren-Miner, business interruption, useful life shortening, worked example |

---

## Reading Order

**If you're completely new** to climate science:
> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07

**If you understand climate basics** but not our methodology:
> 03 -> 04 -> 06 -> 07

**If you just want to understand the code** in Notebook 03:
> 04 -> 05 -> 06

**If you want the financial/business perspective**:
> 07 (then 04 for the SCVR details)

---

## Quick Reference

### Key Numbers

| Item | Value | Source |
|---|---|---|
| Baseline period | 1985-2014 | IPCC AR6 standard |
| Future period | 2026-2055 | Asset construction + 30yr lifespan |
| CMIP6 models available | 34 | NEX-GDDP-CMIP6 |
| Models used per combo | up to 6 | MAX_MODELS cap |
| Scenarios | SSP2-4.5, SSP5-8.5 | Moderate + high emissions |
| Variables (P1 core) | tasmax, tasmin, tas, pr, sfcWind, hurs | variables.json |
| Grid resolution | 0.25 x 0.25 degrees (~25 km) | NEX-GDDP-CMIP6 |

### Key Files

| File | Purpose |
|---|---|
| `notebook_analysis/03_integrated_scvr_cmip6.ipynb` | Main SCVR computation notebook |
| `data/schema/sites.json` | Site coordinates and metadata |
| `data/schema/variables.json` | Variable definitions and priorities |
| `data/schema/scvr_schema.json` | Output Parquet column specification |
| `data/processed/scvr/<site>/cmip6_ensemble_scvr.parquet` | SCVR output |
| `data/cache/thredds/` | Cached NetCDF files and probe results |

### Key Formulas

```
SCVR = (area_future - area_baseline) / area_baseline

Where:
  area = trapezoid integral of sorted daily values
         over exceedance probability [0, 1]
```

```
HCR  = SCVR x hazard_scaling_factor  (from literature)
EFR  = f(HCR, engineering_model_params)  (Peck's, Coffin-Manson, etc.)
NAV  = asset_value - (BI_losses + IUL_shortening_cost)
```
