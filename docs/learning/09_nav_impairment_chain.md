# NAV Impairment — The Complete Chain

**This document ties everything together: the full annual pipeline from SCVR to dollar-denominated asset impairment.** It shows how the five-step chain overlays on the CFADS (Cash Flow Available for Debt Service) chart — the investor's primary decision tool.

For the deep dives on individual steps, see [doc 07 (HCR)](07_hcr_hazard_change.md) and [doc 08 (EFR)](08_efr_equipment_degradation.md).

---

## 1. The Chain at a Glance

```
SCVR(t)  ───►  HCR(t)  ───►  EFR(t)  ───►  CFADS_adjusted(t)  ───►  NAV impairment
(climate)      (hazard)      (failure)      (annual cash flow)       (dollar value)

  Phase A: Compute Parameters              Phase B: Apply to Cash Flows
  ──────────────────────────              ──────────────────────────────
  Sequential: must compute                Simultaneous: EFR + HCR modify
  SCVR before HCR, HCR before EFR.       every year's cash flow at once.
  Run once per scenario.                  Run across all years.
```

**Critical distinction:** The five steps are NOT five sequential cash flow adjustments. They are a **parameter computation pipeline** (Phase A) whose outputs **modify cash flows simultaneously** at every time step (Phase B).

```
Year:    2026   2027   ...   2035   ...   2040   ...   2050   ...   2055
─────    ────   ────         ────         ────         ────         ────
SCVR(t): 0.02   0.02  ...   0.06  ...    0.07  ...    0.09  ...    0.10
HCR(t):  0.05   0.05  ...   0.14  ...    0.19  ...    0.23  ...    0.25
EFR(t):  0.03   0.03  ...   0.07  ...    0.10  ...    0.13  ...    0.14

CFADS_base(t):   $3.2M  $3.2M ...  $3.0M ...   $2.9M ...   $2.7M ...  $2.5M
CFADS_adj(t):    $3.1M  $3.1M ...  $2.8M ...   $2.6M ...   $2.3M ...  $2.0M
                 ─────                          ─────              ─────
                 small gap                     growing gap         large gap
```

---

## 2. How It Maps to the CFADS Chart

The CFADS chart is the central financial tool for infrastructure debt and equity investors. Climate risk manifests as three visible effects on this chart:

```
CFADS ($M/yr)
     ▲
 3.5 │ ████
     │ ████ █████
 3.0 │ ████ █████ █████
     │ ████ █████ █████ █████              ← Standard CFADS (no climate)
 2.5 │ ████ █████ █████ █████ █████
     │ ████ █████ █████ █████ █████ █████
 2.0 │ ████─█████─█████─█████─█████─█████─█████         ← DSCR covenant
     │ ████ █████ █████ █████ █████ █████ █████ █████
 1.5 │ ████ █████ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░
     │ ████ █████ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░
 1.0 │ ████ █████ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░
     │ ████ █████ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░     │
 0.5 │ ████ █████ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░     │
     └──────────────────────────────────────────────────────────────┘
     Y1   Y3    Y5    Y7    Y10   Y13   Y16   Y19   Y21   Y25

  ████ = Climate-adjusted CFADS (the actual cash flow)
  ░░░░ = Climate-adjusted CFADS (continued)
  Top of bars = Standard CFADS (without climate adjustment)
  ─── = DSCR 1.0× debt service covenant

  THREE VISIBLE EFFECTS:
  ─────────────────────

  1. STEEPER SLOPE     EFR-driven: panels degrade faster
     (bars shrink       → each year generates less power
      faster over       → standard 0.5%/yr becomes 0.55-0.6%/yr
      time)

  2. DEEPER TROUGHS    HCR/BI-driven: more hazard events
     (occasional        → heat wave shutdowns, flood downtime
      dips below        → lost generation hours = lost revenue
      smooth trend)

  3. EARLIER END       IUL: asset reaches end-of-life sooner
     (bars stop         → 25 years → 20.7-22.8 years
      at year 21        → final years of revenue disappear
      not year 25)      → THIS IS THE BIGGEST NAV IMPACT
```

