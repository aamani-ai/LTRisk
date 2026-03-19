# LTRisk — Long-Term Climate Risk Evolution

*Quantifying how climate change impairs the value of renewable energy infrastructure assets over their full operating lifetime.*

---

## The One-Line Summary

> Climate change will shorten the life and reduce the revenue of solar and wind assets.
> This project computes by exactly how much — expressed as a NAV Impairment % — using
> CMIP6 climate science and standard engineering degradation models.

---

## Navigation — Where to Start

| I want to... | Go here |
|---|---|
| **Get running in 5 minutes** | [Quick Start](#quick-start) below |
| **Understand what this project does** | [The Framework](#the-framework) |
| **Compute SCVR from cached data** | [`scripts/analysis/scvr/compute_scvr.py`](scripts/analysis/scvr/compute_scvr.py) — [README](scripts/analysis/scvr/README.md) |
| **Learn the methodology from scratch** | [`docs/learning/00_index.md`](docs/learning/00_index.md) — 11 guides in 4 categories |
| **Read the annual SCVR methodology discussion** | [`docs/discussion/discussion_annual_scvr_methodology.md`](docs/discussion/discussion_annual_scvr_methodology.md) |
| **See how SCVR translates to financial impact** | [`docs/learning/C_financial_translation/09_nav_impairment_chain.md`](docs/learning/C_financial_translation/09_nav_impairment_chain.md) |
| **See NB03 implementation details** | [`docs/implementation/03_integrated_scvr_cmip6.md`](docs/implementation/03_integrated_scvr_cmip6.md) |
| **Check project TODO and roadmap** | [`docs/todo.md`](docs/todo.md) |
| **See what variables we use and why** | [`data/schema/VARIABLES.md`](data/schema/VARIABLES.md) |
| **Look up a term or acronym** | [Glossary](#glossary) |

---

## Current Status

**NB01-03 → production scripts.** SCVR computation is now a CLI pipeline. NB04 in progress.

```
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                       PRODUCTION PIPELINE                               │
  ├──────────────────────────────────────────────────────────────────────────┤
  │                                                                        │
  │  fetch_cmip6.py    DONE   Fetch 34 CMIP6 models from THREDDS → cache  │
  │  compute_scvr.py   DONE   SCVR: ensemble, decade, annual, shape, GEV  │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  NB04  IN PROGRESS  HCR + EFR + IUL + NAV impairment                  │
  │                     See: notebook_analysis/04_hcr_efr_iul_nav.ipynb    │
  │                                                                        │
  └──────────────────────────────────────────────────────────────────────────┘

  Pilot sites:   Hayhurst Texas Solar — 24.8 MW, Culberson County, TX
                 Maverick Creek Wind — 491.6 MW, Concho County, TX
  Data source:   NASA NEX-GDDP-CMIP6 via THREDDS (34 models, SSP2-4.5 + SSP5-8.5)
  Baseline:      1985-2014 (30 years)
  Future:        2026-2055 (30-year asset lifetime)
```

---

## Key Finding: Annual SCVR Methodology

The team framework expects annual SCVR values (one per year, 2030-2050). We ran a
concrete experiment to determine the best computation method. The results show that
a **variable-specific strategy** is needed:

```
Variable    Signal  R²(fit)   Recommended Method
──────────────────────────────────────────────────────────
tasmax      Strong  0.97      3 anchors + linear fit
tasmin      Strong  0.99      3 anchors + linear fit
tas         Strong  0.98      3 anchors + linear fit
pr          Noisy   0.59      Period average or non-linear fit
sfcWind     None    0.13      Period average (SCVR ~ 0)
hurs        Weak    0.67      Period average
rsds        None    0.31      Period average (SCVR ~ 0)
```

**Temperature** (the primary risk driver) shows a clean linear trend — 3 non-overlapping
10-year anchors capture the climate signal with R² > 0.95. **Precipitation** is non-linear
and noisy. **Wind/radiation** show no meaningful climate change signal at these sites.

Full analysis: [`docs/discussion/discussion_annual_scvr_methodology.md`](docs/discussion/discussion_annual_scvr_methodology.md)
Experiment script: [`scripts/archive/experiments/annual_scvr_test.py`](scripts/archive/experiments/annual_scvr_test.py)

---

## Quick Start

**Requirements:** Python 3.11+, internet connection (first run only for data fetch)

```bash
# 1. Activate the virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Fetch CMIP6 data (first run only, ~10 min, cached)
python scripts/data/fetch_cmip6.py --site hayhurst_solar

# 4. Compute SCVR
python scripts/analysis/scvr/compute_scvr.py --dry-run   # preview
python scripts/analysis/scvr/compute_scvr.py              # run

# 5. Launch notebooks (for NB04 and exploration)
jupyter lab
```

**First run:** fetches CMIP6 data from NASA THREDDS (~10 min, cached to `data/cache/thredds/`).
**Subsequent runs:** loads from cache, SCVR computation completes in ~2 minutes.

---

## The Framework

### What problem are we solving?

Infrastructure investors and lenders model asset value assuming climate stays like the historical past. That is increasingly wrong. This project quantifies the financial impact of climate change on a renewable energy asset over its full lifetime:

```
  TODAY'S ASSUMPTION                    REALITY
  ────────────────────────              ──────────────────────────────────────
  25-year life, stable climate    →     Panels degrade faster in heat
  Constant hazard frequency       →     Flood and hail events more frequent
  Historical generation patterns  →     Output changes as climate shifts
  ────────────────────────              ──────────────────────────────────────
  NPV_base = $60M                       NPV_climate = $54.1M

                  NAV Impairment = ~$5.9M (9.8%) under SSP5-8.5
```

### The SCVR → NAV pipeline

```
  SCVR(t)                           Annual climate shift per variable
    │
    ├──► HCR(t)                     Hazard-specific amplification
    │      │                        (heat ×2.5, flood ×1.5-2.0, etc.)
    │      │
    │      ├──► BI losses           Revenue lost to hazard events
    │      │
    │      └──► EFR(t)              Equipment degradation rate
    │             │                 (Peck's, Coffin-Manson, Palmgren-Miner)
    │             │
    │             └──► IUL          Asset life: 25yr → 21yr
    │
    └──► Gen(t) adjustment          Climate-adjusted annual generation
           │
           └──► CFADS(t)           Cash flow available for debt service
                  │
                  └──► NAV         Net Asset Value impairment
```

Full pipeline walkthrough: [`docs/learning/C_financial_translation/09_nav_impairment_chain.md`](docs/learning/C_financial_translation/09_nav_impairment_chain.md)

---

## Documentation

### Learning Guides (`docs/learning/`)

Organised into 4 progressive sections — start from the top if you're new, or jump to any section.
Full index with reading orders: [`docs/learning/00_index.md`](docs/learning/00_index.md)

| Section | Folder | Guides | Covers |
|---|---|---|---|
| **A. Climate Foundations** | [`A_climate_foundations/`](docs/learning/A_climate_foundations/) | 01-03 | Climate science, CMIP6 models, SSP scenarios, time windows |
| **B. SCVR Methodology** | [`B_scvr_methodology/`](docs/learning/B_scvr_methodology/) | 04-06 | SCVR formula, variable use cases, scenario comparison |
| **C. Financial Translation** | [`C_financial_translation/`](docs/learning/C_financial_translation/) | 07-09 | HCR hazard mapping, EFR equipment degradation, NAV impairment chain |
| **D. Technical Reference** | [`D_technical_reference/`](docs/learning/D_technical_reference/) | 10-11 | THREDDS data pipeline, distribution shift methods (W1, CVaR, AAL) |

### Discussion Docs (`docs/discussion/`)

| Document | What It Addresses |
|---|---|
| [`discussion_annual_scvr_methodology.md`](docs/discussion/discussion_annual_scvr_methodology.md) | **How to compute annual SCVR values** — 3 options analysed, experiment with real data, variable-specific recommendation. Key decision before NB04. |
| [`discussion_scvr_performance_adjustment.md`](docs/discussion/discussion_scvr_performance_adjustment.md) | How SCVR feeds into the 3 channels of financial impact — Channel 1 (hazard BI), Channel 2 (generation), Channel 3 (equipment life). |

### Implementation Docs (`docs/implementation/`)

| Document | Scope |
|---|---|
| [`03_integrated_scvr_cmip6.md`](docs/implementation/03_integrated_scvr_cmip6.md) | NB03 — ensemble SCVR design decisions |
| [`04_ensemble_exceedance_script.md`](docs/implementation/04_ensemble_exceedance_script.md) | Presentation script for exceedance plots |
| `archive/01_scvr_hayhurst_solar.md` | NB01 — archived |
| `archive/02_nex_gddp_cmip6_thredds.md` | NB02 — archived |

---

## Project Structure

```
LTRisk/
│
├── README.md                            ← you are here
├── requirements.txt
│
├── notebook_analysis/
│   ├── README.md                        ← notebook index
│   ├── 04_hcr_efr_iul_nav.ipynb        ← ONLY active notebook (HCR → NAV)
│   └── archive/                         ← NB01-03 (superseded by scripts)
│
├── scripts/
│   ├── README.md                        ← pipeline overview
│   ├── data/
│   │   ├── fetch_cmip6.py              ← fetch CMIP6 data from THREDDS
│   │   └── README.md
│   ├── analysis/
│   │   └── scvr/
│   │       ├── compute_scvr.py         ← compute SCVR (self-contained)
│   │       ├── README.md               ← detailed methodology + output docs
│   │       └── extra/                   ← plots + PDF report
│   └── archive/                         ← superseded scripts (reference only)
│
├── data/
│   ├── schema/                          ← variable/site/output definitions
│   │   ├── sites.json                  ← pilot site coordinates + metadata
│   │   ├── variables.json              ← variable definitions and priorities
│   │   └── scvr_schema.json            ← output Parquet column spec
│   ├── output/scvr/                     ← SCVR output Parquet (committed)
│   ├── cache/thredds/                   ← cached NetCDF files (not committed)
│   └── processed/                       ← notebook output (not committed)
│
├── docs/
│   ├── learning/                        ← 11 methodology guides in 4 sections
│   │   ├── 00_index.md                 ← table of contents + reading orders
│   │   ├── A_climate_foundations/      ← 01-03
│   │   ├── B_scvr_methodology/         ← 04-06
│   │   ├── C_financial_translation/    ← 07-09
│   │   └── D_technical_reference/      ← 10-11
│   ├── discussion/                      ← methodology decision docs
│   ├── implementation/ + archive/       ← design notes (active + archived)
│   ├── archive/                         ← background/, data_sources/
│   └── todo.md                          ← project roadmap and task tracking
│
└── extra/old_setup_by_others/          ← earlier prototype (reference only)
```

---

## Pilot Sites

| Site | Type | MW | Location | Climate Zone | EUL | Status |
|---|---|---|---|---|---|---|
| Hayhurst Texas Solar | Solar PV | 24.8 | Culberson County, TX | Arid / desert | 25 yr | NB01-03 done |
| Maverick Creek Wind | Wind turbine | 491.6 | Concho County, TX | Semi-arid | 35 yr | NB03 done |

---

## Data Sources

| Source | Scenarios | Models | Horizon | Use |
|---|---|---|---|---|
| **NASA NEX-GDDP-CMIP6** | SSP2-4.5 + SSP5-8.5 | 34 CMIP6 | 1950-2100 | **Production** (NB02+NB03) |
| Open-Meteo Climate API | SSP5-8.5 only | 7 HighResMIP | 1950-2049 | Prototype only (NB01) |

NEX-GDDP-CMIP6 data is fetched via THREDDS server-side point extraction and cached
locally as NetCDF files (~54 MB for 2 sites, 7 variables, 6 models).

---

## Ensemble SCVR Results (NB03)

*6 models pooled, SSP5-8.5, 2026-2055 vs 1985-2014 baseline*

| Variable | Hayhurst Solar | Maverick Wind | Signal |
|---|:---:|:---:|---|
| tasmin | +16.4% | — | Strongest — nights warming fast |
| tas | +9.9% | — | Steady increase |
| tasmax | +8.3% | — | Consistent |
| pr | +1.2% | — | Noisy, non-linear |
| sfcWind | -1.1% | — | Flat — no change |
| hurs | -4.3% | — | Declining — site drying |
| rsds | ~0% | — | Flat |

**Key insight:** Temperature is the dominant risk driver. Wind and solar radiation
are climate-stable at these Texas sites. Risk comes from heat stress on equipment,
not from changes in the generation resource.

---

## Glossary

| Term | Plain English |
|---|---|
| **NAV** | What an asset is worth today = present value of all future revenues |
| **NAV Impairment %** | How much climate change shrinks that value vs the no-change baseline |
| **SCVR** | Severe Climate Variability Rating — "how much more extreme is the climate vs baseline?" as a fraction |
| **HCR** | Hazard Change Ratio — "how much more frequent/severe are hazards?" |
| **EFR** | Equipment Failure Ratio — "how much faster does equipment fail?" |
| **EUL / IUL** | Expected vs Impaired Useful Life (e.g. 25 yr designed → 21 yr actual) |
| **CFADS** | Cash Flow Available for Debt Service — what the lender cares about |
| **CMIP6** | The global standard dataset for long-term climate projections (IPCC AR6 basis) |
| **NEX-GDDP-CMIP6** | NASA's bias-corrected, downscaled CMIP6 dataset — 34 models, daily resolution |
| **SSP2-4.5** | Moderate emissions pathway — world on current policy track — ~+2.4C by 2100 |
| **SSP5-8.5** | High-emissions pathway — no mitigation — ~+4.3C by 2100 |
| **Peck's Model** | Engineering model: heat + humidity accelerates chemical degradation in solar panels |
| **Coffin-Manson** | Engineering model: freeze-thaw fatigue cycles cause microcracks |
| **Palmgren-Miner** | Engineering model: cumulative wind fatigue damage in turbine components |

---

*InfraSure — Long-Term Risk Evolution*
*Python 3.13 | NEX-GDDP-CMIP6 | 34 CMIP6 models | SSP2-4.5 + SSP5-8.5 | March 2026*
