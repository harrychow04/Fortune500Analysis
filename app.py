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
        df['PROFITS'] = pd.to_numeric(df['PROFITS'], errors='coerce')  # Ensure profits column is numeric
        df.dropna(subset=['REVENUES', 'EMPLOYEES', 'PROFITS'], inplace=True)
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

# Streamlit Features
st.title("Fortune 500 Data Explorer")

# Load data
try:
    data_file = 'Fortune 500 Corporate Headquarters.csv'
    df = load_and_clean_data(data_file)
except Exception as e:
    st.error(f"Failed to load the data: {e}")

# [ST2] Multi-select for states
state_list = sorted(df['STATE'].unique())
selected_states = st.sidebar.multiselect("Filter by States", state_list, default=state_list)

# Data Filtering
filtered_df = df[df['STATE'].isin(selected_states)]

# Summary Metrics
total_revenue, total_employees, avg_revenue_per_employee = calculate_summary(filtered_df)

st.subheader("Summary Metrics")
st.write(f"**Total Revenue**: ${total_revenue:,.2f} Million")
st.write(f"**Total Employees**: {total_employees:,}")
st.write(f"**Average Revenue per Employee**: ${avg_revenue_per_employee:,.2f}")

# Visualizations
# [VIZ1] Bar Chart: Revenue by State
st.subheader("Revenue by State")
state_revenue = filtered_df.groupby('STATE')['REVENUES'].sum().sort_values(ascending=False).reset_index()
fig1 = px.bar(state_revenue, x='STATE', y='REVENUES', title="Total Revenue by State (in $)", labels={'REVENUES': 'Revenue ($)'})
st.plotly_chart(fig1)

# [VIZ2] Pie Chart: Employee Distribution by State
st.subheader("Employee Distribution by State")
state_employees = filtered_df.groupby('STATE')['EMPLOYEES'].sum().reset_index()
fig2 = px.pie(state_employees, names='STATE', values='EMPLOYEES', title="Employee Distribution by State")
st.plotly_chart(fig2)

# [VIZ3] Scatter Plot: Revenue vs Employees
st.subheader("Revenue vs Employees")
fig3 = px.scatter(filtered_df, x='EMPLOYEES', y='REVENUES', hover_data=['NAME', 'CITY'], title="Company Revenue vs Employees")
st.plotly_chart(fig3)

# [MAP] Headquarters Map with Smaller Dots
st.subheader("Company Headquarters Map")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_df,
    get_position=["LONGITUDE", "LATITUDE"],
    get_radius=100000,  # Smaller radius
    get_color=[255, 0, 0],
    pickable=True,
)
view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=3)
map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME}"})
st.pydeck_chart(map_fig)

# Heatmap: Profits by State
st.subheader("Profit Heatmap by State")
state_profits = filtered_df.groupby('STATE')['PROFITS'].sum().reset_index()
fig4 = px.choropleth(
    state_profits,
    locations='STATE',
    locationmode='USA-states',
    color='PROFITS',
    color_continuous_scale='reds',
    title="Total Profits by State",
    scope="usa",
)
st.plotly_chart(fig4)

# Additional Analysis: Top Companies by Profit
st.subheader("Top 5 Companies by Profit")
top_profit_companies = filtered_df.nlargest(5, 'PROFITS')[['NAME', 'PROFITS', 'STATE']]
st.table(top_profit_companies)

# Pivot Table: Profit by State and County
st.subheader("Profit Pivot Table")
profit_pivot = pd.pivot_table(filtered_df, values='PROFITS', index='STATE', columns='COUNTY', aggfunc='sum')
st.dataframe(profit_pivot)

# Efficiency Metric
st.subheader("Company Data with Efficiency Metric")
filtered_df['Profit_per_Employee'] = filtered_df['PROFITS'] / filtered_df['EMPLOYEES']
st.dataframe(filtered_df[['NAME', 'STATE', 'PROFITS', 'EMPLOYEES', 'Profit_per_Employee']])
