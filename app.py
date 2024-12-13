"""
Name:       Harry Chow
CS230:      Section 2
Data:       https://www.kaggle.com/datasets/mannmann2/fortune-500-corporate-headquarters
URL:        https://fortune500analysis.streamlit.app/
Github URL: https://github.com/harrychow04/Fortune500Analysis

Description:
This app allows users to explore data on Fortune 500 companies through state comparisons and detailed company comparisons. Gain insights into revenue, profits, and employee distribution.
"""

import streamlit as st
st.set_page_config(page_title="Fortune 500 Data Explorer", layout="wide")

import pandas as pd
import pydeck as pdk
import plotly.express as px
import io

#[DA1] Load and Clean the Data
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)

        #Clean column names
        df.columns = df.columns.str.strip()

        #Ensure financial and numeric columns are cleaned
        if 'REVENUES' in df and df['REVENUES'].dtype == 'object':
            df['REVENUES'] = pd.to_numeric(df['REVENUES'].str.replace(',', ''), errors='coerce').fillna(0)
        if 'PROFIT' in df and df['PROFIT'].dtype == 'object':
            df['PROFIT'] = pd.to_numeric(df['PROFIT'].str.replace(',', ''), errors='coerce').fillna(0)
        if 'EMPLOYEES' in df and df['EMPLOYEES'].dtype == 'object':
            df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'].str.replace(',', ''), errors='coerce').fillna(0)

        #Add a calculated column for revenue per employee
        df['REVENUE_PER_EMPLOYEE'] = (df['REVENUES'] / df['EMPLOYEES']).fillna(0)  # [DA9] New Column
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

#Load the dataset
file_path = 'Fortune 500 Corporate Headquarters.csv'
df = load_data(file_path)

#[DA2] Calculate Summary Metrics
def calculate_summary(df):
    if df.empty:
        return 0, 0
    total_revenue = df['REVENUES'].sum()
    total_employees = df['EMPLOYEES'].sum()
    return total_revenue, total_employees

#Logo
st.image("logo.png", width=150)

#[DA3] Tabs for Navigation
st.title("Fortune 500 Data Explorer")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Dashboard Overview", "State Comparison", "Company Map", 
    "Company Comparison", "Interactive Insights", "Export Data"
])

#[DA4] Dashboard Overview
with tab1:
    st.subheader("Dashboard Overview")

    #Summary Cards
    st.metric(label="Total Companies", value=f"{df['NAME'].nunique()}")
    st.metric(label="Total Revenue (In Millions)", value=f"${df['REVENUES'].sum():,.2f}")
    st.metric(label="Total Employees", value=f"{df['EMPLOYEES'].sum():,}")

    #Financial Overview
    st.write("### Financial Overview")
    try:
        top_state = df.groupby('STATE')['REVENUES'].sum().idxmax()
        top_company = df.loc[df['REVENUES'].idxmax()]
        st.write(f"📊 The state with the highest total revenue is **{top_state}**.")
        st.write(f"🏢 The company with the highest revenue is **{top_company['NAME']}**, "
                 f"generating ${top_company['REVENUES']:,.2f} in revenue.")
    except Exception as e:
        st.error("Unable to generate insights.")

#[DA5] State Comparison Tab
with tab2:
    st.subheader("State Comparison")

    #Aggregated Data for Heatmaps
    state_aggregates = df.groupby('STATE')[['REVENUES', 'PROFIT', 'EMPLOYEES']].sum().reset_index()

    #Revenue Heatmap
    st.write("### Revenue by State (In Millions)")
    revenue_map = px.choropleth(
        state_aggregates, 
        locations="STATE", 
        locationmode="USA-states", 
        color="REVENUES", 
        scope="usa", 
        color_continuous_scale="Viridis",
        title="Revenue by State (In Millions)",
        labels={"REVENUES": "Revenue (In Millions)"},
        range_color=(0, state_aggregates["REVENUES"].max())
    )
    st.plotly_chart(revenue_map, use_container_width=True)

    #Employees Heatmap
    st.write("### Employees by State")
    employee_map = px.choropleth(
        state_aggregates, 
        locations="STATE", 
        locationmode="USA-states", 
        color="EMPLOYEES", 
        scope="usa", 
        color_continuous_scale="Plasma",
        title="Employees by State",
        labels={"EMPLOYEES": "Employees"},
        range_color=(0, state_aggregates["EMPLOYEES"].max())
    )
    st.plotly_chart(employee_map, use_container_width=True)

    #Profit Heatmap
    st.write("### Profit by State (In Millions)")
    profit_map = px.choropleth(
        state_aggregates, 
        locations="STATE", 
        locationmode="USA-states", 
        color="PROFIT", 
        scope="usa", 
        color_continuous_scale="Cividis",
        title="Profit by State (In Millions)",
        labels={"PROFIT": "Profit (In Millions)"},
        range_color=(0, state_aggregates["PROFIT"].max())
    )
    st.plotly_chart(profit_map, use_container_width=True)

