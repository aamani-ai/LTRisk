# Climate Risk Orchestrator — Routing Layer

**The orchestrator is the decision layer between the SCVR Report and the
financial channels.** It maps InfraSure's canonical hazard taxonomy to
LTRisk's climate signal capabilities, determines which metric to use for
each hazard, and routes outputs to the correct financial channel.

```
SCVR Report              ORCHESTRATOR              Financial Channels
(what changed?)          (where does it go?)       (what's the $ impact?)

7 variables          →   Hazard Taxonomy       →   Channel 1 (BI/HCR)
6+ metrics each          Metric Selection          Channel 2 (EFR/IUL)
Tail Confidence          Channel Routing           Risk Flags
                         Coverage Map              Documented Gaps
```

This doc bridges two InfraSure pipelines:
- **Hazards repo** — historical risk from NOAA/NRI (1996-2024, backward-looking)
- **LTRisk** — forward climate projections from CMIP6 (2026-2055, forward-looking)

---

## 1. Purpose — The Missing Layer

### What Exists Today

```
SCVR Report says:  "tasmax shifted +6.9%, Tail Confidence HIGH"
                   "pr shifted -0.1%, Tail Confidence DIVERGENT"

But then what?

  → Which hazards does this affect?
  → Should we use the mean SCVR or the P95?
  → Does it go to Channel 1 (BI) or Channel 2 (EFR)?
  → Or is it a risk indicator that can't be forced into $ formula?
  → Does the hazards repo already have historical data for this?
```

Today, these answers are scattered across 5+ documents. The orchestrator
consolidates them into one place — the single source of truth for routing.

### What the Orchestrator Provides

```
RESPONSIBILITY 1: HAZARD TAXONOMY
  "What climate phenomena exist, and what are they called?"
  Maps InfraSure's 10 canonical hazards + additional hazards
  to specific physical mechanisms and asset vulnerabilities.

RESPONSIBILITY 2: METRIC SELECTION
  "Given this hazard and the Report Card, which SCVR metric matters?"
  Tail Confidence drives the choice: mean SCVR, P95/CVaR,
  direct daily count, or "not computable."

RESPONSIBILITY 3: CHANNEL ROUTING
  "Where does each hazard's output flow in the financial model?"
  Channel 1 (BI): operational shutdown → lost revenue
  Channel 2 (EFR): equipment degradation → life shortening
  Risk Flag: probabilistic → flagged, no deterministic $ yet
  Gap: not computable from available data

RESPONSIBILITY 4: PIPELINE COMPLEMENTARITY
  "How do the historical and forward-looking pipelines connect?"
  Hazards repo provides baseline EAL (historical frequency × severity)
  LTRisk provides climate change delta (how frequency/severity shifts)
  Together: climate-adjusted risk = baseline × (1 + HCR)
```

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

## 3. LTRisk's Climate Signal Capabilities (Bottom-Up)

### 3A. SCVR Report Card — 7 Variables

What the SCVR pipeline produces for each variable (from NB03):

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

### 3B. Computation Modes Available

```
FOR CHANNEL 1 (HCR — Business Interruption):
  Pathway A: SCVR × scaling factor (fast, parametric)
  Pathway B: Direct daily hazard counting from 28-model CMIP6 data (exact)

FOR CHANNEL 2 (EFR — Equipment Degradation):
  Mode A: Apply physics model to mean-shifted conditions (fast)
  Mode B: Integrate physics model over daily data (exact, mandatory for C-M)

BOTH use the same decision criterion:
  Tail Confidence HIGH    → Mode/Pathway A preferred
  Tail Confidence LOW/DIV → Mode/Pathway B mandatory
```

### 3C. What We CAN Compute vs What We CAN'T

