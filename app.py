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

        # Ensure columns are strings before applying `.str.replace`
        if not df['REVENUES'].dtype == 'object':
            df['REVENUES'] = df['REVENUES'].astype(str)
        if not df['EMPLOYEES'].dtype == 'object':
            df['EMPLOYEES'] = df['EMPLOYEES'].astype(str)
        if not df['PROFIT'].dtype == 'object':
            df['PROFIT'] = df['PROFIT'].astype(str)
        
        # Convert REVENUES, EMPLOYEES, and PROFIT to numeric
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
        return 0, 0, 0
    total_revenue = df['REVENUES'].sum() / 1e3  # Convert to billions
    total_employees = df['EMPLOYEES'].sum()
    avg_revenue_per_employee = (
        (df['REVENUES'].sum() / total_employees) / 1e3  # Average Revenue per Employee in billions
        if total_employees > 0
        else 0
    )
    return total_revenue, total_employees, avg_revenue_per_employee

# Load data
data_file = 'Fortune 500 Corporate Headquarters.csv'
df = load_and_clean_data(data_file)

# Sidebar with logo and description
st.sidebar.image("logo.png", caption=None)
st.sidebar.markdown(
    "This app allows users to explore data on Fortune 500 companies through state comparisons and detailed company comparisons. Gain insights into revenue, profits, and employee distribution."
)

# Streamlit app with tabs
st.title("Fortune 500 Data Explorer")
tab1, tab2, tab3 = st.tabs(["State Comparison", "Company Map", "Company Comparison"])

# Tab 1: State Comparison
with tab1:
    st.subheader("State Comparison")
    
    # Filters
    state_list = ["All States"] + sorted(df['STATE'].unique())
    selected_states = st.sidebar.multiselect("Filter by States", state_list, default="All States")
    
    if "All States" in selected_states:
        filtered_df = df
    else:
        filtered_df = df[df['STATE'].isin(selected_states)]
    
    # Summary Metrics
    total_revenue, total_employees, avg_revenue_per_employee = calculate_summary(filtered_df)
    st.write(f"**Total Revenue**: ${total_revenue:,.2f} Billion")
    st.write(f"**Total Employees**: {total_employees:,}")
    st.write(f"**Average Revenue per Employee**: ${avg_revenue_per_employee:,.2f} Billion")
    
    # Scatter Plot: Revenue vs Employees
    st.subheader("Revenue vs Employees")
    fig1 = px.scatter(
        filtered_df,
        x='EMPLOYEES',
        y=filtered_df['REVENUES'] / 1e9,  # Convert to billions
        hover_data=['NAME', 'CITY'],
        title="Company Revenue vs Employees",
        labels={'EMPLOYEES': 'Employees', 'y': 'Revenues (in Billions)'},
    )
    st.plotly_chart(fig1)

    # Heatmaps
    st.subheader("Heatmaps")
    col1, col2, col3 = st.columns(3)
    
    # Profit by State
    with col1:
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

    # Revenue by State
    with col2:
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

    # Companies by State
    with col3:
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

# Tab 2: Company Map
with tab2:
    st.subheader("Company Headquarters Map")
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius=20000,
        get_color=[255, 0, 0],
        pickable=True,
    )
    view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=3)
    map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME}"})
    st.pydeck_chart(map_fig)

# Tab 3: Company Comparison
with tab3:
    st.subheader("Company Comparison")
    
    company_list = sorted(df['NAME'].unique())
    company1 = st.selectbox("Select First Company", company_list)
    company2 = st.selectbox("Select Second Company", company_list)
    
    # Fetch details for selected companies
    company_data1 = df[df['NAME'] == company1].iloc[0]
    company_data2 = df[df['NAME'] == company2].iloc[0]
    
    st.write("### Comparison Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**{company1}**")
        st.write(f"Revenue: ${company_data1['REVENUES'] / 1e9:,.2f} Billion")
        st.write(f"Profit: ${company_data1['PROFIT'] / 1e9:,.2f} Billion")
        st.write(f"Website: [Link]({company_data1['WEBSITE']})")

    with col2:
        st.write(f"**{company2}**")
        st.write(f"Revenue: ${company_data2['REVENUES'] / 1e9:,.2f} Billion")
        st.write(f"Profit: ${company_data2['PROFIT'] / 1e9:,.2f} Billion")
        st.write(f"Website: [Link]({company_data2['WEBSITE']})")

    # Bar Graph Comparison
    comparison_data = pd.DataFrame({
        "Metric": ["Revenue", "Profit"],
        company1: [company_data1['REVENUES'] / 1e9, company_data1['PROFIT'] / 1e9],
        company2: [company_data2['REVENUES'] / 1e9, company_data2['PROFIT'] / 1e9],
    })
    fig5 = px.bar(comparison_data, x="Metric", y=[company1, company2], barmode="group", title="Company Comparison")
    st.plotly_chart(fig5)
