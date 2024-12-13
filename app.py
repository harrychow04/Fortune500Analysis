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

# [DA1] Clean and load the data
@st.cache_data
def load_and_clean_data(filepath):
    try:
        df = pd.read_csv(filepath)
        # Standardize column names
        df.columns = df.columns.str.strip().str.upper().str.replace(' ', '_')

        # Ensure financial columns are numeric
        if 'REVENUES' in df.columns:
            df['REVENUES'] = pd.to_numeric(df['REVENUES'].str.replace(',', ''), errors='coerce')
        if 'PROFIT' in df.columns:
            df['PROFIT'] = pd.to_numeric(df['PROFIT'].str.replace(',', ''), errors='coerce')
        if 'EMPLOYEES' in df.columns:
            df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'].str.replace(',', ''), errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
data_file = 'Fortune 500 Corporate Headquarters.csv'
df = load_and_clean_data(data_file)

# [PY2] Function to calculate summaries
def calculate_summary(df):
    if df.empty:
        return 0, 0  # Handle empty data
    total_revenue = df['REVENUES'].sum()
    total_employees = df['EMPLOYEES'].sum()
    return total_revenue, total_employees

# App layout
st.title("Fortune 500 Data Explorer")

logo_url = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Fortune_500_logo.svg"
st.image(logo_url, width=200)

try:
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["State Comparison", "Company Map", "Company Comparison", "Interactive Insights"])

    # Tab 1: State Comparison
    with tab1:
        st.subheader("State Comparison")
        total_revenue, total_employees = calculate_summary(df)
        st.write(f"**Total Revenue**: ${total_revenue:,.2f} (In Millions)")
        st.write(f"**Total Employees**: {total_employees:,}")

        # Heatmaps
        st.markdown("### Heatmaps")

        # Profit by state
        profit_map = px.choropleth(
            df,
            locations="STATE",
            locationmode="USA-states",
            color="PROFIT",
            scope="usa",
            title="Profit by State (In Millions)",
        )
        st.plotly_chart(profit_map)

        # Revenue by state
        revenue_map = px.choropleth(
            df,
            locations="STATE",
            locationmode="USA-states",
            color="REVENUES",
            scope="usa",
            title="Revenue by State (In Millions)",
        )
        st.plotly_chart(revenue_map)

        # Companies by state
        companies_map = px.choropleth(
            df.groupby("STATE").size().reset_index(name="COMPANIES"),
            locations="STATE",
            locationmode="USA-states",
            color="COMPANIES",
            scope="usa",
            title="Companies by State",
        )
        st.plotly_chart(companies_map)

    # Tab 2: Company Map
    with tab2:
        st.subheader("Company Headquarters Map")
        state_filter = st.selectbox("Filter by State", options=["All"] + df['STATE'].dropna().unique().tolist())
        filtered_df = df if state_filter == "All" else df[df['STATE'] == state_filter]

        # Static map layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position=["LONGITUDE", "LATITUDE"],
            get_radius=20000,
            get_color=[255, 0, 0],
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=37.7749, longitude=-95.7129, zoom=3)
        map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME}"})
        st.pydeck_chart(map_fig)

    # Tab 3: Company Comparison
    with tab3:
        st.subheader("Company Comparison")
        company_selection = st.multiselect("Select Companies", df['NAME'].dropna().unique())
        comparison_df = df[df['NAME'].isin(company_selection)]

        for _, row in comparison_df.iterrows():
            st.markdown(f"### {row['NAME']}")
            st.write(f"**Revenue**: ${row['REVENUES']:,.2f} (In Millions)")
            st.write(f"**Profit**: ${row['PROFIT']:,.2f} (In Millions)")
            st.write(f"[Website]({row['WEBSITE']})")

    # Tab 4: Interactive Insights
    with tab4:
        st.subheader("Interactive Insights")
        metric = st.selectbox("Choose Metric", ["Revenue", "Profit"])
        sorted_df = df.sort_values(metric.upper(), ascending=False)
        top_n = st.slider(f"Number of Companies by {metric}", min_value=1, max_value=len(sorted_df), value=10)
        bar_fig = px.bar(
            sorted_df.head(top_n),
            x="NAME",
            y=metric.upper(),
            title=f"Top {top_n} Companies by {metric} (In Millions)",
            text_auto=True,
        )
        bar_fig.update_traces(textposition="outside")
        st.plotly_chart(bar_fig)

except Exception as e:
    st.error(f"An error occurred: {e}")
