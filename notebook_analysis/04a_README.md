# NB04a — HCR: Hazard Change Ratio

## 1. What is HCR?

**HCR** stands for **Hazard Change Ratio**. It measures how much more (or
less) frequently a specific climate hazard event occurs under future climate
conditions compared to the historical baseline.

```
HCR = (future_frequency - baseline_frequency) / baseline_frequency

  HCR = +0.20  means 20% MORE events per year than baseline
  HCR = -0.40  means 40% FEWER events per year (a benefit)
  HCR = 0      means no change in frequency
```

**Intuitively:** if a solar farm historically experienced about 2.4 extreme
precipitation days per year, and climate models project 2.6 in the future,
the HCR = (2.6 - 2.4) / 2.4 = +0.08, meaning +8% more extreme rain days.

HCR captures the **frequency** change — how many more (or fewer) events
happen — not the **severity** change (how intense each event is). It feeds
Channel 1 (Business Interruption) of the financial model, where additional
events translate to additional revenue lost from operational shutdowns,
curtailment, or site inaccessibility.

**What HCR does NOT measure:**
- Equipment degradation from sustained climate stress → that's EFR (NB04b)
- The dollar impact of the frequency change → that's the BI conversion (NB05)
- Whether the resource (sun, wind) changed → that's SCVR (NB03) and it's ≈ 0

---

## 2. Which Hazards?

### The 5 BI Hazards We Compute HCR For

These are hazards that cause **operational shutdown or curtailment** —
the plant could produce but doesn't because of the event.

#### Heat Wave

```
Definition:   3+ consecutive days where BOTH tasmax AND tasmin exceed
              their per-day-of-year 90th percentile (per-DOY P90),
              with ±15-day smoothing on the threshold
Mechanism:    Inverter thermal protection shutdown + panel derating
Variables:    tasmax, tasmin (compound threshold — both must be exceeded)
Computation:  Published scaling: SCVR_tasmax × 2.5
              (Diffenbaugh et al. 2017 PNAS; Cowan et al. 2017 Sci. Reports)
              Cross-validated against direct counting: implied scaling 2.7×

Nuances:
  - This is a COMPOUND definition — both day AND night must be hot
  - Per-DOY thresholds adapt to seasonality (a hot March day ≠ a hot July day)
  - The 3-consecutive-day requirement filters one-off hot days (synoptic noise)
  - The 2.5× scaling was derived by Diffenbaugh/Cowan from their own
    event counting in climate models — we reuse their published result
  - We do NOT show Pathway B day counts for this hazard because the
    per-DOY P90 compound definition has a tiny baseline (~1.5 days/yr),
    giving misleading percentages. The published scaling is calibrated
    for a different, more common threshold definition (~15 days/yr).
```

#### Extreme Precipitation

```
Definition:   Days where daily precipitation exceeds the 95th percentile
              of baseline wet days (days with pr ≥ 1mm)
Mechanism:    Site flooding, equipment submersion, access road washout
Variables:    pr (precipitation)
Computation:  Direct counting from daily CMIP6 data
              (No published site-level scaling exists; mean SCVR ≈ 0
               but extreme events increase — Jensen's inequality)

Nuances:
  - "Wet-day" P95: the threshold is computed from days with pr ≥ 1mm,
    excluding dry days. At arid sites like Hayhurst, ~78% of days are
    dry, so all-day P95 would be a meaningless ~6mm threshold.
  - Published scaling CANNOT be used here: Clausius-Clapeyron gives
    ~7%/°C for atmospheric moisture, but this doesn't translate
    directly to flood event frequency at a specific site.
  - The SCVR Report Card flags precipitation as DIVERGENT — mean SCVR
    says "no change" but P95 SCVR says "extremes increasing." Direct
    counting is mandatory.
```

#### Flood (Rx5day)

```
Definition:   Annual maximum rolling 5-day precipitation sum
              (the wettest 5 consecutive days in each year)
Mechanism:    Sustained heavy rainfall → flooding, site submersion
Variables:    pr (precipitation)
Computation:  Direct counting from daily CMIP6 data
              (Same Jensen's inequality issue as extreme_precip)
Unit:         Millimeters (mm), not days — Rx5day is a magnitude metric

Nuances:
  - Rx5day captures SUSTAINED heavy rainfall that causes flooding,
    not just single-day spikes
  - The HCR compares mean annual Rx5day (mm) between baseline and future
  - Values are in mm (e.g., base=60.2mm → fut=61.7mm = +2.6%)
  - This is the standard hydrology metric for flood risk assessment
```

