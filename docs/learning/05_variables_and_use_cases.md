# Variables and Asset Use Cases

> What does each SCVR number actually mean? This guide covers the physical meaning, failure pathways, and real SCVR values for each variable — then walks through two complete asset examples.

---

# Part 1 — Per-Variable Guide

---

## The 7 Variables at a Glance

```
┌──────────┬──────────┬──────────────────────────┬───────────────┬────────────┐
│ Variable │ Unit     │ Physical meaning          │ scvr_direction│ Asset      │
├──────────┼──────────┼──────────────────────────┼───────────────┼────────────┤
│ tasmax   │ °C       │ Hottest moment of the day │ higher_worse  │ Both       │
│ tasmin   │ °C       │ Coolest moment of the day │ lower_freeze  │ Both       │
│ tas      │ °C       │ Average daily temperature │ higher_worse  │ Both       │
│ pr       │ mm/day   │ Total daily rainfall      │ extremes_both │ Both       │
│ sfcWind  │ m/s      │ Mean daily wind speed     │ high_ext_worse│ Wind       │
│ hurs     │ %        │ Mean daily humidity       │ context_dep.  │ Both       │
│ rsds     │ MJ/m²/d  │ Solar irradiance (GHI)   │ NOT IN SCVR   │ Solar perf │
└──────────┴──────────┴──────────────────────────┴───────────────┴────────────┘
```

> **rsds is the exception** — it is NOT computed as a SCVR hazard variable. It feeds Pathway B (solar performance modeling) as an absolute value, not a distribution comparison. See section 7.

---

## 1. tasmax — Daily Maximum Temperature

**What it is:** The single hottest reading recorded at a site in a given day. Peaks around 2-4 PM in summer.

**Why it matters for assets:**
- Solar panels: efficiency drops ~0.4%/°C above 25°C STC (Standard Test Conditions)
- Wind: minor material effects; relevant for electronics cooling
- Both: contributes to heat wave event counts

**SCVR direction: `higher_is_worse`**
- Positive SCVR = more area under the high-temperature curve = more hot days and/or hotter extremes = **more stress**
- Negative SCVR = cooling (not expected in West Texas under any scenario)

**Real values (Hayhurst Solar, nb01):**
```
2030: +4.2%  |  2040: +7.4%  |  2050: +9.2%
```
Monotonically increasing — every future decade is hotter than the last. The signal is clean and reliable.

**What SCVR of +0.074 (2040) means physically:**
The exceedance area under the tasmax curve is 7.4% larger. In West Texas terms: the 98th percentile temperature (the very hottest 2% of days) shifts from ~43°C to ~45°C. That extra 2°C at the extremes is where accelerated panel aging occurs.

---

## 2. tasmin — Daily Minimum Temperature

**What it is:** The coolest reading of the day — typically 4-6 AM before sunrise. In desert climates, nights cool dramatically.

**Why it matters for assets:**
- Nights warming faster than days is a well-documented phenomenon under high-emission scenarios
- Solar: thermal cycling fatigue. Large tasmax-tasmin swings create expansion/contraction stress on solder joints. If nights warm, the swing may increase OR decrease depending on whether days warm faster
- Both: icing risk (tasmin < 0°C = potential freeze event)

**SCVR direction: `lower_is_worse_for_freeze`**

Two distinct regimes:
```
tasmin positive SCVR (warming nights):
  → Fewer frost events (fewer freeze-thaw cycles) ← GOOD for materials
  → More heat stress overnight ← BAD for Peck's aging model
  → Net effect depends on which dominates

tasmin negative SCVR (cooling nights, not expected):
  → More frost events → more icing, freeze damage
```

**Real values (Hayhurst Solar, nb01):**
```
2030: +9.2%  |  2040: +14.8%  |  2050: +17.9%
```
**tasmin has the strongest SCVR signal of all variables** — +17.9% by 2050. Nights are warming faster than days (tasmax only +9.2% by 2050). This is the primary driver of Peck's accelerated aging.

---

## 3. tas — Daily Mean Temperature

**What it is:** The average of all hourly readings in a day (approximately `(tasmax + tasmin) / 2` in practice).

**Why it matters:**
- Primary input to Peck's aging model (uses mean ambient temperature, not max)
- Fire Weather Index (FWI) computation
- General trend indicator — least "peaky" of the three temperature variables

