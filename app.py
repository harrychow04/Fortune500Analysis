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

# [DA1] Load and Clean Data
@st.cache_data
def load_and_clean_data(filepath):
    try:
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()  # Remove extra spaces in column names

        # Check if required columns are present
        required_columns = ['STATE', 'REVENUES', 'EMPLOYEES', 'PROFIT', 'LONGITUDE', 'LATITUDE', 'NAME', 'WEBSITE']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"The following required columns are missing: {', '.join(missing_columns)}")
            return pd.DataFrame()

        # Convert relevant columns to appropriate types
        df['STATE'] = df['STATE'].astype(str)
        df['REVENUES'] = pd.to_numeric(df['REVENUES'].replace({',': ''}, regex=True), errors='coerce').fillna(0)
        df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'].replace({',': ''}, regex=True), errors='coerce').fillna(0)
        df['PROFIT'] = pd.to_numeric(df['PROFIT'].replace({',': ''}, regex=True), errors='coerce').fillna(0)
        df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
        df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# [PY1] Filter Data by State
def filter_data(df, state=None, min_employees=0):
    filtered_df = df[df['EMPLOYEES'] >= min_employees]
    if state and state != "All States":
        filtered_df = filtered_df[filtered_df['STATE'] == state]
    return filtered_df

# [PY2] Calculate Summary Metrics
def calculate_summary(df):
    if df.empty:
        return 0, 0  # Handle empty data
    total_revenue = df['REVENUES'].sum()
    total_employees = df['EMPLOYEES'].sum()
    return total_revenue, total_employees

# [PY3] Add Error Handling for Filtering or Analysis
def safe_filter(df, state):
    try:
        return filter_data(df, state)
    except Exception as e:
        st.error(f"Error filtering data: {e}")
        return pd.DataFrame()

# Load Data
data_file = 'Fortune 500 Corporate Headquarters.csv'
df = load_and_clean_data(data_file)

if not df.empty:
    # Sidebar with logo and description
    st.sidebar.image("logo.png", caption=None)
    st.sidebar.markdown(
        "Explore Fortune 500 companies through state comparisons, company maps, and custom insights."
    )

    # Streamlit Tabs
    st.title("Fortune 500 Data Explorer")
    tab1, tab2, tab3, tab4 = st.tabs(["State Comparison", "Company Map", "Company Comparison", "Interactive Insights"])

    # Tab 1: State Comparison
    with tab1:
        st.subheader("State Comparison")

        # Filters
        state_list = ["All States"] + sorted(df['STATE'].unique())
        selected_state = st.sidebar.selectbox("Select State", state_list)

        filtered_df = df if selected_state == "All States" else df[df['STATE'] == selected_state]

        # Calculate Summary Metrics
        total_revenue, total_employees = calculate_summary(filtered_df)
        st.write(f"**Total Revenue**: ${total_revenue:,.0f}")
        st.write(f"**Total Employees**: {total_employees:,}")

        # Revenue vs Employees Scatter Plot
        st.subheader("Revenue vs Employees")
        fig1 = px.scatter(
            filtered_df,
            x='EMPLOYEES',
            y='REVENUES',
            hover_data=['NAME', 'CITY'],
            title="Company Revenue vs Employees",
            labels={'EMPLOYEES': 'Employees', 'REVENUES': 'Revenue'},
        )
        st.plotly_chart(fig1)

        # Heatmaps
        st.subheader("Heatmaps")
        profit_by_state = filtered_df.groupby('STATE')['PROFIT'].sum().reset_index()
        fig2 = px.choropleth(
            profit_by_state,
            locations='STATE',
            locationmode='USA-states',
            color='PROFIT',
            title="Profit by State",
            scope="usa",
            color_continuous_scale="reds"
        )
        st.plotly_chart(fig2)

        revenue_by_state = filtered_df.groupby('STATE')['REVENUES'].sum().reset_index()
        fig3 = px.choropleth(
            revenue_by_state,
            locations='STATE',
            locationmode='USA-states',
            color='REVENUES',
            title="Revenue by State",
            scope="usa",
            color_continuous_scale="blues"
        )
        st.plotly_chart(fig3)

    # Tab 2: Company Map
    with tab2:
        st.subheader("Company Headquarters Map")
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["LONGITUDE", "LATITUDE"],
            get_radius=30000,
            get_color=[255, 0, 0],
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=3)
        map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state)
        st.pydeck_chart(map_fig)

    # Tab 3: Company Comparison
    with tab3:
        st.subheader("Company Comparison")

        # Select Companies
        company_list = df['NAME'].unique()
        company1 = st.selectbox("Select First Company", company_list)
        company2 = st.selectbox("Select Second Company", company_list)

        comp1 = df[df['NAME'] == company1].iloc[0]
        comp2 = df[df['NAME'] == company2].iloc[0]

        # Display Comparison
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"### {company1}")
            st.write(f"**Revenue**: ${comp1['REVENUES']:,.0f}")
            st.write(f"**Profit**: ${comp1['PROFIT']:,.0f}")
            st.write(f"[Website]({comp1['WEBSITE']})")

        with col2:
            st.write(f"### {company2}")
            st.write(f"**Revenue**: ${comp2['REVENUES']:,.0f}")
            st.write(f"**Profit**: ${comp2['PROFIT']:,.0f}")
            st.write(f"[Website]({comp2['WEBSITE']})")

    # Tab 4: Interactive Insights
    with tab4:
        st.subheader("Interactive Insights")
        metric = st.selectbox("Choose Metric", ['Revenue', 'Profit'])
        threshold = st.slider(f"Minimum {metric}", min_value=0, max_value=int(df[metric.upper()].max()), step=1000)

        filtered_insights = df[df[metric.upper()] >= threshold]
        fig4 = px.bar(
            filtered_insights,
            x="NAME",
            y=metric.upper(),
            title=f"Companies with {metric} above {threshold}",
            labels={metric.upper(): f"{metric} Amount"}
        )
        st.plotly_chart(fig4)
else:
    st.error("No data available to display.")
