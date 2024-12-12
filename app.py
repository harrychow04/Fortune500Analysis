"""
Name:       Harry Chow
CS230:      Section 2
Data:       https://www.kaggle.com/datasets/mannmann2/fortune-500-corporate-headquarters
URL:        Link to your web application on Streamlit Cloud (if posted) 

Description:    

This program ... (a few sentences about your program and the queries and charts)
"""

import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px

# [DA1] Clean the data
@st.cache_data
def load_and_clean_data(filepath):
    try:
        df = pd.read_csv(filepath)
        # Ensure columns are strings before applying `.str.replace`
        if not df['REVENUES'].dtype == 'object':
            df['REVENUES'] = df['REVENUES'].astype(str)
        if not df['EMPLOYEES'].dtype == 'object':
            df['EMPLOYEES'] = df['EMPLOYEES'].astype(str)
        if not df['PROFIT'].dtype == 'object':
            df['PROFIT'] = df['PROFIT'].astype(str)
        
        # Convert REVENUES and PROFIT to numeric, handling potential errors
        df['REVENUES'] = pd.to_numeric(df['REVENUES'].str.replace(',', ''), errors='coerce').fillna(0)
        df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'].str.replace(',', ''), errors='coerce').fillna(0)
        df['PROFIT'] = pd.to_numeric(df['PROFIT'].str.replace(',', ''), errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# [PY2] Function that returns more than one value
def calculate_summary(df):
    if df.empty:
        return 0, 0, 0  # Handle case where no data is filtered
    total_revenue = df['REVENUES'].sum() / 1e3  # Convert to billions
    total_employees = df['EMPLOYEES'].sum()
    avg_revenue_per_employee = total_revenue / total_employees if total_employees > 0 else 0
    return total_revenue, total_employees, avg_revenue_per_employee

# Load data
data_file = 'Fortune 500 Corporate Headquarters.csv'
df = load_and_clean_data(data_file)

# Streamlit app with tabs
st.title("Fortune 500 Data Explorer")

try:
    tab1, tab2 = st.tabs(["State Comparison", "Company Map"])

    # Tab 1: State Comparison
    with tab1:
        st.subheader("State Comparison")
        total_revenue, total_employees, avg_revenue_per_employee = calculate_summary(df)
        st.write(f"**Total Revenue**: ${total_revenue:,.2f} Billion")
        st.write(f"**Total Employees**: {total_employees:,}")
        st.write(f"**Average Revenue per Employee**: ${avg_revenue_per_employee:,.2f} Billion")

    # Tab 2: Static Dot Map
    with tab2:
        st.subheader("Company Headquarters Map")
        # Use static dot size for simplicity
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["LONGITUDE", "LATITUDE"],
            get_radius=30000,  # Static radius size for all dots
            get_color=[255, 0, 0],
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=3)
        map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME}"})
        st.pydeck_chart(map_fig)

except Exception as e:
    st.error(f"An error occurred: {e}")
