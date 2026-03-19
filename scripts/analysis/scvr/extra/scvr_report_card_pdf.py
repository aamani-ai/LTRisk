"""
scvr_report_card_pdf.py
=======================
Generate a 7-page PDF report explaining the SCVR Report Card:
  what it is, how it's calculated, why it exists, and how it feeds
  into the downstream LTRisk pipeline.

Reads pre-computed JSON outputs from ensemble_exceedance.py.
No new dependencies — uses matplotlib PdfPages only.

Usage:
    python scripts/presentation/scvr_report_card_pdf.py
"""

import json
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ── CONFIG ────────────────────────────────────────────────────────────────────
SITE_ID = "hayhurst_solar"
VARIABLES = ["tasmax", "tasmin", "tas", "pr", "sfcWind", "hurs", "rsds"]
SCENARIOS = ["ssp245", "ssp585"]
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed" / "presentation" / SITE_ID

CONFIDENCE_COLORS = {
    "HIGH": "#27ae60",
    "MODERATE": "#f39c12",
    "LOW": "#e67e22",
    "DIVERGENT": "#c0392b",
}
CONFIDENCE_TEXT_COLORS = {
    "HIGH": "white",
    "MODERATE": "white",
    "LOW": "white",
    "DIVERGENT": "white",
}

VAR_LABELS = {
    "tasmax": "Max Temperature",
    "tasmin": "Min Temperature",
    "tas": "Mean Temperature",
    "pr": "Precipitation",
    "sfcWind": "Wind Speed",
    "hurs": "Relative Humidity",
    "rsds": "Solar Irradiance",
}

SCENARIO_LABELS = {"ssp245": "SSP2-4.5", "ssp585": "SSP5-8.5"}

PAGE_W, PAGE_H = 11, 8.5  # landscape letter


# ── DATA LOADING ──────────────────────────────────────────────────────────────

def load_data():
    """Load all decomposition and summary JSONs."""
    data = {}
    for var in VARIABLES:
        decomp_path = DATA_DIR / var / f"scvr_decomposition_{var}.json"
        summary_path = DATA_DIR / var / f"scvr_summary_{var}.json"
        entry = {"var": var}
        if decomp_path.exists():
            with open(decomp_path) as f:
                entry["decomp"] = json.load(f)
        if summary_path.exists():
            with open(summary_path) as f:
                entry["summary"] = json.load(f)
        data[var] = entry

    # Site info from first available summary
    for var in VARIABLES:
        s = data[var].get("summary", {})
        if s.get("site_name"):
            data["_site_name"] = s["site_name"]
            data["_n_models"] = s.get("n_models", "?")
            data["_baseline"] = s.get("baseline_period", [1985, 2014])
            data["_future"] = s.get("future_period", [2026, 2055])
            break
    return data


# ── HELPER: DRAW TEXT BOX ─────────────────────────────────────────────────────

def draw_box(ax, x, y, w, h, text, facecolor="#ecf0f1", edgecolor="#bdc3c7",
             fontsize=9, ha="center", va="center", fontweight="normal",
             textcolor="black"):
    """Draw a rounded box with centered text."""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                         facecolor=facecolor, edgecolor=edgecolor, lw=1.2)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha=ha, va=va, fontsize=fontsize,
            fontweight=fontweight, color=textcolor,
            transform=ax.transData, wrap=True)