```
COMPUTABLE FROM NEX-GDDP CMIP6:
  ✅ Heat waves (tasmax + tasmin compound thresholds)
  ✅ Freeze-thaw cycles (tasmin < 0 AND tasmax > 0)
  ✅ Frost days (tasmin < 0)
  ✅ Extreme precipitation / Rx5day (pr daily)
  ✅ Dry spells (consecutive days pr < 1mm)
  ✅ FWI proxy (tasmax + hurs + sfcWind + pr composite)
  ✅ Wind extremes (sfcWind, poor proxy — daily mean, not gusts)
  ✅ Icing proxy (tasmin < 0 AND hurs > 90%)
  ✅ Thermal aging acceleration (Peck's from SCVR_tas + SCVR_hurs)
  ✅ Thermal cycling fatigue (Coffin-Manson from daily counts)

NOT COMPUTABLE FROM NEX-GDDP:
  ❌ Hail (requires CAPE, wind shear, freezing level — not in dataset)
  ❌ Tornado (requires CAPE, storm-relative helicity)
  ❌ Hurricane track/intensity (requires SST, upper-air profiles)
  ❌ Coastal flooding (requires sea level rise + storm surge models)
  ❌ Lightning (requires convective parameters)
  ❌ Earthquake (not climate-related)
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

| Canonical Hazard | HCR Computable? | Computation Method | Severity | HCR Estimate (SSP585) | Baseline BI? | Additional_BI? |
|---|---|---|---|---|---|---|
| **Heat Wave** | YES | Published scaling (2.5×, Diffenbaugh 2017) | RANGE: sev=1.48 (+48%). Published scaling may embed severity. Report +20% to +34% | +20% (freq) to +34% (×sev) | NO (NRI EAL only) | NO — missing baseline BI |
| **Riverine Flood** (daily P95) | YES | Direct counting | YES: sev=1.07. Frequency counting misses severity — add it | +12.5% (combined) | NO (NRI EAL only) | PARTIAL (NRI proxy) |
| **Riverine Flood** (Rx5day) | YES | Direct counting (mm) | ALREADY CAPTURED — measures intensity not count | +2.6% | NO (NRI EAL only) | PARTIAL |
| **Strong Wind** | YES (~0) | Published scaling (1.0×) | MOOT — HCR ≈ 0 | ~0% | YES (full BI) | YES but ≈ $0 |
| **Ice Storm** | YES | Direct counting (compound) | NO — compound threshold, severity ambiguous | -44.5% (benefit) | NO (NRI EAL only) | PARTIAL |
| **Wildfire** | YES | Direct counting (FWI) | TBD — FWI is composite | TBD (risk indicator) | NO (NRI EAL only) | PARTIAL |
| **Hurricane** | YES (published) | Published consensus (Knutson 2020) | PARTIALLY — freq down, intensity up, combined +7-43% | +7% to +43% | NO (NRI EAL only) | PARTIAL |
| **Coastal Flood** | YES (SLR) | Published SLR × amplification | YES — SLR captures both | 10-1000× | NO (NRI EAL only) | PARTIAL |
| **Winter Weather** | YES | Direct counting (compound) | TBD | Decreasing | NO (NRI EAL only) | PARTIAL |
| **Hail** | **BLOCKED** | Needs CAPE, shear — not in CMIP6 | N/A | N/A | YES (full BI, Thirza curve) | NO — missing HCR |
| **Tornado** | **BLOCKED** | Needs upper-air data | N/A | N/A | YES (full BI, Feuerstein curve) | NO — missing HCR |

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
  Peck's (thermal aging):     Mode A (published Arrhenius from SCVR_tas)
  Coffin-Manson (cycling):    Mode B (direct freeze-thaw counts from daily data)
  Palmgren-Miner (wind):      Mode A (SCVR_sfcWind ≈ 0, effectively zero)

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

## 5. The Routing Rules

### Rule 1: Start From Canonical Hazards

```
For each of InfraSure's 10 canonical hazards, ask:

  1. Can LTRisk compute an HCR for this hazard?
     → YES (CMIP6 data + published scaling or direct computation)
     → NO (data not available — hail, tornado)

  2. If YES: what's the best computation method?
     → Published scaling exists? Use it. (Heat wave: 2.5× from PNAS)
     → No published scaling? Compute directly from daily data.
     → Published external data? Use it. (Hurricane: Knutson 2020)

  3. Does baseline BI exist from the hazards repo?
     → YES (hail, tornado, strong wind — full BI computation)
     → NO (heat, flood, ice, wildfire — only NRI EAL, which ≠ BI)

  4. Can we compute Additional_BI?
     → BOTH baseline_BI + HCR exist → clean: Additional_BI = baseline_BI × HCR
     → Only baseline_BI exists (no HCR) → report historical BI only
     → Only HCR exists (no baseline_BI) → need proxy or new BI methodology
