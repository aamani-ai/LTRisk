---
title: "Discussion — How Should Annual SCVR Values Be Computed?"
type: discussion
domain: climate-risk / methodology
created: 2026-03-09
status: draft — experiment complete, needs team decision before NB03 refactoring
context: >
  The team framework shows annual SCVR tables (2030, 2031, ..., 2050) and the
  downstream chain (HCR, EFR, IUL, NAV) consumes annual values. But the framework
  does not specify HOW to compute SCVR per year. This doc lays out the options,
  tradeoffs, and a recommendation so the team can make a concrete decision before
  any NB03 refactoring or NB04 implementation begins.
relates-to:
  - docs/learning/B_scvr_methodology/04_scvr_methodology.md
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/learning/C_financial_translation/09_nav_impairment_chain.md
  - docs/background/drive_docs/LT Risk Evolution Framework.md
  - docs/implementation/03_integrated_scvr_cmip6.md
  - docs/todo.md
---

# Discussion — How Should Annual SCVR Values Be Computed?

> **The question:** The team framework expects annual SCVR(t) for each year
> 2030–2050 (one value per variable per scenario per year). NB03 currently
> computes one SCVR per (variable, scenario) using the full 30-year future window.
> How do we produce annual values? And is annual SCVR even the right framing?

> **Why this matters:** Every downstream step — HCR(t), EFR(t), IUL,
> CFADS adjustment, NAV impairment — depends on having annual SCVR values.
> The method we choose here determines the quality and meaning of everything
> that follows.

> **Decision needed before:** Any NB03 refactoring or NB04 implementation.

---

## 1. What the Team Framework Says

The framework doc (`LT Risk Evolution Framework.md`, Step 1) shows this table:

```
| RCP4.5     | 2030 | 2031 | …. | 2040 | …. | 2050 |
|------------|------|------|-----|------|-----|------|
| Temp SCVR  |      |      |     |      |     |      |
| Wind SCVR  |      |      |     |      |     |      |
| ……         |      |      |     |      |     |      |
```

And says: *"Display graphs and tables showing annual evolution of these SCVR
and Climate variables."*

The HCR and EFR tables follow the same annual format. The IUL formula
references *"the average of the product of EFR and SCVR across all years"*.

**What the framework does NOT specify:** How to compute a single SCVR value
for a single year. It shows the desired output format but not the computation
method.

---

## 2. What SCVR Actually Needs

SCVR is defined as:

```
SCVR = (area_future - area_baseline) / area_baseline

where area = trapezoid integral of daily values sorted descending
             over exceedance probability [0, 1]
```

This requires two sets of daily values:

```
BASELINE:  Always the same — 30 years (1985-2014) × 6 models = ~65,700 daily values
FUTURE:    The question — how many daily values define "a year"?
```

The baseline is fixed and robust (65,700 values → smooth exceedance curve).
The challenge is defining the future pool for each individual year.

### Why This Is Hard

```
SIGNAL vs NOISE — THE CORE PROBLEM

  Climate signal:    ~0.03°C/year warming trend (gradual, smooth)
  Weather noise:     ±5-10°C day-to-day, ±1-2°C year-to-year
  Signal-to-noise:   Very low for a single year

  To detect a 0.03°C/year signal, you need enough data to average
  out the ±5-10°C daily weather noise. One year (365 days) is marginal.
  Ten years (3,650 days) is much better. Thirty years (10,950 days) is solid.

  But if you use 30 years to estimate SCVR for "year 2040", you're
  averaging climate from 2026-2055 — you no longer have a value
  specific to 2040.
```

This is the fundamental tension: **precision per year** vs **statistical robustness**.

---

## 3. What the Notebooks Currently Do

### NB03 (current production notebook)

NB03 computes **one SCVR per (variable, scenario)** using the full 30-year
asset lifetime as the future window:

```
Baseline:  1985-2014  (30 years × 6 models = ~65,700 daily values)
Future:    2026-2055  (30 years × 6 models = ~65,700 daily values)

→ ONE SCVR value per variable per scenario
→ center_year = 2040 (midpoint of 2026-2055)
→ Output: cmip6_ensemble_scvr.parquet (14 rows for Hayhurst, 12 for Maverick)
```

**Strengths:**
- Maximum pool size → very smooth, robust exceedance curves
- Captures full daily distribution shape (tails, extremes)
- Correct for "how much does the ENTIRE future differ from baseline?"

**Limitation:**
- One value — no temporal evolution at all. Cannot populate the annual table.

### NB01 (prototype, single-model)

NB01 used 20-year rolling windows at 5 target years (2030, 2035, 2040, 2045, 2050):

```
Target year   Window           Pool size (1 model)
──────────────────────────────────────────────────────
2030          2020-2040        20 yrs × 365 = ~7,300 daily values
2035          2025-2045        ~7,300
2040          2030-2050        ~7,300 (clipped to 2049)
2045          2035-2049        ~5,475 (clipped)
2050          2040-2049        ~3,650 (clipped)
```

