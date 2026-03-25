"""
SCVR Dashboard — Interactive Streamlit visualisation of SCVR outputs.

Reads pre-computed data from data/output/scvr/<site_id>/scvr_report.json.
No recomputation — pure consumer of compute_scvr.py outputs.

Usage:
    streamlit run scripts/presentation/scvr_dashboard.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
SITES_PATH = ROOT / "data" / "schema" / "sites.json"
OUTPUT_DIR = ROOT / "data" / "output" / "scvr"

# ── Constants ────────────────────────────────────────────────────────────────
VAR_LABELS = {
    "tasmax": "Max Temperature",
    "tasmin": "Min Temperature",
    "tas": "Mean Temperature",
    "pr": "Precipitation",
    "sfcWind": "Wind Speed",
    "hurs": "Relative Humidity",
}

SCENARIO_LABELS = {"ssp245": "SSP2-4.5", "ssp585": "SSP5-8.5"}

# Variables where SCVR (mean metric) is unreliable — Pathway B primary
PATHWAY_B_VARS = {"pr"}

SCENARIO_COLORS = {"ssp245": "#3498db", "ssp585": "#e74c3c"}

SEVERITY_COLORS = {
    "LOW": "#27ae60",
    "MODERATE": "#f39c12",
    "ELEVATED": "#e67e22",
    "HIGH": "#c0392b",
}

SEVERITY_THRESHOLDS = [
    (0.05, "LOW", "#27ae60"),
    (0.10, "MODERATE", "#f39c12"),
    (0.20, "ELEVATED", "#e67e22"),
    (float("inf"), "HIGH", "#c0392b"),
]

PLOTLY_TEMPLATE = "plotly_white"

# ── Methodology Content ──────────────────────────────────────────────────────
# Hardcoded from docs/learning/B_scvr_methodology/04_scvr_methodology.md,
# scripts/analysis/scvr/README.md, and docs/discussion/ so the dashboard
# works standalone without requiring the docs folder.

METHODOLOGY_WHAT = r"""
**SCVR (Severe Climate Variability Rating)** is a single number that measures how much
a climate variable's distribution shifts between a historical baseline and a future period.

It answers: *"By what fraction did the climate distribution shift between the
historical baseline and the asset's future?"*

### The Formula

```
SCVR = (area_future - area_baseline) / area_baseline
```

Where **area** is the area under the empirical exceedance curve — a descending sort
of all daily values plotted against exceedance probability [0, 1], integrated with
the trapezoidal rule.

### Key Insight: SCVR = Mean Ratio

At large sample sizes (~300,000 daily values from 28+ models × 30 years), the area
under the exceedance curve converges to the expected value E[X]. This means:

```
SCVR  =  (mean_future - mean_baseline) / mean_baseline
```

Three independent methods — empirical trapezoid, normal parametric (MLE), and direct
mean ratio — agree to **6+ decimal places** across all 7 variables × 2 scenarios.
The exceedance curve formulation is retained as a **communication framework** (it
visualises the shift intuitively), but the computation is a mean ratio.

### What the Values Mean

| SCVR | Meaning |
|------|---------|
| **= 0** | No change from baseline |
| **0.00 – 0.05** | Low change |
| **0.05 – 0.10** | Moderate change |
| **0.10 – 0.20** | Elevated change |
| **> 0.20** | High change — review for tail sensitivity |
| **< 0** | Fewer extremes (e.g., fewer frost days under warming) |

A positive SCVR means the distribution shifted toward higher values.

### SCVR's Blind Spot

Because SCVR is a **mean-based** metric, it can miss **tail fattening** — situations
where extreme events intensify even though the average barely changes.

**Real example — Precipitation (Hayhurst Solar):**

| Metric | Value | What it says |
|--------|-------|-------------|
| Mean SCVR | -0.1% | "Almost no change" |
| P95 SCVR | +1.9% | 95th percentile shifted up |
| CVaR 95% | +2.4% | Average severity of tail events increased |
| **Tail Confidence** | **LOW** | Mean and tail decouple — SCVR alone is misleading |

The mean barely moved, but the tails ARE fattening. This is why we compute
**companion metrics** (see the Report Card tab) alongside SCVR — they tell you
when SCVR is trustworthy vs when it understates tail risk.

### Exceedance Curves

Think of the daily temperatures at a site over 30 years. Sort them from hottest to
coldest and draw a curve — that's an **exceedance curve**. The area under it summarises
the whole distribution. SCVR measures how much that area grew from baseline to future.

```
  Baseline (B) vs Future (F):

  Value
    47 |  F                        F is shifted right/up
    45 |B F                        = more extreme values
       |B  F
    40 |B   FF
       | B    FF
    35 | BB     FFF
       |   BBB     FFFF
    30 |     BBBBB     FFFFF
       |         BBBBBBB   FFFFF
    25 |              BBBBBBBB  FFFFFF
       └──────────────────────────────────
       0%            50%            100%
                Exceedance Probability
```
"""

METHODOLOGY_HOW = """
### Step-by-Step Computation

1. **Collect daily values** — 30 years × ~365 days × N models (pooled) = ~300,000+ values
   per period (baseline 1985–2014, future 2026–2055)

2. **Sort descending** — highest value first (hottest day at index 0)

3. **Assign exceedance probabilities** — `np.linspace(0, 1, n)` normalises both arrays
   to [0, 1] regardless of length

4. **Compute area** — `np.trapezoid(sorted_values, exc_probs)` — trapezoidal integration

5. **Compare** — `SCVR = (area_future - area_baseline) / area_baseline`

### The Core Function

```python
def compute_scvr(baseline_values, future_values):
    b = np.sort(baseline_values[~np.isnan(baseline_values)])[::-1]
    f = np.sort(future_values[~np.isnan(future_values)])[::-1]

    exc_b = np.linspace(0, 1, len(b))
    exc_f = np.linspace(0, 1, len(f))

    area_b = float(np.trapezoid(b, exc_b))
    area_f = float(np.trapezoid(f, exc_f))

    scvr = (area_f - area_b) / area_b if area_b != 0 else 0.0
    return {"scvr": scvr, "area_baseline": area_b, "area_future": area_f}
```

### Mathematical Note

This computation is mathematically equivalent to `(mean(future) - mean(baseline)) / mean(baseline)`.
The area under the exceedance curve equals E[X] when n is large (error ~10^-11 at n=300k).
The exceedance formulation is retained for its visual interpretability — seeing the curves
shift makes the concept tangible for non-technical stakeholders.

### Why Daily Data — Not Annual Means

Annual aggregation destroys tail information. A 45°C extreme day gets averaged with
300+ normal days and becomes invisible. SCVR uses **all ~300,000 daily values** to
preserve the full distribution shape including extremes.

### Ensemble Pooling

All available CMIP6 models are **pooled** — daily values from all models are concatenated
into one array before computing exceedance. A 28-model ensemble with 30 years each
produces ~306,600 daily values. This captures both inter-model spread and inter-annual
variability in a single robust estimate.
"""

METHODOLOGY_EQUIVALENCE = r"""
### The Equivalence Proof

Three independent methods of computing SCVR produce **identical results** (to 6+ decimal places):

| Method | Formula | Approach |
|--------|---------|----------|
| **Empirical Trapezoid** | `trapezoid(sorted_desc, linspace(0,1,n))` | Area under exceedance curve |
| **Normal Parametric (MLE)** | Fit N(mu, sigma), compute `integral of x * (1-CDF)` | Parametric area |
| **Direct Mean Ratio** | `(mean_future - mean_baseline) / mean_baseline` | Simple arithmetic |

