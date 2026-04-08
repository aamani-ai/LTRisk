---
title: "Discussion — EFR Two Modes: SCVR-Based vs Direct Daily Integration"
type: discussion
domain: climate-risk / equipment-degradation / methodology
created: 2026-04-02
status: draft — proposed two-mode architecture, pending team review
context: >
  The HCR channel has two pathways (A: SCVR-based scaling, B: direct daily
  counting) because Jensen's inequality means the mean-based approximation
  can give wrong answers for non-linear threshold functions. This doc argues
  that EFR has the SAME problem — Peck's Arrhenius function and Coffin-Manson
  cycling are also non-linear, so applying them to the mean temperature gives
  a different (and systematically biased) answer than integrating over daily
  data. We propose formalising two input modes for EFR, mirroring HCR's
  Pathway A/B structure.
relates-to:
  - docs/learning/C_financial_translation/08_efr_equipment_degradation.md
  - docs/discussion/hcr_financial/hcr_efr_boundary.md
  - docs/discussion/hcr_financial/jensen_inequality_hcr_scvr.md
  - docs/plan/plan_climate_risk_orchestrator.md
---

# Discussion — EFR Two Modes

> **The question:** HCR has two pathways because Jensen's inequality makes
> the mean-based approach unreliable for non-linear threshold functions.
> Does EFR have the same problem? Should it also have two input modes?

