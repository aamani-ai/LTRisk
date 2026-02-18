# LTRisk — Long-Term Climate Risk Evolution

*Quantifying how climate change impairs the value of renewable energy infrastructure assets over their full operating lifetime.*

---

## The One-Line Summary

> Climate change will shorten the life and reduce the revenue of solar and wind assets.
> This project computes by exactly how much — expressed as a NAV Impairment % — using
> CMIP6 climate science and standard engineering degradation models.

---

## Navigation — Where to Start

Depending on what you need, go directly to the right place:

| I want to... | Go here |
|---|---|
| **Get running in 5 minutes** | [Quick Start](#quick-start) below |
| **Understand what this project does** | [The Framework](#the-framework) |
| **See the actual results** | [Phase 1 Results — SCVR](#phase-1-results--scvr) |
| **Run the first notebook** | [`notebook_analysis/01_hayhurst_solar_scvr.ipynb`](notebook_analysis/01_hayhurst_solar_scvr.ipynb) |
| **Read about the notebook in detail** | [`docs/implementation/01_scvr_hayhurst_solar.md`](docs/implementation/01_scvr_hayhurst_solar.md) |
| **Understand the climate data source** | [`docs/data_sources/OPENMETEO_CMIP6_GUIDE.md`](docs/data_sources/OPENMETEO_CMIP6_GUIDE.md) ⚠️ read the warning at the top |
| **See what variables we use and why** | [`data/schema/VARIABLES.md`](data/schema/VARIABLES.md) |
| **Understand the full scientific framework** | [`docs/background/LONG_TERM_RISK_FRAMEWORK.md`](docs/background/LONG_TERM_RISK_FRAMEWORK.md) |
| **Look up a term or acronym** | [Glossary](#glossary) |

---

## Current Status

**Phase 1 of 4 complete** — climate data pipeline and SCVR working end-to-end on first pilot site.

```
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                        PROJECT PHASES                                    │
  ├──────────────────────────────────────────────────────────────────────────┤
  │                                                                          │
  │  PHASE 1  ✅ DONE      Climate data ingestion + SCVR computation        │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  PHASE 2  🔲 NEXT      HCR (hazard risk) + EFR (equipment aging)        │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  PHASE 3  🔲 PLANNED   Asset performance model (pvlib / InfraSure)      │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  PHASE 4  🔲 PLANNED   Final NAV impairment + Monte Carlo uncertainty   │
  │                                                                          │
  └──────────────────────────────────────────────────────────────────────────┘

  Pilot site:   Hayhurst Texas Solar — 24.8 MW, Culberson County, TX
  Data source:  Open-Meteo Climate API — EC_Earth3P_HR CMIP6 model, 1980–2049
  ⚠️  Scenario note: Current data ≈ SSP5-8.5 (high-emissions upper bound).
      Multi-scenario work will use NASA NEX-GDDP-CMIP6 in Phase 2.
```

---

## Quick Start

**Requirements:** Python 3.11+, internet connection (first run only)

```bash
# 1. Activate the virtual environment (already created)
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Run the three smoke tests — all should print PASS
python scripts/tests/test_openmeteo_api.py   # ~10s  confirms API is reachable
python scripts/tests/test_parquet_io.py      # <1s   confirms data I/O works
python scripts/tests/test_scvr_math.py       # <1s   confirms SCVR math is correct

# 4. Launch the notebook
jupyter lab
# → Open notebook_analysis/01_hayhurst_solar_scvr.ipynb
# → Kernel → Restart and Run All
```

**First run:** pulls ~70 years of daily climate data (~30 seconds), saves to Parquet, produces all plots.  
**Subsequent runs:** loads from cache, completes in under 5 seconds.

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
  NPV_base = $22.8M                     NPV_climate = $16.5M

                  NAV Impairment = (1 - 16.5 / 22.8) × 100 = 27.6%
                  "Climate change reduces this asset's value by ~28%"
```

### The three channels

Climate change hits an asset through three independent channels that are modelled separately and then combined:

```
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  CHANNEL A — Hazards → Business Interruption → Lost Revenue             │
  │                                                                         │
  │  Climate change  →  More extreme weather  →  More downtime events      │
  │                                                                         │
  │  Example: More intense precipitation → More flood/hail events          │
  │           Each event = days offline = lost revenue                      │
  │           BI_climate = BI_base × (1 + HCR)                             │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  CHANNEL B — Changed Weather → Different Generation Output              │
  │                                                                         │
  │  Hotter days → Solar panels run hotter → Efficiency drops             │
  │  Changed wind patterns → Different turbine output                      │
  │  Modelled using pvlib (solar) and PyWake (wind) with CMIP6 weather     │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  CHANNEL C — Climate Stress → Equipment Ages Faster → Shorter Life     │
  │                                                                         │
  │  Heat + humidity → Peck's Model → panels degrade faster               │
  │  Freeze-thaw cycles → Coffin-Manson fatigue → microcracks             │
  │  Wind variability → Palmgren-Miner rule → turbine fatigue             │
  │                                                                         │
  │  Asset reaches end-of-life in 21 years instead of 25.                 │
  │  Those 4 lost years = the single biggest NAV driver (~15% of total).   │
  └─────────────────────────────────────────────────────────────────────────┘
```

### How SCVR connects climate to finance

SCVR (Severe Climate Variability Rating) is the central bridge. It converts raw
climate time series into a single dimensionless number per variable per year:

```
  Raw CMIP6 data                         SCVR
  (daily temperature,                    "In 2040, extreme heat is
   precipitation, wind...)    ──────►    14.8% more frequent than
                                         the 1980-2014 baseline"
                                                │
                              ┌─────────────────┴──────────────────┐
                              ▼                                     ▼
                           HCR                                   EFR
                  (Hazard Change Ratio)               (Equipment Failure Ratio)
                  "Flood risk is 22%                  "Panels degrade 1.8×
                   higher by 2040"                     faster by 2040"
                              │                                     │
                              ▼                                     ▼
                        BI Losses                              IUL
                   (revenue lost to                     (asset life cut
                    hazard events)                       from 25→21 yrs)
                              │                                     │
                              └──────────────┬──────────────────────┘
                                             ▼
                                     NAV Impairment %
```

### The full pipeline (all four phases)

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                        │
  │   CMIP6 Climate Data  ──►  SCVR  ──►  HCR / EFR  ──►  NAV Impact    │
  │   (Open-Meteo API)                                                     │
  │                                                                        │
  │   Phase 1 ──────────────┐                                             │
  │   Climate projections   │  ← WE ARE HERE                             │
  │   Historical baseline   │                                             │
  │   Extreme indices       │                                             │
  │   SCVR table            │                                             │
  │   ──────────────────────┘                                             │
  │                                                                        │
  │   Phase 2 ──────────────┐                                             │
  │   HCR table             │  ← literature review + calibration          │
  │   EFR table             │                                             │
  │   IUL calculation       │                                             │
  │   ──────────────────────┘                                             │
  │                                                                        │
  │   Phase 3 ──────────────┐                                             │
  │   pvlib performance     │  ← InfraSure model integration              │
  │   Climate-adjusted rev  │                                             │
  │   ──────────────────────┘                                             │
  │                                                                        │
  │   Phase 4 ──────────────┐                                             │
  │   NPV_base vs climate   │  ← final output                             │
  │   Monte Carlo P10/P90   │                                             │
  │   NAV Impairment %      │                                             │
  │   ──────────────────────┘                                             │
  │                                                                        │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1 Results — SCVR

### What SCVR means in plain English

Take all daily temperature values from 1980–2014 (the baseline). Sort them highest to lowest and draw a curve — this is the exceedance curve, showing the probability of exceeding any given temperature. Now do the same for a future 20-year window (say 2030–2050). If the future curve sits to the right of the baseline — higher temperatures more probable — the area under it grows. SCVR measures that growth as a fraction.

```
  Baseline curve (1980-2014):         Future curve (2030-2050):
  Probability                         Probability
  of exceeding X°C                    of exceeding X°C
        │                                   │
    20% │╲                              20% │  ╲  ← shifted right
        │  ╲                                │   ╲    (hotter days
    10% │    ╲                          10% │    ╲    more likely)
        │      ╲                            │     ╲
     0% └───────╲────► Temp             0% └──────╲─────► Temp
             35°C  44°C                         36°C  46°C

  SCVR = (area under future − area under baseline) / area under baseline
       = +14.8% for tasmax at target year 2040
```

### Hayhurst Solar — SCVR Results

*Site: Culberson County, TX | Model: EC_Earth3P_HR | Baseline: 1980–2014*

| Climate Variable | 2030 | 2035 | 2040 | 2045 | 2050 | Signal |
|---|:---:|:---:|:---:|:---:|:---:|---|
| `tasmin` Night minimum temp | +9.2% | +11.9% | **+14.8%** | +16.7% | +17.9% | ↑ Strongest — nights warming fast |
| `tas` Mean temperature | +5.9% | +7.9% | +10.1% | +11.7% | +12.5% | ↑ Steady increase |
| `tasmax` Day maximum temp | +4.2% | +5.6% | +7.4% | +8.6% | +9.2% | ↑ Consistent |
| `rsds` Solar radiation | +0.9% | +1.0% | +1.1% | +1.4% | +1.7% | ↑ Small — slightly more sun |
| `sfcWind` Wind speed | +0.2% | +0.2% | ~0 | −0.2% | +0.4% | → Flat — no change |
| `hurs` Relative humidity | ~0 | −1.1% | −3.2% | −6.7% | −7.9% | ↓ Declining — site drying |
| `pr` Precipitation | +11.9% | +5.6% | +1.1% | −8.9% | −17.8% | ↓ Inverts — complex |

> ⚠️ 2045 and 2050 use shorter windows (15 and 10 years) due to API data ending 2049. Treat as directional.

**Four key takeaways:**
1. **Temperature is the dominant risk driver** — especially nighttime warming (tasmin +17.9%). This directly drives panel degradation via Peck's Model and freeze-thaw fatigue.
2. **Wind is flat** — sfcWind SCVR stays near zero. Structural fatigue from wind variability is not a stressor at this site.
3. **Site is getting drier** — humidity declining (partly reduces Peck's degradation, but increases soiling and wildfire risk).
4. **Precipitation inverts** — near-term heavier events (flood HCR increases), longer-term drying (dust soiling increases).

### Output plots

**Exceedance curve shift** — the visual definition of SCVR:

![Exceedance Curves](data/processed/scvr/hayhurst_solar/figures/plot_A_exceedance_curves.png)

*Temperature curves shift rightward (hotter extremes more probable). Precipitation shows minimal upper-tail change.*

---

**Extreme climate indices** — annual counts of threshold events, baseline vs future:

![Extreme Indices](data/processed/scvr/hayhurst_solar/figures/extreme_indices.png)

*Heat wave days (top-left) roughly triple. Frost days decline. Max 5-day precipitation shows more variance.*

---

**SCVR over time** — divergence from baseline = 0:

![SCVR Over Time](data/processed/scvr/hayhurst_solar/figures/plot_B_scvr_over_time.png)

*tasmin (dark red, top) is the fastest-growing stressor. Wind (green) is flat. Precipitation (blue) crosses zero ~2040.*

---

**SCVR heatmap** — all variables and years at a glance:

![SCVR Heatmap](data/processed/scvr/hayhurst_solar/figures/plot_C_scvr_heatmap.png)

*Orange-red = more extreme than baseline. Green = fewer extremes. Wind and solar radiation barely move.*

---

**Temperature trend sanity check:**

![Temperature Trend](data/processed/scvr/hayhurst_solar/figures/plot_D_temperature_trend.png)

*+3.3°C warming over 1980–2049 — physically consistent with high-emissions pathway for West Texas.*

---

## Project Structure

```
LTRisk/
│
├── README.md                            ← you are here
├── requirements.txt                     ← pip install -r requirements.txt
│
├── notebook_analysis/                   ← run notebooks in order
│   ├── README.md                        ← notebook index
│   └── 01_hayhurst_solar_scvr.ipynb    ← ✅ Phase 1 (start here)
│
├── scripts/tests/                       ← run before any notebook
│   ├── test_openmeteo_api.py            ← API connectivity
│   ├── test_parquet_io.py               ← data I/O
│   └── test_scvr_math.py               ← SCVR calculation correctness
│
├── data/
│   ├── schema/                          ← read this before touching data
│   │   ├── VARIABLES.md                ← what variables we use and why
│   │   ├── sites.json                  ← pilot site coordinates + model
│   │   └── *.json                      ← column specs for all file types
│   ├── raw/cmip6/hayhurst_solar/       ← raw daily Parquet files
│   └── processed/scvr/hayhurst_solar/  ← SCVR output + figures/
│
├── docs/
│   ├── background/                      ← team framework theory docs
│   ├── data_sources/
│   │   └── OPENMETEO_CMIP6_GUIDE.md   ← ⚠️ read the warning at the top
│   └── implementation/
│       └── 01_scvr_hayhurst_solar.md   ← full results + methodology notes
│
└── extra/old_setup_by_others/          ← earlier prototype (reference only)
```

---

## Important Documents — Read in This Order

```
  ① docs/data_sources/OPENMETEO_CMIP6_GUIDE.md
    ─────────────────────────────────────────────
    What is CMIP6? Why multiple models? What scenarios?
    ⚠️ Critical limitation at the top: all Open-Meteo models are SSP5-8.5 only.

  ② data/schema/VARIABLES.md
    ─────────────────────────
    Which climate variables we fetch, units, API names, priority tiers.
    Know this before modifying the data pipeline.

  ③ notebook_analysis/01_hayhurst_solar_scvr.ipynb
    ────────────────────────────────────────────────
    The actual working analysis. Run it, read the markdown cells.
    Each section has explanations before the code.

  ④ docs/implementation/01_scvr_hayhurst_solar.md
    ───────────────────────────────────────────────
    Detailed notes on the notebook results. Read after running the notebook
    or instead of running it to understand what it produced.
```

---

## Pilot Sites

| Site | Type | MW | Location | Climate Zone | EUL | Status |
|---|---|---|---|---|---|---|
| Hayhurst Texas Solar | Solar PV | 24.8 | Culberson County, TX | Arid / desert | 25 yr | ✅ Phase 1 done |
| Maverick Creek Wind | Wind turbine | 491.6 | Concho County, TX | Semi-arid | 35 yr | 🔲 Notebook 02 |

---

## Data Sources

| Source | Scenarios | Models | Horizon | Access | Use |
|---|---|---|---|---|---|
| **Open-Meteo Climate API** | SSP5-8.5 only | 7 HighResMIP | 1950–2049 | Free API | Prototype ✅ |
| **NASA NEX-GDDP-CMIP6** | SSP2-4.5 + SSP5-8.5 | 35 CMIP6 | 1950–2100 | Free, AWS S3 | Production |
| NOAA GHCN-Daily | Historical obs. | — | 1980–present | Free API | Validation |

> **Open-Meteo limitation:** Switching between its 7 models does NOT change the scenario —
> they all run under SSP5-8.5. Our SCVR results are a high-emissions upper bound on risk.
> Full explanation: [`docs/data_sources/OPENMETEO_CMIP6_GUIDE.md`](docs/data_sources/OPENMETEO_CMIP6_GUIDE.md)

---

## What Comes Next — Notebooks 02–04

```
  NOTEBOOK 02 — HCR + EFR Derivation
  ────────────────────────────────────────────────────────────────────────
  Input:  SCVR table from notebook 01
  Work:   Literature review → assign coefficients to each hazard/mechanism

    Flood HCR     = α × SCVR_precipitation   → scales BI losses for floods
    Icing HCR     = β × SCVR_tasmin          → wind turbine power loss
    Soiling HCR   = γ × SCVR_dry_days        → solar panel soiling
    Peck's EFR    = f(SCVR_tasmin, SCVR_hurs) → degradation acceleration
    IUL           = EUL × [1 − Σ(EFR × SCVR)] → life shortening in years

  Output: HCR tables, EFR tables, IUL estimate (e.g. 25 → 21 years)

  ────────────────────────────────────────────────────────────────────────
  NOTEBOOK 03 — Asset Performance Modeling
  ────────────────────────────────────────────────────────────────────────
  Input:  Raw CMIP6 daily data + site specs
  Work:   Run pvlib with climate-adjusted irradiance/temperature
          → How does annual MWh output change under future climate?
  Output: Revenue projections (baseline vs climate), P10/P50/P90

  ────────────────────────────────────────────────────────────────────────
  NOTEBOOK 04 — Final NAV Impairment
  ────────────────────────────────────────────────────────────────────────
  Input:  BI losses (nb02) + IUL (nb02) + revenue change (nb03)
  Work:   NPV_base vs NPV_climate → NAV Impairment %
          Monte Carlo (1,000 iterations) → P10/P50/P90 confidence bands
  Output: NAV Impairment % range, LTV impact, IRR change for Hayhurst Solar
          → Then repeat for Maverick Creek Wind
```

---

## Glossary

| Term | Plain English |
|---|---|
| **NAV** | What an asset is worth today = present value of all future revenues |
| **NAV Impairment %** | How much climate change shrinks that value vs the no-change baseline |
| **EUL** | How long the asset was designed to last (25 yr solar, 35 yr wind) |
| **IUL** | How long it actually lasts after climate stress accelerates ageing |
| **SCVR** | "How much more extreme is the climate vs the historical baseline?" expressed as a fraction |
| **HCR** | "How much more frequent/severe are hazards (floods, hail, icing)?" as a fraction |
| **EFR** | "How much faster does equipment fail per unit of SCVR?" |
| **WACC** | The discount rate used in NPV calculations (10% in this pilot) |
| **BI** | Revenue lost when an asset goes offline due to a weather event |
| **CMIP6** | The global standard dataset for long-term climate projections (IPCC AR6 basis) |
| **SSP2-4.5** | Moderate emissions pathway — world on current policy track — ~+2.4°C by 2100 |
| **SSP5-8.5** | High-emissions pathway — no mitigation — ~+4.3°C by 2100 (what Open-Meteo gives us) |
| **HighResMIP** | CMIP6 sub-experiment using very high resolution models — SSP5-8.5 only |
| **Peck's Model** | Engineering model for how heat + humidity accelerates chemical degradation in solar panels |
| **Coffin-Manson** | Engineering model for freeze-thaw fatigue cycles in panel solder joints |
| **Palmgren-Miner** | Engineering model for cumulative fatigue damage in wind turbine components |

---

*InfraSure — Long-Term Risk Evolution*  
*Python 3.13 · CMIP6 · Open-Meteo · EC_Earth3P_HR · February 2026*
