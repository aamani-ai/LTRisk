# LTRisk Learning Guide

A comprehensive guide to the climate science, data engineering, and financial methodology behind the LTRisk project. Start from the top if you're new, or jump to any section.

---

## Section A: Climate Foundations

| # | Topic | What You'll Learn |
|---|---|---|
| [01](01_climate_primer.md) | **Climate Science Primer** | Climate vs weather, greenhouse effect, what warming means for Texas assets, all 7 variables with units and SCVR direction, extreme events, feedback loops |
| [02](02_cmip6_models.md) | **CMIP6 and Climate Models** | What a climate model simulates, CMIP6 history, the 34 NEX-GDDP models, ensemble approach, bias correction, model naming conventions |
| [03](03_scenarios_and_time_windows.md) | **Scenarios and Time Windows** | All 5 SSP pathways, why we use SSP2-4.5 + SSP5-8.5, why 1985-2014 baseline, why 2026-2055 future, why the gap is correct, ensemble pooling mechanics |

## Section B: SCVR Methodology

| # | Topic | What You'll Learn |
|---|---|---|
| [04](04_scvr_methodology.md) | **SCVR Methodology** | Definitive reference: step-by-step computation, empirical vs theoretical exceedance (deep dive), trapezoid error analysis, actual code, edge cases, interpretation guide |
| [05](05_variables_and_use_cases.md) | **Variables and Asset Use Cases** | What SCVR means per variable, failure pathways, real Hayhurst Solar walkthrough, Maverick Creek Wind walkthrough, solar vs wind comparison |
| [06](06_scenario_comparison.md) | **Scenario Comparison** | SSP2-4.5 vs SSP5-8.5 — how much the emissions pathway changes SCVR, and when to use each |

## Section C: Financial Translation

| # | Topic | What You'll Learn |
|---|---|---|
| [07](07_hcr_hazard_change.md) | **HCR: Hazard Change Ratio** | How SCVR translates to hazard-specific impact — non-linear tail amplification, variable-to-hazard mapping, annual HCR computation, scaling factors, worked examples for heat and precipitation, negative HCR (warming benefits), compound events |
| [08](08_efr_equipment_degradation.md) | **EFR: Equipment Degradation** | Peck's thermal aging (deep dive), Coffin-Manson thermal cycling, Palmgren-Miner wind fatigue, temperature coefficient derating, combining EFR, IUL computation, standard vs climate degradation, the revised generation formula |
| [09](09_nav_impairment_chain.md) | **NAV Impairment Chain** | The complete SCVR → HCR → EFR → CFADS → NAV pipeline with annual framing, CFADS chart overlay, three channels of financial impact, worked examples with real dollar amounts, investor/lender/insurance perspectives |

## Section D: Technical Reference

| # | Topic | What You'll Learn |
|---|---|---|
| [10](10_data_pipeline.md) | **Data Pipeline** | THREDDS server, NCSS point extraction, NetCDF format, the calendar problem, two-level caching, unit conversion, model probing, full fetch loop |
| [11](11_distribution_shift_methods.md) | **Distribution Shift Methods** | How SCVR relates to Wasserstein W1, CVaR, AAL, KS statistic, PSI, and non-stationary hydrology — the full cross-industry landscape |

---

## Reading Orders

**If you're completely new to climate science:**
> 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09

**If you understand climate basics but not our methodology:**
> 03 → 04 → 05 → 07 → 08 → 09

**If you just want to understand the code in Notebook 03:**
> 04 → 10 → 03

**If you want the financial / business perspective:**
> 09 (then 07 → 08 for the deep dives, then 04 for SCVR details)

**If you want to apply SCVR to a specific asset:**
> 04 → 05 (solar or wind section)

**If a quant reviewer asks about methodology:**
> 04 → 11 → 07 → 08

**If you're building Notebook 04 (HCR + EFR):**
> 07 → 08 → 09 → 04 (implementation reference path)

---

## Quick Reference

### The Formula

```
SCVR = (area_future - area_baseline) / area_baseline

Where area = trapezoid integral of daily values
             sorted descending over exceedance probability [0, 1]
```

### Full Chain (Annual)

```
Phase A — Compute Parameters (sequential, once per scenario):

  SCVR(t) = exceedance area shift for year t
  HCR(t)  = SCVR(t) × hazard_scaling_factor
  EFR(t)  = f(HCR(t), Peck's, Coffin-Manson, Palmgren-Miner)

Phase B — Apply to Cash Flows (simultaneous, every year):

  Gen(t) = Gen_base(t) × (1-std_degrad)^t × (1-climate_degrad(t)) × (1-hazard_BI(t))
  NAV    = Σ Gen(t) × price(t) × discount(t)  over IUL years
```

### Magnitude Table

| SCVR Range | Label | Physical Meaning |
|:---:|:---:|---|
| 0.00 – 0.10 | Low | <10% shift — within natural variability range |
| 0.10 – 0.30 | Moderate | 10–30% shift — detectable trend, monitor closely |
| 0.30 – 0.60 | High | 30–60% shift — significant impact on asset operations |
| > 0.60 | Very High | >60% — review carefully, check for tail sensitivity |

### Variable Quick Reference

| Variable | Unit | scvr_direction | Worst Sign | Asset |
|---|---|---|---|---|
| tasmax | °C | higher_is_worse | + | Both |
| tasmin | °C | lower_is_worse_for_freeze | + | Both |
| tas | °C | higher_is_worse | + | Both |
| pr | mm/day | extremes_both_directions | ± | Both |
| sfcWind | m/s | higher_extremes_are_worse | + | Wind |
| hurs | % | context_dependent | + (heat) / − (drying) | Both |
| rsds | MJ/m²/day | **not a SCVR variable** | N/A | Solar performance only |

### Key Periods

```
Baseline:  1985 ────────────── 2014   (30 yrs, CMIP6 historical experiment)
Gap:                2015 ─ 2025       (intentional — not used)
Future:                  2026 ──────────────── 2055   (30-yr asset lifetime)
```

### Real Numbers (Hayhurst Solar, Notebook 01)

| Variable | 2030 | 2040 | 2050 | Trend |
|---|---|---|---|---|
| tasmin | +9.2% | +14.8% | +17.9% | Strong ↑ — dominant signal |
| tas | +5.9% | +10.1% | +12.5% | Steady ↑ |
| tasmax | +4.2% | +7.4% | +9.2% | Consistent ↑ |
| hurs | ~0% | −3.2% | −7.9% | Declining ↓ |
| pr | +11.9% | +1.1% | −17.8% | Inverts ~2040 |
| sfcWind | +0.2% | ~0% | +0.4% | Flat |
| rsds | +0.9% | +1.1% | +1.7% | Small ↑ |

### NAV Impairment Summary

| Asset | SSP2-4.5 | SSP5-8.5 | Dominant Driver |
|---|---|---|---|
| Hayhurst Solar | ~$3.0M (5.0%) | ~$5.9M (9.8%) | Peck's thermal aging (tasmin) |
| Maverick Wind | ~$0M (~0%) | ~$0.5M (~1%) | Icing reduction offsets |

### Key Files

| File | Purpose |
|---|---|
| `notebook_analysis/03_integrated_scvr_cmip6.ipynb` | Main SCVR computation notebook |
| `data/schema/sites.json` | Site coordinates and metadata |
| `data/schema/variables.json` | Variable definitions and scvr_direction |
| `data/schema/scvr_schema.json` | Output Parquet column specification |
| `data/processed/scvr/<site>/cmip6_ensemble_scvr.parquet` | SCVR output |
| `data/cache/thredds/` | Cached NetCDF files and probe results |
