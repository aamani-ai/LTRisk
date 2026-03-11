# HCR — Hazard Change Ratio

**HCR translates a climate distribution shift (SCVR) into a hazard-specific impact ratio.** It answers: *"If the temperature distribution shifted +8%, how many more heat wave days does that produce?"*

The answer is not 8%. A small shift in the mean can cause a large change in threshold exceedances — this non-linear amplification is what HCR captures.

---

## 1. The Simple Version

SCVR tells you *"the distribution shifted."* HCR tells you *"that shift created this many more hazard events."*

```
SCVR says:                                HCR says:
  "tasmax distribution area               "that means 21% more heat wave days,
   grew 8.4%"                              13% more tropical nights, and
                                            a Fire Weather Index increase of 15%"

  It's a single number about              It's a per-hazard number that connects
  the whole distribution.                  to specific damage mechanisms.
```

**Why the multiplier isn't 1.0:**

```
Temperature (°C)
    ▲
 45 │                                    ╭─── Future
    │                               ╭────╯
 43 │─ ─ ─ ─ ─ ─ ─THRESHOLD─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─ ─ ─
    │                          ╭────╯  ╭─── Baseline
 41 │                     ╭────╯  ╭────╯
    │                ╭────╯  ╭────╯
 39 │           ╭────╯  ╭────╯
    │      ╭────╯  ╭────╯
 37 │ ╭────╯  ╭────╯
    │─╯  ╭────╯
 35 │────╯
    └──────────────────────────────────────────►
       0%     5%     10%    15%    20%    25%
                  Exceedance probability

  Baseline days above threshold: ████         (~8% of days)
  Future days above threshold:   ████████████  (~19% of days)

  Distribution shifted ~8% (SCVR) but days above threshold
  increased ~140% — a 2.5× amplification.

  This is the non-linear tail effect that HCR captures.
```

A small mean shift pushes more days past a fixed threshold because the tail of the distribution is thin — many values are clustered just below the threshold, and a small nudge moves them above it.

**Annual framing:** HCR is computed **per year**, not per epoch. As SCVR(t) evolves year by year, HCR(t) tracks it:

```
Year:    2030   2031   2032   ...   2040   ...   2050
SCVR(t): 0.03   0.03   0.04  ...   0.07   ...   0.12
HCR(t):  0.08   0.08   0.10  ...   0.18   ...   0.30
         ^^^^                       ^^^^         ^^^^
         small                     moderate      large
```

Each year's HCR maps directly to that year's cash flow adjustment in the CFADS model.

---

## 2. Variables vs Hazards — The Mapping

Climate variables are **measurements**. Hazards are **damage events**.

```
MEASUREMENTS                        DAMAGE EVENTS
(what the models output)            (what breaks equipment)
─────────────────────               ────────────────────────

  tasmax (°C)  ─────────────────►  Heat Wave
               ─────────────────►  Summer Days (>25°C)

  tasmin (°C)  ─────────────────►  Frost Days (tasmin < 0°C)
               ─────────────────►  Cold Wave
               ─────────────────►  Tropical Nights (>20°C)

  tasmax + tasmin ──────────────►  Freeze-Thaw Cycles
                                   (tasmin < 0 AND tasmax > 0)

  tas (°C)     ─────────────────►  Cooling/Heating Degree Days

  pr (mm/day)  ─────────────────►  Extreme Precipitation (Rx5day)
               ─────────────────►  Dry Spells (consecutive pr=0)

  sfcWind (m/s) ────────────────►  Extreme Wind Events
                ────────────────►  Cut-Out Events (>25 m/s)

  hurs (%)     ─────────────────►  Humidity Stress

  tas + hurs + sfcWind + pr ────►  Fire Weather Index (FWI)

  tasmin + hurs ────────────────►  Icing Conditions
                                   (T < 0°C AND RH > 75%)
```

### Hazard Definitions — From Team Framework

These definitions are drawn from the team's [LT Risk Evolution Framework](../background/drive_docs/LT%20Risk%20Evolution%20Framework.md) Appendix 1, with literature sources noted.