**Why they agree:** At large n, sorting n values and integrating against uniform spacing
on [0, 1] is equivalent to computing the sample mean. Formally:

```
area = integral_0^1 Q(p) dp  =  E[X]     (as n -> infinity)
```

where Q(p) is the quantile function. The convergence error is ~10^-11 at n=300,000.

### Verified Across All Variables

| Variable | Empirical | Mean Ratio | Max Divergence |
|----------|-----------|------------|----------------|
| tasmax | +0.068896 | +0.068896 | 0.000000 |
| tasmin | +0.144137 | +0.144137 | 0.000000 |
| pr | -0.001001 | -0.001001 | 0.000000 |
| sfcWind | -0.022011 | -0.022011 | 0.000000 |
| hurs | -0.031207 | -0.031207 | 0.000022 |

### Practical Implication

The exceedance curve is a **communication tool**, not a computational necessity.
We keep the curve because it makes the concept visual and intuitive. But the number
itself is just the fractional change in the mean — and that's exactly why it has a
blind spot for tail fattening (see companion metrics in the Report Card tab).
"""

METHODOLOGY_STRATEGY = """
### Variable-Specific Annual Strategy

Not all variables behave the same under climate change. The annual SCVR strategy
depends on the variable's signal-to-noise ratio:

| Strategy | Variables | Method | Why |
|----------|-----------|--------|-----|
| **anchor_3_linear** | tasmax, tasmin, tas | Split future into 3 decades. Compute SCVR per decade as "anchors". Fit linear trend. Interpolate to annual. | Temperature has a clean, monotonic signal (R² > 0.95) |
| **period_average** | pr, sfcWind, hurs | Use decade-level SCVR directly. No interpolation. | Too noisy for linear fit (R² < 0.7) |

### Decade Windows

Three non-overlapping 10-year windows within the future period:

| Decade | Years | Role |
|--------|-------|------|
| 2026–2035 | Near-term | Already underway |
| 2036–2045 | Mid-term | Core projection period |
| 2046–2055 | End of period | End of typical asset life |

### Anchor Fitting (Temperature)

For temperature variables, the 3 decade SCVR values serve as "anchors". A linear
polyfit through the 3 midpoints (2030.5, 2040.5, 2050.5) produces a slope and
intercept. Annual values are interpolated from this fit.

**Empirical R² values** (Hayhurst Solar):
- tasmax SSP2-4.5: R² = 0.991
- tasmax SSP5-8.5: R² = 0.975
- tasmin SSP2-4.5: R² = 0.999
- tas SSP2-4.5: R² = 0.998

**Why precipitation doesn't get this treatment:**
Precipitation R² ≈ 0.59, wind R² ≈ 0.13 — fitting a line through 3 noisy points
would produce misleading annual values.
"""

METHODOLOGY_INTERPRET = r"""
### SCVR Severity Scale

| SCVR Range | Severity | Colour | Example |
|------------|----------|--------|---------|
| 0.00 - 0.05 | LOW | Green | sfcWind at inland sites |
| 0.05 - 0.10 | MODERATE | Amber | tasmax under SSP2-4.5 |
| 0.10 - 0.20 | ELEVATED | Orange | tasmin under SSP5-8.5 |
| > 0.20 | HIGH | Red | Review for tail sensitivity |
| < 0 | Reduction | - | Frost days under warming |

### Tier 1: Companion Metrics (Audit Trail)

Because SCVR is a mean-based metric, it can miss tail fattening. These **Tier 1 companions**
are always reported alongside SCVR to flag when the mean is misleading:

| Metric | Formula | What It Tells You |
|--------|---------|-------------------|
| **P95 SCVR** | `(P95_future - P95_baseline) / |P95_baseline|` | How much the 95th percentile shifted — catches tail fattening |
| **P99 SCVR** | `(P99_future - P99_baseline) / |P99_baseline|` | Extreme tail (rarest 1%) — confirms if extremes intensify |
| **CVaR 95%** | `(E[X|X>=P95]_f - E[X|X>=P95]_b) / |E[X|X>=P95]_b|` | Average severity of tail events (Expected Shortfall) |
| **Mean-Tail Ratio** | `P95_SCVR / Mean_SCVR` | How well the mean tracks the tail (>0.6 = good, <0.3 = poor) |
| **Model IQR** | `P75 - P25 of per-model SCVR` | How much individual climate models disagree |
| **Tail Confidence** | Algorithmic (see below) | Final verdict: is SCVR reliable for this variable? |

### Tail Confidence Classification

| Flag | Rule | Meaning |
|------|------|---------|
| **HIGH** | Mean-Tail Ratio > 0.6 | Mean and tail agree — SCVR is trustworthy |
| **MODERATE** | Default | Partial agreement — check tail metrics |
| **LOW** | Mean-Tail Ratio < 0.3 OR Model IQR > 2x|Mean| | Weak signal or high model disagreement |
| **DIVERGENT** | sign(Mean) != sign(P95) | Mean and tail oppose — SCVR is misleading |

### Variable Classes

| Class | Variables | Confidence | Implication |
|-------|-----------|-----------|-------------|
| **A** | tasmax, tas | HIGH | SCVR sufficient — mean captures the signal |
| **B** | pr, rsds | LOW / DIVERGENT | SCVR misleading — Pathway B required for hazard counting |
| **C** | tasmin, hurs, sfcWind | MODERATE | SCVR adequate with caveats — check companions |

### Tier 2: Distribution Diagnostics

These deeper diagnostics are available when Tier 1 flags a concern:

| Metric | What It Tells You |
|--------|-------------------|
| **Shape metrics** (skewness, kurtosis) | Whether the distribution shape is changing beyond a simple shift |
| **GEV** (Generalised Extreme Value) | Parametric model of annual block maxima — shape parameter (xi) indicates tail heaviness |
| **GPD** (Generalised Pareto) | Peaks-over-threshold — how the tail above P95 behaves parametrically |
| **KS test** | Kolmogorov-Smirnov goodness-of-fit — does the fitted model match the data? |
"""

METHODOLOGY_PIPELINE = """
### Downstream Pipeline

SCVR is the **central hub** connecting climate projections to financial impact:

```
SCVR(t)                           Annual climate shift per variable
  │
  ├──► HCR(t)                     Hazard Change Ratio
  │      │                        (heat x2.5, flood x1.5-2.0, etc.)
  │      │
  │      ├──► BI losses           Revenue lost to hazard events
  │      │
  │      └──► EFR(t)              Equipment Failure Ratio
  │             │                 (Peck's, Coffin-Manson, Palmgren-Miner)
  │             │
  │             └──► IUL          Impaired Useful Life
  │                               (e.g., 25yr → 21yr)
  │
  └──► Gen(t) adjustment          Climate-adjusted annual generation
         │
         └──► CFADS(t)           Cash flow available for debt service
                │
                └──► NAV         Net Asset Value impairment
```

### Variable → Hazard Routing