**SCVR direction: `higher_is_worse`**
- Consistently positive, sits between tasmin and tasmax signals
- Most physically stable signal (fewer extreme-year outliers)

**Real values (Hayhurst Solar, nb01):**
```
2030: +5.9%  |  2040: +10.1%  |  2050: +12.5%
```

---

## 4. pr — Daily Precipitation

**What it is:** Total rainfall accumulated in a day (in mm). Zero on dry days; can spike to 50-100mm on storm days.

**Why it matters:**
- Both extremes matter (unlike temperature where only one end is bad):
  - **High extremes** → flood HCR, waterlogging, panel damage from hail/debris
  - **Zero-day runs** → drought → dust accumulation on solar panels (soiling) → wildfire risk

**SCVR direction: `extremes_both_directions`** — the most complex variable

```
The precipitation puzzle:
  Positive SCVR → overall area under curve grew
    Could mean: more heavy rain days
    Could mean: both more heavy AND more dry days (distribution stretches both ways)

  Negative SCVR → overall area under curve shrank
    Likely means: fewer mid-range rain days, overall drying

  The SCVR alone doesn't tell you which tail moved.
  For flood risk: look at P90/P95 of pr (upper tail)
  For drought risk: count days where pr < 1mm (lower tail)
```

**Real values (Hayhurst Solar, nb01) — the most interesting pattern:**
```
2030: +11.9%  |  2035: +5.6%  |  2040: +1.1%  |  2045: -8.9%  |  2050: -17.8%
```
This **inversion** is the classic West Texas pattern: near-term, the area grows as some storm events intensify; long-term, overall drying dominates and the area shrinks. The sign flip happens around 2040.

> Treat 2045 and 2050 values with wider uncertainty — shorter future windows in nb01.

---

## 5. sfcWind — Daily Mean Wind Speed

**What it is:** Average wind speed over the entire day at 10m above ground. Not instantaneous gusts.

**Why it matters:**
- Wind turbines: structural fatigue via Palmgren-Miner model. Wind distribution shape drives cumulative damage
- Turbine cut-out: if sfcWind > 25 m/s, turbine shuts down to prevent structural damage
- Hub height note: sfcWind is at 10m; turbines operate at ~80m hub height. The SCVR relative comparison is still valid (the fractional change applies), but absolute values need extrapolation

**SCVR direction: `higher_extremes_are_worse`**
- High extreme SCVR positive = more days with dangerous wind speeds = more cut-outs and fatigue
- Near-zero SCVR = wind distribution essentially unchanged = Palmgren-Miner runs at baseline rate

**Real values (Hayhurst Solar, nb01):**
```
2030: +0.2%  |  2040: ~0%  |  2050: +0.4%
```
Essentially flat — no climate change signal in wind speed at West Texas sites. This is expected and physically consistent with climate model consensus for this region.

**Implication for Maverick Creek Wind:** If sfcWind SCVR ≈ 0, then Palmgren-Miner structural fatigue contribution to EFR is negligible. The asset's climate risk is dominated by temperature and icing variables instead.

---

## 6. hurs — Daily Mean Relative Humidity

**What it is:** How saturated the air is with water vapor, as a percentage (0–100%). At 100%, air cannot hold more water and condensation begins.

**Why it matters:**
- Peck's aging model: acceleration factor = f(temperature) × f(humidity). High heat AND high humidity accelerates degradation exponentially
- Icing detection: requires both tasmin < 0°C AND hurs > 75%
- Fire Weather Index: low humidity + high temperature = fire risk

**SCVR direction: `context_dependent`** — the most nuanced variable

```
Two opposing effects:

  hurs positive SCVR (more humid future):
    Increases Peck's aging rate → BAD
    Increases icing risk if temperatures also cold → BAD
    Reduces fire risk → GOOD

  hurs negative SCVR (drier future):
    Reduces Peck's aging rate → slightly GOOD for panels
    Reduces icing risk → GOOD
    Increases dust/soiling (dry air → more particles) → BAD
    Increases wildfire FWI → BAD
```

**Real values (Hayhurst Solar, nb01):**
```
2030: ~0%  |  2040: -3.2%  |  2050: -7.9%
```
West Texas is drying out. This **partially offsets** the Peck's effect from warming temperatures. The net Peck's acceleration is temperature increase minus humidity relief.

---

## 7. rsds — Solar Irradiance (WHY IT'S DIFFERENT)