### DSCR Covenant Breach

```
DSCR (Debt Service Coverage Ratio) = CFADS / Debt Service

If DSCR < 1.0:  cash flow cannot cover debt payments
If DSCR < 1.2:  lender covenant typically breached → restricted distributions

Standard model:  DSCR stays above 1.2× through year 22
Climate-adjusted: DSCR may breach 1.2× by year 18-19

This 3-4 year acceleration in DSCR thinning is critical for lenders.
Climate risk can push covenant breach EARLIER than projected.
```

---

## 3. Three Channels of Financial Impact

Climate risk flows to NAV through three distinct channels:

```
CHANNEL 1: BUSINESS INTERRUPTION (from HCR)
──────────────────────────────────────────
  More hazard events → more shutdown hours → less generation

  BI_loss(t) = Σ_hazards [HCR_h(t) × baseline_BI_h × revenue_rate]

  Hayhurst SSP5-8.5:
    Heat shutdowns:    ~$63.5K/yr additional by 2040s
    Heat derating:     ~$17.4K/yr additional
    Soiling (drying):  ~$20K/yr additional O&M
    Total BI:          ~$100K/yr by 2040s

  NAV impact (PV of BI over IUL): ~$1.0-1.5M


CHANNEL 2: EQUIPMENT DEGRADATION (from EFR — DOMINANT)
──────────────────────────────────────────────────────
  Faster aging → shorter useful life → less lifetime revenue

  IUL_shortening_cost = Σ_{t=IUL}^{EUL} NCF(t) × discount_factor(t)

  Hayhurst SSP5-8.5:
    Years lost: 2.2-4.3 years (range from linearised to full Peck's)
    Annual NCF: ~$1.78M/yr
    PV of lost years: ~$2.8-5.1M

  NAV impact: ~$2.8-5.1M  (THIS IS THE DOMINANT TERM)


CHANNEL 3: PERFORMANCE / RESOURCE (negligible)
──────────────────────────────────────────────
  Resource change → different generation

  rsds SCVR ≈ +0.002:   Tiny irradiance increase → small upside
  sfcWind SCVR ≈ 0:     No wind change

  Hayhurst rsds upside (PV): ~$0.4M

  NAV impact: ~-$0.4M (offset — reduces total impairment)
  This is < 0.7% of asset value — negligible.

  KEY INSIGHT: "The resource is stable. Climate risk for renewable
  assets is NOT about the resource changing — it's about the
  equipment degrading faster under more extreme conditions."
```

---

## 4. Complete Worked Example: Hayhurst SSP5-8.5

### Input Parameters

```
Asset value:          $60M
Capacity:             24.8 MW
Capacity factor:      25%
Annual generation:    54,300 MWh
PPA / revenue rate:   $40/MWh
Annual revenue:       $2.17M
Annual OpEx:          ~$0.4M
Annual NCF:           ~$1.78M/yr
WACC (discount rate): 10%
EUL:                  25 years
```

### Annual Chain at Years 5, 10, 15

```
                          Year 5 (2031)   Year 10 (2036)  Year 15 (2041)
                          ─────────────   ──────────────  ──────────────
SCVR_tasmax:              0.035           0.058           0.078
SCVR_tas:                 0.032           0.054           0.074
SCVR_hurs:               −0.005          −0.015          −0.035

HCR_heat (×2.5):          0.088           0.145           0.195
HCR_flood:                0.12            0.08            0.02

EFR_peck (net):            0.04            0.07            0.11
EFR_coffin:                0.01            0.02            0.03
EFR_combined:              0.04            0.06            0.10

Std degradation:          −2.5%           −4.9%           −7.2%
Climate degradation:      −0.1%           −0.3%           −0.8%
Hazard BI loss:           −0.4%           −0.7%           −1.0%

Gen (standard):           52,942 MWh      51,639 MWh      50,390 MWh
Gen (climate-adj):        52,677 MWh      51,123 MWh      49,359 MWh
Annual loss:               265 MWh          516 MWh        1,031 MWh
At $40/MWh:               $10.6K/yr        $20.6K/yr       $41.2K/yr
```

