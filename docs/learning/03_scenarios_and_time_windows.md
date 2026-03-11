# Scenarios and Time Windows

> Two design decisions underpin every SCVR computation: which future emissions pathway to use, and which time windows to compare. This guide covers both.

---

# Part 1 — SSP Scenarios: The Five Future Pathways

---

## 1. Why No Scenarios Before 2014?

Before 2014, there is only **one history** — what actually happened:

```
                         THE BRANCHING POINT
                               2014
                                |
  1850 ─────────────────────────┤
         HISTORICAL             |────── SSP1-1.9  (net zero)
         (one experiment)       |────── SSP1-2.6  (strong mitigation)
                                |────── SSP2-4.5  (middle road)     <-- we use
         Real CO2, real         |────── SSP3-7.0  (regional rivalry)
         volcanoes, real        |────── SSP5-8.5  (fossil-fueled)   <-- we use
         solar activity         |
                                |
         Everyone runs the      After 2014, nobody knows
         SAME experiment.       what humanity will do.
         No choices to make.    Each pathway = different assumption.
```

**Analogy**: Think of it like a highway. Before 2014, everyone drove on the same road (the past is fixed). At 2014, the road forks into 5 exits. Each exit represents a different set of choices humanity might make about energy, policy, and development.

The models literally switch input files at 2014:
- Up to 2014: use observed greenhouse gas concentrations
- After 2014: use assumed concentration pathways (the SSPs)

---

## 2. What Does "SSP" Stand For?

**SSP** = Shared Socioeconomic Pathway

Each SSP tells a story about how *society develops* over the 21st century. The number after the dash is the **radiative forcing** in watts per square meter (W/m2) by 2100:

```
RADIATIVE FORCING = extra energy trapped by greenhouse gases

  Pre-industrial baseline = 0 W/m2

  SSP1-1.9:  +1.9 W/m2 by 2100  (like adding a Christmas light per m2)
  SSP1-2.6:  +2.6 W/m2 by 2100
  SSP2-4.5:  +4.5 W/m2 by 2100  (like adding a night-light per m2)
  SSP3-7.0:  +7.0 W/m2 by 2100
  SSP5-8.5:  +8.5 W/m2 by 2100  (like adding an LED bulb per m2)

  (These are averaged over the entire Earth's surface — 510 trillion m2)
```

---

## 3. The Five Pathways in Detail

### SSP1-1.9 — "Taking the Green Road" (Net Zero)

```
CO2 Emissions
     |
  40 |  \
     |   \
  20 |    \
     |     \
   0 |──────\────────────────── net zero by ~2050
     |       \
 -10 |        ─────────────── negative emissions (carbon capture)
     └──────────────────────────
     2020    2040    2060    2080    2100

  Warming: ~1.5C above pre-industrial
  Story:   Rapid green transition, international cooperation,
           sustainable lifestyles, plant-based diets, massive
           renewable deployment, carbon capture at scale.
  Reality: Requires unprecedented global cooperation.
```

### SSP1-2.6 — "Sustainability" (Strong Mitigation)

```
  Warming: ~1.8C
  Story:   Similar to 1.9 but slightly less aggressive.
           Strong mitigation policies but allows some continued
           fossil fuel use. Paris Agreement goals roughly met.
```

### SSP2-4.5 — "Middle of the Road" (We Use This)

```
CO2 Emissions
     |
  40 |───────\
     |        \
  30 |         \
     |          \
  20 |           ───────────────────────────
     |                                       \
  10 |                                        ──────
     └──────────────────────────────────────────────
     2020    2040    2060    2080    2100

  Warming: ~2.7C above pre-industrial by 2100
           ~1.5-2.0C by 2050 (our asset window)
  Story:   Social, economic, and technological trends don't shift
           markedly from historical patterns. Some climate policy
           but incomplete. Uneven development. Slow progress on
           sustainability goals. Population peaks mid-century.
  Why we use it: Most likely "central" pathway. If you had to
           pick one scenario, this is the consensus moderate case.
```

### SSP3-7.0 — "Regional Rivalry"

```
  Warming: ~3.6C
  Story:   Resurgent nationalism, slow economic growth, fragmented
           world, weak global institutions, high inequality. Limited
           climate action. Material-intensive, energy-intensive economy.
```

### SSP5-8.5 — "Fossil-Fueled Development" (We Use This)

