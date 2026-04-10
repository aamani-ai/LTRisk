# Climate Risk Orchestrator — Routing Layer

**The orchestrator maps InfraSure's 10 canonical hazards to LTRisk's
climate signal capabilities.** For each hazard, it determines: what
computation method to use, whether severity is integrated, and how the
result connects to the hazards repo's baseline BI.

```
SCVR Report                ORCHESTRATOR                Financial Channels
(what changed?)            (for each canonical hazard)  (what's the $ impact?)

7 variables            →   Computation method       →   HCR (freq × severity)
6+ metrics each            (published scaling or        → Additional_BI
Tail Confidence             direct computation)      →   EFR (degradation)
Severity diagnostic        Severity integration     →   Risk flags
                           BI baseline availability  →   Documented gaps
```

This doc bridges two InfraSure pipelines:
- **Hazards repo** — historical risk from NOAA/NRI (1996-2024, backward-looking)
- **LTRisk** — forward climate projections from CMIP6 (2026-2055, forward-looking)

---

## 1. Purpose

For each of InfraSure's 10 canonical hazards, the orchestrator answers:

1. **Can LTRisk compute an HCR?**
   Published scaling where a peer-reviewed factor exists.
   Direct computation from daily CMIP6 data where it doesn't.
   Documented gap where CMIP6 can't project the hazard at all.

2. **Is severity integrated?**
   HCR = frequency_ratio × severity_ratio (expected shortfall decomposition).
   For direct counting hazards: severity is genuinely additive.
   For published scaling: severity may already be embedded (report as range).

3. **Does baseline BI exist?**
   Hazards repo has BI for 3 hazards (Hail, Tornado, Strong Wind).
   NRI has EAL for all (but EAL ≠ BI — linearity assumption required).
   Formula: Additional_BI = baseline_BI × HCR.

4. **Where do the two pipelines complement each other?**
   Hazards repo covers historical frequency + severity (backward).
   LTRisk covers climate change delta (forward).
   Together: future_risk = baseline × (1 + HCR).

---

## 2. InfraSure's Canonical Hazard Taxonomy (Top-Down)

These are InfraSure's 10 canonical hazard types from the hazards pipeline,
plus additional hazards relevant to renewable energy assets. Each has a
formal NOAA definition and is tracked in the hazards repo codebase.

### 2A. Current Canonical Hazards (10 active in pipeline)

| # | Canonical Name | Definition (abbreviated) | NOAA Event Types Mapped | Primary Asset Impact |
|---|----------------|--------------------------|-------------------------|---------------------|
| 1 | **Hail** | Ice pellets >= 0.75" from convective storms | Hail | Panel glass fracture, module cracking |
| 2 | **Tornado** | Rotating column EF0-EF5 (65-200+ mph) | Tornado | Total structural destruction |
| 3 | **Strong Wind** | Sustained >= 58 mph or equivalent gusts | Thunderstorm Wind, Strong Wind, High Wind | Panel displacement, nacelle stress |
| 4 | **Winter Weather** | Combined snow/sleet/freezing rain (below ice storm) | Winter Storm, Winter Weather, Heavy Snow | Snow load, irradiance reduction |
| 5 | **Ice Storm** | Freezing rain >= 0.25" ice accumulation | Ice Storm | Panel/blade ice loading, drivetrain icing |
| 6 | **Wildfire** | Uncontrolled fire in wildland vegetation | Wildfire | Panel burn, wiring damage, site access loss |
| 7 | **Hurricane** | Tropical cyclone >= 74 mph sustained | Hurricane, Tropical Storm, Hurricane (Typhoon) | Wind + surge + flood compound damage |
| 8 | **Heat Wave** | >= 3 consecutive days at or above 90F/32C | Heat, Excessive Heat | Panel derating, inverter shutdown, Peck's aging |
| 9 | **Riverine Flood** | Overflow from rivers driven by rainfall/snowmelt | Flood, Flash Flood, Heavy Rain | Equipment submersion, foundation erosion |
| 10 | **Coastal Flood** | Seawater inundation from surge/tides/SLR | Coastal Flood, Storm Surge/Tide | Electrical infrastructure, saltwater corrosion |

### 2B. Additional Hazards (planned or relevant)

