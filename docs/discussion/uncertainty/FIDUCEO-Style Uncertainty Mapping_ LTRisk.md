---
title: "FIDUCEO-Style Uncertainty Mapping: LTRisk"
type: discussion
domain: climate-risk / uncertainty / metrology
created: 2026-04-01
status: working document — equations are implemented unless otherwise noted
prepared-for: Tasnia Shahid, Maria Caffrey (NPL)
prepared-by: Divy Patel (InfraSure / Aamani)
relates-to:
  - docs/learning/B_scvr_methodology/04_scvr_methodology.md
  - docs/learning/C_financial_translation/07_hcr_hazard_change.md
  - docs/learning/C_financial_translation/08_efr_equipment_degradation.md
  - docs/learning/C_financial_translation/09_nav_impairment_chain.md
  - docs/discussion/hcr_financial/hcr_efr_boundary.md
  - docs/discussion/architecture/framework_architecture.md
---

# FIDUCEO-Style Uncertainty Mapping: LTRisk

**Prepared for:** Tasnia Shahid, Maria Caffrey (NPL)
**Prepared by:** Divy Patel (InfraSure / Aamani)
**Date:** April 2026
**Status:** Working document — equations are implemented unless otherwise noted

---

## Purpose

This document maps the uncertainty propagation through InfraSure's Long-Term Risk (LT Risk) framework using the FIDUCEO measurement function diagram approach. The framework translates CMIP6 climate projections into Net Asset Value (NAV) impairment estimates for renewable energy assets via a three-layer equation chain:

```
CMIP6 daily data → SCVR → HCR / EFR → CFADS adjustment → NAV impairment
```

Each layer is presented as a measurement function with its inputs, sensitivity coefficients, and uncertainty characterisation. The goal is to identify where uncertainty is well-characterised, where it amplifies, and where structural choices dominate.

---

## Framework Overview

The system has two independent financial channels fed by a common climate signal (SCVR):

```
                    SCVR(t)
                      |
          +-----------+-----------+
          |                       |
    Channel 1 (BI)          Channel 2 (EFR)
    Hazard events →         Climate stress →
    operational shutdown    equipment degradation
          |                       |
    HCR(t) per hazard       EFR(t) per mechanism
          |                       |
    BI_loss(t)              generation decline + IUL
          |                       |
          +-----------+-----------+
                      |
              CFADS_adjusted(t)
              = Revenue × (1 - EFR) - BI_loss - OpEx
```

---

## Layer 1: SCVR (Severe Climate Variability Rating)

**Status: Stable. Implemented in NB03. Equation will not change.**

### Measurement Function

```
SCVR = (mean_future − mean_baseline) / mean_baseline
```

This is a simple fractional change in distribution means. The exceedance curve area computation converges exactly to the sample mean at our pool sizes (~306,600 daily values per period), proven via the quantile representation theorem with trapezoid error O(1/n²) ≈ 10⁻¹¹.

Three independent computation methods — empirical trapezoid, Normal parametric MLE, and direct mean ratio — agree to within 0.000022 across all 7 variables and both SSP scenarios. The function is definitively linear.

### FIDUCEO Input Diagram

```
                        ┌─────────┐
        ┌──────────────►│         │
        │               │  SCVR   │
        │   ┌──────────►│         │
        │   │           │ = Δμ/μ  │
        │   │   ┌──────►│         │
        │   │   │       └─────────┘
        │   │   │
   ┌────┴┐ ┌┴───┴──┐ ┌──────────┐
   │ x₁  │ │  x₂   │ │   x₃     │
   │     │ │       │ │         │
   │CMIP6│ │Base-  │ │Model    │
   │daily│ │line   │ │pooling  │
   │vals │ │period │ │method   │
   └──┬──┘ └──┬────┘ └────┬────┘
      │        │           │
   u(x₁)   u(x₂)      u(x₃)
```

### Input Uncertainty Budget