This gave temporal evolution (5 snapshots) but with heavy overlap (75%)
and only 1 model. NB03 abandoned this in favour of the full-window approach.

### The gap

Neither notebook produces the annual SCVR table the team framework expects.
NB03 gives one robust value. NB01 gave 5 overlapping snapshots. We need 30
annual values.

---

## 4. The Three Options

### Option A: Per-Year SCVR (1 year of future data per SCVR value)

```
METHOD:
  For each year t in [2026, 2027, ..., 2055]:
    future_pool = daily values from year t across all models
    SCVR(t) = compute_scvr(baseline_pool, future_pool)

POOL SIZE:
  365 days × 6 models = ~2,190 values per year
  (or 365 × 34 models = ~12,410 if using all available models)

RESULT:
  30 individual SCVR values, one per year
```

```
WHAT THE OUTPUT LOOKS LIKE (tasmax, SSP5-8.5, illustrative)

  SCVR
  0.20 │
       │                              *      *        *
  0.15 │              *   *       *      *       *
       │     *    *         *  *     *                 *
  0.10 │  *    *     *                                    *
       │                *
  0.05 │        *
       │
  0.00 └──────────────────────────────────────────────────────
       2026  2030       2035       2040       2045       2050

  Note: Very noisy. Individual years dominated by weather, not climate.
  A cold La Niña year could show SCVR < 0 even within a warming trend.
```

**Pros:**
- Genuinely annual — each value represents one year
- No autocorrelation between adjacent years
- Simple to explain: "SCVR in 2035 uses 2035's weather"

**Cons:**
- ~2,190 values is marginal for a stable exceedance curve
- Single-year weather dominates over climate signal
- Result is noisy — year-to-year jumps of ±50% are normal
- A single anomalous year (El Niño, La Niña) creates misleading SCVR
- Feeding noisy SCVR into HCR and EFR amplifies the noise
- Physical nonsense: climate doesn't actually change year-to-year like this

**Risk to downstream chain:**
```
If SCVR(2035) = 0.15 and SCVR(2036) = 0.05 (because 2036 was a cool year):
  HCR(2035) = 0.15 × 2.5 = 0.375
  HCR(2036) = 0.05 × 2.5 = 0.125

This implies hazard risk DROPPED 67% in one year. Physically wrong —
hazard risk tracks climate trend, not weather variability.
```

**Mitigation (if choosing this option):**
- Use all 34 models instead of 6 → 12,410 values per year (better statistics)
- Apply post-hoc smoothing (e.g., LOESS, running median) to the annual series
- But then you're smoothing after computing — adding a step that could be
  avoided by using a better computation method upfront

**Assessment: Not recommended.** The noise level makes raw per-year SCVR
unsuitable for the downstream chain. Post-hoc smoothing partially fixes it
but introduces its own questions (what kernel? what bandwidth?).

---

### Option B: Rolling Window (overlapping windows, 1 per year)

```
METHOD:
  For each year t in [2026, 2027, ..., 2055]:
    window = [t-W, t+W]  where W = half-window (e.g., 5 or 10 years)
    future_pool = daily values from window across all models
    SCVR(t) = compute_scvr(baseline_pool, future_pool)

POOL SIZE (W=5, 10-year window):
  10 yrs × 365 days × 6 models = ~21,900 values per year

POOL SIZE (W=10, 20-year window):
  20 yrs × 365 days × 6 models = ~43,800 values per year

RESULT:
  30 SCVR values, one per year — but adjacent values share most data
```

```
AUTOCORRELATION PROBLEM (W=5, 10-year window)

  Year 2035: window = 2030-2040      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  Year 2036: window = 2031-2041      ░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░

  Shared data: 9 out of 10 years = 90% overlap

  The SCVR "change" from 2035 to 2036 is driven almost entirely by:
    - Dropping year 2030 from the window
    - Adding year 2041 to the window
  Both are single years — so you're back to single-year noise,
  just spread across the denominator of a large window.

  Result: an artificially smooth curve that LOOKS like a clean trend
  but is actually the same noisy data viewed through a heavy smoother.
```

```
WHAT THE OUTPUT LOOKS LIKE (W=5, tasmax, SSP5-8.5)

  SCVR
  0.15 │
       │                                        ╭────────╮
  0.10 │                           ╭────────────╯
       │              ╭────────────╯
  0.05 │  ╭───────────╯
       │──╯
  0.00 └──────────────────────────────────────────────────────
       2026  2030       2035       2040       2045       2050

  Looks smooth and clean. But the smoothness is an artifact of
  90% data overlap, not a real signal. The "trend" is real (physics
  guarantees it), but the RATE shown is not meaningfully different
  from a simple linear interpolation between anchors.
```

**Pros:**
- Produces smooth annual series (looks like what the team framework expects)
- Each value has large pool size → stable exceedance curves
- Captures daily distribution shape including tails
- Minimal code change from NB03's current approach (just more target years)

