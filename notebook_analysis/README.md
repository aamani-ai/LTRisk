# notebook_analysis/ — Climate Risk Translation Notebooks

## What These Notebooks Do

These notebooks translate the SCVR Report (climate distribution shifts) into
two parallel financial channels: **HCR (business interruption)** and **EFR
(equipment degradation)**. They sit between the SCVR production pipeline
and the Streamlit dashboard.

```
PIPELINE POSITION:

  fetch_cmip6.py → compute_scvr.py → [NB04a + NB04b] → scvr_dashboard.py
  (data)           (SCVR Report)      (HCR + EFR)       (dashboard)
       ↓                ↓                  ↓                  ↓
  data/cache/      data/output/       data/output/       Streamlit app
  thredds/*.nc     scvr/<site>/       hcr/<site>/        (live)
                   scvr_report.json   efr/<site>/
```

---

## Active Notebooks

### NB04a — HCR: Hazard Change Ratio (Channel 1 — Business Interruption)

```
PURPOSE:
  Compute how many MORE hazard events occur per year under climate change.
  Only BI events (operational shutdown/curtailment) produce HCR output.

INPUTS:
  data/output/scvr/<site>/scvr_report.json  ← SCVR Report from NB03
  data/cache/thredds/*.nc                   ← 21K+ daily NetCDF files

COMPUTATION (heavy — loads all daily data, ~2-5 minutes):
  1. Load daily CMIP6 data for 20+ models × 5 variables × 60 years
  2. Compute baseline thresholds (per-DOY P90, P95 wet-day, FWI P90)
  3. Count hazard events for ALL 10 hazards (baseline + future)
  4. Cross-validate Pathway A (SCVR × scaling) vs Pathway B (direct counting)
  5. Route to 3 categories:
     - 5 BI hazards → HCR output (Channel 1)
     - 3 degradation hazards → intermediate counts for NB04b
     - 2 risk indicators → flagged with direction

OUTPUTS:
  data/output/hcr/<site>/hcr_annual.parquet                ← 5 hazards × 2 SSP × 30 years
  data/output/hcr/<site>/hcr_results.json                  ← metadata + risk indicators
  data/output/hcr/<site>/hazard_counts_intermediate.parquet ← all 10 hazards for NB04b
  data/output/hcr/<site>/hcr_timeline.png                  ← visualization

VERIFICATION: 12 automated checks (routing, signs, schema)
```

### NB04b — EFR: Equipment Failure Ratio (Channel 2 — Equipment Degradation)

```
PURPOSE:
  Compute how much FASTER equipment degrades under climate change.
  Three physics models, two computation modes.

INPUTS:
  data/output/scvr/<site>/scvr_report.json                 ← SCVR Report from NB03
  data/output/hcr/<site>/hazard_counts_intermediate.parquet ← freeze-thaw counts from NB04a

COMPUTATION (fast — reads from NB04a output, ~5 seconds):
  1. Peck's Thermal Aging (Mode A):
     SCVR_tas → ΔT → AF = 2^(ΔT/10) → EFR_peck
     Input: annual SCVR from Report Card
     No thresholds needed — direct physics

  2. Coffin-Manson Thermal Cycling (Mode B):
     Direct freeze-thaw cycle counts from NB04a intermediate data
     Baseline vs future 0°C crossing count → EFR_coffin
     Mode B mandatory — Mode A gives wrong direction at Hayhurst

  3. Palmgren-Miner Wind Fatigue (Mode A):
     SCVR_sfcWind ≈ 0 → EFR_palmgren ≈ 0
     Wind distribution unchanged at pilot sites

  4. Combined: EFR = 80% × Peck's + 20% × Coffin-Manson
     IUL = EUL × (1 - avg_EFR)

OUTPUTS:
  data/output/efr/<site>/efr_annual.parquet  ← per year: Peck's + C-M + combined
  data/output/efr/<site>/efr_results.json    ← metadata + IUL estimate
  data/output/efr/<site>/efr_timeline.png    ← visualization

VERIFICATION: 8 automated checks (signs, modes, IUL range)
```