```
CO2 Emissions
     |
  80 |            /─────\
     |           /       \
  60 |          /         \
     |         /           \
  40 |────────/             \
     |                       \
  20 |                        ────────────
     └──────────────────────────────────────
     2020    2040    2060    2080    2100

  Warming: ~4.4C above pre-industrial by 2100
           ~2.0-2.5C by 2050 (our asset window)
  Story:   Rapid economic growth powered by fossil fuels. High
           energy demand. Exploitation of fossil resources.
           Technology advances but NOT in renewables. Faith in
           markets and innovation to solve problems eventually.
  Why we use it: Worst-case upper bound. For risk assessment,
           you MUST include the high-end scenario — investors
           want to know "what if things go badly?"
```

---

## 4. Visual Comparison — All Scenarios

```
GLOBAL MEAN TEMPERATURE CHANGE (relative to 1850-1900)

Temp   5C |                                          ╱ SSP5-8.5
change    |                                        ╱╱
       4C |                                      ╱╱
          |                                   ╱╱╱
       3C |                               ╱╱╱╱       ╱ SSP3-7.0
          |                           ╱╱╱╱         ╱╱
       2C |                      ╱╱╱╱╱          ╱╱╱
          |                ╱╱╱╱╱╱           ╱╱╱╱───── SSP2-4.5
       1C |═══════════╱╱╱╱╱════════════╱╱╱╱══════════════════
          |      ╱╱╱╱╱            ╱╱╱╱╱  ─────────── SSP1-2.6
       0C |─────                ────────────────────── SSP1-1.9
          └──────────────────────────────────────────────────
          1900  1950  2000  2014  2030  2050  2070  2100
                              ^
                              |
                    Scenarios branch here
                    (all identical before)
```

```
CO2 CONCENTRATION (ppm)

 1200 |                                    ╱ SSP5-8.5
      |                                  ╱╱
 1000 |                               ╱╱╱
      |                            ╱╱╱
  800 |                         ╱╱╱
      |                      ╱╱╱           ╱ SSP3-7.0
  600 |                   ╱╱╱          ╱╱╱╱
      |               ╱╱╱╱        ╱╱╱╱───── SSP2-4.5
  400 |═══════════╱╱╱╱═══════╱╱╱╱══════════════════════
      |       ╱╱╱╱       ╱╱╱╱  ──────────── SSP1-2.6
  280 |──────           ──────────────────── SSP1-1.9
      └──────────────────────────────────────────────
      1850  1900  1950  2000  2025  2050  2075  2100
              Pre-industrial
              level: ~280 ppm
```

---

## 5. Why We Use SSP2-4.5 AND SSP5-8.5

For financial risk assessment, you need **at least two scenarios**:

```
SCENARIO PAIR RATIONALE

  SSP2-4.5 ("likely")                SSP5-8.5 ("stress test")
  ────────────────────               ────────────────────────
  Most probable pathway              Worst-case upper bound

  "What will probably happen"        "What if things go badly"

  Used for: central estimates,       Used for: tail risk, stress
  expected losses, base case         testing, insurance pricing,
  financial planning                 regulatory scenarios

  Analogous to:                      Analogous to:
  "Expected" credit loss             "Stressed" credit loss
  VaR at 50th percentile             VaR at 99th percentile
```

**Why not SSP1-2.6?** Even under optimistic emissions cuts, warming through 2055 is already "baked in" — the climate system has inertia. For our 30-year asset window, the difference between SSP1-2.6 and SSP2-4.5 is small. The big divergence happens after 2060.

**Why not SSP3-7.0?** It's between our two chosen scenarios. Using 2-4.5 and 5-8.5 gives the widest bracket:

```
OUR ASSET WINDOW (2026-2055)

Warming by 2050 (approximate, above pre-industrial):

  SSP1-2.6:  ~1.6C  ─── too similar to SSP2-4.5 for this period
  SSP2-4.5:  ~1.8C  ─── OUR LOWER BOUND
  SSP3-7.0:  ~2.0C  ─── in between (redundant)
  SSP5-8.5:  ~2.3C  ─── OUR UPPER BOUND

  The delta between our two scenarios for 2026-2055: ~0.5C
  That 0.5C drives measurably different SCVR values.
```

---

## 6. The "SSP" Part vs the "RCP" Part

SSP scenarios actually combine two things:

```
SSP (Socioeconomic) + RCP (Radiative Forcing) = Full Scenario

  SSP2-4.5 =  SSP2 (middle-of-road society)
            + RCP4.5 (4.5 W/m2 forcing)

  SSP5-8.5 =  SSP5 (fossil-fueled development)
            + RCP8.5 (8.5 W/m2 forcing)
```

