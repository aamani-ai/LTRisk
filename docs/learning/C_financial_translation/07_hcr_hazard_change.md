# HCR — Hazard Change Ratio

**HCR measures how much climate change shifts the expected annual damage
from a specific hazard.** It captures BOTH the change in how often events
occur (frequency) AND the change in how bad each event is (severity).

```
HCR = (future_expected_damage - baseline_expected_damage) / baseline_expected_damage

  HCR = +0.30  means 30% MORE expected annual damage than the baseline
  HCR = -0.45  means 45% LESS expected annual damage (a warming benefit)
  HCR = 0      means no change
```

HCR is computed for InfraSure's **10 canonical hazards** — the same list
used by the hazards repo. For some, LTRisk can project the change. For
others, it can't. This doc explains which, how, and why.

> **BI vs EAL:** HCR measures damage change (related to EAL — total
> economic loss). To translate to Business Interruption (BI — specifically
> lost revenue from downtime): `Additional_BI = baseline_BI × HCR`.
> This requires baseline_BI from the hazards repo and assumes BI changes
> proportionally to damage (a documented linearity assumption).
> See Section 8 and [hcr_redefined_freq_severity.md](../../discussion/hcr_financial/hcr_redefined_freq_severity.md).

---

## 1. Why Both Frequency AND Severity Matter

A frequency-only metric misses that events also get MORE INTENSE under
warming. For some hazards, this changes the financial story entirely:

```
HAZARD          FREQUENCY CHANGE   SEVERITY CHANGE           FREQUENCY-ONLY
                                                             GETS IT WRONG?
═══════════════ ══════════════════ ═══════════════════════    ══════════════
Heat Wave       +150% (2.5× amp)  Events hotter + longer     Understates (+20%
                                  Cumulative heat doubles       vs +30-50% true)
                                  
Hurricane       -7.5% (fewer)     Wind +5%, rain +14%        YES — says "better"
                                  Damage +16-55% (V^3-V^9)     when actually worse
                                  
Wildfire        ~0% (count flat)  Area per fire up to 6×     YES — says "no change"
                                  The real story is severity     when damage doubles+
                                  
Hail            -25% (fewer)      Large stones +15-75%       YES — says "better"
                                  Damage nonlinear in size      when may be worse
                                  
Riverine Flood  +3% (Rx5day)      Intensity +7-14%/°C        Understates (+3%
                                  Damage nonlinear in depth     vs +10-30% true)

Ice Storm       -45% (fewer)      Severity unclear            OK — freq dominates
Strong Wind     ~0%               ~0%                         OK — both flat
```

**For 4 of 10 canonical hazards, frequency-only tells the wrong story.**

---

## 1B. The Two Components: Frequency × Severity

### The Mathematical Identity

The expected annual excess above a threshold decomposes exactly:

```
E[annual excess above T] = P(X > T) × E[X - T | X > T]
                         = frequency  × mean_excess
                         = "how often" × "how far above"

This is the law of iterated expectations — an identity, not an approximation.
No assumptions needed beyond stationarity within each 30-year window.
```

Therefore HCR can be decomposed:

```
HCR_combined = frequency_ratio × severity_ratio - 1

Where:
  frequency_ratio = freq_future / freq_baseline = (1 + HCR_freq)
  severity_ratio  = mean_excess_future / mean_excess_baseline

  Both are computable from the daily CMIP6 data we already process.
```

### Worked Example: Heat Wave at Hayhurst (SSP5-8.5)

```
Frequency:  baseline ~36.5 exceedance days → future ~101 days
            HCR_freq = +177% (but we use 2.5× published scaling → +20%)

Severity:   mean excess above P90 threshold:
            baseline = 1.29°C above threshold
            future   = 1.91°C above threshold
            severity_ratio = 1.91 / 1.29 = 1.48 (+48%)

If we combine (using direct counting + severity):
  HCR_combined = (1 + 1.77) × 1.48 - 1 = +310% (direct counting, very high)
  
If we combine (using published 2.5× + severity):
  HCR_combined = (1 + 0.20) × 1.48 - 1 = +78%
  
But: see the CRITICAL CAVEAT below about double-counting.
```

### Worked Example: Riverine Flood (Daily P95, SSP5-8.5)