**Cons:**
- Autocorrelation: adjacent years share 80-90% of data
- The annual "evolution" is largely artificial smoothing, not new information
- Edge effects: early/late years have asymmetric or truncated windows
- Window size choice is arbitrary (W=5? W=7? W=10?)
- Creates false precision — 30 highly correlated values contain roughly
  the same information as 3-5 independent estimates
- If someone computes uncertainty intervals, they'd need to account for
  the correlation structure (non-trivial)

**Assessment: Works but is misleading.** It produces the output format
the team framework expects, but the appearance of smooth annual evolution
overstates the actual information content. The 30 values contain roughly
3-5 independent pieces of information, dressed up as 30.

---

### Option C: Anchor Points + Fitted Curve

```
METHOD:
  Step 1 — Compute SCVR at non-overlapping "anchor" windows:
    Anchor 1: 2026-2035 (10 years)  → SCVR_1, assigned to midpoint 2030.5
    Anchor 2: 2036-2045 (10 years)  → SCVR_2, assigned to midpoint 2040.5
    Anchor 3: 2046-2055 (10 years)  → SCVR_3, assigned to midpoint 2050.5

  Step 2 — Fit a smooth curve through the anchors:
    f(t) = a + b×t  (linear)
    or
    f(t) = a + b×t + c×t²  (quadratic — if 4+ anchors)

  Step 3 — Read off annual values:
    SCVR(t) = f(t)  for each year t in [2026, 2027, ..., 2055]

POOL SIZE PER ANCHOR:
  10 yrs × 365 days × 6 models = ~21,900 values (robust)

RESULT:
  3 independent anchor points → fitted to 30 annual values
```

```
WHAT THE OUTPUT LOOKS LIKE (tasmax, SSP5-8.5)

  SCVR
  0.15 │
       │                                      ╱─── fitted curve
  0.10 │                        ●────────────╱     (linear or quadratic)
       │              ╱─────────
  0.05 │  ●──────────╱
       │ ╱            ●  = anchor point (independent, non-overlapping)
  0.00 └──────────────────────────────────────────────────────
       2026  2030       2035       2040       2045       2050

  Three robust anchor points. The curve between them is an explicit
  assumption (linear trend) — transparent, not hidden in data overlap.
```

```
WHY ANCHORS ARE INDEPENDENT

  Anchor 1: 2026-2035  ▓▓▓▓▓▓▓▓▓▓
  Anchor 2: 2036-2045              ▓▓▓▓▓▓▓▓▓▓
  Anchor 3: 2046-2055                          ▓▓▓▓▓▓▓▓▓▓

  Zero overlap. Each anchor uses completely different years.
  The three SCVR values are statistically independent estimates.
  Any trend between them is genuine climate evolution, not smoothing artifact.
```

**Pros:**
- Each anchor is statistically independent (zero data overlap)
- Large pool per anchor (~21,900 values) → robust exceedance curves
- The interpolation assumption is explicit — you KNOW you're fitting a line
- Transparent about information content: "we have 3 independent measurements,
  the rest is interpolation"
- Easy to add uncertainty bands: bootstrap each anchor → propagate to curve
- Physically appropriate: climate evolves smoothly, so linear/quadratic
  interpolation is well-justified over 30 years

**Cons:**
- Only 3 independent data points — limited ability to detect non-linear trends
- The interpolation IS an assumption (though a well-justified one for climate)
- Slightly more complex to implement than Option B (fit step)
- Mid-decade detail is interpolated, not measured
- If the actual trend has a kink or step change, 3 anchors won't capture it

**Possible enhancements:**
- Use 5-year anchors (6 independent points) instead of 10-year (3 points)
  - Pool: 5 × 365 × 6 = ~10,950 values — still decent for exceedance curves
  - But noisier per anchor
- Use all 34 models (×34 instead of ×6) → each anchor has ~124,100 values
  - Even 5-year anchors with 34 models give ~63,875 values — very robust
  - This is the strongest variant

**Assessment: Recommended.** Honest about what we know (3 robust estimates)
vs what we assume (smooth interpolation between them). Avoids the statistical
traps of Options A and B while producing the annual format the framework needs.

---

## 5. Head-to-Head Comparison

```
                        Option A          Option B          Option C
                        Per-Year          Rolling Window    Anchor + Fit
────────────────────────────────────────────────────────────────────────
Pool size per value     ~2,190            ~21,900           ~21,900 (per anchor)
Independent estimates   30                ~3-5 (effective)  3 (explicit)
Autocorrelation         None              Very high (90%)   None
Noise level             High              Low (artificial)  Low (genuine)
Output format           Annual ✓          Annual ✓          Annual ✓
Tail capture            Marginal          Good              Good
Transparency            High              Low               High
Implementation effort   Low               Low               Medium
Uncertainty bands       Easy (but wide)   Hard (correlated) Easy

INFORMATION CONTENT:
  All three options contain roughly the same amount of climate
  information — because the climate signal evolves slowly.
  The difference is how honestly each presents that information.

  Option A: honest but too noisy to use
  Option B: usable but hides the smoothing in data overlap
  Option C: usable AND transparent about the interpolation
```

---

## 6. What About Using All 34 Models?