| Variable | Hazard Channel | Downstream Impact |
|----------|---------------|-------------------|
| tasmax | Heat stress | Equipment degradation (Peck's model), generation derating |
| tasmin | Freeze/thaw | Mechanical fatigue (Coffin-Manson), icing damage |
| tas | Ambient thermal | Overall thermal stress envelope |
| pr | Flood/drought | Business interruption, erosion, water availability |
| sfcWind | Wind loading | Turbine fatigue (Palmgren-Miner), generation variability |
| hurs | Humidity/corrosion | Accelerated corrosion (Peck's), PV soiling |

### Pathway A vs Pathway B (HCR Computation)

The pipeline uses **two pathways** to compute Hazard Change Ratios:

| Pathway | Method | Used For | How |
|---------|--------|----------|-----|
| **A** | SCVR-based | IUL shortening (86% of NAV impact) | Applies SCVR to Peck's/Coffin-Manson degradation models |
| **B** | Direct daily counting | Business interruption (5 key hazards) | Counts threshold crossings from raw daily data — bypasses SCVR |

**Why Pathway B matters:** For precipitation and other Class B variables, SCVR misses
tail fattening (see "SCVR's Blind Spot" above). But the pipeline is **already financially
correct** because Pathway B counts extreme events directly from daily data — it doesn't
rely on SCVR at all. Precipitation's tail fattening IS captured in the financial output.

**Why companion metrics still matter:** Pathway B is not self-documenting. A reviewer
looking at `SCVR_pr = -0.1%` cannot tell that the pipeline handles tails correctly
without tracing through Pathway B code. Companion metrics (P95 SCVR, Tail Confidence)
make this visible instantly — turning an hours-long audit into a seconds-long check.
"""

METHODOLOGY_PROCESSING = r"""
### Units & Preprocessing

All data comes from **NEX-GDDP CMIP6** daily climate projections. The pipeline applies
these conversions before any computation:

| Variable | Raw Unit (CMIP6) | Output Unit | Conversion |
|----------|-----------------|-------------|------------|
| tasmax, tasmin, tas | Kelvin (K) | Celsius (°C) | -273.15 (auto-detected if mean > 200) |
| pr | kg/m²/s | mm/day | ×86400 |
| sfcWind | m/s | m/s | No conversion needed |
| hurs | % | % | No conversion needed |

### Precipitation: Wet-Day Filtering for Tail Metrics

At arid sites (e.g., Hayhurst, West Texas), **~78% of days are dry** (< 0.1 mm/day).
This means:

- The **all-day P95** sits in the dry/wet transition zone (~5.9 mm) — it tells you nothing
  about extreme rainfall intensity
- The **wet-day P95** (filtering to > 0.1 mm) captures actual rainfall events (~15 mm) —
  this is where tail fattening is visible

**What uses which:**

| Metric | Days Used | Why |
|--------|-----------|-----|
| Mean SCVR | All days | Correct for the overall distribution mean |
| P95 / P99 SCVR (Report Card) | **Wet days only** (> 0.1 mm) | Meaningful tail comparison |
| CVaR 95% (Report Card) | **Wet days only** (> 0.1 mm) | Average severity of actual rain events |
| Shape metrics percentiles (Distribution Shape tab) | All days | Full distribution characterisation |
| GEV annual maxima | All days | Annual max is always a wet day |
| GPD exceedances | All days | Threshold set on full distribution |

**Important:** The P95 shown in the **Distribution Shape** tab (all days, ~5.9 mm) is
different from the P95 used in the **Report Card's** P95 SCVR (wet days, ~15 mm).
Both are correct for their purpose — the shape tab characterises the full distribution
(including the dry-day mass), while the Report Card focuses on hazard-relevant tail shifts.

### Variable Specification

| Variable | SCVR Strategy | Typical R² | Tail Confidence | Notes |
|----------|--------------|-----------|----------------|-------|
| tasmax | anchor_3_linear | > 0.97 | HIGH | Clean monotonic warming signal |
| tasmin | anchor_3_linear | > 0.99 | MODERATE | Mean overstates tail somewhat |
| tas | anchor_3_linear | > 0.99 | HIGH | Average of daily min/max |
| pr | period_average | ~ 0.59 | LOW / DIVERGENT | Wet-day filtering for tail metrics; Pathway B for hazards |
| sfcWind | period_average | ~ 0.13 | MODERATE | Very noisy; decade-level SCVR only, no annual interpolation |
| hurs | period_average | ~ 0.50 | MODERATE | Moderate noise; corrosion/soiling pathway |
"""


def scvr_severity(value):
    for threshold, label, _ in SEVERITY_THRESHOLDS:
        if abs(value) < threshold:
            return label
    return "HIGH"


def scvr_color(value):
    for threshold, _, color in SEVERITY_THRESHOLDS:
        if abs(value) < threshold:
            return color
    return "#c0392b"


def var_label(v):
    return VAR_LABELS.get(v, v)


def scen_label(s):
    return SCENARIO_LABELS.get(s, s)


# ── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_sites():
    with open(SITES_PATH) as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


@st.cache_data
def load_site_data(site_id):
    report_path = OUTPUT_DIR / site_id / "scvr_report.json"
    if not report_path.exists():
        return None
    with open(report_path) as f:
        report = json.load(f)
    return {
        "report": report,
        "ensemble": pd.DataFrame(report["ensemble_scvr"]),
        "decade": pd.DataFrame(report["decade_scvr"]),
        "annual": pd.DataFrame(report["annual_scvr"]),
        "shape": pd.DataFrame(report["shape_metrics"]),
        "gev_fits": report.get("gev_fits", {}),
        "gpd_fits": report.get("gpd_fits", {}),
        "anchor_fits": report.get("anchor_fits", {}),
        "companions": report.get("companion_metrics", []),
        "config": report.get("config", {}),
        "models": report.get("models", {}),
    }


# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SCVR Dashboard",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
sites = load_sites()
site_ids = list(sites.keys())

with st.sidebar:
    st.title("SCVR Dashboard")
    st.caption("Severe Climate Variability Rating")

    selected_site = st.selectbox(
        "Site",
        site_ids,
        format_func=lambda s: sites[s]["name"],
    )

    data = load_site_data(selected_site)

    if data is None:
        st.error(f"No SCVR outputs for **{selected_site}**. Run `compute_scvr.py` first.")
        st.stop()

    config = data["config"]
    all_scenarios = config.get("scenarios", ["ssp245", "ssp585"])
    all_variables = config.get("variables", list(VAR_LABELS.keys()))

    selected_scenarios = st.multiselect(
        "Scenarios",
        all_scenarios,
        default=all_scenarios,
        format_func=scen_label,
    )
    selected_variables = st.multiselect(
        "Variables",
        all_variables,
        default=all_variables,
        format_func=var_label,
    )

    if not selected_scenarios or not selected_variables:
        st.warning("Select at least one scenario and one variable.")
        st.stop()

    # Site info card
    st.divider()
    site_info = sites[selected_site]
    st.markdown(f"**{site_info['name']}**")
    st.caption(
        f"{site_info.get('county', '')}, {site_info.get('state', '')}  \n"
        f"({site_info['lat']:.4f}, {site_info['lon']:.4f})"
    )
    col1, col2 = st.columns(2)
    col1.metric("Capacity", f"{site_info.get('capacity_mw', '?')} MW")
    col2.metric("EUL", f"{site_info.get('eul_years', '?')} yr")

    total_models = max(
        (m.get("count", 0) for m in data["models"].values()), default=0
    )
    st.metric("Max Models", total_models)
    st.caption(
        f"Baseline: {config['baseline_years'][0]}–{config['baseline_years'][1]}  \n"
        f"Future: {config['future_years'][0]}–{config['future_years'][1]}"
    )


# ── Filter helper ────────────────────────────────────────────────────────────
def filt(df, scenarios=True, variables=True):
    """Filter a DataFrame by selected scenarios and variables."""
    mask = pd.Series(True, index=df.index)
    if scenarios and "scenario" in df.columns:
        mask &= df["scenario"].isin(selected_scenarios)
    if variables and "variable" in df.columns:
        mask &= df["variable"].isin(selected_variables)
    return df[mask].copy()


# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab_rc, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Summary", "Report Card", "Decade Progression", "Annual Trajectory",
    "Distribution Shape", "Extreme Value Fits",
    "Methodology", "Raw Report",
])


# ══════════════════════════════════════════════════════════════════════════════
# Tab 1: Summary
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    ens = filt(data["ensemble"])
    if ens.empty:
        st.info("No ensemble data for current filters.")
    else:
        # Metric cards
        cols = st.columns(4)
        max_row = ens.loc[ens["scvr"].idxmax()]
        cols[0].metric(
            "Highest SCVR",
            f"{max_row['scvr']:.4f}",
            delta=f"{var_label(max_row['variable'])} / {scen_label(max_row['scenario'])}",
            delta_color="off",
        )
        cols[1].metric("Variables", len(selected_variables))
        cols[2].metric(
            "Baseline",
            f"{config['baseline_years'][0]}–{config['baseline_years'][1]}",
        )
        cols[3].metric(
            "Future",
            f"{config['future_years'][0]}–{config['future_years'][1]}",
        )

        # SCVR Heatmap
        st.subheader("SCVR Heatmap")
        pivot = ens.pivot_table(
            index="variable", columns="scenario", values="scvr", aggfunc="first"
        )
        pivot = pivot.reindex(index=selected_variables, columns=selected_scenarios)
        pivot_display = pivot.rename(index=var_label, columns=scen_label)

        fig_heat = go.Figure(
            data=go.Heatmap(
                z=pivot_display.values,
                x=pivot_display.columns.tolist(),
                y=pivot_display.index.tolist(),
                text=np.vectorize(lambda v: f"{v:.4f}")(pivot_display.values),
                texttemplate="%{text}",
                textfont={"size": 14},
                colorscale=[
                    [0.0, "#27ae60"],
                    [0.33, "#f39c12"],
                    [0.66, "#e67e22"],
                    [1.0, "#c0392b"],
                ],
                zmin=0,
                zmax=max(0.20, float(pivot_display.max().max()) * 1.1),
                colorbar=dict(title="SCVR"),
            )
        )
        fig_heat.update_layout(
            template=PLOTLY_TEMPLATE,
            height=50 + 50 * len(selected_variables),
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        st.caption(
            "⚠ Precipitation SCVR ≈ 0 does not mean 'no change' — SCVR is a mean metric and "
            "precipitation extremes can intensify while the average stays flat. "
            "See the Report Card tab for tail confidence details."
        )

        # Grouped bar chart
        st.subheader("SCVR by Variable")
        ens_plot = ens.copy()
        ens_plot["var_label"] = ens_plot["variable"].map(var_label)
        ens_plot["scen_label"] = ens_plot["scenario"].map(scen_label)
        fig_bar = px.bar(
            ens_plot,
            x="var_label",
            y="scvr",
            color="scen_label",
            barmode="group",
            color_discrete_map={
                scen_label(s): c for s, c in SCENARIO_COLORS.items()
            },
            labels={"var_label": "Variable", "scvr": "SCVR", "scen_label": "Scenario"},
            template=PLOTLY_TEMPLATE,
        )
        fig_bar.add_hline(y=0.05, line_dash="dash", line_color="#888", annotation_text="0.05")
        fig_bar.add_hline(y=0.10, line_dash="dash", line_color="#888", annotation_text="0.10")
        fig_bar.update_layout(height=400, margin=dict(t=20))
        st.plotly_chart(fig_bar, use_container_width=True)

        # Model count per variable
        with st.expander("Model coverage per variable"):
            model_data = data["models"]
            rows = []
            for v in selected_variables:
                m = model_data.get(v, {})
                rows.append({
                    "Variable": var_label(v),
                    "Models": m.get("count", 0),
                    "Names": ", ".join(m.get("names", [])),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# Report Card: Companion Metrics (Tail Confidence Audit Trail)
# ══════════════════════════════════════════════════════════════════════════════

TAIL_CONFIDENCE_COLORS = {
    "HIGH": "#27ae60",
    "MODERATE": "#f39c12",
    "LOW": "#e67e22",
    "DIVERGENT": "#c0392b",
    "INSUFFICIENT_DATA": "#95a5a6",
}

with tab_rc:
    companions = data.get("companions", [])
    if not companions:
        st.info(
            "No companion metrics found. Re-run `compute_scvr.py` to generate "
            "the SCVR audit trail (per-model SCVR, tail confidence, etc.)."
        )
    else:
        st.subheader("SCVR Tail Confidence Report Card")
        st.caption(
            "Companion metrics that contextualise when SCVR is trustworthy vs misleading. "
            "Hover any column header for its definition and formula."
        )

        # ── Info banner for unreliable variables ────────────────────────────
        st.info(
            "**† = SCVR unreliable for this variable.** SCVR is a mean-based metric. "
            "For precipitation, the average barely changes but extreme events intensify — "
            "SCVR ≈ 0 does NOT mean 'no change.' These variables use **Pathway B** "
            "(direct threshold counting) instead. See the Tail Confidence column."
        )

        # ── Section 1: Tail Confidence Overview Table ────────────────────────
        table_rows = []
        for c in companions:
            vname = var_label(c["variable"])
            if c["variable"] in PATHWAY_B_VARS:
                vname += " †"
            table_rows.append({
                "Variable": vname,
                "Scenario": scen_label(c["scenario"]),
                "Mean SCVR": c.get("mean_scvr"),
                "P95 SCVR": c.get("tail_scvr_p95"),
                "P99 SCVR": c.get("extreme_scvr_p99"),
                "CVaR 95%": c.get("cvar95_ratio"),
                "Mean-Tail Ratio": c.get("mean_tail_ratio"),
                "Model IQR": c.get("model_iqr"),
                "Tail Confidence": c.get("tail_confidence", "N/A"),
            })
        df_rc = pd.DataFrame(table_rows)

        # Column config with help tooltips explaining each metric
        col_config = {
            "Variable": st.column_config.TextColumn(
                "Variable",
                help=(
                    "Climate variable being assessed. Variable-specific notes: "
                    "For precipitation (pr), P95/P99/CVaR use wet-day filtering "
                    "(>0.1 mm/day) — different from the all-day percentiles in the "
                    "Distribution Shape tab. Temperature values are in Celsius "
                    "(converted from Kelvin). For wind (sfcWind), SCVR is noisier "
                    "(R²~0.13) — decade-level values only, no annual interpolation."
                ),
            ),
            "Scenario": st.column_config.TextColumn(
                "Scenario",
                help="SSP emissions pathway. SSP2-4.5 = moderate mitigation; SSP5-8.5 = high emissions.",
            ),
            "Mean SCVR": st.column_config.NumberColumn(
                "Mean SCVR",
                format="%.6f",
                help=(
                    "Pooled SCVR across all models. Equivalent to the fractional change in the mean: "
                    "(mean_future - mean_baseline) / mean_baseline. "
                    "Proven equivalent to the area-under-exceedance-curve ratio at large n. "
                    "Positive = distribution shifted toward higher values."
                ),
            ),
            "P95 SCVR": st.column_config.NumberColumn(
                "P95 SCVR",
                format="%.6f",
                help=(
                    "Fractional change in the 95th percentile: "
                    "(P95_future - P95_baseline) / |P95_baseline|. "
                    "Captures tail behaviour that the mean-based SCVR misses. "
                    "If P95 SCVR >> Mean SCVR, tails are fattening even when the mean barely moves."
                ),
            ),
            "P99 SCVR": st.column_config.NumberColumn(
                "P99 SCVR",
                format="%.6f",
                help=(
                    "Fractional change in the 99th percentile: "
                    "(P99_future - P99_baseline) / |P99_baseline|. "
                    "Extreme tail metric — tracks the rarest 1% of daily values. "
                    "Useful when P95 and mean diverge; confirms whether extreme events are intensifying."
                ),
            ),
            "CVaR 95%": st.column_config.NumberColumn(
                "CVaR 95%",
                format="%.6f",
                help=(
                    "Conditional Value at Risk at 95%: fractional change in the mean of values "
                    "above the 95th percentile. Formula: (CVaR_future - CVaR_baseline) / |CVaR_baseline|, "
                    "where CVaR = E[X | X >= P95]. Also called Expected Shortfall. "
                    "Captures the average severity of tail events, not just a single quantile."
                ),
            ),
            "Mean-Tail Ratio": st.column_config.NumberColumn(
                "Mean-Tail Ratio",
                format="%.4f",
                help=(
                    "Ratio of P95 SCVR to Mean SCVR: P95_SCVR / Mean_SCVR. "
                    "Measures how well the mean represents the tail. "
                    "> 0.6 = strong agreement (tail moves with mean). "
                    "< 0.3 = weak linkage (mean and tail decouple). "
                    "Negative = mean and tail move in opposite directions (DIVERGENT)."
                ),
            ),
            "Model IQR": st.column_config.NumberColumn(
                "Model IQR",
                format="%.6f",
                help=(
                    "Interquartile range (P75 - P25) of per-model SCVR values. "
                    "Measures how much individual climate models disagree on the SCVR signal. "
                    "If IQR > 2x |Mean SCVR|, model disagreement exceeds the signal itself — "
                    "confidence is LOW regardless of mean-tail agreement."
                ),
            ),
            "Tail Confidence": st.column_config.TextColumn(
                "Tail Confidence",
                help=(
                    "Algorithmic classification of SCVR reliability for this variable:\n"
                    "- HIGH: Mean-Tail Ratio > 0.6 — mean and tail agree, SCVR is trustworthy.\n"
                    "- MODERATE: Partial agreement — SCVR adequate but check companions.\n"
                    "- LOW: Mean-Tail Ratio < 0.3 OR Model IQR > 2x|Mean| — weak signal.\n"
                    "- DIVERGENT: Mean and tail have opposite signs — SCVR is misleading, "
                    "Pathway B (direct hazard counting) required."
                ),
            ),
        }

        def _highlight_confidence(val):
            color = TAIL_CONFIDENCE_COLORS.get(val, "#95a5a6")
            return f"background-color: {color}; color: white; font-weight: bold"

        styled = df_rc.style.map(
            _highlight_confidence, subset=["Tail Confidence"]
        )
        st.dataframe(
            styled, use_container_width=True, hide_index=True,
            column_config=col_config,
        )

        # ── Confidence Level Legend ─────────────────────────────────────────
        st.markdown("**Confidence Levels:**")
        leg_cols = st.columns(4)
        leg_cols[0].markdown(":green[**HIGH**] — Mean and tail shift together. SCVR reliable.")
        leg_cols[1].markdown(":orange[**MODERATE**] — Weaker agreement. SCVR usable with caution.")
        leg_cols[2].markdown(":orange[**LOW**] — Weak linkage or high model disagreement.")
        leg_cols[3].markdown(":red[**DIVERGENT**] — Mean and tail oppose. SCVR misleading.")

        # ── Metric Definitions (expandable reference) ─────────────────────────
        with st.expander("Metric Definitions & Formulas"):
            st.markdown(r"""
| Metric | Formula | What it tells you |
|--------|---------|-------------------|
| **Mean SCVR** | `(mean_future - mean_baseline) / mean_baseline` | Fractional shift in the distribution centre. Mathematically equivalent to the area-under-exceedance-curve ratio (proven to ~10^-11 at n=300k daily values). |
| **P95 SCVR** | `(P95_future - P95_baseline) / |P95_baseline|` | How much the 95th percentile shifted. Catches tail fattening that the mean misses entirely. |
| **P99 SCVR** | `(P99_future - P99_baseline) / |P99_baseline|` | Same as P95 but for the extreme 1% tail. Confirms whether the rarest events are intensifying. |
| **CVaR 95%** | `(E[X|X>=P95]_future - E[X|X>=P95]_baseline) / |E[X|X>=P95]_baseline|` | Also called *Expected Shortfall*. Average severity of tail events above the 95th percentile, not just a point quantile. |
| **Mean-Tail Ratio** | `P95_SCVR / Mean_SCVR` | How well the mean tracks the tail. >0.6 = strong linkage, <0.3 = weak, negative = opposing directions. |
| **Model IQR** | `P75 - P25 of per-model SCVR values` | Spread of SCVR across individual climate models. High IQR relative to Mean SCVR = models disagree on the signal. |
| **Tail Confidence** | Algorithmic (see below) | Final classification: is SCVR trustworthy for this variable? |

**Tail Confidence Algorithm:**
1. If `sign(Mean) != sign(P95)` and both > 0.5% magnitude: **DIVERGENT**
1b. If `|Mean| <= 0.5%` but `|P95| > 0.5%` and signs differ: **DIVERGENT** *(near-zero mean with opposite-sign tail — classic precipitation pattern)*
2. If `|Mean-Tail Ratio| < 0.3`: **LOW** (weak linkage)
3. If `Model IQR > 2 * |Mean SCVR|`: **LOW** (model disagreement exceeds signal)
4. If `Mean-Tail Ratio > 0.6`: **HIGH** (mean and tail agree)
5. Otherwise: **MODERATE**

**Why this matters:** Mean-based SCVR is mathematically correct but can be *financially misleading*.
Example: precipitation SCVR ~ -0.1% says "no change" but P95 SCVR = +1.9% and CVaR = +2.4%
— tails ARE fattening. The pipeline handles this via Pathway B (direct hazard counting from daily data),
but without companion metrics, a reviewer cannot see this from the report alone.
""")

        # ── Section 2: Per-Model SCVR Distribution (Box Plot) ────────────────
        st.subheader("Per-Model SCVR Distribution",
                     help="Each box shows the spread of SCVR values across individual "
                          "climate models. Diamond markers = pooled ensemble SCVR. "
                          "Wide boxes = models disagree on the climate signal.")
        box_rows = []
        ensemble_markers = []
        for c in companions:
            per_model = c.get("per_model_scvr", {})
            for model, scvr_val in per_model.items():
                box_rows.append({
                    "Variable": var_label(c["variable"]),
                    "Scenario": scen_label(c["scenario"]),
                    "var_scen": f"{var_label(c['variable'])} ({scen_label(c['scenario'])})",
                    "Model": model,
                    "SCVR": scvr_val,
                })
            ensemble_markers.append({
                "var_scen": f"{var_label(c['variable'])} ({scen_label(c['scenario'])})",
                "SCVR": c["mean_scvr"],
            })

        if box_rows:
            df_box = pd.DataFrame(box_rows)
            fig_box = px.box(
                df_box, x="var_scen", y="SCVR", color="Scenario",
                color_discrete_map={
                    scen_label(k): v for k, v in SCENARIO_COLORS.items()
                },
                template=PLOTLY_TEMPLATE,
                labels={"var_scen": "", "SCVR": "SCVR"},
            )
            # Overlay ensemble (pooled) SCVR as diamond markers
            df_ens = pd.DataFrame(ensemble_markers)
            fig_box.add_trace(go.Scatter(
                x=df_ens["var_scen"], y=df_ens["SCVR"],
                mode="markers", name="Pooled SCVR",
                marker=dict(symbol="diamond", size=12, color="black",
                            line=dict(width=2, color="white")),
            ))
            fig_box.update_layout(
                height=450,
                xaxis_tickangle=-30,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_box, use_container_width=True)

        # ── Section 3: Mean vs Tail Scatter ──────────────────────────────────
        st.subheader("Mean SCVR vs P95 SCVR",
                     help="Scatter plot comparing mean-based SCVR (x-axis) against "
                          "tail-based P95 SCVR (y-axis). Points on the dashed diagonal = "
                          "perfect agreement. Points above = tail shifting more than mean "
                          "(SCVR understates risk). Points in different quadrants = DIVERGENT.")
        scatter_rows = []
        for c in companions:
            if c.get("mean_scvr") is not None and c.get("tail_scvr_p95") is not None:
                scatter_rows.append({
                    "Variable": var_label(c["variable"]),
                    "Scenario": scen_label(c["scenario"]),
                    "Mean SCVR": c["mean_scvr"],
                    "P95 SCVR": c["tail_scvr_p95"],
                    "Tail Confidence": c.get("tail_confidence", "N/A"),
                })
        if scatter_rows:
            df_scatter = pd.DataFrame(scatter_rows)
            fig_scatter = px.scatter(
                df_scatter, x="Mean SCVR", y="P95 SCVR",
                color="Variable", symbol="Scenario",
                hover_data=["Tail Confidence"],
                template=PLOTLY_TEMPLATE,
            )
            # Add y=x reference line
            all_vals = list(df_scatter["Mean SCVR"]) + list(df_scatter["P95 SCVR"])
            lo, hi = min(all_vals), max(all_vals)
            pad = (hi - lo) * 0.1 or 0.01
            fig_scatter.add_shape(
                type="line", x0=lo - pad, y0=lo - pad, x1=hi + pad, y1=hi + pad,
                line=dict(dash="dash", color="grey", width=1),
            )
            fig_scatter.update_layout(height=450)
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption(
                "Points on the dashed line: mean and tail agree. "
                "Points above the line: tail shifting more than mean (SCVR understates risk). "
                "Points below: mean overstates tail shift."
            )

        # ── Section 4: Variable Classification Cards ─────────────────────────
        st.subheader("Variable Classification",
                     help="Per-variable verdict based on Tail Confidence. "
                          "GREEN/HIGH = SCVR alone is reliable. "
                          "AMBER/MODERATE = check tail metrics. "
                          "RED/DIVERGENT = SCVR misleading, Pathway B handles this.")
        # Variable-specific processing notes
        _VAR_NOTES = {
            "pr": "† SCVR unreliable (mean metric). P95/CVaR on wet days only. Uses Pathway B for hazard counting.",
            "sfcWind": "R² ~ 0.13 — decade-level SCVR only, no annual interpolation.",
        }
        for c in companions:
            label = f"**{var_label(c['variable'])}** ({scen_label(c['scenario'])})"
            tc = c.get("tail_confidence", "N/A")
            mean_s = c.get("mean_scvr")
            p95_s = c.get("tail_scvr_p95")
            mean_fmt = f"{mean_s:.6f}" if mean_s is not None else "—"
            p95_fmt = f"{p95_s:.6f}" if p95_s is not None else "—"
            msg = f"{label} — Mean SCVR: {mean_fmt}, P95 SCVR: {p95_fmt}"
            note = _VAR_NOTES.get(c["variable"], "")
            if note:
                msg += f" | *{note}*"

            if tc == "HIGH":
                st.success(f"{msg} | **{tc}**: SCVR is reliable for this variable.")
            elif tc == "MODERATE":
                st.warning(f"{msg} | **{tc}**: SCVR adequate, but check tail metrics.")
            elif tc == "LOW":
                st.warning(f"{msg} | **{tc}**: Weak mean-tail linkage or high model disagreement.")
            elif tc == "DIVERGENT":
                st.error(
                    f"{msg} | **{tc}**: Mean and tail point opposite directions. "
                    "SCVR misleading — Pathway B required for hazard counting."
                )
            else:
                st.info(f"{msg} | **{tc}**")


# ══════════════════════════════════════════════════════════════════════════════
# Tab 2: Decade Progression
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    dec = filt(data["decade"])
    if dec.empty:
        st.info("No decade data for current filters.")
    else:
        st.subheader("SCVR by Decade")
        dec_plot = dec.copy()
        dec_plot["var_label"] = dec_plot["variable"].map(var_label)
        dec_plot["scen_label"] = dec_plot["scenario"].map(scen_label)

        fig_dec = px.bar(
            dec_plot,
            x="decade",
            y="scvr",
            color="scen_label",
            facet_col="var_label",
            facet_col_wrap=3,
            barmode="group",
            color_discrete_map={
                scen_label(s): c for s, c in SCENARIO_COLORS.items()
            },
            labels={"decade": "Decade", "scvr": "SCVR", "scen_label": "Scenario"},
            template=PLOTLY_TEMPLATE,
        )
        fig_dec.update_layout(height=350 * ((len(selected_variables) + 2) // 3), margin=dict(t=40))
        fig_dec.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig_dec, use_container_width=True)

        # Sparklines — slope of SCVR across decades
        st.subheader("Decade-to-Decade Acceleration")
        n_vars = len(selected_variables)
        ncols = min(3, n_vars)
        nrows = (n_vars + ncols - 1) // ncols
        fig_spark = make_subplots(
            rows=nrows, cols=ncols,
            subplot_titles=[var_label(v) for v in selected_variables],
            vertical_spacing=0.12,
            horizontal_spacing=0.08,
        )
        for i, v in enumerate(selected_variables):
            row = i // ncols + 1
            col = i % ncols + 1
            v_dec = dec[dec["variable"] == v]
            for scen in selected_scenarios:
                s_dec = v_dec[v_dec["scenario"] == scen].sort_values("decade")
                if s_dec.empty:
                    continue
                mids = s_dec["decade"].apply(
                    lambda d: (int(d.split("-")[0]) + int(d.split("-")[1])) / 2
                )
                fig_spark.add_trace(
                    go.Scatter(
                        x=mids, y=s_dec["scvr"],
                        mode="lines+markers",
                        name=scen_label(scen),
                        line=dict(color=SCENARIO_COLORS[scen]),
                        showlegend=(i == 0),
                    ),
                    row=row, col=col,
                )
        fig_spark.update_layout(
            template=PLOTLY_TEMPLATE,
            height=250 * nrows,
            margin=dict(t=40),
        )
        st.plotly_chart(fig_spark, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 3: Annual Trajectory
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    ann = filt(data["annual"])
    if ann.empty:
        st.info("No annual data for current filters.")
    else:
        st.subheader("Annual SCVR Trajectory")
        ann_plot = ann.copy()
        ann_plot["var_label"] = ann_plot["variable"].map(var_label)
        ann_plot["scen_label"] = ann_plot["scenario"].map(scen_label)

        fig_ann = px.line(
            ann_plot,
            x="year",
            y="scvr",
            color="scen_label",
            facet_col="var_label",
            facet_col_wrap=3,
            markers=True,
            color_discrete_map={
                scen_label(s): c for s, c in SCENARIO_COLORS.items()
            },
            labels={"year": "Year", "scvr": "SCVR", "scen_label": "Scenario"},
            template=PLOTLY_TEMPLATE,
        )
        fig_ann.update_layout(
            height=350 * ((len(selected_variables) + 2) // 3),
            margin=dict(t=40),
        )
        fig_ann.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig_ann, use_container_width=True)

        # Anchor fit details
        anchor_fits = data["anchor_fits"]
        fitted_vars = [v for v in selected_variables if v in anchor_fits]
        if fitted_vars:
            st.subheader("Anchor Fit Details")
            fit_rows = []
            for v in fitted_vars:
                for scen, fit in anchor_fits[v].items():
                    if scen not in selected_scenarios:
                        continue
                    fit_rows.append({
                        "Variable": var_label(v),
                        "Scenario": scen_label(scen),
                        "Slope": f"{fit['slope']:.6f}",
                        "Intercept": f"{fit['intercept']:.4f}",
                        "R²": f"{fit['r2']:.4f}",
                        "Anchors": " → ".join(f"{s:.4f}" for s in fit["scvrs"]),
                    })
            if fit_rows:
                st.dataframe(pd.DataFrame(fit_rows), use_container_width=True, hide_index=True)

        # Detail view for one variable
        st.subheader("Detail View")
        detail_var = st.selectbox(
            "Variable", selected_variables, format_func=var_label, key="ann_detail"
        )
        detail = ann[ann["variable"] == detail_var]
        fig_detail = go.Figure()
        for scen in selected_scenarios:
            s_data = detail[detail["scenario"] == scen].sort_values("year")
            if s_data.empty:
                continue
            fig_detail.add_trace(go.Scatter(
                x=s_data["year"], y=s_data["scvr"],
                mode="lines+markers",
                name=scen_label(scen),
                line=dict(color=SCENARIO_COLORS[scen], width=2),
                marker=dict(size=5),
            ))
            # Overlay anchor fit line if available
            if detail_var in anchor_fits and scen in anchor_fits[detail_var]:
                fit = anchor_fits[detail_var][scen]
                x_fit = np.array([s_data["year"].min(), s_data["year"].max()])
                y_fit = fit["slope"] * x_fit + fit["intercept"]
                fig_detail.add_trace(go.Scatter(
                    x=x_fit, y=y_fit,
                    mode="lines",
                    name=f"{scen_label(scen)} fit (R²={fit['r2']:.3f})",
                    line=dict(color=SCENARIO_COLORS[scen], dash="dash", width=1),
                ))
        fig_detail.update_layout(
            template=PLOTLY_TEMPLATE,
            xaxis_title="Year",
            yaxis_title="SCVR",
            height=400,
            margin=dict(t=20),
        )
        fig_detail.add_hline(y=0.05, line_dash="dot", line_color="#aaa")
        fig_detail.add_hline(y=0.10, line_dash="dot", line_color="#aaa")
        method = detail["method"].dropna().iloc[0] if not detail["method"].dropna().empty else "unknown"
        st.caption(f"Method: `{method}`")
        st.plotly_chart(fig_detail, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 4: Distribution Shape
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    shape = data["shape"]
    shape_f = shape[shape["variable"].isin(selected_variables)].copy()
    # Keep baseline + selected scenarios
    shape_f = shape_f[
        (shape_f["scenario"] == "baseline") | shape_f["scenario"].isin(selected_scenarios)
    ]

    if shape_f.empty:
        st.info("No shape metrics for current filters.")
    else:
        # Percentile range chart
        st.subheader("Percentile Ranges: Baseline vs Future")
        detail_var_shape = st.selectbox(
            "Variable", selected_variables, format_func=var_label, key="shape_var"
        )
        sv = shape_f[shape_f["variable"] == detail_var_shape].copy()
        sv["label"] = sv.apply(
            lambda r: "Baseline" if r["scenario"] == "baseline"
            else f"{scen_label(r['scenario'])} {r['period']}",
            axis=1,
        )

        fig_box = go.Figure()
        for _, row in sv.iterrows():
            label = row["label"]
            color = (
                "#95a5a6" if row["scenario"] == "baseline"
                else SCENARIO_COLORS.get(row["scenario"], "#999")
            )
            fig_box.add_trace(go.Bar(
                name=label,
                x=[label],
                y=[row["p90"] - row["p10"]],
                base=row["p10"],
                marker_color=color,
                opacity=0.3,
                showlegend=False,
            ))
            fig_box.add_trace(go.Bar(
                name=label,
                x=[label],
                y=[row["p75"] - row["p25"]],
                base=row["p25"],
                marker_color=color,
                opacity=0.7,
                showlegend=False,
            ))
            # Median line
            fig_box.add_trace(go.Scatter(
                x=[label], y=[row["p50"]],
                mode="markers",
                marker=dict(symbol="line-ew-open", size=20, color="black", line_width=2),
                showlegend=False,
            ))

        fig_box.update_layout(
            template=PLOTLY_TEMPLATE,
            barmode="overlay",
            yaxis_title=var_label(detail_var_shape),
            height=400,
            margin=dict(t=20),
        )
        st.plotly_chart(fig_box, use_container_width=True)
        st.caption("Outer bar: P10–P90 | Inner bar: P25–P75 | Marker: P50 (median)")

        # Radar chart: baseline vs final decade
        st.subheader("Shape Comparison: Baseline vs Final Decade")
        radar_metrics = ["cv", "skewness", "kurtosis", "std"]
        available_metrics = [m for m in radar_metrics if m in sv.columns and sv[m].notna().any()]

        if available_metrics and len(sv) >= 2:
            baseline_row = sv[sv["scenario"] == "baseline"].iloc[0] if len(sv[sv["scenario"] == "baseline"]) > 0 else None
            final_rows = sv[sv["period"].str.startswith("204") | sv["period"].str.startswith("205")]

            if baseline_row is not None and len(final_rows) > 0:
                fig_radar = go.Figure()
                # Baseline
                vals_b = [abs(float(baseline_row[m])) for m in available_metrics]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals_b + [vals_b[0]],
                    theta=available_metrics + [available_metrics[0]],
                    name="Baseline",
                    line=dict(color="#95a5a6"),
                    fill="toself",
                    opacity=0.5,
                ))
                for _, frow in final_rows.iterrows():
                    vals_f = [abs(float(frow[m])) for m in available_metrics]
                    fig_radar.add_trace(go.Scatterpolar(
                        r=vals_f + [vals_f[0]],
                        theta=available_metrics + [available_metrics[0]],
                        name=f"{scen_label(frow['scenario'])} {frow['period']}",
                        line=dict(color=SCENARIO_COLORS.get(frow["scenario"], "#999")),
                        fill="toself",
                        opacity=0.3,
                    ))
                fig_radar.update_layout(
                    template=PLOTLY_TEMPLATE,
                    polar=dict(radialaxis=dict(visible=True)),
                    height=400,
                    margin=dict(t=20),
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        # Delta table
        st.subheader("Change from Baseline")
        baseline_metrics = sv[sv["scenario"] == "baseline"]
        if len(baseline_metrics) > 0:
            brow = baseline_metrics.iloc[0]
            delta_rows = []
            future = sv[sv["scenario"] != "baseline"]
            for _, row in future.iterrows():
                delta_rows.append({
                    "Period": f"{scen_label(row['scenario'])} {row['period']}",
                    "Mean Δ": f"{row['mean'] - brow['mean']:+.3f}",
                    "Std Δ": f"{row['std'] - brow['std']:+.3f}",
                    "P95 Δ": f"{row['p95'] - brow['p95']:+.3f}",
                    "P99 Δ": f"{row['p99'] - brow['p99']:+.3f}",
                    "Skewness Δ": f"{(row.get('skewness', 0) or 0) - (brow.get('skewness', 0) or 0):+.4f}",
                    "Kurtosis Δ": f"{(row.get('kurtosis', 0) or 0) - (brow.get('kurtosis', 0) or 0):+.4f}",
                })
            if delta_rows:
                st.dataframe(pd.DataFrame(delta_rows), use_container_width=True, hide_index=True)

        # Precipitation caveat
        if "pr" in selected_variables:
            st.info(
                "**Precipitation note:** Percentiles shown here include **all days** "
                "(~78% dry at arid sites). The Report Card tab's P95 SCVR uses "
                "**wet-day filtering** (> 0.1 mm) for meaningful tail comparison. "
                "See Methodology > Data Processing for details."
            )


# ══════════════════════════════════════════════════════════════════════════════
# Tab 5: Extreme Value Fits
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    gev_fits = data["gev_fits"]
    gpd_fits = data["gpd_fits"]

    if not gev_fits and not gpd_fits:
        st.info("No extreme value fits available (requires scipy).")
    else:
        # GEV table
        if gev_fits:
            st.subheader("GEV Fits (Block Maxima)")
            gev_rows = []
            for key, fit in gev_fits.items():
                parts = key.split("_", 1)
                scen = parts[0]
                var = parts[1] if len(parts) > 1 else key
                if var not in selected_variables:
                    continue
                if scen not in ["baseline"] and scen not in selected_scenarios:
                    continue
                gev_rows.append({
                    "Variable": var_label(var),
                    "Scenario": "Baseline" if scen == "baseline" else scen_label(scen),
                    "Shape (ξ)": f"{fit['shape']:.4f}",
                    "Location (μ)": f"{fit['loc']:.3f}",
                    "Scale (σ)": f"{fit['scale']:.3f}",
                    "Blocks": fit["n_blocks"],
                    "KS Stat": f"{fit['ks_statistic']:.4f}",
                    "KS p-value": f"{fit['ks_pvalue']:.4f}",
                    "_pval": fit["ks_pvalue"],
                })
            if gev_rows:
                gev_df = pd.DataFrame(gev_rows)
                st.dataframe(
                    gev_df.drop(columns=["_pval"]).style.apply(
                        lambda row: [
                            "" if col != "KS p-value"
                            else f"background-color: {'#d5f5e3' if gev_df.iloc[row.name]['_pval'] > 0.05 else '#fadbd8'}"
                            for col in row.index
                        ],
                        axis=1,
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption("Green p-value: good fit (p > 0.05). Red: poor fit.")

        # GPD table
        if gpd_fits:
            st.subheader("GPD Fits (Peaks Over Threshold)")
            gpd_rows = []
            for key, fit in gpd_fits.items():
                parts = key.split("_", 1)
                scen = parts[0]
                var = parts[1] if len(parts) > 1 else key
                if var not in selected_variables:
                    continue
                if scen not in ["baseline"] and scen not in selected_scenarios:
                    continue
                gpd_rows.append({
                    "Variable": var_label(var),
                    "Scenario": "Baseline" if scen == "baseline" else scen_label(scen),
                    "Shape (ξ)": f"{fit['shape']:.4f}",
                    "Scale (σ)": f"{fit['scale']:.3f}",
                    "Threshold": f"{fit['threshold']:.3f}",
                    "Exceedances": fit["n_exceedances"],
                    "Exc. Rate": f"{fit['exceedance_rate']:.4f}",
                    "KS p-value": f"{fit['ks_pvalue']:.4f}",
                    "_pval": fit["ks_pvalue"],
                })
            if gpd_rows:
                gpd_df = pd.DataFrame(gpd_rows)
                st.dataframe(
                    gpd_df.drop(columns=["_pval"]).style.apply(
                        lambda row: [
                            "" if col != "KS p-value"
                            else f"background-color: {'#d5f5e3' if gpd_df.iloc[row.name]['_pval'] > 0.05 else '#fadbd8'}"
                            for col in row.index
                        ],
                        axis=1,
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

        # Parameter shift chart
        st.subheader("GEV Parameter Shift")
        detail_var_ev = st.selectbox(
            "Variable", selected_variables, format_func=var_label, key="ev_var"
        )
        params = ["Shape (ξ)", "Location (μ)", "Scale (σ)"]
        scenarios_ordered = ["baseline"] + [s for s in selected_scenarios]
        shift_data = []
        for scen in scenarios_ordered:
            key = f"{scen}_{detail_var_ev}"
            fit = gev_fits.get(key)
            if fit:
                shift_data.append({
                    "Scenario": "Baseline" if scen == "baseline" else scen_label(scen),
                    "Shape (ξ)": fit["shape"],
                    "Location (μ)": fit["loc"],
                    "Scale (σ)": fit["scale"],
                })
        if shift_data:
            shift_df = pd.DataFrame(shift_data)
            fig_shift = make_subplots(
                rows=1, cols=3,
                subplot_titles=params,
            )
            colors = ["#95a5a6"] + [SCENARIO_COLORS.get(s, "#999") for s in selected_scenarios]
            for j, param in enumerate(params):
                fig_shift.add_trace(
                    go.Bar(
                        x=shift_df["Scenario"],
                        y=shift_df[param],
                        marker_color=colors[:len(shift_df)],
                        showlegend=False,
                    ),
                    row=1, col=j + 1,
                )
            fig_shift.update_layout(
                template=PLOTLY_TEMPLATE,
                height=350,
                margin=dict(t=40),
            )
            st.plotly_chart(fig_shift, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 6: Methodology
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.header("SCVR Methodology Reference")
    st.caption("Sourced from project documentation — learning guides and discussion papers.")

    with st.expander("What is SCVR?", expanded=True):
        st.markdown(METHODOLOGY_WHAT)

    with st.expander("How is it Computed?"):
        st.markdown(METHODOLOGY_HOW)

    with st.expander("SCVR = Mean Ratio (Equivalence Proof)"):
        st.markdown(METHODOLOGY_EQUIVALENCE)

    with st.expander("Variable-Specific Strategy"):
        st.markdown(METHODOLOGY_STRATEGY)

    with st.expander("Interpretation Guide & Companion Metrics"):
        st.markdown(METHODOLOGY_INTERPRET)

    with st.expander("Downstream Pipeline (SCVR → HCR → EFR → NAV)"):
        st.markdown(METHODOLOGY_PIPELINE)

    with st.expander("Data Processing & Variable Notes"):
        st.markdown(METHODOLOGY_PROCESSING)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 7: Raw Report
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.header("Full SCVR Report")
    report = data["report"]

    # Summary table
    summary_rows = [
        {"Section": "ensemble_scvr", "Count": len(report.get("ensemble_scvr", [])), "Type": "rows"},
        {"Section": "decade_scvr", "Count": len(report.get("decade_scvr", [])), "Type": "rows"},
        {"Section": "annual_scvr", "Count": len(report.get("annual_scvr", [])), "Type": "rows"},
        {"Section": "shape_metrics", "Count": len(report.get("shape_metrics", [])), "Type": "rows"},
        {"Section": "gev_fits", "Count": len(report.get("gev_fits", {})), "Type": "keys"},
        {"Section": "gpd_fits", "Count": len(report.get("gpd_fits", {})), "Type": "keys"},
        {"Section": "anchor_fits", "Count": len(report.get("anchor_fits", {})), "Type": "variables"},
        {"Section": "models", "Count": len(report.get("models", {})), "Type": "variables"},
    ]
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    # Download button
    report_json = json.dumps(report, indent=2, default=str)
    st.download_button(
        label="Download scvr_report.json",
        data=report_json,
        file_name=f"scvr_report_{selected_site}.json",
        mime="application/json",
    )

    # Interactive JSON tree
    st.subheader("JSON Contents")
    st.json(report, expanded=1)


# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    f"Data: `{OUTPUT_DIR / selected_site}/scvr_report.json` | "
    f"Generated: {data['report'].get('timestamp', 'unknown')} | "
    f"Computation: {config.get('computation_time_s', '?')}s"
)
