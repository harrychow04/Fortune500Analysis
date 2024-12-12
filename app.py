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
        df['REVENUES'] = df['REVENUES'].astype(str)
        df['EMPLOYEES'] = df['EMPLOYEES'].astype(str)
        df['PROFIT'] = df['PROFIT'].astype(str)
        
        # Convert REVENUES, EMPLOYEES, and PROFIT to numeric
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

# Sidebar with logo and description
st.sidebar.image("logo.png", caption=None)
st.sidebar.markdown(
    "This app allows users to explore data on Fortune 500 companies through state comparisons, company comparisons, and generate custom insights."
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
    
    if "All States" in selected_states:
        filtered_df = df
    else:
        filtered_df = df[df['STATE'].isin(selected_states)]
    
    # Summary Metrics
    total_revenue = filtered_df['REVENUES'].sum() / 1e3  # Convert to billions
    total_employees = filtered_df['EMPLOYEES'].sum()
    st.write(f"**Total Revenue**: ${total_revenue:,.2f} Billion")
    st.write(f"**Total Employees**: {total_employees:,}")
    
    # Scatter Plot: Revenue vs Employees
    st.subheader("Revenue vs Employees")
    fig1 = px.scatter(
        filtered_df,
        x='EMPLOYEES',
        y=filtered_df['REVENUES'] / 1e9,  # Convert to billions
        hover_data=['NAME', 'CITY'],
        title="Company Revenue vs Employees",
        labels={'EMPLOYEES': 'Employees', 'y': 'Revenue (in Billions)'},
    )
    st.plotly_chart(fig1)

    # Heatmaps: Vertically aligned
    st.subheader("Heatmaps")
    
    # Profit by State
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
    company_data1 = df[df['NAME'] == company1]
    company_data2 = df[df['NAME'] == company2]
    
    if not company_data1.empty and not company_data2.empty:
        st.write("### Comparison Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{company1}**")
            st.write(f"Revenue: ${company_data1['REVENUES'].values[0] / 1e9:,.2f} Billion")
            st.write(f"Profit: ${company_data1['PROFIT'].values[0] / 1e9:,.2f} Billion")
            st.write(f"Website: [Link]({company_data1['WEBSITE'].values[0]})")

        with col2:
            st.write(f"**{company2}**")
            st.write(f"Revenue: ${company_data2['REVENUES'].values[0] / 1e9:,.2f} Billion")
            st.write(f"Profit: ${company_data2['PROFIT'].values[0] / 1e9:,.2f} Billion")
            st.write(f"Website: [Link]({company_data2['WEBSITE'].values[0]})")
    else:
        st.write("Selected companies not found in the dataset.")

# Tab 4: Interactive Insights
with tab4:
    st.subheader("Interactive Insights")
    metric = st.selectbox("Select Metric", ["Revenue", "Profit", "Employees"])
    min_value = st.number_input(f"Minimum {metric}", min_value=0, value=0)
    max_value = st.number_input(f"Maximum {metric}", min_value=0, value=1000000)
    
    if metric == "Revenue":
        filtered_insights = df[(df['REVENUES'] >= min_value) & (df['REVENUES'] <= max_value)]
    elif metric == "Profit":
        filtered_insights = df[(df['PROFIT'] >= min_value) & (df['PROFIT'] <= max_value)]
    else:  # Employees
        filtered_insights = df[(df['EMPLOYEES'] >= min_value) & (df['EMPLOYEES'] <= max_value)]
    
    st.write(f"Filtered Data ({metric}):", filtered_insights)
    st.write(f"Total Companies: {len(filtered_insights)}")
    
    if not filtered_insights.empty:
        fig6 = px.bar(filtered_insights, x="NAME", y=metric.upper(), title=f"{metric} of Filtered Companies")
        st.plotly_chart(fig6)

