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

# [DA1] Load and clean the data
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df['REVENUES'] = pd.to_numeric(df['REVENUES'].str.replace(',', ''), errors='coerce').fillna(0)
        df['PROFIT'] = pd.to_numeric(df['PROFIT'].str.replace(',', ''), errors='coerce').fillna(0)
        df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'].str.replace(',', ''), errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# [DA2] Load the data
data_file = 'Fortune 500 Corporate Headquarters.csv'
df = load_data(data_file)

# [DA3] Title and logo
st.image("logo.png", use_column_width=True)
st.title("Fortune 500 Data Explorer")

# [VIS1] Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs(["State Comparison", "Company Map", "Company Comparison", "Interactive Insights"])

# [VIS2] State Comparison
with tab1:
    st.subheader("State Comparison")
    total_revenue = df['REVENUES'].sum()
    total_employees = df['EMPLOYEES'].sum()
    st.write(f"**Total Revenue**: ${total_revenue:,.2f} (In Millions)")
    st.write(f"**Total Employees**: {total_employees:,}")
    st.write("## Heatmaps")

    # [VIS2a] Profit by state
    profit_by_state = df.groupby('STATE')['PROFIT'].sum().reset_index()
    profit_map = px.choropleth(profit_by_state, locations='STATE', locationmode="USA-states",
                               color='PROFIT', scope="usa", title="Profit by State (In Millions)")
    st.plotly_chart(profit_map)
    st.caption("This heatmap visualizes the profit distribution of Fortune 500 companies by state.")

    # [VIS2b] Revenue by state
    revenue_by_state = df.groupby('STATE')['REVENUES'].sum().reset_index()
    revenue_map = px.choropleth(revenue_by_state, locations='STATE', locationmode="USA-states",
                                color='REVENUES', scope="usa", title="Revenue by State (In Millions)")
    st.plotly_chart(revenue_map)
    st.caption("This heatmap visualizes the revenue distribution of Fortune 500 companies by state.")

    # [VIS2c] Companies by state
    companies_by_state = df.groupby('STATE').size().reset_index(name='COUNT')
    company_map = px.choropleth(companies_by_state, locations='STATE', locationmode="USA-states",
                                color='COUNT', scope="usa", title="Companies by State")
    st.plotly_chart(company_map)
    st.caption("This heatmap visualizes the number of Fortune 500 company headquarters in each state.")

# [VIS3] Company Map
with tab2:
    st.subheader("Company Headquarters Map")
    st.write("View headquarters of Fortune 500 companies across the USA.")
    company_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius=30000,
        get_color=[255, 0, 0],
        pickable=True
    )
    view_state = pdk.ViewState(latitude=37.0902, longitude=-95.7129, zoom=3, pitch=0)
    company_map = pdk.Deck(layers=[company_layer], initial_view_state=view_state)
    st.pydeck_chart(company_map)

# [VIS4] Company Comparison
with tab3:
    st.subheader("Company Comparison")
    selected_companies = st.multiselect("Select Companies", df['NAME'].unique())
    if selected_companies:
        comparison_df = df[df['NAME'].isin(selected_companies)]
        for _, row in comparison_df.iterrows():
            st.write(f"### {row['NAME']}")
            st.write(f"Revenue: ${row['REVENUES']:.2f} (In Millions)")
            st.write(f"Profit: ${row['PROFIT']:.2f} (In Millions)")
            st.write(f"Website: [Link]({row['WEBSITE']})")

# [VIS5] Interactive Insights
with tab4:
    st.subheader("Interactive Insights")
    metric = st.selectbox("Choose Metric", ["REVENUES", "PROFIT", "EMPLOYEES"])
    threshold = st.slider(f"Minimum {metric}", min_value=0, max_value=int(df[metric].max()), step=1000)
    filtered_df = df[df[metric] >= threshold]
    sorted_df = filtered_df.sort_values(by=metric, ascending=False)
    bar_chart = px.bar(sorted_df, x="NAME", y=metric, title=f"{metric} of Filtered Companies (In Millions)")
    st.plotly_chart(bar_chart)
