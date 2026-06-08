import streamlit as st
import pandas as pd
import os
import plotly.express as px

from data.data_loader import load_actual_data, load_forecast_data, filter_data
from visualizations.charts import (
    plot_demand_trend, plot_demand_distribution, plot_box_distribution,
    plot_category_analysis, plot_forecast_vs_actual, plot_accuracy_heatmap,
    plot_treemap, plot_pareto, plot_monthly_boxplot, plot_seasonal_decomposition
)
from utils.helpers import apply_custom_css
from reports.exporter import generate_csv_download_link, generate_pdf_report

st.set_page_config(page_title="Vehicle Demand Forecasting", layout="wide", initial_sidebar_state="expanded")
apply_custom_css()

st.title("Vehicle Demand Forecasting Dashboard")
st.markdown("Analyze and forecast vehicle demand across different models and engines using historical sales data.")

# Define paths relative to the dashboard script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST_DATA_PATH = os.path.join(BASE_DIR, "final_data_for_vehicle_forecasting.csv")
FC_DATA_PATH = os.path.join(BASE_DIR, "forecast_details.csv")

with st.spinner("Loading Data..."):
    df_actual = load_actual_data(HIST_DATA_PATH)
    df_fc = load_forecast_data(FC_DATA_PATH)

if df_actual.empty or df_fc.empty:
    st.error("Failed to load required data. Please ensure CSV files exist in the parent directory.")
    st.stop()

# --- 2. Interactive Filters (Sidebar) ---
st.sidebar.header("Filters")
all_halbs = df_actual['HALB'].dropna().unique().tolist()
selected_halb = st.sidebar.multiselect("HALB", all_halbs)

filtered_actual = filter_data(df_actual, selected_halb, None, None, None, None)
all_engines = filtered_actual['Engine'].dropna().unique().tolist()
selected_engine = st.sidebar.multiselect("Engine", all_engines)

filtered_actual = filter_data(filtered_actual, None, selected_engine, None, None, None)
all_models = filtered_actual['Model'].dropna().unique().tolist()
selected_model = st.sidebar.multiselect("Model", all_models)

filtered_actual = filter_data(filtered_actual, None, None, selected_model, None, None)
all_types = filtered_actual['Vehicle Type'].dropna().unique().tolist()
selected_type = st.sidebar.multiselect("Vehicle Type", all_types)

min_date = df_actual['Month'].min().date()
max_date = df_actual['Month'].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply Final Filters
df_actual_filtered = filter_data(df_actual, selected_halb, selected_engine, selected_model, selected_type, date_range)
df_fc_filtered = df_fc.copy()
if selected_halb: df_fc_filtered = df_fc_filtered[df_fc_filtered['HALB'].isin(selected_halb)]
if selected_engine: df_fc_filtered = df_fc_filtered[df_fc_filtered['Engine'].isin(selected_engine)]
if selected_model: df_fc_filtered = df_fc_filtered[df_fc_filtered['Model'].isin(selected_model)]
if selected_type: df_fc_filtered = df_fc_filtered[df_fc_filtered['Vehicle Type'].isin(selected_type)]

# --- Tabs Setup ---
tabs = st.tabs([
    "Executive Summary", "Data Overview", "Exploratory Data Analysis", "Hierarchical Analysis", 
    "Forecast Comparison", "Model Performance", "Advanced Analytics", "Business Insights"
])

# --- 1. Executive Summary Section ---
with tabs[0]:
    total_demand = df_actual_filtered['Demand'].sum()
    avg_demand = df_actual_filtered['Demand'].mean()
    highest_demand_veh = "N/A"
    lowest_demand_veh = "N/A"
    
    if not df_actual_filtered.empty:
        agg = df_actual_filtered.groupby('Model')['Demand'].sum()
        highest_demand_veh = agg.idxmax() if not agg.empty else "N/A"
        lowest_demand_veh = agg.idxmin() if not agg.empty else "N/A"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><p class="metric-label">Total Demand</p><p class="metric-value">{total_demand:,.0f}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card" style="margin-top:20px;"><p class="metric-label">Avg Monthly Demand</p><p class="metric-value">{avg_demand:,.0f}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><p class="metric-label">Unique HALBs</p><p class="metric-value">{df_actual_filtered["HALB"].nunique()}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card" style="margin-top:20px;"><p class="metric-label">Engine Types</p><p class="metric-value">{df_actual_filtered["Engine"].nunique()}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><p class="metric-label">Total Models</p><p class="metric-value">{df_actual_filtered["Model"].nunique()}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card" style="margin-top:20px;"><p class="metric-label">Vehicle Types</p><p class="metric-value">{df_actual_filtered["Vehicle Type"].nunique()}</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><p class="metric-label">Highest Demand</p><p class="metric-value" style="font-size:18px;">{highest_demand_veh}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card" style="margin-top:20px;"><p class="metric-label">Lowest Demand</p><p class="metric-value" style="font-size:18px;">{lowest_demand_veh}</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Export Reports")
    report_dict = {
        "Total Demand": total_demand,
        "Unique Models": df_actual_filtered["Model"].nunique(),
        "Highest Demand": highest_demand_veh,
        "Average Accuracy (Forecast)": f"{df_fc_filtered['Accuracy %'].mean():.2f}%" if not df_fc_filtered.empty else "N/A"
    }
    st.markdown(generate_pdf_report(report_dict, "Executive_Summary.txt"), unsafe_allow_html=True)