# [DA6] Company Map Tab
with tab3:
    st.subheader("Company Headquarters Map")

    # State Filter
    state_filter = st.selectbox("Filter by State", options=["All States"] + sorted(df['STATE'].unique()))
    filtered_df = df if state_filter == "All States" else df[df['STATE'] == state_filter]

    # Toggle for revenue-based colorization
    color_toggle = st.checkbox("Colorize by Revenue")

    # Determine dot colors
    if color_toggle:
        # Map revenue values to a gradient scale
        max_revenue = filtered_df['REVENUE'].max()
        min_revenue = filtered_df['REVENUE'].min()
        filtered_df['COLOR'] = filtered_df['REVENUE'].apply(
            lambda rev: [255, int(255 * (rev - min_revenue) / (max_revenue - min_revenue)), 0]
        )
    else:
        # Default color (red)
        filtered_df['COLOR'] = [[255, 0, 0] for _ in range(len(filtered_df))]

    # Display Map
    try:
        # Create a tooltip to display company name and full address (Street, City, State)
        tooltip = {
            "html": """
                <b>Company:</b> {NAME}<br>
                <b>Address:</b> {ADDRESS}, {CITY}, {STATE}<br>
                <b>Revenue:</b> {REVENUE}
            """,
            "style": {
                "backgroundColor": "steelblue",
                "color": "white",
                "fontSize": "12px",
                "borderRadius": "5px",
                "padding": "5px",
            }
        }

        # Scatterplot Layer for the map
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position=["LONGITUDE", "LATITUDE"],
            get_radius=st.slider("Dot Size", min_value=1000, max_value=50000, value=30000),
            get_fill_color="COLOR",
            pickable=True
        )

        # Configure the map's view state
        view_state = pdk.ViewState(latitude=37.7749, longitude=-95.7129, zoom=3)

        # Render the map with tooltips
        map_fig = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        )
        st.pydeck_chart(map_fig)
    except Exception as e:
        st.error(f"An error occurred: {e}")

#[DA7] Company Comparison Tab
with tab4:
    st.subheader("Company Comparison")
    selected_companies = st.multiselect("Select Companies", options=df['NAME'].unique())
    comparison_df = df[df['NAME'].isin(selected_companies)]
    for _, row in comparison_df.iterrows():
        st.write(f"### {row['NAME']}")
        st.write(f"Revenue: ${row['REVENUES']:,} (In Millions)")
        st.write(f"Profit: ${row['PROFIT']:,} (In Millions)")
        st.write(f"Headquarters: {row['CITY']}, {row['STATE']}")
        st.write(f"[Website]({row['WEBSITE']})")
        st.write("---")

# [DA8] Interactive Insights Tab
with tab5:
    st.subheader("Investment Insights")

    # Select Metric and Set Threshold
    metric = st.selectbox("Choose a Metric to Analyze", options=["REVENUES", "PROFIT", "EMPLOYEES"])
    threshold = st.slider(
        f"Filter Companies by Minimum {metric.capitalize()}",
        min_value=0, max_value=int(df[metric].max()), step=1000,
        value=int(df[metric].mean())  # Default to the average
    )

    # Filter Companies Based on Metric and Threshold
    filtered_insights = df[df[metric] >= threshold].sort_values(by=metric, ascending=False)

    if not filtered_insights.empty:
        # Key Metrics Section
        st.write(f"### Key Insights for {metric.capitalize()}")
        top_company = filtered_insights.iloc[0]
        average_metric = filtered_insights[metric].mean()

        # Format values based on metric type
        if metric == "EMPLOYEES":
            metric_format = "{:,}"  # Comma-separated integers for employees
            metric_unit = "Employees"
        else:
            metric_format = "${:,.2f}"  # Monetary values for revenues and profit
            metric_unit = "USD"

        st.write(f"- 🏆 **Top Company**: {top_company['NAME']} with {metric.capitalize()} = {metric_format.format(top_company[metric])}.")
        st.write(f"- 📊 **Average {metric.capitalize()}** across selected companies: {metric_format.format(average_metric)}.")
        st.write(f"- 🔢 **Total Companies Above Threshold**: {len(filtered_insights)}.")

        # Display Top Companies
        top_n = st.slider("Show Top N Companies", min_value=5, max_value=20, step=1, value=10)
        st.write(f"### Top {top_n} Companies by {metric.capitalize()}")
        st.table(filtered_insights.head(top_n)[['NAME', metric]])

        # Scatterplot Visualization
        comparison_metric = st.selectbox(
            "Compare Against Another Metric", options=["REVENUES", "PROFIT", "EMPLOYEES"]
        )
        st.write(f"### {metric.capitalize()} vs. {comparison_metric.capitalize()} (Scatterplot)")

        # Ensure proper formatting for scatterplot based on numeric values
        fig_scatter = px.scatter(
            filtered_insights, 
            x=metric, 
            y=comparison_metric, 
            hover_name="NAME",
            title=f"{metric.capitalize()} vs {comparison_metric.capitalize()}",
            labels={
                metric: metric.capitalize(),
                comparison_metric: comparison_metric.capitalize(),
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Revenue Per Employee Analysis (only for REVENUES)
        if metric == "REVENUES":
            st.write("### Companies with the Highest Revenue per Employee")
            top_rpe = filtered_insights.nlargest(10, 'REVENUE_PER_EMPLOYEE')[['NAME', 'REVENUE_PER_EMPLOYEE']]
            st.table(top_rpe)

        # Financial News Links
        st.write("### Explore More Financial Insights")
        st.markdown("""
        - [Yahoo Finance](https://finance.yahoo.com)
        - [Bloomberg](https://www.bloomberg.com)
        - [Google Finance](https://www.google.com/finance)
        """)

        # Recommendations Section
        st.write("### Recommendations")
        st.write(f"- Focus on companies with {metric.capitalize()} above {metric_format.format(threshold)}.")
        if metric == "REVENUES" and 'REVENUE_PER_EMPLOYEE' in df.columns:
            st.write("- Prioritize companies with high revenue per employee for better operational efficiency.")
    else:
        st.write(f"No companies match the criteria of {metric.capitalize()} above {threshold:,}.")
        st.write(f"No companies match the selected criteria of {metric.capitalize()} above {threshold:,}.")

#[DA9] Export Data Tab
with tab6:
    st.subheader("Export Data")
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    st.download_button("Download Full Dataset", data=buffer.getvalue(), file_name="fortune500_data.csv", mime="text/csv")
