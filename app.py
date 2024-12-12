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
    total_revenue = df['REVENUES'].sum() / 1e12  # Convert to trillions
    total_employees = df['EMPLOYEES'].sum()
    avg_revenue_per_employee = total_revenue / total_employees if total_employees else 0
    return total_revenue, total_employees, avg_revenue_per_employee

# Load data
try:
    data_file = 'Fortune 500 Corporate Headquarters.csv'
    df = load_and_clean_data(data_file)
except Exception as e:
    st.error(f"Failed to load the data: {e}")

# Sidebar with logo and description
st.sidebar.image("logo.png", caption=None)  # Removed caption text
st.sidebar.markdown("This app allows users to explore data on Fortune 500 companies through state comparisons and detailed company comparisons. Gain insights into revenue, profits, and employee distribution.")

# Streamlit app with tabs
st.title("Fortune 500 Data Explorer")

tab1, tab2 = st.tabs(["State Comparison", "Company Comparison"])

# Tab 1: State Comparison
with tab1:
    st.subheader("State Comparison")
    
    # State filter with "All States" option
    state_list = ["All States"] + sorted(df['STATE'].unique())
    selected_states = st.sidebar.multiselect("Filter by States", state_list, default="All States")
    
    # Adjust filter logic for "All States"
    if "All States" in selected_states:
        filtered_df = df
    else:
        filtered_df = df[df['STATE'].isin(selected_states)]
    
    # Summary Metrics
    total_revenue, total_employees, avg_revenue_per_employee = calculate_summary(filtered_df)
    st.write(f"**Total Revenue**: ${total_revenue:,.2f} Trillion")
    st.write(f"**Total Employees**: {total_employees:,}")
    st.write(f"**Average Revenue per Employee**: ${avg_revenue_per_employee:,.2f} Trillion")
    
    # Pie Chart: Employee Distribution with improved readability
    st.subheader("Employee Distribution by State")
    state_employees = filtered_df.groupby('STATE')['EMPLOYEES'].sum().reset_index()
    state_employees = state_employees.sort_values(by='EMPLOYEES', ascending=False)
    
    # Limit to top 10 states and group others
    top_states = state_employees[:10]
    other_states = state_employees[10:]
    other_sum = other_states['EMPLOYEES'].sum()
    other_row = pd.DataFrame({'STATE': ['Other'], 'EMPLOYEES': [other_sum]})
    top_states = pd.concat([top_states, other_row], ignore_index=True)
    
    fig2 = px.pie(top_states, names='STATE', values='EMPLOYEES', title="Employee Distribution by State")
    st.plotly_chart(fig2)

    # Map: Adjusted dot size based on revenue
    st.subheader("Company Headquarters Map")
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius="REVENUES",  # Radius proportional to revenue
        get_color=[255, 0, 0],
        pickable=True,
    )
    view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=3)
    map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME}"})
    st.pydeck_chart(map_fig)

    # Scatter Plot: Revenue vs Employees with optimized axes
    st.subheader("Company Revenue vs Employees")

    # Calculate max values for a dynamic range
    x_max = filtered_df['EMPLOYEES'].max() * 1.1  # Extend 10% beyond max value
    y_max = filtered_df['REVENUES'].max() * 1.1  # Extend 10% beyond max value

    # Plot with adjusted range
    fig3 = px.scatter(
        filtered_df,
        x='EMPLOYEES',
        y='REVENUES',
        hover_data=['NAME', 'CITY'],
        title="Company Revenue vs Employees",
        labels={'EMPLOYEES': 'Employees', 'REVENUES': 'Revenues (in Trillions)'},
    )
    fig3.update_xaxes(range=[0, x_max])  # Set X-axis range
    fig3.update_yaxes(range=[0, y_max])  # Set Y-axis range
    st.plotly_chart(fig3)

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
    st.write(f"**Revenue:** ${company_data1['REVENUES']:,.2f} Trillion")
    st.write(f"**Profit:** ${company_data1['PROFIT']:,.2f} Billion")
    if company_data1['COMMENTS'] != "NOT AVAILABLE":
        st.write(f"**Comments:** {company_data1['COMMENTS']}")
    st.write(f"**Website:** [Visit]({company_data1['WEBSITE']})")

    st.markdown("### Company 2 Details")
    st.write(f"**Name:** {company_data2['NAME']}")
    st.write(f"**Address:** {company_data2['ADDRESS']}, {company_data2['CITY']}, {company_data2['STATE']} {company_data2['ZIP']}")
    st.write(f"**Employees:** {company_data2['EMPLOYEES']:,}")
    st.write(f"**Revenue:** ${company_data2['REVENUES']:,.2f} Trillion")
    st.write(f"**Profit:** ${company_data2['PROFIT']:,.2f} Billion")
    if company_data2['COMMENTS'] != "NOT AVAILABLE":
        st.write(f"**Comments:** {company_data2['COMMENTS']}")
    st.write(f"**Website:** [Visit]({company_data2['WEBSITE']})")

    # Comparison Chart
    comparison_data = pd.DataFrame({
        "Metric": ["Revenue", "Profit", "Employees"],
        company1: [company_data1['REVENUES'], company_data1['PROFIT'], company_data1['EMPLOYEES']],
        company2: [company_data2['REVENUES'], company_data2['PROFIT'], company_data2['EMPLOYEES']],
    })
    fig5 = px.bar(comparison_data, x="Metric", y=[company1, company2], barmode="group", title="Company Comparison")
    st.plotly_chart(fig5)
