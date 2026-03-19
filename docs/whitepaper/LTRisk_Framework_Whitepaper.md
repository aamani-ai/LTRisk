# LTRisk Framework
## Climate-Adjusted Infrastructure Valuation

> A comprehensive methodology for quantifying how climate change shifts physical variable
> distributions and translates those shifts into equipment failure costs, cash flow adjustments,
> and net asset value impairment for renewable energy infrastructure.

---

| Field          | Value                                                            |
|----------------|------------------------------------------------------------------|
| Version        | Internal Technical Review                                        |
| Scope          | End-to-End Methodology with Mathematical Foundations             |
| Data Source    | NASA NEX-GDDP-CMIP6 (34 GCMs, 0.25° grid)                      |
| Scenarios      | SSP2-4.5 (moderate), SSP5-8.5 (high emissions)                  |
| Classification | Internal — Technical Working Document                            |
| Author Org     | InfraSure                                                        |
| Date           | March 2026                                                       |

---

## Table of Contents

- [Master Pipeline](#master-pipeline)
- [Section A — Climate Foundations](#section-a--climate-foundations)
  - [A1. Data Pipeline — NASA to Notebook](#a1-data-pipeline--nasa-to-notebook)
  - [A2. CMIP6 Models and Ensemble Strategy](#a2-cmip6-models-and-ensemble-strategy)
  - [A3. Scenarios and Time Windows](#a3-scenarios-and-time-windows)
  - [A4. Variables and Use Cases](#a4-variables-and-use-cases)
- [Section B — SCVR Methodology](#section-b--scvr-methodology)
  - [B1. Mathematical Definition — Wasserstein W1 and Beyond](#b1-mathematical-definition--wasserstein-w1-and-beyond)
  - [B2. SCVR in the Distribution Shift Landscape](#b2-scvr-in-the-distribution-shift-landscape)
  - [B3. Empirical vs Parametric — Why SCVR's Choices Are Defensible](#b3-empirical-vs-parametric--why-scvrs-choices-are-defensible)
  - [B4. Annual SCVR — Options A, B, and C](#b4-annual-scvr--options-a-b-and-c)
  - [B5. Performance Adjustment Analysis (Channel 3)](#b5-performance-adjustment-analysis-channel-3)
- [Section C — Financial Translation](#section-c--financial-translation)
  - [C1. HCR — Hazard Change Ratios](#c1-hcr--hazard-change-ratios)
  - [C2. EFR — Equipment Failure Replacement Costs](#c2-efr--equipment-failure-replacement-costs)
  - [C3. Cash Flow Integration — CFADS and DSCR](#c3-cash-flow-integration--cfads-and-dscr)
  - [C4. NAV Impairment Chain](#c4-nav-impairment-chain)
  - [C5. Worked Example — Hayhurst Solar Year 10](#c5-worked-example--hayhurst-solar-year-10)
- [Section D — Technical Reference](#section-d--technical-reference)
  - [D1. Variable-Specific SCVR Findings](#d1-variable-specific-scvr-findings)
  - [D2. Scenario Comparison — SSP2-4.5 vs SSP5-8.5](#d2-scenario-comparison--ssp2-45-vs-ssp5-85)
  - [D3. Engineering Reliability Models](#d3-engineering-reliability-models)
  - [D4. Implementation Roadmap](#d4-implementation-roadmap)
  - [Case Study Summary](#case-study-summary)
- [Section E — Critical Assessment & Future Direction](#section-e--critical-assessment--future-direction)
  - [E1. What Is Genuinely Novel](#e1-what-is-genuinely-novel)
  - [E2. Where We Are Applying Existing Work](#e2-where-we-are-applying-existing-work)
  - [E3. External Work We Should Incorporate](#e3-external-work-we-should-incorporate)
  - [E4. Strategic Priorities & Open Questions](#e4-strategic-priorities--open-questions)
- [Living Document Note](#living-document-note)

---

> **Reading Guide:** Executives should start with the Master Pipeline diagram and Section C (Financial Translation). Quantitative reviewers should focus on Section B (SCVR Methodology) for mathematical rigor. Engineers should refer to Section D for implementation details. Section E provides an honest self-assessment of novelty, gaps, and strategic priorities.

---

## Master Pipeline

The LTRisk framework is a **six-stage pipeline** that begins with raw climate model output and ends with a dollar-denominated net asset value impairment. Each stage is independently auditable and produces a named intermediate metric. The pipeline's power lies in its modularity: each stage can be validated, stress-tested, or replaced independently without breaking the rest of the chain.

```
FIGURE 1: End-to-End LTRisk Pipeline

┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Climate   │     │    SCVR     │     │     HCR     │     │     EFR     │     │    CFADS    │     │     NAV     │
│    Data     │────▶│             │────▶│             │────▶│             │────▶│             │────▶│             │
│             │     │             │     │             │     │             │     │             │     │             │
│  NASA NEX   │     │ Distribution│     │   Hazard    │     │  Equipment  │     │  Cash Flow  │     │  Net Asset  │
│   CMIP6     │     │    Shift    │     │   Change    │     │   Failure   │     │  Adjusted   │     │    Value    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘

     [1]                  [2]                  [3]                  [4]                  [5]                  [6]
```

The pipeline translates climate data through physical science (SCVR), hazard physics (HCR), cost accounting (EFR), and financial modeling (CFADS) to arrive at a single auditable impairment number (NAV). Each intermediate metric is named, calculable, and independently defensible to counterparties.

| Stage        | Input                              | Output                          | Key Metric                          |
|--------------|------------------------------------|---------------------------------|-------------------------------------|
| Climate Data | NASA NEX-GDDP-CMIP6                | Daily time series per variable  | 7 variables, 6 models               |
| SCVR         | Pooled daily distributions         | Fractional distribution shift   | SCVR(t) per variable (anchor-based) |
| HCR          | SCVR values + physics models       | Hazard-specific change ratios   | HCR(t) per hazard                   |
| EFR          | HCR + equipment cost schedules     | Annual failure cost adjustment  | EFR(t) in $/year                    |
| CFADS        | Base cash flows + EFR              | Climate-adjusted CFADS          | CFADS(t) = Base - EFR(t)            |
| NAV          | CFADS(t) time series               | DCF impairment vs base case     | % NAV loss                          |

---

## Section A — Climate Foundations

This section describes the climate data infrastructure that underpins all downstream calculations. Understanding the data source, its limitations, and the design choices made in the pipeline is essential context for interpreting SCVR values. Every number in Sections B, C, and D ultimately traces back to the data architecture described here.

---

### A1. Data Pipeline — NASA to Notebook

LTRisk sources all climate data from the **NASA NEX-GDDP-CMIP6** dataset, hosted on NASA's NCCS (NASA Center for Climate Simulation) THREDDS servers in Greenbelt, Maryland. The dataset contains daily output from 34 CMIP6 global climate models, downscaled to a **0.25-degree (~25 km) global grid** using the BCSD (Bias-Correction Spatial Disaggregation) method. BCSD corrects for systematic model biases relative to observational products, making the data suitable for site-level applications.

```
FIGURE 2: Data Pipeline from NASA Servers to Processed Daily Distributions

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐
│  NASA NCCS   │     │   THREDDS    │     │    Point     │     │    Unit      │     │    Pooled Daily      │
│   Servers    │────▶│    NCSS      │────▶│  Extraction  │────▶│  Conversion  │────▶│   Distributions      │
│              │     │              │     │              │     │              │     │                      │
│  ~50 TB      │     │  HTTP NCSS   │     │  ~5 KB per   │     │  K→°C        │     │  6 models x 30 yrs   │
│  global      │     │  endpoint    │     │  grid cell   │     │  kg/m²/s     │     │  x 365 days          │
│  data        │     │  request     │     │  (vs 500 MB  │     │  → mm/day    │     │  = ~65,700 values    │
│              │     │              │     │  full file)  │     │              │     │  per distribution    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────────────┘

                 Data reduction factor: ~100,000x (500 MB → ~5 KB per point extraction)
```

#### The Critical Architectural Insight: Server-Side Point Extraction

Each global daily NetCDF file is approximately **500 MB**. Rather than downloading entire files, the pipeline sends an HTTP request to the THREDDS NCSS (NetCDF Subset Service) endpoint specifying latitude, longitude, time range, and variable name. The server extracts just the relevant grid cell and returns roughly **5 KB**. This reduces data transfer by a factor of **100,000** and makes the pipeline feasible on commodity hardware — an operation that would otherwise require petabyte-scale infrastructure becomes tractable on a standard workstation.

> **Data volume per site:** 7 variables × 2 scenarios × 6 models × 60 years = 5,040 annual files. Each contains ~365 daily values. Total: approximately **1.84 million daily observations per site**, of which ~65,700 values (6 models × 30 years × 365 days) are pooled per distribution comparison.

#### Unit Conversions

CMIP6 models use SI units internally, which differ from the engineering units used in LTRisk's downstream calculations. The following conversions are applied consistently:

| Variable           | CMIP6 Unit    | LTRisk Unit | Conversion Formula          |
|--------------------|---------------|-------------|------------------------------|
| tasmax, tasmin, tas | Kelvin (K)   | Celsius (°C)| Subtract 273.15              |
| pr (precipitation) | kg/m²/s       | mm/day      | Multiply by 86,400 s/day     |
| sfcWind            | m/s           | m/s         | None (pass-through)          |
| hurs (humidity)    | %             | %           | None (pass-through)          |
| rsds (solar radiation) | W/m²      | W/m²        | None (pass-through)          |

> **Temperature auto-detection:** If a series mean exceeds 200, values are assumed to be in Kelvin and converted. This guards against double-conversion in models that pre-convert to Celsius before writing to NetCDF. This is a defensive programming measure — some GCMs deviate from the CMIP6 variable specification.

#### The Calendar Problem

CMIP6 models use different internal calendars — standard Gregorian, proleptic Gregorian, noleap (365 days always), 360-day (12 × 30), and all-leap (366 days always). Python's native `datetime` module cannot handle non-standard calendars. LTRisk uses the **`cftime` library** to decode time axes with their native calendar, then converts to standard `pandas` `DatetimeIndex` for downstream analysis.

Files are opened with `decode_times=False` to prevent `xarray` from applying its own calendar assumptions — a subtle but critical flag that prevents silent data corruption in edge-case models.

The calendar handling matters because distributional comparisons across models require that "January" in model A refers to the same season as "January" in model B. Without proper calendar normalization, pooling values from different models would mix seasons, introducing spurious distributional shifts.

---

### A2. CMIP6 Models and Ensemble Strategy

**CMIP6** (Coupled Model Intercomparison Project Phase 6) is the most recent generation of global climate models, used in the IPCC AR6 report. The NASA NEX-GDDP-CMIP6 dataset includes 34 participating models from institutions worldwide. Not all models provide data for every variable-scenario combination — availability varies by model, variable, and scenario, so LTRisk dynamically probes model availability before fetching.

#### Ensemble Size: The 6-Model Cap

LTRisk caps at **6 models per variable-scenario-site combination** (first 6 alphabetically from available models). This design choice balances computational cost against ensemble diversity. Daily values from all models and years are pooled into a single distribution — this pooling is deliberate and captures both:

1. **Inter-model spread**: Structural uncertainty across different climate model architectures
2. **Temporal variability**: Natural year-to-year climate variability within each model's projection

> **Why pooling works:** At n = 65,700 daily values (6 models × 30 years × ~365 days), the empirical CDF has converged to the true underlying distribution. Trapezoid integration error is less than **0.0001%**. The inter-model spread is itself useful signal — it captures structural uncertainty in climate projections rather than hiding it behind an ensemble mean.

The 6-model cap is conservative in that larger ensembles would reduce sampling variance further. However, the primary uncertainty in climate projections is structural (which model architecture is correct?) rather than sampling uncertainty, so increasing from 6 to 34 models would add computational cost without proportionally improving the risk estimate.

#### Model Discovery (Probing)

Before fetching data, LTRisk parallel-probes all 34 models using **HTTP HEAD requests** (`ThreadPoolExecutor`, 12 workers):

1. **Step 1:** Probe SSP scenario availability for all 34 models
2. **Step 2:** For models found in Step 1, probe historical experiment availability
3. **Step 3:** Sort available models alphabetically and cap at 6

This three-step probe prevents wasting 30+ minutes on timeout errors from unavailable model-scenario combinations — a real problem in production environments where some THREDDS endpoints respond slowly or not at all. Results are cached in a **JSON probe cache** for instant subsequent runs on the same site.

---

### A3. Scenarios and Time Windows

LTRisk uses two CMIP6 Shared Socioeconomic Pathway (SSP) scenarios, selected to bracket a range of plausible futures rather than predict a single trajectory.

| Parameter              | SSP2-4.5 (Moderate)              | SSP5-8.5 (High Emissions)             |
|------------------------|----------------------------------|---------------------------------------|
| Radiative Forcing      | 4.5 W/m² by 2100                 | 8.5 W/m² by 2100                      |
| CO₂ Trajectory         | Peaks ~2040, slow decline         | Continuous rise through 2100          |
| Temperature (global)   | +2.1 to 3.5°C by 2100            | +3.3 to 5.7°C by 2100                 |
| Narrative              | Middle of the road               | Fossil-fuel intensive                 |
| Use in LTRisk          | Base case for financial models    | Stress test / tail scenario            |

#### Time Windows

| Window   | Period    | Source                          | Purpose                         |
|----------|-----------|---------------------------------|---------------------------------|
| Baseline | 1985–2014 | CMIP6 historical experiment     | Reference distribution          |
| Future   | 2026–2055 | CMIP6 SSP experiments           | Forward-looking projection      |

The **baseline period (1985–2014)** matches CMIP6 conventions and avoids the early satellite era where observations are less reliable. The 30-year window is the climatological standard for computing stable distributional statistics.

The **future window (2026–2055)** is deliberately near-term for two reasons:
1. It aligns with typical infrastructure financing horizons (25–30 years)
2. It represents climate shifts that are largely "locked in" regardless of emissions scenario — SSP divergence between moderate and high-emissions pathways becomes material only after ~2050. This means the scenario choice matters less for near-term assets than most investors assume — a finding with important practical implications for portfolio construction.

---

### A4. Variables and Use Cases

LTRisk tracks seven physical variables from the CMIP6 dataset, each selected for its documented causal pathway to infrastructure damage or performance degradation:

| Variable       | CMIP6 Name | Physical Meaning                       | Infrastructure Impact                          |
|----------------|------------|----------------------------------------|------------------------------------------------|
| Max Temp       | tasmax     | Daily max near-surface air temp        | Module thermal degradation (Peck's model)      |
| Min Temp       | tasmin     | Daily min near-surface air temp        | Freeze-thaw cycling (Coffin-Manson)            |
| Mean Temp      | tas        | Daily mean temperature                 | HVAC load, thermal derating                    |
| Precipitation  | pr         | Daily total precipitation              | Hail damage, flooding, erosion                 |
| Humidity       | hurs       | Near-surface relative humidity         | Corrosion, PID (potential-induced degradation) |
| Wind Speed     | sfcWind    | 10m surface wind speed                 | Structural fatigue (Palmgren-Miner rule)       |
| Solar Radiation| rsds       | Downwelling shortwave radiation flux   | Energy yield resource assessment               |

The variable selection is driven by engineering, not by data availability. The seven variables map directly to established engineering degradation models (see Section D3) that have been validated in equipment reliability literature. Variables without established degradation linkages are excluded to prevent spurious model complexity.

---

## Section B — SCVR Methodology

The **Scenario Climate Variable Ratio (SCVR)** is the analytical core of the LTRisk framework. All downstream financial calculations trace directly back to SCVR values. This section provides complete mathematical foundations, positions SCVR within the broader landscape of distributional shift metrics, justifies its design choices, and explains the three approaches to generating time-series SCVR values for the financial model.

---

### B1. Mathematical Definition — Wasserstein W1 and Beyond

The Scenario Climate Variable Ratio (SCVR) is a **signed, normalized Wasserstein W1 distance** applied to empirical climate variable distributions. It quantifies both the **magnitude** and **direction** of distributional shift between a baseline (historical) period and a future (projected) period.

#### Core Formula

```
SCVR = (Area_future - Area_baseline) / Area_baseline
```

Where:
- **Area** = integral of value over exceedance probability = integral from 0 to 1 of Q(p) dp ≈ E[X] at large n
- **Q(p)** is the quantile function (inverse CDF) — i.e., the value at exceedance probability p
- The integral is computed via the **trapezoidal rule** over the empirical distribution

In plain language: SCVR is the fractional change in the "area under the exceedance curve" between the future and baseline climate periods. A positive SCVR means the distribution shifted toward higher values (warming for temperature, more precipitation for rainfall). A negative SCVR means the distribution shifted toward lower values (cooling or drying).

#### The Exceedance Curve

The exceedance curve — also called the survival function or complementary CDF — plots P(X > x) on the vertical axis against the climate variable value x on the horizontal axis. For any value x, the curve gives the probability that a randomly drawn day will exceed that value.

```
FIGURE 3: Exceedance Curve Comparison — Baseline vs Future

  P(X > x)
  1.0 ┤
      │╲
      │  ╲──────── Baseline (1985-2014)
      │   ╲  ╲
  0.5 ┤    ╲   ╲──────── Future (2026-2055)
      │     ╲    ╲   ░░░░░░░░░░░░░░░░░░
      │      ╲    ╲░░░░░░░░░░░░░░░░░░░
      │       ╲░░░░░╲░░░░░░░░░░░░░░░░░
      │        ░░░░░░ ╲░░░░░░░░░░░░░░░
  0.0 ┤─────────────────────────────────
      └────────────────────────────────▶
             Climate Variable Value

      ░░ = Shaded area (Area_future - Area_baseline)

      SCVR = Shaded Area / Baseline Area

  Interpretation:
  - Rightward shift of the curve = warming/wetting = positive SCVR
  - Leftward shift of the curve = cooling/drying = negative SCVR
  - The shaded area represents the distributional shift captured by SCVR
```

The area under the exceedance curve is exactly the expected value of the variable: integral from 0 to 1 of Q(p) dp = E[X]. This means SCVR can be interpreted as the fractional change in the mean of the distribution — but computed in a way that respects the full shape of the distribution, not just the sample mean.

#### Relationship to Wasserstein W1

The **Wasserstein W1 distance** (also called Earth Mover's Distance or EMD) between two distributions P and Q is defined as the integral of the absolute difference between their CDFs:

```
W1(P, Q) = integral of |F_P(x) - F_Q(x)| dx
```

*Where F_P and F_Q are the cumulative distribution functions (CDFs) of P and Q respectively.*

SCVR differs from raw W1 in three important ways, each of which is deliberate:

**1. Sign-preserving:** SCVR does not take the absolute value — a positive SCVR means the distribution shifted toward higher values (warming for temperature, wetting for precipitation). Raw W1 treats a +2°C shift identically to a -2°C shift, which is physically wrong and financially misleading. Knowing the direction of shift is essential for engineering damage models.

**2. Normalized:** Division by the baseline area converts absolute shift (in physical units) into a dimensionless fractional shift, making SCVR comparable across variables and sites. A raw W1 distance of "+2 degrees" means very different things at a desert site (baseline 38°C) vs a mountain site (baseline 5°C).

**3. Exceedance representation:** SCVR integrates over exceedance probability (the quantile function Q(p)) rather than over the value axis. This is the natural representation for empirical distributions because it handles unequal sample sizes gracefully and aligns with how engineers think about extreme-event frequencies.

#### Why Normalization Matters

Absolute Wasserstein distance is not comparable across variables or sites. Consider the same +2°C distributional shift at two different locations:

| Site                      | Baseline Mean | Shift | SCVR Result    | Physical Interpretation                                   |
|---------------------------|---------------|-------|----------------|-----------------------------------------------------------|
| Hot desert (tasmax ~38°C) | 38°C          | +2°C  | 2/38 = **5.3%** | Marginal increase in already-extreme heat                |
| Cold mountain (tasmax ~5°C) | 5°C         | +2°C  | 2/5 = **40%**   | Fundamentally changes freeze-thaw regime                 |

The cold site's SCVR is 7.5× larger — this is **physically correct**. A +2°C shift at a site with baseline 5°C changes whether water freezes at night; at a desert site, it is a marginal change in equipment operating temperature. SCVR's normalization encodes this physically meaningful asymmetry into a single dimensionless number.

This normalization property is what makes SCVR suitable for portfolio-level risk comparison: a SCVR of 8% for a mountain solar site and 8% for a desert solar site represent genuinely comparable levels of climate exposure, even though the underlying absolute temperature changes may be different.

#### 5-Step Computation Walkthrough

The empirical SCVR computation follows five steps:

**Step 1 — Pool:** Concatenate daily values from all models and all years within the chosen window.
- Baseline pool: always the full 30-year historical pool: **~65,700 values** (6 models × 30 years × 365 days)
- Future pool size depends on the windowing strategy (see B4): full-window pools ~65,700 values; 10-year anchor windows pool ~21,900 values

**Step 2 — Sort:** Sort both pooled arrays in **descending order** to form empirical exceedance distributions. The largest value maps to the lowest exceedance probability (rarest event); the smallest value maps to exceedance probability ≈ 1.0 (essentially certain to be exceeded).

**Step 3 — Assign probabilities:** Map each sorted value to an exceedance probability using **Weibull plotting positions**:

```
p_i = i / (n + 1)   for i = 1, 2, ..., n (sorted descending)
```

This maps the highest value to p = 1/(n+1) ≈ 0 and the lowest value to p = n/(n+1) ≈ 1. Weibull plotting positions are preferred over linspace because they produce unbiased quantile estimates for the empirical distribution.

**Step 4 — Integrate:** Compute area under each exceedance curve using the **trapezoidal rule**:

```
Area = sum over i from 1 to (n-1) of:
       (p_{i+1} - p_i) * (v_i + v_{i+1}) / 2
```

*Where v_i is the climate variable value at exceedance probability p_i.*

**Step 5 — Ratio:** Compute the signed normalized ratio:

```
SCVR = (Area_future - Area_baseline) / Area_baseline
```

#### Convergence Callout

> **Convergence guarantee:** At n = 65,700 (full 30-year window), the trapezoid integration error is less than **0.0001%**. At n = 21,900 (10-year anchor windows used for annual SCVR), the error is still less than **0.001%** — SCVR is an area-based (mean) metric, not a tail statistic, so it is insensitive to the rougher tails at smaller pool sizes. The empirical exceedance approach remains the correct choice at all pool sizes used by LTRisk (n ≥ 10,000).

This convergence guarantee is the reason empirical (non-parametric) estimation is preferred over parametric fitting. At these sample sizes, the empirical CDF has already converged; parametric fitting would add distributional assumptions without improving accuracy.

#### Why Daily Granularity, Not Annual

SCVR is computed from ~65,700 **daily** values, not from 30 annual means. This is not arbitrary — it is required by the downstream engineering models:

- **Peck's equation** (thermal aging) is driven by the daily temperature distribution. Cumulative thermal damage depends on every individual hot day, not on the average annual temperature.
- **Coffin-Manson** (freeze-thaw cycling) counts daily thermal cycles. The number of freeze-thaw events per year depends on individual daily minima crossing the 0°C threshold.
- **The Palmgren-Miner rule** (structural fatigue) accumulates damage from every wind event in the distribution tail.

A year with 20 days above 40°C and a year with 0 days above 40°C can have the **same annual mean temperature**. SCVR on annual means would call these identical. SCVR on daily values correctly identifies the 20-hot-days year as carrying significantly more thermal degradation risk.

---

### B2. SCVR in the Distribution Shift Landscape

SCVR did not emerge in a vacuum. Multiple disciplines independently developed tools for measuring distributional shifts over the past century. Understanding where SCVR sits in this landscape validates its design choices and answers the institutional investor question: *"What methodology is this based on?"*

```
FIGURE 4: Distribution Shift Measurement Methods by Discipline

┌─────────────────────────────────────────────────────────────────────────────────┐
│                    Distribution Shift Measurement Landscape                     │
├────────────────────┬────────────────────────────────────────────────────────────┤
│ Discipline         │ Methods                                                    │
├────────────────────┼────────────────────────────────────────────────────────────┤
│ Information Theory │ [KL Divergence]  [Wasserstein W1]  [JSD]  [Total Var.]    │
│                    │                                                            │
│ Finance & Risk     │ [VaR]  [CVaR / ES]  [PSI]  [Stress Testing (Basel)]       │
│                    │                                                            │
│ Insurance / CAT    │ [AAL]  [EP Curves]  [PML]  [Return Periods]               │
│                    │                                                            │
│ Hydrology          │ [GEV Non-Stationary]  [Delta Method]  [KS Test]           │
│                    │                                                            │
│ Machine Learning   │ [KS Statistic]  [MMD]  [Covariate Shift Detection]        │
│                    │                                                            │
│ Climate Risk       │ ══▶ SCVR ◀══  Full CDF | Normalized | Signed | Empirical  │
└────────────────────┴────────────────────────────────────────────────────────────┘

  SCVR is positioned as the intersection of best practices across all disciplines.
```

#### Information Theory

**KL Divergence** D_KL(P||Q) = integral of P(x) * log(P(x)/Q(x)) dx measures how much information is lost when Q is used to approximate P. It is **asymmetric** (D_KL(P||Q) ≠ D_KL(Q||P)) and **undefined** when Q assigns zero probability to events P considers possible — a problem for empirical distributions with finite sample sizes.

**Jensen-Shannon Divergence (JSD)** symmetrizes KL by averaging both directions: JSD(P||Q) = (1/2) * D_KL(P||M) + (1/2) * D_KL(Q||M) where M = (P+Q)/2. This resolves the asymmetry but does not resolve the interpretability problem — JSD is unitless and not directly interpretable in physical units.

**Wasserstein W1** is preferred for SCVR because it **respects the metric structure of the value space** — moving a distribution by 2°C costs twice as much as moving it by 1°C. KL Divergence does not guarantee this; it measures information-theoretic dissimilarity, not physical displacement.

#### Finance and Risk Management

**Value at Risk (VaR)** asks: what is the loss at the 99th percentile? It is a **point measure** — one quantile, not the distributional shape. VaR ignores everything except one specific point on the distribution, which means two distributions can have the same VaR despite very different tails.

**CVaR / Expected Shortfall (ES)** integrates the tail above VaR: ES_alpha = E[X | X > VaR_alpha]. This is structurally similar to SCVR (it integrates part of the distribution) but is restricted to the tail and not normalized. It captures extreme losses well but misses moderate-frequency changes that accumulate over long infrastructure lifetimes.

**Stress testing (Basel III, DFAST)** applies deterministic scenario shifts — the finance equivalent of the "delta method" in hydrology. This is a valid approach for short-horizon credit risk but cannot capture distributional shape changes that are essential for engineering failure modeling.

**PSI (Population Stability Index)** is a discretized, asymmetric KL divergence widely used in credit scoring to detect population drift: PSI = sum over bins of (Act - Exp) * ln(Act/Exp). The discretization into bins introduces arbitrary binning choices that affect sensitivity.

#### Insurance and CAT Modeling

The insurance industry built its own equivalent of the Wasserstein integral through catastrophe (CAT) modeling:

- An **Exceedance Probability (EP) curve** plots P(annual loss > x) vs x — exactly the same shape as SCVR's exceedance curve, but for dollar losses rather than physical variables.
- **Average Annual Loss (AAL)** = integral of loss × f(loss) d(loss) = E[annual loss] = area under the EP curve.

SCVR is literally **(AAL_future - AAL_baseline) / AAL_baseline**, applied to physical climate variables instead of dollar losses. This structural equivalence means SCVR has the endorsement of the insurance industry's 30-year track record of CAT modeling, applied to a new domain.

> **Key convergence:** The insurance and information theory communities independently converged on the same integral because **integrating the full exceedance curve is the mathematically correct summary statistic for a shifted distribution**. SCVR adopts this convergent best practice and adds sign-preservation and normalization.

#### Machine Learning — Distribution Shift Detection

In ML, when a model trained on distribution P is deployed on distribution Q (covariate shift), performance degrades. Climate change is precisely covariate shift: the input distribution P(X) (temperature, rainfall, wind) shifts, while the engineering failure physics P(Y|X) remains constant.

- The **Kolmogorov-Smirnov (KS) statistic** measures the maximum vertical gap between two CDFs — a point measure that ignores the shape of the gap.
- **Maximum Mean Discrepancy (MMD)** maps distributions into reproducing kernel Hilbert space but loses interpretability in physical units.
- **SCVR integrates the entire CDF gap**, not just the maximum — capturing both the width and magnitude of distributional shift across the full support of the distribution.

#### Comprehensive Comparison Table

| Method            | Integrates                  | Normalized      | Sign     | Parametric |
|-------------------|-----------------------------|-----------------|----------|------------|
| KL Divergence     | Log-ratio weighted sum       | No              | No       | Optional   |
| Wasserstein W1    | Full CDF area                | No              | No (abs) | No         |
| KS Statistic      | Max point gap only           | No              | No       | No         |
| VaR               | Single quantile              | No              | Yes      | Optional   |
| CVaR / ES         | Tail area only               | No              | Yes      | Optional   |
| AAL (Insurance)   | Full loss CDF                | No              | Yes      | Yes/No     |
| PSI (Credit/ML)   | Binned KL-like               | No              | No       | No         |
| Delta Method      | Mean shift only              | No              | Yes      | No         |
| GEV Non-Stat.     | Parametric full dist.        | Optional        | Yes      | Yes        |
| **SCVR**          | **Full value CDF**           | **Yes (÷ base)**| **Yes**  | **No**     |

> **SCVR is uniquely positioned:** It is the only method in common use that combines full-distribution integration, baseline normalization, sign preservation, and non-parametric estimation. This combination makes it ideally suited for translating climate model output into financial risk metrics.

---

### B3. Empirical vs Parametric — Why SCVR's Choices Are Defensible

Three fundamental methodological choices define SCVR's implementation. Each choice has alternatives; each choice was made for specific, defensible reasons.

#### Choice 1: Empirical, Not Parametric

SCVR does not fit a GEV, Normal, Gumbel, or any other parametric distribution. It uses the raw sorted empirical data directly. At n = 65,700, the empirical CDF has converged — the trapezoid integration error is < 0.0001%.

**Why not parametric?** Fitting a parametric model to climate data adds distributional assumptions without improving accuracy at these sample sizes. More importantly, parametric fitting introduces **misspecification risk**, especially in the tails where the climate change signal is strongest. Climate variables are not normal (tasmax is left-bounded at absolute zero), not purely Gumbel, and not necessarily in the domain of attraction of any standard extreme value distribution at the daily scale. Empirical estimation makes zero distributional assumptions and lets the data speak directly.

The traditional argument for parametric fitting — that it enables extrapolation to unobserved return periods — is irrelevant here. SCVR is computing a distributional mean (the area under the exceedance curve), not extrapolating to 1-in-10,000-year events. The area metric is robust to tail uncertainty.

#### Choice 2: Normalized Ratio, Not Absolute Distance

SCVR = (Area_future - Area_baseline) / Area_baseline. The normalization by baseline area converts the absolute distributional shift into a dimensionless fractional shift.

**Why normalize?** Absolute Wasserstein distance is not comparable across variables or sites. A +2°C shift at a desert site (baseline ~38°C) has different physical consequences than at a mountain site (baseline ~5°C) — the mountain site's freeze-thaw regime changes fundamentally, while the desert site experiences marginal additional heat. Normalizing converts absolute shift to fractional shift, making SCVR dimensionless and cross-comparable across any variable, any site, any asset class.

This dimensionlessness is not merely convenient — it is a prerequisite for portfolio-level aggregation. Without normalization, aggregating SCVR values across a solar portfolio in Arizona and a wind farm in Minnesota would mix incompatible physical units.

#### Choice 3: Daily Granularity, Not Annual

Engineering failure models (Peck's, Coffin-Manson) are driven by the **daily distribution**. Cumulative damage depends on every thermal cycle, every freeze-thaw event, not on the annual mean.

**Why not annual?** A year with 20 days above 40°C and a year with 0 days above 40°C can have identical annual means. SCVR on annual means would call them identical for risk purposes. SCVR on daily values correctly identifies the 20-hot-days year as carrying dramatically more thermal degradation risk. Annual SCVR would destroy the most important information in the dataset — it would answer the wrong question.

---

### B4. Annual SCVR — Options A, B, and C

The downstream financial chain (HCR, EFR, CFADS, NAV) requires **year-by-year SCVR(t) values** — one SCVR number for each future year from 2026 to 2055. But SCVR needs large pools of daily data to produce stable exceedance curves, and the climate signal evolves at approximately +0.03°C/year — far below the ±5–10°C of daily weather noise in any single year. The core tension is **precision per year** (which requires less data aggregation) vs **statistical robustness** (which requires more).

Three approaches were evaluated to resolve this tension:

```
FIGURE 5: Three Approaches to Generating Annual SCVR(t) Time Series

┌──────────────────────────┬──────────────────────────┬──────────────────────────────┐
│   Option A: Per-Year     │  Option B: Rolling Window │    Option C: Anchor + Fit    │
│                          │                          │        (RECOMMENDED)          │
├──────────────────────────┼──────────────────────────┼──────────────────────────────┤
│ Pool: 1 yr x 6 models    │ Pool: 10yr rolling =      │ Pool: 3 x 10yr =              │
│ = ~2,190 per SCVR value  │ ~21,900 per SCVR value    │ 3 x ~21,900 per SCVR value    │
│                          │                          │                              │
│ 30 independent values    │ Smooth but 90% overlap    │ 3 independent anchors,        │
│ Noisy: weather dominates │ False precision (30 vals  │ zero overlap, linear fit      │
│ Negative years common    │ but only 3-5 independent) │ R² > 0.95 for temperature     │
│ Not recommended          │ Edge effects bias ends    │ Recommended for all variables │
└──────────────────────────┴──────────────────────────┴──────────────────────────────┘

  Data independence increases left to right ──▶
  Statistical noise decreases left to right ──▶
  Genuine signal visibility increases left to right ──▶
```

#### Option A: Per-Year Comparison

Compare each future year independently against the full historical baseline. Each year pools only ~2,190 values (6 models × 365 days) — marginal for a stable exceedance curve.

The result is 30 independent values, but they oscillate wildly. A cold La Niña year can produce SCVR < 0 even within a warming trend. A hot El Niño year can produce SCVR values 3× the underlying trend. This noise propagates and **amplifies** through the HCR-EFR chain because Peck's equation is exponential — a small SCVR perturbation produces a disproportionately large EFR perturbation. Not recommended.

#### Option B: Rolling Window

Use a 10-year rolling window centered on each future year, pooling ~21,900 values per SCVR computation. Smoother than Option A, but adjacent years share **90% of their data** — a 10-year window centered on 2035 overlaps 9 of 10 years with a window centered on 2034.

The apparent smoothness is an artifact of data overlap, not genuine signal. The 30 values contain roughly 3–5 **independent** pieces of information dressed up as 30. This creates a dangerous illusion of precision: year-by-year DSCR plots derived from Option B appear to have 30 data points of resolution, but only 3–5 are actually independent. Edge effects also bias the first and last few years, where the rolling window cannot be fully centered.

#### Option C: Non-Overlapping Anchors + Linear Fit (Recommended)

Compute SCVR at **3 non-overlapping 10-year anchor windows**, each with ~21,900 values and zero data overlap between windows. Any trend between anchors is genuine climate evolution, not a smoothing artifact.

#### Anchor Windows Table

| Anchor | Window    | Midpoint | Pool Size           | Independence                    |
|--------|-----------|----------|---------------------|---------------------------------|
| Early  | 2026–2035 | ~2030    | ~21,900 daily values| Zero overlap with other anchors  |
| Mid    | 2036–2045 | ~2040    | ~21,900 daily values| Zero overlap with other anchors  |
| Late   | 2046–2055 | ~2050    | ~21,900 daily values| Zero overlap with other anchors  |

#### Linear Fit Formula

A linear curve is fitted through the 3 anchor SCVR values:

```
f(t) = alpha + beta * (t - 2026)
```

Where:
- **alpha** = SCVR at t = 2026 (estimated from the Early anchor SCVR at midpoint 2030, back-extrapolated 4 years)
- **beta** = slope of SCVR change per year (fitted by ordinary least squares through the 3 anchor points)
- **t** = calendar year (2026 to 2055)

Annual SCVR values are then read off the fitted curve: SCVR(t) = f(t) for each year t from 2026 to 2055.

**Why is the linear assumption physically justified?**
1. CO₂ concentration increase is approximately linear over the 2026–2055 horizon
2. Radiative forcing is approximately linear in CO₂ concentration for small increments (ΔF ≈ 5.35 × ln(C/C₀))
3. Global mean temperature response tracks forcing with a roughly linear coefficient over 30-year windows
4. Site-level temperature follows global mean temperature with a site-specific amplification factor that is approximately constant over this horizon

The interpolation assumption is **explicit and transparent**: the 3 anchor points are robustly measured; the years between them are linearly interpolated. This is preferable to implicit smoothing from rolling windows, which also assumes smoothness but hides the assumption inside the algorithm.

#### Experimental Validation Table

All three options were tested against real CMIP6 data (Hayhurst Solar, SSP5-8.5, 6 models). The results split cleanly into **three variable categories**, demonstrating that a one-size-fits-all approach across all climate variables is incorrect:

| Variable          | Noise / Signal Ratio | R² (3 Anchors) | Negative Years (of 30) | Recommended Annual SCVR Strategy              |
|-------------------|----------------------|-----------------|------------------------|------------------------------------------------|
| tasmax, tasmin, tas | 0.29–0.33 (low)    | > 0.95          | 0 of 30                | 3 anchors + linear fit (Option C)              |
| pr (precipitation) | 9.05 (very high)   | ~0.59           | 16 of 30               | Period-average or 6 anchors + non-linear fit   |
| hurs (humidity)    | 0.97 (moderate)    | ~0.67           | 25 of 30               | Period-average SCVR (constant over time)       |
| sfcWind, rsds      | 1.3–8.4 (high)     | Near 0          | 14–25 of 30            | Period-average SCVR ≈ 0 (negligible signal)    |

#### Variable-Specific Strategy Callout

> **Variable-specific strategy:** Temperature variables (tasmax, tasmin, tas) show strong monotonic trends with R² > 0.95 — use 3 non-overlapping anchor points with linear interpolation. Precipitation is non-linear with very high noise (noise/signal = 9.05) — use period-average SCVR or 6 anchors (5-year windows) with a non-linear fit. Wind speed and solar radiation show weak or absent trends — treat SCVR as constant at approximately zero using the pooled 30-year value. Humidity shows moderate noise with a drying trend — use period-average SCVR.
>
> **The annual table format is the same regardless of method:** the output is always a 30-row table with year and SCVR value. Only the computation behind each cell changes by variable.
>
> **Fallback (if 3 anchors are too coarse):** Use 6 non-overlapping 5-year anchors (~10,950 values each with 6 models, or ~62,050 with all 34 CMIP6 models). This gives 6 independent data points enabling quadratic or piecewise-linear fitting while maintaining statistical robustness. Experimental evidence shows 3 and 6 anchors produce equivalent R² for temperature, so 3 is sufficient for the primary risk driver.

---

### B5. Performance Adjustment Analysis (Channel 3)

Climate change affects renewable energy infrastructure through **three distinct channels**. Understanding which channels are material — and which are negligible — is critical for model parsimony and defensibility.

```
FIGURE 6: Three Impact Channels — Materiality Assessment

┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│       Channel 1         │   │       Channel 2         │   │       Channel 3         │
│  Equipment Degradation  │   │    Thermal Derating     │   │    Resource Shift       │
│                         │   │                         │   │                         │
│   Temperature, humidity,│   │  Solar modules lose     │   │  Does climate change    │
│   freeze-thaw shifts    │   │  ~0.3%/°C efficiency    │   │  alter solar/wind       │
│   degrade equipment     │   │  above 25°C operating   │   │  resource itself?       │
│   faster               │   │  temperature            │   │                         │
├─────────────────────────┤   ├─────────────────────────┤   ├─────────────────────────┤
│   ~$6.5M EFR           │   │   ~0.3%/degree          │   │   SCVR near 0           │
│   DOMINANT RISK        │   │   MINOR (50x smaller)   │   │   NEGLIGIBLE            │
└─────────────────────────┘   └─────────────────────────┘   └─────────────────────────┘
            │                             │                             │
            ▼                             ▼                             ▼
   Captured in EFR calc          Included in model           Excluded from model
                                  (small coefficient)         (empirically zero)

Key insight: "Risk is to the hardware, not to the fuel supply."
```

#### Channel 1: Equipment Degradation (Material)

Temperature, humidity, and freeze-thaw shifts degrade equipment faster than baseline engineering assumptions. This is the core of the EFR calculation. For the Hayhurst Solar example, EFR ≈ **$6.5M over the project life** under SSP5-8.5.

This channel dominates the financial impact because the physics is nonlinear: Peck's equation has an **exponential** temperature dependence. A 6.8% shift in the temperature distribution (measured by SCVR) translates to a 12% increase in degradation rate (HCR = 1.12) — not 6.8%, but 12% — because of the exponential acceleration factor. This nonlinearity means SCVR values, while numerically modest (3–10%), drive disproportionately large changes in failure rates and replacement costs.

#### Channel 2: Thermal Derating (Minor)

Solar photovoltaic modules lose efficiency at higher temperatures: approximately **-0.3%/°C** above 25°C operating temperature for crystalline silicon. A +2°C shift in mean temperature produces approximately 0.6% additional energy loss.

This loss is real and included in the model, but it is roughly **50× smaller** than Channel 1's equipment failure cost for a typical solar project. At a project scale of $50M revenue, 0.6% represents $300K annually — significant but secondary to the $6.5M lifetime EFR from accelerated equipment failure.

The Channel 2 coefficient (-0.3%/°C) is a well-established material property of crystalline silicon PV, published in IEC standards and validated across thousands of module datasheets.

#### Channel 3: Resource Shift (Negligible)

Does climate change materially alter the solar or wind resource itself? Empirically: **no**. Solar radiation (rsds) and surface wind speed (sfcWind) SCVR values are near zero across all sites and scenarios tested in the CMIP6 ensemble.

The underlying physics explains why:

**Solar (rsds):** Downwelling shortwave radiation at the surface is driven by atmospheric composition, cloud cover, and aerosol loading. Climate models show these change very little at the 2026–2055 timescale at most sites. While individual sites may see small cloud cover changes, the ensemble mean SCVR is near zero.

**Wind (sfcWind):** Small changes in surface wind density are partially offset by changes in icing frequency at cold sites and by changes in boundary layer stability. These effects approximately self-cancel in the CMIP6 ensemble, producing near-zero net SCVR.

**Ratio test:** Channel 1 (EFR ≈ $6.5M lifetime) vs Channel 2 (thermal derating ≈ 0.3% of revenue) vs Channel 3 (≈ 0): the ratio is approximately 6.5M : 300K/yr : 0, or about 1 : 0.3 : 0. Channel 3 contributes effectively zero to the risk signal.

> **Key finding:** "Risk is to the hardware, not to the fuel supply." Climate change degrades the equipment that converts climate resources into energy (Channel 1), marginally reduces conversion efficiency (Channel 2), but does not materially change the resources themselves over a 30-year horizon (Channel 3). This simplifies the model: LTRisk needs to track temperature, humidity, and precipitation shifts, but not rsds or sfcWind shifts for revenue projection.

---

## Section C — Financial Translation

This section describes how SCVR values (dimensionless climate metrics) are converted into dollar-denominated financial impacts. The translation chain — SCVR → HCR → EFR → CFADS → NAV — maintains physical rigor at each stage while producing outputs that integrate directly into standard project finance models.

---

### C1. HCR — Hazard Change Ratios

The **Hazard Change Ratio (HCR)** translates a dimensionless SCVR into a **hazard-specific physical impact multiplier**. Each hazard has its own physics model that maps climate variable shifts to degradation rate changes. HCR is the bridge between climate science (SCVR) and financial engineering (EFR).

```
FIGURE 7: SCVR to HCR to EFR Translation Chain

┌────────────────────┐          ┌────────────────────┐          ┌────────────────────┐
│  SCVR              │          │  HCR               │          │  EFR               │
│  (Distribution     │          │  (Hazard Change)   │          │  (Equipment        │
│   Shift)           │          │                    │          │   Failure Cost)    │
├────────────────────┤          ├────────────────────┤          ├────────────────────┤
│ tasmax SCVR ──────▶│──────────│▶ Thermal Aging ───▶│──────────│▶ Module Degradation│
│                    │          │                    │          │                    │
│ tasmin SCVR ──────▶│──────────│▶ Freeze-Thaw ─────▶│──────────│▶ Structural Fatigue│
│                    │          │                    │          │                    │
│ hurs SCVR ────────▶│──────────│▶ Humidity Corr. ──▶│──────────│▶ Connection Failure│
│                    │          │                    │          │                    │
│ pr SCVR ──────────▶│──────────│▶ Hail / Precip ───▶│──────────│▶ Output Loss       │
└────────────────────┘          └────────────────────┘          └────────────────────┘

Each arrow represents a physics model (Peck's, Coffin-Manson, Palmgren-Miner, empirical curves).
HCR = 1.0 means no climate change impact. HCR = 1.15 means 15% faster degradation.
```

#### HCR by Hazard Type

| Hazard               | Physics Model     | Key Variable(s)  | HCR Formula Description                           |
|----------------------|-------------------|-------------------|----------------------------------------------------|
| Thermal aging        | Peck's equation   | tasmax, hurs      | Acceleration factor from Arrhenius temperature term |
| Freeze-thaw cycling  | Coffin-Manson     | tasmin            | Cycle count ratio × fatigue exponent               |
| Humidity corrosion   | Peck's (RH term)  | hurs, tasmax      | RH-weighted degradation rate ratio                 |
| Structural fatigue   | Palmgren-Miner    | sfcWind           | Cumulative damage fraction shift                   |
| Hail / precip damage | Empirical curves  | pr                | Precipitation intensity exceedance ratio           |

HCR values are typically close to **1.0** for moderate scenarios (SSP2-4.5) and diverge further under high-emissions scenarios (SSP5-8.5). An HCR of 1.15 means the hazard-specific degradation rate is **15% higher than baseline assumptions** — a solar module that was expected to fail after 25 years at baseline climate will now fail after approximately 21.7 years (25/1.15 ≈ 21.7).

The nonlinear relationship between SCVR and HCR is a critical feature: because Peck's equation involves an exponential term, small climate shifts (3–8% SCVR) produce disproportionately larger changes in degradation rates (10–20% HCR increase). This nonlinearity is why climate risk in solar infrastructure is not a "rounding error" — it is a material financial exposure.

---

### C2. EFR — Equipment Failure Replacement Costs

The **Equipment Failure Replacement cost (EFR)** translates HCR physical impact ratios into dollar costs by combining them with equipment cost schedules (replacement costs, maintenance intervals, component lifetimes). EFR represents the **incremental annual cost of equipment failure attributable to climate change** — the cost above and beyond what was projected in the original (pre-climate) financial model.

#### EFR Formula

```
EFR(t) = SUM over all hazards h of: [ (HCR_h(t) - 1) * BaselineCost_h(t) ]
```

**Term-by-term interpretation:**
- **(HCR_h(t) - 1):** The fractional increase in degradation rate for hazard h in year t. Subtracting 1 isolates the climate-attributable increment — if HCR = 1.0 (no change), this term is 0 and EFR = 0.
- **BaselineCost_h(t):** The expected annual cost of hazard h in year t under baseline (pre-climate) assumptions, from the original financial model's O&M schedule.
- **Summation over hazards:** All relevant failure modes are combined linearly. This assumes failure modes are independent, which is approximately correct when they affect different components (thermal aging affects modules, freeze-thaw affects mounting structures, corrosion affects electrical connections).

EFR(t) = 0 means climate change adds no incremental cost in year t (either climate impact is zero, or it has been fully priced into the baseline). A positive EFR represents the additional annual O&M / replacement expenditure beyond what was budgeted in the base case financial model — a direct hit to free cash flow.

---

### C3. Cash Flow Integration — CFADS and DSCR

The cash flow integration module is where climate risk meets financial modeling. LTRisk operates in a **two-repository architecture**: the climate risk engine (producing EFR time series) and the financial model (producing base-case CFADS). Integration requires careful temporal and definitional alignment between the two.

#### The CFADS Waterfall

**Cash Flow Available for Debt Service (CFADS)** is the standard metric for project finance. It represents revenue minus all operating costs, taxes, and reserves — the cash available to service debt and distribute equity returns.

```
FIGURE 8: CFADS Waterfall Showing Climate Adjustment Insertion Point

Revenue          O&M           Insurance      Tax &         Climate        CFADS        Debt
(P50)           Costs                        Lease          Adj.           (net)        Service
  │               │               │             │              │              │              │
  │               │               │             │              │              │              │
  ▼               ▼               ▼             ▼              ▼              ▼              ▼
┌────────┐    ┌───────┐       ┌───────┐    ┌───────┐     ┌───────┐      ┌────────┐    ┌───────┐
│        │    │░░░░░░░│       │░░░░░░░│    │░░░░░░░│     │░░░░░░░│      │        │    │░░░░░░░│
│        │    │  deduct       │  deduct    │  deduct     │EFR(t) │      │        │    │ DS    │
│ Gross  │    │       │       │       │    │       │     │  new! │      │ Net    │    │       │
│ Revenue│    │ O&M   │       │ Insur.│    │ Tax/  │     │       │      │ CFADS  │    │       │
│        │    │ costs │       │       │    │ Lease │     │       │      │        │    │       │
└────────┘    └───────┘       └───────┘    └───────┘     └───────┘      └────────┘    └───────┘
                                                                                           │
                                                                                           ▼
                                                                                    DSCR = CFADS / DS
                                                                                         = 1.60x (base)
                                                                                         = 1.56x (climate-adj)
```

The climate adjustment (EFR) enters the waterfall as an **additional cost line**, reducing CFADS:

```
CFADS_adjusted(t) = CFADS_base(t) - EFR(t)
```

This is the simplest and most model-agnostic insertion method (Approach A in the BI Conversion table below). It requires only the EFR time series and the base-case CFADS — no deep access to the financial model internals.

#### BI Conversion: From Annual Impact to Financial Line Items

A critical implementation challenge is converting the annual EFR (a "bulk impairment" number) into specific financial line items (O&M increase, insurance escalation, capex reserves) that the financial model can absorb. Three approaches were evaluated:

| Approach         | Method                                                              | Pros                            | Cons                               |
|------------------|---------------------------------------------------------------------|---------------------------------|------------------------------------|
| A: Direct Subtraction | Subtract EFR from CFADS directly                               | Simplest, model-agnostic        | No granularity on cost type        |
| B: Ratio Allocation | Allocate EFR across O&M, insurance, capex by historical ratios  | Preserves cost structure        | Requires cost breakdown data       |
| C: Bottom-Up Rebuild | Rebuild each cost line from HCR-adjusted failure curves         | Most accurate                   | Complex, needs full model access   |

> **Recommended:** Start with **Approach A** (direct subtraction) for initial implementation. It requires only the EFR time series and base CFADS. Move to **Approach B** when cost breakdown data is available from the financial model. Approach C is the long-term target but requires deep integration with the financial model.

#### DSCR — The Debt Service Coverage Ratio

DSCR (Debt Service Coverage Ratio) is the primary covenant metric in project finance. A DSCR below 1.0× means the project cannot service its debt from operating cash flows. Lenders typically require minimum DSCR of 1.20–1.40× with lock-up triggers at higher levels (typically 1.10–1.20×).

```
DSCR_adjusted(t) = CFADS_adjusted(t) / DebtService(t)
```

Climate risk manifests as **DSCR erosion over time**. If DSCR_adjusted(t) falls below covenant thresholds in specific years, it triggers:
- **Cash sweep events:** Free cash flow is trapped and used to prepay debt, reducing equity distributions
- **Distribution lock-ups:** Equity distributions are blocked until DSCR recovers above the threshold

Both consequences directly reduce equity returns **even if the project never technically defaults**. This is why DSCR time-series analysis (not just average DSCR) is the correct way to represent climate risk — a climate-adjusted DSCR of 1.15× in Year 20 can trigger cash trapping even if average DSCR over the project life remains above 1.40×.

---

### C4. NAV Impairment Chain

The final stage converts the climate-adjusted CFADS time series into a single **dollar-denominated NAV impairment figure** through discounted cash flow (DCF) analysis.

```
FIGURE 9: NAV Impairment Calculation Chain

┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────────┐
│  EFR(t)  │────▶│ Revenue  │────▶│ CFADS(t) │────▶│ DSCR(t)  │────▶│   DCF    │────▶│     NAV      │
│          │     │  Adj.    │     │          │     │          │     │          │     │  Impairment  │
│ Annual   │     │ (minor)  │     │ Adjusted │     │ Covenant │     │ Present  │     │              │
│ failure  │     │          │     │ cash     │     │ analysis │     │ value    │     │  % of base   │
│ costs    │     │          │     │ flows    │     │          │     │ calc.    │     │  NAV         │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────────┘
```

#### NAV Impairment Formula

```
NAV Impairment = SUM over t from 1 to T of [ EFR(t) / (1 + r)^t ] / NAV_base
```

**Term-by-term interpretation:**
- **EFR(t):** The incremental failure cost in year t (from the EFR calculation)
- **(1 + r)^t:** The discount factor, where r is the discount rate (typically the project's WACC or equity IRR hurdle rate)
- **SUM of EFR(t) / (1+r)^t:** The present value of all climate-attributable costs over the project life
- **/ NAV_base:** Normalization by base-case NAV converts to a percentage impairment

The impairment is expressed as a **percentage of base-case NAV**. A 5% impairment means that climate risk, as projected by the CMIP6 ensemble under a given scenario, reduces the project's net asset value by 5% relative to a world without climate change. This is the single number that investors, lenders, and board members need to frame climate exposure against other risks in the portfolio.

---

### C5. Worked Example — Hayhurst Solar Year 10

This worked example traces through the **complete LTRisk pipeline** for a single year (Year 10) of a solar project, showing how abstract SCVR numbers translate to concrete financial impact. The example uses the Hayhurst Solar project under SSP5-8.5 (high emissions scenario).

| Step | Metric                  | Value    | Notes                                                                      |
|------|-------------------------|----------|----------------------------------------------------------------------------|
| 1    | tasmax SCVR (SSP5-8.5)  | +6.8%    | Temperature distribution shifted 6.8% higher than historical baseline     |
| 2    | hurs SCVR (SSP5-8.5)    | -2.1%    | Relative humidity decreased slightly (drying trend)                         |
| 3    | Thermal aging HCR       | 1.12     | 12% faster thermal degradation rate via Peck's equation (exponential!)     |
| 4    | Combined HCR            | 1.15     | All hazards combined: thermal aging + humidity corrosion + freeze-thaw      |
| 5    | Year 10 EFR             | $220K    | Incremental equipment failure cost in Year 10, above baseline O&M          |
| 6    | Base CFADS Y10          | $4.2M    | From financial model (pre-climate adjustment)                               |
| 7    | Adjusted CFADS Y10      | $3.98M   | $4.2M - $0.22M = climate-adjusted free cash flow                           |
| 8    | Base DSCR Y10           | 1.65×    | Comfortable above 1.40× covenant; no covenant stress                       |
| 9    | Adjusted DSCR Y10       | 1.56×    | Still above covenant but measurably eroded; watch list territory            |
| 10   | Cumulative NAV impairment| ~5%     | Present value of all EFR(t) from Year 1–30, normalized by base NAV         |

> **Key takeaway:** A 6.8% shift in the temperature distribution translates to a **12% increase in degradation rate** (nonlinear — Peck's equation is exponential in temperature), which produces $220K/year in additional failure costs. Over the project life, this compounds to approximately **5% NAV impairment** under SSP5-8.5.
>
> The nonlinearity is the critical insight: a 6.8% SCVR does not produce a 6.8% HCR or a 6.8% EFR increase. Peck's equation amplifies the distributional shift by roughly 1.8× due to its exponential temperature dependence. This amplification is why climate risk is material even when raw SCVR values appear modest.

Note that Year 10 DSCR of 1.56× is still above the typical 1.40× covenant minimum, but the erosion from 1.65× to 1.56× is measurable. By Year 20 or Year 25, continued SCVR increases (following the linear trend from the 3-anchor fit) will produce larger EFR values and potentially trigger covenant stress — which is exactly the scenario that motivates proactive climate risk disclosure.

---

## Section D — Technical Reference

This section provides reference tables and specifications for practitioners implementing the LTRisk framework. It is organized for look-up rather than sequential reading.

---

### D1. Variable-Specific SCVR Findings

The following table summarizes SCVR results observed across LTRisk case studies, organized by variable, scenario, and signal strength. These findings inform the variable-specific strategies described in B4.

| Variable | SSP2-4.5 SCVR | SSP5-8.5 SCVR | Signal   | Annual SCVR Approach | Key Observation                                      |
|----------|---------------|---------------|----------|----------------------|------------------------------------------------------|
| tasmax   | +3–5%         | +5–10%        | Strong   | 3 anchors + linear   | Clear warming signal, monotonic trend, R² > 0.95     |
| tasmin   | +4–7%         | +7–12%        | Strong   | 3 anchors + linear   | Larger % shift due to lower baseline; fewer freeze days |
| tas      | +3–5%         | +5–9%         | Strong   | 3 anchors + linear   | Consistent with tasmax/tasmin envelope               |
| hurs     | -1 to -3%     | -2 to -5%     | Moderate | Period-average       | Drying trend; site-dependent; R² ~0.67               |
| pr       | Variable      | Variable      | Weak     | Period-average       | Highly site-dependent; some wetter, some drier       |
| sfcWind  | Near 0        | Near 0        | None     | Constant ≈ 0         | No systematic shift detected across ensemble         |
| rsds     | Near 0        | Near 0        | None     | Constant ≈ 0         | Solar resource stable; Channel 3 empirically negligible |

**Reading the table:**
- Temperature variables (rows 1–3) dominate the risk signal. They show large, consistent, monotonically increasing SCVR values with strong R² (> 0.95) for anchor-based linear trend fit. These are the primary risk drivers for solar thermal aging via Peck's equation.
- **tasmin has larger percentage SCVR than tasmax** because its baseline value is lower. A mountain site with baseline tasmin of -5°C experiences a proportionally larger shift from +2°C warming than a desert site with baseline tasmin of +10°C. This translates directly to changes in the freeze-thaw cycle regime.
- **Humidity (hurs)** provides a secondary risk signal relevant to corrosion models and PID (potential-induced degradation) in solar modules. Its moderate signal warrants period-average treatment — a constant SCVR applied uniformly across the 30-year horizon.
- **Precipitation (pr)** is highly site-dependent: some locations get wetter, some drier. The noise/signal ratio of 9.05 means individual-year precipitation SCVR is essentially uninterpretable. The recommended approach is a period-average SCVR (or zero if the 30-year pooled estimate is not statistically different from zero).
- **Wind speed and solar radiation** contribute zero risk signal and are excluded from the annual SCVR time series as risk drivers. Their SCVR ≈ 0 finding is the quantitative basis for the Channel 3 conclusion in B5.

---

### D2. Scenario Comparison — SSP2-4.5 vs SSP5-8.5

The two scenarios bracket a range of possible futures. For the 2026–2055 projection window, the scenarios have not yet fully diverged — most of the near-term warming is already "locked in" by historical emissions.

| Dimension              | SSP2-4.5                          | SSP5-8.5                                    |
|------------------------|-----------------------------------|---------------------------------------------|
| Temperature SCVR       | +3–5%                             | +5–10% (roughly 2× SSP2-4.5)               |
| NAV Impairment (Solar) | ~2–3%                             | ~5% (non-linear scaling due to Peck's)      |
| NAV Impairment (Wind)  | ~0–1%                             | ~1% (wind less exposed to thermal effects)  |
| DSCR Erosion           | Marginal (within covenant buffer) | Noticeable in tail years (Years 20–30)      |
| Key Driver             | Moderate warming                  | Accelerated warming + humidity shifts       |

> **Practical implication:** For near-term project finance (2025–2055 horizon), the scenario choice matters less than expected. SSP5-8.5 impacts are roughly 2× SSP2-4.5 for temperature-driven risks, but even SSP5-8.5 produces only ~5% NAV impairment for solar — a material but not catastrophic exposure for a well-structured project. **The real divergence occurs post-2050**, affecting longer-lived assets (pumped hydro, grid infrastructure) or refinancing decisions that extend the investment horizon beyond 2055.

The nonlinear relationship between temperature SCVR and NAV impairment is important: SSP5-8.5 SCVR is 2× SSP2-4.5 SCVR, but NAV impairment under SSP5-8.5 (5%) is more than 2× SSP2-4.5 impairment (2–3%). This superlinear scaling is a direct consequence of Peck's exponential temperature dependence — the same amplification discussed in the C5 worked example.

---

### D3. Engineering Reliability Models

The HCR calculation relies on established engineering reliability models that translate climate variable distributions into equipment degradation rates. These models do not measure distribution shift — they **consume the SCVR shift as input** and output a dimensionless acceleration factor (which becomes HCR).

| Model           | Application                      | Input Distribution              | Output                         |
|-----------------|----------------------------------|---------------------------------|--------------------------------|
| Peck's Equation  | Solar module thermal aging       | Temperature × humidity distribution | Degradation rate (% / year) |
| Coffin-Manson    | Thermal fatigue / freeze-thaw    | Daily temperature cycling distribution | Crack propagation rate     |
| Palmgren-Miner   | Wind turbine structural fatigue  | Wind speed distribution         | Cumulative damage fraction     |
| Weibull / ALT    | Accelerated life testing         | Multi-stress distribution       | Time-to-failure distribution   |

#### Peck's Equation (Solar Thermal Aging)

Peck's model for accelerated aging combines temperature and humidity effects on semiconductor and encapsulant degradation:

```
AF = (RH / RH_ref)^n * exp[ -Ea/k * (1/T - 1/T_ref) ]
```

Where:
- **AF** = Acceleration Factor (ratio of degradation rate at test conditions to degradation rate at reference conditions)
- **RH** = relative humidity (decimal fraction)
- **RH_ref** = reference relative humidity (typically 0.50 or 0.60 for outdoor conditions)
- **n** = humidity exponent (typically **2–3** for PV module encapsulants)
- **Ea** = activation energy (typically **0.7–1.1 eV** for PV modules; higher for glass/encapsulant delamination)
- **k** = Boltzmann's constant = 8.617 × 10⁻⁵ eV/K
- **T** = temperature in Kelvin
- **T_ref** = reference temperature in Kelvin (typically 298.15 K = 25°C)

**The critical physics:** The exponential term in Peck's equation means that a small increase in temperature produces a **disproportionately large** increase in degradation rate. This is why a 6.8% SCVR (reflecting modest warming in physical units) translates to a 12% HCR (12% faster degradation) — not a 6.8% increase. The Arrhenius exponential amplifies the temperature signal. For Ea = 0.7 eV and a temperature shift from 45°C to 47°C (representative of a hot-day tail shift), AF increases by approximately 1.08–1.12× — consistent with the Hayhurst Solar example.

**Integration with SCVR:** Rather than applying Peck's equation to point temperature estimates, LTRisk integrates AF over the full daily temperature distribution:

```
Mean_AF = (1/n) * SUM over all days i of: AF(T_i, RH_i)
```

This distributional integration is exactly what SCVR captures — the shift in the area under the Peck's-weighted exceedance curve. The HCR is then: HCR = Mean_AF_future / Mean_AF_baseline.

#### Coffin-Manson (Freeze-Thaw Cycling)

The Coffin-Manson relation models fatigue life under cyclic thermal stress:

```
Nf = C * (delta_T)^(-m)
```

Where:
- **Nf** = cycles to failure (number of freeze-thaw cycles before mechanical failure)
- **delta_T** = temperature range per cycle (°C) — the difference between daily maximum and daily minimum crossing the 0°C threshold
- **C** = material constant (calibrated per component type; typically 10⁴–10⁶ for solder joints)
- **m** = fatigue exponent (typically **2–3** for solder joints and metal interconnects in PV modules)

**Climate change effects on Coffin-Manson:** As climate warms, the **number of freeze-thaw cycles** may decrease (fewer days where the daily minimum drops below 0°C). But the **temperature range per cycle** (delta_T) may increase as the daily maximum rises while the minimum is bounded near 0°C by latent heat effects. The net effect on Nf is site-dependent and cannot be estimated from annual means alone. LTRisk captures this by comparing the full daily tasmin distribution (which determines freeze-thaw cycle frequency) under future vs baseline climate.

#### Palmgren-Miner Rule (Wind Turbine Structural Fatigue)

The Palmgren-Miner cumulative damage rule is used for wind turbine structural fatigue:

```
D = SUM over all stress levels i of: n_i / N_i
```

Where:
- **D** = cumulative damage fraction (failure occurs when D = 1.0)
- **n_i** = actual number of cycles experienced at stress level i
- **N_i** = cycles to failure at stress level i (from the material's S-N curve)

**Integration with SCVR:** Wind speed determines aerodynamic loading on turbine blades and tower structures. The sfcWind SCVR ≈ 0 finding (B5, Channel 3) implies that wind speed distributions are not meaningfully shifting under climate change over the 2026–2055 horizon. Consequently, the Palmgren-Miner contribution to EFR is near zero for the sites studied. The model is retained for completeness and for sites where sfcWind SCVR may be non-negligible.

---

### D4. Implementation Roadmap

The recommended implementation sequence for the LTRisk framework, ordered by complexity and value delivery:

| Phase   | Deliverable                              | Dependencies                                               | Value Delivered                         |
|---------|------------------------------------------|------------------------------------------------------------|-----------------------------------------|
| Phase 1 | SCVR engine + basic EFR for any site     | NASA data access, climate processing pipeline              | Core risk metric per asset              |
| Phase 2 | CFADS integration (Approach A)           | EFR time series + base case financial model                | NAV impairment figure                   |
| Phase 3 | Annual SCVR(t) + DSCR time series        | Option C methodology + financial model alignment           | Year-by-year covenant analysis          |
| Phase 4 | DSCR hero chart + dashboard              | Full CFADS integration + visualization layer               | Portfolio-level risk view               |
| Phase 5 | BI conversion (Approach B/C)             | Detailed cost breakdown from financial model               | Granular cost attribution               |

**Phase 1** (SCVR + basic EFR) can be completed in 2–4 weeks with access to the NASA THREDDS endpoint and a site's latitude/longitude. It requires no financial model integration — the output is a climate risk scorecard (SCVR by variable + total EFR estimate) that can be delivered as a standalone memo.

**Phase 2** (CFADS integration) requires a base-case financial model in a readable format. The Approach A direct subtraction can be implemented in Excel or Python in a single day once EFR is available. The output is a single NAV impairment percentage — the number that goes into investment committee memos.

**Phase 3** (Annual SCVR + DSCR time series) is the Phase 2 extension. Option C anchor-based SCVR(t) provides year-by-year resolution. This phase produces the "DSCR time series" chart showing climate-adjusted vs base-case DSCR from 2026 to 2055 — the primary tool for covenant analysis.

**Phase 4** (Dashboard) wraps Phase 3 outputs into a visualization layer. The dashboard vision: a single-page view per asset showing base-case vs climate-adjusted DSCR over time, cumulative NAV impairment by scenario, and variable-by-variable SCVR decomposition.

> **Dashboard vision:** The end-state is a **single-page dashboard per asset** showing: base-case vs climate-adjusted DSCR over time, cumulative NAV impairment by scenario, and variable-by-variable SCVR decomposition. This becomes the "hero chart" for investor presentations and internal risk review — a single visual that communicates the full LTRisk output without requiring understanding of the underlying methodology.

**Phase 5** (BI conversion) provides the granular cost attribution that project operators need for O&M planning. This phase connects the climate risk signal back to specific maintenance schedules, enabling proactive rather than reactive asset management.

---

### Case Study Summary

| Asset          | Type      | Location         | SSP2-4.5 Impairment | SSP5-8.5 Impairment | Primary Driver            |
|----------------|-----------|------------------|----------------------|----------------------|---------------------------|
| Hayhurst Solar | Solar PV  | South-Central US | ~3%                  | ~5%                  | Thermal aging (tasmax)    |
| Maverick Wind  | Wind Farm | Central US       | ~0%                  | ~1%                  | Minimal exposure          |

**Solar assets** show materially higher climate exposure than wind assets. The primary driver is thermal aging via Peck's equation, which is **exponentially sensitive** to temperature shifts. A +5–10% SCVR for tasmax (typical SSP5-8.5 result for South-Central US) translates to a 12–20% increase in thermal degradation rate, producing measurable lifetime cost increases.

**Wind assets** are more resilient because:
1. Their primary failure mode (structural fatigue) is governed by wind speed distributions, which show near-zero SCVR
2. Temperature shifts are less directly coupled to turbine component failure physics
3. The thermal aging pathway (Peck's equation) is less relevant for tower steel and fiberglass blade materials than for PV module semiconductors and encapsulants

This asset-class differential has portfolio construction implications: solar-heavy portfolios carry meaningfully more climate risk than wind-heavy portfolios in the 2026–2055 window, particularly under high-emissions scenarios.

---

# E. Critical Assessment & Future Direction

This section provides an honest, internal-only assessment of the LTRisk framework: what is genuinely novel, where we are applying existing methodologies, what external work we should incorporate, and where the defensible value actually sits. This candor is essential for prioritizing engineering effort and making credible claims to technical counterparties.

---

## E1. What Is Genuinely Novel

| Element | Novelty | Why It Matters |
|---------|---------|----------------|
| End-to-end pipeline (Climate → NAV) | **High** — this integration does not exist as a productized offering | Individual pieces exist (climate analytics, reliability engineering, project finance) but nobody has stitched Climate Data → SCVR → HCR → EFR → CFADS → NAV into a modular, site-level pipeline for renewable project finance. This is the real IP. |
| Anchor-based annual SCVR (Option C) | **Moderate** — smart practical engineering | 3 non-overlapping windows + linear fit is not theoretically groundbreaking, but the variable-specific strategy table (temperature → linear fit, precipitation → period-average, wind/solar → constant ≈ 0) reflects genuine empirical work competitors would need to replicate. |
| Last-mile financial translation (DSCR covenant analysis) | **High** — this is the market gap | Most climate risk platforms stop at a risk score or physical risk rating. Going to "your DSCR drops from 1.65x to 1.56x in Year 10, and here is the covenant trigger year" is what project finance teams actually need. Nobody else delivers this cleanly. |
| Channel 1/2/3 materiality finding | **Moderate** — useful reframeable insight | "Risk is to the hardware, not the fuel supply" is a genuinely useful insight that should be front and center in any pitch. Makes investors sit up. Simplifies the model. |

> **The defensible moat is not the SCVR math — it is the last-mile integration into project finance workflows.** DSCR covenant analysis, NAV impairment as a percentage, year-by-year cash flow impact — that is the gap in the market, and that is where engineering effort should be concentrated.

---

## E2. Where We Are Applying Existing Work

Intellectual honesty requires acknowledging where LTRisk applies well-established methods rather than inventing new ones. This is not a weakness — building on proven foundations is good engineering — but we should not oversell methodological novelty in these areas.

| Component | Reality Check | Implication |
|-----------|--------------|-------------|
| SCVR metric | Signed, normalized Wasserstein W₁. At large n, SCVR ≈ (mean_future − mean_baseline) / mean_baseline. This is a fractional change in the distribution mean computed via exceedance areas — a well-understood quantity. | The Wasserstein framing adds credibility with technical reviewers, but do not oversell methodological novelty. Anyone doing climate delta analysis on means computes something equivalent. The value is in how we use it, not the metric itself. |
| HCR layer (Peck's, Coffin-Manson, etc.) | These are textbook reliability engineering models. Integrating Peck's AF over the full daily distribution is good practice, but standard in accelerated life testing literature. | Companies like DNV, Black & Veatch, and the IEC 61215/61730 standards ecosystem have been doing PV qualification testing with these models for years. We should calibrate against their published data rather than deriving from first principles. |
| CMIP6 data pipeline | Point extraction via THREDDS NCSS is well-documented NASA infrastructure. BCSD downscaling is the standard method. The 6-model ensemble cap is a practical choice, not a methodological contribution. | Solid engineering implementation of existing data access. Opportunity to expand to 34-model ensemble for robustness testing. |

> **Honest framing for technical counterparties:** "LTRisk builds on the Wasserstein distance framework and established reliability engineering models (Peck's, Coffin-Manson, Palmgren-Miner). Our contribution is the end-to-end integration into project finance workflows and the empirical calibration of variable-specific annual SCVR strategies."

---

## E3. External Work We Should Incorporate

The following external bodies of work are directly relevant to LTRisk and should be studied, calibrated against, or integrated into future iterations. Learning from these rather than rebuilding from first principles will accelerate development and increase credibility.

| Source | What They Offer | How to Integrate |
|--------|----------------|------------------|
| CAT Modeling Industry (Verisk/AIR, RMS, CoreLogic) | Decades of hazard-to-financial-loss translation chains. Parametric trigger structures, damage curves, loss development methodologies. Swiss Re sigma reports. Munich Re NatCatSERVICE. | Borrow empirically calibrated damage functions for the HCR → EFR translation instead of building from first principles. Their EP curve / AAL framework is structurally identical to SCVR. |
| TCFD / PCAF / NGFS Frameworks | PCAF prescribes physical risk assessment methodology for project finance assets. The BI conversion framework (our Approach B/C) is essentially pre-built with industry consensus. | Adopt PCAF's taxonomy for the financial translation layer. This gives LTRisk's output instant compatibility with regulatory reporting requirements (TCFD disclosures). |
| NREL PV Degradation Studies (Jordan & Kurtz, PVRD) | Published activation energies and humidity exponents calibrated to real field data across thousands of PV systems. Site-specific degradation databases. | Replace generic Ea = 0.7–1.1 eV ranges in Peck's equation with NREL's site-specific calibrated parameters. Dramatically narrows uncertainty in HCR calculations. |
| XDI / Moody's Four Twenty Seven | Site-level climate risk scoring for infrastructure. Partially published methodologies. Already adopted by institutional investors. | Understand where they stop and LTRisk goes further. Sharpen positioning: they deliver risk scores, we deliver covenant-level cash flow impact. Consider data partnership opportunities. |
| IEC 61215/61730 Standards | PV module qualification and safety testing standards. Embedded accelerated aging protocols (damp heat, thermal cycling). | Validate Peck's and Coffin-Manson parameters against IEC-certified test results. Strengthens the HCR calibration. |

---

## E4. Strategic Priorities & Open Questions

### Priority Matrix

| Priority | Action | Effort | Impact | Status |
|----------|--------|--------|--------|--------|
| P0 (Now) | Deepen Section C — financial translation is the defensible moat. Real calibration data from operating assets (degradation curves, actual O&M cost breakdowns, insurance claim histories). | High | Critical | Gap |
| P0 (Now) | NREL calibration — replace generic Peck's parameters with published NREL site-specific degradation data. | Medium | High | Gap |
| P1 (Next) | PCAF/TCFD alignment — map LTRisk outputs to PCAF physical risk taxonomy for regulatory reporting compatibility. | Medium | High | Planned |
| P1 (Next) | CAT model benchmarking — compare HCR → EFR damage functions against Verisk/AIR published damage curves. | Medium | Medium | Planned |
| P2 (Later) | Expand to wind-specific failure modes — gearbox, blade erosion, foundation fatigue using site-specific SCADA data. | High | Medium | Future |
| P2 (Later) | Multi-asset portfolio aggregation — correlated risk across sites, diversification benefit quantification. | High | Medium | Future |

### Open Questions

**Calibration gap:** How do we validate HCR predictions against actual observed degradation? We need partnerships with asset operators who will share real O&M data (degradation curves, component replacement histories, insurance claims) to backtest the model.

**Ensemble selection:** The 6-model cap is pragmatic but potentially biases toward models that happen to sort alphabetically first. Should we switch to a skill-weighted ensemble, or at minimum validate that the 6-model subset produces SCVR within the 34-model envelope?

**Tail risk treatment:** SCVR is an area-based (mean) metric — it does not specifically capture tail risk (e.g., the 1-in-20-year extreme heat event that triggers a catastrophic failure). Should we add a complementary tail metric (e.g., CVaR-based) for acute hazard events?

**Non-stationarity beyond 2055:** The linear interpolation assumption in Option C is well-justified for the 30-year window. But for assets with 35+ year lives, the SSP scenarios diverge materially post-2050. How do we handle extension windows?

**Correlation structure:** Variables are currently treated independently. Temperature and humidity are physically correlated (compound heat-humidity events). Should Peck's equation be evaluated on joint distributions rather than marginals?

**Regulatory adoption:** TCFD reporting requirements are tightening. How quickly can we align LTRisk outputs with PCAF taxonomy to make the framework directly usable for climate disclosure filings?

> **Bottom line:** Spend less time refining the SCVR methodology (it is good enough) and more time on the Section C financial translation — that is where the defensible moat sits. The SCVR-to-HCR-to-EFR chain needs real calibration data from operating assets more than it needs methodological polish. The pipeline integration and last-mile DSCR covenant analysis are the genuine competitive advantages.

---

## Living Document Note

> **Living Document.** This whitepaper reflects the current state of the LTRisk framework as of March 2026. The SCVR methodology (Sections B1–B5) is grounded in working notebook-level detail — including anchor-window strategies, variable-specific nuances, and experimental validation — because that is where the deepest implementation work has been done to date.
>
> As the framework progresses through subsequent stages (HCR calibration with asset-specific activation energies, EFR model expansion to wind and storage, CFADS integration with live financial models, and full NAV impairment chain), each section will be expanded with the same level of rigor and practical detail.
>
> **Expect future iterations to deepen Sections C and D** as those workstreams mature. The SCVR framework is complete and production-ready; the financial translation chain (C1–C4) is implemented at the Approach A level and actively being expanded to Approach B and C.

---

## InfraSure

---

*LTRisk Framework — Internal Technical Review*

*Methodology grounded in Wasserstein distance theory, CMIP6 climate projections, and established engineering reliability models.*

**InfraSure — Confidential**

*Version: March 2026 | Classification: Internal Technical Working Document*