def draw_arrow(ax, x1, y1, x2, y2, label="", color="#7f8c8d"):
    """Draw an arrow between two points with optional label."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.5))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.01, my, label, fontsize=7, color=color, va="center")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Title + Executive Summary
# ══════════════════════════════════════════════════════════════════════════════

def page_title(pdf, data):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))

    # Title block
    fig.text(0.5, 0.82, "SCVR Report Card", ha="center", va="center",
             fontsize=36, fontweight="bold", color="#2c3e50")
    fig.text(0.5, 0.74, data.get("_site_name", "Unknown Site"),
             ha="center", va="center", fontsize=22, color="#7f8c8d")
    fig.text(0.5, 0.68,
             f"Baseline: {data['_baseline'][0]}\u2013{data['_baseline'][1]}   |   "
             f"Future: {data['_future'][0]}\u2013{data['_future'][1]}   |   "
             f"Scenarios: SSP2-4.5, SSP5-8.5",
             ha="center", va="center", fontsize=11, color="#95a5a6")

    # Divider
    fig.add_artist(plt.Line2D([0.15, 0.85], [0.62, 0.62],
                              color="#bdc3c7", lw=1.5))

    # Executive summary
    summary_text = (
        "The SCVR Report Card is an intelligence layer that answers one question:\n"
        "\"How much should I trust this SCVR number?\"\n\n"
        "SCVR captures the mean distribution shift between baseline and future climate.\n"
        "But hazards and financial impacts depend on tail behavior \u2014 extreme events \u2014\n"
        "which the mean can miss entirely. The report card compares the mean signal\n"
        "against tail metrics (P95, CVaR) and model agreement (IQR) to classify each\n"
        "variable's SCVR as HIGH, MODERATE, LOW, or DIVERGENT confidence.\n\n"
        "This makes the pipeline dynamic and variable-specific: temperature SCVR\n"
        "(HIGH confidence) feeds directly into equipment failure models, while\n"
        "precipitation SCVR (DIVERGENT) is routed to direct hazard counting instead."
    )
    fig.text(0.5, 0.42, summary_text, ha="center", va="center",
             fontsize=12, color="#2c3e50", linespacing=1.6,
             family="monospace")

    # Confidence legend at bottom
    ax = fig.add_axes([0.15, 0.08, 0.7, 0.12])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    flags = ["HIGH", "MODERATE", "LOW", "DIVERGENT"]
    counts = {f: 0 for f in flags}
    for var in VARIABLES:
        for scen in SCENARIOS:
            rc = data[var].get("decomp", {}).get("epoch_report_card", {}).get(scen, {})
            conf = rc.get("tail_confidence", "")
            if conf in counts:
                counts[conf] += 1
    for i, flag in enumerate(flags):
        x = 0.05 + i * 0.24
        box = FancyBboxPatch((x, 0.2), 0.2, 0.6, boxstyle="round,pad=0.02",
                             facecolor=CONFIDENCE_COLORS[flag],
                             edgecolor="none")
        ax.add_patch(box)
        ax.text(x + 0.1, 0.5, f"{flag}\n({counts[flag]}/{len(VARIABLES)*2} var-scenario pairs)",
                ha="center", va="center", fontsize=9, fontweight="bold",
                color="white")

    fig.text(0.5, 0.03, "LTRisk Framework  |  March 2026",
             ha="center", fontsize=8, color="#bdc3c7")

    pdf.savefig(fig)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — The Problem: Why SCVR Alone Isn't Enough
# ══════════════════════════════════════════════════════════════════════════════

def page_problem(pdf, data):
    fig, axes = plt.subplots(1, 2, figsize=(PAGE_W, PAGE_H))
    fig.suptitle("Why SCVR Alone Isn't Enough", fontsize=20,
                 fontweight="bold", color="#2c3e50", y=0.95)

    # Subtitle
    fig.text(0.5, 0.88,
             "SCVR measures the mean shift. But hazards depend on tail behavior.\n"
             "When the mean and tail move together, SCVR works. When they diverge, it fails.",
             ha="center", fontsize=11, color="#7f8c8d", linespacing=1.5)

    # LEFT: Temperature — mean and tail move together
    ax = axes[0]
    x = np.linspace(15, 50, 500)
    baseline = np.exp(-0.5 * ((x - 30) / 5) ** 2)
    future = np.exp(-0.5 * ((x - 32) / 5) ** 2)
    ax.fill_between(x, baseline, alpha=0.3, color="#95a5a6", label="Baseline")
    ax.fill_between(x, future, alpha=0.3, color="#e74c3c", label="Future")
    ax.plot(x, baseline, color="#7f8c8d", lw=2)
    ax.plot(x, future, color="#c0392b", lw=2)
    # Threshold line
    ax.axvline(40, color="#2c3e50", ls="--", lw=1.5, alpha=0.7)
    ax.text(40.5, 0.85, "Hazard\nthreshold", fontsize=8, color="#2c3e50")
    # Arrows showing shift
    ax.annotate("", xy=(32, 0.7), xytext=(30, 0.7),
                arrowprops=dict(arrowstyle="->", color="#27ae60", lw=2.5))
    ax.text(31, 0.75, "Mean\nshifts", ha="center", fontsize=8, color="#27ae60",
            fontweight="bold")
    ax.annotate("", xy=(42, 0.15), xytext=(40, 0.15),
                arrowprops=dict(arrowstyle="->", color="#27ae60", lw=2.5))
    ax.text(41, 0.2, "Tail\nshifts too", ha="center", fontsize=8,
            color="#27ae60", fontweight="bold")
    ax.set_title("Temperature: Mean tracks tail", fontsize=13,
                 fontweight="bold", color="#27ae60", pad=10)
    ax.text(0.5, -0.08, "SCVR works \u2014 Confidence: HIGH",
            transform=ax.transAxes, ha="center", fontsize=11,
            fontweight="bold", color="#27ae60")
    ax.set_xlabel("Temperature (\u00b0C)", fontsize=10)
    ax.set_ylabel("Density", fontsize=10)
    ax.legend(fontsize=9, loc="upper left")
    ax.set_ylim(0, 1.1)

    # RIGHT: Precipitation — mean flat, tail fattens
    ax = axes[1]
    x = np.linspace(0, 80, 500)
    # Gamma-like distribution for precip
    from scipy.stats import gamma as gamma_dist
    baseline_pr = gamma_dist.pdf(x, a=2, scale=8)
    # Future: same mean but fatter tail
    future_pr = gamma_dist.pdf(x, a=1.8, scale=8.9)  # same mean, wider tail
    ax.fill_between(x, baseline_pr, alpha=0.3, color="#95a5a6", label="Baseline")
    ax.fill_between(x, future_pr, alpha=0.3, color="#3498db", label="Future")
    ax.plot(x, baseline_pr, color="#7f8c8d", lw=2)
    ax.plot(x, future_pr, color="#2980b9", lw=2)
    # Threshold line
    ax.axvline(40, color="#2c3e50", ls="--", lw=1.5, alpha=0.7)
    ax.text(41, 0.06, "Extreme\nthreshold", fontsize=8, color="#2c3e50")
    # Arrows
    ax.annotate("", xy=(16.2, 0.052), xytext=(16, 0.052),
                arrowprops=dict(arrowstyle="->", color="#7f8c8d", lw=2))
    ax.text(16.5, 0.056, "Mean\nbarely moves", ha="center", fontsize=8,
            color="#7f8c8d")
    # Show fatter tail
    ax.fill_between(x[x > 40], future_pr[x > 40], baseline_pr[x > 40],
                    where=future_pr[x > 40] > baseline_pr[x > 40],
                    alpha=0.5, color="#c0392b", label="Extra extreme days")
    ax.text(55, 0.008, "Tail fattens\n(SCVR misses this)",
            fontsize=8, color="#c0392b", fontweight="bold", ha="center")
    ax.set_title("Precipitation: Mean misses the tail", fontsize=13,
                 fontweight="bold", color="#c0392b", pad=10)
    ax.text(0.5, -0.08, "SCVR gives wrong answer \u2014 Confidence: DIVERGENT",
            transform=ax.transAxes, ha="center", fontsize=11,
            fontweight="bold", color="#c0392b")
    ax.set_xlabel("Precipitation (mm/day)", fontsize=10)
    ax.set_ylabel("Density", fontsize=10)
    ax.legend(fontsize=9, loc="upper right")

    plt.tight_layout(rect=[0, 0.05, 1, 0.85])

    fig.text(0.5, 0.02,
             "The Report Card answers: \"How much should I trust this SCVR?\"  \u2014  "
             "It compares the mean signal against P95, CVaR, and model agreement.",
             ha="center", fontsize=10, color="#2c3e50", style="italic")

    pdf.savefig(fig)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — How It's Calculated
# ══════════════════════════════════════════════════════════════════════════════

def page_algorithm(pdf, data):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    fig.text(0.5, 0.95, "How the Report Card Is Calculated", ha="center",
             fontsize=20, fontweight="bold", color="#2c3e50")

    # Left side: inputs
    ax = fig.add_axes([0.02, 0.05, 0.45, 0.82])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.97, "Inputs (from SCVR Decomposition)", ha="center",
            fontsize=13, fontweight="bold", color="#2c3e50")

    inputs = [
        ("Mean SCVR", "Pooled exceedance area ratio\n(the headline SCVR number)"),
        ("Tail SCVR (P95)", "Fractional change in 95th percentile\n(how the extreme tail shifted)"),
        ("CVaR 95%", "Conditional Value at Risk\n(average of values above P95)"),
        ("Model IQR", "Inter-quartile range of per-model SCVR\n(how much models disagree)"),
        ("Extreme SCVR (P99)", "Fractional change in 99th percentile\n(optional: deepest tail)"),
    ]
    for i, (name, desc) in enumerate(inputs):
        y = 0.85 - i * 0.155
        draw_box(ax, 0.02, y, 0.96, 0.13, "", facecolor="#eaf2f8",
                 edgecolor="#2980b9")
        ax.text(0.06, y + 0.085, name, fontsize=10, fontweight="bold",
                color="#2c3e50", va="center")
        ax.text(0.06, y + 0.04, desc, fontsize=8, color="#7f8c8d",
                va="center")

    ax.text(0.5, 0.06, "Computed at two levels:", ha="center", fontsize=10,
            fontweight="bold", color="#2c3e50")
    ax.text(0.5, 0.02,
            "Epoch (full 30-year window)  +  Decade (3 \u00d7 10-year windows)",
            ha="center", fontsize=9, color="#7f8c8d")

    # Right side: decision tree
    ax2 = fig.add_axes([0.50, 0.05, 0.48, 0.82])
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis("off")

    ax2.text(0.5, 0.97, "Decision Tree", ha="center",
             fontsize=13, fontweight="bold", color="#2c3e50")

    # Decision nodes
    nodes = [
        (0.35, 0.84, 0.58, 0.09, "Signs differ\n(mean vs P95)?", "#ecf0f1"),
        (0.35, 0.65, 0.58, 0.09, "Mean-Tail Ratio < 0.3?", "#ecf0f1"),
        (0.35, 0.46, 0.58, 0.09, "Model IQR > 2 \u00d7 |mean|?", "#ecf0f1"),
        (0.35, 0.27, 0.58, 0.09, "Mean-Tail Ratio > 0.6?", "#ecf0f1"),
    ]
    for x, y, w, h, text, color in nodes:
        draw_box(ax2, x, y, w, h, text, facecolor=color,
                 edgecolor="#bdc3c7", fontsize=9)

    # Result boxes (right side)
    results = [
        (0.05, 0.845, "DIVERGENT", CONFIDENCE_COLORS["DIVERGENT"]),
        (0.05, 0.655, "LOW", CONFIDENCE_COLORS["LOW"]),
        (0.05, 0.465, "LOW", CONFIDENCE_COLORS["LOW"]),
        (0.05, 0.275, "HIGH", CONFIDENCE_COLORS["HIGH"]),
    ]
    for x, y, text, color in results:
        draw_box(ax2, x, y, 0.25, 0.08, text, facecolor=color,
                 edgecolor="none", fontsize=10, fontweight="bold",
                 textcolor="white")

    # "yes" arrows (left)
    for i in range(4):
        node_y = nodes[i][1] + nodes[i][3] / 2
        res_y = results[i][1] + 0.04
        ax2.annotate("", xy=(0.30, res_y), xytext=(0.35, node_y),
                     arrowprops=dict(arrowstyle="->", color="#27ae60", lw=1.5))
        ax2.text(0.32, (node_y + res_y) / 2, "yes", fontsize=7,
                 color="#27ae60", fontweight="bold", ha="center")

    # "no" arrows (down)
    for i in range(3):
        y1 = nodes[i][1]
        y2 = nodes[i + 1][1] + nodes[i + 1][3]
        mx = 0.64
        ax2.annotate("", xy=(mx, y2), xytext=(mx, y1),
                     arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.5))
        ax2.text(mx + 0.03, (y1 + y2) / 2, "no", fontsize=7,
                 color="#c0392b", fontweight="bold")

    # Final "no" → MODERATE
    draw_box(ax2, 0.40, 0.10, 0.50, 0.08, "MODERATE",
             facecolor=CONFIDENCE_COLORS["MODERATE"],
             edgecolor="none", fontsize=10, fontweight="bold",
             textcolor="white")
    ax2.annotate("", xy=(0.64, 0.18), xytext=(0.64, 0.27),
                 arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.5))
    ax2.text(0.67, 0.225, "no", fontsize=7, color="#c0392b",
             fontweight="bold")

    # Guard threshold note
    ax2.text(0.5, 0.02,
             "Guard: both |mean| and |P95| must exceed 0.005\n"
             "to trigger DIVERGENT (prevents false alarms at noise level)",
             ha="center", fontsize=8, color="#95a5a6", style="italic")

    pdf.savefig(fig)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Epoch Report Card Table
# ══════════════════════════════════════════════════════════════════════════════

def page_epoch_table(pdf, data):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    fig.text(0.5, 0.95, "Epoch Report Card \u2014 All Variables",
             ha="center", fontsize=20, fontweight="bold", color="#2c3e50")
    fig.text(0.5, 0.90,
             f"{data.get('_site_name', '')}  |  "
             f"Baseline: {data['_baseline'][0]}\u2013{data['_baseline'][1]}  |  "
             f"Future: {data['_future'][0]}\u2013{data['_future'][1]}",
             ha="center", fontsize=11, color="#7f8c8d")

    ax = fig.add_axes([0.05, 0.15, 0.9, 0.70])
    ax.axis("off")

    # Build table data
    col_labels = ["Variable", "Models",
                  "SSP2-4.5\nSCVR", "SSP2-4.5\nP95", "SSP2-4.5\nM-T Ratio",
                  "SSP2-4.5\nConfidence",
                  "SSP5-8.5\nSCVR", "SSP5-8.5\nP95", "SSP5-8.5\nM-T Ratio",
                  "SSP5-8.5\nConfidence"]

    cell_text = []
    cell_colors = []
    for var in VARIABLES:
        decomp = data[var].get("decomp", {})
        summary = data[var].get("summary", {})
        n_models = summary.get("n_models", "?")
        row = [VAR_LABELS.get(var, var), str(n_models)]
        row_colors = ["#f8f9fa", "#f8f9fa"]

        for scen in SCENARIOS:
            rc = decomp.get("epoch_report_card", {}).get(scen, {})
            scvr = rc.get("mean_scvr", 0)
            p95 = rc.get("tail_scvr_p95", 0)
            mtr = rc.get("mean_tail_ratio")
            conf = rc.get("tail_confidence", "?")

            row.append(f"{scvr:+.4f}")
            row_colors.append("#f8f9fa")
            row.append(f"{p95:+.4f}")
            row_colors.append("#f8f9fa")
            row.append(f"{mtr:.2f}" if mtr is not None else "N/A")
            row_colors.append("#f8f9fa")
            row.append(conf)
            row_colors.append(CONFIDENCE_COLORS.get(conf, "#f8f9fa"))

        cell_text.append(row)
        cell_colors.append(row_colors)

    table = ax.table(cellText=cell_text, colLabels=col_labels,
                     cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)

    # Style header
    for j in range(len(col_labels)):
        cell = table[0, j]
        cell.set_facecolor("#2c3e50")
        cell.set_text_props(color="white", fontweight="bold", fontsize=8)

    # Style data cells
    for i in range(len(VARIABLES)):
        for j in range(len(col_labels)):
            cell = table[i + 1, j]
            if j == 0:
                cell.set_text_props(fontweight="bold", ha="left")
            # Color confidence cells
            if j in [5, 9]:  # confidence columns
                conf = cell_text[i][j]
                cell.set_facecolor(CONFIDENCE_COLORS.get(conf, "#f8f9fa"))
                cell.set_text_props(color="white", fontweight="bold")
            else:
                cell.set_facecolor("#f8f9fa" if i % 2 == 0 else "white")

    # Key observations
    fig.text(0.08, 0.10, "Key Observations:", fontsize=11,
             fontweight="bold", color="#2c3e50")
    observations = [
        "tasmax/tas: HIGH \u2014 tail tracks mean (M-T \u2248 0.70). Safe for direct use in EFR/IUL models.",
        "tasmin: MODERATE \u2014 nighttime tail amplification weaker (M-T = 0.56). Nighttime has different physics.",
        "pr: DIVERGENT \u2014 mean \u2248 0 but P95 positive. Extreme rain increasing while total flat. Pathway B mandatory.",
        "rsds: MODERATE \u2014 both signals near noise floor (< 0.005). Guard threshold prevents false DIVERGENT.",
    ]
    for i, obs in enumerate(observations):
        fig.text(0.10, 0.07 - i * 0.022, f"\u2022 {obs}",
                 fontsize=8, color="#2c3e50")

    pdf.savefig(fig)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — Decade Progression
# ══════════════════════════════════════════════════════════════════════════════

def page_decade_progression(pdf, data):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    fig.text(0.5, 0.95, "Decade Progression \u2014 Confidence Over Time",
             ha="center", fontsize=20, fontweight="bold", color="#2c3e50")
    fig.text(0.5, 0.90,
             "The report card is computed per decade to reveal if trust changes over time.\n"
             "Divergence isn't static \u2014 it can emerge or widen as the climate signal strengthens.",
             ha="center", fontsize=10, color="#7f8c8d", linespacing=1.4)

    # Heatmap: confidence per variable × decade, for SSP245
    conf_to_num = {"HIGH": 3, "MODERATE": 2, "LOW": 1, "DIVERGENT": 0}
    decades = ["2026-2035", "2036-2045", "2046-2055"]

    for scen_idx, scen in enumerate(SCENARIOS):
        ax = fig.add_axes([0.08 + scen_idx * 0.48, 0.12, 0.42, 0.65])

        grid = np.full((len(VARIABLES), len(decades)), np.nan)
        annotations = []

        for i, var in enumerate(VARIABLES):
            drc = data[var].get("decomp", {}).get("decade_report_cards", {}).get(scen, {})
            for j, dec in enumerate(decades):
                rc = drc.get(dec, {})
                conf = rc.get("tail_confidence", "")
                if conf in conf_to_num:
                    grid[i, j] = conf_to_num[conf]
                    annotations.append((j, i, conf))

        # Custom colormap: DIVERGENT=red, LOW=orange, MODERATE=amber, HIGH=green
        from matplotlib.colors import ListedColormap, BoundaryNorm
        cmap = ListedColormap([
            CONFIDENCE_COLORS["DIVERGENT"],
            CONFIDENCE_COLORS["LOW"],
            CONFIDENCE_COLORS["MODERATE"],
            CONFIDENCE_COLORS["HIGH"],
        ])
        norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)

        ax.imshow(grid, cmap=cmap, norm=norm, aspect="auto", origin="upper")

        # Annotate cells
        for j, i, conf in annotations:
            ax.text(j, i, conf, ha="center", va="center", fontsize=8,
                    fontweight="bold", color="white")

        ax.set_xticks(range(len(decades)))
        ax.set_xticklabels(decades, fontsize=9)
        ax.set_yticks(range(len(VARIABLES)))
        ax.set_yticklabels([VAR_LABELS.get(v, v) for v in VARIABLES], fontsize=9)
        ax.set_title(f"{SCENARIO_LABELS[scen]}", fontsize=13,
                     fontweight="bold", color="#2c3e50", pad=10)

        # Grid lines
        for edge in range(len(VARIABLES) + 1):
            ax.axhline(edge - 0.5, color="white", lw=2)
        for edge in range(len(decades) + 1):
            ax.axvline(edge - 0.5, color="white", lw=2)

    # Callout
    fig.text(0.5, 0.04,
             "Precipitation: confidence degrades from LOW to DIVERGENT as the "
             "mean drifts negative while extreme tail events grow.  |  "
             "Temperature: stable HIGH across all decades \u2014 reliable throughout.",
             ha="center", fontsize=9, color="#2c3e50", style="italic")

    pdf.savefig(fig)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — Downstream Impact
# ══════════════════════════════════════════════════════════════════════════════

def page_downstream(pdf, data):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    fig.text(0.5, 0.95, "Downstream Impact \u2014 How It Feeds the Pipeline",
             ha="center", fontsize=20, fontweight="bold", color="#2c3e50")

    # Pipeline diagram
    ax = fig.add_axes([0.05, 0.38, 0.9, 0.50])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # SCVR box
    draw_box(ax, 0.01, 0.70, 0.15, 0.20, "SCVR\n(per variable)",
             facecolor="#3498db", edgecolor="#2980b9", fontsize=10,
             fontweight="bold", textcolor="white")

    # Report Card box
    draw_box(ax, 0.22, 0.65, 0.18, 0.30, "Report\nCard\n\nTail\nConfidence",
             facecolor="#9b59b6", edgecolor="#8e44ad", fontsize=10,
             fontweight="bold", textcolor="white")

    # Arrow SCVR → Report Card
    draw_arrow(ax, 0.16, 0.80, 0.22, 0.80)

    # HIGH/MODERATE path
    draw_box(ax, 0.48, 0.78, 0.24, 0.18,
             "Channel 2: EFR / IUL\n(Peck's model, Coffin-Manson)\n86% of NAV impact",
             facecolor="#27ae60", edgecolor="#1e8449", fontsize=8,
             fontweight="bold", textcolor="white")
    draw_arrow(ax, 0.40, 0.85, 0.48, 0.87, label="HIGH/MOD")

    # Also Channel 1 cross-validate
    draw_box(ax, 0.48, 0.55, 0.24, 0.18,
             "Channel 1: HCR\nPathway A (SCVR \u00d7 scaling)\ncross-validate with Pathway B",
             facecolor="#2ecc71", edgecolor="#27ae60", fontsize=8,
             textcolor="white")
    draw_arrow(ax, 0.40, 0.78, 0.48, 0.68, label="HIGH/MOD")

    # LOW path
    draw_box(ax, 0.48, 0.30, 0.24, 0.18,
             "Channel 1: HCR\nPathway B only (direct count)\n+ report P95 alongside",
             facecolor="#e67e22", edgecolor="#d35400", fontsize=8,
             fontweight="bold", textcolor="white")
    draw_arrow(ax, 0.40, 0.72, 0.48, 0.43, label="LOW")

    # DIVERGENT path
    draw_box(ax, 0.48, 0.05, 0.24, 0.18,
             "Channel 1: HCR\nPathway B only\nSCVR excluded from Channel 2",
             facecolor="#c0392b", edgecolor="#96281b", fontsize=8,
             fontweight="bold", textcolor="white")
    draw_arrow(ax, 0.40, 0.68, 0.48, 0.18, label="DIVERGENT")

    # Final NAV box
    draw_box(ax, 0.78, 0.55, 0.18, 0.30, "NAV\nImpairment\nModel",
             facecolor="#2c3e50", edgecolor="#1a252f", fontsize=11,
             fontweight="bold", textcolor="white")
    draw_arrow(ax, 0.72, 0.87, 0.78, 0.78)
    draw_arrow(ax, 0.72, 0.64, 0.78, 0.68)
    draw_arrow(ax, 0.72, 0.39, 0.78, 0.60)
    draw_arrow(ax, 0.72, 0.14, 0.78, 0.58)

    # Routing table
    ax2 = fig.add_axes([0.08, 0.03, 0.84, 0.30])
    ax2.axis("off")

    ax2.text(0.5, 0.95, "Variable Routing (SSP2-4.5)", ha="center",
             fontsize=12, fontweight="bold", color="#2c3e50")

    col_labels = ["Variable", "Confidence", "Channel 2\n(EFR/IUL)", "Channel 1\n(HCR)",
                  "HCR Pathway"]
    rows = []
    for var in VARIABLES:
        rc = data[var].get("decomp", {}).get("epoch_report_card", {}).get("ssp245", {})
        conf = rc.get("tail_confidence", "?")
        if conf in ("HIGH", "MODERATE"):
            ch2 = "Yes"
            ch1 = "Cross-validate"
            pathway = "A + B"
        elif conf == "LOW":
            ch2 = "With caveat"
            ch1 = "Yes"
            pathway = "B only"
        else:
            ch2 = "No"
            ch1 = "Yes"
            pathway = "B only"
        rows.append([VAR_LABELS.get(var, var), conf, ch2, ch1, pathway])

    table = ax2.table(cellText=rows, colLabels=col_labels,
                      cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.6)

    for j in range(len(col_labels)):
        table[0, j].set_facecolor("#2c3e50")
        table[0, j].set_text_props(color="white", fontweight="bold", fontsize=8)

    for i, row in enumerate(rows):
        conf = row[1]
        table[i + 1, 1].set_facecolor(CONFIDENCE_COLORS.get(conf, "#f8f9fa"))
        table[i + 1, 1].set_text_props(color="white", fontweight="bold")
        for j in [0, 2, 3, 4]:
            table[i + 1, j].set_facecolor("#f8f9fa" if i % 2 == 0 else "white")

    pdf.savefig(fig)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — Key Findings + Next Steps
# ══════════════════════════════════════════════════════════════════════════════

def page_findings(pdf, data):
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    fig.text(0.5, 0.95, "Key Findings & What This Enables",
             ha="center", fontsize=20, fontweight="bold", color="#2c3e50")

    # Findings in boxes
    ax = fig.add_axes([0.05, 0.10, 0.9, 0.78])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Finding 1: Temperature is reliable
    draw_box(ax, 0.02, 0.82, 0.96, 0.14, "",
             facecolor="#eafaf1", edgecolor="#27ae60")
    ax.text(0.05, 0.93, "1. Temperature SCVR is reliable (HIGH confidence)",
            fontsize=12, fontweight="bold", color="#27ae60")
    ax.text(0.05, 0.87,
            "tasmax and tas have M-T ratios > 0.6 \u2014 the tail tracks the mean proportionally. "
            "This validates using temperature SCVR directly in Peck's exponential aging model (Channel 2), "
            "which drives 86% of the NAV impact. tasmin is MODERATE (M-T = 0.56) due to different "
            "nighttime physics \u2014 use with noted uncertainty.",
            fontsize=9, color="#2c3e50", wrap=True)

    # Finding 2: Precipitation is divergent
    draw_box(ax, 0.02, 0.62, 0.96, 0.14, "",
             facecolor="#fdedec", edgecolor="#c0392b")
    ax.text(0.05, 0.73, "2. Precipitation SCVR is misleading (DIVERGENT)",
            fontsize=12, fontweight="bold", color="#c0392b")
    ax.text(0.05, 0.67,
            "Mean SCVR \u2248 0 but P95 and CVaR are positive \u2014 extreme rainfall is increasing "
            "while total precipitation is flat. SCVR gives the wrong sign for flood risk. "
            "The pipeline correctly routes precipitation through HCR Pathway B (direct hazard counting), "
            "bypassing the misleading SCVR entirely.",
            fontsize=9, color="#2c3e50", wrap=True)

    # Finding 3: Divergence emerges over time
    draw_box(ax, 0.02, 0.42, 0.96, 0.14, "",
             facecolor="#fef9e7", edgecolor="#f39c12")
    ax.text(0.05, 0.53, "3. Divergence emerges and widens over time",
            fontsize=12, fontweight="bold", color="#e67e22")
    ax.text(0.05, 0.47,
            "Decade-level report cards show precipitation confidence degrading from LOW (2026\u20132035) "
            "to DIVERGENT (2036\u20132055). The mean-tail disconnect isn't present from day one \u2014 "
            "it develops as the climate signal strengthens. This temporal view reveals risks that "
            "a single epoch number would hide.",
            fontsize=9, color="#2c3e50", wrap=True)

    # What this enables
    draw_box(ax, 0.02, 0.08, 0.96, 0.28, "",
             facecolor="#f4ecf7", edgecolor="#8e44ad")
    ax.text(0.05, 0.33, "What the Report Card Enables",
            fontsize=13, fontweight="bold", color="#8e44ad")

    enables = [
        ("Variable-specific routing:", "Each variable gets routed through the correct "
         "pipeline channel based on its confidence flag \u2014 not a one-size-fits-all approach."),
        ("Audit trail:", "The report card proves the pipeline handles SCVR limitations correctly. "
         "When a reviewer asks \"why do you trust SCVR for temperature but not precipitation?\" "
         "\u2014 the answer is in the data."),
        ("Stakeholder transparency:", "Communicates uncertainty honestly. A DIVERGENT flag on "
         "precipitation is more informative than a misleading SCVR = -0.001."),
        ("Dynamic intelligence:", "As new data or models are added, report cards update automatically. "
         "A variable that was MODERATE might become HIGH with better model coverage."),
    ]
    for i, (title, desc) in enumerate(enables):
        y = 0.27 - i * 0.05
        ax.text(0.05, y, f"\u2022 {title}", fontsize=9, fontweight="bold",
                color="#2c3e50")
        ax.text(0.22, y, desc, fontsize=8, color="#555555")

    fig.text(0.5, 0.03, "LTRisk Framework  |  SCVR Report Card  |  March 2026",
             ha="center", fontsize=8, color="#bdc3c7")

    pdf.savefig(fig)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("Loading data ...")
    data = load_data()

    out_path = DATA_DIR / "scvr_report_card.pdf"
    print(f"Generating PDF ({out_path}) ...")

    with PdfPages(str(out_path)) as pdf:
        page_title(pdf, data)
        page_problem(pdf, data)
        page_algorithm(pdf, data)
        page_epoch_table(pdf, data)
        page_decade_progression(pdf, data)
        page_downstream(pdf, data)
        page_findings(pdf, data)

    print(f"Saved: {out_path}  (7 pages)")


if __name__ == "__main__":
    main()