NB03 currently caps at 6 models per variable/scenario combination (MAX_MODELS=6).
NEX-GDDP-CMIP6 has 34 models. Using all 34 changes the calculus:

```
POOL SIZES WITH 34 MODELS

  Option A (per year):    365 × 34 = 12,410 values/year    (decent)
  Option B (10yr window): 3,650 × 34 = 124,100 values      (excellent)
  Option C (10yr anchor): 3,650 × 34 = 124,100 values      (excellent)
  Option C (5yr anchor):  1,825 × 34 = 62,050 values       (very good)
```

With 34 models, even Option A becomes more defensible (12,410 values gives a
reasonable exceedance curve). And Option C with 5-year anchors gives 6
independent points with 62,050 values each — arguably the best of all worlds.

**However:** Using all 34 models introduces model spread as an additional
source of variation. Some models are known to run warm or cold. Ensemble
pooling assumes all models are exchangeable — this assumption gets weaker
as you add more diverse models. NB03's current 6-model cap was a pragmatic
choice (faster, fewer data quality issues). Lifting it needs testing.

**Recommendation:** Start with 6 models and Option C (3 anchors). If the
anchor SCVRs are noisy, expand to 34 models and/or 6 anchors (5-year windows).

---

## 7. How Does This Affect the Downstream Chain?

The learning docs (07 HCR, 08 EFR, 09 NAV) describe what happens GIVEN
annual SCVR values. The chain formulas are correct regardless of which
option produces the annual values:

```
SCVR(t) → HCR(t) = SCVR(t) × scaling_factor     [doc 07]
HCR(t)  → EFR(t) = f(HCR, Peck's, C-M, P-M)     [doc 08]
EFR(t)  → Gen(t) adjusted → CFADS(t) → NAV        [doc 09]
```

What changes is the **character** of the annual SCVR series:

```
                    Option A             Option C
                    (per year)           (anchor + fit)
──────────────────────────────────────────────────────────
SCVR(2035)          0.08 (noisy)        0.065 (smooth)
SCVR(2036)          0.04 (dropped!)     0.068 (smooth)
SCVR(2037)          0.11 (jumped!)      0.071 (smooth)

HCR_heat(2035)      0.20                0.163
HCR_heat(2036)      0.10 (halved!)      0.170
HCR_heat(2037)      0.28 (tripled!)     0.178

EFR(2035)           jumpy               smooth progression
EFR(2036)           jumpy               smooth progression
```