# --- 3. Data Overview ---
with tabs[1]:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_demand_distribution(df_actual_filtered), use_container_width=True)
        st.plotly_chart(plot_demand_trend(df_actual_filtered), use_container_width=True)
    with col2:
        st.plotly_chart(plot_box_distribution(df_actual_filtered), use_container_width=True)
        st.plotly_chart(plot_category_analysis(df_actual_filtered, 'HALB'), use_container_width=True)
        
    col3, col4 = st.columns(2)
    with col3: st.plotly_chart(plot_category_analysis(df_actual_filtered, 'Engine'), use_container_width=True)
    with col4: st.plotly_chart(plot_category_analysis(df_actual_filtered, 'Vehicle Type'), use_container_width=True)

# --- Exploratory Data Analysis (EDA) ---
with tabs[2]:
    st.subheader("Exploratory Data Analysis (EDA)")
    
    col_stat1, col_stat2 = st.columns([1, 2])
    with col_stat1:
        st.markdown("#### Descriptive Statistics")
        if not df_actual_filtered.empty:
            stats_df = df_actual_filtered['Demand'].describe().reset_index()
            stats_df.columns = ['Metric', 'Value']
            st.dataframe(stats_df.style.format({"Value": "{:.2f}"}), use_container_width=True)
    with col_stat2:
        st.markdown("#### Demand Trend & Rolling Average")
        st.plotly_chart(plot_seasonal_decomposition(df_actual_filtered), use_container_width=True)
        
    st.markdown("#### Demand Seasonality")
    st.plotly_chart(plot_monthly_boxplot(df_actual_filtered), use_container_width=True)

# --- 4. Hierarchical Analysis & 8. Forecast Visualizations ---
with tabs[3]:
    st.markdown("### Hierarchical Demand Drill-Down")
    st.plotly_chart(plot_forecast_vs_actual(df_actual_filtered, df_fc_filtered, "Historical vs Forecast Demand by Model"), use_container_width=True)
    
    st.markdown("#### Monthly Forecast Breakdown (Jan-Mar 2025)")
    if not df_fc_filtered.empty:
        summary_pivot = pd.pivot_table(df_fc_filtered, values='Forecast Demand', index='Month', columns='Model Used', aggfunc='sum')
        
        # Extract Actual Demand avoiding duplicates caused by multiple models per segment
        actuals = df_fc_filtered.drop_duplicates(subset=['HALB', 'Engine', 'Model', 'Vehicle Type', 'Month'])
        actual_summary = actuals.groupby('Month')['Actual Demand'].sum()
        
        # Add Actual to the pivot table at the front
        summary_pivot.insert(0, 'Actual', actual_summary)
        
        # Format Month index for cleaner display
        summary_pivot.index = summary_pivot.index.strftime('%Y-%b')
        st.dataframe(summary_pivot.style.format("{:.2f}"))

