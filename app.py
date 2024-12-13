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

# Add logo
st.sidebar.image("logo.png", width=150)
st.title("Fortune 500 Data Explorer")

@st.cache_data
def load_and_clean_data(filepath):
    try:
        df = pd.read_csv(filepath)
        df['REVENUES'] = df['REVENUES'].str.replace(',', '').astype(float)
        df['PROFIT'] = df['PROFIT'].str.replace(',', '').astype(float)
        df['EMPLOYEES'] = df['EMPLOYEES'].str.replace(',', '').astype(int)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
data_file = 'Fortune 500 Corporate Headquarters.csv'
df = load_and_clean_data(data_file)

# Tabs for each section
tab1, tab2, tab3, tab4 = st.tabs(["State Comparison", "Company Map", "Company Comparison", "Interactive Insights"])

with tab1:
    st.header("State Comparison")
    total_revenue = df['REVENUES'].sum()
    total_employees = df['EMPLOYEES'].sum()
    st.write(f"**Total Revenue**: ${total_revenue:,.2f} (In Millions)")
    st.write(f"**Total Employees**: {total_employees:,}")
    
    st.subheader("Heatmaps")
    # Profit by State Heatmap
    st.caption("This heatmap shows the total profit by state (In Millions).")
    profit_map = px.choropleth(df, locations="STATE", color="PROFIT", 
                               locationmode="USA-states", scope="usa", 
                               color_continuous_scale="Greens",
                               title="Profit by State (In Millions)")
    st.plotly_chart(profit_map)

    # Revenue by State Heatmap
    st.caption("This heatmap shows the total revenue by state (In Millions).")
    revenue_map = px.choropleth(df, locations="STATE", color="REVENUES", 
                                locationmode="USA-states", scope="usa", 
                                color_continuous_scale="Purples",
                                title="Revenue by State (In Millions)")
    st.plotly_chart(revenue_map)

    # Headquarters per State Heatmap
    st.caption("This heatmap shows the number of company headquarters per state.")
    df_hq_count = df.groupby('STATE').size().reset_index(name='HEADQUARTERS_COUNT')
    hq_map = px.choropleth(df_hq_count, locations="STATE", color="HEADQUARTERS_COUNT", 
                           locationmode="USA-states", scope="usa", 
                           color_continuous_scale="Blues",
                           title="Headquarters per State")
    st.plotly_chart(hq_map)

with tab2:
    st.header("Company Map")
    state_filter = st.selectbox("Filter by State", options=["All States"] + sorted(df['STATE'].unique()))
    filtered_df = df if state_filter == "All States" else df[df['STATE'] == state_filter]
    st.map(filtered_df[['LATITUDE', 'LONGITUDE']])

with tab3:
    st.header("Company Comparison")
    selected_companies = st.multiselect("Select Companies", options=df['NAME'].unique())
    if selected_companies:
        comparison_data = df[df['NAME'].isin(selected_companies)]
        for _, row in comparison_data.iterrows():
            st.subheader(row['NAME'])
            st.write(f"Revenue: ${row['REVENUES']:,.2f} (In Millions)")
            st.write(f"Profit: ${row['PROFIT']:,.2f} (In Millions)")
            st.write(f"Website: [Link]({row['WEBSITE']})")

with tab4:
    st.header("Interactive Insights")
    metric = st.selectbox("Choose Metric", options=["REVENUES", "PROFIT", "EMPLOYEES"])
    threshold = st.slider(f"Minimum {metric} (In Millions)", 
                          min_value=int(df[metric].min()), 
                          max_value=int(df[metric].max()), 
                          step=1000)
    filtered_insights = df[df[metric] >= threshold]
    sorted_insights = filtered_insights.sort_values(by=metric, ascending=False)
    fig = px.bar(sorted_insights, x="NAME", y=metric, 
                 title=f"{metric} of Filtered Companies (In Millions)", 
                 labels={metric: f"{metric} (In Millions)", "NAME": "Company Name"})
    st.plotly_chart(fig)