```

### Rule 2: Computation Method (driven by data availability)

```
For each hazard where HCR IS computable:

  Published peer-reviewed scaling exists?
  ├── YES: Use it (traceable, defensible)
  │        Heat wave: SCVR_tasmax × 2.5 (Diffenbaugh 2017)
  │        Hurricane: Knutson 2020 consensus
  │        Coastal flood: IPCC SLR projections
  │
  └── NO: Compute directly from daily CMIP6 data
           Extreme precip: count Rx5day exceedances
           Ice storm: compound threshold counting
           Wildfire: FWI from daily data
           Winter weather: compound threshold counting
           
  This is NOT a preference hierarchy. It's a data availability question.
  Published scaling IS empirical counting done by other researchers.
  See: pathway_defensibility.md
```

### Rule 3: Financial Channel

```
  HCR hazards (event-driven BI):
    Formula: Additional_BI = baseline_BI × HCR
    Where baseline_BI comes from hazards repo (when available)
    Assumption: BI changes proportionally to damage (linearity)

  EFR (continuous degradation — separate from HCR):
    Formula: climate_degrad = EFR × std_degrad × t + IUL truncation
    Peck's, Coffin-Manson, Palmgren-Miner (unchanged)

  Risk indicators (probabilistic, no deterministic $):
    Elevated risk conditions, but P(event | condition) << 1
    Report direction + magnitude. Phase 2: frequency × severity model.
    Examples: wildfire (high FWI ≠ fire), drought/dry spell

  NOT COMPUTABLE FROM AVAILABLE DATA  → Documented Gap
    Hazard is real and potentially material, but our data can't quantify it.
    Flag in reporting. Hazards repo may have historical EAL.
    Examples: hail, tornado, hurricane, coastal flood