> **Short answer:** Yes. The Arrhenius function (Peck's) and cycle-counting
> (Coffin-Manson) are both non-linear. Using SCVR (the mean) as input
> systematically underestimates Peck's and gives the wrong direction for
> Coffin-Manson at some sites. Formalising two modes (A: SCVR-based,
> B: daily-data-based) creates a clean parallel with HCR and resolves
> the Coffin-Manson routing issue from the hcr_efr_boundary discussion.

---

## 1. The Parallel: HCR and EFR Have the Same Jensen's Problem

### HCR (well-documented, see jensen_inequality_hcr_scvr.md)

```
Jensen's inequality: E[f(X)] ≠ f(E[X])  for non-linear f

HCR Pathway A:  f(E[X])    = apply threshold function to mean SCVR
HCR Pathway B:  E[f(X)]    = apply threshold function to each day, then average

For precipitation: Pathway A gives WRONG SIGN
  Mean SCVR = -0.1% → HCR_flood ≈ 0 (wrong)
  Pathway B counts actual Rx5day events → HCR_flood = +4% (correct)
```

### EFR (same math, not yet formalised)

```
Same inequality applies — the physics models are non-linear:

EFR Mode A:  g(E[T])     = apply Arrhenius to mean temperature
EFR Mode B:  E[g(T)]     = apply Arrhenius to each daily temperature, then average

Arrhenius is CONVEX (exponential in 1/T), so by Jensen's inequality:
  E[g(T)] > g(E[T])

  Mode A UNDERESTIMATES true degradation because it misses the
  disproportionate contribution of hot days.
```

---

## 2. Where It Matters: Model by Model

### Peck's Thermal Aging — Mode A underestimates by ~5-15%

```
The Arrhenius function: AF = exp(Ea/kT)

This is a CONVEX function of temperature.

Consider two days at Hayhurst:
  Day 1: 45°C (hot summer)  →  AF_1 = exp(Ea/k × 1/318) = very high
  Day 2: 25°C (mild spring) →  AF_2 = exp(Ea/k × 1/298) = moderate

  Mode A (mean):  AF_mean = exp(Ea/k × 1/308)  ← uses average of 35°C
  Mode B (daily): AF_daily = (AF_1 + AF_2) / 2  ← averages the AF values

  Because exp is convex:
    AF_daily > AF_mean     (always, by Jensen's inequality)

  The hot day contributes DISPROPORTIONATELY to aging.
  Using the mean temperature MISSES this asymmetry.

  At Hayhurst:
    Temperature variance changes only +2% (doc 04 decade shape analysis)
    So the Jensen's gap for Peck's is moderate: ~5-15% underestimate
    
    Mode A (mean-based):  EFR_peck ≈ 0.11
    Mode B (daily-based): EFR_peck ≈ 0.12-0.13 (estimated)

    Direction is SAME (both positive) but magnitude differs.
    For Phase 1, Mode A is acceptable. For Phase 2, Mode B is better.
```

### Coffin-Manson Thermal Cycling — Mode A gives WRONG DIRECTION

```
This is where the gap is critical — just like precipitation in HCR.

Mode A (current):
  Uses SCVR to estimate change in daily temperature swing (ΔT)
  ΔT_baseline = 18.0°C, ΔT_future = 18.3°C
  EFR_coffin = 1 - (18.0/18.3)^2 = +0.03 (MORE damage)

Mode B (proposed):
  Counts actual freeze-thaw cycles from daily data
  Baseline: 45.71 freeze-thaw days/yr
  Future:   34.31 freeze-thaw days/yr (warming = fewer 0°C crossings)
  Change:   -25% FEWER high-amplitude cycles

  The cycles that MATTER MOST for fatigue are the freeze-thaw ones
  (ΔT = 15-25°C, crossing 0°C = maximum material stress)
  
  Mode A says: +3% more damage (wrong direction)
  Mode B says: -25% fewer damaging cycles (correct direction)

This is the SAME failure mode as precipitation in HCR:
  Mean-based approximation misses what's happening in the tails
  → gives wrong sign → mandatory Mode B
```

### Palmgren-Miner Structural Fatigue — Mode A is sufficient

```
  SCVR_sfcWind ≈ 0 at both pilot sites
  → wind load distribution is unchanged
  → both Mode A and Mode B give EFR_palmgren ≈ 0
  
  The distinction doesn't matter when the signal is zero.
  At high-wind sites where SCVR_sfcWind is material,
  Mode B (integrating actual daily load cycles) would be
  more accurate — but that's a future concern.
```

---

## 3. The Proposed Two-Mode Architecture

### Mode A: SCVR-Based (fast, parametric)

```
Input:   SCVR values from NB03 Report Card
Process: Apply physics model to the mean-shifted conditions
Output:  EFR per model per year

Peck's:          T_stress = T_ref × (1 + SCVR_tas)
                 AF = exp(Ea/k × (1/T_ref - 1/T_stress))
                 EFR_peck = AF_ratio - 1

Coffin-Manson:   ΔT_future = estimated from SCVR_tasmax, SCVR_tasmin
                 EFR_coffin = 1 - (ΔT_base / ΔT_future)^β

Palmgren-Miner:  Wind distribution shifted by SCVR_sfcWind
                 EFR_palmgren from shifted S-N integration

When to use:
  - Quick screening
  - When Tail Confidence is HIGH (temperature variables)
  - When variance change is small (< 5%)
  - Phase 1 default for Peck's and Palmgren-Miner
```

### Mode B: Direct Daily Integration (exact, empirical)

```
Input:   Daily CMIP6 values from THREDDS cache (same data as Pathway B in HCR)
Process: Apply physics model to EACH DAY, then aggregate
Output:  EFR per model per year (more accurate)

Peck's:          For each day d:
                   AF(d) = exp(Ea/k × (1/T_ref - 1/T(d)))
                 EFR_peck = mean(AF_future_days) / mean(AF_baseline_days) - 1
                 (Integrates Arrhenius over actual daily temperature profile)

Coffin-Manson:   Count actual cycles from daily data:
                   freeze_thaw_count = days where tasmin < 0 AND tasmax > 0
                   thermal_cycle_amplitude = tasmax(d) - tasmin(d) per day
                 EFR_coffin = f(cycle_counts, amplitudes) vs baseline

Palmgren-Miner:  For each day d:
                   wind_load(d) = f(sfcWind(d))
                   damage(d) = load(d)^m / N_f(load)
                 EFR_palmgren = sum(damage_future) / sum(damage_baseline) - 1

When to use:
  - When Mode A gives wrong direction (Coffin-Manson at warming sites)
  - When higher accuracy needed (Peck's for Phase 2)
  - When variance changes are significant
  - Mandatory for Coffin-Manson (same logic as Pathway B for precip)
```

---

## 4. The Unified View — Both Channels, Both Modes

This creates a clean, symmetric architecture across the entire framework:

```
                      SCVR Report Card
                      (7 variables, 6+ metrics)
                              │
                ┌─────────────┴─────────────┐
                │                           │
          CHANNEL 1 (HCR)            CHANNEL 2 (EFR)
          Business Interruption      Equipment Degradation
                │                           │
         ┌──────┴──────┐            ┌───────┴───────┐
         │             │            │               │
      Mode A        Mode B       Mode A          Mode B
      SCVR ×        Direct       SCVR →          Direct
      scaling       daily        physics          daily
      factor        counting     model            integration
         │             │            │               │
         ▼             ▼            ▼               ▼
      HCR(t)        HCR(t)      EFR(t)          EFR(t)
      parametric    empirical   parametric      empirical
         │             │            │               │
         └──────┬──────┘            └───────┬───────┘
                │                           │
         BI_loss(t)                  climate_degrad(t)
         (additive)                  + IUL truncation
                │                    (multiplicative)
                └───────────┬───────────────┘
                            │
                     CFADS_adjusted(t)
```

### The Routing Decision — Same Logic for Both Channels

The orchestrator uses the **same criteria** to decide Mode A vs Mode B
for both HCR and EFR:

```
ROUTING MATRIX (unified across channels)

                        Channel 1 (HCR)     Channel 2 (EFR)
                        ───────────────     ───────────────
Tail Confidence HIGH:   Mode A preferred    Mode A preferred
                        (cross-validate B)  (Peck's from SCVR)

Tail Confidence MOD:    Mode A + B          Mode A + B
                        (compare, flag)     (report range)

Tail Confidence LOW:    Mode B mandatory    Mode B preferred
                        (A unreliable)      (A underestimates)

Tail Confidence DIV:    Mode B only         Mode B only
                        (A wrong sign)      (A wrong direction)
```

### Per-Model Routing (Hayhurst Solar SSP5-8.5)

```
Model             Variable(s)    Tail Conf.   Mode   Rationale
──────────────    ───────────    ──────────   ────   ─────────────────────────
Peck's            tas, hurs      HIGH         A      Mean-based AF is ~5-15%
                                                      low, but acceptable for
                                                      Phase 1. Mode B for Phase 2.

Coffin-Manson     tasmax,tasmin   HIGH (temp)  B      Mode A gives wrong direction
                  (freeze-thaw)                        (+3% damage vs -25% fewer
                                                      cycles). Mandatory Mode B.

Palmgren-Miner    sfcWind        MOD/HIGH     A      SCVR ≈ 0. Both modes give
                                                      EFR ≈ 0. Doesn't matter.
```

---

## 5. What This Resolves

### 1. The Coffin-Manson routing problem (from hcr_efr_boundary.md)

The boundary discussion proposed moving freeze-thaw from HCR to EFR and
feeding cycle counts to Coffin-Manson. Mode B formalises this: freeze-thaw
counts from daily data are the Mode B input to Coffin-Manson. The daily
counting infrastructure built for HCR Pathway B now explicitly serves
BOTH channels.

### 2. The orchestrator's routing symmetry

The orchestrator plan needs a routing matrix. With two modes for both
channels, the matrix is symmetric:

```
For each hazard/model:
  1. Check input variable's Tail Confidence
  2. If HIGH: use Mode A (fast, SCVR-based)
  3. If LOW/DIVERGENT: use Mode B (daily data)
  4. If MODERATE: use both, report range

This is ONE decision rule for the entire framework,
not separate rules for HCR and EFR.
```

### 3. Peck's accuracy improvement path

Mode A Peck's is acceptable for Phase 1 (~5-15% underestimate). Mode B
Peck's (integrating Arrhenius over daily temperatures) is the Phase 2
upgrade. The architecture supports both without restructuring.

### 4. Shared infrastructure

HCR Pathway B and EFR Mode B use the **same daily data cache**. The NB04
daily loading code serves both channels. No duplication needed.

---

## 6. What Doesn't Change

- **SCVR computation** — unchanged. Still the foundation.
- **Report Card** — unchanged. Still routes variables to modes.
- **The physics models themselves** — Peck's, Coffin-Manson, Palmgren-Miner
  equations are the same. Only the INPUT changes (mean vs daily).
- **Financial translation** — Effect 1 (annual generation) and Effect 2 (IUL)
  work the same regardless of which mode produced the EFR value.
- **Channel independence** — HCR and EFR are still parallel. Mode A/B is an
  INTERNAL choice within each channel, not a cross-channel dependency.

---

## 7. Implementation Priority

```
PHASE 1 (current):
  Peck's:          Mode A (SCVR-based)      ← acceptable, 5-15% conservative
  Coffin-Manson:   Mode B (direct counts)   ← mandatory, Mode A gives wrong sign
  Palmgren-Miner:  Mode A (SCVR-based)      ← SCVR ≈ 0, both modes give ~0

PHASE 2 (future):
  Peck's:          Mode B (daily integration) ← improves accuracy by ~10%
  Coffin-Manson:   Mode B (remains)           ← already correct
  Palmgren-Miner:  Mode B (daily loads)       ← only relevant at high-wind sites
```

---

## 8. Open Questions

1. **Peck's Mode B implementation:** Should we integrate Arrhenius over all
   ~306K daily temperatures, or use a representative subset (e.g., summer
   months only, since hot days contribute most)?

2. **Coffin-Manson Mode B:** Should we count ALL thermal cycles (365/yr) or
   only freeze-thaw cycles (the high-amplitude ones that cause most damage)?
   The current proposal counts freeze-thaw only. Should mild daily cycling
   (ΔT = 15°C, no freeze) also be included?

3. **Weighting in combined EFR:** If Peck's uses Mode A and Coffin-Manson
   uses Mode B, should the 80/20 weighting change? (Mode B Coffin-Manson
   may have larger magnitude than Mode A, shifting the balance.)

4. **Cross-validation:** For Peck's, should we run both Mode A and Mode B
   and report the gap? This would quantify the Jensen's error for each site.

---

## Cross-References

| Topic | Doc | What It Covers |
|-------|-----|---------------|
| Jensen's inequality (HCR context) | [jensen_inequality_hcr_scvr.md](../hcr_financial/jensen_inequality_hcr_scvr.md) | The same math that motivates Mode B for EFR |
| HCR/EFR boundary | [hcr_efr_boundary.md](../hcr_financial/hcr_efr_boundary.md) | Freeze-thaw reclassification that Mode B resolves |
| EFR physics models | [08_efr_equipment_degradation.md](../../learning/C_financial_translation/08_efr_equipment_degradation.md) | Peck's, Coffin-Manson, Palmgren-Miner details |
| Orchestrator plan | [plan_climate_risk_orchestrator.md](../../plan/plan_climate_risk_orchestrator.md) | Where this routing lives in the architecture |
| SCVR Report Card | [04_scvr_methodology.md](../../learning/B_scvr_methodology/04_scvr_methodology.md) | Tail Confidence flags that drive Mode A vs B |