### NAV Impairment Calculation

```
CHANNEL 1 — Business Interruption:
  PV of BI losses over 20.7-year IUL:
  Heat + soiling + flood BI: ~$1.2M

CHANNEL 2 — IUL Shortening:
  Lost years: 4.3 years (using full Peck's)
  Revenue in years 21-25 (undiscounted): 4.3 × $1.78M = $7.65M
  PV at 10% (discounted to year 0, midpoint ~year 23): ~$5.1M

CHANNEL 3 — rsds upside (offset):
  Slightly higher irradiance → ~$0.4M NPV benefit

TOTAL:
  NAV impairment = $1.2M + $5.1M − $0.4M = $5.9M

  On $60M asset: $5.9M / $60M = 9.8% NAV impairment

  ┌─────────────────────────────────────────┐
  │  HAYHURST SOLAR SSP5-8.5                │
  │  NAV impairment: $5.9M (9.8%)          │
  │    Channel 2 (IUL): $5.1M  (86%)       │
  │    Channel 1 (BI):  $1.2M  (20%)       │
  │    Channel 3 (rsds): −$0.4M (−7%)      │
  └─────────────────────────────────────────┘
```

---

## 5. Hayhurst SSP2-4.5 — Scenario Delta

```
Under the moderate emissions pathway:

  SCVR_tasmax (2040): ~0.050 (vs 0.074 under SSP585)
  EFR_combined:       ~0.10 (vs 0.17)
  IUL:                22.5 years (vs 20.7)
  Years lost:         2.5 (vs 4.3)

  Channel 1 (BI):     ~$0.6M
  Channel 2 (IUL):    ~$2.8M
  Channel 3 (rsds):   −$0.4M
  ─────────────────────────────
  Total impairment:   ~$3.0M (5.0% of $60M)

  SCENARIO DELTA:
    SSP5-8.5 impairment:  $5.9M (9.8%)
    SSP2-4.5 impairment:  $3.0M (5.0%)
    ─────────────────────────────────────
    Difference:           $2.9M (~5 percentage points)

  "The emission pathway choice is worth ~$2.9M on this one asset."
```

---

## 6. Maverick Wind — Comparison

```
Maverick Creek Wind, SSP5-8.5:

  sfcWind SCVR ≈ 0 → Palmgren-Miner EFR ≈ 0
  EFR_combined ≈ 0.04 (minor thermal effects only)
  IUL = 25 × 0.96 = 24 years (1 year lost)

  Channel 1 (BI):     ~$0.5M (minor heat + flood)
  Channel 2 (IUL):    ~$1.0M (1 year of revenue)
  Icing benefit:       −$1.0M to −$2.0M (fewer icing shutdowns)
  ─────────────────────────────────────────────
  Total impairment:   ~$0.5-1.5M (~0.5-1.5% on comparable basis)
```

---

## 7. NAV Summary Table

```
                       SSP2-4.5              SSP5-8.5
                       ────────              ────────
HAYHURST SOLAR
  IUL shortening:      ~$2.8M                ~$5.1M
  BI + O&M losses:     ~$0.6M                ~$1.2M
  rsds upside:         −$0.4M                −$0.4M
  ──────────────────────────────────────────────────
  Total impairment:    ~$3.0M (5.0%)         ~$5.9M (9.8%)

MAVERICK WIND
  IUL shortening:      ~$0.5M                ~$1.0M
  BI losses:           ~$0.3M                ~$0.5M
  Icing benefit:       −$1.0M                −$1.0M
  ──────────────────────────────────────────────────
  Total impairment:    ~$0.0M (~0%)          ~$0.5M (~1%)

KEY RATIOS:
  Solar/Wind:          Solar is ~10× more impaired
  SSP585/SSP245:       High emissions roughly doubles impairment
  IUL/BI:              IUL shortening is ~4× larger than BI losses
```