| Input | Symbol | Value / Choice | Uncertainty u(x) | Type | Sensitivity ∂f/∂x |
|-------|--------|---------------|-------------------|------|-------------------|
| **Future daily values** | x₁ | ~306,600 values pooled from 28 CMIP6 models | Model spread (IQR across per-model SCVRs). Measured: 2.5% for tasmax SSP2-4.5 | Type A (statistical) | ∂SCVR/∂mean_future = 1/mean_baseline (linear) |
| **Baseline daily values** | x₁ᵦ | ~306,600 values, 1985–2014, same 28 models | Same model spread mechanism. Also: observational anchoring uncertainty (models vs ERA5 in baseline period) | Type A + Type B | ∂SCVR/∂mean_baseline = −mean_future/mean_baseline² (linear, sign-inverting) |
| **Baseline period choice** | x₂ | 1985–2014 (30 years) | Structural choice. Shifting ±5 years changes SCVR by ~0.5–1.0% for temperature variables | Type B (systematic) | Affects denominator — shifts all SCVRs proportionally |
| **Model pooling method** | x₃ | Concatenation (all daily values from all models pooled, model identity lost) | Alternative: per-model SCVR then ensemble mean. Difference is negligible at n > 10K but pooling obscures model-level outliers | Type B (methodological) | Near-zero effect on SCVR value; affects uncertainty characterisation |

### Uncertainty Characterisation: The SCVR Report Card

SCVR alone is a single mean-shift number. Its blind spot is tail changes when the mean is stable — the "precipitation problem" where mean SCVR ≈ 0% but P95 SCVR = +1.9% (opposite sign). The Report Card addresses this with six companion metrics:

| Companion Metric | Formula | What It Reveals |
|-----------------|---------|----------------|
| P95 SCVR | (P95_future − P95_baseline) / \|P95_baseline\| | 95th percentile shift vs mean shift |
| P99 SCVR | (P99_future − P99_baseline) / \|P99_baseline\| | Extreme tail shift |
| CVaR 95% | (E[X\|X≥P95]_fut − E[X\|X≥P95]_base) / \|E[X\|X≥P95]_base\| | Expected Shortfall — average of worst 5% |
| Mean-Tail Ratio | P95_SCVR / Mean_SCVR | >0.6 = coherent; <0.3 = weak linkage |
| Model IQR | P75 − P25 of per-model SCVR values | Inter-model agreement |
| Tail Confidence | Classification: HIGH / MODERATE / LOW / DIVERGENT | Overall reliability flag |

The Tail Confidence classification algorithm:

```
if sign(mean) ≠ sign(P95):        → DIVERGENT
elif |mean_tail_ratio| < 0.3:     → LOW
elif model_IQR > 2 × |mean|:     → LOW
elif mean_tail_ratio > 0.6:      → HIGH
else:                             → MODERATE
```

### Variable Classification (Hayhurst Solar, SSP2-4.5)

| Variable | Mean SCVR | P95 SCVR | Tail Confidence | Implication |
|----------|-----------|----------|-----------------|-------------|
| tasmax | +6.9% | +4.9% | **HIGH** | Mean is conservative (overstates tail by ~30%). Safe for pipeline use. |
| tasmin | +14.6% | — | **MODERATE** | Usable with caveats. Flag Model IQR. |
| tas | +8.8% | — | **HIGH** | Same behaviour as tasmax. |
| pr | −0.1% | +1.9% | **DIVERGENT** | Mean and tail point opposite directions. SCVR excluded from direct use — Pathway B mandatory. |
| sfcWind | −0.7% | — | **MODERATE/HIGH** | Small signal, models agree. |
| hurs | −3.3% | — | **MODERATE** | Usable with P95 flagged alongside. |
| rsds | +0.4% | — | **MODERATE** | Near-zero. Channel 3 (resource change) is negligible. |

### What's Stable at This Layer

Everything. The SCVR equation is mathematically proven equivalent across three methods. The Report Card companion metrics are computed from the same sorted arrays. The computation is implemented, tested, and producing results across 7 variables × 2 scenarios × 28–31 models. No structural changes anticipated.

---

## Layer 2A: HCR (Hazard Change Ratio) — Business Interruption Channel

**Status: Equations defined. NB04 Part A (HCR) implemented. Hazard routing under active revision (see "What's In Flux" below).**

### Measurement Function (General Form)

```
HCR_h = [mean(hazard_days_h, future) − mean(hazard_days_h, baseline)]
        / mean(hazard_days_h, baseline)
```

This is computed per hazard h via two pathways:

**Pathway A** (SCVR-based scaling): HCR_h = SCVR_var × scaling_factor_h. Used when Tail Confidence is HIGH and literature provides a validated amplification factor. Inherits SCVR uncertainty plus scaling factor uncertainty.

**Pathway B** (direct daily counting): Count hazard days directly from daily CMIP6 output using threshold definitions. Independent of SCVR. Preferred when Tail Confidence is LOW or DIVERGENT, or when the hazard definition is compound (multiple variables).

### The Core Non-Linearity

A small mean shift can produce a large change in threshold exceedances. This is the key amplification that HCR captures:

```
Example: tasmax SCVR = +6.9% (mean shift)
         But heat wave days (above P90 threshold) increase by ~140%
         Amplification factor: ~2.5×

Why: the tail of the distribution is thin — many values cluster just
below the threshold, and a small nudge moves them above it.
```

The sensitivity coefficient ∂HCR/∂SCVR is therefore non-linear and state-dependent — it depends on the shape of the distribution near the threshold. This is where uncertainty amplifies in the framework.

### FIDUCEO Input Diagram (Per-Hazard)

```
                          ┌──────────┐
          ┌──────────────►│          │
          │               │  HCR_h   │
          │   ┌──────────►│          │
          │   │           │ per-hazard│
          │   │   ┌──────►│ ratio    │
          │   │   │       └──────────┘
          │   │   │
     ┌────┴┐ ┌┴───┴──┐ ┌──────────┐
     │ x₁  │ │  x₂   │ │   x₃     │
     │     │ │       │ │         │
     │SCVR │ │Thresh-│ │Scaling  │
     │or   │ │old    │ │factor   │
     │daily│ │defn   │ │(Path A) │
     │vals │ │       │ │or count │
     └──┬──┘ └──┬────┘ └────┬────┘
        │        │           │
     u(x₁)   u(x₂)      u(x₃)
```

### Per-Hazard Equations, Inputs, and Confidence

#### Heat Wave — HIGH confidence, fully computable

```
Step 1: P90_max(doy), P90_min(doy) from baseline per calendar day ±15-day window
Step 2: HW_flag(d) = 1 if tasmax(d) > P90_max AND tasmin(d) > P90_min
Step 3: HW_days(year) = Σ HW_flag(d) for runs of ≥ 3 consecutive flagged days
HCR_heatwave = Δmean(HW_days) / mean(HW_days, baseline)
```

| Input | Uncertainty | Notes |
|-------|------------|-------|
| tasmax, tasmin daily values | Model spread (28 CMIP6 models pooled) | Inherited from SCVR layer |
| P90 threshold definition | Structural: baseline period, window width (±15 days) | Sensitivity: ±2-day window changes threshold by ~0.3°C |
| 3-consecutive-day rule | Definitional choice (Copernicus EDO standard) | Alternative: 5-day rule would reduce counts ~40% |
| Pathway A scaling factor | 2.0–3.0× SCVR_tasmax (base: 2.5) | Diffenbaugh et al. 2013; Cowan et al. 2018 |

**Financial mechanism:** Inverter thermal shutdown → lost generation hours. This IS business interruption. The formula HCR × baseline_BI_pct × Revenue works correctly here.

#### Extreme Precipitation / Flooding — MODERATE confidence, partially computable

```
Rx5day(year) = max rolling 5-day precipitation sum
HCR_flood_precip = Δmean(Rx5day) / mean(Rx5day, baseline)
```

| Input | Uncertainty | Notes |
|-------|------------|-------|
| pr daily values | High model disagreement (IQR = 7.8% for pr). Tail Confidence = DIVERGENT. | Pathway B is mandatory — SCVR mean is misleading for precipitation |
| Soil moisture compound | NOT in NEX-GDDP. Approximated via Hargreaves water balance model | 51.6% of floods are multi-driver; precip-only underestimates by up to 2× |
| Clausius-Clapeyron scaling | ~7%/°C globally, but 2–3× at P99 (super-C-C) | Pathway A factor: 1.5–2.0× SCVR_pr |

**Key uncertainty:** The precipitation-only estimate misses compound flooding (rainfall on saturated soil). The Hargreaves PET approximation for soil moisture is a proxy of a proxy.

#### Wildfire (FWI) — LOW confidence, computable as approximation