| Hazard | Definition | Relevance | Status |
|--------|-----------|-----------|--------|
| **Lightning** | Electrostatic discharge, up to 30kA | Turbine blade strikes, inverter surge | Planned (NRI data available) |
| **Drought** | Prolonged below-average precipitation | Soiling, fire fuel loading, cooling water | Planned (NRI data available) |
| **Earthquake** | Seismic ground shaking | Racking displacement, tower fatigue | Planned (USGS PSHA) |
| **Cold Wave** | Rapid temperature drop below seasonal norm | Thermal shock, lubricant freeze | In HAZARDS list, no damage curve |

### 2C. Future Asset Types and Their Hazard Priorities

| Asset Type | New Hazards vs Solar/Wind |
|-----------|--------------------------|
| **Battery Storage (BESS)** | Thermal runaway from ambient heat, electrolyte flood contamination |
| **Data Centers** | Cooling load increase, UPS degradation, below-grade flood |
| **Offshore Wind** | Hurricane wave loading, marine icing, seabed scour |
| **Transmission/Distribution** | Ice loading on lines, conductor-initiated wildfire |

---


---

## 3. LTRisk's Climate Signal Capabilities

### 3A. SCVR Report Card — 7 Variables

```
Variable    SCVR (SSP585)   Tail Conf.   Annual Strategy    Signal
─────────   ─────────────   ──────────   ───────────────    ──────
tasmax      +0.080          HIGH         anchor_3_linear    Strong
tasmin      +0.173          MODERATE     anchor_3_linear    Strong
tas         +0.105          HIGH         anchor_3_linear    Strong
pr          -0.007          DIVERGENT    period_average     Misleading
sfcWind     -0.026          MOD/HIGH     period_average     Near zero
hurs        -0.036          MODERATE     period_average     Small
rsds        +0.003          MODERATE     period_average     Near zero
```

### 3B. Computation Methods

```
PUBLISHED SCALING (where peer-reviewed factor exists):
  Use the published result. It IS empirical counting done by other
  researchers — we reuse their peer-reviewed work.
  
  Heat wave:    SCVR_tasmax × 2.5 (Diffenbaugh 2017, PNAS)
  Strong wind:  SCVR_sfcWind × 1.0 (trivial, ≈ 0)
  Hurricane:    Knutson 2020 consensus
  Coastal flood: IPCC SLR × exponential amplification

DIRECT COMPUTATION (where no published scaling exists):
  Count threshold exceedances AND compute mean excess (severity)
  from daily CMIP6 data across 20+ models.
  
  Riverine flood: Rx5day + daily P95 exceedance (from daily pr)
  Ice storm:      Compound threshold (tasmin<0, tasmax>0, pr>0.5, hurs>85%)
  Wildfire:       FWI composite (tasmax, hurs, sfcWind, pr)
  Winter weather: Compound threshold (pr + tasmin < 0°C)

NOT COMPUTABLE FROM CMIP6:
  Hail:    needs CAPE, wind shear, freezing level
  Tornado: needs upper-air profiles
```

### 3C. Severity Diagnostic

```
For each hazard, NB04a computes BOTH:
  1. Frequency: how many events cross the threshold
  2. Severity: mean excess above threshold (how far above)

Combined HCR = (1 + HCR_freq) × severity_ratio - 1

  Heat wave:     freq +20%, severity +48% → combined +20% to +34% (range)
  Riverine flood: freq +5.5%, severity +6.5% → combined +12.5%
  Rx5day:        already measures intensity — severity ratio = 1.0
  Ice storm:     compound threshold — severity ratio = 1.0 (ambiguous)

See severity_sensitivity.md for dependencies and Gen.1→2→3 evolution.
```

---

## 4. The Bridge — Mapping Hazards to Signals

This is the core artifact of the orchestrator. For each of InfraSure's
10 canonical hazards, it shows: what can LTRisk compute, how, with what
severity treatment, and whether baseline BI exists for the dollar conversion.

> **BI vs EAL:** BI = lost revenue from downtime. EAL = total economic
> loss. The hazards repo computes BI for 3 hazards (Hail, Tornado,
> Strong Wind). NRI computes EAL for all hazards. EAL ≠ BI. Applying
> HCR (damage-level) to BI requires a linearity assumption.
> See [hcr_redefined_freq_severity.md](../../discussion/hcr_financial/hcr_redefined_freq_severity.md).

### The Routing Matrix

**Part A — HCR Computation: What can LTRisk project for each hazard?**