# --- 6. Forecast Comparison Dashboard ---
with tabs[4]:
    st.subheader("Forecast Comparison Table")
    if not df_fc_filtered.empty:
        # Zero table: Forecast Demand is 0 (includes negative-clamped rows and truly zero rows)
        # Non-zero table: only rows where Forecast Demand > 0
        is_zero = df_fc_filtered['Forecast Demand'] == 0
        
        df_zero = df_fc_filtered[is_zero]
        df_non_zero = df_fc_filtered[~is_zero]
        
        st.markdown("#### Non-Zero Forecasts & Demand")
        if not df_non_zero.empty:
            st.dataframe(
                df_non_zero,
                use_container_width=True,
                column_config={
                    "HALB":           st.column_config.TextColumn("HALB", width=120),
                    "Engine":         st.column_config.TextColumn("Engine", width=80),
                    "Model":          st.column_config.TextColumn("Model", width=160),
                    "Vehicle Type":   st.column_config.TextColumn("Vehicle Type", width=100),
                    "Model Used":     st.column_config.TextColumn("Model Used", width=120),
                    "Month":          st.column_config.TextColumn("Month", width=110),
                    "Actual Demand":  st.column_config.NumberColumn("Actual Demand", width=110, format="%d"),
                    "Forecast Demand":st.column_config.NumberColumn("Forecast Demand", width=120, format="%d"),
                    "Difference":     st.column_config.NumberColumn("Difference", width=90, format="%d"),
                    "Accuracy %":     st.column_config.NumberColumn("Accuracy %", width=100, format="%.2f"),
                    "MAPE":           st.column_config.NumberColumn("MAPE", width=90, format="%.2f"),
                }
            )
            st.markdown(generate_csv_download_link(df_non_zero, "forecast_comparison_nonzero.csv", "Export Non-Zero Data"), unsafe_allow_html=True)
        else:
            st.info("No non-zero records found for this selection.")
            
        st.markdown("#### Zero Forecasts & Demand")
        if not df_zero.empty:
            st.dataframe(
                df_zero,
                use_container_width=True,
                column_config={
                    "HALB":           st.column_config.TextColumn("HALB", width=120),
                    "Engine":         st.column_config.TextColumn("Engine", width=80),
                    "Model":          st.column_config.TextColumn("Model", width=160),
                    "Vehicle Type":   st.column_config.TextColumn("Vehicle Type", width=100),
                    "Model Used":     st.column_config.TextColumn("Model Used", width=120),
                    "Month":          st.column_config.TextColumn("Month", width=110),
                    "Actual Demand":  st.column_config.NumberColumn("Actual Demand", width=110, format="%d"),
                    "Forecast Demand":st.column_config.NumberColumn("Forecast Demand", width=120, format="%d"),
                    "Difference":     st.column_config.NumberColumn("Difference", width=90, format="%d"),
                    "Accuracy %":     st.column_config.NumberColumn("Accuracy %", width=100, format="%.2f"),
                    "MAPE":           st.column_config.NumberColumn("MAPE", width=90, format="%.2f"),
                }
            )
            st.markdown(generate_csv_download_link(df_zero, "forecast_comparison_zero.csv", "Export Zero Data"), unsafe_allow_html=True)
        else:
            st.info("No zero records found for this selection.")
    else:
        st.info("No forecast data available for current selection.")

# --- 7. Model Performance Section & 10. Accuracy Heatmap ---
with tabs[5]:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Accuracy Leaderboard")
        if not df_fc_filtered.empty:
            leaderboard = df_fc_filtered.groupby('Model Used').agg({'Accuracy %': 'mean', 'MAPE': 'mean'}).reset_index().sort_values('Accuracy %', ascending=False)
            st.dataframe(
                leaderboard,
                use_container_width=True,
                column_config={
                    "Model Used":  st.column_config.TextColumn("Model Used", width=140),
                    "Accuracy %":  st.column_config.NumberColumn("Accuracy %", width=110, format="%.2f %%"),
                    "MAPE":        st.column_config.NumberColumn("MAPE", width=90, format="%.2f"),
                }
            )
            
            fig_acc = px.bar(leaderboard, x='Model Used', y='Accuracy %', title="Accuracy Comparison", color='Accuracy %', color_continuous_scale="Blues")
            st.plotly_chart(fig_acc, use_container_width=True)
    with col2:
        st.subheader("Accuracy Heatmap")
        st.plotly_chart(plot_accuracy_heatmap(df_fc_filtered), use_container_width=True)

# --- 11. Advanced Analytics ---
with tabs[6]:
    st.subheader("Top Demand Contributors")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_treemap(df_actual_filtered), use_container_width=True)
    with col2:
        st.plotly_chart(plot_pareto(df_actual_filtered), use_container_width=True)

