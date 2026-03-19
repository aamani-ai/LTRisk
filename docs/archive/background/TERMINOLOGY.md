# Long-Term Climate Risk Modeling - Terminology & Glossary

*Reference guide for concepts, acronyms, and data sources used in the NAV impairment framework*

**Created:** February 1, 2026  
**Purpose:** Quick reference for team members and stakeholders

---

## Table of Contents

1. [Financial & Business Terms](#financial--business-terms)
2. [Climate Risk Framework Terms](#climate-risk-framework-terms)
3. [Climate Data Sources](#climate-data-sources)
4. [Climate Scenarios](#climate-scenarios)
5. [Scientific Models](#scientific-models)
6. [Climate Metrics & Indices](#climate-metrics--indices)
7. [Equipment & Asset Terms](#equipment--asset-terms)

---

## Financial & Business Terms

### NAV (Net Asset Value)
**Definition:** The total value of an asset calculated as the present value of all future cash flows.

**In our context:** We calculate NAV impairment % to show how much climate change reduces an asset's value.

```
NAV = NPV of all future revenues over asset lifetime
NAV_Impairment_% = (1 - NPV_climate / NPV_base) × 100%
```

**Example:**
```
Hayhurst Solar (24.8 MW) - Base Scenario:
  • EUL: 25 years
  • Annual Revenue: ~$2.5M/year (declining with degradation)
  • WACC: 10%
  • NAV_base = NPV of 25 years of revenues ≈ $22.8M

Hayhurst Solar - Climate Scenario (RCP 4.5):
  • IUL: 21 years (shortened by climate stress)
  • Annual Revenue: ~$2.2M/year (lower due to heat effects)
  • Additional BI losses: $50-90K/year
  • NAV_climate ≈ $16.5M

NAV Impairment:
  = (1 - $16.5M / $22.8M) × 100%
  = 27.6%

Interpretation: "Climate change reduces this asset's value by ~28%"
```

---

### NPV (Net Present Value)
**Definition:** The sum of future cash flows discounted back to today's value.

**Formula:**
```
NPV = Σ [Cash_Flow_t / (1 + r)^t]

Where:
  t = year (1, 2, 3, ... N)
  r = discount rate (WACC)
```

**Example:**
- $1M revenue in Year 5 with 10% discount rate
- NPV = $1M / (1.10)^5 = $620,921

---

### NAV vs NPV - Important Distinction

These terms are related but serve different purposes:

| Term | NAV (Net Asset Value) | NPV (Net Present Value) |
|------|----------------------|------------------------|
| **What it is** | The VALUE of an existing asset | A calculation method (can include investment cost) |
| **Formula** | NAV = NPV of future revenues | NPV = -Investment + Σ[Cash flows / (1+r)^t] |
| **Sign** | Always positive (for working asset) | Can be negative (bad investment) |
| **Use case** | "What is this asset worth?" | "Should I invest in this project?" |

**In Our Framework:**
```
NAV = NPV of future revenues (we DON'T subtract initial investment)

Why? Because the asset ALREADY EXISTS. We're valuing it, not deciding 
whether to build it.

┌─────────────────────────────────────────────────────────────────┐
│  NPV (Investment Decision)         NAV (Asset Valuation)        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  NPV = -$30M + $22.8M              NAV = $22.8M                │
│      = -$7.2M                                                   │
│                                                                 │
│  "Don't build this project"        "This asset is worth $22.8M"│
│  (negative NPV = bad investment)   (what a buyer would pay)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Simple Analogy:**
```
You bought a house 5 years ago for $500K.
Today's rental income NPV = $400K.

NPV (investment view): -$500K + $400K = -$100K (bad investment!)
NAV (current value):   $400K (what the house is worth TODAY)

For climate risk, we care about NAV - how much is the asset worth now,
and how does climate change affect that value?
```

**When This Distinction Matters:**
- **Current Pilot:** Focuses on NAV (valuing existing assets)
- **Future Use - New Projects:** Will need full NPV (investment decisions under climate scenarios)
- **Lender Discussions:** They think in NPV terms (loan recovery analysis)
- **Equity Investors:** Care about both NAV (current holdings) and NPV (new investments)

---

### WACC (Weighted Average Cost of Capital)
**Definition:** The blended rate of return required by all capital providers (debt + equity).

**Team's Assumption:** 10%

**Industry Context:**
| Asset Type | Typical WACC Range |
|------------|-------------------|
| Utility-scale solar (contracted) | 6-8% |
| Utility-scale wind (contracted) | 6-8% |
| Merchant renewables | 8-12% |
| Team's pilot assumption | 10% |

**Why it matters:** Higher WACC → Lower NPV → Climate impacts appear smaller (percentage-wise)

**Example - Impact of WACC on NAV Impairment:**
```
Same asset, same climate scenario, different WACC:

WACC = 6%:
  • NPV_base = $28M
  • NPV_climate = $20M
  • NAV Impairment = 29%

WACC = 10%:
  • NPV_base = $23M
  • NPV_climate = $17M
  • NAV Impairment = 26%

Lower WACC → Climate risk appears MORE significant!
(Future cash flows matter more when discount rate is lower)
```

---

### WACC vs IRR vs Discount Rate - Key Distinctions

These three terms are related but serve different purposes. Understanding their differences is crucial for proper financial analysis.

#### Quick Comparison Table

| Concept | What It Is | Who Determines It | Direction of Calculation |
|---------|-----------|-------------------|-------------------------|
| **Discount Rate** | Generic term for any rate converting future $ to present $ | Context-dependent | Future → Present |
| **WACC** | *Specific* discount rate based on cost of capital | Market + Capital structure | Future → Present |
| **IRR** | Rate that makes NPV = 0 | Calculated from cash flows | Solve for rate |

#### Detailed Explanations

**Discount Rate (Generic Concept)**
```
Any rate used to calculate present value from future values.

Formula: PV = FV / (1 + r)^t

Examples of discount rates:
  • Risk-free rate (Treasury yields)
  • Required return by an investor
  • WACC (when valuing a company/project)
  • Social discount rate (for public policy)

"Discount rate" is the umbrella term; WACC and IRR are specific applications.
```

**WACC (Weighted Average Cost of Capital)**
```
The blended cost of ALL capital providers (debt + equity).

Formula:
  WACC = (E/V) × Re + (D/V) × Rd × (1 - T)

Where:
  E = Market value of equity
  D = Market value of debt
  V = E + D (total capital)
  Re = Cost of equity (what shareholders require)
  Rd = Cost of debt (interest rate on loans)
  T = Tax rate (interest is tax-deductible)

WACC represents the MINIMUM return a project must generate to satisfy
all capital providers. It's an INPUT to NPV calculations.
```

**IRR (Internal Rate of Return)**
```
The discount rate that makes NPV exactly equal to zero.

Definition: Find r such that:
  0 = -Initial_Investment + Σ [Cash_Flow_t / (1 + r)^t]

IRR is an OUTPUT - you calculate it FROM the cash flows.
It tells you: "What return does this project actually generate?"
```

#### The Key Relationship

```
┌─────────────────────────────────────────────────────────────────────┐
│                     THE INVESTMENT DECISION RULE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   IRR > WACC  →  Accept project (returns exceed cost of capital)   │
│   IRR < WACC  →  Reject project (returns below cost of capital)    │
│   IRR = WACC  →  Break-even (NPV = 0)                              │
│                                                                     │
│   WACC is the "hurdle rate" that IRR must clear.                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Example - Hayhurst Solar Investment Analysis

```
PROJECT: Hayhurst Texas Solar (24.8 MW)
Initial Investment: $30M
Expected Cash Flows: ~$2.5M/year for 25 years (declining with degradation)

Step 1: Calculate WACC (the hurdle rate)
─────────────────────────────────────────
  Capital Structure:
    • Debt: $21M (70%) at 5% interest rate
    • Equity: $9M (30%) requiring 15% return
    • Tax rate: 25%

  WACC = (30% × 15%) + (70% × 5% × (1 - 25%))
       = 4.5% + 2.625%
       = 7.125%
  
  (Team uses 10% as conservative assumption in pilot)

Step 2: Calculate NPV using WACC as discount rate
─────────────────────────────────────────────────
  NPV = -$30M + Σ [$2.5M × (1-0.005)^t / (1.10)^t]
      = -$30M + $22.8M
      = -$7.2M  (NEGATIVE - bad investment at 10% WACC!)

  But with actual WACC of 7.125%:
  NPV = -$30M + $27.5M = -$2.5M (still negative, but closer)

Step 3: Calculate IRR (what return does project actually generate?)
───────────────────────────────────────────────────────────────────
  Find r where: -$30M + Σ [$2.5M × (1-0.005)^t / (1 + r)^t] = 0
  
  Solving: IRR ≈ 5.8%

Step 4: Investment Decision
───────────────────────────
  IRR (5.8%) < WACC (7.125%)  →  Project doesn't meet hurdle rate
  
  This means investors would be better off putting their money elsewhere.
  (Or the project needs better terms: lower construction cost, higher PPA price)
```

#### How They Connect in Our Climate Risk Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│              CLIMATE RISK AFFECTS BOTH NPV AND IRR                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  BASE SCENARIO:                                                     │
│    • Cash flows: $2.5M/year for 25 years                           │
│    • NPV (at 10% WACC): $22.8M                                     │
│    • IRR: 5.8%                                                      │
│                                                                     │
│  CLIMATE SCENARIO (RCP 4.5):                                        │
│    • Cash flows: $2.2M/year for 21 years (reduced by climate)      │
│    • NPV (at 10% WACC): $16.5M                                     │
│    • IRR: 3.2%                                                      │
│                                                                     │
│  IMPACT:                                                            │
│    • NAV Impairment: 28% (NPV drops from $22.8M to $16.5M)         │
│    • IRR drops: 2.6 percentage points (from 5.8% to 3.2%)          │
│                                                                     │
│  FOR EQUITY INVESTORS:                                              │
│    Climate change reduces IRR from barely acceptable to poor.       │
│    A project that was marginal becomes clearly uneconomic.          │
│                                                                     │
│  FOR LENDERS:                                                       │
│    NAV impairment means collateral value drops.                    │
│    LTV goes from 92% to 127% (underwater).                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Common Confusions Clarified

| Misconception | Reality |
|--------------|---------|
| "IRR and discount rate are the same" | No - discount rate is an INPUT, IRR is an OUTPUT |
| "WACC is always the right discount rate" | Only for corporate valuation; project-specific rates may differ |
| "Higher IRR is always better" | Not if it comes with higher risk; risk-adjusted returns matter |
| "WACC doesn't change" | It changes with market conditions, capital structure, and perceived risk |

#### Why the Team Uses 10% WACC

```
The pilot assumes 10% WACC because:

1. Conservative Approach
   Industry WACC for contracted renewables: 6-8%
   Using 10% is deliberately conservative (understates NPV)

2. Simplicity
   Avoids site-specific WACC calculations for pilot phase

3. Sensitivity Buffer
   If results are meaningful at 10%, they're even more
   significant at realistic 6-8% rates

4. Merchant Risk Proxy
   10% is closer to merchant (uncontracted) project risk,
   providing a stress test view

Phase 1 Enhancement: Site-specific WACC based on actual capital structure
```

---

### BI (Business Interruption)
**Definition:** Revenue lost when an asset is forced offline due to hazards (floods, hail, extreme weather, etc.).

**In our framework:**
```
BI_loss_climate(t) = BI_base × (1 + HCR(t))

Where:
  BI_base = Current BI losses (no climate change)
  HCR = Hazard Change Ratio (how much hazard risk increases)
```

**Example:**
```
Maverick Creek Wind (491.6 MW):

Current BI Losses (Base Scenario):
  • Flood-related downtime: $150K/year
  • Hail damage repairs: $80K/year
  • Extreme wind curtailment: $120K/year
  • Total BI_base: $350K/year

Climate Scenario (2040, RCP 4.5):
  • HCR_flood = +25% (more extreme precipitation)
  • HCR_hail = +10% (more convective storms)
  • HCR_wind = +15% (more extreme wind events)

BI Losses (Climate-Adjusted):
  • Flood: $150K × 1.25 = $187.5K
  • Hail: $80K × 1.10 = $88K
  • Wind: $120K × 1.15 = $138K
  • Total BI_climate: $413.5K/year (+18% increase)

Over 25 years, this adds up to significant NPV reduction.
```

---

### LTV (Loan-To-Value)
**Definition:** Ratio of loan amount to asset value. Used by lenders to assess risk.

**In our context:** If NAV drops due to climate risk, LTV increases → Higher risk for lenders.

**Formula:**
```
LTV = Loan_Amount / Asset_Value × 100%
```

**Example:**
```
Hayhurst Solar Project Financing:
  • Project Cost: $30M
  • Loan Amount: $21M (70% debt financing)
  • Equity: $9M (30%)

Base Scenario (No Climate Change):
  • NAV (Asset Value): $22.8M
  • LTV = $21M / $22.8M = 92%
  → Acceptable for most lenders

Climate Scenario (RCP 4.5):
  • NAV (Climate-Impaired): $16.5M
  • LTV = $21M / $16.5M = 127%
  → UNDERWATER! Loan exceeds asset value.
  → Lender faces significant credit risk.

This is why lenders care about climate risk:
A 28% NAV impairment turns a healthy 92% LTV into a distressed 127% LTV.
```

---

## Climate Risk Framework Terms

### EUL (Expected Useful Life)
**Definition:** The baseline expected operating lifetime of an asset under normal conditions.

**Team's Assumptions:**
| Asset Type | EUL |
|------------|-----|
| Solar PV | 25 years |
| Wind Turbines | 35 years |

**Industry Context:**
- Solar: 25-30 years is standard (aligns with panel warranties)
- Wind: 20-25 years is more common in NREL/IEA studies; 35 years may be optimistic

---

### IUL (Impaired Useful Life)
**Definition:** The reduced asset lifetime due to accelerated degradation from climate stress.

**Formula:**
```
IUL = EUL × [1 - Σ(EFR_i × SCVR_i)]

Where:
  EFR = Equipment Failure Ratio
  SCVR = Severe Climate Variability Rating
```

**Example:**
- EUL = 25 years
- Total life reduction from climate stress = 15%
- IUL = 25 × (1 - 0.15) = 21.25 years

---

### SCVR (Severe Climate Variability Rating)
**Definition:** Quantifies how much MORE extreme weather occurs under climate change compared to the historical baseline.

**Calculation:** Measures the increase in area under exceedance curves (probability of extreme events).

```
SCVR(year) = [Area_under_exceedance(future) - Area_under_exceedance(baseline)] 
             / Area_under_exceedance(baseline)
```

**Visual Intuition - Exceedance Curve Shift:**
```
Probability of Exceeding Temperature Threshold
     │
 20% │                      
     │                          ╭───── Future Climate (2040)
 15% │                       ╭──╯
     │                    ╭──╯
 12% │- - - - - - - - - -●───╯        ← Future: 12% chance of >40°C
 10% │                 ╱ │
     │               ╱   │
  5% │──────────────●    │            ← Baseline: 5% chance of >40°C
     │             ╱│    │
     │           ╱  │    │
  0% └─────────┴────┴────┴──────────
              35   40   45    Temperature (°C)
                    │
                    └── Threshold we care about

  SCVR measures how much the curve shifts UP at extreme thresholds.
  Shaded area between curves = increased extreme event probability.
```

**Simple Numerical Example:**
```
Historical baseline: 5% chance of temperature > 40°C
Future (RCP 4.5, 2040): 12% chance of temperature > 40°C

SCVR_temp = (12% - 5%) / 5% = 140% increase in extreme heat probability

Interpretation: "Extreme heat events are 2.4× more likely in 2040"
```

**Detailed Example - Multiple Variables for Texas Site:**
```
SCVR Evolution Over Time (RCP 4.5 Scenario)
┌─────────────────┬────────┬────────┬────────┬────────┐
│ Variable        │  2030  │  2040  │  2050  │  2060  │
├─────────────────┼────────┼────────┼────────┼────────┤
│ Temperature     │  +25%  │  +55%  │  +90%  │ +130%  │
│ Precipitation   │  +10%  │  +18%  │  +25%  │  +35%  │
│ Wind Extremes   │   +8%  │  +15%  │  +22%  │  +30%  │
│ Heat Waves      │  +40%  │  +85%  │ +140%  │ +200%  │
│ Freeze Events   │  -15%  │  -25%  │  -35%  │  -45%  │
└─────────────────┴────────┴────────┴────────┴────────┘

Note: Freeze events DECREASE (fewer cold days), but this doesn't
necessarily help solar - panels still age, just from different stressors.
```

**Computed for:**
- Temperature extremes (heat stress on equipment)
- Precipitation extremes (flood risk)
- Wind extremes (turbine stress, cut-out events)
- Heat waves (sustained high temperature periods)
- Cold waves (freeze damage, icing)
- Freeze/frost events (thermal cycling fatigue)

**Why SCVR Matters - The Bridge Between Climate and Finance:**
```
┌─────────────────────────────────────────────────────────────────────┐
│                    SCVR IS THE CENTRAL HUB                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   CMIP Climate Data                                                 │
│         │                                                           │
│         ▼                                                           │
│   ┌──────────┐                                                      │
│   │   SCVR   │ ◄── "How much worse is extreme weather?"            │
│   └────┬─────┘                                                      │
│        │                                                            │
│        ├────────────────┬───────────────────┐                       │
│        ▼                ▼                   ▼                       │
│   ┌─────────┐     ┌──────────┐      ┌─────────────┐                │
│   │   HCR   │     │   EFR    │      │ Performance │                │
│   │ (Hazard │     │(Equip.   │      │   Model     │                │
│   │ Change) │     │ Failure) │      │  (Gen/Rev)  │                │
│   └────┬────┘     └────┬─────┘      └──────┬──────┘                │
│        │               │                   │                        │
│        ▼               ▼                   ▼                        │
│   ┌─────────┐     ┌─────────┐       ┌──────────┐                   │
│   │   BI    │     │   IUL   │       │ Revenue  │                   │
│   │ Losses  │     │ (Short- │       │ Streams  │                   │
│   │         │     │ er Life)│       │          │                   │
│   └────┬────┘     └────┬────┘       └────┬─────┘                   │
│        │               │                 │                          │
│        └───────────────┴─────────────────┘                          │
│                        │                                            │
│                        ▼                                            │
│                 ┌─────────────┐                                     │
│                 │ NAV Impact  │                                     │
│                 │ (NPV, LTV)  │                                     │
│                 └─────────────┘                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Insight:** SCVR translates abstract climate model outputs into actionable risk metrics that feed directly into financial calculations.

---

### HCR (Hazard Change Ratio)
**Definition:** The percentage increase in hazard risk (flood, hail, wind damage) as a function of SCVR.

**Formula:**
```
HCR_hazard(t) = f(SCVR_relevant_variables)

Examples:
  HCR_flood(t) = α × SCVR_precipitation(t)
  HCR_hail(t) = β × SCVR_temperature(t) + γ × SCVR_wind(t)
```

**Purpose:** Connects climate projections → BI losses

**Example:**
```
Pluvial Flood HCR Calculation:

Literature finding: ~7% increase in extreme precip per 1°C warming
Flood damage amplification: 1.5× (drainage overwhelm, non-linear effects)

For Texas site under RCP 4.5:
  • 2030: SCVR_precip = 10% → HCR_flood = 1.5 × 10% = 15%
  • 2040: SCVR_precip = 18% → HCR_flood = 1.5 × 18% = 27%
  • 2050: SCVR_precip = 25% → HCR_flood = 1.5 × 25% = 37.5%

If baseline flood BI = $200K/year:
  • 2030 flood BI = $200K × (1 + 0.15) = $230K
  • 2040 flood BI = $200K × (1 + 0.27) = $254K
  • 2050 flood BI = $200K × (1 + 0.375) = $275K

Note: HCR coefficients (like the 1.5× amplification) are derived 
from published research in Step 3 of the work plan.
```

**Status:** Team will derive specific coefficient values from published research (Step 3 of work plan)

---

### EFR (Equipment Failure Ratio)
**Definition:** The percentage decrease in asset life per percentage increase in SCVR.

**Formula:**
```
Life_reduction = Σ(EFR_i × SCVR_i)

Example:
  EFR_temp = 0.5% (0.5% life reduction per 1% SCVR increase)
  SCVR_temp = 20%
  Life_reduction_from_temp = 0.5% × 20% = 10%
```

**Purpose:** Connects climate stress → shortened asset life → reduced NPV

**Status:** Team will derive specific values from published research (Step 4 of work plan)

---

## Climate Data Sources

### CMIP (Coupled Model Intercomparison Project)
**Definition:** International effort to coordinate climate model experiments. Produces standardized climate projections used globally.

**Versions:**

| Version | Era | Key Characteristics |
|---------|-----|---------------------|
| **CMIP5** | 2013 | Used RCP scenarios; older generation |
| **CMIP6** | 2021 | Uses SSP scenarios; improved physics, higher resolution |

**Team's Original Proposal:** CMIP5 (via CORDEX)  
**Recommended:** Consider CMIP6 (via NEX-GDDP-CMIP6) for better accuracy

---

### CORDEX (Coordinated Regional Climate Downscaling Experiment)
**Definition:** Regional climate model outputs that downscale global CMIP data to higher resolution.

**Resolution:** ~25-50 km (better than raw CMIP ~100 km)

**Associated with:** CMIP5

**Access:** Various regional portals (e.g., World Bank Climate Knowledge Portal)

---

### NEX-GDDP-CMIP6 (NASA Earth Exchange Global Daily Downscaled Projections)
**Definition:** NASA product that takes raw CMIP6 outputs and:
1. Applies bias correction against historical observations
2. Downscales to 0.25° (~25 km) daily resolution

**Key Variables Available:**
| Variable | Description | Use Case |
|----------|-------------|----------|
| `rsds` | Surface Downwelling Shortwave Radiation | Solar irradiance (GHI) |
| `tas` | Near-surface air temperature | Heat stress, efficiency |
| `tasmax` | Daily maximum temperature | Heat waves |
| `tasmin` | Daily minimum temperature | Freeze events |
| `pr` | Precipitation | Flood risk |
| `hurs` | Near-surface relative humidity | Degradation models |
| `sfcWind` | Near-surface wind speed | Wind generation |

**Why it's better:**
- Bias-corrected (removes systematic model errors)
- Downscaled (usable for site-specific analysis)
- Consistent grid across all variables
- Well-documented and widely used

**Access:** https://www.nccs.nasa.gov/services/data-collections/land-based-products/nex-gddp-cmip6

---

### rsds (Surface Downwelling Shortwave Radiation)
**Definition:** Total solar radiation reaching the Earth's surface. Equivalent to GHI (Global Horizontal Irradiance).

**Units:** W/m²

**Importance:** 
- Direct input for solar PV performance models (pvlib)
- Available in CMIP6 and NEX-GDDP-CMIP6
- Eliminates need to "generate" solar irradiance from other variables

---

### GHI, DNI, DHI (Solar Irradiance Components)
**GHI (Global Horizontal Irradiance):** Total solar radiation on horizontal surface
- rsds from CMIP is essentially GHI

**DNI (Direct Normal Irradiance):** Direct beam from sun
- Not directly in CMIP; can be derived from GHI using decomposition models

**DHI (Diffuse Horizontal Irradiance):** Scattered radiation from sky
- Not directly in CMIP; can be derived from GHI

**Relationship:** GHI = DNI × cos(zenith_angle) + DHI

---

## Climate Scenarios

### RCP (Representative Concentration Pathways)
**Definition:** Greenhouse gas concentration trajectories used in CMIP5.

| Scenario | Description | 2100 Warming |
|----------|-------------|--------------|
| RCP 2.6 | Strong mitigation | ~1.5°C |
| RCP 4.5 | Moderate mitigation | ~2.4°C |
| RCP 6.0 | Less mitigation | ~2.8°C |
| RCP 8.5 | No mitigation (business as usual) | ~4.3°C |

**Team's Pilot:** RCP 4.5 (moderate pathway)

**Example - Why RCP 4.5:**
```
RCP 4.5 represents a "middle of the road" scenario:
  • Global emissions peak around 2040, then decline
  • CO2 concentration stabilizes at ~538 ppm by 2100
  • Consistent with moderate climate policy action

For infrastructure analysis, RCP 4.5 is often preferred because:
  • Not overly optimistic (RCP 2.6 requires aggressive action)
  • Not worst-case (RCP 8.5 may be unrealistic)
  • Aligns with current policy trajectory
  • Provides reasonable stress test for assets

NAV Impairment comparison (same asset):
  • RCP 2.6: ~15% impairment (limited warming)
  • RCP 4.5: ~28% impairment (moderate warming)
  • RCP 8.5: ~45% impairment (severe warming)
```

---

### SSP (Shared Socioeconomic Pathways)
**Definition:** Narratives about future societal development used in CMIP6 (combined with RCPs).

| Scenario | Description |
|----------|-------------|
| SSP1-1.9 | Sustainability, very low emissions |
| SSP1-2.6 | Sustainability, low emissions |
| SSP2-4.5 | Middle of the road |
| SSP3-7.0 | Regional rivalry, high emissions |
| SSP5-8.5 | Fossil-fueled development, very high emissions |

**Mapping to RCP:** SSP2-4.5 ≈ RCP 4.5 (similar radiative forcing)

---

## Scientific Models

### Temperature Coefficient Model (Solar PV)
**Purpose:** Calculates instantaneous power loss from high cell temperatures.

**Formula:**
```
P_actual = P_rated × [1 + γ × (T_cell − T_ref)]

Where:
  P_actual = Actual power output (W)
  P_rated = Rated power at STC (W)
  γ = Temperature coefficient (-0.003 to -0.005 per °C)
  T_cell = Cell temperature (°C)
  T_ref = Reference temperature (25°C)
```

**Example:**
- Panel rated at 400W at 25°C
- Cell temperature: 50°C
- γ = -0.004/°C
- P_actual = 400 × [1 + (-0.004) × (50 - 25)] = 400 × 0.90 = 360W (10% loss)

---

### Peck's Model (Long-Term Degradation)
**Purpose:** Estimates accelerated aging from heat and humidity exposure.

**Formula:**
```
η = exp(γ0 + γ1 × ln(RH) + γ2 / T_mod)

Where:
  η = Aging acceleration factor (dimensionless)
  RH = Relative humidity (%)
  T_mod = Module temperature (Kelvin)
  γ0, γ1, γ2 = Material-specific constants
```

**Interpretation:** η > 1 means degradation is faster than baseline; η = 2 means 2× faster aging.

**Example:**
```
Comparing baseline vs. climate stress conditions:

Baseline Conditions (reference):
  • Temperature: 25°C (298K)
  • Relative Humidity: 50%
  • η_base = 1.0 (by definition)

Climate Stress Conditions (RCP 4.5, 2050):
  • Temperature: 28°C (301K) - 3°C warmer
  • Relative Humidity: 60% - 10% more humid
  • η_stress ≈ 1.8 (degradation 80% faster)

Impact on Panel Life:
  • Baseline degradation rate: 0.5%/year
  • Climate-stressed rate: 0.5% × 1.8 = 0.9%/year
  
  • Time to reach 80% output (economic threshold):
    - Baseline: 20% ÷ 0.5% = 40 years
    - Climate: 20% ÷ 0.9% = 22 years
    
  • Life reduction: (40 - 22) / 40 = 45%

This is why heat + humidity stress is a major driver of EFR.
```

**Source:** Well-established in semiconductor reliability engineering

---

### Coffin-Manson Model (Thermal Fatigue)
**Purpose:** Estimates cycles to failure from thermal expansion/contraction (freeze/thaw).

**Formula:**
```
N_f = C × (Δε_p)^(-k)

Where:
  N_f = Number of cycles to failure
  Δε_p = Plastic strain amplitude (from temperature swing)
  C, k = Material-specific constants
```

**Application:** More freeze/thaw cycles → Faster accumulation of microcracks → Shorter panel life

---

### Palmgren-Miner Rule (Cumulative Fatigue)
**Purpose:** Estimates when wind turbine components fail from cumulative stress cycles.

**Formula:**
```
D = Σ(n_i / N_i)

Where:
  D = Cumulative damage (D = 1 means failure)
  n_i = Actual cycles at stress level i
  N_i = Cycles to failure at stress level i (from S-N curve)
```

**Application:** Higher wind variability → More stress cycles → Faster fatigue → Shorter turbine life

**Example:**
```
Maverick Creek Wind Turbine - Blade Root Fatigue:

Stress Level | n_i (cycles/yr) | N_i (to failure) | Damage/year
-------------|-----------------|------------------|------------
Low (5-10 m/s)  | 50,000      | 100,000,000      | 0.0005
Med (10-15 m/s) | 30,000      | 10,000,000       | 0.003
High (15-20 m/s)| 10,000      | 1,000,000        | 0.01
Very High (>20) | 1,000       | 100,000          | 0.01
-------------|-----------------|------------------|------------
Total annual damage D = 0.0235 per year

Time to failure (D = 1): 1 / 0.0235 = 42.5 years

CLIMATE SCENARIO (more extreme winds):
Stress Level | n_i (cycles/yr) | N_i (to failure) | Damage/year
-------------|-----------------|------------------|------------
Low (5-10 m/s)  | 45,000      | 100,000,000      | 0.00045
Med (10-15 m/s) | 28,000      | 10,000,000       | 0.0028
High (15-20 m/s)| 14,000      | 1,000,000        | 0.014
Very High (>20) | 2,000       | 100,000          | 0.02
-------------|-----------------|------------------|------------
Total annual damage D = 0.0372 per year (+58% increase)

Time to failure: 1 / 0.0372 = 26.9 years

Life reduction: (42.5 - 26.9) / 42.5 = 37%
```

---

### Fire Weather Index (FWI)
**Purpose:** Proxy for wildfire risk based on weather conditions.

**Inputs:** Temperature, relative humidity, wind speed, precipitation

**Formula:** Complex multi-component calculation (Canadian Forest Fire Weather Index System)

**Relevance:** Can be computed from CMIP variables to estimate wildfire exposure trends

---

## Climate Metrics & Indices

### Heat Wave Index
**Definition:** 3+ consecutive days where both T_max and T_min exceed the 90th percentile of historical baseline.

**Source:** Copernicus Global Drought Observatory

---

### Cold Wave Index
**Definition:** 3+ consecutive days where both T_max and T_min fall below the 10th percentile of historical baseline.

**Source:** Copernicus Global Drought Observatory

---

### Freeze/Frost Days
**Definitions:**
- **Frost Day:** T_min < 0°C
- **Icing Day:** T_max < 0°C (entire day below freezing)

**Source:** Climpact-sci.org

---

### Extreme Precipitation
**Definition:** Maximum 5-day rolling sum of precipitation in a year.

**Alternative:** Count of days exceeding the 95th percentile of historical daily precipitation.

---

### Wind Cut-Out Threshold
**Definition:** Wind speed above which turbines shut down for safety (typically 25 m/s).

**Note:** Varies by turbine model (22-28 m/s range)

**Example:**
```
Maverick Creek Wind - Extreme Wind Production Loss:

Typical turbine power curve:
  Wind Speed  | Power Output
  ------------|-------------
  0-3 m/s     | 0 MW (below cut-in)
  3-12 m/s    | Increasing (cubic relationship)
  12-25 m/s   | Rated power (e.g., 3 MW)
  >25 m/s     | 0 MW (cut-out for safety)

Base Scenario (current climate):
  • Hours >25 m/s: 50 hours/year
  • Lost generation: 50 h × 491.6 MW = 24,580 MWh
  • Revenue loss at $50/MWh: $1.23M/year

Climate Scenario (RCP 4.5, 2040 - more extreme winds):
  • Hours >25 m/s: 85 hours/year (+70%)
  • Lost generation: 85 h × 491.6 MW = 41,786 MWh
  • Revenue loss at $50/MWh: $2.09M/year
  • Additional loss: $0.86M/year

Note: This is a PERFORMANCE impact (Step 2), not a LIFE impact (Step 4).
The turbine survives but loses production during extreme wind events.
```

---

## Equipment & Asset Terms

### Utility-Scale Solar/Wind
**Definition:** Large commercial installations (typically >1 MW) connected to the grid.

**Team's Pilot Sites:**
| Site | Type | Capacity | Location |
|------|------|----------|----------|
| Hayhurst Texas Solar | Solar PV | 24.8 MW | Culberson, TX |
| Maverick Creek Wind | Wind | 491.6 MW | Concho, TX |

---

### PPA (Power Purchase Agreement)
**Definition:** Long-term contract to sell electricity at fixed or formula-based prices.

**Relevance:** Contracted assets have more predictable revenue → Lower WACC → Different risk profile

**Example:**
```
Hayhurst Solar - Two Scenarios:

CONTRACTED (with 20-year PPA):
  • PPA Price: $45/MWh (fixed for 20 years)
  • Revenue certainty: HIGH
  • WACC: 6-7% (lower risk)
  • Climate impact is primarily on GENERATION (not price)

MERCHANT (no PPA, sell at spot prices):
  • Average Price: $50/MWh (but varies $20-$120)
  • Revenue certainty: LOW
  • WACC: 10-12% (higher risk)
  • Climate impact affects BOTH generation AND price exposure

For NAV impairment analysis:
  • Contracted: Focus on generation decline and BI losses
  • Merchant: Also need to consider price volatility
    (climate could increase scarcity prices, partially offsetting
    generation losses - or renewable overbuild could crash prices)

The pilot focuses on contracted assets (simpler to model).
Price evolution is excluded but noted as Phase 1 enhancement.
```

---

### Degradation Rate
**Definition:** Annual percentage decline in power output over time.

**Industry Standard (Solar):**
- Median: ~0.5%/year (Jordan & Kurtz, NREL)
- Range: 0.3-0.8%/year depending on technology and climate

**Example - Baseline vs Climate-Accelerated Degradation:**
```
Hayhurst Solar (24.8 MW nameplate):

BASELINE DEGRADATION (0.5%/year):
  Year  | Output % | Generation (GWh) | Revenue ($50/MWh)
  ------+----------+------------------+------------------
    1   |  100.0%  |     54.6         |    $2.73M
    5   |   97.5%  |     53.2         |    $2.66M
   10   |   95.1%  |     51.9         |    $2.60M
   15   |   92.8%  |     50.7         |    $2.53M
   20   |   90.5%  |     49.4         |    $2.47M
   25   |   88.2%  |     48.2         |    $2.41M

CLIMATE-ACCELERATED DEGRADATION (0.9%/year - from Peck's Model):
  Year  | Output % | Generation (GWh) | Revenue ($50/MWh)
  ------+----------+------------------+------------------
    1   |  100.0%  |     54.6         |    $2.73M
    5   |   95.6%  |     52.2         |    $2.61M
   10   |   91.4%  |     49.9         |    $2.50M
   15   |   87.4%  |     47.7         |    $2.39M
   20   |   83.5%  |     45.6         |    $2.28M
   25   |   79.8%  |     43.6         |    $2.18M

Cumulative Revenue Loss over 25 years:
  • Baseline total: ~$63.5M
  • Climate-accelerated: ~$59.2M
  • Loss: $4.3M (6.8% revenue reduction from degradation alone)
```

---

### Capacity Factor
**Definition:** Actual generation divided by theoretical maximum generation.

**Formula:**
```
Capacity_Factor = Actual_Generation / (Nameplate_Capacity × 8760 hours)
```

**Typical Values:**
| Asset Type | Typical Capacity Factor |
|------------|------------------------|
| Solar PV (utility-scale) | 20-30% |
| Wind (onshore) | 25-45% |

**Example:**
```
Hayhurst Solar (24.8 MW):
  • Nameplate Capacity: 24.8 MW
  • Hours per year: 8,760
  • Theoretical max: 24.8 MW × 8,760 h = 217,248 MWh = 217.2 GWh

  • Actual Generation: 54.6 GWh/year
  • Capacity Factor: 54.6 / 217.2 = 25.1%

Maverick Creek Wind (491.6 MW):
  • Nameplate Capacity: 491.6 MW
  • Theoretical max: 491.6 MW × 8,760 h = 4,306,416 MWh = 4,306 GWh

  • Actual Generation: ~1,550 GWh/year
  • Capacity Factor: 1,550 / 4,306 = 36.0%

Why it matters for climate analysis:
  • Higher temperatures → Lower solar efficiency → Lower capacity factor
  • Changed wind patterns → Different wind capacity factor
  • Capacity factor directly affects revenue and NAV
```

---

## Quick Reference: Key Equations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SUMMARY OF KEY EQUATIONS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  NAV IMPAIRMENT:                                                            │
│  NAV_Impairment_% = (1 - NPV_climate / NPV_base) × 100%                    │
│                                                                              │
│  IMPAIRED USEFUL LIFE:                                                      │
│  IUL = EUL × [1 - Σ(EFR_i × SCVR_i)]                                       │
│                                                                              │
│  BUSINESS INTERRUPTION (Climate-Adjusted):                                  │
│  BI_climate(t) = BI_base × (1 + HCR(t))                                    │
│                                                                              │
│  NET PRESENT VALUE:                                                         │
│  NPV = Σ [Revenue_t / (1 + WACC)^t]  for t = 1 to EUL or IUL              │
│                                                                              │
│  SOLAR POWER (Temperature-Adjusted):                                        │
│  P_actual = P_rated × [1 + γ × (T_cell − 25°C)]                            │
│                                                                              │
│  AGING ACCELERATION (Peck's Model):                                         │
│  η = exp(γ0 + γ1 × ln(RH) + γ2 / T_kelvin)                                 │
│                                                                              │
│  FATIGUE CYCLES (Coffin-Manson):                                           │
│  N_f = C × (Δε_p)^(-k)                                                     │
│                                                                              │
│  CUMULATIVE DAMAGE (Palmgren-Miner):                                        │
│  D = Σ(n_i / N_i)  [D = 1 means failure]                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Version History

| Date | Changes |
|------|---------|
| Feb 1, 2026 | Initial creation |
| Feb 1, 2026 | Added detailed WACC vs IRR vs Discount Rate comparison section |
| Feb 1, 2026 | Enhanced SCVR section with ASCII visualizations and flow diagram |
| Feb 1, 2026 | Added NAV vs NPV distinction section |

---

*End of Terminology Guide*