| Hazard | Definition | Source Variables | Literature |
|--------|-----------|-----------------|------------|
| **Heat Wave** | 3+ consecutive days where T_max AND T_min exceed the 90th percentile of the historical baseline | tasmax, tasmin | Copernicus EDO factsheet |
| **Cold Wave** | 3+ consecutive days where T_max AND T_min fall below the 10th percentile of the historical baseline | tasmax, tasmin | Copernicus EDO factsheet |
| **Frost Days** | Days where T_min < 0°C | tasmin | ClimPACT indices |
| **Icing Days** | Days where T_max < 0°C | tasmax | ClimPACT indices |
| **Extreme Precip** | Maximum rolling 5-day precipitation total (Rx5day) | pr | ClimPACT indices |
| **Dry Spell** | Maximum consecutive days with pr < 1mm | pr | (derived) |
| **Wind Extreme** | Daily mean as proxy for storm intensity | sfcWind | PMC/12586526 |
| **Wildfire (FWI)** | Fire Weather Index = f(T_max, RH, wind, pr) | tas, hurs, sfcWind, pr | PMC/11737286 |
| **Icing Conditions** | T < 0°C AND RH > 75% | tasmin, hurs | (compound) |

### Additional Indices (Derivable from Current Variables)

| Index | Definition | Use Case |
|-------|-----------|----------|
| Tropical Nights | Days where T_min > 20°C | Peck's aging — no nighttime relief |
| Summer Days | Days where T_max > 25°C | Solar efficiency drop-off threshold |
| Cooling Degree Days | Σ max(0, T_mean − 18.33°C) | Substation/inverter cooling loads |
| Heating Degree Days | Σ max(0, 18.33°C − T_mean) | Facility heating costs |
| Dry Spells | Max consecutive days with pr = 0 | Wildfire fuel drying, solar soiling |

### What's Directly Computable vs Proxy

```
DIRECTLY COMPUTABLE (from NEX-GDDP daily data):
  ✓ Heat wave days      ✓ Frost days       ✓ Tropical nights
  ✓ Summer days         ✓ Icing days       ✓ Dry spell length
  ✓ Rx5day              ✓ CDD/HDD         ✓ Wind cut-out events
  ✓ FWI (using simplified Canadian FWI)

PROXY ONLY (need variables not in NEX-GDDP):
  ~ Wind gusts (have daily mean, not instantaneous max)
  ~ Hail (no direct variable — use convective proxies)
  ~ Wildfire (full FWI needs VPD, soil moisture, fuel load)

NOT AVAILABLE:
  ✗ Lightning frequency
  ✗ Tornado events
  ✗ Coastal flooding / storm surge
```

**NB01 already computes many of these.** The annual climate indices in Notebook 01 — `heat_wave_days`, `frost_days`, `rx5day`, `fwi_mean` — are exactly the hazard counts that HCR measures. NB04 should build on this existing infrastructure.

---

## 3. HCR Formula — Annual Computation

### The Phase 1 Formula (Linear)

```
HCR_hazard(t) = SCVR_variable(t) × scaling_factor

Where:
  t              = year (2026, 2027, ..., 2055)
  SCVR_variable  = annual SCVR for the relevant input variable
  scaling_factor = hazard-specific amplification constant
```

This is a **linear approximation** — Phase 1 of the implementation. Future phases may use power-law or lookup-table HCR functions.

### Why Scaling ≠ 1.0

Three physical reasons justify amplification:

**1. Tail amplification (threshold exceedance)**

When a distribution shifts by δ, the fraction of values exceeding a fixed threshold changes by much more than δ. For a normal distribution:

```
If the mean shifts by 0.5σ:
  - Values above μ+1σ increase from 15.9% to 30.9% (nearly doubled)
  - Values above μ+2σ increase from 2.3% to 6.7% (nearly tripled)

The further into the tail, the larger the amplification.

This is why heat scaling > 1: a small mean temperature shift
causes a disproportionate increase in extreme heat days.
```

**2. Clausius-Clapeyron for precipitation**

The atmosphere holds ~7% more water vapor per °C of warming. This amplifies extreme precipitation events even when mean precipitation changes little:

```
+1°C warming → +7% atmospheric moisture capacity
  → Extreme storm events draw from a richer moisture pool
  → Rx5day (extreme 5-day precipitation) grows ~7%/°C
  → But mean precipitation may grow only ~2%/°C

The extreme:mean ratio ≈ 3.5× amplification
This is why precipitation HCR scaling > 1
```

**3. Compound effects**

Some hazards depend on multiple variables acting together:

```
Icing = (T < 0°C) AND (RH > 75%)
  - If T warms (fewer days below 0°C)
  - AND humidity drops (fewer days above 75%)
  - Both effects reduce icing → compound reduction

Fire = f(high T, low RH, wind, dry fuel)
  - Warming + drying act together → compound amplification
  - The combined effect exceeds the sum of individual effects
```