```
Frequency:  HCR_freq = +5.5% (from direct counting)

Severity:   mean excess above P95 wet-day threshold:
            baseline = 7.79 mm above threshold
            future   = 8.30 mm above threshold
            severity_ratio = 8.30 / 7.79 = 1.065 (+6.5%)

Combined:   HCR_combined = 1.055 × 1.065 - 1 = +12.4%

For direct counting, this is straightforward — no double-counting risk
because the counting never captured severity in the first place.

Note: Rx5day (+2.6%) does NOT need severity integration because it
already measures intensity (mm), not frequency.
```

### CRITICAL CAVEAT: Double-Counting Risk With Published Scaling

```
When a published scaling factor (like Diffenbaugh's 2.5×) was derived
from climate model output, the researchers counted events in a WARMER
climate where events are BOTH more frequent AND more intense.

The 2.5× factor may ALREADY embed some severity change.
If we ALSO multiply by our severity ratio (1.48×), we may DOUBLE-COUNT
the severity component.

FOR DIRECT COUNTING (flood, ice storm):
  Severity IS genuinely missing — we count events equally regardless
  of intensity. Safe to add severity ratio.

FOR PUBLISHED SCALING (heat wave 2.5×):
  UNCERTAIN whether severity is already included. The 2.5× was derived
  from empirical event counting that implicitly captured intensity change.
  
  Honest reporting for heat wave:
    Lower bound: +20% (published scaling alone — may include some severity)
    Upper bound: +78% (published scaling × severity ratio — may double-count)
    Truth: likely between the two, but we cannot decompose the 2.5× into
           its frequency and severity components without reproducing
           Diffenbaugh's original analysis.
```

### When to Apply Severity Integration (Per Hazard)

```
HAZARD                  SEVERITY           DOUBLE-COUNT      RECOMMENDATION
                        INTEGRATION?       RISK?
═══════════════════     ════════════       ═══════════       ═══════════════
heat_wave               UNCERTAIN          YES               Report RANGE
(published 2.5×)        2.5× may embed     (published factor   (+20% to +78%)
                        severity            from empirical       
                                           counting)            

riverine_flood_daily    YES — add it       NO                Combined: +12.4%
(direct counting)       Counting misses    (counting never     (freq 5.5% ×
                        severity            had severity)       sev 6.5%)

riverine_flood_rx5day   NO — already       N/A               Keep +2.6% as-is
                        captures intensity  (measures mm,       
                        (mm, not count)     not count)          

ice_storm               KEEP FREQ-ONLY     AMBIGUOUS         Keep -44.5%
(compound threshold)    Compound makes     (4-var threshold     (severity unclear
                        "excess" ambiguous  has no single       for compound)
                                           intensity axis)     

strong_wind             MOOT               N/A               Keep ~0%
                        HCR ≈ 0            (no signal)         
```

---

## 2. The 10 Canonical Hazards

These are InfraSure's canonical hazard types from the hazards repo.
For each, we state whether LTRisk can compute an HCR and how.

### Tier 1 — Directly Computable or Published Scaling

#### Heat Wave (GOLD STANDARD)

```
Canonical definition: ≥3 consecutive days at or above 90°F (32°C)
                      (NOAA: "Heat" + "Excessive Heat")
                      
Computation:   Published scaling: SCVR_tasmax × 2.5
Source:        Diffenbaugh et al. 2017 (PNAS); Cowan et al. 2017
Cross-check:   NB04a direct counting gives implied scaling = 2.7× (within 8%)
Direction:     STRONGLY INCREASING
HCR estimate:  +20% per SSP5-8.5 epoch (freq only); +30-50% with severity

Hayhurst (SSP5-8.5):
  Year     SCVR_tasmax   × 2.5    = HCR       Interpretation
  ────     ──────────    ─────    ─────────   ──────────────
  2030     0.042          2.5     0.105       10% more heat damage
  2035     0.056          2.5     0.140       14%
  2040     0.074          2.5     0.185       19%
  2045     0.086          2.5     0.215       22%
  2050     0.092          2.5     0.230       23%
```

#### Riverine Flood

