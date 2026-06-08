import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Theme configurations
THEME_COLOR = "#2B3674"
ACCENT_COLOR = "#4318FF"
SUCCESS_COLOR = "#05CD99"

def plot_demand_trend(df, title="Monthly Demand Trend"):
    """Line chart for monthly demand trend."""
    if df.empty: return go.Figure()
    trend_df = df.groupby('Month')['Demand'].sum().reset_index()
    fig = px.line(trend_df, x='Month', y='Demand', title=title, markers=True)
    fig.update_traces(line_color=ACCENT_COLOR)
    fig.update_layout(template="plotly_white", margin=dict(t=50, l=0, r=0, b=0))
    return fig

def plot_demand_distribution(df):
    """Histogram for demand distribution — filters zeros and uses log Y scale for readability."""
    if df.empty: return go.Figure()
    # Filter out zero demand rows so the histogram isn't dominated by them
    df_nonzero = df[df['Demand'] > 0]
    if df_nonzero.empty:
        df_nonzero = df
    fig = px.histogram(
        df_nonzero, x='Demand', nbins=40,
        title="Demand Distribution (Non-Zero)",
        log_y=True,           # Log scale makes the tail visible
        color_discrete_sequence=[ACCENT_COLOR]
    )
    fig.update_traces(marker_color=ACCENT_COLOR, marker_line_color="#2B3674", marker_line_width=0.5)
    fig.update_layout(
        template="plotly_white",
        margin=dict(t=50, l=0, r=0, b=0),
        yaxis_title="Count (log scale)",
        xaxis_title="Demand"
    )
    return fig

def plot_box_distribution(df):
    """Box plot for demand distribution."""
    if df.empty: return go.Figure()
    fig = px.box(df, y='Demand', title="Demand Box Plot")
    fig.update_traces(marker_color=THEME_COLOR)
    fig.update_layout(template="plotly_white", margin=dict(t=50, l=0, r=0, b=0))
    return fig

def plot_category_analysis(df, category_col, top_n=20):
    """Horizontal bar chart — shows Top N categories by demand."""
    if df.empty: return go.Figure()
    cat_df = df.groupby(category_col)['Demand'].sum().reset_index().sort_values('Demand', ascending=False)
    # Limit to top N only if data exceeds it
    total = len(cat_df)
    cat_df = cat_df.head(top_n).sort_values('Demand', ascending=True)
    title = f"Demand by {category_col}" if total <= top_n else f"Top {top_n} by Demand — {category_col}"
    fig = px.bar(
        cat_df, x='Demand', y=category_col,
        orientation='h',
        title=title,
        color='Demand',
        color_continuous_scale=[[0, '#A3AED0'], [0.4, ACCENT_COLOR], [1.0, THEME_COLOR]]
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(t=50, l=0, r=20, b=0),
        coloraxis_showscale=False,
        height=500           # fixed height — scrolling inside Plotly if needed
    )
    return fig

def plot_forecast_vs_actual(hist_df, forecast_df, title="Historical vs Forecast"):
    """Line chart with historical vs forecasted demand."""
    fig = go.Figure()

    if not hist_df.empty:
        trend_hist = hist_df.groupby('Month')['Demand'].sum().reset_index()
        fig.add_trace(go.Scatter(x=trend_hist['Month'], y=trend_hist['Demand'],
                                 mode='lines+markers', name='Actual History',
                                 line=dict(color=THEME_COLOR, width=2)))

    if not forecast_df.empty:
        trend_fc = forecast_df.groupby(['Month', 'Model Used'])['Forecast Demand'].sum().reset_index()
        for model in trend_fc['Model Used'].unique():
            model_df = trend_fc[trend_fc['Model Used'] == model]
            fig.add_trace(go.Scatter(x=model_df['Month'], y=model_df['Forecast Demand'],
                                     mode='lines+markers', name=f'Forecast ({model})',
                                     line=dict(dash='dash', width=2)))
    
    fig.update_layout(title=title, template="plotly_white", hovermode='x unified', margin=dict(t=50, l=0, r=0, b=0))
    return fig