#### Wind Extreme

```
Definition:   Days where daily mean sfcWind exceeds 15 m/s
Mechanism:    Turbine cut-out, panel displacement, structural stress
Variables:    sfcWind (surface wind speed at 10m)
Computation:  Published scaling: SCVR_sfcWind × 1.0 (linear, no amplification)

Nuances:
  - POOR PROXY: NEX-GDDP provides daily MEAN wind, not gusts. Actual
    cut-out events are triggered by instantaneous gusts (3-second peaks),
    which can be 1.5-2× the daily mean.
  - At Hayhurst: 0 baseline days exceed 15 m/s daily mean. The HCR
    is essentially zero regardless of computation approach.
  - SCVR_sfcWind ≈ 0 at both pilot sites — wind patterns are stable
    under climate change at these locations.
  - Included for completeness and for future sites where wind may matter.
```

#### Icing Shutdown

```
Definition:   Days where tasmin < 0°C AND tasmax > 0°C AND
              pr > 0.5mm AND hurs > 85%
              (surface conditions favourable for ice accumulation)
Mechanism:    Blade/panel icing → forced shutdown until thaw
Variables:    tasmin, tasmax, pr, hurs (4-variable compound threshold)
Computation:  Direct counting from daily CMIP6 data
              (No published compound icing scaling factor exists)

Nuances:
  - This is a SURFACE PROXY — real icing depends on vertical
    temperature profile (warm layer aloft + freezing surface),
    which NEX-GDDP doesn't provide.
  - The 85% humidity threshold follows IEC 61400-1 blade icing
    standard (corrected from earlier 75%).
  - At Hayhurst: HCR is strongly NEGATIVE (-44.5% under SSP585)
    because warming reduces the number of days meeting all four
    criteria simultaneously. This is a genuine financial BENEFIT.
  - The BI component is the forced shutdown. The physical ice stress
    on materials is a separate consideration (not modelled here).
```

### Why Only These 5?

The framework classifies all hazards into three categories based on their
**financial mechanism** — not their climate definition:

```
CATEGORY 1 — BI Events (these 5 → HCR output):
  Cause operational shutdown/curtailment.
  The plant COULD produce but DOESN'T because of the event.
  Formula: BI_loss = HCR × baseline_BI_pct × Revenue

CATEGORY 2 — Degradation Inputs (3 hazards → EFR, NB04b):
  freeze_thaw:  Cumulative solder joint fatigue (Coffin-Manson)
  frost_days:   Sub-zero thermal stress on materials
  cold_wave:    Extended cold → thermal shock
  
  These do NOT cause shutdown. The plant operates normally.
  They cause cumulative MATERIAL STRESS that shortens asset life.
  → Routed to EFR (NB04b) via direct cycle counts

CATEGORY 3 — Risk Indicators (2 hazards → flagged):
  fire_weather: High FWI day ≠ actual fire (probabilistic)
  dry_spell:    Contributes to soiling + fire fuel (gradual)
  
  No deterministic $ formula can be applied.
  → Direction and magnitude flagged, no HCR computed
```

---

## 3. When and With What Data?

### Temporal Range

```
Baseline period:   1985–2014 (30 years of historical climate)
Future period:     2026–2055 (30-year asset lifetime projection)
Annual resolution: One HCR value per hazard per year (2026, 2027, ..., 2055)
```

### Data Source

```
Source:    NASA NEX-GDDP-CMIP6 (bias-corrected, downscaled to 0.25°)
Access:    Via THREDDS/NCSS, cached locally as NetCDF files
Models:    20 CMIP6 models with complete coverage across all variables
Variables: tasmax, tasmin, pr, hurs, sfcWind (daily values)
Scenarios: SSP2-4.5 (moderate emissions) and SSP5-8.5 (high emissions)
```

### How Many Data Points?

```
Per model:  ~10,950 daily values per variable per period (30 years × 365 days)
Pooled:     20 models × 10,950 = ~219,000 daily values per variable per period
Total:      ~219,000 values × 5 variables × 2 periods = ~2.2 million values loaded
```

### Why Daily Data?

HCR counts threshold exceedances — days where a variable crosses a specific
value. This requires DAILY resolution. Annual or monthly data would average
away the extreme days that matter for hazard counting.

---

## 4. How We Calculate HCR — The Methodology