| Canonical Hazard | CMIP6 Variables | Threshold / Proxy | Method | Severity | HCR (SSP585) |
|---|---|---|---|---|---|
| **Heat Wave** | tasmax, tasmin | Compound: 3+ consec. days, both > per-DOY P90 | Published scaling (2.5×, Diffenbaugh 2017) | RANGE: sev=1.48. Published may embed severity | +20% to +34% |
| **Riverine Flood** (daily) | pr | Daily pr > P95 wet-day threshold | Direct counting | YES: sev=1.07. Combined freq×sev | +12.5% |
| **Riverine Flood** (Rx5day) | pr | Max rolling 5-day sum (mm) | Direct counting | ALREADY CAPTURED (measures intensity) | +2.6% |
| **Strong Wind** | sfcWind | Daily mean > 15 m/s (poor — not gusts) | Published scaling (1.0×) | MOOT — HCR ≈ 0 | ~0% |
| **Ice Storm** | tasmin, tasmax, pr, hurs | Compound: tasmin<0, tasmax>0, pr>0.5mm, hurs>85% | Direct counting | NO — compound, severity ambiguous | -44.5% (benefit) |
| **Wildfire** | tasmax, hurs, sfcWind, pr | FWI proxy: 0.3×T + 0.3×(1-H) + 0.2×W + 0.2×(1-P) | Direct counting (FWI P90) | TBD — composite index | Risk indicator |
| **Hurricane** | — (not in NEX-GDDP) | Needs SST, ocean dynamics | Published (Knutson 2020) | PARTIALLY — "fewer but fiercer" | +7% to +43% |
| **Coastal Flood** | — (not in NEX-GDDP) | Needs SLR + surge models | Published (SLR × amplification) | YES — exponential with SLR | 10-1000× |
| **Winter Weather** | tasmin, pr | Compound: pr > threshold AND tasmin < 0°C | Direct counting | TBD | Decreasing |
| **Hail** | — (not in NEX-GDDP) | Needs CAPE, wind shear, freezing level | **BLOCKED** | N/A | N/A |
| **Tornado** | — (not in NEX-GDDP) | Needs CAPE, SRH, upper-air profiles | **BLOCKED** | N/A | N/A |
| **Drought / Dry Spell** | pr | Max consecutive days pr < 1mm | Direct counting | TBD | Risk indicator |

**Part B — Baseline BI: What does the hazards repo have?**

| Canonical Hazard | Hazards Repo BI? | Damage Curve | Baseline BI Source | Can Compute Additional_BI? |
|---|---|---|---|---|
| Heat Wave | NO | None (gap) | NRI EAL only | NO — missing baseline BI |
| Riverine Flood | NO | HAZUS flood depth | NRI EAL only | PARTIAL (NRI proxy + linearity) |
| Strong Wind | YES | Unanwa sustained wind | NOAA events + forced/recovery hours | YES but ≈ $0 (HCR ≈ 0) |
| Ice Storm | NO | PNNL ice accumulation | NRI EAL only | PARTIAL |
| Wildfire | NO | FSF flame length | NRI EAL only | PARTIAL |
| Hurricane | NO | PNNL/Climada wind speed | NRI EAL only | PARTIAL |
| Coastal Flood | NO | HAZUS flood depth | NRI EAL only | PARTIAL |
| Winter Weather | NO | Ederen severity index | NRI EAL only | PARTIAL |
| Hail | YES | Thirza hail diameter | NOAA events + forced/recovery hours | NO — missing HCR |
| Tornado | YES | Feuerstein wind speed | NOAA events + forced/recovery hours | NO — missing HCR |

**EFR (Equipment Degradation) — separate channel, not event-driven:**

| Model | Method | Input | Status |
|---|---|---|---|
| Peck's (thermal aging) | Published Arrhenius from SCVR_tas | tas, hurs | Active — EFR ≈ +15.6% (SSP585) |
| Coffin-Manson (cycling) | Direct freeze-thaw counts from daily data | tasmin, tasmax | Active — EFR ≈ -30.1% (fewer cycles, benefit) |
| Palmgren-Miner (wind) | SCVR_sfcWind (≈ 0 at TX sites) | sfcWind | Dormant — EFR ≈ 0 |

**Summary:**

