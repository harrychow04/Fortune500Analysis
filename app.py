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
import io

# Set Page Configuration
st.set_page_config(page_title="Fortune 500 Data Explorer", layout="wide")

# [DA1] Load and Clean the Data
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)

        # Clean column names
        df.columns = df.columns.str.strip()

        # Ensure financial and numeric columns are cleaned
        if 'REVENUES' in df and df['REVENUES'].dtype == 'object':
            df['REVENUES'] = pd.to_numeric(df['REVENUES'].str.replace(',', ''), errors='coerce').fillna(0)
        if 'PROFIT' in df and df['PROFIT'].dtype == 'object':
            df['PROFIT'] = pd.to_numeric(df['PROFIT'].str.replace(',', ''), errors='coerce').fillna(0)
        if 'EMPLOYEES' in df and df['EMPLOYEES'].dtype == 'object':
            df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'].str.replace(',', ''), errors='coerce').fillna(0)

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the dataset
file_path = 'Fortune 500 Corporate Headquarters.csv'
df = load_data(file_path)

# [DA2] Calculate Summary Metrics
def calculate_summary(df):
    if df.empty:
        return 0, 0
    total_revenue = df['REVENUES'].sum()
    total_employees = df['EMPLOYEES'].sum()
    return total_revenue, total_employees

# Add the Logo
st.image("logo.png", width=150)

# [DA3] Tabs for Navigation
st.title("Fortune 500 Data Explorer")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Dashboard Overview", "State Comparison", "Company Map", 
    "Company Comparison", "Interactive Insights", "Export Data"
])

# [DA4] Dashboard Overview
with tab1:
    st.subheader("Dashboard Overview")

    # Summary Cards
    st.metric(label="Total Companies", value=f"{df['NAME'].nunique()}")
    st.metric(label="Total Revenue (In Millions)", value=f"${df['REVENUES'].sum():,.2f}")
    st.metric(label="Total Employees", value=f"{df['EMPLOYEES'].sum():,}")

    # AI-Generated Insights
    st.write("### AI-Generated Insights")
    try:
        top_state = df.groupby('STATE')['REVENUES'].sum().idxmax()
        top_company = df.loc[df['REVENUES'].idxmax()]
        st.write(f"📊 The state with the highest total revenue is **{top_state}**.")
        st.write(f"🏢 The company with the highest revenue is **{top_company['NAME']}**, "
                 f"generating ${top_company['REVENUES']:,.2f} in revenue.")
    except Exception as e:
        st.error("Unable to generate insights.")

# [DA5] State Comparison Tab
with tab2:
    st.subheader("State Comparison")

    # Heatmap Filters
    min_profit = st.slider("Minimum Profit for Heatmap (In Millions)", min_value=0, max_value=int(df['PROFIT'].max()), step=100)
    filtered_df = df[df['PROFIT'] >= min_profit]

    # Heatmap: Profit by State
    try:
        profit_map = px.choropleth(
            filtered_df, 
            locations="STATE", 
            locationmode="USA-states", 
            color="PROFIT", 
            scope="usa", 
            title=f"Profit by State (Min: {min_profit})"
        )
        st.plotly_chart(profit_map, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# [DA6] Company Map Tab
with tab3:
    st.subheader("Company Headquarters Map")

    # State Filter
    state_filter = st.selectbox("Filter by State", options=["All States"] + sorted(df['STATE'].unique()))
    filtered_df = df if state_filter == "All States" else df[df['STATE'] == state_filter]

    # Display Map
    try:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position=["LONGITUDE", "LATITUDE"],
            get_radius=st.slider("Dot Size", min_value=1000, max_value=50000, value=30000),
            get_color=[255, 0, 0],
            pickable=True
        )
        view_state = pdk.ViewState(latitude=37.7749, longitude=-95.7129, zoom=3)
        map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state)
        st.pydeck_chart(map_fig)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# [DA7] Company Comparison Tab
with tab4:
    st.subheader("Company Comparison")
    selected_companies = st.multiselect("Select Companies", options=df['NAME'].unique())
    comparison_df = df[df['NAME'].isin(selected_companies)]
    for _, row in comparison_df.iterrows():
        st.write(f"### {row['NAME']}")
        st.write(f"Revenue: ${row['REVENUES']:,} (In Millions)")
        st.write(f"Profit: ${row['PROFIT']:,} (In Millions)")
        st.write(f"[Website]({row['WEBSITE']})")
        st.write("---")

# [DA8] Interactive Insights Tab
with tab5:
    st.subheader("Interactive Insights")
    metric = st.selectbox("Choose Metric", options=["REVENUES", "PROFIT", "EMPLOYEES"])
    threshold = st.slider(f"Minimum {metric} (In Millions)", min_value=0, max_value=int(df[metric].max()), step=1000)
    filtered_insights = df[df[metric] >= threshold].sort_values(by=metric, ascending=False)
    fig = px.bar(
        filtered_insights, 
        x="NAME", 
        y=metric, 
        title=f"{metric.capitalize()} of Filtered Companies (In Millions)",
        labels={metric: f"{metric.capitalize()} (In Millions)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# [DA9] Export Data Tab
with tab6:
    st.subheader("Export Data")
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    st.download_button("Download Full Dataset", data=buffer.getvalue(), file_name="fortune500_data.csv", mime="text/csv")
