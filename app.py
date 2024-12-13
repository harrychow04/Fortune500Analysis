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
import pydeck as pdk
import plotly.express as px
import io

# Set Page Config
st.set_page_config(page_title="Fortune 500 Data Explorer", layout="wide")

# Load Data
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        df['REVENUES'] = pd.to_numeric(df['REVENUES'].str.replace(',', ''), errors='coerce').fillna(0)
        df['PROFIT'] = pd.to_numeric(df['PROFIT'].str.replace(',', ''), errors='coerce').fillna(0)
        df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'].str.replace(',', ''), errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load dataset
file_path = 'Fortune 500 Corporate Headquarters.csv'
df = load_data(file_path)

# Add Logo
st.sidebar.image("logo.png", use_column_width=True)

# Sidebar Navigation
menu = st.sidebar.radio(
    "Navigation", 
    ["Dashboard Overview", "State Comparison", "Company Map", "Company Comparison", "Interactive Insights", "Export Data"]
)

# Dashboard Overview
if menu == "Dashboard Overview":
    st.title("Fortune 500 Data Explorer")
    st.subheader("Dashboard Overview")
    st.metric("Total Companies", value=f"{df['NAME'].nunique()}")
    st.metric("Total Revenue (In Millions)", value=f"${df['REVENUES'].sum():,.2f}")
    st.metric("Total Employees", value=f"{df['EMPLOYEES'].sum():,}")

    # AI Insights
    st.write("### AI-Generated Insights")
    try:
        top_state = df.groupby('STATE')['REVENUES'].sum().idxmax()
        top_company = df.loc[df['REVENUES'].idxmax()]
        st.write(f"📊 The state with the highest total revenue is **{top_state}**.")
        st.write(f"🏢 The company with the highest revenue is **{top_company['NAME']}**, generating ${top_company['REVENUES']:,.2f}.")
    except Exception:
        st.error("Unable to generate insights.")

# State Comparison
elif menu == "State Comparison":
    st.title("State Comparison")
    st.write("### Profit by State (In Millions)")
    profit_map = px.choropleth(
        df, 
        locations="STATE", 
        locationmode="USA-states", 
        color="PROFIT", 
        scope="usa", 
        labels={"PROFIT": "Profit (In Millions)"},
    )
    st.plotly_chart(profit_map, use_container_width=True)
    st.caption("This heatmap displays profits by state.")

    st.write("### Revenue by State (In Millions)")
    revenue_map = px.choropleth(
        df, 
        locations="STATE", 
        locationmode="USA-states", 
        color="REVENUES", 
        scope="usa", 
        labels={"REVENUES": "Revenue (In Millions)"},
    )
    st.plotly_chart(revenue_map, use_container_width=True)
    st.caption("This heatmap shows total revenue by state.")

# Company Map
elif menu == "Company Map":
    st.title("Company Headquarters Map")
    state_filter = st.selectbox("Filter by State", options=["All States"] + sorted(df['STATE'].unique()))
    filtered_df = df if state_filter == "All States" else df[df['STATE'] == state_filter]
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

# Company Comparison
elif menu == "Company Comparison":
    st.title("Company Comparison")
    selected_companies = st.multiselect("Select Companies", options=df['NAME'].unique())
    comparison_df = df[df['NAME'].isin(selected_companies)]
    for _, row in comparison_df.iterrows():
        st.write(f"### {row['NAME']}")
        st.write(f"Revenue: ${row['REVENUES']:,} (In Millions)")
        st.write(f"Profit: ${row['PROFIT']:,} (In Millions)")
        st.write("---")

# Interactive Insights
elif menu == "Interactive Insights":
    st.title("Interactive Insights")
    metric = st.selectbox("Choose Metric", options=["REVENUES", "PROFIT", "EMPLOYEES"])
    threshold = st.slider(f"Minimum {metric} (In Millions)", min_value=0, max_value=int(df[metric].max()), step=1000)
    filtered_insights = df[df[metric] >= threshold].sort_values(by=metric, ascending=False)
    fig = px.bar(
        filtered_insights, 
        x="NAME", 
        y=metric, 
        title=f"{metric.capitalize()} of Filtered Companies (In Millions)",
        labels={metric: f"{metric.capitalize()} (In Millions)"},
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write("### Top 5 Companies")
    st.write(filtered_insights.head(5)[["NAME", metric]])

# Export Data
elif menu == "Export Data":
    st.title("Export Data")
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    st.download_button("Download Full Dataset", data=buffer.getvalue(), file_name="fortune500_data.csv", mime="text/csv")