### Current Scaling Factors

| Hazard | Scaling Factor | Input Variable(s) | Status | Basis |
|--------|---------------|-------------------|--------|-------|
| Heat stress | 2.5 | tasmax SCVR | Working estimate | Tail amplification at P90; Peck's calibration |
| Flood (extreme precip) | 1.5–2.0 | pr SCVR (high tail) | Preliminary range | Clausius-Clapeyron ~7%/°C |
| Hail | 1.0 | pr SCVR + sfcWind SCVR | Placeholder | Limited literature for convective proxy |
| Soiling/dust | 0.8 | pr SCVR (dry days) | Preliminary | Indirect: fewer rain days → more dust |
| Fire weather | Complex | tas + pr + hurs + sfcWind | Framework only | Multi-variable FWI interaction |
| Freeze-thaw | 1.0–1.5 | tasmin SCVR (inverse) | Working estimate | Linear threshold crossing |
| Icing | Compound | tasmin + hurs | Working estimate | Dual-threshold logic |

> **Confidence note:** These scaling factors are the **largest source of uncertainty** in the entire SCVR→NAV chain. The physics (Peck's, Coffin-Manson) are well-established, but the climate-to-hazard amplification factors are working estimates that need validation against observed hazard frequency data. See Section 9.

### Linear vs Non-Linear HCR

Phase 1 uses `HCR = SCVR × constant` (linear). This is appropriate when:
- SCVR is small (<0.15) — the linear approximation holds
- We don't have enough data to calibrate a non-linear function

For future phases, a power-law form may be more physical:

```
Phase 1 (current):    HCR = SCVR × α
Phase 2+ (future):    HCR = α × SCVR^β

Where β > 1 captures accelerating tail effects.
Example: β = 1.3 means a doubling of SCVR more than doubles HCR.
```

For the SCVR range we observe (0.03–0.16), the linear and power-law forms differ by <15%. The linear form is adequate for Phase 1.

---

## 4. Worked Example: Heat Stress at Hayhurst Solar

### Setup

Hayhurst Solar, SSP5-8.5, heat stress hazard.

From NB03 ensemble SCVR (using annual values from the team framework's annual approach):

```
Year:      2030    2035    2040    2045    2050
SCVR_tasmax: 0.042   0.056   0.074   0.086   0.092
```

Heat stress scaling factor: **2.5** (working estimate).

### Annual HCR Computation

```
HCR_heat(t) = SCVR_tasmax(t) × 2.5

Year     SCVR_tasmax   × 2.5   = HCR_heat    Interpretation
────     ──────────    ─────   ─────────    ──────────────
2030     0.042          2.5     0.105        10% more heat stress
2035     0.056          2.5     0.140        14% more heat stress
2040     0.074          2.5     0.185        19% more heat stress
2045     0.086          2.5     0.215        22% more heat stress
2050     0.092          2.5     0.230        23% more heat stress
```

### Visualising the Amplification

```
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

### What HCR = 0.185 Means in Practice (Year 2040)

```
Baseline heat wave days per year (Hayhurst):  ~15 days
  (days where tasmax AND tasmin exceed P90 of historical)

Future heat wave days: 15 × (1 + 0.185) = ~17.8 days

Additional heat wave days: ~2.8 days/year

But each additional day at higher intensity:
  - Higher peak temperatures (P90 threshold itself shifts)
  - More hours above panel derating threshold (25°C STC)
  - More cumulative thermal stress for Peck's aging model

The 2.8 extra days × higher intensity per day = ~19% more total
heat stress, consistent with HCR = 0.185.
```

### Dollar Impact Per Year

```
Annual HCR feeds directly into CFADS:

  BI_heat(2040) = baseline_BI_heat × HCR_heat(2040)
                = baseline_BI_heat × 0.185

If baseline heat-related BI = $35K/yr:
  Additional BI from heat = $35K × 0.185 = $6,475/yr

  Over asset life (NPV at 8%): feeds into total NAV impairment
  See doc 09 for the complete financial chain.
```

---

## 5. Worked Example: Precipitation → Flood Risk

### The Precipitation Puzzle

Precipitation SCVR at Hayhurst shows the inversion pattern:

```
Year:      2030    2035    2040    2045    2050
SCVR_pr:   +0.119  +0.056  +0.011  -0.089  -0.178
            wet ──────────── dry ──────────── dry
```

For flood risk, the **positive** SCVR years matter (more extreme rain events). For soiling/fire risk, the **negative** SCVR years matter (drying).

### HCR for Flood

```
HCR_flood(t) = max(0, SCVR_pr(t)) × flood_scaling

Where flood_scaling = 1.5-2.0 (Clausius-Clapeyron amplification)
Using midpoint 1.75:

Year     SCVR_pr    Clamp    × 1.75   = HCR_flood
────     ───────    ─────    ──────   ──────────
2030     +0.119     0.119     1.75     0.208
2035     +0.056     0.056     1.75     0.098
2040     +0.011     0.011     1.75     0.019
2045     −0.089     0.000     1.75     0.000   ← no flood amplification
2050     −0.178     0.000     1.75     0.000   ← drying period
```

**Why we clamp at zero:** Negative SCVR_pr means overall drying — fewer precipitation days. But individual storms in a drier climate can still be intense. The clamping is a simplification; Phase 2+ may separate the wet tail from the dry tail of the pr distribution.

### Clausius-Clapeyron Amplification

```
Why does flood scaling exceed 1.0?

The atmosphere obeys Clausius-Clapeyron:
  +1°C warming → ~7% more moisture capacity

What this means for storms:

  Historical 100mm storm event:
    Atmosphere holds X kg/m² of water vapor
    Storm dumps ~100mm

  Future (+2°C warmer) 100mm-equivalent storm:
    Atmosphere holds X × 1.14 kg/m² (7% × 2°C)
    Storm dumps ~114mm

    Same storm dynamics → 14% more rainfall
    The pr SCVR captures the distribution shift,
    but the Clausius-Clapeyron effect amplifies
    the extreme tail disproportionately.

  At the 99th percentile, observed amplification
  is often 2-3× the C-C rate → scaling = 1.5-2.0
```

---

## 6. Negative HCR — Warming Reduces Some Hazards

Not all HCR values are positive. Warming genuinely reduces some hazards:

```
HAZARDS THAT DECREASE WITH WARMING

  Frost days:
    Baseline (Maverick): ~30-50 frost days/year (Dec-Feb)
    Future (SSP585):     ~20-35 frost days/year
    HCR_frost:           NEGATIVE (~-0.25 to -0.40)
    → Fewer freeze events → less icing on turbine blades

  Cold wave days:
    Same direction — fewer consecutive cold days
    HCR_coldwave:        NEGATIVE

  Icing conditions (compound):
    Requires both T < 0°C AND RH > 75%
    Both conditions become less frequent
    HCR_icing:           NEGATIVE (~-0.30 to -0.50)

FINANCIAL IMPLICATION:
  Negative HCR = FEWER hazard events = LESS damage
  This shows up as a NAV UPSIDE in the financial model.

  For Maverick Wind:
    Icing reduction saves ~$1-3M NPV (fewer shutdowns)
    This partially offsets the (small) heat-related costs
```

This is one of the few cases in climate risk analysis where warming produces a genuine financial benefit — and it's specific to wind farms in regions with meaningful icing risk.

---

## 7. Compound Events — When Hazards Interact

### What Are Compound Events?

Some damage occurs only when **two or more climate conditions coincide**. The combined HCR is not simply additive:

```
COMPOUND EVENT EXAMPLES

1. DROUGHT → FLASH FLOOD
   Extended dry spell hardens soil surface
   → When rain finally arrives, reduced infiltration
   → Same rainfall event produces more surface runoff
   → Flood damage amplified by prior drought

   HCR_compound > HCR_drought + HCR_flood

2. HEAT × HUMIDITY → ACCELERATED AGING
   Peck's model: AF = f(Temperature) × f(Humidity)
   The two factors MULTIPLY, not add.
   A +10% temperature increase combined with +10% humidity
   gives more than +20% total aging acceleration.

   EFR captures this directly (see doc 08).

3. WIND × ICE → STRUCTURAL FAILURE
   High winds on iced blades create asymmetric loading
   that neither wind alone nor ice alone would cause.
   The loading is multiplicative:

   Load_compound = Load_wind × (1 + ice_mass_fraction)

   Blade icing + sustained wind = the most dangerous
   combination for turbine structural integrity.
```

### How Compound HCRs Interact

```
SIMPLE (INDEPENDENT) HAZARDS:
  HCR_total = HCR_heat + HCR_flood + HCR_wind
  (each hazard acts on a different damage pathway)

COMPOUND (INTERACTING) HAZARDS:
  HCR_compound = f(HCR_A, HCR_B) > HCR_A + HCR_B
  (damage pathways overlap or amplify each other)

Phase 1 approach: treat as independent (additive)
Phase 2+: implement compound interaction terms

For Phase 1, this is conservative (underestimates compound risk)
when both hazards increase, but the error is small when
SCVR values are moderate (<0.15).
```

---

## 8. HCR Output Format

The HCR output is an **annual table per hazard per scenario**, matching the team framework format:

```
HAYHURST SOLAR — SSP5-8.5

Hazard              2030   2031   ...   2040   ...   2050
─────────────────   ─────  ─────       ─────       ─────
Heat stress          0.11   0.11  ...   0.19   ...   0.23
Flood (extreme pr)   0.21   0.20  ...   0.02   ...   0.00
Freeze-thaw         -0.05  -0.05  ...  -0.08   ...  -0.10
Soiling/dust         0.00   0.00  ...   0.05   ...   0.14
Fire weather         0.05   0.05  ...   0.09   ...   0.14
Icing               -0.08  -0.08  ...  -0.12   ...  -0.15

Notes:
  - Negative values = hazard DECREASING (benefit)
  - Flood HCR falls as precipitation shifts to drying post-2040
  - Soiling HCR rises as drying intensifies
  - Heat stress grows monotonically
```

```
MAVERICK WIND — SSP5-8.5

Hazard              2030   2031   ...   2040   ...   2050
─────────────────   ─────  ─────       ─────       ─────
Heat stress          0.08   0.08  ...   0.14   ...   0.17
Wind structural      0.00   0.00  ...   0.00   ...   0.00
Icing               -0.12  -0.12  ...  -0.18   ...  -0.22
Cut-out events       0.00   0.00  ...   0.00   ...   0.00
Flood (access)       0.15   0.14  ...   0.02   ...   0.00

Notes:
  - sfcWind SCVR ≈ 0 → wind structural and cut-out HCRs = 0
  - Icing strongly negative = significant benefit
  - This is WHY wind is ~10× less climate-impaired than solar
```

### Parquet Schema for NB04 Output

```
Columns:
  site_id:    string    ("hayhurst_solar", "maverick_wind")
  scenario:   string    ("ssp245", "ssp585")
  year:       int       (2026, 2027, ..., 2055)
  hazard:     string    ("heat_stress", "flood", "freeze_thaw", ...)
  hcr:        float     (signed — negative = hazard decreasing)
  scvr_input: float     (the SCVR value used as input)
  scaling:    float     (the scaling factor applied)
  confidence: string    ("validated", "working_estimate", "preliminary")
```

---

## 9. Sensitivity Analysis — The Biggest Uncertainty

The HCR scaling factors are the **most uncertain parameters** in the SCVR→NAV chain. The physics models downstream (Peck's, Coffin-Manson) have well-established equations — but the climate-to-hazard amplification is where the real uncertainty lives.

### Heat Scaling Sensitivity

```
HAYHURST SOLAR NAV IMPAIRMENT vs HEAT SCALING FACTOR

  SCVR_tasmax (2040) = 0.074  (fixed — from climate models)

  Scaling = 2.0:   HCR = 0.148   NAV impact ≈ $4.2M  (7.0%)
  Scaling = 2.5:   HCR = 0.185   NAV impact ≈ $5.9M  (9.8%)  ← base case
  Scaling = 3.0:   HCR = 0.222   NAV impact ≈ $7.8M  (13.0%)

  Range: $4.2M — $7.8M  (factor of 1.9× between low and high)

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

  A ±0.5 change in scaling factor moves NAV impairment by ~±$1.5-2M.
  This is a significant source of uncertainty.
```

### Why This Matters for NB04

The scaling factors should be:
1. **Calibrated** where possible — compare annual hazard counts from NB01 climate indices against SCVR predictions
2. **Bounded** by physical constraints — Clausius-Clapeyron sets an upper bound for precipitation; tail statistics set bounds for temperature
3. **Reported with ranges** — present NAV under low/mid/high HCR assumptions
4. **Updated** as more literature and observational data become available

---

## 10. Connection to NB01 Climate Indices

Notebook 01 already computes **annual hazard counts** as climate indices. These are the same quantities that HCR measures:

```
NB01 ANNUAL INDICES           HCR HAZARD           RELATIONSHIP
──────────────────            ──────────            ────────────
heat_wave_days(t)      →     Heat stress      →    HCR ≈ (future - baseline) / baseline
frost_days(t)          →     Freeze-thaw      →    HCR = (future - baseline) / baseline
rx5day(t)              →     Flood risk       →    HCR ≈ (future - baseline) / baseline
fwi_mean(t)            →     Fire weather     →    HCR = (future - baseline) / baseline
```

This means NB04 has **two pathways** to compute HCR:

```
PATHWAY A: SCVR × Scaling (parametric)
  + Fast to compute
  + Consistent with SCVR framework
  + Works even without annual index data
  − Depends on scaling factor estimates

PATHWAY B: Direct Index Comparison (empirical)
  + Uses actual hazard counts (no scaling factor needed)
  + More physically grounded
  + NB01 already has the infrastructure
  − Requires full daily data processing per year
  − Annual hazard counts can be noisy (need multi-model averaging)

RECOMMENDED: Use both. Cross-validate Pathway A against Pathway B.
Where they agree, confidence is high.
Where they disagree, investigate the scaling factor.
```

### Calibrating Scaling Factors Using NB01 Data

```
Example — calibrating heat stress scaling:

1. From NB01, get annual heat_wave_days for baseline and future
   Baseline mean: 15 heat wave days/year
   Future mean (2040 window): 18 heat wave days/year
   Empirical HCR_heat = (18 - 15) / 15 = +0.20

2. From NB03, get SCVR_tasmax = 0.074

3. Implied scaling = HCR / SCVR = 0.20 / 0.074 = 2.7

   Close to our working estimate of 2.5 — validates the assumption.
   If it came out at 4.0, we'd need to revise.
```

---

## 11. Open Questions for NB04 Implementation

### Priority Research Needed

| Question | Impact | Approach |
|----------|--------|----------|
| Are heat scaling factors region-specific? | HIGH | Compare Hayhurst vs Maverick implied scaling |
| How to handle pr sign inversion for flood HCR? | MEDIUM | Separate wet-tail from dry-tail analysis |
| Is FWI computable from NEX-GDDP variables? | MEDIUM | Implement simplified Canadian FWI |
| Compound event interaction terms? | LOW (Phase 2) | Literature review — start with Zscheischler et al. |
| Non-linear HCR (power law)? | LOW (Phase 2) | Need more sites for calibration data |

### Implementation Decisions for NB04

1. **Annual SCVR prerequisite:** NB04 needs annual SCVR values from NB03. NB03 currently computes SCVR at 5 discrete target years with 20-year rolling windows. This needs refactoring to annual computation before NB04 can proceed (see `docs/todo.md`).

2. **Which scaling factors to use:** Start with the working estimates in the table above. Cross-validate against NB01 climate indices. Report results with low/mid/high scaling scenarios.

3. **Negative HCR handling:** Allow negative HCR values (hazard decreasing). These create NAV upsides that partially offset other impairments.

4. **Per-hazard vs aggregate HCR:** Compute HCR per hazard separately, then combine at the EFR/NAV stage. Do not aggregate HCR values across hazards — they feed into different EFR models.

---

## 12. Common Misconceptions

| You might think... | But actually... |
|---|---|
| HCR = SCVR (they're the same thing) | No — SCVR measures distribution shift; HCR measures hazard change. A +8% distribution shift can cause +21% more heat hazard (2.5× amplification) |
| HCR scaling factors are known precisely | No — they are the biggest uncertainty in the chain. The range between low and high estimates can change NAV by ±$2M |
| All hazards increase with warming | No — frost days, icing events, and cold waves decrease. HCR can be negative (a financial benefit) |
| HCR is constant over time | No — HCR(t) varies each year as SCVR(t) evolves. It maps directly to annual CFADS adjustments |
| Compound events are simply additive | No — interacting hazards can amplify each other non-linearly. Phase 1 treats them as additive (conservative simplification) |
| HCR tells you the dollar impact | No — HCR tells you hazard change. The dollar impact comes from combining HCR with equipment models (EFR, doc 08) and financial models (NAV, doc 09) |
| sfcWind SCVR ≈ 0 means wind farms have no climate risk | Not exactly — wind farms still face heat stress, icing changes, and flood risk through other variables. But the dominant structural fatigue pathway is unaffected |

---

## Next

- [08 - EFR: Equipment Failure & Degradation](08_efr_equipment_degradation.md) — The engineering models that translate HCR into physical equipment degradation
- [09 - NAV Impairment Chain](09_nav_impairment_chain.md) — The complete annual pipeline from SCVR to dollar impairment
- [04 - SCVR Methodology](04_scvr_methodology.md) — How SCVR is computed (the input to this doc)

Return to [Index](00_index.md) for the full learning guide table of contents.
