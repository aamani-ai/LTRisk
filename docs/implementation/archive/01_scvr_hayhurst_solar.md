# Notebook 01 — SCVR Analysis: Hayhurst Solar

*Implementation notes for `notebook_analysis/01_hayhurst_solar_scvr.ipynb`*

**Site:** Hayhurst Texas Solar — Culberson County, TX (24.8 MW, arid/desert)  
**Model:** EC_Earth3P_HR (European CMIP6 HighResMIP, 29 km native resolution)  
**Scenario label:** SSP2-4.5 — but see [Important Note on Scenario](#important-note-on-scenario)  
**Baseline period:** 1980–2014 (35 years, 12,784 days)  
**Future period:** 2015–2049 (35 years, data ends 2049; 2050 is null in the API)

---

## Where This Fits in the LTRisk Pipeline

```
  THIS NOTEBOOK
  ┌───────────────────────────────────────────────────────────────┐
  │  Raw climate data (Open-Meteo API)                            │
  │        │                                                      │
  │        ▼                                                      │
  │  Section 1: Data Acquisition  →  data/raw/cmip6/             │
  │        │                                                      │
  │        ▼                                                      │
  │  Section 2: Baseline check    →  "Is this data realistic?"   │
  │        │                                                      │
  │        ▼                                                      │
  │  Section 3: Extreme indices   →  Heat waves, frost days, etc │
  │        │                                                      │
  │        ▼                                                      │
  │  Section 4: SCVR computation  →  data/processed/scvr/        │
  │        │                                                      │
  │        ▼                                                      │
  │  Section 5: Visualisation     →  figures/*.png               │
  └───────────────────────────────────────────────────────────────┘
             │
             ▼
        NEXT NOTEBOOKS (02+)
        ┌──────────────────────────────────────────────────────────┐
        │  HCR (Hazard Change Ratio)  =  f(SCVR)  → BI losses     │
        │  EFR (Equipment Failure)    =  f(SCVR)  → IUL           │
        │  NAV Impairment             =  NPV_climate / NPV_base    │
        └──────────────────────────────────────────────────────────┘
```

SCVR is the **bridge** between raw climate projections and financial risk.
Without it, we cannot connect "temperatures will rise" to "this asset's value
is impaired by X%."

---

## Important Note on Scenario

The Open-Meteo Climate API serves HighResMIP models that are aligned with
**approximately RCP8.5 / SSP5-8.5** (high-emissions, no-mitigation pathway).
The `scenario` label `ssp245` in file names is a metadata identifier only —
it does **not** change what the API returns.

This means our SCVR values represent an **upper-bound / conservative** view
of climate risk. For multi-scenario analysis (SSP2-4.5 vs SSP5-8.5), the
NASA NEX-GDDP-CMIP6 dataset would be needed.

The +3.3°C warming trend over 1980–2049 (Plot D) confirms the high-emissions
pathway interpretation.

---

## Section 2 — Baseline Climate at Hayhurst Solar

Before computing anything, the notebook confirms the data is physically correct
for Culberson County, West Texas (arid/desert climate zone).

![Baseline Seasonality](../../data/processed/scvr/hayhurst_solar/figures/baseline_seasonality.png)

**What the baseline shows (1980–2014):**

| Variable | Jan | Jun | Jul | Annual notes |
|---|---|---|---|---|
| tasmax | ~15°C | ~36°C | ~37°C | Classic hot desert — large annual swing |
| tasmin | ~2°C | ~22°C | ~23°C | Nights can freeze in winter |
| Precipitation | ~0.5 mm/day | ~1.5 mm/day | ~2 mm/day | Monsoon-influenced summer peak; very low total ~250 mm/yr |
| Wind speed | ~14–17 m/s | ~14–16 m/s | ~13–14 m/s | Moderate, slightly higher in spring |
| rsds (solar) | ~13 MJ/m² | ~29 MJ/m² | ~28 MJ/m² | Very high summer irradiance — excellent solar resource |
| hurs | ~35% | ~35% | ~46% | Dry overall; small monsoon humidity bump in summer |

**Verdict:** Data is physically realistic. High irradiance (rsds peaks ~29 MJ/m² in June) confirms Culberson County is one of the best solar resource areas in the US. Low humidity confirms the arid desert classification.

---

## Section 3 — Extreme Climate Indices

Annual counts of threshold-exceeding events across the full 1980–2049 period.

![Extreme Indices](../../data/processed/scvr/hayhurst_solar/figures/extreme_indices.png)

**Key observations from the plots (grey = baseline 1980–2014, colour = future 2015–2049):**

| Index | Baseline range | Future range | Visible trend |
|---|---|---|---|
| Heat wave days | 5–40 days/yr | 25–80 days/yr | Strong upward — 3–4× more frequent by 2040s |
| Frost days (tasmin<0°C) | 10–50 days/yr | 5–40 days/yr | Gradual decline — fewer cold nights |
| Icing days (tasmax<0°C) | 0–8 days/yr | 0–7 days/yr | Mostly unchanged; rare events persist |
| Max 5-day precip | 20–100 mm | 20–260 mm | Higher variance, occasional extreme events |
| Max consecutive dry days | 25–65 days/yr | 25–90 days/yr | Slightly longer dry spells in future |
| Wind cut-out days (>25 m/s) | 5–40 days/yr | 10–30 days/yr | No clear trend — high inter-annual variance |
| Fire Weather Index (mean) | ~0.63 | ~0.63 | Essentially flat — composed stressors offset each other |

**The most important signal here:** Heat wave days roughly triple over the analysis period. This directly feeds the EFR temperature coefficient and Peck's aging model in notebook 02.

---

## Section 4 — SCVR Computation

### What SCVR measures

SCVR (Severe Climate Variability Rating) answers the question:

> *"How much more area is under the tail of the climate distribution in the future, compared to the historical baseline?"*

Think of the exceedance curve as a probability curve — it shows the chance of exceeding any given value. If the curve shifts rightward (for temperature) or upward (for extremes), the area under it grows. SCVR measures that growth as a fraction.

```
  EXCEEDANCE CURVE CONCEPT

  Probability of         Baseline        Future 2040
  exceeding X °C         (1980–2014)     window
      │
  20% │ ╮                  ╭───── Future curve is shifted RIGHT
      │  ╲                ╱       (higher temperatures more probable)
  15% │   ╲              ╱
      │    ╲        ╭────╯        Area between curves
  10% │     ╲    ╭──╯             = increase in extreme heat exposure
      │      ╲  ╱
   5% │       ╲╱
      └────────────────────────► Temperature (°C)
               35   38   41   44
                         ▲
                         The P90 threshold from baseline
                         is exceeded far more often in the future
```

**Formula:**

```
  SCVR(variable, year) = (Area_future − Area_baseline) / Area_baseline

  Where Area = ∫ F⁻¹(1−p) dp  ≈  trapz(values_sorted_descending, p ∈ [0,1])
```

- **SCVR = 0**: Future distribution identical to baseline
- **SCVR = +0.10**: Exceedance area is 10% larger → more or more intense extremes
- **SCVR = −0.10**: Exceedance area is 10% smaller → fewer extremes (e.g., frost days declining)

### Why 20-year windows?

Single-year SCVR is useless — one warm year or one unusually wet year swamps the
climate signal. We use **20-year windows centered on each target year** to extract
the long-term trend from inter-annual noise.

```
  Example: center_year = 2030
  Window  : 2020–2040  (20 years of future data)
  Compared: 1980–2014  (35-year baseline, always the same)

  center_year = 2045
  Window  : 2035–2049  (only 15 years — shorter due to 2049 API cutoff)
  ⚠️ Less statistically robust — treat with wider uncertainty
```

### The actual exceedance curves

![Exceedance Curve Shift](../../data/processed/scvr/hayhurst_solar/figures/plot_A_exceedance_curves.png)

**Reading this plot:**
- **Left panel (tasmax):** The curve shifts clearly rightward — the top 20% of hot days in 2030 start at ~35°C (vs ~34°C baseline), and by 2040 the curve extends toward 44°C. The entire area under the curve grows. This is a clean, interpretable SCVR signal.
- **Right panel (pr):** The curves nearly overlap. Precipitation extremes in Culberson County don't change dramatically in the upper tail (rare heavy rain events). The SCVR for precipitation is driven more by the mid-range distribution shifts.

---

## Section 4 Results — The SCVR Table

*Computed from real EC_Earth3P_HR data. Positive = more extremes than baseline. Negative = fewer.*

| Variable | 2030 | 2035 | 2040 | 2045 | 2050 | Trend | Reliability |
|---|---|---|---|---|---|---|---|
| `tasmin` | **+9.2%** | **+11.9%** | **+14.8%** | **+16.7%** | **+17.9%** | Strong ↑ | ✅ Robust |
| `tas` | +5.9% | +7.9% | +10.1% | +11.7% | +12.5% | Steady ↑ | ✅ Robust |
| `tasmax` | +4.2% | +5.6% | +7.4% | +8.6% | +9.2% | Consistent ↑ | ✅ Robust |
| `rsds` | +0.9% | +1.0% | +1.1% | +1.4% | +1.7% | Small ↑ | ✅ Robust |
| `sfcWind` | +0.2% | +0.2% | ~0 | −0.2% | +0.4% | Flat | ✅ No signal |
| `hurs` | ~0 | −1.1% | −3.2% | −6.7% | −7.9% | Declining ↓ | ✅ Robust |
| `pr` | +11.9% | +5.6% | +1.1% | −8.9% | **−17.8%** | Inverts | ⚠️ Later values less robust |

### SCVR heatmap

![SCVR Heatmap](../../data/processed/scvr/hayhurst_solar/figures/plot_C_scvr_heatmap.png)

The heatmap shows at a glance: temperature variables (orange-red) increase across all years, wind and solar radiation barely move, and precipitation (bottom row) shifts from slightly positive to negative — meaning drier overall by mid-century.

### SCVR evolution over time

![SCVR Over Time](../../data/processed/scvr/hayhurst_solar/figures/plot_B_scvr_over_time.png)

**Five things this chart tells you:**

1. **tasmin dominates** (top line, dark red — +17.9% by 2050): Nights are warming faster than days. This is a well-documented phenomenon in desert climates under high-emission scenarios. It matters most for Peck's aging model (more hot humid nights accelerate panel degradation) and for freeze-thaw cycle counts.

2. **Temperature variables are monotonically increasing** (tasmax, tas, tasmin all trend upward): No ambiguity — every target year is hotter than the one before. This is the most reliable signal in the dataset.

3. **Wind is flat** (green line near zero): No significant change in wind speed extremes. For wind turbines at Maverick Creek Wind (Concho County), Palmgren-Miner structural fatigue from changing wind patterns is unlikely to be the dominant stressor.

4. **Humidity is declining** (purple line going negative, −7.9% by 2050): West Texas is drying out. The counterintuitive implication: *lower humidity actually reduces Peck's model degradation rate* (η is lower). However, it simultaneously increases soiling risk (more dust) and FWI (wildfire).

5. **Precipitation is the most complex** (blue line, starts positive, crosses zero ~2040, reaches −17.8% by 2050): The distribution is shifting — fewer total rain days but the occasional extreme event. The 2045/2050 values use shorter windows (15 and 10 years respectively) and should be treated with wider uncertainty bounds.

### Window sizes (statistical context)

| Target Year | Future Window | Future Days Used | vs Baseline (12,784) | Caution |
|---|---|---|---|---|
| 2030 | 2020–2040 | 7,671 | 60% | None |
| 2035 | 2025–2045 | 7,670 | 60% | None |
| 2040 | 2030–2049 | 7,305 | 57% | None |
| 2045 | 2035–2049 | 5,479 | 43% | ⚠️ Shorter window |
| 2050 | 2040–2049 | 3,653 | 29% | ⚠️ Only 10 years |

The 2045 and 2050 windows are shorter because our data ends in 2049 (2050 is null
in the Open-Meteo API). Treat those columns with wider uncertainty, especially for
high-variance variables like precipitation.

---

## Section 5 — Temperature Trend Sanity Check

![Temperature Trend](../../data/processed/scvr/hayhurst_solar/figures/plot_D_temperature_trend.png)

**Linear warming rate: +3.3°C over 70 years (1980–2049), or ~0.47°C per decade.**

This is consistent with high-emission (RCP8.5/SSP5-8.5) projections for the Southwest US. It confirms our earlier note that the Open-Meteo HighResMIP models represent a high-emissions pathway, not the moderate SSP2-4.5 pathway. The continuous warming trend with no inflection point (no emissions peak) is the clearest indicator of this.

---

## Summary: What These SCVR Values Mean for NAV Impairment

| SCVR signal | Physical meaning | Feeds into | Expected direction |
|---|---|---|---|
| tasmin +17.9%, tasmax +9.2% | Much hotter days and nights | EFR → IUL shortening via Peck's model and temp coefficient losses | NAV ↓ |
| hurs −7.9% | Drier atmosphere | EFR → slightly offsets Peck's effect; FWI → wildfire HCR increases | Mixed |
| pr from +12% → −18% | More intense near-term rain, drier long-term | Flood HCR (near-term ↑), dust/soiling HCR (long-term ↑) | NAV ↓ |
| sfcWind ~0 | No wind change | Palmgren-Miner EFR essentially unchanged | Neutral |
| rsds +1.7% | Slightly more solar resource | Generation performance model → slightly offsets losses | NAV ↑ (small) |

**Overall picture for Hayhurst Solar:**
Temperature stress is the dominant climate risk driver, particularly nighttime warming (tasmin).
The asset will face accelerated panel aging, more heat wave downtime, and increasing soiling
from drying conditions. These effects are partially offset by slightly improved solar irradiance.
The net effect on NAV will be computed in notebook 02 once HCR and EFR coefficients are applied.

---

## Known Limitations of This Analysis

### Limitation 1 — The 2045 and 2050 SCVR values are less statistically reliable

SCVR is computed using a **20-year window centered on each target year**. That means:

```
  Target 2030  →  use future data from  2020 ──────────── 2040   (20 years ✅ full window)
  Target 2035  →  use future data from  2025 ──────────── 2045   (20 years ✅ full window)
  Target 2040  →  use future data from  2030 ──────────── 2050   (20 years ✅ full window)

  Target 2045  →  should use           2035 ──────────────────── 2055
                  BUT API data ends at 2049 ↑
                  So we only get:       2035 ──────── 2049        (15 years ⚠️)

  Target 2050  →  should use           2040 ──────────────────── 2060
                  BUT API data ends at 2049 ↑
                  So we only get:       2040 ───── 2049           (10 years ⚠️)
```

The further out you target, the shorter the actual window — because the Open-Meteo API
stops at 2049 (2050 is fully null). A 10-year future window compared to a 35-year baseline
gives a noisier, less confident SCVR estimate. **It is not wrong, just less certain.**

Practically:
- **2030, 2035, 2040** SCVR values: fully robust, use with confidence
- **2045** SCVR values: indicative, treat with ±30% wider uncertainty
- **2050** SCVR values: least robust, use only for directional trend, not precise magnitude

**Fix for production analysis:** Use the NASA NEX-GDDP-CMIP6 dataset (available on AWS S3),
which provides daily data through 2100. This gives full 20-year windows for all target years.

---

### Limitation 2 — The data represents SSP5-8.5 (high emissions), not SSP2-4.5 as labelled

Think of climate scenarios like speed limits for greenhouse gas emissions:

```
  SSP1-2.6  ──  Strict limit. Emissions drop fast.          +1.5°C by 2100
  SSP2-4.5  ──  Moderate limit. Emissions peak ~2040.       +2.4°C by 2100
  SSP5-8.5  ──  No limit. Emissions rise all century.       +4.3°C by 2100
```

The models we use come from the **HighResMIP** group — a CMIP6 sub-project focused on
running models at very high spatial resolution. To save computing cost, all HighResMIP
models were run under **one** emissions pathway: approximately SSP5-8.5 (the highest).

When our files are named `ssp245_EC_Earth3P_HR_...`, the `ssp245` label is something
**we wrote** as metadata. It does not change what the API actually gave us. The
underlying model ran under high emissions.

**The proof is in Plot D** — the temperature warming trend shows +3.3°C over 70 years:

```
  What SSP2-4.5 predicts for West Texas:  ~+1.5–2°C by 2050  (slow, curved)
  What SSP5-8.5 predicts for West Texas:  ~+3–4°C by 2050    (fast, linear)

  Our measured trend: +3.3°C over 1980–2049  ← matches SSP5-8.5, not SSP2-4.5
```

**What this means practically:**

| Question | Answer |
|---|---|
| Are the SCVR numbers wrong? | No — they are correct for what the data says |
| What scenario do they represent? | Approximately SSP5-8.5 (high-emissions, no-mitigation) |
| Is this conservative or optimistic? | Conservative — it over-estimates risk vs a moderate scenario |
| How different would SSP2-4.5 be? | Roughly half the SCVR signal for temperature variables |
| When does this matter? | When reporting to stakeholders who ask "which scenario did you use?" |

**Fix for production analysis:** Use the NASA NEX-GDDP-CMIP6 dataset which has actual
separate model runs for SSP2-4.5 and SSP5-8.5, allowing a proper side-by-side comparison.
See `docs/data_sources/OPENMETEO_CMIP6_GUIDE.md` section 8 for details.

---

### Limitation 3 — Daily mean wind vs hub height

`sfcWind` is measured at 10 m above ground. Wind turbines at Maverick Creek operate
at 80 m hub height. At higher altitudes wind speeds are generally faster.
A vertical extrapolation would be needed for the wind performance model:

```
  v(hub) = v(10m) × (hub_height / 10)^α
  where α ≈ 0.14 for flat terrain (power law exponent)

  Example: v(10m) = 5 m/s  →  v(80m) ≈ 5 × (80/10)^0.14 ≈ 6.5 m/s
```

For SCVR relative comparisons (baseline vs future), this correction cancels out
and does not affect the SCVR values. It only matters when computing absolute wind
generation performance in notebook 03.

---

### Limitation 4 — Precipitation SCVR interpretation

Negative SCVR for precipitation means the **overall exceedance area shrinks** —
the distribution shifts toward fewer and lighter rain days. It does **not** mean
there are no extreme rain events; it means the general distribution is drier overall.

This is the classic West Texas pattern: fewer total rain days, but the rare events
that do occur can be more intense. The HCR derivation for flood risk in notebook 02
needs to treat these separately:
- Flood HCR from event intensity → look at the upper 1–5% of the distribution
- Drought/soiling HCR from dry-day frequency → look at the zero-precipitation frequency

---

## Output Files

| File | Size | Description |
|---|---|---|
| `data/raw/cmip6/hayhurst_solar/historical_EC_Earth3P_HR_1980_2014.parquet` | ~1 MB | 12,784 daily rows, 7 climate variables, baseline period |
| `data/raw/cmip6/hayhurst_solar/ssp245_EC_Earth3P_HR_2015_2049.parquet` | ~1 MB | 12,784 daily rows (excl. null 2050), future period |
| `data/processed/scvr/hayhurst_solar/ssp245_EC_Earth3P_HR_scvr.parquet` | <50 KB | 35 rows: 7 variables × 5 target years, SCVR + window metadata |
| `data/processed/scvr/hayhurst_solar/figures/` | 8 PNG files | All analysis plots at 150 dpi |

---

## Next Steps → Notebook 02

The SCVR table is the input to notebook 02, which will:

1. Apply **HCR coefficients** (from published literature) to convert SCVR → hazard risk increase
   - Flood: HCR = α × SCVR_precipitation
   - Hail: HCR = β × SCVR_tasmax + γ × SCVR_sfcWind
   - Dust/soiling: HCR = δ × SCVR_dry_spell × SCVR_sfcWind

2. Apply **EFR models** to convert SCVR → equipment life reduction
   - Peck's aging: η = f(SCVR_tasmin, SCVR_hurs) → faster degradation
   - Temp coefficient: f(SCVR_tasmax) → instantaneous power losses
   - Freeze-thaw (Coffin-Manson): f(frost_days × heat_wave_days)

3. Combine into **IUL** (Impaired Useful Life)
   - IUL = EUL × [1 − Σ(EFR_i × SCVR_i)]
   - For Hayhurst Solar: EUL = 25 years → IUL expected to be ~20–23 years based on temperature signals

---

*Related documentation:*
- `docs/data_sources/OPENMETEO_CMIP6_GUIDE.md` — data source details, model descriptions, API reference
- `data/schema/VARIABLES.md` — variable priority tiers and confirmed model availability
- `data/schema/scvr_schema.json` — SCVR output column spec and methodology