### Step-by-Step Flow

```
SCVR Report (from NB03)
  │
  │  7 variables, 6+ metrics each,
  │  Tail Confidence per variable
  │
  ├─► For EACH of the 5 BI hazards, ask:
  │
  │   Does a published, peer-reviewed scaling factor exist?
  │   │
  │   ├── YES (heat_wave, wind_extreme):
  │   │     HCR(t) = annual_SCVR(t) × published_scaling_factor
  │   │     
  │   │     heat_wave:    SCVR_tasmax(t) × 2.5
  │   │     wind_extreme: SCVR_sfcWind(t) × 1.0
  │   │     
  │   │     Annual SCVR from 3-anchor linear fit (NB03)
  │   │     Scaling from Diffenbaugh 2017 (PNAS) / Cowan 2017
  │   │     Cross-validated against direct counting (implied 2.7×)
  │   │
  │   └── NO (extreme_precip, flood_rx5day, icing_shutdown):
  │         Must compute directly from daily CMIP6 data
  │         │
  │         │  Step 1: Load daily data for 20 models × 60 years
  │         │  Step 2: Compute baseline thresholds from 1985-2014
  │         │          (per-DOY P90 for heat, P95 wet-day for precip)
  │         │  Step 3: Count events in baseline AND future using
  │         │          SAME thresholds (baseline thresholds are fixed)
  │         │  Step 4: HCR = (future_count - baseline_count) / baseline_count
  │         │  Step 5: Interpolate annually via 3-anchor linear fit:
  │         │          3 decade windows → 3 HCR points → linear fit → 30 values
  │         │
  │         Why direct counting is necessary:
  │           - Precipitation: mean SCVR ≈ 0 but extremes increase
  │             (Jensen's inequality — published scaling gives wrong sign)
  │           - Icing: 4-variable compound threshold, no published scaling
  │           - Rx5day: no published site-level flood frequency scaling
  │
  ├─► Also counts ALL 10 hazards (including degradation + indicators)
  │   and saves intermediate counts for NB04b (EFR)
  │
  └─► Output:
        hcr_annual.parquet    (5 hazards × 2 scenarios × 30 years = 300 rows)
        hcr_results.json      (metadata + risk indicators)
        hazard_counts_intermediate.parquet (all 10 hazards for NB04b)
```

### The Annual Interpolation (3-Anchor Fit)

```
For each hazard, we don't compute HCR for every individual year (too noisy).
Instead:

  1. Split future into 3 non-overlapping decades:
     [2026-2035], [2036-2045], [2046-2055]

  2. Compute HCR for each decade (anchor point):
     HCR_early  (midpoint 2030.5)
     HCR_mid    (midpoint 2040.5)
     HCR_late   (midpoint 2050.5)

  3. Fit a linear trend through the 3 anchor points:
     HCR(t) = slope × t + intercept

  4. Read off annual values for all 30 years

  Exception: dry_spell uses epoch mean as flat value
  (max metric cannot be interpolated linearly)
```

### Cross-Validation

For heat_wave (the only hazard with published scaling), we run BOTH:
- Published scaling: SCVR × 2.5 = +20%
- Direct counting: implied scaling = 2.7×

These agree within 8% — validating the published scaling factor at this site.

---

## 5. Pipeline Position

```
  fetch_cmip6.py     compute_scvr.py     NB04a              NB04b           Dashboard
  (data download)    (SCVR Report)       (HCR)              (EFR)           (Streamlit)
       │                  │                 │                  │                │
       ▼                  ▼                 ▼                  ▼                ▼
  data/cache/        data/output/      data/output/       data/output/     Live app
  thredds/*.nc       scvr/<site>/      hcr/<site>/        efr/<site>/
  (21K+ files)       scvr_report.json  hcr_annual.parq    efr_annual.parq
                                       hcr_results.json   efr_results.json
                                       counts_interm.parq
                     
  ← Downloaded →     ← Computed →      ← YOU ARE HERE →   ← Reads from    ← Reads from
    once               once               NB04a             NB04a+NB03       NB04a+NB04b
```

### What NB04a Reads

| Input | Source | What it provides |
|-------|--------|-----------------|
| `scvr_report.json` | NB03 / compute_scvr.py | Annual SCVR per variable, Tail Confidence, Report Card |
| `sites.json` | Data schema | Site coordinates, capacity, EUL |
| `data/cache/thredds/*.nc` | fetch_cmip6.py | 21K+ daily NetCDF files (5 variables × 20+ models × 60 years) |