# --- 9. Business Insights Section ---
with tabs[7]:
    st.subheader("Automated Business Insights")
    if not df_actual_filtered.empty and not df_fc_filtered.empty:

        # ── Compute all insight values ──────────────────────────────────
        halb_agg      = df_actual_filtered.groupby('HALB')['Demand'].sum()
        engine_agg    = df_actual_filtered.groupby('Engine')['Demand'].sum()
        model_agg     = df_actual_filtered.groupby('Model')['Demand'].sum()
        vtype_agg     = df_actual_filtered.groupby('Vehicle Type')['Demand'].sum()
        monthly_agg   = df_actual_filtered.groupby('Month')['Demand'].sum().sort_index()

        best_halb       = halb_agg.idxmax()   if not halb_agg.empty   else "N/A"
        worst_halb      = halb_agg.idxmin()   if not halb_agg.empty   else "N/A"
        best_engine     = engine_agg.idxmax() if not engine_agg.empty else "N/A"
        top_model       = model_agg.idxmax()  if not model_agg.empty  else "N/A"
        low_model       = model_agg.idxmin()  if not model_agg.empty  else "N/A"
        best_vtype      = vtype_agg.idxmax()  if not vtype_agg.empty  else "N/A"
        worst_vtype     = vtype_agg.idxmin()  if not vtype_agg.empty  else "N/A"
        peak_month      = monthly_agg.idxmax().strftime('%B %Y') if not monthly_agg.empty else "N/A"
        low_month       = monthly_agg.idxmin().strftime('%B %Y') if not monthly_agg.empty else "N/A"

        # Volatility: std/mean coefficient of variation per model
        vol = df_actual_filtered.groupby('Model')['Demand'].std() / (df_actual_filtered.groupby('Model')['Demand'].mean() + 1)
        most_volatile   = vol.idxmax() if not vol.empty else "N/A"

        # Growth: compare first half vs second half of date range
        if len(monthly_agg) >= 4:
            mid = len(monthly_agg) // 2
            first_half  = monthly_agg.iloc[:mid].mean()
            second_half = monthly_agg.iloc[mid:].mean()
            growth_pct  = ((second_half - first_half) / (first_half + 1)) * 100
            trend_label = f"📈 +{growth_pct:.1f}%" if growth_pct >= 0 else f"📉 {growth_pct:.1f}%"
            trend_color = "#05CD99" if growth_pct >= 0 else "#EE5D50"
        else:
            trend_label = "N/A"
            trend_color = "#A3AED0"

        # Forecast accuracy summary
        acc_agg     = df_fc_filtered.groupby('Model Used')['Accuracy %'].mean()
        best_model  = acc_agg.idxmax() if not acc_agg.empty else "N/A"
        worst_fc    = acc_agg.idxmin() if not acc_agg.empty else "N/A"
        avg_acc     = acc_agg.mean()

        # Pareto: how many models cover 80% of demand
        sorted_models = model_agg.sort_values(ascending=False)
        cumsum = sorted_models.cumsum() / sorted_models.sum()
        pareto_count = int((cumsum < 0.80).sum()) + 1

        # ── Render insight cards ────────────────────────────────────────
        def insight_card(icon, title, value, subtitle="", color="#4318FF"):
            st.markdown(f"""
            <div style="background:#fff;border-radius:12px;padding:16px 20px;
                        box-shadow:0 4px 12px rgba(112,144,176,0.12);
                        border-left:5px solid {color};margin-bottom:14px;">
                <div style="font-size:13px;color:#A3AED0;font-weight:600;text-transform:uppercase;">{icon} {title}</div>
                <div style="font-size:20px;font-weight:700;color:#2B3674;margin:4px 0;">{value}</div>
                <div style="font-size:12px;color:#A3AED0;">{subtitle}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("#### 📊 Demand Intelligence")
        c1, c2, c3 = st.columns(3)
        with c1:
            insight_card("🏆", "Top Contributing HALB",  best_halb,
                         f"Total: {halb_agg.get(best_halb,0):,.0f} units", "#4318FF")
            insight_card("⚠️", "Lowest Demand HALB", worst_halb,
                         f"Total: {halb_agg.get(worst_halb,0):,.0f} units", "#EE5D50")
        with c2:
            insight_card("🚗", "Top Performing Model", top_model,
                         f"Total: {model_agg.get(top_model,0):,.0f} units", "#05CD99")
            insight_card("📉", "Declining Model", low_model,
                         f"Total: {model_agg.get(low_model,0):,.0f} units", "#FF6B6B")
        with c3:
            insight_card("⚡", "Most Volatile Model", most_volatile,
                         "Highest demand variability (CV)", "#FFB547")
            insight_card("🔥", "Peak Demand Month", peak_month,
                         f"Lowest demand: {low_month}", "#4318FF")

        st.markdown("#### 🔮 Forecast Intelligence")
        c4, c5, c6 = st.columns(3)
        with c4:
            insight_card("✅", "Best Forecast Model", best_model,
                         f"Avg accuracy: {acc_agg.get(best_model, 0):.1f}%", "#05CD99")
        with c5:
            insight_card("❌", "Worst Forecast Model", worst_fc,
                         f"Avg accuracy: {acc_agg.get(worst_fc, 0):.1f}%", "#EE5D50")
        with c6:
            insight_card("📐", "Overall Avg Forecast Accuracy", f"{avg_acc:.1f}%",
                         "Across all models & segments", "#4318FF")

        st.markdown("#### 📈 Trend & Segment Intelligence")
        c7, c8, c9 = st.columns(3)
        with c7:
            insight_card("📊", "Overall Demand Trend", trend_label,
                         "Second half vs first half of period", trend_color)
        with c8:
            insight_card("🚙", "Top Vehicle Type", best_vtype,
                         f"Lowest: {worst_vtype}", "#4318FF")
        with c9:
            insight_card("🌿", "Pareto — 80% Demand",
                         f"{pareto_count} model(s)",
                         "Number of models driving 80% of total demand", "#FFB547")

    else:
        st.info("Insights not available without data.")
