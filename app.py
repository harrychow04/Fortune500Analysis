import pandas as pd
import streamlit as st
import plotly.express as px
import pydeck as pdk

# [DA1] Clean the data
@st.cache_data
def load_and_clean_data(filepath):
    try:
        df = pd.read_csv(filepath)
        df['REVENUES'] = pd.to_numeric(df['REVENUES'], errors='coerce')
        df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'], errors='coerce')
        df['PROFIT'] = pd.to_numeric(df['PROFIT'], errors='coerce')
        df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
        df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
        df.dropna(subset=['REVENUES', 'EMPLOYEES', 'PROFIT', 'LATITUDE', 'LONGITUDE'], inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# [PY2] Function that returns more than one value
def calculate_summary(df):
    total_revenue = df['REVENUES'].sum() / 1e6  # Convert to millions
    total_employees = df['EMPLOYEES'].sum()
    avg_revenue_per_employee = total_revenue / total_employees if total_employees else 0
    return total_revenue, total_employees, avg_revenue_per_employee

# Load data
try:
    data_file = 'Fortune 500 Corporate Headquarters.csv'
    df = load_and_clean_data(data_file)
except Exception as e:
    st.error(f"Failed to load the data: {e}")

# Streamlit app with tabs
st.title("Fortune 500 Data Explorer")

tab1, tab2 = st.tabs(["State Comparison", "Company Comparison"])

# Tab 1: State Comparison
with tab1:
    st.subheader("State Comparison")
    
    # State filter
    state_list = sorted(df['STATE'].unique())
    selected_states = st.sidebar.multiselect("Filter by States", state_list, default=state_list)
    filtered_df = df[df['STATE'].isin(selected_states)]
    
    # Summary Metrics
    total_revenue, total_employees, avg_revenue_per_employee = calculate_summary(filtered_df)
    st.write(f"**Total Revenue**: ${total_revenue:,.2f} Million")
    st.write(f"**Total Employees**: {total_employees:,}")
    st.write(f"**Average Revenue per Employee**: ${avg_revenue_per_employee:,.2f}")
    
    # Visualizations
    state_revenue = filtered_df.groupby('STATE')['REVENUES'].sum().sort_values(ascending=False).reset_index()
    fig1 = px.bar(state_revenue, x='STATE', y='REVENUES', title="Total Revenue by State (in $)", labels={'REVENUES': 'Revenue ($)'})
    st.plotly_chart(fig1)

    state_employees = filtered_df.groupby('STATE')['EMPLOYEES'].sum().reset_index()
    fig2 = px.pie(state_employees, names='STATE', values='EMPLOYEES', title="Employee Distribution by State")
    st.plotly_chart(fig2)

    fig3 = px.scatter(filtered_df, x='EMPLOYEES', y='REVENUES', hover_data=['NAME', 'CITY'], title="Company Revenue vs Employees")
    st.plotly_chart(fig3)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius=100000,
        get_color=[255, 0, 0],
        pickable=True,
    )
    view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=3)
    map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME}"})
    st.pydeck_chart(map_fig)

    state_profits = filtered_df.groupby('STATE')['PROFIT'].sum().reset_index()
    fig4 = px.choropleth(
        state_profits,
        locations='STATE',
        locationmode='USA-states',
        color='PROFIT',
        color_continuous_scale='reds',
        title="Total Profit by State",
        scope="usa",
    )
    st.plotly_chart(fig4)

# Tab 2: Company Comparison
with tab2:
    st.subheader("Company Comparison")

    # Select two companies for comparison
    company_list = sorted(df['NAME'].unique())
    company1 = st.selectbox("Select First Company", company_list, index=0)
    company2 = st.selectbox("Select Second Company", company_list, index=1)
    
    company_data1 = df[df['NAME'] == company1].iloc[0]
    company_data2 = df[df['NAME'] == company2].iloc[0]

    # Display details for both companies
    st.markdown("### Company 1 Details")
    st.write(f"**Name:** {company_data1['NAME']}")
    st.write(f"**Address:** {company_data1['ADDRESS']}, {company_data1['CITY']}, {company_data1['STATE']} {company_data1['ZIP']}")
    st.write(f"**Employees:** {company_data1['EMPLOYEES']:,}")
    st.write(f"**Revenue:** ${company_data1['REVENUES']:,.2f}")
    st.write(f"**Profit:** ${company_data1['PROFIT']:,.2f}")
    st.write(f"**Website:** [Visit]({company_data1['WEBSITE']})")

    st.markdown("### Company 2 Details")
    st.write(f"**Name:** {company_data2['NAME']}")
    st.write(f"**Address:** {company_data2['ADDRESS']}, {company_data2['CITY']}, {company_data2['STATE']} {company_data2['ZIP']}")
    st.write(f"**Employees:** {company_data2['EMPLOYEES']:,}")
    st.write(f"**Revenue:** ${company_data2['REVENUES']:,.2f}")
    st.write(f"**Profit:** ${company_data2['PROFIT']:,.2f}")
    st.write(f"**Website:** [Visit]({company_data2['WEBSITE']})")

    # Comparison Chart
    comparison_data = pd.DataFrame({
        "Metric": ["Revenue", "Profit", "Employees"],
        company1: [company_data1['REVENUES'], company_data1['PROFIT'], company_data1['EMPLOYEES']],
        company2: [company_data2['REVENUES'], company_data2['PROFIT'], company_data2['EMPLOYEES']],
    })
    fig5 = px.bar(comparison_data, x="Metric", y=[company1, company2], barmode="group", title="Company Comparison")
    st.plotly_chart(fig5)