---

## Data Flow Between Notebooks

```
                    NB03 (SCVR)
                    compute_scvr.py
                         │
                    scvr_report.json
                    (7 vars, 6+ metrics,
                     Tail Confidence)
                         │
              ┌──────────┴──────────┐
              │                     │
         NB04a (HCR)           NB04b (EFR)
         ┌────────────┐        ┌────────────┐
         │            │        │            │
         │ Load 21K   │        │ Read from  │
         │ NC files   │        │ NB04a      │
         │ (2-5 min)  │        │ (~5 sec)   │
         │            │        │            │
         │ Count ALL  │────────│ Peck's     │
         │ 10 hazards │  intermediate  │ (Mode A)   │
         │            │  .parquet      │            │
         │ Route:     │        │ Coffin-M   │
         │  5 → HCR   │        │ (Mode B)   │
         │  3 → EFR   │        │            │
         │  2 → flags  │        │ Combined   │
         │            │        │ + IUL      │
         └────┬───────┘        └────┬───────┘
              │                     │
    hcr_annual.parquet    efr_annual.parquet
    hcr_results.json      efr_results.json
              │                     │
              └──────────┬──────────┘
                         │
                    Dashboard
                    (scvr_dashboard.py)
                    HCR tab + EFR tab
```

**Why two notebooks instead of one?**
- Each is reviewable independently (HCR reviewer doesn't need Arrhenius math)
- NB04b runs in seconds (no NC loading) — fast iteration on EFR parameters
- Clean separation of Channel 1 (BI) from Channel 2 (degradation)
- NB04a's intermediate Parquet is the contract between them

---

## The Three-Category Classification

NB04a counts events for all 10 hazards but routes them to different destinations:

```
CATEGORY                  HAZARDS                   DESTINATION
──────────────────────    ──────────────────────    ─────────────────────
Category 1: BI Events     heat_wave                 → hcr_annual.parquet
(cause operational         extreme_precip              (Channel 1)
 shutdown)                 flood_rx5day
                           wind_extreme
                           icing_shutdown

Category 2: Degradation    freeze_thaw               → hazard_counts_
(cause material stress,    frost_days                   intermediate.parquet
 not shutdown)             cold_wave                   → NB04b (EFR)

Category 3: Risk           fire_weather               → hcr_results.json
Indicators                 dry_spell                    "risk_indicators" section
(probabilistic, no                                      (direction + magnitude)
 deterministic $)
```

---

## Computation Modes

Both channels use the same routing logic — the SCVR Report Card's Tail
Confidence flag determines which mode is used:

```
                    CHANNEL 1 (HCR)          CHANNEL 2 (EFR)
                    ───────────────          ───────────────
Tail Conf. HIGH:    Pathway A preferred      Mode A preferred
                    (SCVR × scaling)         (SCVR → physics)

Tail Conf. DIVERG:  Pathway B mandatory      Mode B mandatory
                    (direct counting)        (daily integration)

WHY:
  Pathway/Mode A uses the MEAN shift (SCVR) — avoids threshold subjectivity
  Pathway/Mode B uses DAILY DATA — captures non-linear effects A misses
  
  A is preferred because it's more defensible (no arbitrary thresholds)
  B is mandatory when A gives wrong answers (Jensen's inequality)
  
  See: docs/discussion/hcr_financial/pathway_defensibility.md
```

---

## Key Results (Hayhurst Solar, SSP5-8.5)

```
CHANNEL 1 — HCR (Business Interruption):
  heat_wave:       +20.0% more events  (Pathway A, 2.5× scaling)
  extreme_precip:  +5.3%               (Pathway B, direct counting)
  flood_rx5day:    +2.5%               (Pathway B)
  icing_shutdown:  -5.2% (benefit)     (Pathway B)
  wind_extreme:    -2.6%               (Pathway A)

CHANNEL 2 — EFR (Equipment Degradation):
  Peck's (Mode A):          +15.6% faster aging
  Coffin-Manson (Mode B):   -30.1% fewer freeze-thaw cycles (benefit)
  Combined (80/20):         +6.5% net degradation acceleration
  IUL:                      23.4 years (EUL=25, 1.6 years lost)

RISK INDICATORS:
  fire_weather:  -0.5% (decreasing at this site under SSP585)
  dry_spell:     +10.6% (increasing)

KEY FINDING:
  Channel 2 (EFR) >> Channel 1 (HCR) by ~50-250×
  The dominant risk is equipment aging faster, not more shutdowns.
```

---

## How to Run

```bash
# Activate virtual environment
source .venv/bin/activate

# Run NB04a first (heavy — 2-5 minutes, loads all daily data)
jupyter nbconvert --to notebook --execute 04a_hcr_hazard_change_ratio.ipynb --inplace

# Then run NB04b (fast — ~5 seconds, reads from NB04a output)
jupyter nbconvert --to notebook --execute 04b_efr_equipment_degradation.ipynb --inplace
```

Or open in Jupyter Lab and run cells interactively:
```bash
jupyter lab
```

**Prerequisite:** SCVR Report must exist at `data/output/scvr/<site>/scvr_report.json`
(produced by `scripts/analysis/scvr/compute_scvr.py`).

Notebooks assume the working directory is the **project root** (not `notebook_analysis/`).

---

## Output Schemas

### hcr_annual.parquet

| Column | Type | Description |
|--------|------|-------------|
| site_id | string | Site name (e.g., "Hayhurst Texas Solar") |
| scenario | string | SSP scenario (ssp245, ssp585) |
| year | int | Year (2026-2055) |
| hazard | string | Hazard name (5 BI hazards only) |
| hcr | float | Hazard Change Ratio (fractional, e.g., 0.185 = +18.5%) |
| scvr_input | float | SCVR value used (for Pathway A) |
| scaling | float | Scaling factor (for Pathway A; 0 for Pathway B) |
| pathway | string | "A" or "B" |
| confidence | string | Confidence level |

### efr_annual.parquet

| Column | Type | Description |
|--------|------|-------------|
| site_id | string | Site name |
| scenario | string | SSP scenario |
| year | int | Year (2026-2055) |
| efr_peck | float | Peck's thermal aging EFR (Mode A) |
| efr_coffin | float | Coffin-Manson cycling EFR (Mode B, can be negative) |
| efr_palmgren | float | Palmgren-Miner wind fatigue EFR (Mode A, ≈0) |
| efr_combined | float | Weighted combination (80% Peck's + 20% C-M) |
| mode_peck | string | "A" |
| mode_coffin | string | "B" |

---

## Archive

NB01-03 were stepping stones — each superseded by production scripts:

| Notebook | Superseded by |
|---|---|
| `01_hayhurst_solar_scvr.ipynb` | `scripts/analysis/scvr/compute_scvr.py` |
| `02_NEX_GDDP_CMIP6_THREDDS.ipynb` | `scripts/data/fetch_cmip6.py` |
| `03_integrated_scvr_cmip6.ipynb` | `scripts/analysis/scvr/compute_scvr.py` |
| `04_hcr_efr_combined_archived.ipynb` | Split into 04a + 04b (April 2026) |

Archived notebooks are in `archive/` for reference.

---

## Related Documentation

| Topic | Doc |
|-------|-----|
| SCVR Report methodology | `docs/learning/B_scvr_methodology/04_scvr_methodology.md` |
| Orchestrator (routing layer) | `docs/learning/C_financial_translation/06b_climate_risk_orchestrator.md` |
| HCR methodology | `docs/learning/C_financial_translation/07_hcr_hazard_change.md` |
| EFR methodology | `docs/learning/C_financial_translation/08_efr_equipment_degradation.md` |
| Why Pathway A is preferred | `docs/discussion/hcr_financial/pathway_defensibility.md` |
| HCR/EFR boundary (3-category) | `docs/discussion/hcr_financial/hcr_efr_boundary.md` |
| EFR two modes | `docs/discussion/efr_degradation/efr_two_modes.md` |
| Framework architecture | `docs/discussion/architecture/framework_architecture.md` |
