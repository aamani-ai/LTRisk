"""
Interactive Dashboard for Climate Risk Assessment Results

This module creates an interactive Dash dashboard to visualize:
- SCVR trends over time
- Asset performance under different scenarios
- Business interruption losses
- Equipment degradation curves
- NAV impairment with uncertainty bands
- Monte Carlo simulation results

Usage:
    python dashboard/dashboard.py

Then navigate to: http://127.0.0.1:8050

Author: Climate Risk Assessment Team
Date: 2025
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.config import OUTPUT_DIR, DASHBOARD_CONFIG, VISUALIZATION

# Initialize Dash app
app = dash.Dash(__name__)
app.title = DASHBOARD_CONFIG['title']

# Color scheme
colors = VISUALIZATION['color_scheme']


def load_results():
    """Load analysis results from output directory. Returns {} on any error so the app does not crash."""
    results = {}
    try:
        if not OUTPUT_DIR.exists():
            return results
        for file in OUTPUT_DIR.glob('*.csv'):
            name = file.stem
            try:
                results[name] = pd.read_csv(file)
            except Exception:
                continue
    except Exception:
        pass
    return results


def create_scvr_plot(scvr_data):
    """Create SCVR time series plot."""
    fig = go.Figure()
    
    for variable in scvr_data['variable'].unique():
        var_data = scvr_data[scvr_data['variable'] == variable]
        
        fig.add_trace(go.Scatter(
            x=var_data['year'],
            y=var_data['scvr'],
            mode='lines+markers',
            name=variable,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title='Severe Climate Variability Rating (SCVR) Over Time',
        xaxis_title='Year',
        yaxis_title='SCVR (1.0 = baseline)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def create_performance_plot(revenue_data):
    """Create asset performance comparison plot."""
    fig = go.Figure()
    
    # Base scenario
    fig.add_trace(go.Scatter(
        x=revenue_data['year'],
        y=revenue_data['revenue_usd'],
        mode='lines',
        name='Base Scenario',
        line=dict(color=colors['base'], width=3)
    ))
    
    # Add P10/P90 envelope if available
    if 'revenue_p90' in revenue_data.columns:
        fig.add_trace(go.Scatter(
            x=revenue_data['year'],
            y=revenue_data['revenue_p90'],
            mode='lines',
            name='P90',
            line=dict(width=0),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=revenue_data['year'],
            y=revenue_data['revenue_p10'],
            mode='lines',
            name='P10',
            fill='tonexty',
            fillcolor='rgba(112, 173, 71, 0.2)',
            line=dict(width=0)
        ))
    
    fig.update_layout(
        title='Asset Revenue Projections',
        xaxis_title='Year',
        yaxis_title='Revenue (USD)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def create_bi_breakdown_plot(bi_data):
    """Create business interruption breakdown plot."""
    # Aggregate by hazard type
    hazard_totals = bi_data.groupby('hazard')['bi_loss_mwh'].sum().reset_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=hazard_totals['hazard'],
            y=hazard_totals['bi_loss_mwh'],
            marker=dict(color=colors['rcp85'])
        )
    ])
    
    fig.update_layout(
        title='Total Business Interruption Losses by Hazard Type',
        xaxis_title='Hazard',
        yaxis_title='BI Loss (MWh)',
        template='plotly_white'
    )
    
    return fig


def create_degradation_plot(years):
    """Create equipment degradation curves."""
    # Synthetic degradation curves
    years_arr = np.array(years)
    
    fig = go.Figure()
    
    # Typical degradation
    typical_deg = 1 - 0.006 * years_arr
    fig.add_trace(go.Scatter(
        x=years,
        y=typical_deg * 100,
        mode='lines',
        name='Typical (0.6%/yr)',
        line=dict(color=colors['base'], width=2, dash='dash')
    ))
    
    # Climate-stressed degradation
    climate_deg = 1 - 0.015 * years_arr
    fig.add_trace(go.Scatter(
        x=years,
        y=climate_deg * 100,
        mode='lines',
        name='Climate-Stressed (1.5%/yr)',
        line=dict(color=colors['rcp85'], width=3)
    ))
    
    fig.update_layout(
        title='Equipment Performance Degradation Over Time',
        xaxis_title='Years of Operation',
        yaxis_title='Capacity Retention (%)',
        hovermode='x unified',
        template='plotly_white',
        yaxis=dict(range=[70, 100])
    )
    
    return fig


def create_monte_carlo_plot(mc_data):
    """Create Monte Carlo distribution plot."""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=mc_data['nav_ratio'],
        nbinsx=50,
        marker=dict(color=colors['rcp45']),
        name='NAV Ratio Distribution'
    ))
    
    # Add percentile lines
    p10 = mc_data['nav_ratio'].quantile(0.10)
    p50 = mc_data['nav_ratio'].quantile(0.50)
    p90 = mc_data['nav_ratio'].quantile(0.90)
    
    fig.add_vline(x=p10, line_dash="dash", line_color="red", 
                  annotation_text=f"P10: {p10:.3f}")
    fig.add_vline(x=p50, line_dash="dash", line_color="green",
                  annotation_text=f"P50: {p50:.3f}")
    fig.add_vline(x=p90, line_dash="dash", line_color="blue",
                  annotation_text=f"P90: {p90:.3f}")
    
    fig.update_layout(
        title='Monte Carlo Simulation: NAV Impairment Ratio Distribution',
        xaxis_title='NAV Impairment Ratio',
        yaxis_title='Frequency',
        template='plotly_white'
    )
    
    return fig


def create_nav_waterfall(final_results):
    """Create waterfall chart showing NAV components."""
    if final_results is None:
        return go.Figure()
    try:
        npv_base = float(final_results.get('npv_base', 0))
        npv_climate = float(final_results.get('npv_climate', 0))
    except (TypeError, AttributeError, KeyError):
        return go.Figure()
    # Estimate breakdown (simplified)
    bi_impact = npv_base * 0.15
    cat_impact = npv_base * 0.08
    deg_impact = npv_base * 0.12
    
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Base NPV", "BI Losses", "Cat Events", "Degradation", "Climate NPV"],
        y=[npv_base, -bi_impact, -cat_impact, -deg_impact, npv_climate],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": colors['rcp85']}},
        increasing={"marker": {"color": colors['base']}},
        totals={"marker": {"color": colors['rcp45']}}
    ))
    
    fig.update_layout(
        title="NAV Impairment Waterfall Analysis",
        yaxis_title="NPV (USD)",
        template='plotly_white'
    )
    
    return fig


# Dashboard Layout
app.layout = html.Div([
    html.H1('Climate Risk Assessment Dashboard',
            style={'textAlign': 'center', 'color': '#2E75B6'}),
    
    html.Hr(),
    
    # Controls
    html.Div([
        html.Label('Select Asset:'),
        dcc.Dropdown(
            id='asset-selector',
            options=[
                {'label': 'Hayhurst Solar', 'value': 'hayhurst_solar'},
                {'label': 'Maverick Wind', 'value': 'maverick_wind'}
            ],
            value='hayhurst_solar'
        ),
        
        html.Label('Select Scenario:'),
        dcc.Dropdown(
            id='scenario-selector',
            options=[
                {'label': 'RCP 4.5', 'value': 'rcp45'},
                {'label': 'RCP 8.5', 'value': 'rcp85'}
            ],
            value='rcp45'
        ),
    ], style={'width': '30%', 'margin': 'auto', 'padding': '20px'}),
    
    # Summary Metrics
    html.Div(id='summary-metrics', style={'textAlign': 'center', 'padding': '20px'}),
    
    # Visualizations
    html.Div([
        dcc.Graph(id='scvr-plot'),
        dcc.Graph(id='performance-plot'),
        dcc.Graph(id='bi-breakdown-plot'),
        dcc.Graph(id='degradation-plot'),
        dcc.Graph(id='monte-carlo-plot'),
        dcc.Graph(id='nav-waterfall-plot')
    ])
])


@app.callback(
    [Output('summary-metrics', 'children'),
     Output('scvr-plot', 'figure'),
     Output('performance-plot', 'figure'),
     Output('bi-breakdown-plot', 'figure'),
     Output('degradation-plot', 'figure'),
     Output('monte-carlo-plot', 'figure'),
     Output('nav-waterfall-plot', 'figure')],
    [Input('asset-selector', 'value'),
     Input('scenario-selector', 'value')]
)
def update_dashboard(asset_id, scenario):
    """Update all dashboard components based on selections."""
    final_data = None
    final_key = f'{asset_id}_{scenario}_final_results'

    # Load data (never raise; empty dict on error)
    results = load_results()

    # Create metric cards
    try:
        if final_key in results:
            final_data = results[final_key].iloc[0]
            nav_ratio = final_data.get('nav_impairment_ratio', 0)
            iul = final_data.get('iul_years', 0)
            eul = final_data.get('eul_years', 25)
            p10 = final_data.get('nav_ratio_p10', nav_ratio)
            p90 = final_data.get('nav_ratio_p90', nav_ratio)
            metrics = html.Div([
                html.Div([
                    html.H3(f"{nav_ratio:.3f}"),
                    html.P("NAV Impairment Ratio")
                ], style={'display': 'inline-block', 'margin': '20px', 'padding': '20px',
                         'border': '2px solid #2E75B6', 'borderRadius': '10px'}),
                html.Div([
                    html.H3(f"{iul:.0f} / {eul:.0f}"),
                    html.P("IUL / EUL (years)")
                ], style={'display': 'inline-block', 'margin': '20px', 'padding': '20px',
                         'border': '2px solid #2E75B6', 'borderRadius': '10px'}),
                html.Div([
                    html.H3(f"P10: {p10:.3f} | P90: {p90:.3f}"),
                    html.P("Confidence Interval")
                ], style={'display': 'inline-block', 'margin': '20px', 'padding': '20px',
                         'border': '2px solid #2E75B6', 'borderRadius': '10px'})
            ])
        else:
            metrics = html.Div("No results available for this selection. Run Section 3 first.")
    except Exception:
        metrics = html.Div("No results available for this selection. Run Section 3 first.")

    # Create plots (use empty figure if data missing or any error to avoid HTTP 500)
    empty_fig = go.Figure()
    try:
        scvr_key = f'{asset_id}_{scenario}_scvr'
        scvr_fig = create_scvr_plot(results[scvr_key]) if scvr_key in results else empty_fig
    except Exception:
        scvr_fig = empty_fig
    try:
        rev_key = f'{asset_id}_{scenario}_revenue'
        perf_fig = create_performance_plot(results[rev_key]) if rev_key in results else empty_fig
    except Exception:
        perf_fig = empty_fig
    try:
        bi_key = f'{asset_id}_{scenario}_bi_losses'
        bi_fig = create_bi_breakdown_plot(results[bi_key]) if bi_key in results else empty_fig
    except Exception:
        bi_fig = empty_fig
    try:
        deg_fig = create_degradation_plot(list(range(0, 26)))
    except Exception:
        deg_fig = empty_fig
    try:
        mc_key = f'{asset_id}_{scenario}_monte_carlo'
        mc_fig = create_monte_carlo_plot(results[mc_key]) if mc_key in results else empty_fig
    except Exception:
        mc_fig = empty_fig
    try:
        nav_fig = create_nav_waterfall(final_data) if final_data is not None else empty_fig
    except Exception:
        nav_fig = empty_fig

    return metrics, scvr_fig, perf_fig, bi_fig, deg_fig, mc_fig, nav_fig


if __name__ == '__main__':
    # Dash 2.14+ uses app.run(); older versions use app.run_server()
    run_fn = getattr(app, 'run', None) or getattr(app, 'run_server', None)
    run_fn(
        host=DASHBOARD_CONFIG['host'],
        port=DASHBOARD_CONFIG['port'],
        debug=DASHBOARD_CONFIG['debug']
    )
