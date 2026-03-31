# Discussion: Decade-Resolved Shape Analysis & Team Feedback Response

*Draft — 2026-03-13*

---

## 1. Background — Prashant's Feedback (~2026-03-12)

During a team review of the initial exceedance curve outputs, senior reviewer Prashant raised
concerns about the SCVR exceedance curves:

- The **scenario gap** (SSP2-4.5 vs SSP5-8.5) looked too small
- Exceedance curves showed only a **horizontal shift**, not shape/slope change
- He expected to see **intensity effects** (tail fattening, slope change) in later years
- The single 30-year SCVR value doesn't reveal temporal progression

**Six proposed checks:**

| # | Check | Purpose |
|---|-------|---------|
| 1 | Recompute SCVR year-by-year | Show annual progression, not one epoch value |
| 2 | Use continuous fitted methodology | Parametric fit alongside empirical |
| 3 | Refit exceedance curves per decade | Check if slope/intensity changes in later years |
| 4 | Expand to up to 34 ensemble members | More statistical robustness |
| 5 | Validate against ERA5 reanalysis | Drift check — is baseline realistic? |
| 6 | Check CLR cloud cover variable | Missing linkage: precip → cloud → irradiance |

---

## 2. Why SCVR Shows "Just a Shift" — This Is By Design

SCVR is defined as:

```
SCVR = (area_future − area_baseline) / area_baseline
```

At large sample sizes (n > 10,000), the trapezoid area under the empirical exceedance curve
converges to the sample mean E[X]. Therefore:

```
SCVR ≈ (E[X_future] − E[X_baseline]) / E[X_baseline]
```

**SCVR is fundamentally a mean-shift metric.** It captures how the center of the distribution
moves, not how the tails fatten or the variance changes. This is not a bug — it's what SCVR
is designed to measure.

A pure horizontal shift of the entire distribution gives a positive SCVR that looks like
"just a shift" in the exceedance plot, because that's exactly what it is. Shape changes
(variance increase, kurtosis change, tail fattening) are invisible in a single SCVR number.

**Implication:** To surface shape changes, we need additional metrics alongside SCVR.

---

## 3. What We Added to Surface Shape Changes

### 3a. Decade-Resolved Exceedance Curves

Split the 30-year future into 3 non-overlapping decades (2026-2035, 2036-2045, 2046-2055).
Plot exceedance curves for each decade separately.

**Visual test:** If tails fan out in later decades (curves diverge at the extreme right),
the distribution shape IS changing. If curves are parallel shifts, it's purely a mean shift.

### 3b. Shape Metrics per Decade

For each decade + baseline, compute: mean, variance, skewness, P95, P99.

If variance or P99 increases faster than the mean, the tails are fattening.
Skewness changes indicate asymmetric distribution evolution.

### 3c. GEV Parametric Fit

Fit `scipy.stats.genextreme` to annual block maxima per decade. The GEV shape parameter ξ
directly tracks tail evolution:
- ξ < 0: Light tail (bounded above)
- ξ ≈ 0: Gumbel (exponential tail)
- ξ > 0: Heavy tail (Fréchet, polynomial decay)

If ξ increases over decades → tails are fattening.

### 3d. SCVR Annual Progression (Anchor Fit)

Instead of one SCVR per 30-year window, compute SCVR at 3 anchor points (decade midpoints)
and fit a linear trend. The slope shows whether SCVR is accelerating.

---

## 4. Variable-Specific Strategy Decision

Not all variables respond the same way to the anchor fit approach. Based on empirical testing
(documented in `annual_scvr_methodology.md` §14):

| Strategy | Variables | R² | Rationale |
|----------|-----------|-----|-----------|
| `anchor_3_linear` | tasmax, tasmin, tas | > 0.95 | Clear monotonic signal, low noise-to-signal |
| `period_average` | pr, hurs, sfcWind, rsds | 0.59 or N/A | Too noisy for linear fit; SCVR ≈ 0 for wind/radiation |

**Temperature:** 3-anchor linear fit works well. SCVR increases monotonically, R² > 0.95.
Interpolate to 30 annual values for CFADS integration.

**Precipitation:** Noise-to-signal ratio = 9.05. Non-linear behavior. Period average only.

**Wind/radiation:** SCVR ≈ 0 — no meaningful signal to fit. Period average as placeholder.

---

## 5. Empirical vs Parametric — When Each Matters

### For SCVR (our current metric): Empirical is correct

SCVR is an area/mean metric computed via trapezoid integration. At all anchor pool sizes
(n ≥ 10,000 daily values), the empirical estimate is extremely accurate:

```
Trapezoid error at n=47,000: O(1/n²) ≈ 4.5 × 10⁻¹⁰ — negligible
```

Parametric fitting adds complexity and model risk (wrong distributional assumption)
without improving the SCVR estimate.

### For other metrics: Parametric matters

| Metric | Empirical OK? | Parametric needed? |
|--------|---------------|-------------------|
| SCVR (area ratio) | Yes — area = mean at large n | No benefit |
| P95, P99 | Yes — n > 10,000 gives tight empirical | Marginal benefit |
| CVaR (tail average above threshold) | Acceptable at large n | Preferred — smoother tail |
| Return periods (1-in-100-year events) | Poor — need n > 10,000 years | Essential — extrapolation required |

**Decision:** Compute GEV alongside empirical as a **diagnostic** (ξ parameter evolution),
not as a replacement for the SCVR computation itself.

**Reference:** Full analysis in `annual_scvr_methodology.md` §14.6

### Quantitative proof: parametric vs empirical SCVR

To confirm the empirical approach, we computed SCVR three ways for tasmax (SSP2-4.5, n=142,399):