```

### Rule 3: Pipeline Complementarity (LTRisk + Hazards Repo)

```
INPUT: Which pipeline(s) cover this hazard?

  BOTH PIPELINES COVER IT:
    Hazards repo: historical frequency and EAL (NOAA 1996-2024)
    LTRisk: climate change delta (CMIP6 2026-2055)
    USE: climate-adjusted risk = baseline_EAL × (1 + HCR)
    ALSO: cross-validate (does LTRisk's forward projection match
           the trend in NOAA historical data?)
    Examples: heat wave, riverine flood, strong wind

  HAZARDS REPO ONLY:
    Hazard has historical data but no CMIP6-computable forward projection.
    USE: baseline_EAL from hazards repo as the risk estimate.
    FLAG: "No climate change projection available. Historical rate assumed."
    OPPORTUNITY: EAL provides baseline_BI_pct for Channel 1 formula.
    Examples: hail (baseline EAL = ~$X/yr from NOAA), tornado, hurricane

  LTRISK ONLY:
    Hazard is a continuous degradation process, not a discrete event.
    No NOAA event type corresponds to "your panels aged 11% faster."
    USE: EFR physics models (Peck's, Coffin-Manson, Palmgren-Miner)
    Examples: thermal aging, thermal cycling fatigue, wind structural fatigue

  NEITHER PIPELINE:
    Hazard exists but neither pipeline quantifies it well.
    FLAG: documented gap with priority ranking from asset risk profile.
    Examples: lightning (planned), earthquake (planned for seismic zones)
```

---

## 6. Coverage Map — What We Cover vs What We Don't

### Hayhurst Solar (24.8 MW, West Texas)

```
HAZARD               │ Priority │ LTRisk    │ Haz. Repo │ Combined  │ Notes
                     │ (fin.)   │ Coverage  │ Coverage  │           │
═════════════════════╪══════════╪═══════════╪═══════════╪═══════════╪══════════════════
Thermal aging        │ #1       │ ██████████│ ░░░░░░░░░░│ LTRisk    │ Peck's from SCVR
(Peck's)             │          │ FULL      │ N/A       │ only      │ ~$5M NAV impact
─────────────────────┼──────────┼───────────┼───────────┼───────────┼──────────────────
Hail                 │ #2       │ ░░░░░░░░░░│ ██████████│ Haz. repo │ NOAA events +
                     │          │ GAP       │ FULL      │ only      │ Thirza dmg curve
─────────────────────┼──────────┼───────────┼───────────┼───────────┼──────────────────
Heat wave            │ #3       │ ██████████│ █████░░░░░│ BOTH      │ Cross-validate:
(BI shutdown)        │          │ FULL      │ NRI EAL   │           │ LTRisk HCR vs
                     │          │           │           │           │ NOAA trend
─────────────────────┼──────────┼───────────┼───────────┼───────────┼──────────────────
Riverine flood       │ #4       │ █████░░░░░│ ██████████│ BOTH      │ LTRisk: pr Rx5day
                     │          │ PARTIAL   │ FULL      │           │ Haz repo: HAZUS
─────────────────────┼──────────┼───────────┼───────────┼───────────┼──────────────────
Wildfire             │ #5       │ ███░░░░░░░│ ██████████│ BOTH      │ LTRisk: FWI proxy
                     │          │ PROXY     │ FULL      │ (compl.)  │ Haz repo: FSF
─────────────────────┼──────────┼───────────┼───────────┼───────────┼──────────────────
Freeze-thaw          │ #6       │ ██████████│ ░░░░░░░░░░│ LTRisk    │ Coffin-Manson
(Coffin-Manson)      │          │ FULL      │ N/A       │ only      │ Mode B counts
─────────────────────┼──────────┼───────────┼───────────┼───────────┼──────────────────
Tornado              │ #7       │ ░░░░░░░░░░│ ██████████│ Haz. repo │ NOAA + Feuerstein
                     │          │ GAP       │ FULL      │ only      │ dmg curve
─────────────────────┼──────────┼───────────┼───────────┼───────────┼──────────────────
Strong wind          │ #8       │ ██░░░░░░░░│ ██████████│ BOTH      │ LTRisk: poor proxy
                     │          │ PROXY     │ FULL      │ (haz dom.)│ Haz repo: NOAA
─────────────────────┼──────────┼───────────┼───────────┼───────────┼──────────────────
Winter weather       │ #9       │ █████░░░░░│ █████░░░░░│ BOTH      │ LTRisk: frost/ice
                     │          │ PARTIAL   │ NRI EAL   │ (partial) │ proxy. Haz: NRI
─────────────────────┼──────────┼───────────┼───────────┼───────────┼──────────────────
Hurricane            │ #10      │ ░░░░░░░░░░│ ██████████│ Haz. repo │ Inland TX: low
                     │          │ GAP       │ FULL      │ only      │ but non-zero
═════════════════════╧══════════╧═══════════╧═══════════╧═══════════╧══════════════════

COVERAGE SUMMARY:
  LTRisk FULL:       3/10 hazards (thermal aging, heat wave BI, freeze-thaw)
  LTRisk PARTIAL:    2/10 (flood, winter weather)
  LTRisk PROXY:      2/10 (wildfire, strong wind)
  LTRisk GAP:        3/10 (hail, tornado, hurricane — covered by hazards repo)

  Hazards Repo FULL: 7/10 (hail, tornado, strong wind, wildfire, hurricane,
                           flood, winter weather)

  COMBINED COVERAGE: 9/10 hazards have at least one pipeline quantifying them
  REMAINING GAP:     Coastal flood (inland site — low priority)
                     Lightning (planned)
```

### Maverick Wind (491.6 MW, Central Texas)

```
HAZARD               │ Priority │ LTRisk    │ Haz. Repo │ Combined
═════════════════════╪══════════╪═══════════╪═══════════╪══════════
Icing shutdown (BI)  │ #1       │ █████░░░░░│ █████░░░░░│ BOTH
                     │          │ PROXY     │ NRI       │ (partial)
Wind fatigue (P-M)   │ #2       │ ██████████│ ░░░░░░░░░░│ LTRisk
                     │          │ FULL(≈0)  │ N/A       │ only
Hail (blade erosion) │ #3       │ ░░░░░░░░░░│ ██████████│ Haz. repo
                     │          │ GAP       │ FULL      │ only
Strong wind          │ #4       │ ██░░░░░░░░│ ██████████│ Haz. repo
                     │          │ PROXY     │ FULL      │ dominant
Tornado              │ #5       │ ░░░░░░░░░░│ ██████████│ Haz. repo
                     │          │ GAP       │ FULL      │ only
Heat (nacelle)       │ #6       │ █████░░░░░│ █████░░░░░│ BOTH
                     │          │ PARTIAL   │ NRI       │ (partial)
```

---

## 7. Worked Example — Hayhurst Solar, Full Routing

Walking through every hazard for one asset, showing the orchestrator's
decision at each step.

```
ASSET: Hayhurst Texas Solar, 24.8 MW, SSP5-8.5, Year 2040

STEP 1: Read SCVR Report Card
  tasmax: +0.080, HIGH        tas: +0.105, HIGH
  tasmin: +0.173, MODERATE    pr: -0.007, DIVERGENT
  sfcWind: -0.026, MOD/HIGH   hurs: -0.036, MODERATE
  rsds: +0.003, MODERATE

STEP 2: Route each hazard

  HEAT WAVE (BI):
    Rule 1: tasmax HIGH → Mean SCVR sufficient → Pathway A
    Rule 2: Operational shutdown → Channel 1
    Rule 3: Hazards repo has NRI EAL → cross-validate
    Result: HCR_heat = 0.080 × 2.5 = 0.200
            BI_loss = $2.17M × 1.0% × 0.200 = $4,340/yr

  HEAT WAVE (Peck's aging):
    Rule 1: tas HIGH → Mean SCVR sufficient → Mode A
    Rule 2: Cumulative stress → Channel 2
    Rule 3: LTRisk only (no historical EAL for degradation)
    Result: EFR_peck = 0.11, climate_degrad(14) = 0.0077
            Gen loss: 418 MWh/yr = $16,720/yr

  HAIL:
    Rule 1: N/A — not computable from CMIP6
    Rule 2: N/A
    Rule 3: Hazards repo has NOAA events + Thirza damage curve
    Result: DOCUMENTED GAP in LTRisk. Use hazards repo EAL.
            Hazards repo EAL_hail(Hayhurst) = $X/yr (from NOAA)

  RIVERINE FLOOD:
    Rule 1: pr DIVERGENT → Mandatory Pathway B
    Rule 2: Operational shutdown → Channel 1
    Rule 3: Both pipelines — cross-validate LTRisk Rx5day trend vs NOAA
    Result: HCR_flood = 0.020 (from Pathway B Rx5day counting)
            BI_loss = $2.17M × 0.3% × 0.020 = $130/yr

  WILDFIRE:
    Rule 1: FWI composite, LOW confidence → Risk flag
    Rule 2: Probabilistic → cannot force into BI formula
    Rule 3: Hazards repo has FSF damage curve + NOAA events
    Result: RISK FLAG — FWI trend = +11% (SSP585)
            Direction: increasing risk. No deterministic $ in Phase 1.
            Hazards repo EAL_wildfire provides baseline estimate.

  FREEZE-THAW (Coffin-Manson):
    Rule 1: tasmax/tasmin for 0°C crossing — use daily counts → Mode B
    Rule 2: Cumulative material stress → Channel 2
    Rule 3: LTRisk only
    Result: 45.71 → 31.55 cycles/yr = -31% fewer cycles
            EFR_coffin = NEGATIVE (benefit — fewer damaging cycles)

  STRONG WIND:
    Rule 1: sfcWind MOD → Pathway A acceptable, but proxy quality poor
    Rule 2: Cut-out → Channel 1 (if any events)
    Rule 3: Hazards repo has NOAA + Unanwa curve
    Result: HCR_wind ≈ 0 (0 baseline cut-out days at Hayhurst)
            Hazards repo provides wind risk estimate from NOAA events.

  TORNADO, HURRICANE, COASTAL FLOOD:
    All → DOCUMENTED GAP. Hazards repo covers with NOAA historical data.
    Inland TX: hurricane and coastal flood are low priority.
    Tornado: moderate priority — hazards repo EAL applies.

STEP 3: Aggregate

  Channel 1 (BI):     ~$4,470/yr additional (heat + flood + wind)
  Channel 2 (EFR):    EFR_combined ≈ 0.078 → ~$17K/yr + IUL shortening
  Risk Flags:         Wildfire (+11% FWI trend), Drought/dry spell
  Gaps:               Hail (#2 priority), tornado, hurricane, coastal
```

---

## 8. Draft hazard_taxonomy.yaml Schema

Machine-readable version of the routing matrix. When the YAML becomes code,
NB04 would load this to determine its routing automatically.

```yaml
# hazard_taxonomy.yaml — Climate Risk Orchestrator Configuration
# Version: 1.0 (Phase 1)
# This file defines the routing for each hazard through the LTRisk pipeline.

metadata:
  version: "1.0"
  last_updated: "2026-04"
  asset_types: ["solar_pv", "onshore_wind"]
  scenarios: ["ssp245", "ssp585"]

hazards:

  # ── CHANNEL 1: BUSINESS INTERRUPTION ──────────────────────────

  heat_wave_bi:
    canonical_name: "Heat Wave"
    category: "bi_event"
    definition: "3+ consecutive days, tasmax AND tasmin > per-DOY P90"
    noaa_event_types: ["Heat", "Excessive Heat"]
    input_variables: ["tasmax", "tasmin"]
    scvr_metric: "mean_scvr"
    tail_confidence_required: "HIGH"
    computation_mode: "pathway_a"
    scaling_factor: 2.5
    financial_channel: "channel_1_bi"
    bi_mechanism: "inverter_thermal_shutdown"
    baseline_bi_pct:
      solar_pv: { low: 0.005, mid: 0.010, high: 0.020 }
      onshore_wind: { low: 0.001, mid: 0.002, high: 0.005 }
    coverage: "full"
    confidence: "high"

  extreme_precip:
    canonical_name: "Riverine Flood"
    category: "bi_event"
    definition: "pr exceeds P95 wet-day threshold"
    noaa_event_types: ["Flood", "Flash Flood", "Heavy Rain"]
    input_variables: ["pr"]
    scvr_metric: "p95_cvar"
    tail_confidence_required: "any"  # always Pathway B for pr
    computation_mode: "pathway_b"
    financial_channel: "channel_1_bi"
    bi_mechanism: "site_flooding_downtime"
    baseline_bi_pct:
      solar_pv: { low: 0.001, mid: 0.003, high: 0.005 }
    coverage: "partial"
    confidence: "moderate"

  flood_rx5day:
    canonical_name: "Riverine Flood"
    category: "bi_event"
    definition: "Maximum rolling 5-day precipitation sum"
    noaa_event_types: ["Flood", "Flash Flood"]
    input_variables: ["pr"]
    scvr_metric: "p95_cvar"
    computation_mode: "pathway_b"
    financial_channel: "channel_1_bi"
    coverage: "partial"

  wind_cutout:
    canonical_name: "Strong Wind"
    category: "bi_event"
    definition: "sfcWind > 15 m/s daily mean (poor gust proxy)"
    noaa_event_types: ["Thunderstorm Wind", "Strong Wind", "High Wind"]
    input_variables: ["sfcWind"]
    scvr_metric: "mean_scvr"
    computation_mode: "pathway_a"
    scaling_factor: 1.0
    financial_channel: "channel_1_bi"
    coverage: "proxy"
    confidence: "low"
    notes: "Daily mean, not gusts. 0 baseline days at Hayhurst."

  icing_shutdown:
    canonical_name: "Ice Storm"
    category: "bi_event"
    definition: "tasmin < 0 AND hurs > 90% (surface proxy)"
    noaa_event_types: ["Ice Storm"]
    input_variables: ["tasmin", "hurs"]
    computation_mode: "pathway_b"
    financial_channel: "channel_1_bi"
    coverage: "proxy"

  # ── CHANNEL 2: EQUIPMENT DEGRADATION ──────────────────────────

  thermal_aging:
    canonical_name: "Heat Wave"  # same hazard, different channel
    category: "degradation"
    definition: "Continuous thermal stress from elevated mean temperature"
    input_variables: ["tas", "hurs"]
    scvr_metric: "mean_scvr"
    computation_mode: "mode_a"
    physics_model: "pecks_arrhenius"
    parameters:
      activation_energy_eV: 0.7
      humidity_exponent: 2.66
    financial_channel: "channel_2_efr"
    coverage: "full"
    confidence: "high"

  thermal_cycling:
    canonical_name: "Winter Weather"  # freeze-thaw component
    category: "degradation"
    definition: "Days where tasmin < 0°C AND tasmax > 0°C"
    input_variables: ["tasmax", "tasmin"]
    scvr_metric: "direct_daily_count"
    computation_mode: "mode_b"  # mandatory — Mode A gives wrong direction
    physics_model: "coffin_manson"
    parameters:
      fatigue_exponent: 2.0
    financial_channel: "channel_2_efr"
    coverage: "full"
    confidence: "high"
    notes: "Mode B mandatory. Mode A gives wrong sign at warming sites."

  wind_fatigue:
    canonical_name: "Strong Wind"
    category: "degradation"
    definition: "Cumulative structural fatigue from wind load cycles"
    input_variables: ["sfcWind"]
    scvr_metric: "mean_scvr"
    computation_mode: "mode_a"
    physics_model: "palmgren_miner"
    financial_channel: "channel_2_efr"
    coverage: "full"
    confidence: "low"
    notes: "SCVR_sfcWind ≈ 0 at pilot sites. EFR ≈ 0."

  # ── RISK INDICATORS ───────────────────────────────────────────

  wildfire:
    canonical_name: "Wildfire"
    category: "risk_indicator"
    definition: "FWI composite > baseline P90"
    noaa_event_types: ["Wildfire"]
    input_variables: ["tasmax", "hurs", "sfcWind", "pr"]
    scvr_metric: "composite_fwi"
    financial_channel: "risk_flag"
    coverage: "proxy"
    confidence: "low"
    notes: "Phase 2: P(fire|FWI) × E[loss|fire]. Hazards repo has FSF curve."

  dry_spell:
    canonical_name: "Drought"
    category: "risk_indicator"
    definition: "Maximum consecutive days with pr < 1mm"
    noaa_event_types: ["Drought"]
    input_variables: ["pr"]
    scvr_metric: "period_average"
    financial_channel: "risk_flag"
    coverage: "proxy"
    notes: "Soiling component → performance. Fire component → wildfire indicator."

  # ── DOCUMENTED GAPS ───────────────────────────────────────────

  hail:
    canonical_name: "Hail"
    category: "gap"
    noaa_event_types: ["Hail"]
    input_variables: []  # requires CAPE, wind shear — not in NEX-GDDP
    financial_channel: "gap"
    coverage: "gap"
    hazards_repo_coverage: "full"  # NOAA events + Thirza damage curve
    notes: "#2 priority risk for solar. Historical EAL from hazards repo."

  tornado:
    canonical_name: "Tornado"
    category: "gap"
    noaa_event_types: ["Tornado"]
    input_variables: []
    financial_channel: "gap"
    coverage: "gap"
    hazards_repo_coverage: "full"

  hurricane:
    canonical_name: "Hurricane"
    category: "gap"
    noaa_event_types: ["Hurricane", "Tropical Storm"]
    input_variables: []
    financial_channel: "gap"
    coverage: "gap"
    hazards_repo_coverage: "full"

  coastal_flood:
    canonical_name: "Coastal Flood"
    category: "gap"
    noaa_event_types: ["Coastal Flood", "Storm Surge/Tide"]
    input_variables: []
    financial_channel: "gap"
    coverage: "gap"
    hazards_repo_coverage: "full"
    notes: "Inland TX sites: low priority."
```

---

## 9. Connection to FIDUCEO Uncertainty Mapping

The orchestrator's routing decisions map directly to the FIDUCEO uncertainty
layers documented in [FIDUCEO-Style Uncertainty Mapping](../../discussion/uncertainty/FIDUCEO-Style%20Uncertainty%20Mapping_%20LTRisk.md):

```
Orchestrator Decision          FIDUCEO Layer           Uncertainty Type
─────────────────────          ─────────────           ────────────────
Metric selection               Layer 1 (SCVR)          u(x₁): model spread
  (mean vs P95 vs daily)       Which metric is input?   Type A (statistical)

Channel assignment             Layer 2A (HCR) or        u(x₂): threshold def
  (BI vs EFR vs flag)          Layer 2B (EFR)           u(x₃): scaling/physics
                                                        Type B (systematic)

Coverage assessment            All layers               Structural uncertainty
  (FULL vs GAP)                Missing data             Not quantifiable
```

The FIDUCEO doc traces uncertainty through each layer. The orchestrator tells
you WHICH layer each hazard enters — and therefore which uncertainty budget
applies.

---

## 10. Open Questions

1. **Compound hazard confidence:** Heat wave requires tasmax (HIGH) AND
   tasmin (MODERATE). What confidence does the compound get? Current approach:
   use the LOWER confidence (conservative). Alternative: weighted by
   contribution.

2. **Site-specificity:** The routing matrix uses Hayhurst values. Should it
   change per site? Probably yes for coverage assessment (coastal sites have
   different priorities) but routing RULES should be universal.

3. **When does the YAML become code?** The schema above could be loaded by
   NB04 as a config file instead of hardcoding routing decisions. This would
   make NB04 configuration-driven rather than code-driven.

4. **Cross-validation protocol:** For hazards both pipelines cover (heat wave,
   flood), what's the formal cross-validation process? Compare LTRisk's
   forward HCR trend against NOAA's historical trend? What's "agreement"?

5. **Hazards repo EAL as baseline_BI_pct:** The hazards repo computes
   site-specific EAL from NOAA events. Can this directly provide the
   baseline_BI_pct that Channel 1 needs? E.g., EAL_heat(Hayhurst) / Revenue
   = baseline_BI_pct_heat. This would solve the biggest unknown in Channel 1.

---

## Next

- [07 - HCR: Hazard Change Ratio](07_hcr_hazard_change.md) — Detailed computation for Channel 1 BI hazards
- [08 - EFR: Equipment Degradation](08_efr_equipment_degradation.md) — Detailed computation for Channel 2 degradation models
- [09 - NAV Impairment Chain](09_nav_impairment_chain.md) — How both channels combine in the financial model

## Discussion Docs

- [HCR/EFR boundary](../../discussion/hcr_financial/hcr_efr_boundary.md) — Why hazards are classified into 3 categories
- [EFR two modes](../../discussion/efr_degradation/efr_two_modes.md) — Why EFR has Mode A/B (same Jensen's issue as HCR)
- [Top-down meets bottom-up](../../discussion/architecture/top_down_meets_bottom_up.md) — Why both approaches are needed
- [Channel 1 BI calculation](../../discussion/hcr_financial/channel_1_bi_calculation.md) — Three approaches to convert HCR to dollars
- [Channel 2 EFR financial](../../discussion/efr_degradation/channel_2_efr_financial.md) — How EFR becomes generation loss + IUL
- [FIDUCEO uncertainty mapping](../../discussion/uncertainty/FIDUCEO-Style%20Uncertainty%20Mapping_%20LTRisk.md) — Uncertainty propagation through each layer

Return to [Index](../00_index.md) for the full learning guide table of contents.