**What it is:** Surface Downwelling Shortwave Radiation = Global Horizontal Irradiance (GHI). The total solar energy reaching the ground per unit area per day.

**Why it's in the variable list:** It's essential for solar asset performance — energy yield = rsds × panel area × efficiency.

**Why it does NOT participate in SCVR the same way:**

```
SCVR logic (P1 variables):           rsds logic (P2 performance):
  "How much did the EXTREMES           "How much did the MEAN irradiance
   of the distribution shift?"          change year over year?"

  Answers: did heat waves get           Answers: will my panels generate
  worse? did flooding increase?         more or less electricity in 2040?

  → Feeds HCR hazard scaling           → Feeds pvlib solar generation
  → Drives EFR / aging models           model directly
  → Ends at IUL / NAV impairment       → Drives revenue / cash flow
```

The `scvr_direction` for rsds is `not_primary_scvr_variable` — it's deliberately excluded from the hazard chain.

**Real rsds SCVR (Hayhurst, nb01):**
```
2030: +0.9%  |  2040: +1.1%  |  2050: +1.7%
```
The SCVR value is tiny and low — because the *shape* of the irradiance distribution barely changes. But what matters for revenue is the **absolute level**: if mean rsds increases by 1%, that's ~543 MWh/year additional generation at Hayhurst (a small but real NAV upside).

> rsds is a **revenue offset** to the thermal losses, not a hazard input. Notebook 04 will handle it separately as a performance pathway.

---

## Variable Summary: Which Matters Most by Asset

```
SOLAR FARM (Hayhurst)          WIND FARM (Maverick)
──────────────────────         ──────────────────────
1. tasmin  ████████  +17.9%    1. sfcWind ░░░░░░░░  ~0%
2. tas     ██████    +12.5%    2. tasmin  (icing — see below)
3. tasmax  █████     +9.2%     3. tasmax  (minor)
4. pr      ███ (inv) ±17.8%    4. pr      (flood)
5. hurs    ██ (-7.9% offset)   5. hurs    (icing)
6. sfcWind ░         ~0%
7. rsds    ░ (perf)  +1.7%
```