---

## 8. Investor and Lender Perspective

### Equity Investor View

```
WITHOUT climate adjustment:
  Asset value = $60M
  Expected return = 8%/year over 25 years
  → Seems like a solid infrastructure investment

WITH climate adjustment (SSP2-4.5):
  Asset value = $60M − $3.0M = $57.0M
  Effective return ≈ 7.6%/year over 22.5 years
  → Still investable, but lower return
  → May still clear a 7% hurdle rate

WITH climate adjustment (SSP5-8.5):
  Asset value = $60M − $5.9M = $54.1M
  Effective return ≈ 6.8%/year over 20.7 years
  → MARGINAL — might not meet 7% hurdle rate
  → Requires repricing or risk premium

DELTA: The emission pathway choice swings IRR by ~0.8 percentage points.
For a portfolio of 50 similar assets, that's material.
```

### Lender View

```
DSCR IMPACT:

  Standard projection:     DSCR stays above 1.2× through year 22
  Climate-adjusted (245):  DSCR may thin to 1.2× by year 20
  Climate-adjusted (585):  DSCR may breach 1.2× by year 18

  For lenders, the question is: when does the cash flow cushion erode?

  Earlier DSCR thinning means:
    → Restricted distributions to equity sooner
    → Potential covenant breach triggers
    → LTV (Loan-to-Value) ratio shifts unfavorably

  Climate risk = credit risk for infrastructure debt.
```

### Insurance View

```
TAIL RISK PRICING:

  SSP5-8.5 shows more extreme outcomes:
    → Higher heat wave frequency → more BI claims
    → More extreme precipitation → more flood claims
    → Longer dry spells → higher wildfire exposure

  Insurers should use SSP5-8.5 for tail-risk pricing:
    → Premiums may need to increase 5-15% for solar assets
    → Wind farms may see premium stability or slight decrease
       (icing reduction offsets flood risk increase)

  SCVR provides the quantitative basis for these pricing decisions.
```

---

## 9. Where Each Notebook Fits — Updated Pipeline Map

```
NOTEBOOK PIPELINE (with annual framing)

  NB 01: Climate Indices (annual hazard counts)
         ├── heat_wave_days(t), frost_days(t), rx5day(t), fwi_mean(t)
         ├── Used for HCR cross-validation (see doc 07 §10)
         └── Output: annual climate indices per site

  NB 02: NEX-GDDP THREDDS Pipeline
         ├── Fetches daily data from THREDDS servers
         ├── Handles cftime calendars, unit conversion, caching
         └── Output: daily climate data (NetCDF / Parquet)

  NB 03: SCVR Computation (NEEDS REFACTORING → annual)
         ├── Currently: 5 target years with 20-year rolling windows
         ├── Target: Annual SCVR(t) for each year 2026-2055
         ├── Uses all available CMIP6 models (up to 34)
         └── Output: Annual SCVR Parquet per site per scenario

  NB 04: HCR + EFR Computation (TO BUILD — reference: docs 07, 08)
         ├── Reads annual SCVR from NB03
         ├── Computes HCR(t) per hazard using scaling factors
         ├── Computes EFR(t) using Peck's, Coffin-Manson, Palmgren-Miner
         ├── Cross-validates HCR against NB01 climate indices
         └── Output: Annual HCR and EFR Parquet per site per scenario

  NB 05+: Financial Model / NAV Impairment (FUTURE)
         ├── Reads HCR + EFR from NB04
         ├── Applies to CFADS cash flow model
         ├── Computes NAV impairment, DSCR trajectory, IRR adjustment
         └── Output: Dollar-denominated climate risk assessment

  scripts/presentation/ensemble_exceedance.py:
         ├── Currently: computes one SCVR per entire period
         ├── Target: SCVR progression plot over time (annual)
         └── Used for presentation visualisation
```

