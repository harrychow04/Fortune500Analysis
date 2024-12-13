"""
Name:       Harry Chow
CS230:      Section 2
Data:       https://www.kaggle.com/datasets/mannmann2/fortune-500-corporate-headquarters
URL:        Link to your web application on Streamlit Cloud (if posted) 

Description:    
This app allows users to explore data on Fortune 500 companies through state comparisons and detailed company comparisons. Gain insights into revenue, profits, and employee distribution.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# [DA1] Set page configuration
st.set_page_config(page_title="Fortune 500 Data Explorer", layout="wide")

# [DA2] Load and Clean Data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # Clean column names
    df['REVENUES'] = pd.to_numeric(df['REVENUES'], errors='coerce').fillna(0)
    df['PROFIT'] = pd.to_numeric(df['PROFIT'], errors='coerce').fillna(0)
    df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'], errors='coerce').fillna(0)
    return df

file_path = "Fortune 500 Corporate Headquarters.csv"
df = load_data(file_path)

# [DA3] Add logo
st.image("logo.png", width=200)
st.title("Fortune 500 Data Explorer")

# [DA4] Dashboard Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Dashboard Overview", "State Comparison", "Company Map", 
    "Company Comparison", "Interactive Insights", "Export Data"
])

# [DA5] Dashboard Overview
with tab1:
    st.subheader("Dashboard Overview")
    st.metric("Total Companies", value=f"{df.shape[0]}")
    st.metric("Total Revenue (In Millions)", value=f"${df['REVENUES'].sum():,.2f}")
    st.metric("Total Employees", value=f"{df['EMPLOYEES'].sum():,}")

# [DA6] State Comparison Tab
with tab2:
    st.subheader("State Comparison")

    # Revenue Heatmap
    st.write("### Revenue by State (In Millions)")
    max_revenue = df['REVENUES'].max()
    revenue_map = px.choropleth(
        df, locations='STATE', locationmode="USA-states", color='REVENUES',
        scope="usa", color_continuous_scale="Viridis",
        title="Revenue Distribution by State",
        range_color=(0, 100000),  # Adjusted range for better contrast
    )
    st.plotly_chart(revenue_map, use_container_width=True)

    # Employees Heatmap
    st.write("### Employees by State")
    max_employees = df['EMPLOYEES'].max()
    employees_map = px.choropleth(
        df, locations='STATE', locationmode="USA-states", color='EMPLOYEES',
        scope="usa", color_continuous_scale="Plasma",
        title="Employees Distribution by State",
        range_color=(0, 100000),  # Adjusted range for better contrast
    )
    st.plotly_chart(employees_map, use_container_width=True)

    # Profit Heatmap
    st.write("### Profit by State (In Millions)")
    max_profit = df['PROFIT'].max()
    profit_map = px.choropleth(
        df, locations='STATE', locationmode="USA-states", color='PROFIT',
        scope="usa", color_continuous_scale="Cividis",
        title="Profit Distribution by State",
        range_color=(0, 100000),  # Adjusted range for better contrast
    )
    st.plotly_chart(profit_map, use_container_width=True)

    # Top 5 States by Metrics
    st.write("### Top 5 States by Metric")
    metrics = ['REVENUES', 'EMPLOYEES', 'PROFIT']
    for metric in metrics:
        st.write(f"#### Top 5 States by {metric.capitalize()}:")
        top_states = df.groupby('STATE')[metric].sum().nlargest(5)
        st.table(top_states)

# [DA7] Company Map Tab
with tab3:
    st.subheader("Company Headquarters Map")
    state_filter = st.selectbox("Filter by State", options=["All States"] + sorted(df['STATE'].unique()))
    filtered_df = df if state_filter == "All States" else df[df['STATE'] == state_filter]

    # Interactive Map
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
        map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME}"})
        st.pydeck_chart(map_fig)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# [DA8] Company Comparison Tab
with tab4:
    st.subheader("Company Comparison")
    selected_companies = st.multiselect("Select Companies", options=df['NAME'].unique())
    comparison_df = df[df['NAME'].isin(selected_companies)]
    for _, row in comparison_df.iterrows():
        st.write(f"### {row['NAME']}")
        st.write(f"Revenue: ${row['REVENUES']:,.2f} (In Millions)")
        st.write(f"Profit: ${row['PROFIT']:,.2f} (In Millions)")
        st.write(f"[Website]({row['WEBSITE']})")
        st.write("---")

# [DA9] Interactive Insights Tab
with tab5:
    st.subheader("Interactive Insights")
    metric = st.selectbox("Choose Metric", options=["REVENUES", "PROFIT", "EMPLOYEES"])
    threshold = st.slider(f"Minimum {metric} (In Millions)" if metric != "EMPLOYEES" else f"Minimum {metric}",
                          min_value=0, max_value=int(df[metric].max()), step=1000)
    filtered_insights = df[df[metric] >= threshold].sort_values(by=metric, ascending=False)
    fig = px.bar(
        filtered_insights, 
        x="NAME", 
        y=metric, 
        title=f"{metric.capitalize()} of Filtered Companies",
        labels={metric: f"{metric.capitalize()} (In Millions)" if metric != "EMPLOYEES" else metric.capitalize()},
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top 5 Companies
    st.write("### Top 5 Companies")
    top_5 = filtered_insights.nlargest(5, metric)
    for _, row in top_5.iterrows():
        st.write(f"- {row['NAME']} - {row[metric]:,.2f} (In Millions)" if metric != "EMPLOYEES" else f"- {row['NAME']} - {row[metric]:,}")

# [DA10] Export Data Tab
with tab6:
    st.subheader("Export Data")
    csv_data = df.to_csv(index=False)
    st.download_button("Download Data as CSV", data=csv_data, file_name="fortune500_data.csv", mime="text/csv")