```
Canonical definition: River overflow from sustained rainfall/snowmelt
                      (NOAA: "Flood" + "Flash Flood" + "Heavy Rain")
                      
Computation:   Direct counting — Rx5day from daily CMIP6 pr data
               (No published site-level scaling exists)
               Mean SCVR_pr ≈ 0, but extremes increase (Jensen's inequality)
Direction:     INCREASING
HCR estimate:  +2.6% (SSP5-8.5, Rx5day); severity adds more (+10-30% true)
Published:     Clausius-Clapeyron ~6.5-7%/°C for extreme precip intensity
```

#### Ice Storm

```
Canonical definition: Freezing rain producing ≥0.25" ice accumulation
                      (NOAA: "Ice Storm")
                      
Computation:   Direct counting — compound threshold from daily data
               (tasmin < 0°C AND hurs > 85%)
Direction:     DECREASING below 40°N (benefit from warming)
HCR estimate:  -44.5% (SSP5-8.5, Hayhurst)
Published:     Jeong et al. 2019 (NHESS) — ice loads decrease below 40°N
```

#### Wildfire

```
Canonical definition: Uncontrolled fire in wildland vegetation
                      (NOAA: "Wildfire")
                      
Computation:   FWI computable from daily CMIP6 (tasmax, hurs, sfcWind, pr)
Direction:     STRONGLY INCREASING
HCR estimate:  Burned area roughly doubles per ~1.5°C of warming
Published:     Abatzoglou & Williams 2016 (PNAS) — doubled western US fire area
               Quilcaille et al. 2023 (ESSD) — FWI from all CMIP6 models
Caveat:        FWI calibrated for Canadian forests; regional calibration needed
```

### Tier 2 — Feasible From Published External Data

#### Hurricane

```
Canonical definition: Tropical cyclone ≥74 mph sustained winds
                      (NOAA: "Hurricane" + "Tropical Storm")
                      
Computation:   NOT computable from NEX-GDDP. Published consensus used.
Published:     Knutson et al. 2020 (BAMS, WMO consensus):
               Frequency: -5 to -10% per 2°C (fewer storms)
               Wind: +5% (1-10% range), Rain: +14%, Cat 4-5: +13%
               "Fewer but fiercer"
Direction:     Frequency DOWN, intensity UP → net damage INCREASING
               Mendelsohn et al. 2012: climate roughly doubles TC damage
               despite frequency decrease
HCR estimate:  +7% to +43% depending on wind-damage power law (V^3 to V^9)
Note:          Hayhurst (inland TX): low exposure regardless of trend
```

#### Coastal Flood

```
Canonical definition: Seawater inundation from surge/tides/SLR
                      (NOAA: "Coastal Flood" + "Storm Surge/Tide")
                      
Computation:   NOT computable from NEX-GDDP. Published SLR projections used.
Published:     Buchanan et al. 2020: SLR exponentially increases flood freq
               100-year events → 10-year events at 1/3 of US sites by 2050
               Amplification: 10× to 1000× per 0.5m SLR
Direction:     EXPONENTIALLY INCREASING
Note:          Hayhurst (inland TX): not applicable
```

#### Winter Weather

```
Canonical definition: Snow/sleet/freezing rain compound event
                      (NOAA: "Winter Storm" + "Winter Weather" + "Heavy Snow")
                      
Computation:   Direct counting — compound threshold (pr > X AND tasmin < 0°C)
Direction:     DECREASING below ~45°N
Published:     64% of US stations show less snowfall than 1970s
Note:          Not yet implemented in NB04a; feasible to add
```

### Tier 3 — Blocked or Trivial

#### Strong Wind

```
Canonical definition: Sustained winds ≥58 mph
Computation:   SCVR_sfcWind × 1.0 ≈ 0 (no climate signal at TX sites)
Direction:     FLAT (global "stilling" trend)
HCR:           ~0%
```

#### Hail — BLOCKED

```
Canonical definition: Ice pellets ≥0.75" from convective storms
Computation:   NOT computable (needs CAPE, wind shear — not in NEX-GDDP)
Published:     Raupach et al. 2021: frequency DOWN (US), stone size UP
               "Hailstone size dichotomy" — fewer small, more large
Direction:     AMBIGUOUS (net financial impact: likely increasing)
Note:          #2 financial risk for solar from insurance data.
               Hazards repo has full historical BI. Climate delta unknown.
```

#### Tornado — BLOCKED

