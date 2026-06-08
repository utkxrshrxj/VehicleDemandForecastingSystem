import pandas as pd
import streamlit as st
import os
import numpy as np

def load_actual_data(file_path):
    """Loads historical demand data."""
    if not os.path.exists(file_path):
        st.error(f"Data file not found: {file_path}")
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    df['Month'] = pd.to_datetime(df['Month'], format='%d/%m/%Y', errors='coerce')
    # Rename columns to standard names
    df.rename(columns={
        'Halb': 'HALB',
        'engine_type': 'Engine',
        'map_model': 'Model',
        'Vehicle_Type': 'Vehicle Type',
        'total_demand': 'Demand'
    }, inplace=True)
    return df

def load_forecast_data(file_path):
    """Loads pre-calculated forecast data."""
    if not os.path.exists(file_path):
        st.error(f"Forecast file not found: {file_path}")
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    # The file has format yyyy-mm-dd
    df['Month'] = pd.to_datetime(df['Month'], errors='coerce')
    df.rename(columns={
        'Halb': 'HALB',
        'Vehicle_Type': 'Vehicle Type',
        'Forecast_Model': 'Model Used',
        'Actual_Demand': 'Actual Demand',
        'Forecast_Demand': 'Forecast Demand'
    }, inplace=True)
    
    # Step 1: Floor Forecast Demand to whole integer (vehicles cannot be fractions)
    df['Forecast Demand'] = np.floor(df['Forecast Demand']).astype(int)
    
    # Step 2: Clamp negative forecasts to 0 (demand cannot be negative)
    df['Forecast Demand'] = df['Forecast Demand'].clip(lower=0)
    
    # Step 3: Recalculate Difference based on clean floored+clamped forecast
    df['Difference'] = df['Actual Demand'] - df['Forecast Demand']
    
    # Step 4: Recalculate accuracy metrics on clean data
    def calculate_accuracy(row):
        act = row['Actual Demand']
        fcast = row['Forecast Demand']
        diff = abs(act - fcast)
        if act == 0 and fcast == 0:
            return 100.0, 0.0
        elif act == 0:
            # Actual is 0 but forecast is non-zero: full penalty
            return 0.0, 100.0
        mape = (diff / act) * 100
        acc = max(0.0, 100 - mape)
        return round(acc, 4), round(mape, 4)

    acc_mape = df.apply(calculate_accuracy, axis=1)
    df['Accuracy %'] = acc_mape.apply(lambda x: x[0])
    df['MAPE'] = acc_mape.apply(lambda x: x[1])
    
    return df

def filter_data(df, selected_halb, selected_engine, selected_model, selected_type, date_range):
    """Filters data based on sidebar selections."""
    filtered_df = df.copy()
    if selected_halb:
        filtered_df = filtered_df[filtered_df['HALB'].isin(selected_halb)]
    if selected_engine:
        filtered_df = filtered_df[filtered_df['Engine'].isin(selected_engine)]
    if selected_model:
        filtered_df = filtered_df[filtered_df['Model'].isin(selected_model)]
    if selected_type:
        filtered_df = filtered_df[filtered_df['Vehicle Type'].isin(selected_type)]
        
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['Month'].dt.date >= start_date) & (filtered_df['Month'].dt.date <= end_date)]
        
    return filtered_df