def plot_accuracy_heatmap(forecast_df, top_n_halb=30):
    """
    MAPE Heatmap — rows: HALB, columns: Forecast Model.
    Only uses rows with non-zero Actual Demand to show real variation.
    Sorted by worst average MAPE so problematic HALBs appear at top.
    Lower MAPE (green) = better. Higher MAPE (red) = worse.
    """
    if forecast_df.empty: return go.Figure()

    # Filter to non-zero actuals so trivial 100% accuracy rows don't dominate
    df_nz = forecast_df[forecast_df['Actual Demand'] > 0]
    if df_nz.empty:
        # Fall back to full data if everything is zero
        df_nz = forecast_df

    pivot = pd.pivot_table(
        df_nz, values='MAPE',
        index='HALB', columns='Model Used',
        aggfunc='mean'
    )
    if pivot.empty: return go.Figure()

    # Sort by worst (highest) average MAPE so interesting rows appear first
    pivot['_avg'] = pivot.mean(axis=1)
    pivot = pivot.sort_values('_avg', ascending=False).head(top_n_halb).drop(columns='_avg')

    pivot_rounded = pivot.round(1)

    # Dynamic color range based on actual data spread
    vmin = float(pivot.min().min())
    vmax = float(pivot.max().max())
    # Cap vmax at 200 to avoid extreme outliers washing out the scale
    vmax = min(vmax, 200)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=list(pivot.columns),
        y=list(pivot.index),
        # Green = low MAPE (good), Red = high MAPE (bad) — REVERSED scale
        colorscale=[
            [0.0,  '#1A7340'],   # dark green — 0% MAPE (perfect)
            [0.25, '#A8D5A2'],   # light green
            [0.5,  '#F39C12'],   # amber
            [0.75, '#E74C3C'],   # red
            [1.0,  '#7B241C'],   # dark red — very high MAPE
        ],
        zmin=vmin, zmax=vmax,
        text=pivot_rounded.values,
        texttemplate="%{text}",
        textfont=dict(size=11, color='white'),
        hovertemplate=(
            "<b>HALB</b>: %{y}<br>"
            "<b>Model</b>: %{x}<br>"
            "<b>MAPE</b>: %{z:.1f}<br>"
            "<extra></extra>"
        ),
        showscale=True,
        colorbar=dict(
            title="MAPE<br>(lower=better)",
            thickness=15, len=0.9
        )
    ))

    cell_h = max(24, 600 // max(len(pivot), 1))
    fig.update_layout(
        title="MAPE Heatmap — Worst Performing HALBs × Forecast Model<br>"
              "<sup>Green = low error (good) | Red = high error (bad) | Non-zero actuals only</sup>",
        template="plotly_white",
        height=max(500, len(pivot) * cell_h + 130),
        margin=dict(t=80, l=150, r=20, b=50),
        xaxis=dict(tickangle=-30, side='bottom'),
        yaxis=dict(autorange='reversed')
    )
    return fig

def plot_treemap(df):
    """Treemap of Top Demand Contributors."""
    if df.empty: return go.Figure()
    agg_df = df.groupby(['HALB', 'Model'])['Demand'].sum().reset_index()
    fig = px.treemap(agg_df, path=[px.Constant("All"), 'HALB', 'Model'], values='Demand',
                     title="Top Demand Contributors (Treemap)", color='Demand', color_continuous_scale='Blues')
    fig.update_layout(margin=dict(t=50, l=0, r=0, b=0))
    return fig

def plot_pareto(df):
    """Pareto chart for 80/20 analysis by Model."""
    if df.empty: return go.Figure()
    cat_df = df.groupby('Model')['Demand'].sum().reset_index().sort_values('Demand', ascending=False)
    cat_df['Cumulative Percentage'] = (cat_df['Demand'].cumsum() / cat_df['Demand'].sum()) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=cat_df['Model'], y=cat_df['Demand'], name="Demand", marker_color=ACCENT_COLOR))
    fig.add_trace(go.Scatter(x=cat_df['Model'], y=cat_df['Cumulative Percentage'], name="Cumulative %", yaxis="y2", line=dict(color=SUCCESS_COLOR, width=3)))
    
    fig.update_layout(
        title="Pareto Analysis (Models)",
        template="plotly_white",
        yaxis=dict(title="Demand"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105]),
        margin=dict(t=50, l=0, r=0, b=0),
        legend=dict(x=0.01, y=0.99)
    )
    return fig

def plot_monthly_boxplot(df):
    """Box plot of demand by month to show seasonality."""
    if df.empty: return go.Figure()
    # Extract month name
    df_copy = df.copy()
    df_copy['Month Name'] = df_copy['Month'].dt.strftime('%b')
    df_copy['Month Num'] = df_copy['Month'].dt.month
    df_copy = df_copy.sort_values('Month Num')
    
    fig = px.box(df_copy, x='Month Name', y='Demand', title="Demand Seasonality by Month", color='Month Name')
    fig.update_layout(template="plotly_white", margin=dict(t=50, l=0, r=0, b=0), showlegend=False)
    return fig

def plot_seasonal_decomposition(df):
    """Line chart showing aggregate trend of demand (simplified seasonal breakdown)."""
    if df.empty: return go.Figure()
    trend_df = df.groupby('Month')['Demand'].sum().reset_index().sort_values('Month')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend_df['Month'], y=trend_df['Demand'], mode='lines+markers', name='Raw Demand', line=dict(color=ACCENT_COLOR)))
    
    # Simple rolling average for trend
    trend_df['Trend (3-Month)'] = trend_df['Demand'].rolling(window=3, center=True).mean()
    fig.add_trace(go.Scatter(x=trend_df['Month'], y=trend_df['Trend (3-Month)'], mode='lines', name='3-Month Trend', line=dict(color=SUCCESS_COLOR, width=3)))
    
    fig.update_layout(title="Demand Trend Analysis", template="plotly_white", hovermode='x unified', margin=dict(t=50, l=0, r=0, b=0))
    return fig