```
Canonical definition: Rotating column EF0-EF5
Computation:   NOT computable (mesoscale, needs upper-air data)
Published:     Diffenbaugh 2013: severe environments +40-100%
               But environment ≠ tornado. Conversion efficiency unknown.
Direction:     UNCERTAIN
```

---

## 3. How HCR Is Computed

### Two Methods — Based on Data Availability

```
DOES A PUBLISHED PEER-REVIEWED SCALING FACTOR EXIST FOR THIS HAZARD?

  YES → Use it:
    HCR(t) = SCVR(t) × published_scaling_factor
    
    Heat wave:    SCVR_tasmax × 2.5 (Diffenbaugh 2017, PNAS)
    Hurricane:    Published consensus (Knutson 2020)
    Coastal flood: SLR projections (IPCC/NOAA)
    Strong wind:  SCVR_sfcWind × 1.0 (trivial, ≈ 0)
    
    The published scaling IS empirical counting done by other
    researchers — we reuse their peer-reviewed result.

  NO → Compute directly from daily CMIP6 data:
    Count hazard events AND compute mean excess above threshold.
    HCR_freq = (future_count - baseline_count) / baseline_count
    severity_ratio = mean_excess_future / mean_excess_baseline
    HCR_combined = (1 + HCR_freq) × severity_ratio - 1
    
    Riverine flood (daily): freq +5.5% × severity +6.5% = combined +12.4%
    Riverine flood (Rx5day): already captures intensity — no severity needed
    Ice storm: compound threshold — keep frequency-only (severity ambiguous)
    Wildfire: FWI from daily data (severity integration TBD)
    Winter weather: compound threshold counting (severity integration TBD)
    
    This is NOT a "fallback." It's the only option when no one
    has published the scaling. See pathway_defensibility.md.
```

### The Scaling Factors

| Hazard | Method | Severity Included? | HCR Estimate (SSP585) | Published Source |
|--------|--------|-------------------|----------------------|-----------------|
| Heat wave | Published scaling (2.5×) | UNCERTAIN — 2.5× may embed severity. Report range: +20% to +78% | +20% (scaling) to +78% (× severity) | Diffenbaugh 2017 (PNAS) |
| Riverine flood (daily) | Direct counting + severity | YES — combined: freq ×  severity | +12.4% (freq 5.5% × sev 6.5%) | C-C 7%/°C validates direction |
| Riverine flood (Rx5day) | Direct counting (mm) | ALREADY CAPTURED — measures intensity | +2.6% (as-is) | Standard hydrology metric |
| Ice storm | Direct counting | NO — compound threshold, severity ambiguous | -44.5% (freq only) | Jeong 2019 validates direction |
| Wildfire | Direct counting (FWI) | TBD — FWI is a composite index | TBD | Abatzoglou 2016 |
| Strong wind | Published (1.0×) | MOOT — HCR ≈ 0 | ~0% | SCVR ≈ 0 |
| Hurricane | Published external | PARTIALLY — Knutson reports freq + intensity separately | +7% to +43% (combined) | Knutson 2020 (BAMS) |
| Coastal flood | Published SLR | YES — SLR amplification captures both | 10-1000× | Buchanan 2020; IPCC AR6 |
| Hail | BLOCKED | N/A | N/A | Hazards repo covers |
| Tornado | BLOCKED | N/A | N/A | SPC data covers |
| Winter weather | Direct counting | TBD | TBD (decreasing) | Not yet implemented |

### Annual Interpolation (3-Anchor Fit)

```
For temperature-driven hazards (published scaling):
  Annual SCVR from NB03 → HCR(t) = SCVR(t) × scaling_factor
  R² > 0.97 for temperature variables

For directly-computed hazards:
  1. Split future into 3 non-overlapping decades:
     [2026-2035], [2036-2045], [2046-2055]
  2. Compute HCR for each decade (anchor point)
  3. Fit linear trend through 3 anchors → annual values

  HCR
    25 │                                             * Anchor 3
       │                                        ····   (2046-2055)
    20 │                                   ·····
       │                              ·····
    15 │                         *····       ← Linear fit
       │                    ····   Anchor 2
    10 │               ····        (2036-2045)
       │          *····
     5 │     ····   Anchor 1
       │····        (2026-2035)
     0 └──────────────────────────────────────────────
        2026   2030   2035   2040   2045   2050  2055
```

