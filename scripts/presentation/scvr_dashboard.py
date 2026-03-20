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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Summary", "Decade Progression", "Annual Trajectory",
    "Distribution Shape", "Extreme Value Fits",
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


# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    f"Data: `{OUTPUT_DIR / selected_site}/scvr_report.json` | "
    f"Generated: {data['report'].get('timestamp', 'unknown')} | "
    f"Computation: {config.get('computation_time_s', '?')}s"
)