**Key takeaway:** Solar is far more climate-sensitive than wind for West Texas sites. The dominant driver for solar is tasmin (nighttime warming → Peck's aging). The dominant driver for wind is near-zero (sfcWind flat), with tasmin warming actually reducing icing events.

---

# Part 2 — Solar Asset: Hayhurst Texas Solar

---

## Site Profile

```
┌────────────────────────────────────────────────────────┐
│  HAYHURST TEXAS SOLAR                                  │
│  Culberson County, TX (arid/desert)                    │
│  Coordinates: 31.815992°N, 104.0853°W                  │
│  Capacity: 24.8 MW                                     │
│  Construction start: 2026                              │
│  Operational lifespan: 30 years                        │
│  Asset lifetime: 2026 – 2055                           │
│  Climate zone: Hot desert (Köppen BWh)                 │
│  Baseline: 1985 – 2014 (CMIP6 historical standard)     │
└────────────────────────────────────────────────────────┘
```

**Why West Texas is interesting for solar:**
- Excellent solar resource (rsds peaks ~29 MJ/m²/day in June — top-tier in the US)
- Very low cloud cover → high capacity factors
- But: extreme summer heat (tasmax regularly 40–45°C) and low humidity
- The same conditions that make it great for solar also make thermal aging the primary risk

---

## SCVR Results — All Variables (Notebook 01)

*Single model (EC-Earth3P-HR), rolling 20-year windows, effectively SSP5-8.5*

| Variable | 2030 | 2035 | 2040 | 2045 | 2050 | Trend |
|---|---|---|---|---|---|---|
| **tasmin** | +9.2% | +11.9% | +14.8% | +16.7% | +17.9% | Strong ↑ — dominant signal |
| **tas** | +5.9% | +7.9% | +10.1% | +11.7% | +12.5% | Steady ↑ |
| **tasmax** | +4.2% | +5.6% | +7.4% | +8.6% | +9.2% | Consistent ↑ |
| **rsds** | +0.9% | +1.0% | +1.1% | +1.4% | +1.7% | Small ↑ — revenue offset |
| **sfcWind** | +0.2% | +0.2% | ~0% | −0.2% | +0.4% | Flat — no signal |
| **hurs** | ~0% | −1.1% | −3.2% | −6.7% | −7.9% | Declining — drying |
| **pr** | +11.9% | +5.6% | +1.1% | −8.9% | −17.8% | Inverts ~2040 |

> 2045 and 2050 have shorter future windows (15 and 10 years) — treat as directional, not precise.

---

## What Each SCVR Means for a Solar Panel

### tasmin: +14.8% by 2040 — THE DOMINANT RISK

```
Failure pathway: Peck's accelerated aging model

  Peck's equation: AF = exp(Ea/k × (1/T_ref - 1/T_stress)) × (RH_stress/RH_ref)^n

  Inputs that shift:
    T_stress ← tas SCVR (mean temperature rises)
    RH_stress ← hurs SCVR (humidity falls, partially offsetting)

  Why tasmin is key:
    In desert climates, evenings cool dramatically.
    If nights stay hotter (tasmin +14.8%), panels never get the
    cool-down period that slows thermal degradation.
    Hot nights = no relief from thermal stress = faster aging.
```

**Physical analogy:** Think of metal under constant heat vs metal that cools every night. The one that cools recovers partially. As nights warm, that recovery diminishes.

### tasmax: +7.4% by 2040 — EFFICIENCY LOSSES

```
Failure pathway: Temperature coefficient derating

  Most crystalline silicon panels: power output = -0.4%/°C above 25°C STC

  Example at Hayhurst:
    Baseline P98 tasmax: ~43°C → derating factor = (43-25) × 0.4% = 7.2% power loss
    Future P98 tasmax:   ~45°C → derating factor = (45-25) × 0.4% = 8.0% power loss

    Additional derating: +0.8 percentage points
    At 24.8 MW × 8,760 hrs × 25% CF × 0.8%:  ~435 MWh/yr extra loss
    At $40/MWh: ~$17,400/yr additional revenue loss
```

### tasmax - tasmin thermal swing

```
Failure pathway: Coffin-Manson thermal cycling fatigue

  Each day the panel heats up (tasmax) and cools down (tasmin).
  The daily temperature swing stresses solder joints and encapsulant.

  Nb01 signal:
    tasmax growing +9.2% by 2050 (days getting hotter)
    tasmin growing +17.9% by 2050 (nights warming faster)

    → Nights warming FASTER than days
    → Daily swing (tasmax - tasmin) may actually DECREASE slightly
    → Coffin-Manson fatigue may be lower than feared

  This is a case where two positive SCVRs partially cancel each other
  for a specific failure mode.
```

### hurs: −7.9% by 2050 — PARTIAL RELIEF

```
West Texas is drying out. Lower humidity:
  ✓ Reduces the humidity term in Peck's model → slows aging slightly
  ✗ Increases dust/soiling accumulation → reduces panel efficiency
  ✗ Increases wildfire FWI → fire damage risk rises

Net effect on Peck's: temperature increase still dominates.
The humidity decline is a second-order offset, not a rescue.
```

### pr: Inverts ~2040 — TWO RISKS IN ONE

```
Near-term (pre-2040): positive SCVR — more precipitation area
  → Flood risk increasing: more intense storm events
  → Hail: some CMIP6 models show increasing convective intensity

Long-term (post-2040): negative SCVR — drying dominates
  → Soiling: more dust days → panels need more cleaning
  → Fire weather: dry vegetation → higher FWI
  → Less frequent rain → no natural cleaning of panels

The sign flip means:
  Insurance (flood) pricing should use near-term signal
  Operations (cleaning schedule) should use long-term signal
```

### rsds: +1.7% by 2050 — THE SILVER LINING

```
rsds is NOT in the hazard chain. It's a performance input.
But a +1.7% increase in the solar radiation distribution area
translates to slightly more energy generation.

Rough estimate for Hayhurst:
  24.8 MW × 8,760 hrs × 25% CF × 1.7% = ~921 MWh/yr additional
  At $40/MWh → ~$36,800/yr
  Over 30 years (discounted at 8%) → ~$414,000 NPV

Small but real — partially offsets thermal losses.
This is why rsds is tracked even though it's not a SCVR hazard variable.
```

### sfcWind: ~0% — No Signal

Wind speed does not change meaningfully at this site. No structural wind stress change.

---

## Failure Mode Map: Hayhurst Solar

```
SCVR Signal                  Failure Pathway               NAV Impact
────────────                 ───────────────               ──────────
tasmin +14.8%  ──────────►  Peck's aging           ──►   IUL shortening
tas    +10.1%  ──────────►  (same, secondary)      ──►   (25yr → ~22yr)
                                                          ~$13M loss

tasmax +7.4%   ──────────►  Temp coefficient        ──►   BI losses
                             derating               ──►   ~435 MWh/yr
                                                          ~$17K/yr

tasmax }       ──────────►  Coffin-Manson           ──►   IUL (small)
tasmin }(↑↑)               thermal cycling               partly offset by
               slower swing (nights warm faster)          swing reduction

pr +11.9%      ──────────►  Flood / hail HCR        ──►   Event losses
pr -17.8%      ──────────►  Soiling / fire HCR      ──►   O&M cost increase

hurs -7.9%     ──────────►  Offsets Peck's          ──►   Small NAV benefit
                             (second order)

rsds +1.7%     ──────────►  Performance pathway     ──►   NAV upside
               (NOT hazard)  (pvlib model)                ~$414K NPV
```

---

## Priority Ranking for Hayhurst Solar

| Rank | Variable | SCVR (2040) | Primary concern |
|---|---|---|---|
| 1 | tasmin | +14.8% | Peck's aging — accelerated panel degradation |
| 2 | tasmax | +7.4% | Power output derating losses |
| 3 | tas | +10.1% | Secondary Peck's input |
| 4 | pr | +1.1% (flipping) | Near-term flood, long-term soiling |
| 5 | hurs | −3.2% | Partial offset to Peck's (note: negative is partially good) |
| 6 | rsds | +1.1% | Revenue upside (performance, not hazard) |
| 7 | sfcWind | ~0% | No material change |

---

## SSP Comparison (Notebook 03 Ensemble)

*Multi-model ensemble (`ensemble_pooled`, 6 models)*

| Variable | SSP2-4.5 | SSP5-8.5 | Delta |
|---|---|---|---|
| tasmax | ~+0.050 | ~+0.084 | ~+0.034 |
| tasmin | ~+0.060 | ~+0.092 | ~+0.032 |
| tas | ~+0.050 | ~+0.074 | ~+0.024 |
| pr | ~+0.002 | ~+0.022 | ~+0.020 |
| hurs | ~−0.010 | ~−0.015 | ~−0.005 |
| sfcWind | ~0 | ~0 | ~0 |
| rsds | ~+0.002 | ~+0.002 | ~0 |

> The emission scenario matters most for temperature variables — the delta between SSP245 and SSP585 is ~0.03-0.04 SCVR units, which translates to ~5 percentage points of NAV impairment difference.

---

## Summary: Hayhurst in One Paragraph

Hayhurst Texas Solar faces moderate-to-high climate risk driven overwhelmingly by temperature. Nights are warming faster than days (+14.8% SCVR on tasmin by 2040), keeping panels hot longer and accelerating Peck's thermal aging. Daytime heat (+7.4% tasmax) causes direct efficiency losses through the temperature coefficient. The West Texas drying trend (−3.2% hurs) provides a small offset to aging rates but simultaneously increases soiling and fire risk. Precipitation shows a near-term wet signal followed by long-term drying. Wind and solar radiation are essentially unchanged. The net financial outcome is a shortening of useful life from ~25 years to ~21-22 years, and increasing business interruption losses — estimated at **~13.7% NAV impairment under SSP5-8.5** (vs ~8.5% under SSP2-4.5).

---

# Part 3 — Wind Asset: Maverick Creek Wind

---

## Site Profile

```
┌────────────────────────────────────────────────────────┐
│  MAVERICK CREEK WIND                                   │
│  Concho County, TX (semi-arid/grassland)               │
│  Coordinates: 31.262546°N, 99.84396°W                  │
│  Capacity: 491.6 MW                                    │
│  Construction start: 2026                              │
│  Operational lifespan: 30 years                        │
│  Asset lifetime: 2026 – 2055                           │
│  Climate zone: Semi-arid (Köppen BSk/BSh)              │
│  Baseline: 1985 – 2014 (CMIP6 historical standard)     │
└────────────────────────────────────────────────────────┘
```

**Why Concho County is different from Culberson:**
- Further east, slightly more humid and more precipitation than Culberson
- Excellent wind resource — part of the "Wind Belt" through Central Texas
- Lower extreme heat than West Texas (Culberson is hotter and drier)
- Icing risk is real in winter (tasmin regularly below 0°C in Dec-Feb)

Maverick Creek uses **P1_core only** — rsds (solar radiation) is not relevant for a wind farm.

---

## Expected SCVR Results (Notebook 03 Ensemble)

*Multi-model ensemble (up to 6 CMIP6 models pooled), SSP2-4.5 and SSP5-8.5*

| Variable | SSP2-4.5 | SSP5-8.5 | Direction | Key concern |
|---|---|---|---|---|
| **tasmax** | ~+0.045 | ~+0.080 | Higher is worse | Material brittleness at thermal extremes |
| **tasmin** | ~+0.055 | ~+0.085 | Complex (see below) | Icing reduction (good) vs heat stress (minor) |
| **tas** | ~+0.045 | ~+0.070 | Higher is worse | Secondary — electronics cooling |
| **pr** | ~+0.005 | ~+0.020 | Extremes both | Flood downtime; negligible soiling effect |
| **sfcWind** | ~0 | ~0 | High ext worse | **Flat — the key finding** |
| **hurs** | ~−0.008 | ~−0.012 | Context dep. | Icing conditions; corrosion |

> Values are projections from ensemble runs — the flat sfcWind signal is consistent across all 6 models and both scenarios.

---

## What Each SCVR Means for a Wind Turbine

### sfcWind: ~0% — The Central Finding

```
Failure pathway: Palmgren-Miner cumulative fatigue

  Palmgren-Miner model: D = Σ(n_i / N_i)
  where n_i = actual load cycles at wind speed i
        N_i = fatigue life at wind speed i

  If sfcWind distribution doesn't change (SCVR ≈ 0):
    → n_i stays the same
    → N_i stays the same
    → D accumulates at baseline rate
    → No additional climate-driven fatigue

Wind turbines at Maverick Creek face essentially the same
wind-loading profile in 2055 as in baseline. The structural
fatigue risk from CHANGING wind patterns is near-zero.
```

**What this does NOT mean:** Wind turbines still face fatigue — it's just not getting worse due to climate change. The baseline fatigue is already priced into the 25-year design life.

### tasmin: +8.5% (SSP585) — ICING DYNAMICS

For a wind farm, warming nights have a very different implication than for solar:

```
Two competing effects of tasmin rising:

EFFECT 1: Fewer icing events (good)
  Icing occurs when: tasmin < 0°C AND hurs > ~75%
  As tasmin rises, fewer nights cross the 0°C threshold.
  Fewer icing events → fewer turbine shutdowns → less generation loss
  → Less ice loading on blades → less structural stress

EFFECT 2: Warmer operating temperature (minor)
  Turbine electronics and gearboxes run hotter.
  Generally secondary to icing effects for wind assets.

Net effect for Central Texas:
  The icing reduction (fewer frost nights) likely outweighs
  the thermal stress increase. For wind farms, warming tasmin
  may actually be a mild BENEFIT, unlike solar where it's the
  primary risk driver.
```

### tasmax: +8.0% (SSP585) — MATERIAL EFFECTS

```
Failure pathway: Material brittleness and electronics

  High tasmax → blade material (fiberglass/carbon fiber) thermal stress
  But: wind turbines are designed for wide temperature ranges
  The thermal coefficient issue that plagues solar panels (crystalline silicon
  -0.4%/°C) does not apply to wind turbines

  Concern level: LOW-MODERATE

  More relevant: nacelle electronics (inverters, sensors) have upper
  temperature limits. Extended high-heat periods may increase cooling
  system loads and failure rates.
```

### hurs: −1.2% (SSP585) — CORROSION AND ICING

```
Lower humidity:
  ✓ Reduces corrosion risk on metal components (nacelle, tower)
  ✓ Reduces icing probability (dry air → less freezing fog)
  ✗ Minor — does not significantly change blade aerodynamics

For wind turbines, lower humidity is generally beneficial.
```

### pr: +2.0% (SSP585) — FLOOD DOWNTIME ONLY

```
Flood risk:
  Wind farms are elevated (towers ~80m) — flood risk is mainly
  to substations, access roads, and underground cables.

  Hail risk:
  Hail is a real concern — hailstones can damage blade leading
  edges, causing erosion that reduces aerodynamic efficiency.

  SCVR for pr of +0.020 is modest — the flood/hail HCR in
  Notebook 04 will translate this to a small additional risk,
  primarily through access disruption and insurance events.
```

---

## Failure Mode Map: Maverick Wind

```
SCVR Signal                  Failure Pathway               NAV Impact
────────────                 ───────────────               ──────────
sfcWind ~0     ──────────►  Palmgren-Miner EFR    ──►   Baseline rate only
                             structural fatigue           No incremental
                                                          climate impact

tasmin +8.5%   ──────────►  Icing reduction       ──►   NAV UPSIDE (small)
               (warming)    → fewer shutdowns            + fewer blade stress
                                                          events

tasmax +8.0%   ──────────►  Electronics heat      ──►   Minor IUL effect
                             Material stress              Low impact

hurs -1.2%     ──────────►  Less corrosion        ──►   NAV upside (minor)
               (drying)     Less icing

pr +2.0%       ──────────►  Flood/hail HCR        ──►   Event losses
               (intensifying)                            Insurance costs
```

---

## Icing: The Unique Wind Risk

Unlike solar, wind farms in Central Texas face real icing risk. As climate warms:

```
Historical icing conditions at Maverick (baseline 1985-2014):
  Frost days (tasmin < 0°C): ~30-50 days/year (Dec-Feb)
  Icing conditions (tasmin < 0 AND hurs > 75%): ~10-20 days/year

Future projection (2026-2055, SSP585):
  Frost days: ~20-35 days/year (fewer cold nights)
  Icing conditions: ~7-15 days/year (both factors decline)

Change: fewer icing shutdowns, less ice loading
Benefit: ~5-15 additional generation days per year
Revenue impact: ~$1-3M NPV benefit (491.6 MW at typical CF)
```

This icing reduction is a genuine climate benefit for Maverick — rare in climate risk analysis where most signals are negative.

---

## Summary: Maverick Wind in One Paragraph

Maverick Creek Wind is notably **resilient to climate change** compared to Hayhurst Solar. The primary driver of wind turbine fatigue — wind speed distribution — shows essentially zero change (sfcWind SCVR ≈ 0). Temperature warming creates minor material stress but wind turbines are not temperature-sensitive in the way solar panels are. The most interesting signal is the warming of tasmin (nights getting warmer), which **reduces icing events** — a genuine benefit for a wind farm in Central Texas. Precipitation may intensify slightly near-term (flood/hail risk), but this is manageable through insurance. The net financial picture: **~2-4% NAV impairment under SSP5-8.5** — roughly one-quarter to one-third of what Hayhurst Solar faces.

---

# Part 4 — Solar vs Wind: Direct Comparison

---

```
                    HAYHURST SOLAR          MAVERICK WIND
                    (24.8 MW solar)         (491.6 MW wind)
────────────────────────────────────────────────────────────
Primary risk        Thermal aging           None (wind unchanged)
variable            tasmin +14.8%           sfcWind ~0%

Secondary risk      Power derating          Minor materials
variable            tasmax +7.4%            tasmax +8.0%

Unexpected          hurs drying             tasmin warming →
finding             offsets aging           FEWER icing events

Dominant            IUL shortening          Near-baseline EFR
financial           (life reduced ~3 yrs)   (no extra shortening)
impact

rsds role           Revenue offset          Not applicable
                    +1.7% upside

Overall climate     HIGH                    LOW-MODERATE
sensitivity

Estimated NAV       13.7% impairment        2-4% impairment
impairment          (SSP585)                (SSP585)
(SSP5-8.5)
```

### Why the Gap Is So Large

Solar panels are fundamentally **temperature-sensitive devices**:
- Operating efficiency drops with temperature
- Material aging accelerates with temperature (exponential in Peck's model)
- At Hayhurst, temperature is already pushing limits (summer peaks ~43°C)

Wind turbines are **mechanical devices** designed for harsh environments:
- Power output depends on wind speed (not temperature)
- Structural fatigue follows the wind distribution (which isn't changing)
- The primary climate signal (sfcWind) is essentially flat

This is not because wind assets are better-built — it's because the climate variable that drives their performance (wind) is not changing, while the variable that drives solar performance degradation (temperature) is changing significantly.

---

## Next

- [06 - Scenario Comparison](06_scenario_comparison.md) — SSP2-4.5 vs SSP5-8.5 side-by-side for both assets
- [07 - HCR: Hazard Change Ratio](07_hcr_hazard_change.md) — How SCVR translates to hazard-specific impact ratios
- [09 - NAV Impairment Chain](09_nav_impairment_chain.md) — Full SCVR → HCR → EFR → NAV chain with real dollar amounts