### What NB04a Writes

| Output | Purpose | Consumer |
|--------|---------|----------|
| `hcr_annual.parquet` | 5 BI hazards × 2 SSP × 30 years | Dashboard, NB05 |
| `hcr_results.json` | Epoch summary, risk indicators, routing | Dashboard |
| `hazard_counts_intermediate.parquet` | All 10 hazard counts per model | NB04b (EFR) |
| `hcr_timeline.png` | Visualization | Reference |

---

## 6. Key Results (Hayhurst Texas Solar, SSP5-8.5)

```
PUBLISHED SCALING:
  heat_wave:       +20.0%  (Diffenbaugh 2017, scaling 2.5×)
  wind_extreme:    -2.6%   (SCVR ≈ 0, essentially no signal)

DIRECT COUNTING:
  extreme_precip:  +5.5%   base=2.4 → fut=2.6 days/yr
  flood_rx5day:    +2.6%   base=60.2 → fut=61.7 mm
  icing_shutdown:  -44.5%  base=0.6 → fut=0.3 days/yr (warming benefit)

RISK INDICATORS (flagged, not in HCR output):
  fire_weather:    -0.5%   (decreasing — FWI composite flips under SSP585)
  dry_spell:       +10.6%  (increasing — longer dry periods)
```

---

## 7. Output Schema

### hcr_annual.parquet

| Column | Type | Description |
|--------|------|-------------|
| site_id | string | Site name (e.g., "Hayhurst Texas Solar") |
| scenario | string | SSP scenario (ssp245, ssp585) |
| year | int | Year (2026-2055) |
| hazard | string | Hazard name (5 BI hazards only) |
| hcr | float | Hazard Change Ratio (fractional) |
| scvr_input | float | SCVR value used |
| scaling | float | Published scaling factor (0 for direct counting) |
| computation | string | "published_scaling" or "direct_counting" |
| confidence | string | Confidence level |

### hcr_results.json

```json
{
  "site_id": "Hayhurst Texas Solar",
  "classification": "3-category (BI events / degradation / risk indicators)",
  "routing_decision": "Published scaling where available; direct counting where necessary",
  "epoch_summary": {
    "heat_wave": {
      "ssp585": {
        "mean_hcr": 0.1997,
        "computation": "published_scaling",
        "published_source": "Diffenbaugh et al. 2017 (PNAS)",
        "scaling_factor": 2.5
      }
    },
    "extreme_precip": {
      "ssp585": {
        "mean_hcr": 0.0555,
        "computation": "direct_counting",
        "baseline_annual_rate": 2.43,
        "future_annual_rate": 2.57,
        "rate_unit": "days/yr"
      }
    }
  },
  "risk_indicators": {
    "fire_weather": {"ssp585": {"direction": "decreasing", "magnitude_pct": -0.5}},
    "dry_spell": {"ssp585": {"direction": "increasing", "magnitude_pct": 10.6}}
  },
  "degradation_hazards_moved_to_efr": ["cold_wave", "freeze_thaw", "frost_days"]
}
```

---

## 8. How to Run

```bash
# Activate virtual environment
source .venv/bin/activate

# Execute (heavy — loads 21K+ NC files, takes 2-5 minutes)
jupyter nbconvert --to notebook --execute 04a_hcr_hazard_change_ratio.ipynb --inplace

# Or open interactively
jupyter lab
```

**Prerequisite:** SCVR Report must exist at `data/output/scvr/<site>/scvr_report.json`

---

## 9. Related Documentation

| Topic | Doc |
|-------|-----|
| HCR methodology (full) | `docs/learning/C_financial_translation/07_hcr_hazard_change.md` |
| Why published scaling vs direct counting | `docs/discussion/hcr_financial/pathway_defensibility.md` |
| HCR/EFR boundary (3 categories) | `docs/discussion/hcr_financial/hcr_efr_boundary.md` |
| Jensen's inequality (why direct counting for precip) | `docs/discussion/hcr_financial/jensen_inequality_hcr_scvr.md` |
| Orchestrator (routing matrix) | `docs/learning/C_financial_translation/06b_climate_risk_orchestrator.md` |
| SCVR Report methodology | `docs/learning/B_scvr_methodology/04_scvr_methodology.md` |
| EFR notebook (NB04b) | `notebook_analysis/04b_README.md` |