```
Hazards with BOTH baseline BI + HCR:    1 (Strong Wind — but HCR ≈ 0)
Hazards with baseline BI but no HCR:    2 (Hail, Tornado — CMIP6 blocked)
Hazards with HCR but no baseline BI:    7 (Heat, Flood, Ice, Wildfire, etc.)
Clean Additional_BI computation:        effectively 0 out of 10 today

The two pipelines cover DIFFERENT hazards.
Closing the gap requires expanding hazards repo BI coverage to
include heat wave, flood, ice storm, wildfire, etc.
```

```
CANONICAL     │ HCR              │ COMPUTATION     │ BASELINE BI         │ CAN COMPUTE     │
HAZARD        │ COMPUTABLE?      │ METHOD          │ (hazards repo)      │ Additional_BI?  │
══════════════╪══════════════════╪═════════════════╪═════════════════════╪═════════════════╡
Heat Wave     │ YES              │ Published       │ NO (not in hazards  │ NO — missing    │
              │                  │ scaling (2.5×,  │ repo BI yet; NRI    │ baseline BI.    │
              │                  │ Diffenbaugh)    │ EAL only)           │ Need Option C2  │
              │                  │                 │                     │ or C3.          │
──────────────┼──────────────────┼─────────────────┼─────────────────────┼─────────────────┤
Hail          │ NO (needs CAPE,  │ BLOCKED         │ YES — full BI calc  │ NO — missing    │
              │ shear — not in   │                 │ (Thirza damage      │ HCR. Use        │
              │ NEX-GDDP)       │                 │ curve + recovery)   │ historical BI.  │
──────────────┼──────────────────┼─────────────────┼─────────────────────┼─────────────────┤
Tornado       │ NO (needs upper  │ BLOCKED         │ YES — full BI calc  │ NO — missing    │
              │ air data)        │                 │ (Feuerstein curve)  │ HCR. Use        │
              │                  │                 │                     │ historical BI.  │
──────────────┼──────────────────┼─────────────────┼─────────────────────┼─────────────────┤
Strong Wind   │ YES (~0 signal)  │ Published       │ YES — full BI calc  │ YES but ≈ $0    │
              │                  │ scaling (1.0×)  │ (Unanwa curve)      │ (HCR ≈ 0)      │
──────────────┼──────────────────┼─────────────────┼─────────────────────┼─────────────────┤
Riverine      │ YES              │ Direct counting │ NO (NRI EAL only,   │ PARTIAL —       │
Flood         │                  │ (Rx5day from    │ not BI)             │ NRI EAL proxy   │
              │                  │ daily pr)       │                     │ + linearity     │
──────────────┼──────────────────┼─────────────────┼─────────────────────┼─────────────────┤
Ice Storm     │ YES              │ Direct counting │ NO (NRI EAL only)   │ PARTIAL         │
              │                  │ (compound       │                     │                 │
              │                  │ threshold)      │                     │                 │
──────────────┼──────────────────┼─────────────────┼─────────────────────┼─────────────────┤
Wildfire      │ YES              │ Direct counting │ NO (NRI EAL only)   │ PARTIAL         │
              │                  │ (FWI from       │                     │                 │
              │                  │ daily data)     │                     │                 │
──────────────┼──────────────────┼─────────────────┼─────────────────────┼─────────────────┤
Hurricane     │ YES (published)  │ Published       │ NO (NRI EAL only)   │ PARTIAL         │
              │                  │ scaling         │                     │                 │
              │                  │ (Knutson 2020)  │                     │                 │
──────────────┼──────────────────┼─────────────────┼─────────────────────┼─────────────────┤
Coastal       │ YES (SLR-based)  │ Published SLR   │ NO (NRI EAL only)   │ PARTIAL         │
Flood         │                  │ projections     │                     │                 │
──────────────┼──────────────────┼─────────────────┼─────────────────────┼─────────────────┤
Winter        │ YES              │ Direct counting │ NO (NRI EAL only)   │ PARTIAL         │
Weather       │                  │ (compound       │                     │                 │
              │                  │ threshold)      │                     │                 │
══════════════╧══════════════════╧═════════════════╧═════════════════════╧═════════════════╝

ADDITIONAL: EFR (Equipment Degradation — separate from HCR, not event-driven)
  Peck's (thermal aging):     Published Arrhenius from SCVR_tas
  Coffin-Manson (cycling):    Direct freeze-thaw counts from daily data
  Palmgren-Miner (wind):      Published S-N from SCVR_sfcWind (≈ 0, effectively zero)
```

### Key Observations

1. **Hail is the #1 gap** — highest financial priority for solar (from insurance
   data) but not computable from CMIP6. The hazards repo has historical BI.
   This is where pipeline complementarity matters most.

