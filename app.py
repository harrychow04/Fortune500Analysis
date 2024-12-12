"""
Name:       Harry Chow
CS230:      Section 2
Data:       https://www.kaggle.com/datasets/mannmann2/fortune-500-corporate-headquarters
URL:        Link to your web application on Streamlit Cloud (if posted) 

Description:    
This app allows users to explore data on Fortune 500 companies through state comparisons and detailed company comparisons. Gain insights into revenue, profits, and employee distribution.
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
        # Strip whitespace from column names to avoid KeyError
        df.columns = df.columns.str.strip()

        # Check if 'STATE' column exists and is properly formatted
        if 'STATE' not in df.columns:
            st.error("The 'STATE' column is missing from the dataset. Please check your CSV file.")
            return pd.DataFrame()

        # Convert 'STATE' column to string
        df['STATE'] = df['STATE'].astype(str)

        # Ensure other numeric columns are cleaned properly
        df['REVENUES'] = pd.to_numeric(df['REVENUES'].str.replace(',', ''), errors='coerce').fillna(0)
        df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'].str.replace(',', ''), errors='coerce').fillna(0)
        df['PROFIT'] = pd.to_numeric(df['PROFIT'].str.replace(',', ''), errors='coerce').fillna(0)

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
data_file = 'Fortune 500 Corporate Headquarters.csv'
df = load_and_clean_data(data_file)

if not df.empty:
    # Sidebar with logo and description
    st.sidebar.image("logo.png", caption=None)
    st.sidebar.markdown(
        "Explore Fortune 500 companies through state comparisons, company maps, and custom insights."
    )

    # Streamlit app with tabs
    st.title("Fortune 500 Data Explorer")
    tab1, tab2, tab3, tab4 = st.tabs(["State Comparison", "Company Map", "Company Comparison", "Interactive Insights"])

    # Tab 1: State Comparison
    with tab1:
        st.subheader("State Comparison")

        # Filters
        state_list = ["All States"] + sorted(df['STATE'].unique())
        selected_states = st.sidebar.multiselect("Filter by States", state_list, default="All States")

        filtered_df = df if "All States" in selected_states else df[df['STATE'].isin(selected_states)]

        # [PY2] Summary Metrics
        total_revenue = filtered_df['REVENUES'].sum()
        total_employees = filtered_df['EMPLOYEES'].sum()
        st.write(f"**Total Revenue**: ${total_revenue:,.0f}")
        st.write(f"**Total Employees**: {total_employees:,}")

        # [VIZ1] Scatter Plot: Revenue vs Employees
        st.subheader("Revenue vs Employees")
        fig1 = px.scatter(
            filtered_df,
            x='EMPLOYEES',
            y='REVENUES',
            hover_data=['NAME', 'CITY'],
            title="Company Revenue vs Employees",
            labels={'EMPLOYEES': 'Employees', 'REVENUES': 'Revenue'},
        )
        fig1.update_traces(texttemplate='%{y:,}', textposition='top center')
        st.plotly_chart(fig1)

        # Heatmaps
        st.subheader("Heatmaps")

        # [DA3] Profit by State
        profit_by_state = filtered_df.groupby('STATE')['PROFIT'].sum().reset_index()
        fig2 = px.choropleth(
            profit_by_state,
            locations='STATE',
            locationmode='USA-states',
            color='PROFIT',
            color_continuous_scale='reds',
            title="Profit by State",
            scope="usa",
        )
        st.plotly_chart(fig2)

        # [DA2] Revenue by State
        revenue_by_state = filtered_df.groupby('STATE')['REVENUES'].sum().reset_index()
        fig3 = px.choropleth(
            revenue_by_state,
            locations='STATE',
            locationmode='USA-states',
            color='REVENUES',
            color_continuous_scale='blues',
            title="Revenue by State",
            scope="usa",
        )
        st.plotly_chart(fig3)

        # [DA5] Companies by State
        companies_by_state = filtered_df.groupby('STATE').size().reset_index(name='COMPANIES')
        fig4 = px.choropleth(
            companies_by_state,
            locations='STATE',
            locationmode='USA-states',
            color='COMPANIES',
            color_continuous_scale='greens',
            title="Companies by State",
            scope="usa",
        )
        st.plotly_chart(fig4)
else:
    st.error("No data available to display.")