```
FWI = f(tasmax, hurs, sfcWind, pr) via Canadian FWI system (Van Wagner 1987)
  Sub-components: FFMC (1-day memory), ISI (wind × FFMC), DMC/DC → BUI, FWI composite
High_FWI_days(year) = count(FWI(d) > threshold)
HCR_wildfire = Δmean(High_FWI_days) / mean(High_FWI_days, baseline)
```

| Input | Uncertainty | Notes |
|-------|------------|-------|
| tasmax (proxy for noon T) | Systematic 5–10% overestimate from using daily max instead of noon obs | Vitolo et al. 2025 |
| FFMC/ISI/BUI memory chain | Sequential daily calculation — errors compound. Initial conditions assumed | Each component has its own sensitivity coefficients |
| FWI threshold (15/19/30) | Site-specific choice with no universal calibration | Determines count, therefore HCR |
| FWI → fire occurrence | P(fire \| high FWI) << 1. Non-linear, probabilistic. | **This is the fundamental disconnect** — see "What's In Flux" |

**Critical note:** Fire weather is being reclassified as a **probabilistic risk indicator** rather than a deterministic BI event. The formula HCR × baseline_BI_pct × Revenue does not apply because the relationship between high-FWI days and actual fire events is non-linear and stochastic. See Section "What's In Flux" below.

#### Wind Cut-Out — LOW confidence, poor proxy

```
V_hub(d) = sfcWind(d) × ln(z_hub / z_0) / ln(10 / z_0)
  [log profile; z_0 ≈ 0.03m; z_hub ≈ 80–100m → V_hub ≈ sfcWind × 1.36]
Cut_out_days(year) = count(V_hub(d) > 25 m/s)  [or gust proxy if ERA5 available]
HCR_wind = Δmean / mean
```

| Input | Uncertainty | Notes |
|-------|------------|-------|
| sfcWind (daily mean at 10m) | Cut-out is triggered by instantaneous gusts, not daily means. Systematic underestimate of cut-out frequency. | At Maverick Creek: sfcWind SCVR ≈ 0 → HCR ≈ 0 |
| Hub-height extrapolation | Log profile assumes neutral stability, flat terrain. Roughness z_0 varies. | Factor 1.36 has ±15% uncertainty from terrain effects |
| Gust factor G | Typically 1.5–2.0 open terrain. Requires ERA5 for site-specific value. | If unavailable, adds ~50% uncertainty to cut-out counts |

#### Ice Storm — LOW confidence, surface proxy only

```
FRP(d) = 1  if tasmin < 0°C AND tasmax > 0°C AND pr > 0.5mm AND hurs > 90%
HCR_icestorm = Δmean(FRP_days) / mean(FRP_days, baseline)
→ Expected negative for Texas (fewer days in the −10 to 0°C window)
```

| Input | Uncertainty | Notes |
|-------|------------|-------|
| Vertical temperature profile | **NOT in NEX-GDDP.** Ice storms require a warm layer aloft + sub-freezing surface. Surface proxy only. | Fundamental limitation — no correction available from NEX-GDDP alone |
| RH threshold (90%) | Changed from earlier 75% based on IEC 61400-1 standard for blade icing (requires near-saturated conditions) | Threshold change substantially affects event counts |

### What's In Flux at This Layer

**Hazard reclassification (March 2026, under team review):** The 10 hazards currently routed through HCR → BI_loss are being reclassified into three categories based on their actual financial mechanism:

| Category | Hazards | Routing | Status |
|----------|---------|---------|--------|
| **BI Events** (stay in HCR → Channel 1) | Heat wave, extreme precip/flooding, wind cut-out, icing shutdown | HCR × baseline_BI_pct × Revenue | Equations stable |
| **Degradation Inputs** (move to EFR → Channel 2) | Freeze-thaw cycles, frost days, cold wave | Daily counts → Coffin-Manson directly | Routing change — equations unchanged |
| **Risk Indicators** (separate treatment) | Fire weather (FWI), dry spell | Flagged with direction + magnitude, no deterministic $ conversion in Phase 1 | Treatment TBD |

**Why this matters for uncertainty:** The reclassification doesn't change the climate equations — it changes where their outputs flow in the financial model. Freeze-thaw cycle counts feeding Coffin-Manson directly (instead of the current SCVR mean approximation) actually **reduces uncertainty** in Channel 2 by replacing a derived input with a directly counted one. Removing probabilistic hazards (fire weather) from the deterministic BI formula removes a source of false precision.