Option A's noise propagates and amplifies through HCR (×2.5 scaling)
and EFR (non-linear Peck's model). Option C's smooth interpolation
produces physically reasonable monotonic progression.

**The team framework's IUL formula also favours smooth inputs:**

```
IUL = EUL × (1 - Σ(EFR(t) × SCVR(t)) averaged across all years)

With noisy inputs:  the average washes out the noise → same result
With smooth inputs: each year's contribution is meaningful → same result

The AVERAGE is the same either way (the mean of noise is the mean of
the underlying signal). But the annual BREAKDOWN is only meaningful
with smooth inputs.
```

---

## 8. What Does the Climate Science Say?

### 8.1 Climate Evolves Smoothly

The forced climate response (the part we're measuring with SCVR) evolves
on multi-decadal timescales:

```
CO2 concentration:   Smooth increase (~2.5 ppm/yr under SSP5-8.5)
Radiative forcing:   Smooth logarithmic function of CO2
Temperature response: Smooth, with ~10-year lag to equilibrium
SCVR (distribution):  Should follow temperature response — smooth

Year-to-year:  Natural variability (ENSO, NAO, volcanic aerosols)
               adds ±0.1-0.3°C noise on the smooth ~0.03°C/yr trend
```

This means a smooth annual SCVR curve is **more physically correct** than
a noisy one. The noise in Option A is real weather variability, but it's
not the climate signal that SCVR is designed to measure.

### 8.2 Precedent in Climate Science

Climate scientists routinely face this same problem. Standard approaches:

```
COMMON APPROACHES IN CLIMATE LITERATURE

  1. Running means (20-year or 30-year)
     → Used by IPCC for defining "climate normals"
     → Equivalent to our Option B
     → Acknowledged to have autocorrelation; used anyway because
        the alternative (per-year) is too noisy

  2. Trend fitting (linear or polynomial)
     → Used in detection-and-attribution studies
     → Equivalent to our Option C
     → Explicit about the smoothness assumption

  3. Epoch differences (non-overlapping blocks)
     → Used by IPCC for scenario comparison (2021-2040 vs 2041-2060)
     → Equivalent to our Option C anchors (without the interpolation)
     → Gives robust estimates but not annual values

  4. Generalized additive models (GAMs)
     → Used in modern trend detection
     → More sophisticated version of Option C
     → Over-engineered for our use case (3 anchors → simple line is fine)
```

The climate community uses Options B and C depending on context. Option A
(raw annual values) is used for time series analysis but NOT for computing
derived metrics like exceedance shifts — too noisy.

---

## 9. The Recommendation

### Primary: Option C with 10-Year Anchors

```
RECOMMENDED APPROACH

  Step 1: Compute 3 anchor-point SCVRs (non-overlapping, 10-year windows)
          Anchor 1: 2026-2035 → SCVR_early   (midpoint ~2030)
          Anchor 2: 2036-2045 → SCVR_mid     (midpoint ~2040)
          Anchor 3: 2046-2055 → SCVR_late    (midpoint ~2050)

  Step 2: Fit linear curve through the 3 anchors
          f(t) = α + β × (t - 2026)

  Step 3: Read off annual values
          SCVR(2026) = f(2026), SCVR(2027) = f(2027), ..., SCVR(2055) = f(2055)

  Step 4: Report both:
          - The 3 anchor values (what we actually measured)
          - The 30 annual values (what we interpolated)
          - The fit parameters (α, β)
          - R² of the fit (how linear the trend actually is)
```

### Why Linear Interpolation Is Justified

```
Over a 30-year window (2026-2055):
  - CO2 increase is approximately linear (~2.5 ppm/yr, total ~75 ppm)
  - Radiative forcing is logarithmic in CO2, but linear in ΔCO2 for small changes
  - Temperature response is approximately linear for small forcing changes
  - SCVR tracks temperature → approximately linear

If the 3 anchors show strong curvature (SCVR_mid >> midpoint of SCVR_early
and SCVR_late), consider quadratic fit. But for most variables over 30 years,
linear is a good first approximation.
```

### Output Format

This produces exactly what the team framework expects:

```
| SSP5-8.5    | 2030  | 2031  | 2032  | ... | 2040  | ... | 2050  |
|-------------|-------|-------|-------|-----|-------|-----|-------|
| Temp SCVR   | 0.05  | 0.053 | 0.056 |     | 0.09  |     | 0.12  |
| Wind SCVR   | -0.01 | -0.01 | -0.01 |     | -0.01 |     | -0.01 |
| Precip SCVR | 0.04  | 0.04  | 0.03  |     | 0.02  |     | 0.01  |

With annotation:
  ● = anchor point (independently computed from non-overlapping window)
  ○ = interpolated from linear fit through anchors
```

### Fallback: Option C with 5-Year Anchors + 34 Models

If 10-year anchors with 6 models prove too coarse (e.g., the 3 points
don't clearly define a trend), expand to:

```
FALLBACK APPROACH

  6 anchors × 5-year windows:
    2026-2030  →  SCVR(~2028)
    2031-2035  →  SCVR(~2033)
    2036-2040  →  SCVR(~2038)
    2041-2045  →  SCVR(~2043)
    2046-2050  →  SCVR(~2048)
    2051-2055  →  SCVR(~2053)

  Using all 34 models:
    5 × 365 × 34 = ~62,050 values per anchor (very robust)

  6 independent points allow quadratic or piecewise-linear fit.
```

---

## 10. Does This Deviate from the Team's Path?

**No.** The team framework specifies the OUTPUT format (annual table) and the
downstream FORMULAS (HCR = SCVR × factor, EFR = f(Peck's, ...), etc.). It does
not specify the computation method for producing annual SCVR values.

```
WHAT THE TEAM FRAMEWORK DEFINES:
  ✓ Annual SCVR table format (2030, 2031, ..., 2050)
  ✓ HCR = f(SCVR, scaling_factors)
  ✓ EFR = f(Peck's, Coffin-Manson, Palmgren-Miner)
  ✓ IUL = EUL × (1 - avg(EFR × SCVR))
  ✓ NAV impairment = NPV(base) - NPV(climate)

WHAT THE TEAM FRAMEWORK DOES NOT DEFINE:
  ✗ How to compute SCVR for a single year
  ✗ Window size for future pool
  ✗ Whether to use rolling windows, anchors, or per-year
  ✗ How many models to include in the ensemble
```

Option C fills in the computation method while producing the exact output format
the framework expects. The annual SCVR table, the HCR table, the EFR table —
all look identical regardless of whether the values came from Option A, B, or C.

The only change is that Option C is **transparent** about where the annual values
come from: 3 robust measurements + linear interpolation, rather than 30 values
that appear independent but aren't.

---

## 11. Implementation Impact on NB03

### Current NB03 → Option C

```
WHAT CHANGES IN NB03

  CURRENT:
    future_start = 2026
    future_end   = 2055
    → Pool ALL 30 years into one future pool
    → ONE SCVR per variable/scenario (center_year = 2040)

  OPTION C:
    ANCHORS = [
      (2026, 2035),   # Anchor 1: early decade
      (2036, 2045),   # Anchor 2: mid decade
      (2046, 2055),   # Anchor 3: late decade
    ]
    → 3 non-overlapping SCVR anchor values
    → Linear fit → 30 annual values

  CODE CHANGE:
    - The DATA dict already has all daily values for 2026-2055 per model
    - Add a loop that slices each model's daily Series by anchor window
    - Call compute_scvr() 3 times instead of once (same function, different slices)
    - Add np.polyfit(anchor_midpoints, anchor_scvrs, deg=1) (3 lines)
    - Add np.polyval(fit, np.arange(2026, 2056)) (1 line)
    - Update Parquet output to include both anchors and annual values
    - Update plots: show anchor points + fitted line
    - Keep existing full-window SCVR as a "period SCVR" for backward compatibility

  EFFORT: Small. The SCVR computation function is unchanged.
  The data is already fetched. We just slice it differently.
```

### What NB04 Receives

```
FROM NB03 (Option C):
  - scvr_anchors.parquet:   3 rows per variable × scenario
  - scvr_annual.parquet:    30 rows per variable × scenario (interpolated)
  - fit_parameters.json:    α, β, R² per variable × scenario

NB04 USES:
  - scvr_annual.parquet for HCR(t) = SCVR(t) × scaling_factor
  - The annual values feed directly into the framework's annual tables
```

---

## 12. What We Are NOT Changing

To be explicit about what stays the same:

```
UNCHANGED:
  ✓ SCVR formula: (area_future - area_baseline) / area_baseline
  ✓ Exceedance curve: daily values sorted descending, trapezoid integral
  ✓ Baseline: 1985-2014 (30 years, same for all computations)
  ✓ Ensemble pooling: concatenate daily values across models (not average)
  ✓ Daily data: no annual aggregation before SCVR computation
  ✓ Output: one SCVR per variable × scenario × year
  ✓ Downstream chain: HCR, EFR, IUL, NAV formulas all unchanged
  ✓ Team framework output format: annual tables
```

The only thing that changes is the **windowing strategy** for the future pool.

---

## 13. Open Questions for Team Discussion

1. **Do we need sub-decadal resolution in the early years?**
   If the financial model only needs SCVR at years 5, 10, 15, 20, 25
   (not every single year), even the 3-anchor approach gives more detail
   than needed. Is true annual resolution required, or is "annual-resolution
   via interpolation" sufficient?

2. **How many models?**
   Current: 6 models (fastest available per variable/scenario).
   Option: all 34 models (more robust but slower fetch, larger cache).
   Decision affects pool size and therefore anchor window size.

3. **Linear vs quadratic fit?**
   With 3 anchors, linear is the only option. With 5-6 anchors (5-year windows),
   quadratic becomes possible. Is the potential non-linearity worth the extra
   anchors?

4. **Should we report the fit quality (R²)?**
   If R² is low (anchors don't fall on a line), that itself is information —
   it suggests the SCVR evolution is not smooth, which would warrant investigation.

5. **Does the IUL formula care about annual detail?**
   The formula `IUL = EUL × (1 - avg(EFR × SCVR))` averages over all years.
   A smooth trend and a noisy series with the same mean give the same IUL.
   But the annual HCR-driven BI losses DO care about year-by-year values.
   Which use case drives the resolution requirement?

6. **Empirical vs parametric exceedance at anchor pool sizes?**
   Doc 04 argues empirical exceedance is sufficient at n=65,700 (full window).
   With anchors, n drops to ~21,900 (10-year) or ~10,950 (5-year).
   The body of the distribution is still well-covered, but tail percentiles
   (99th+) get rougher. Does this matter for SCVR (an area/mean metric)?
   Should we test empirical vs GEV-fitted SCVR at different pool sizes?
   See Section 14.6 for analysis.

---

## 14. Experimental Evidence (2026-03-10)

> **Script:** `scripts/experiments/annual_scvr_test.py`
> **Data:** Hayhurst Solar, SSP5-8.5, 6 models, cached NEX-GDDP-CMIP6 data
> **Plots:** `scripts/experiments/output/annual_scvr_comparison_<var>_ssp585.png`
>
> **Follow-up:** The variable-specific strategy, decade analysis, and shape metrics were
> implemented in NB03 and the presentation script based on these results.
> See [discussion_decade_shape_analysis.md](discussion_decade_shape_analysis.md) for
> the full decade-resolved analysis, team feedback response, and first results with 13 models.

We ran the experiment described in Section 4 for all 7 climate variables,
computing SCVR four ways (per-year, 3-anchor, 6-anchor, full-window) using
real cached data. Results below.

### 14.1 Cross-Variable Summary

```
Variable    Mean     Std    Noise/Sig  Neg_Yrs  R²(3)   R²(6)   Verdict
─────────────────────────────────────────────────────────────────────────────
tasmax     0.0833   0.0279     0.33       0     0.972   0.972   Strong linear ✓
tasmin     0.1636   0.0477     0.29       0     0.985   0.951   Strong linear ✓
tas        0.0992   0.0327     0.33       0     0.982   0.959   Strong linear ✓
pr         0.0124   0.1123     9.05      16     0.589   0.593   Non-linear, noisy ✗
sfcWind   -0.0112   0.0145     1.29      25     0.131   0.101   No signal ✗
hurs      -0.0425   0.0413     0.97      25     0.668   0.614   Weak signal ~
rsds       0.0005   0.0044     8.40      14     0.308   0.168   No signal ✗

Columns:
  Mean      = mean of 30 per-year SCVR values
  Std       = standard deviation of per-year SCVR
  Noise/Sig = Std / |Mean|  (lower = cleaner signal)
  Neg_Yrs   = how many of 30 years have SCVR < 0
  R²(3)     = R² of linear fit through 3 non-overlapping 10-year anchors
  R²(6)     = R² of linear fit through 6 non-overlapping 5-year anchors
```

### 14.2 Three Variable Categories

The results split cleanly into three groups:

**Category 1 — Temperature (tasmax, tasmin, tas): Anchor approach works excellently**

```
  Per-year SCVR (tasmax, SSP5-8.5):

    0.14 │           *            *     *             *   *
         │  *    *       *  *  *     *     * *   *       *
    0.10 │     *     *                 *          *
         │*                                               *
    0.06 │              ─────── 3-anchor linear fit ───────
         │                     (R² = 0.97)
    0.02 └────────────────────────────────────────────────────
         2026     2032      2038      2044      2050

  • Noise-to-signal: 0.33 (low — climate signal dominates)
  • Zero negative years (warming always exceeds baseline)
  • 3 anchors ≈ 6 anchors — linear trend captures everything
  • Per-year scatter is visible but the trend is clear
  • CONCLUSION: 3 non-overlapping anchors + linear fit is ideal
```

**Category 2 — Precipitation (pr): Non-linear, anchor approach marginal**

```
  Per-year SCVR (pr, SSP5-8.5):

    0.20 │     *
         │  *
    0.10 │        *  *               *              *
    0.00 │────────────*──*──────*──────────*───*────────*──
         │                *  *     *     *        *
   -0.10 │                          *                  *
         │                                *
   -0.20 └────────────────────────────────────────────────────
         2026     2032      2038      2044      2050

  • Noise-to-signal: 9.05 (very high — weather dominates completely)
  • 16 of 30 years have negative SCVR
  • R²(3) = 0.59 — linear fit captures only 60% of anchor variation
  • Pattern: wetter early decades, drier later — possibly non-linear
  • CONCLUSION: Anchors don't fully capture precipitation's behavior.
    Consider: (a) quadratic fit if 6 anchors, (b) report anchors only
    without interpolation, or (c) use period-average SCVR (current NB03).
```

**Category 3 — Wind, radiation, humidity (sfcWind, rsds, hurs): No meaningful signal**

```
  Per-year SCVR (sfcWind, SSP5-8.5):

    0.02 │   *          *                          *
    0.01 │ *   *            *       *
    0.00 │──────*──*──────────*────────*───────*──────*────
   -0.01 │         *  *         *  *     *  *     * *
   -0.02 │                                     *
   -0.03 │              *                *
         └────────────────────────────────────────────────────
         2026     2032      2038      2044      2050

  • sfcWind: Mean SCVR = -0.011, R²(3) = 0.13 (no trend)
  • rsds:    Mean SCVR = 0.001,  R²(3) = 0.31 (no trend)
  • hurs:    Mean SCVR = -0.043, R²(3) = 0.67 (weak drying trend)
  • CONCLUSION: SCVR ≈ 0 for these variables. Anchor fit is meaningless
    because there's no signal to fit. For downstream chain: these variables
    contribute near-zero HCR, which is itself informative (wind/solar
    resource is climate-stable at this site).
```

### 14.3 What This Means for the Recommendation

The experiment **confirms Option C (anchor + fit) for temperature variables**
and reveals that a one-size-fits-all approach across all variables is wrong:

```
VARIABLE-SPECIFIC STRATEGY (UPDATED RECOMMENDATION)

  Temperature (tasmax, tasmin, tas):
    → Option C: 3 anchors + linear fit (R² > 0.95)
    → 3 anchors are sufficient; 6 anchors add no benefit
    → Per-year noise is manageable but unnecessary

  Precipitation (pr):
    → Option C with caution: 6 anchors + quadratic/piecewise fit
    → OR: Report period-average SCVR with uncertainty range
    → Linear interpolation is NOT appropriate (R² ≈ 0.6)

  Wind / Radiation / Humidity (sfcWind, rsds, hurs):
    → Report period-average SCVR ≈ 0 (current NB03 approach)
    → Annual computation adds noise, not information
    → Downstream: set HCR ≈ 0 for these hazards at this site
```

### 14.4 Key Takeaways

1. **The experiment justified the anchor approach for temperature** — the
   primary driver of physical risk. R² > 0.95 means 3 non-overlapping anchors
   capture the climate signal with high fidelity.

2. **Per-year SCVR is usable but noisier than needed.** Noise-to-signal of
   0.33 for temperature means the trend is visible in raw data, but anchors
   are cleaner and more defensible for downstream financial calculations.

3. **Precipitation needs special treatment.** The non-linear, high-noise
   behavior (R² = 0.59, noise-to-signal = 9.05) means neither per-year nor
   simple linear anchors are ideal. This is a known challenge in climate
   science — precipitation projections are inherently noisier than temperature.

4. **Some variables have no climate change signal at this site.** Wind speed
   and solar radiation SCVR ≈ 0, which is itself a useful finding: the
   resource is stable, and the risk comes from temperature, not generation.

5. **3 anchors ≈ 6 anchors for temperature.** No benefit to 5-year windows
   over 10-year windows when the underlying trend is strongly linear.

### 14.6 Empirical vs Parametric Exceedance at Anchor Pool Sizes

The SCVR methodology (doc 04, §3e) argues that empirical exceedance curves are
sufficient because n = 65,700. With the anchor method, the pool size per anchor
drops. Does this change the conclusion?

```
POOL SIZE BY METHOD

  Full window (NB03 now):    6 models × 30 yrs × 365 = ~65,700
  10-year anchor (Option C): 6 models × 10 yrs × 365 = ~21,900
  5-year anchor (variant):   6 models ×  5 yrs × 365 = ~10,950
  Per-year (Option A):       6 models ×  1 yr  × 365 =  ~2,190

  With 34 models:
  10-year anchor:           34 models × 10 yrs × 365 = ~124,100
  5-year anchor:            34 models ×  5 yrs × 365 =  ~62,050
```

**Why empirical still works for anchors:**

SCVR is an **area metric** (trapezoid integral = mean of the distribution), not a
tail statistic. The trapezoid error scales as O(1/n²):

```
  n = 65,700  →  error ≈ 2.3 × 10⁻¹⁰   (full window)
  n = 21,900  →  error ≈ 2.1 × 10⁻⁹    (10-year anchor)
  n = 10,950  →  error ≈ 8.3 × 10⁻⁹    (5-year anchor)
  n =  2,190  →  error ≈ 2.1 × 10⁻⁷    (per-year)

  All negligible. Trapezoid error is not the issue at any pool size.
```

The real question is **sampling variability** — whether the empirical exceedance
curve at lower N faithfully represents the underlying distribution. For the body
of the distribution (p = 0.1 to 0.9, where ~80% of the SCVR area sits), even
n = 2,190 is adequate. The tails (p < 0.01) get rough at low N — the 99th
percentile is estimated from ~22 points at n = 2,190.

But SCVR doesn't weight the tails specially. A GEV or gamma fit would smooth
the tails, but the integrated area (which is what SCVR measures) would barely
change because the tails contribute so little to the total area.

```
WHERE A PARAMETRIC FIT WOULD MATTER VS WHERE IT WOULDN'T

  Metric          Tail-sensitive?   Parametric needed at low N?
  ─────────────────────────────────────────────────────────────
  SCVR (area)     No (= mean)       No — empirical is sufficient
  CVaR (5%)       Yes               Yes — would benefit from GEV fit
  Return period   Yes (extreme)     Yes — EVT is the standard tool
  KS statistic    No (max gap)      No — empirical is standard
```

**Conclusion:** Empirical exceedance remains the right choice for SCVR at all
anchor pool sizes we'd realistically use (n ≥ 10,000). The argument in doc 04
holds — the only number that changes is n, and SCVR's area-based nature makes
it insensitive to tail roughness. If we later add tail-focused metrics (CVaR,
return periods) alongside SCVR, those would benefit from parametric fitting —
but that's a different metric, not a different SCVR.

**Potential validation experiment:** Compute SCVR two ways for the same anchor —
(a) empirical as now, (b) GEV-fitted exceedance curve — and compare. If the
values are within 1%, the empirical choice is confirmed. This has not been run
yet but would be straightforward to add to `scripts/experiments/annual_scvr_test.py`.

---

## 15. Summary

```
THE DECISION TREE (UPDATED WITH EXPERIMENTAL EVIDENCE)

  Q: Does the team framework specify HOW to compute annual SCVR?
  A: No — only the output format (annual table).

  Q: Can we compute SCVR for a single year directly?
  A: Yes — experiment shows noise-to-signal = 0.33 for temperature
     (usable) but 9.05 for precipitation (not usable).

  Q: Do anchors capture the signal?
  A: For temperature: YES — R² > 0.95, 3 anchors = 6 anchors.
     For precipitation: PARTIALLY — R² = 0.59, non-linear behavior.
     For wind/radiation: NO SIGNAL to capture (SCVR ≈ 0).

  Q: What's the cleanest approach?
  A: Variable-specific:
     - Temperature → 3 anchors + linear fit (confirmed by experiment)
     - Precipitation → 6 anchors + non-linear fit, or period average
     - Wind/radiation → period average SCVR ≈ 0 (no annual needed)

  Q: Does this deviate from the team's path?
  A: No. It fills in an unspecified computation method while producing
     the exact output format the framework requires.
```

**Next step:** Team reviews the experimental results (Section 14) and
decides on the variable-specific strategy. Once decided, NB03 refactoring
is straightforward (small code change), and NB04 implementation can proceed
with well-defined annual SCVR inputs.

**Evidence base:** `scripts/experiments/annual_scvr_test.py` (reproducible),
7 comparison plots in `scripts/experiments/output/`.

---

*This document should be reviewed before any NB03 refactoring begins.
See `docs/todo.md` for the implementation task list.*
