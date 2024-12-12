"""
Name:       Harry Chow
CS230:      Section 2
Data:       https://www.kaggle.com/datasets/mannmann2/fortune-500-corporate-headquarters
URL:        Link to your web application on Streamlit Cloud (if posted) 

Description:    
This app allows users to explore data on Fortune 500 companies through state comparisons and detailed company comparisons. Gain insights into revenue, profits, and employee distribution.
'''

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
        
        # Convert REVENUES, EMPLOYEES, and PROFIT to numeric, handling potential errors
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

# Sidebar with logo and description
st.sidebar.image("logo.png", caption=None)  # Restore logo
st.sidebar.markdown(
    "This app allows users to explore data on Fortune 500 companies through state comparisons and detailed company comparisons. Gain insights into revenue, profits, and employee distribution."
)

# Streamlit app with tabs
st.title("Fortune 500 Data Explorer")

try:
    tab1, tab2 = st.tabs(["State Comparison", "Company Map"])

    # Tab 1: State Comparison
    with tab1:
        st.subheader("State Comparison")
        
        # State filter with "All States" option
        state_list = ["All States"] + sorted(df['STATE'].unique())
        selected_states = st.sidebar.multiselect("Filter by States", state_list, default="All States")
        
        # Filter the dataframe based on state selection
        if "All States" in selected_states:
            filtered_df = df
        else:
            filtered_df = df[df['STATE'].isin(selected_states)]
        
        # Summary Metrics
        total_revenue, total_employees, avg_revenue_per_employee = calculate_summary(filtered_df)
        st.write(f"**Total Revenue**: ${total_revenue:,.2f} Billion")
        st.write(f"**Total Employees**: {total_employees:,}")
        st.write(f"**Average Revenue per Employee**: ${avg_revenue_per_employee:,.2f} Billion")

        # Pie Chart: Employee Distribution
        st.subheader("Employee Distribution by State")
        state_employees = filtered_df.groupby('STATE')['EMPLOYEES'].sum().reset_index()
        state_employees = state_employees.sort_values(by='EMPLOYEES', ascending=False)
        
        # Limit to top 10 states and group others
        top_states = state_employees[:10]
        other_states = state_employees[10:]
        other_sum = other_states['EMPLOYEES'].sum()
        other_row = pd.DataFrame({'STATE': ['Other'], 'EMPLOYEES': [other_sum]})
        top_states = pd.concat([top_states, other_row], ignore_index=True)
        
        fig1 = px.pie(top_states, names='STATE', values='EMPLOYEES', title="Employee Distribution by State")
        st.plotly_chart(fig1)

        # Heatmap: Profit by State
        st.subheader("Profit Heatmap by State")
        state_profits = filtered_df.groupby('STATE')['PROFIT'].sum().reset_index()
        fig2 = px.choropleth(
            state_profits,
            locations='STATE',
            locationmode='USA-states',
            color='PROFIT',
            color_continuous_scale='reds',
            title="Total Profit by State",
            scope="usa",
        )
        st.plotly_chart(fig2)

        # Scatter Plot: Revenue vs Employees
        st.subheader("Revenue vs Employees")
        fig3 = px.scatter(
            filtered_df,
            x='EMPLOYEES',
            y=filtered_df['REVENUES'] / 1e9,  # Convert to billions
            hover_data=['NAME', 'CITY'],
            title="Company Revenue vs Employees",
            labels={'EMPLOYEES': 'Employees', 'REVENUES': 'Revenues (in Billions)'},
        )
        st.plotly_chart(fig3)

    # Tab 2: Company Headquarters Map
    with tab2:
        st.subheader("Company Headquarters Map")
        # Use static dot size for simplicity
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["LONGITUDE", "LATITUDE"],
            get_radius=20000,  # Smaller static radius
            get_color=[255, 0, 0],
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=3)
        map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME}"})
        st.pydeck_chart(map_fig)

except Exception as e:
    st.error(f"An error occurred: {e}")