**Impact on existing results:** Minimal for Channel 1 BI_loss (the removed hazards had ~$0 BI contribution anyway, since freeze-thaw doesn't cause downtime). Improved for Channel 2 EFR (Coffin-Manson gets actual cycle counts instead of mean approximation).

---

## Layer 2B: EFR (Equipment Failure Ratio) — Equipment Degradation Channel

**Status: Equations defined. NB04 EFR section in progress. Inputs improving via reclassification.**

### Measurement Functions (Three Physics Models)

EFR uses SCVR directly (not HCR). Three independent degradation mechanisms, each with its own well-characterised physics:

#### Peck's Model (Thermal Aging)

```
AF_thermal = exp[(Ea/k_B) × (1/T_ref − 1/T_stress)]

Where:
  Ea = activation energy (~0.7 eV for encapsulant, ~0.5 eV for solder)
  k_B = Boltzmann constant (8.617 × 10⁻⁵ eV/K)
  T_ref = reference temperature (baseline mean)
  T_stress = stressed temperature (future mean, derived from SCVR)
```

| Input | Uncertainty | Notes |
|-------|------------|-------|
| Activation energy Ea | Material-specific. Literature range 0.3–1.0 eV for PV components | Dominant uncertainty source. Doubles degradation per 10°C at Ea = 0.7 eV |
| T_stress from SCVR | Inherited from SCVR Layer 1 — well-characterised (HIGH confidence for tasmax) | Linear transformation: T_stress = T_baseline × (1 + SCVR) |
| Arrhenius assumption | Assumes single dominant failure mechanism. Real degradation involves multiple competing mechanisms | Type B (model structural uncertainty) |

**Sensitivity:** The Arrhenius exponential means Peck's is highly sensitive to temperature. A +2°C shift roughly doubles degradation rate at Ea = 0.7 eV. This is a genuine physical non-linearity, well-established in materials science.

#### Coffin-Manson (Thermal Cycling Fatigue)

```
N_f = C × (ΔT)^(−β)

Where:
  N_f = cycles to failure
  C = material constant
  ΔT = thermal cycle amplitude (tasmax − tasmin on cycling days)
  β = fatigue exponent (~2.0 for solder joints, ~1.5 for encapsulant)
```

| Input | Uncertainty | Notes |
|-------|------------|-------|
| Cycle count | **Improving:** currently uses SCVR-derived estimate; will use direct Pathway B freeze-thaw counts post-reclassification | Direct counting removes a layer of approximation |
| ΔT amplitude | From daily tasmax − tasmin on freeze-thaw days | Well-characterised from CMIP6 daily data |
| Fatigue exponent β | Material-dependent, typically 1.5–2.5 for PV materials | Moderate uncertainty; well-studied in reliability engineering literature |

#### Palmgren-Miner (Wind Fatigue Accumulation)

```
D = Σ (n_i / N_f,i)

Where:
  D = cumulative damage fraction (failure at D = 1)
  n_i = number of cycles at stress level i
  N_f,i = cycles to failure at stress level i (from S-N curve)
```

| Input | Uncertainty | Notes |
|-------|------------|-------|
| sfcWind SCVR | Near-zero at pilot sites (Maverick Creek SCVR ≈ −0.7%) | Wind fatigue EFR ≈ 0 at these sites. Becomes relevant for higher-wind sites. |
| S-N curve parameters | Turbine-manufacturer-specific. Public data limited. | Type B uncertainty from manufacturer data access |
| Miner's rule linearity assumption | Damage accumulates linearly. Non-linear damage accumulation observed in practice. | Conservative for low damage fractions |

### What's Stable at This Layer

The three physics models (Peck's, Coffin-Manson, Palmgren-Miner) are established reliability engineering methods with decades of validation in electronics and mechanical fatigue. The equation forms will not change. The reclassification improves Coffin-Manson inputs by replacing SCVR-derived estimates with direct cycle counts.

### What May Change

The material parameters (Ea, β, S-N curves) are asset-type-specific and may be refined as more operational data becomes available. The relative weighting of the three mechanisms for different asset types (solar vs wind) is an open question for NB04/NB05.

---

## Layer 3: Financial Translation (CFADS → NAV)

**Status: Structural framework defined. NB05 not yet built. Dollar estimates are illustrative only.**

### Measurement Function

```
CFADS_adjusted(t) = Revenue(t) × (1 − EFR(t)) − BI_loss(t) − OpEx(t)

Where:
  BI_loss(t) = Σ_h [HCR_h(t) × baseline_BI_pct_h × Revenue(t)]    (Channel 1, additive)
  EFR(t) = weighted combination of Peck's, Coffin-Manson, Palmgren-Miner    (Channel 2, multiplicative)
  If t > IUL: CFADS_adjusted = 0    (Channel 2b: life truncation)

NAV_impairment = Σ_t [CFADS_baseline(t) − CFADS_adjusted(t)] / (1+r)^t
```

### FIDUCEO Input Diagram

```
                              ┌──────────────┐
            ┌────────────────►│              │
            │                 │ NAV          │
            │   ┌────────────►│ impairment   │
            │   │             │              │
            │   │   ┌────────►│              │
            │   │   │         └──────────────┘
            │   │   │
       ┌────┴┐ ┌┴───┴──┐ ┌──────────────┐
       │ x₁  │ │  x₂   │ │   x₃         │
       │     │ │       │ │             │
       │HCR  │ │EFR    │ │Financial    │
       │per  │ │per    │ │assumptions  │
       │haz. │ │mech.  │ │(Revenue,    │
       │     │ │       │ │ OpEx, r,    │
       │     │ │       │ │ IUL, BI%)   │
       └──┬──┘ └──┬────┘ └──────┬──────┘
          │        │             │
       u(x₁)   u(x₂)        u(x₃)
```

### Key Uncertainty Sources at This Layer

| Input | Uncertainty Source | Magnitude | Notes |
|-------|-------------------|-----------|-------|
| baseline_BI_pct per hazard | How much revenue is lost per unit of hazard? Industry benchmarks, operational data, or engineering estimates | Potentially large (2–5× range) | This is the weakest link in Channel 1 |
| EFR mechanism weighting | Relative importance of Peck's vs Coffin-Manson vs Palmgren-Miner | TBD — requires NB04 output | Asset-type dependent |
| IUL (Impaired Useful Life) | How much does EFR shorten operational life? | Potentially the largest single driver of NAV impairment | Post-debt years are highest-value; losing them hurts most |
| Discount rate r | Standard project finance parameter | Well-characterised | Not climate-dependent |
| Revenue, OpEx projections | Standard financial model inputs | Well-characterised | Not climate-dependent |

### Illustrative Estimates (Theoretical — Not Final)

For Hayhurst Solar under SSP5-8.5, initial theoretical estimates from worked examples (not computed NB04/NB05 results):

```
Channel 2 (IUL shortening):    ~$5.1M
Channel 1 (Hazard BI):         ~$1.2M
Channel 3 (rsds upside):      ~-$0.4M
Total NAV impairment:          ~$5.9M  (~10% of $60M asset value)
```

These illustrate the structure of how channels combine. Actual values will come from NB04/NB05 and may differ by 2–3×.

### What's Stable at This Layer

The two-channel CFADS formula (multiplicative EFR + additive BI_loss) is architecturally stable. The separation of channels is physically motivated and will not collapse.

### What May Change

Everything about the dollar calibration: baseline_BI_pct values, EFR mechanism weights, IUL computation, and how risk indicators (fire weather, dry spell) are eventually incorporated. NB05 is future work.

---

## Summary: Uncertainty Amplification Through the Chain

```
Layer 1 (SCVR):     LINEAR function. Uncertainty = model spread.
                    Well-characterised via Report Card.
                    u(SCVR) ≈ Model IQR ≈ 2.5% for tasmax.

       ↓ Non-linear amplification at thresholds

Layer 2A (HCR):     NON-LINEAR per hazard. Small SCVR → large HCR.
                    Amplification factor 2–3× for well-characterised hazards.
                    Confidence varies: HIGH (heat wave) to LOW (wind, ice storm).
                    Proxy quality is the dominant uncertainty at this layer.

Layer 2B (EFR):     NON-LINEAR via Arrhenius (exponential in T).
                    Well-characterised physics. Material parameters (Ea, β)
                    are the dominant uncertainty.
                    SCVR input is HIGH confidence for temperature variables.

       ↓ Financial calibration uncertainty

Layer 3 (NAV):      LINEAR combination of HCR and EFR outputs.
                    Financial assumptions (baseline_BI_pct, IUL) are the
                    dominant uncertainty. Climate uncertainty is well-bounded
                    relative to financial conversion uncertainty.
```

### Where Uncertainty Is Smallest

SCVR for temperature variables (tasmax, tas). The equation is simple, the input data is large, models agree, and the Report Card confirms coherent behaviour across quantiles.

### Where Uncertainty Is Largest

The financial conversion layer — particularly baseline_BI_pct (how much revenue is lost per unit of hazard increase) and IUL computation (how much degradation shortens asset life). These are calibration parameters that depend on operational data and engineering judgment, not climate science.

### Where Uncertainty Amplifies Most

The SCVR → HCR step for threshold-based hazards. A +6.9% mean shift (SCVR) can produce a +140% change in days above threshold (HCR). This amplification is physically real (not a modelling artifact) and well-studied in extreme value theory, but it means that u(SCVR) gets multiplied by 2–3× when it enters HCR.

---

## Notation and Definitions

| Symbol | Definition |
|--------|-----------|
| SCVR | Severe Climate Variability Rating — fractional mean shift |
| HCR | Hazard Change Ratio — % change in hazard event frequency |
| EFR | Equipment Failure Ratio — fractional acceleration of degradation |
| IUL | Impaired Useful Life — shortened operational lifetime |
| BI | Business Interruption — revenue lost to hazard downtime |
| NAV | Net Asset Value |
| CFADS | Cash Flow Available for Debt Service |
| DSCR | Debt Service Coverage Ratio |
| Pathway A | HCR from SCVR × literature scaling factor |
| Pathway B | HCR from direct daily hazard counting |

---

## References

### Climate Science
- Diffenbaugh et al. 2013, PNAS — Heat wave amplification from mean warming
- Cowan et al. 2018, Scientific Reports — +4 to +34 extra heat wave days per °C
- IPCC AR6 Chapter 11 — Extreme event attribution, Clausius-Clapeyron scaling
- Tabari 2020, Scientific Reports — Precipitation extreme scaling rates
- Vitolo et al. 2025, npj Climate and Atmospheric Science — FWI trends and calibration
- Van Wagner 1987 — Canadian Forest Fire Weather Index System
- Zscheischler et al. 2024 — Compound flood drivers (51.6% multi-driver)
- Jeong et al. 2019, NHESS — Freezing rain frequency projections
- IEC 61400-1 — Wind turbine design standard (icing, structural loading)

### Uncertainty Framework
- FIDUCEO (FIdelity and Uncertainty in Climate data records from Earth Observation) — Measurement function uncertainty diagram methodology
- GUM (Guide to the Expression of Uncertainty in Measurement) — Type A / Type B uncertainty classification

### Reliability Engineering
- Peck's model — Arrhenius acceleration for thermal aging
- Coffin-Manson — Low-cycle thermal fatigue
- Palmgren-Miner — Cumulative linear damage rule

---

## Cross-References to LTRisk Documentation

This uncertainty mapping draws from detailed methodology docs throughout the project. For deeper dives on any layer:

### Layer 1 (SCVR) — Methodology & Companion Metrics

| Topic | Doc | What It Covers |
|-------|-----|---------------|
| SCVR computation & Report Card | [04_scvr_methodology.md](../../learning/B_scvr_methodology/04_scvr_methodology.md) | Step-by-step computation, method equivalence proof (3 methods agree to 6+ decimals), Report Card with all 6 companion metrics, Tail Confidence algorithm, variable classes (A/B/C), decade progression, annual strategy |
| Method equivalence derivation | [scvr_method_equivalence.md](../scvr_methodology/scvr_method_equivalence.md) | Full proof that empirical trapezoid = Normal MLE = direct mean ratio; SCVR decomposition (mean vs tail); companion metrics design rationale |
| Annual SCVR experiment | [annual_scvr_methodology.md](../scvr_methodology/annual_scvr_methodology.md) | Per-year vs rolling vs anchor fit comparison; R² results per variable; why temperature uses anchor_3_linear and precipitation uses period_average |
| Decade shape analysis | [decade_shape_analysis.md](../scvr_methodology/decade_shape_analysis.md) | Variance, P99, GEV ξ evolution across decades; evidence that temperature is primarily a mean shift (+2% variance vs +2.8°C mean) |
| SCVR vs other metrics | [11_distribution_shift_methods.md](../../learning/D_technical_reference/11_distribution_shift_methods.md) | SCVR compared to W1, CVaR, KS, AAL; honest framing as mean-shift metric; insurance AAL analogy |

### Layer 2A (HCR) — Hazard Computation & Routing

| Topic | Doc | What It Covers |
|-------|-----|---------------|
| HCR methodology | [07_hcr_hazard_change.md](../../learning/C_financial_translation/07_hcr_hazard_change.md) | 10 hazard definitions, scaling factors, Pathway A vs B, compound events, negative HCR, annual framing |
| Pathway A vs B | [hcr_pathway_a_vs_b.md](../hcr_financial/hcr_pathway_a_vs_b.md) | Why both exist, cross-validation loop, when Pathway A fails (precipitation), worked examples |
| Jensen's inequality | [jensen_inequality_hcr_scvr.md](../hcr_financial/jensen_inequality_hcr_scvr.md) | Mathematical proof for the non-linear amplification at Layer 2A; why E[f(X)] ≠ f(E[X]) for threshold crossings |
| **Hazard reclassification** | [hcr_efr_boundary.md](../hcr_financial/hcr_efr_boundary.md) | **Directly relevant to "What's In Flux" section.** Proposes 3-category classification: BI events (Channel 1), degradation inputs (Channel 2), risk indicators (separate). Worked examples for heat wave, freeze-thaw, fire weather. |

### Layer 2B (EFR) — Equipment Degradation

| Topic | Doc | What It Covers |
|-------|-----|---------------|
| EFR physics models | [08_efr_equipment_degradation.md](../../learning/C_financial_translation/08_efr_equipment_degradation.md) | Peck's (Arrhenius derivation, Ea sensitivity), Coffin-Manson (cycle counting, β exponent), Palmgren-Miner (S-N curves); IUL computation; thermal coefficient vs Peck's distinction |
| Performance adjustment | [scvr_performance_adjustment.md](../scvr_methodology/scvr_performance_adjustment.md) | Why Channel 3 (resource change) is negligible; thermal derating ~0.3% vs EFR ~10% — degradation is 30–50× larger than performance effect |

### Layer 3 (Financial) — NAV Impairment

| Topic | Doc | What It Covers |
|-------|-----|---------------|
| NAV impairment chain | [09_nav_impairment_chain.md](../../learning/C_financial_translation/09_nav_impairment_chain.md) | Complete SCVR → HCR + EFR → CFADS → NAV pipeline; three channels; worked dollar examples; DSCR covenant breach timing |
| Cash flow integration | [cashflow_integration.md](../hcr_financial/cashflow_integration.md) | Three BI conversion approaches (top-down, bottom-up, benchmarks); LTRisk ↔ project_finance bridge; baseline_BI_pct calibration |
| Framework architecture | [framework_architecture.md](../architecture/framework_architecture.md) | Two-channel system map; variable → channel routing; Report Card as router |

---

## Data Sources

| Source | Resolution | Variables | Coverage |
|--------|-----------|-----------|----------|
| NEX-GDDP-CMIP6 (via THREDDS) | 0.25° daily | tasmax, tasmin, tas, pr, sfcWind, hurs, rsds | 28–31 models, 1985–2014 baseline + 2026–2055 future |
| Pilot sites | Hayhurst Solar (TX), Maverick Creek Wind (TX) | — | SSP2-4.5 and SSP5-8.5 |

---

## Notebook Pipeline Status

| Notebook | Purpose | Status |
|----------|---------|--------|
| NB01 | Climate indices (annual hazard counts) | ✅ Built |
| NB02 | THREDDS data pipeline | ✅ Built |
| NB03 | SCVR computation | ✅ Built |
| NB04 | HCR + EFR computation | ✅ HCR Part A done; EFR and reclassification in progress |
| NB05 | Financial model / NAV impairment | ◻ Future |