**SSP** (the narrative) tells you: What does society look like? How vulnerable are people? What's the economy doing?

**RCP** (the physics) tells you: How much extra energy is trapped? What's the CO2 concentration?

For our purposes, we only care about the **physical climate outputs** (temperature, rain, wind), so the RCP part is what drives our data. But the SSP narrative matters for financial context — SSP5-8.5 implies a world where fossil fuels dominate, which is relevant for valuing renewable energy assets.

---

## 7. Common Misconceptions

| Misconception | Reality |
|---|---|
| "SSP5-8.5 is impossible" | Current policies track between SSP2-4.5 and SSP3-7.0. SSP5-8.5 is unlikely for 2100 but useful as a stress test. |
| "SSP1-1.9 means no climate change" | Even net zero by 2050 means ~1.5C of warming. Climate damage is already locked in for our asset's lifetime. |
| "Scenarios are predictions" | They are **projections** — "if emissions follow path X, then climate does Y." No probability is assigned. |
| "Higher SSP = more likely" | The numbers are radiative forcing, NOT probability. SSP2-4.5 is arguably more likely than SSP5-8.5. |
| "Scenarios diverge immediately after 2014" | For the 2020s-2030s, all scenarios are very similar. Major divergence happens after ~2050. |

---

## 8. What This Means for Our SCVR Results

When you see the SCVR table in Notebook 03:

```
Variable    SSP2-4.5    SSP5-8.5    Delta
────────    ────────    ────────    ─────
tasmax       +0.05       +0.08      0.03
pr           +0.02       +0.04      0.02
sfcWind      -0.01       -0.01      0.00
```

**Reading this**:
- Both scenarios show warming (positive SCVR for temperature)
- SSP5-8.5 always shows more change than SSP2-4.5 (as expected)
- The **delta** between scenarios tells you how much the emission pathway matters for each variable
- If delta is near zero (like sfcWind), the variable is insensitive to emissions — natural variability dominates
- If delta is large, the variable is highly sensitive to emissions — the "choice of future" matters

---

# Part 2 — Time Windows: Baseline, Future, and the Gap

---

## 9. Our Two Time Windows

```
TIMELINE

  1985                    2014    2025  2026                    2055
  ├─────── BASELINE ───────┤     GAP   ├─────── FUTURE ─────────┤
  │  30 years              │   11 yrs  │  30 years              │
  │  historical experiment │           │  SSP experiment        │
  │  "What was normal?"    │           │  "What will the asset  │
  │                        │           │   experience?"         │
  └────────────────────────┘           └────────────────────────┘
```

| Window | Period | Years | Source Experiment | Purpose |
|---|---|---|---|---|
| Baseline | 1985-2014 | 30 | `historical` | Define "normal" climate |
| Future | 2026-2055 | 30 | `ssp245` or `ssp585` | Asset's operational exposure |

---

## 10. Why 1985-2014 for Baseline?

Three reasons:

### Reason 1: CMIP6 Historical Experiment Ends at 2014

```
CMIP6 experiment design:

  historical experiment:  1850 ──────────────────── 2014  (ENDS HERE)
  SSP experiments:                                  2015 ──────── 2100

  The historical experiment LITERALLY has no data after 2014.
  It's not a choice — it's a constraint.
```

### Reason 2: IPCC Standard Reference Period

The IPCC Sixth Assessment Report (AR6) uses 1995-2014 or 1985-2014 as the modern reference period. By using this same window, our results are **directly comparable** with published climate science.

### Reason 3: 30 Years = Statistical Robustness

```
WHY 30 YEARS AND NOT 20 OR 10?

  Climate has natural variability:
  - El Nino/La Nina cycles: 2-7 years
  - Pacific Decadal Oscillation: 20-30 years
  - Atlantic Multidecadal Oscillation: 60-80 years
  - Volcanic eruptions: random (Pinatubo 1991, etc.)

  Window too short (10 years):
    Might land on an El Nino cluster -> baseline looks too warm
    Or a volcanic eruption -> baseline looks too cool
    Not enough data for robust tail estimation

  30 years smooths these out:
    Contains ~5 El Nino cycles
    Contains ~1 full PDO cycle
    ~10,950 daily values per model -> robust exceedance curves
```

### Why Not Start Earlier (1950)?