---

## 4. The Non-Linear Amplification — Why HCR ≠ SCVR

A small shift in the distribution mean causes a disproportionately large
change in threshold exceedances:

```
  Probability
  density
    ▲
    │         Baseline         Future (shifted right)
    │          ╭──╮              ╭──╮
    │        ╭─╯  ╰─╮         ╭─╯  ╰─╮
    │      ╭─╯      ╰─╮     ╭─╯      ╰─╮
    │    ╭─╯    ░░░░   ╰─╮╭─╯   ▓▓▓▓▓▓  ╰─╮
    │  ╭─╯      ░░░░░░   ╰╯     ▓▓▓▓▓▓▓▓   ╰─╮
    │──╯        ░░░░░░░░║        ▓▓▓▓▓▓▓▓▓▓    ╰──
    └───────────────────║────────────────────────────► Temperature
                        ║
                   THRESHOLD (fixed)

    ░░░ = baseline days above threshold (small area)
    ▓▓▓ = future days above threshold (much larger area)

    Mean shift:           +8%  (SCVR = 0.074)
    Tail exceedance shift: ~140% more days above threshold
    Amplification:         ~2.5×
```

```
SCVR vs HCR at Hayhurst (heat wave, SSP5-8.5):

               SCVR (distribution shift)         HCR (hazard change)
               ─────────────────────────         ──────────────────────
2030:  ██░░░░░░░░░░░░░░░░░░  4.2%      ██████░░░░░░░░░░░░░░  10.5%
2035:  ███░░░░░░░░░░░░░░░░░  5.6%      ████████░░░░░░░░░░░░  14.0%
2040:  ████░░░░░░░░░░░░░░░░  7.4%      ██████████░░░░░░░░░░  18.5%
2045:  █████░░░░░░░░░░░░░░░  8.6%      ████████████░░░░░░░░  21.5%
2050:  █████░░░░░░░░░░░░░░░  9.2%      █████████████░░░░░░░  23.0%

       └── moderate shift ──┘           └── substantial hazard ─┘
       The 2.5× amplification is the non-linear tail effect.
```

### The 2.5× vs 26× Threshold Sensitivity

NB04 revealed that different threshold definitions give very different
scaling factors from the SAME data:

```
Definition 1 — compound heat wave (3+ consecutive, tasmax+tasmin > P90):
  Baseline: ~1.5 compound days/yr → Future: ~19.6 → implied scaling ~2.5×

Definition 2 — simple P90 exceedance (tasmax > P90, any single day):
  Baseline: ~36.5 days/yr → Future: ~101 → implied scaling ~26×

SAME DATA, 10× DIFFERENT SCALING.
Both are correct for their threshold definition.

The published 2.5× (Diffenbaugh) was calibrated for compound definitions.
The 26× applies to simple single-day P90 exceedance.
This is why using published scaling avoids threshold subjectivity.
```

---

## 5. Cross-Validation

For heat wave (the hazard with published scaling), we compute BOTH
published scaling and direct counting, then compare:

```
Published scaling (Pathway A):  SCVR_tasmax × 2.5 = +18.5% (2040)
Direct counting (Pathway B):    implied scaling = 2.7× (compound HW definition)

Agreement: within 8%
→ Published scaling is validated at this site.
→ The 2.5× factor is appropriate for compound heat wave events.
```

---

## 6. Negative HCR — When Warming Is a Benefit

Some hazards DECREASE with warming — these produce negative HCR:

```
Frost/freeze events:
  Baseline: 30-50 frost days/year at Hayhurst/Maverick
  Future: 20-35 (warming reduces sub-zero days)
  HCR_frost: -0.25 to -0.40

Icing:
  Baseline: ~0.6 icing days/yr at Hayhurst
  Future: ~0.3
  HCR_icing: -0.45

Financial: Fewer shutdown days → MORE revenue → NAV UPSIDE
  Maverick icing reduction: ~$1-3M NPV benefit over asset life
```

---

## 7. Sensitivity Analysis