2. **Severity changes the numbers significantly** — heat wave goes from +20%
   (frequency only) to +20-34% range (with severity). Flood goes from +5.5%
   to +12.5%. See [severity_sensitivity.md](../../discussion/hcr_financial/severity_sensitivity.md).

3. **Two blocked hazards** (hail, tornado) have full BI from the hazards repo
   but no climate delta from LTRisk. Use historical BI until projections exist.

4. **Seven hazards** can be projected by LTRisk but lack baseline BI from the
   hazards repo. Need NRI EAL proxy (with linearity assumption) or expanded BI coverage.

5. **EFR is separate** — Peck's, Coffin-Manson, and Palmgren-Miner are continuous
   degradation models, not event-driven. The hazards repo doesn't cover these.

---


---

## 5. The Routing Rules

### Rule 1: Start From Canonical Hazards

For each of InfraSure's 10 canonical hazards:
1. Can LTRisk compute an HCR? (yes / blocked)
2. What computation method? (published scaling / direct computation)
3. Is severity integrated? (yes / range / not applicable)
4. Does baseline BI exist? (hazards repo BI / NRI EAL only / none)

### Rule 2: Computation Method

```
Published peer-reviewed scaling exists?
├── YES: Use it (traceable, defensible)
│        Heat wave: SCVR_tasmax × 2.5 (Diffenbaugh 2017)
│        Hurricane: Knutson 2020 consensus
│        Coastal flood: IPCC SLR projections
│
└── NO: Compute directly from daily CMIP6 data
         Count threshold exceedances + compute severity diagnostic
         Riverine flood, ice storm, wildfire, winter weather

This is a data availability question, not a preference hierarchy.
Published scaling IS empirical counting done by other researchers.
See: pathway_defensibility.md
```

### Rule 3: Financial Channel

```
HCR hazards (event-driven BI):
  Formula: Additional_BI = baseline_BI × HCR
  Where baseline_BI comes from hazards repo (when available)
  HCR captures frequency × severity (expected shortfall decomposition)
  Linearity assumption: BI ∝ damage (documented)

EFR (continuous degradation — separate from HCR):
  Peck's thermal aging (published Arrhenius from SCVR_tas)
  Coffin-Manson cycling (direct freeze-thaw counts from daily data)
  Palmgren-Miner wind fatigue (SCVR_sfcWind ≈ 0, effectively zero)

Risk indicators (probabilistic, no deterministic $):
  Wildfire (FWI proxy), drought/dry spell
  Report direction + magnitude. Phase 2: frequency × severity model.

Documented gaps (not computable from CMIP6):
  Hail, tornado — use hazards repo historical BI
  Hurricane, coastal flood — use published external projections
```

### Rule 4: Pipeline Complementarity

```
LTRisk covers:  climate change DELTA (how much risk CHANGES)
Hazards repo:   historical BASELINE (how much risk EXISTS today)

Combined: future_risk = baseline × (1 + HCR)

For hazards BOTH cover:     cross-validate forward vs historical trend
For hazards only A covers:  use historical (no climate delta available)
For hazards only B covers:  need baseline from hazards repo or NRI proxy
```

---

## 6. Coverage Map — What We Cover vs What We Don't

### Hayhurst Solar (24.8 MW, West Texas)