```
1950─────────1985─────────2014
 ^             ^
 |             |
 Climate was   This is the "modern baseline."
 different     Close enough to present to be
 then — less   relevant, but before the
 CO2, less     acceleration of warming that
 warming.      happened after 2014.

 Using 1950-2014 would MIX:
  - A cooler early period (less CO2)
  - A warmer late period (more CO2)
  = An artificially "medium" baseline
    that doesn't represent either period well.
```

---

## 11. Why 2026-2055 for Future?

This is driven by the **asset's actual operational lifetime**:

```
ASSET CONFIGURATION (from sites.json + Notebook 03)

  construction_start_year = 2026
  operational_lifespan    = 30 years
  -> future window: 2026 to 2055

  The solar farm at Hayhurst:
    Built: 2026
    Operates: 2026-2055
    Decommissioned: ~2056

  We only care about climate the asset ACTUALLY FACES.
  Climate in 2060? Irrelevant — the asset is gone.
  Climate in 2020? Irrelevant — the asset doesn't exist yet.
```

### Notebook 01 vs Notebook 03 Approach

```
NOTEBOOK 01 (old approach):
  Fixed target years: 2030, 2035, 2040, 2045, 2050
  Each with a 20-year rolling window:
    2030 -> window 2020-2040
    2035 -> window 2025-2045
    2050 -> window 2040-2060

  Problem: Multiple overlapping SCVRs, confusing to interpret.
           Which one represents "the asset's risk"?

NOTEBOOK 03 (new approach):
  ONE window: 2026-2055 (the entire asset lifetime)
  ONE SCVR per variable per scenario.

  Advantage: Clear, definitive answer.
  For schema compatibility: center_year = (2026+2055)//2 = 2040
```

---

## 12. The Gap (2015-2025): Why It's Correct

### The Gap Is NOT Missing Data

```
    Baseline                    Future
    1985──────2014    2015──2025    2026──────2055
                        ^^^^^^^^
                        This data EXISTS on THREDDS.
                        We CHOOSE not to use it.
                        Here's why:
```

### Reason 1: It Doesn't Belong in the Baseline

```
TEMPERATURE TREND

Temp anomaly
(vs 1850-1900)

  +1.5C |                              * * *
        |                          * *
  +1.0C |                    * * *
        |              * * *
  +0.5C |        * * *                    <- 2015-2025 is HERE
        |  * * *                              already +1.0 to +1.3C
  0.0C  |*                                    above pre-industrial
        └──────────────────────────────
        1900  1950  1985  2014  2025

  Adding 2015-2025 to baseline:
    Old baseline mean: +0.6C (average of 1985-2014)
    New baseline mean: +0.7C (average of 1985-2025)

    = baseline gets warmer
    = future looks LESS different
    = SCVR is ARTIFICIALLY LOWER
    = YOU UNDERESTIMATE THE RISK
```

### Reason 2: It Doesn't Belong in the Future

```
  The asset starts in 2026. Including 2015-2025 in the future:

  - Adds 11 years of cooler-than-2040s data
  - Dilutes the hotter end of the distribution
  - Makes future look milder than what the asset will face
  - Again: UNDERESTIMATES RISK

  Also: those years are NOT part of the asset's operational life.
  No revenue, no depreciation, no risk during 2015-2025.
```

### Reason 3: It's the Transition Zone

```
EXPERIMENT BOUNDARY

  historical experiment  SSP experiment
  ────────────────────>  ──────────────>
                     2014|2015

  At this boundary:
  - CO2 concentrations are identical (both ~400 ppm)
  - But the experiment "source" changes
  - Some models have a tiny discontinuity at the join
  - Including data from both sides of the join in
    ONE bag would mix experiment artifacts with climate signal
```

### The Analogy

Think of it like comparing two blood tests:
- **Test 1**: Your blood panel from 2020 (baseline health)
- **Test 2**: Your blood panel from 2030 (after a decade of changed diet)

You wouldn't mix in blood work from 2023-2029 into either test. Those intermediate results don't represent your original state OR your final state — they're the transition.

---

## 13. What If the Asset Started Before 2015?

Our `construction_start_year = 2026` so this doesn't apply, but the code handles it:

```python
if future_start <= 2014:
    # Stitch historical + SSP
    hist_part = fetch_model_years(model, "historical", var,
        range(future_start, min(2015, future_end+1)), ...)
    ssp_part = fetch_model_years(model, scen, var,
        range(2015, future_end+1), ...)
    fut_series = pd.concat([hist_part, ssp_part]).sort_index()
else:
    # All future years come from SSP
    fut_series = fetch_model_years(model, scen, var,
        range(future_start, future_end+1), ...)
```

Example: If an asset started in 2010 with 40-year lifespan (2010-2049):
```
  2010──2014: from "historical" experiment
  2015──2049: from "ssp245" or "ssp585"
  Stitched together into one continuous series
```

---

## 14. Ensemble Pooling Explained

### What Pooling Means

Instead of keeping models separate, we throw all their daily values into one bag:

```
WITHOUT POOLING (per-model):

  Model A baseline:  [32.1, 35.4, 28.9, ...]   10,950 values
  Model B baseline:  [31.8, 34.9, 29.2, ...]   10,950 values
  Model C baseline:  [33.0, 36.1, 28.5, ...]   10,950 values

  -> 3 separate SCVR values
  -> Which one do you report?

WITH POOLING (ensemble):

  Pooled baseline:   [32.1, 35.4, 28.9, ...,   <- Model A
                      31.8, 34.9, 29.2, ...,   <- Model B
                      33.0, 36.1, 28.5, ...]   <- Model C
                     = 32,850 values in ONE bag

  -> 1 SCVR value that represents the ensemble
```

### Why Pooling Works

```
THE LAW OF LARGE NUMBERS IN ACTION

  Model A alone: might be biased warm (+1C)
  Model B alone: might be biased cool (-0.5C)
  Model C alone: might be unbiased

  Per-model SCVR:
    A: 0.095  (inflated by warm bias)
    B: 0.052  (deflated by cool bias)
    C: 0.073  (probably closest to truth)
    Average: 0.073

  Pooled SCVR:
    0.074  (biases cancel in the combined distribution)

  Pooling naturally averages out individual model biases
  because the exceedance curve is computed on ALL values at once.
```

### Why We Also Compute Per-Model SCVR

```
PURPOSE: UNCERTAINTY QUANTIFICATION

  If all models agree:        If models disagree:

  A: 0.071   ──┐              A: 0.032   ──┐
  B: 0.068     ├── tight       B: 0.145     ├── wide spread
  C: 0.073     │   spread      C: 0.025     │   = LOW confidence
  D: 0.079     │   = HIGH      D: 0.180     │
  E: 0.075     │   confidence  E: 0.065     │
  F: 0.074   ──┘              F: 0.120   ──┘

  Pooled: 0.074               Pooled: 0.088

  The pooled value is "right"  The pooled value is "right"
  AND we're confident.        BUT we're NOT confident.

  -> The Strip Plot (Plot D in NB03) shows this visually.
```

---

## 15. Comparison with Alternative Time Window Approaches

### Approach A: Rolling Windows (what Notebook 01 did)

```
  Target year 2030: window 2020-2040, SCVR_2030 = 0.05
  Target year 2035: window 2025-2045, SCVR_2035 = 0.06
  Target year 2040: window 2030-2050, SCVR_2040 = 0.07
  Target year 2050: window 2040-2060, SCVR_2050 = 0.09

  Pro: Shows how risk evolves over time
  Con: Windows overlap heavily (2030-2040 appears in ALL of them)
  Con: Which SCVR represents "the asset's risk"? Ambiguous.
  Con: More complex output, harder to communicate to stakeholders.
```

### Approach B: Full Lifetime Window (what Notebook 03 does)

```
  Window 2026-2055, SCVR = 0.073

  Pro: One definitive number per variable/scenario
  Pro: Directly answers "what will THIS ASSET experience?"
  Pro: Simple to communicate: "7.3% more extreme climate"
  Con: Loses temporal evolution (you don't know if it's front-loaded)
```

### Approach C: Decade Buckets

```
  2026-2035: SCVR_early  = 0.04
  2036-2045: SCVR_mid    = 0.07
  2046-2055: SCVR_late   = 0.10

  Pro: Shows acceleration
  Con: Only 10 years per bucket (fewer data points, noisier)
  Con: Bucket boundaries are arbitrary
```

We chose Approach B because the primary consumer (HCR/EFR computation in Notebook 04) needs a single SCVR per variable per scenario. Temporal evolution can be explored in visualizations (Plot C spaghetti) without changing the core output.

---

## Next

- [04 - SCVR Methodology](04_scvr_methodology.md) — How we turn climate data into a single risk number