```
SCVR_tasmax (2040) = 0.074 (fixed from climate models)

Scaling   HCR      NAV impact     As % of $60M
────────  ───────  ───────────    ────────────
2.0       0.148    ~$4.2M         7.0%
2.5       0.185    ~$5.9M         9.8%    ← base case
3.0       0.222    ~$7.8M         13.0%

NAV ($M)
 8 │                                          ●  3.0
   │                                     ●
 6 │                                ●         ← 2.5 (base)
   │                           ●
 4 │                      ●                   ← 2.0
   │
 2 │
   └──────────────────────────────────────────
     1.0    1.5    2.0    2.5    3.0    3.5
                  Heat Scaling Factor

A ±0.5 change in scaling moves NAV by ~±$1.5-2M.
Scaling factors are the largest uncertainty in the HCR → NAV chain.
```

---

## 8. How HCR Connects to BI (Business Interruption)

### The Formula

```
Additional_climate_BI(hazard, t) = baseline_BI(hazard) × HCR(hazard, t)

Where:
  baseline_BI = historical annual BI from the hazards repo ($/yr)
  HCR = climate change damage ratio from LTRisk (fractional)
```

### The Baseline BI Availability Problem

```
Hazards repo computes BI for:      Hail, Tornado, Strong Wind (3 hazards)
LTRisk computes HCR for:           Heat, Flood, Ice, Wildfire, etc. (7 hazards)

OVERLAP: Only Strong Wind has BOTH — but HCR ≈ 0.
→ No hazard currently has a clean Additional_BI computation.

For hazards with HCR but no baseline BI (heat, flood, etc.):
  Option C1: Use NRI EAL as proxy (EAL ≠ BI — linearity assumption)
  Option C2: Expand hazards repo BI to cover these hazards
  Option C3: Compute BI directly in LTRisk using damage functions
```

### The Linearity Assumption

```
Applying HCR (computed from damage-level data) to BI assumes:
  BI changes proportionally to total damage.
  
  This UNDERESTIMATES for heat (BI is mostly shutdown hours, 
  which grow faster than property damage under warming).
  
  This OVERESTIMATES for hail (property damage grows faster
  than BI under larger stone sizes).
  
  Gen.1: Accept as documented assumption.
  Gen.2: Develop BI-specific damage functions.
```

### The Financial Chain (Worked Example)

```
HAYHURST SOLAR 2040, SSP5-8.5:

HCR per hazard              baseline_BI     Additional_BI
──────────────────────────  ──────────────  ─────────────
heat_wave:     HCR = +0.185 $35K/yr (est.)  $6,475/yr
flood_rx5day:  HCR = +0.020 $7K/yr (est.)   $140/yr
wind_extreme:  HCR ≈ 0      $8K/yr          $0/yr
fire_weather:  Risk flag     —               —
icing_shutdown:HCR = -0.044  $2K/yr          -$88/yr (benefit)
                             ──────────────  ─────────────
TOTAL                        $52K/yr         $6,527/yr

→ CFADS(2040) = Revenue × (1-EFR) - baseline_BI_total - Additional_BI - OpEx
              = $2.07M × 0.993 - $52K - $6.5K - $704K
              = $1.29M

Channel 1 (HCR) contribution: ~$6.5K/yr at year 2040
Channel 2 (EFR) contribution: ~$41K/yr at year 2040
Channel 2 is ~6× larger than Channel 1.
```

---

## 9. EFR — The Other Channel (Separate From HCR)

HCR and EFR are parallel, independent channels:

```
HCR (this doc):  Change in expected DAMAGE from hazard EVENTS
  Events cause operational shutdown/curtailment
  Temporary — plant resumes after the event
  Additional_BI = baseline_BI × HCR

EFR (doc 08):    Acceleration of equipment DEGRADATION rate
  Continuous climate stress ages equipment faster
  Permanent — damage accumulates each year
  climate_degrad + IUL truncation
  
  Peck's (thermal aging):     Mode A (published Arrhenius)
  Coffin-Manson (cycling):    Mode B (direct freeze-thaw counts)
  Palmgren-Miner (wind):      Mode A (SCVR ≈ 0)

THEY DON'T OVERLAP:
  "Plant was shut down for 4 hours" = HCR (BI, temporary)
  "Panels aged 11% faster this year" = EFR (degradation, permanent)
```

---

## 10. Common Misconceptions