| Hazard | Priority | LTRisk | Haz. Repo | Combined | Notes |
|---|---|---|---|---|---|
| Thermal aging (Peck's) | #1 | FULL | N/A | LTRisk only | EFR ≈ +15.6%, ~$5M NAV impact |
| Hail | #2 | GAP | FULL (Thirza) | Haz. repo only | #1 financial risk for solar |
| Heat wave (BI) | #3 | FULL | NRI EAL | BOTH | HCR +20-34%, cross-validate vs NOAA |
| Riverine flood | #4 | PARTIAL | FULL (HAZUS) | BOTH | LTRisk: Rx5day. Haz repo: depth |
| Wildfire | #5 | PROXY (FWI) | FULL (FSF) | BOTH | LTRisk: FWI proxy. Haz repo: NOAA |
| Freeze-thaw (C-M) | #6 | FULL | N/A | LTRisk only | EFR via direct cycle counts |
| Tornado | #7 | GAP | FULL (Feuerstein) | Haz. repo only | NOAA events + damage curve |
| Strong wind | #8 | PROXY | FULL (Unanwa) | BOTH (haz dom.) | LTRisk: poor proxy (daily mean) |
| Winter weather | #9 | PARTIAL | NRI EAL | BOTH (partial) | LTRisk: frost/ice proxy |
| Hurricane | #10 | GAP | FULL (PNNL) | Haz. repo only | Inland TX: low but non-zero |

**Coverage summary:**
- LTRisk FULL: 3/10 (thermal aging, heat wave, freeze-thaw)
- LTRisk PARTIAL: 2/10 (flood, winter weather)
- LTRisk PROXY: 2/10 (wildfire, strong wind)
- LTRisk GAP: 3/10 (hail, tornado, hurricane — covered by hazards repo)
- Hazards Repo FULL: 7/10
- COMBINED: 9/10 hazards covered by at least one pipeline
- REMAINING GAP: Coastal flood (inland site — low priority), Lightning (planned)

### Maverick Wind (491.6 MW, Central Texas)

| Hazard | Priority | LTRisk | Haz. Repo | Combined |
|---|---|---|---|---|
| Icing shutdown (BI) | #1 | PROXY | NRI | BOTH (partial) |
| Wind fatigue (P-M) | #2 | FULL (≈0) | N/A | LTRisk only |
| Hail (blade erosion) | #3 | GAP | FULL | Haz. repo only |
| Strong wind | #4 | PROXY | FULL | Haz. repo dominant |
| Tornado | #5 | GAP | FULL | Haz. repo only |
| Heat (nacelle) | #6 | PARTIAL | NRI | BOTH (partial) |

---


---

## 7. Worked Example — Hayhurst Solar, Full Routing

Walking through key hazards for one asset:

```
ASSET: Hayhurst Texas Solar, 24.8 MW, SSP5-8.5, Year 2040

STEP 1: Read SCVR Report Card
  tasmax: +0.080, HIGH        tas: +0.105, HIGH
  tasmin: +0.173, MODERATE    pr: -0.007, DIVERGENT
  sfcWind: -0.026, MOD/HIGH   hurs: -0.036, MODERATE

STEP 2: Route each hazard

  HEAT WAVE:
    Method: Published scaling (SCVR_tasmax × 2.5, Diffenbaugh 2017)
    HCR_freq: 0.080 × 2.5 = +20.0%
    Severity: mean excess 1.29°C → 1.91°C, ratio = 1.48
    HCR range: +20% (published alone) to +34% (× severity)
    Caveat: published 2.5× may already embed severity
    Baseline BI: NOT available from hazards repo (NRI EAL only)

  RIVERINE FLOOD (daily P95):
    Method: Direct counting (no published site-level scaling)
    HCR_freq: +5.5% (from daily threshold counting)
    Severity: mean excess 7.79mm → 8.30mm, ratio = 1.065
    HCR_combined: 1.055 × 1.065 - 1 = +12.5%
    Baseline BI: NOT available (NRI EAL only)

  RIVERINE FLOOD (Rx5day):
    Method: Direct counting (max 5-day rolling precipitation)
    HCR: +2.6% (already measures intensity in mm, no separate severity)
    Baseline BI: NOT available

  ICE STORM:
    Method: Direct counting (4-variable compound threshold)
    HCR_freq: -44.5% (warming reduces icing — BENEFIT)
    Severity: not applied (compound threshold, ambiguous)
    Baseline BI: NOT available

  STRONG WIND:
    Method: Published scaling (1.0×)
    HCR: ~0% (SCVR_sfcWind ≈ 0, no climate signal)
    Baseline BI: YES (hazards repo has full BI from NOAA events)
    Additional_BI = baseline_BI × 0 ≈ $0

  HAIL (documented gap):
    LTRisk: CANNOT compute (no CAPE in CMIP6)
    Hazards repo: HAS full BI ($24K/yr est. from NOAA events)
    Report: "Historical hail BI: $24K/yr. Climate projection: not available."

  WILDFIRE (risk indicator):
    Method: FWI proxy from daily data
    Direction: -0.5% (SSP585 — FWI flips at this site)
    No deterministic $ — flagged only
```

---

## 8. Draft hazard_taxonomy.yaml Schema

Machine-readable version of the routing matrix. When the YAML becomes
code, NB04a would load this to determine its routing automatically.

```yaml
# hazard_taxonomy.yaml — Climate Risk Orchestrator Configuration
# Version: 2.0 (aligned with canonical hazards, severity integration)

metadata:
  version: "2.0"
  last_updated: "2026-04"
  asset_types: ["solar_pv", "onshore_wind"]
  scenarios: ["ssp245", "ssp585"]
  hcr_definition: "frequency_ratio × severity_ratio - 1 (expected shortfall)"

hazards:

  # ── CANONICAL: Heat Wave ───────────────────────────────────────────
  heat_wave:
    canonical_name: "Heat Wave"
    category: "bi_event"
    computation: "published_scaling"
    scaling: 2.5
    published_source: "Diffenbaugh et al. 2017 (PNAS); Cowan et al. 2017"
    input_variables: ["tasmax", "tasmin"]
    threshold: "Compound: 3+ consec. days, both > per-DOY P90"
    severity_integrated: "range"
    severity_note: "Published 2.5× may embed severity. Report range."
    baseline_bi_available: false
    baseline_bi_source: "NRI EAL only"

  # ── CANONICAL: Riverine Flood (daily exceedance) ───────────────────
  riverine_flood_daily:
    canonical_name: "Riverine Flood"
    sub_metric: "P95 daily exceedance"
    category: "bi_event"
    computation: "direct_counting"
    input_variables: ["pr"]
    threshold: "Daily pr > P95 wet-day threshold"
    severity_integrated: true
    severity_note: "Combined freq × severity. No double-counting risk."
    baseline_bi_available: false

  # ── CANONICAL: Riverine Flood (Rx5day) ─────────────────────────────
  riverine_flood_rx5day:
    canonical_name: "Riverine Flood"
    sub_metric: "5-day max precipitation"
    category: "bi_event"
    computation: "direct_counting"
    input_variables: ["pr"]
    threshold: "Annual max rolling 5-day sum (mm)"
    severity_integrated: "already_captured"
    severity_note: "Measures intensity (mm), not count. Severity in metric."
    baseline_bi_available: false

  # ── CANONICAL: Strong Wind ─────────────────────────────────────────
  strong_wind:
    canonical_name: "Strong Wind"
    category: "bi_event"
    computation: "published_scaling"
    scaling: 1.0
    input_variables: ["sfcWind"]
    threshold: "Daily mean sfcWind > 15 m/s (proxy — not gusts)"
    severity_integrated: false
    severity_note: "HCR ≈ 0 — severity is moot"
    baseline_bi_available: true
    baseline_bi_source: "Hazards repo: NOAA events + Unanwa damage curve"

  # ── CANONICAL: Ice Storm ───────────────────────────────────────────
  ice_storm:
    canonical_name: "Ice Storm"
    category: "bi_event"
    computation: "direct_counting"
    input_variables: ["tasmin", "tasmax", "pr", "hurs"]
    threshold: "Compound: tasmin<0, tasmax>0, pr>0.5mm, hurs>85%"
    severity_integrated: false
    severity_note: "Compound threshold — severity ambiguous"
    baseline_bi_available: false

  # ── CANONICAL: Wildfire (risk indicator) ───────────────────────────
  wildfire:
    canonical_name: "Wildfire"
    category: "risk_indicator"
    computation: "direct_counting"
    input_variables: ["tasmax", "hurs", "sfcWind", "pr"]
    threshold: "FWI proxy: 0.3×T + 0.3×(1-H) + 0.2×W + 0.2×(1-P)"
    severity_integrated: false
    note: "High FWI ≠ fire. Probabilistic treatment needed."

  # ── CANONICAL: Drought / Dry Spell (risk indicator) ────────────────
  dry_spell:
    canonical_name: "Drought"
    category: "risk_indicator"
    computation: "direct_counting"
    input_variables: ["pr"]
    threshold: "Max consecutive days with pr < 1mm"

  # ── DEGRADATION → EFR (Channel 2) ─────────────────────────────────
  freeze_thaw:
    canonical_name: "Winter Weather"
    category: "degradation"
    efr_model: "coffin_manson"
    computation: "direct_counting"
    input_variables: ["tasmin", "tasmax"]
    threshold: "Days where tasmin < 0°C AND tasmax > 0°C"
    note: "Published mean approximation gives wrong direction. Direct counts mandatory."

  frost_days:
    canonical_name: "Winter Weather"
    category: "degradation"
    efr_model: "coffin_manson"
    input_variables: ["tasmin"]
    threshold: "Days where tasmin < 0°C"

  cold_wave:
    canonical_name: "Winter Weather"
    category: "degradation"
    efr_model: "coffin_manson"
    input_variables: ["tasmin", "tasmax"]
    threshold: "Compound: 3+ consec. days, both temps < P10"

  # ── DOCUMENTED GAPS ────────────────────────────────────────────────
  hail:
    canonical_name: "Hail"
    category: "gap"
    reason: "Requires CAPE, wind shear — not in NEX-GDDP"
    hazards_repo: "Full BI computation (Thirza damage curve)"

  tornado:
    canonical_name: "Tornado"
    category: "gap"
    reason: "Requires upper-air data"
    hazards_repo: "Full BI computation (Feuerstein damage curve)"

  hurricane:
    canonical_name: "Hurricane"
    category: "gap"
    reason: "Requires SST, ocean dynamics"
    published_scaling: "Knutson 2020: freq -5-10%, wind +5%, rain +14%"

  coastal_flood:
    canonical_name: "Coastal Flood"
    category: "gap"
    reason: "Requires SLR + surge models"
    published_scaling: "Buchanan 2020: 10-1000× per 0.5m SLR"
```

---

## 9. Connection to FIDUCEO Uncertainty Mapping

The orchestrator's routing decisions map to FIDUCEO uncertainty layers:

| Orchestrator Decision | FIDUCEO Layer | Uncertainty Type |
|---|---|---|
| Computation method selection | Layer 2 (HCR/EFR) | Type B (methodological) |
| Severity integration choice | Layer 2 (HCR) | Structural (double-counting risk) |
| Baseline BI availability | Layer 3 (Financial) | Type B (data availability) |
| Coverage gap (blocked hazards) | All layers | Structural (missing data) |

See [FIDUCEO uncertainty mapping](../../discussion/uncertainty/FIDUCEO-Style%20Uncertainty%20Mapping_%20LTRisk.md).

---

## 10. Open Questions

1. **Severity double-counting for published scaling:** The 2.5× from
   Diffenbaugh may already embed severity. Multiplying by our severity
   ratio (1.48) risks double-counting. Report as range until resolved.

2. **Baseline BI gap:** 7/10 hazards lack baseline BI from the hazards
   repo. The clean formula `Additional_BI = baseline_BI × HCR` works
   for 0/10 hazards today. Closing requires expanding hazards repo BI
   coverage to heat, flood, ice, wildfire.

3. **Linearity assumption:** Applying damage-level HCR to BI assumes
   BI ∝ damage. This underestimates for heat (BI grows faster than
   property damage) and overestimates for hail (property damage grows
   faster than BI). Documented as Gen.1 assumption.

4. **Severity sensitivity:** Severity ratio depends on threshold
   definition (P90 gives 1.48; P95 might give 1.71). A ±20% shift
   in severity moves heat wave HCR by ±36 percentage points. Getting
   severity right matters MORE than getting frequency scaling right.

5. **When does the YAML become code?** The schema above could be loaded
   by NB04a as a config file instead of hardcoding routing decisions.

---

## Next

- [07 — HCR: Hazard Change Ratio](07_hcr_hazard_change.md) — Detailed HCR methodology with severity
- [08 — EFR: Equipment Degradation](08_efr_equipment_degradation.md) — Channel 2 (parallel to HCR)
- [09 — NAV Impairment Chain](09_nav_impairment_chain.md) — How both channels combine

## Discussion Docs

- [HCR redefined (freq + severity)](../../discussion/hcr_financial/hcr_redefined_freq_severity.md) — Full argument + Gen.1 assumptions
- [Top-down canonical reframe](../../discussion/hcr_financial/hcr_top_down_reframe.md) — Starting from 10 canonical hazards
- [Severity sensitivity](../../discussion/hcr_financial/severity_sensitivity.md) — Dependencies and Gen.1→2→3 evolution
- [Published scaling defensibility](../../discussion/hcr_financial/pathway_defensibility.md) — Why published scaling where available
- [Pipeline complementarity](../../discussion/architecture/pipeline_complementarity.md) — How the two pipelines connect
- [BI methodology foundations](../../discussion/bi_methodology/01_what_is_bi.md) — What BI is and isn't
- [FIDUCEO uncertainty](../../discussion/uncertainty/FIDUCEO-Style%20Uncertainty%20Mapping_%20LTRisk.md) — Uncertainty propagation

Return to [Index](../00_index.md) for the full learning guide table of contents.
