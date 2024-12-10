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
        df.dropna(subset=['REVENUES', 'EMPLOYEES'], inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# [PY1] Function with two or more parameters, one having a default value
def filter_data(df, state=None, min_employees=0):
    filtered_df = df[df['EMPLOYEES'] >= min_employees]
    if state:
        filtered_df = filtered_df[filtered_df['STATE'] == state]
    return filtered_df

# [PY2] Function that returns more than one value
def calculate_summary(df):
    total_revenue = df['REVENUES'].sum()
    total_employees = df['EMPLOYEES'].sum()
    avg_revenue_per_employee = total_revenue / total_employees if total_employees else 0
    return total_revenue, total_employees, avg_revenue_per_employee

# [PY3] Error checking with try/except
try:
    data_file = 'Fortune 500 Corporate Headquarters.csv'
    df = load_and_clean_data(data_file)
except Exception as e:
    st.error(f"Failed to load the data: {e}")

# [PY4] List comprehension
state_list = [state for state in df['STATE'].unique()]

# Streamlit Features
st.title("Fortune 500 Data Explorer")

# [ST4] Customized sidebar with logo from repository
st.sidebar.image("logo.png", caption="FortuneView Logo")  # Adjust the path to match your repository structure

# [ST1] Slider for filtering employees
employee_filter = st.sidebar.slider("Minimum Number of Employees", 0, int(df['EMPLOYEES'].max()), 1000)

# [ST2] Multi-select for states
selected_states = st.sidebar.multiselect("Select States", state_list)

# Data Filtering
filtered_df = filter_data(df, state=None if not selected_states else selected_states[0], min_employees=employee_filter)

# Summary Metrics
total_revenue, total_employees, avg_revenue_per_employee = calculate_summary(filtered_df)

st.subheader("Summary Metrics")
st.write(f"**Total Revenue**: ${total_revenue:,.2f}")
st.write(f"**Total Employees**: {total_employees:,}")
st.write(f"**Average Revenue per Employee**: ${avg_revenue_per_employee:,.2f}")

# Visualizations
# [VIZ1] Bar Chart: Revenue by State
st.subheader("Revenue by State")
state_revenue = filtered_df.groupby('STATE')['REVENUES'].sum().sort_values(ascending=False).reset_index()  # [DA2] Sort data
fig1 = px.bar(state_revenue, x='STATE', y='REVENUES', title="Total Revenue by State", labels={'REVENUES': 'Revenue ($)'})
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

# [MAP] Detailed Map: Headquarters by State
st.subheader("Company Headquarters Map")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_df,
    get_position=["LONGITUDE", "LATITUDE"],
    get_radius=200000,
    get_color=[255, 0, 0],
    pickable=True,
)
view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=3)
map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME}"})
st.pydeck_chart(map_fig)

# Data Analytics Features
# [DA3] Find top largest companies by revenue
st.subheader("Top 5 Companies by Revenue")
top_companies = filtered_df.nlargest(5, 'REVENUES')[['NAME', 'REVENUES', 'STATE']]  # [DA3] Top largest
st.table(top_companies)

# [DA6] Pivot table for revenue by state and county
st.subheader("Revenue Pivot Table")
pivot_table = pd.pivot_table(filtered_df, values='REVENUES', index='STATE', columns='COUNTY', aggfunc='sum')  # [DA6]
st.dataframe(pivot_table)

# [DA7] Add/drop/select columns
st.subheader("Company Data with Efficiency Metric")
filtered_df['Revenue_per_Employee'] = filtered_df['REVENUES'] / filtered_df['EMPLOYEES']  # [DA9] Add new column
st.dataframe(filtered_df[['NAME', 'STATE', 'REVENUES', 'EMPLOYEES', 'Revenue_per_Employee']])