| You might think... | But actually... |
|---|---|
| HCR = SCVR | No — HCR is amplified. A +8% SCVR can produce +20% HCR (2.5× amplification). |
| HCR only measures frequency | Redefined: HCR captures both frequency AND severity through the damage function. |
| All hazards increase with warming | No — ice storm (-45%), frost (-25-40%), icing (-45%) are financial BENEFITS. |
| The 2.5× scaling is our assumption | No — it's from Diffenbaugh et al. 2017 (PNAS), peer-reviewed, cross-validated at 2.7×. |
| 2.5× and 26× contradict each other | No — different threshold definitions. Compound heat wave: 2.5×. Simple P90: 26×. Both correct for their definition. |
| HCR directly gives you $ losses | No — HCR gives the damage RATIO. To get $: Additional_BI = baseline_BI × HCR. This requires baseline_BI from the hazards repo. |
| Hail can be projected from CMIP6 | No — requires CAPE and wind shear, not available. Use hazards repo historical data. |
| We can compute HCR for all 10 hazards | No — 7 computable, 2 blocked (hail, tornado), 1 trivial (strong wind ≈ 0). |

---

## Next

- [08 — EFR: Equipment Degradation](08_efr_equipment_degradation.md) — Channel 2 (degradation, parallel to HCR)
- [09 — NAV Impairment Chain](09_nav_impairment_chain.md) — How HCR + EFR combine in CFADS
- [04 — SCVR Report Methodology](../B_scvr_methodology/04_scvr_methodology.md) — What feeds HCR

## Discussion Docs

- [HCR redefined (freq + severity)](../../discussion/hcr_financial/hcr_redefined_freq_severity.md) — Full argument for redefining HCR + Gen.1 assumptions
- [Top-down canonical reframe](../../discussion/hcr_financial/hcr_top_down_reframe.md) — Starting from 10 canonical hazards + Tier 1/2/3 assessment
- [Published scaling defensibility](../../discussion/hcr_financial/pathway_defensibility.md) — Why published scaling where available, direct computation where necessary
- [HCR/EFR boundary](../../discussion/hcr_financial/hcr_efr_boundary.md) — Which hazards cause BI (HCR) vs degradation (EFR)
- [Pipeline complementarity](../../discussion/architecture/pipeline_complementarity.md) — How hazards repo and LTRisk connect
- [BI methodology foundations](../../discussion/bi_methodology/01_what_is_bi.md) — What BI is and isn't

## Key References

| Paper | Finding | DOI |
|-------|---------|-----|
| Diffenbaugh et al. 2017 | Heat wave 2.5× amplification | [doi:10.1073/pnas.1618082114](https://doi.org/10.1073/pnas.1618082114) |
| Cowan et al. 2017 | 4-34 extra heat wave days/°C | [doi:10.1038/s41598-017-12520-2](https://doi.org/10.1038/s41598-017-12520-2) |
| Knutson et al. 2020 | Hurricane: fewer but fiercer | [doi:10.1175/BAMS-D-18-0194.1](https://doi.org/10.1175/BAMS-D-18-0194.1) |
| Tabari 2020 | Extreme precip +6.5-7%/°C | [doi:10.1038/s41598-020-70816-2](https://doi.org/10.1038/s41598-020-70816-2) |
| Jeong et al. 2019 | Ice loads decrease below 40°N | [doi:10.5194/nhess-19-857-2019](https://doi.org/10.5194/nhess-19-857-2019) |
| Abatzoglou & Williams 2016 | Wildfire area doubled | [doi:10.1073/pnas.1607171113](https://doi.org/10.1073/pnas.1607171113) |
| Mendelsohn et al. 2012 | TC damage doubles (V^3-V^9) | [doi:10.1038/nclimate1357](https://doi.org/10.1038/nclimate1357) |
| Buchanan et al. 2020 | Coastal flood exponential with SLR | [doi:10.1038/s41598-020-62188-4](https://doi.org/10.1038/s41598-020-62188-4) |
| Raupach et al. 2021 | Hail: fewer US events, larger stones | [doi:10.1038/s43017-020-00133-9](https://doi.org/10.1038/s43017-020-00133-9) |
| Quilcaille et al. 2023 | FWI from all CMIP6 1850-2100 | [doi:10.5194/essd-15-2153-2023](https://doi.org/10.5194/essd-15-2153-2023) |

Return to [Index](../00_index.md) for the full learning guide table of contents.