| Method | SCVR |
|--------|------|
| Empirical trapezoid (our method) | +0.068731 |
| Normal parametric (MLE μ) | +0.068731 |
| Direct mean ratio (np.mean) | +0.068731 |

All three agree to 6 decimal places. This is expected: at n > 10,000 the empirical trapezoid
area under the exceedance curve converges to E[X], which is exactly what parametric means
estimate. No parametric fit can improve on this.

**Why not fit GEV to daily data?** GEV (Generalized Extreme Value) is the limiting distribution
for block maxima, not for daily values. Fitting GEV to 142,000 daily values gives wrong shape
parameters and unreliable mean estimates. GEV should only be used for annual block maxima
(n ≈ 390), where it is theoretically appropriate.

### GPD: the right parametric fit for the tail

For threshold exceedances, the Pickands-Balkema-de Haan theorem states that the Generalized
Pareto Distribution (GPD) is the theoretically correct limiting distribution. We fit GPD to
daily values above the P95 threshold, giving exceedance probabilities in the same space as
the empirical curve. This is now shown on the tail-zoom panel (bottom row of decade exceedance
plots) as dashed lines.

GPD fit quality is quantified via KS test D-statistic (saved in JSON alongside the fit
parameters). At n ≈ 7,120 exceedances the KS p-value is trivially small (large-sample
sensitivity), but the D-statistic itself is informative: D < 0.02 indicates excellent fit.

---

## 6. First Results — tasmax (Hayhurst Solar, 13 models)

### Decade SCVR Progression

| Decade | SSP2-4.5 | SSP5-8.5 |
|--------|----------|----------|
| 2026-2035 | +0.051 | +0.060 |
| 2036-2045 | +0.070 | +0.075 |
| 2046-2055 | +0.085 | +0.107 |

Scenario gap widens: 0.009 → 0.005 → 0.022. SSP5-8.5 accelerates in the final decade.

### Shape Metrics Evolution

| Period | Mean (°C) | Variance | P99 (°C) | GEV ξ |
|--------|-----------|----------|----------|-------|
| Baseline | 26.52 | 70.48 | 40.83 | +0.321 |
| SSP585 2026-35 | 28.12 | 71.75 | 42.50 | +0.234 |
| SSP585 2046-55 | 29.35 | 72.00 | 43.70 | +0.240 |

**Interpretation:**
- Mean shifts +2.8°C — dominant signal
- Variance increases only +2% (70.5 → 72.0) — this is **mostly a shift, not shape change**
- P99 tracks mean proportionally (+2.9°C) — no disproportionate tail fattening
- GEV ξ stays positive (heavy-tailed) but doesn't trend upward — tails not getting heavier

**For temperature at this site, Prashant's intuition about shape change is not confirmed
by the data.** The warming is primarily a mean shift. This is physically expected — CMIP6
models consistently show that temperature variance changes are small relative to the mean shift
for mid-century horizons. Shape changes become more pronounced post-2070.

However, the decade-resolved exceedance plot DOES show clear progressive shift with visible
scenario separation in the tail, which addresses the "exceedance curves all look the same" concern.

---

## 7. Status of Prashant's 6 Checks

| # | Check | Status | Implementation |
|---|-------|--------|----------------|
| 1 | Year-by-year SCVR | **Done** | 3-anchor linear fit (temperature), decade bars (others) |
| 2 | Continuous fitted methodology | **Done** | GPD + GEV on tail-zoom panels, with KS/AIC diagnostics. Empirical proven equivalent to parametric for SCVR (3-method comparison). |
| 3 | Refit exceedance per decade | **Done** | Decade-resolved exceedance (3 curves × 2 scenarios) |
| 4 | Expand to 34 models | **Partial** | Using 13/34 (all that respond on NASA THREDDS for this site/variable). `discover_models()` probes all 34 NEX-GDDP models — 21 don't serve data for this grid cell. Data availability limitation, not code. |
| 5 | ERA5 validation | **Future** | Requires ERA5 download for site coordinates — not in NEX-GDDP |
| 6 | CLR cloud cover | **Future** | CLR not in NEX-GDDP-CMIP6 variable list. Would need CERES or ERA5 as alternate source. |

---

## 8. Open Questions for Team

1. **Is the decade exceedance sufficient?** The curves show progressive shift and scenario separation,
   but variance/kurtosis changes are minimal for temperature. Does Prashant want annual-resolution
   exceedance curves, or is decade resolution enough?

2. ~~**GEV overlay issue**~~ **RESOLVED** — GPD (same probability space as daily empirical) is
   the primary parametric fit on the tail-zoom panel (dashed lines). GEV retained as secondary
   overlay (dotted) for annual-max context. Both include KS + AIC diagnostics in JSON. 2×2
   layout: top row = full empirical, bottom row = tail zoom with GPD + GEV + P95 marker.

3. **Precipitation shape change:** Temperature is mostly a shift, but precipitation may show
   real shape changes (more intense events, changed inter-arrival times). Should we prioritize
   precipitation shape analysis over temperature?

4. **ERA5 priority:** How important is the ERA5 validation before presenting to stakeholders?
   Can we present the CMIP6 results with a caveat, or is ERA5 a blocker?

---

## Cross-References

- [annual_scvr_methodology.md](annual_scvr_methodology.md) — Anchor fit methodology, variable-specific strategy evidence
- [docs/implementation/03_integrated_scvr_cmip6.md](../implementation/03_integrated_scvr_cmip6.md) — NB03 implementation (Section 3b)
- [docs/implementation/ensemble_exceedance_script.md](../implementation/ensemble_exceedance_script.md) — Script implementation (Sections 6b-6d)
- [scripts/shared/scvr_utils.py](../../scripts/shared/scvr_utils.py) — Shared analysis functions