```
DATA FLOW:

  THREDDS → daily NetCDF → SCVR(t) → HCR(t) → EFR(t) → CFADS_adj(t) → NAV
  (NB02)    (cache)        (NB03)    (NB04)    (NB04)    (NB05)         (NB05)
                             ↑
                             │
                    NB01 climate indices
                    (cross-validation)
```

---

## 10. Key Terminology — Compact Glossary

| Term | Full Name | What It Is | Computed In |
|------|-----------|-----------|-------------|
| **SCVR** | Severe Climate Variability Rating | Fractional shift in exceedance curve area between baseline and future | NB03 |
| **HCR** | Hazard Change Ratio | Climate-to-hazard translation: SCVR × scaling factor | NB04 |
| **EFR** | Equipment Failure Ratio | Hazard-to-degradation translation via engineering models (Peck's, C-M, P-M) | NB04 |
| **IUL** | Impaired Useful Life | Expected operational lifetime shortened by climate-driven degradation | NB04 |
| **EUL** | Expected Useful Life | Design lifetime without climate adjustment (25 yrs solar, 25-35 yrs wind) | Input |
| **NAV** | Net Asset Value | Financial value of the asset, reduced by climate impairment | NB05 |
| **BI** | Business Interruption | Revenue lost due to climate-caused downtime (heat shutdowns, flooding) | NB04/05 |
| **CFADS** | Cash Flow Available for Debt Service | Annual cash flow after OpEx, before debt payments | Financial model |
| **DSCR** | Debt Service Coverage Ratio | CFADS / debt service — must stay above 1.0-1.2× | Financial model |
| **NCF** | Net Cash Flow | Revenue minus operating expenses | Financial model |
| **WACC** | Weighted Average Cost of Capital | Discount rate for NPV calculations (10% for this pilot) | Input |
| **SSP** | Shared Socioeconomic Pathway | Future emission scenario — we use SSP2-4.5 and SSP5-8.5 | CMIP6 |
| **STC** | Standard Test Conditions | Reference conditions for solar panel rating: 25°C, 1000 W/m², AM1.5 | Industry standard |

---

## 11. The "Without SCVR" Problem

```
WITHOUT SCVR:
  "Climate change will make things hotter and wetter."
  → Cannot quantify financial impact
  → Investors use qualitative judgments
  → Climate risk is either ignored or overestimated

WITH SCVR → HCR → EFR → NAV:
  "+0.084 tasmax SCVR"               (8.4% distribution shift)
  → "+0.21 heat HCR"                (21% more heat hazard)
  → "+0.16 EFR"                     (16% faster aging via Peck's)
  → "IUL = 20.7 years"              (4.3 years lost)
  → "$5.9M NAV impairment"          (9.8% of $60M asset)

  Every step is:
    ✓ Quantitative (a number, not a qualitative label)
    ✓ Traceable (can audit back to daily climate data)
    ✓ Annual (maps to cash flow model at each time step)
    ✓ Scenario-aware (different SSP = different dollar answer)

SCVR is the bridge that makes climate science useful for
financial decision-making, insurance pricing, and asset valuation.
```

---

## Next

- [07 - HCR: Hazard Change Ratio](07_hcr_hazard_change.md) — Deep dive on climate-to-hazard translation
- [08 - EFR: Equipment Degradation](08_efr_equipment_degradation.md) — Deep dive on engineering degradation models
- [04 - SCVR Methodology](04_scvr_methodology.md) — How SCVR is computed (the foundation of the chain)

Return to [Index](00_index.md) for the full learning guide table of contents.
