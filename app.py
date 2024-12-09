import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px

# Load Data
@st.cache
def load_data(filepath):
    try:
        data = pd.read_csv(filepath)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load Industry Database
@st.cache
def load_industry_database():
    return {
        "Apple": "Technology",
        "Microsoft": "Technology",
        "Amazon": "Retail",
        "Walmart": "Retail",
        "ExxonMobil": "Energy",
        # Add all 500 companies here...
    }

# Load Ticker Database
@st.cache
def load_ticker_database():
    return {
        "Apple": "https://finance.yahoo.com/quote/AAPL/",
        "Microsoft": "https://finance.yahoo.com/quote/MSFT/",
        "Amazon": "https://finance.yahoo.com/quote/AMZN/",
        "Walmart": "https://finance.yahoo.com/quote/WMT/",
        "ExxonMobil": "https://finance.yahoo.com/quote/XOM/",
        # Add all 500 companies here...
    }

# Filter Data Based on User Input
def filter_data(df, states, industries, industry_db):
    if states:
        df = df[df['STATE'].isin(states)]
    if industries:
        companies_in_industry = [company for company, industry in industry_db.items() if industry in industries]
        df = df[df['NAME'].isin(companies_in_industry)]
    return df

# Revenue by State (Ordered)
def create_revenue_chart(df):
    state_data = df.groupby('STATE')['REVENUES'].sum().reset_index()
    state_data = state_data.sort_values(by='REVENUES', ascending=False)  # Sort by revenue
    fig = px.bar(state_data, x='STATE', y='REVENUES', title="Total Revenue by State")
    st.plotly_chart(fig)

# Employee Distribution with Interactivity
def create_employee_chart(df):
    state_data = df.groupby('STATE')['EMPLOYEES'].sum().reset_index()
    state_data = state_data[state_data['EMPLOYEES'] > 0]  # Remove states with no employees
    fig = px.pie(
        state_data,
        values='EMPLOYEES',
        names='STATE',
        title="Employee Distribution",
        hover_data=['EMPLOYEES'],
    )
    st.plotly_chart(fig)

    # Add interactivity: Click on a state to list companies
    selected_state = st.selectbox("Select a State to View Companies", state_data['STATE'])
    if selected_state:
        companies_in_state = df[df['STATE'] == selected_state][['NAME', 'EMPLOYEES']]
        st.write(f"Companies in {selected_state}:")
        st.dataframe(companies_in_state)

# Top Companies by Revenue with Filtering
def display_top_companies(df):
    st.subheader("Top Companies by Revenue")
    options = ["Top", "Bottom", "Middle", "Filter by Industry"]
    selection = st.radio("Choose Filter Type", options)

    if selection == "Top":
        top_companies = df.nlargest(10, 'REVENUES')[['NAME', 'REVENUES', 'STATE']]
    elif selection == "Bottom":
        top_companies = df.nsmallest(10, 'REVENUES')[['NAME', 'REVENUES', 'STATE']]
    elif selection == "Middle":
        middle_idx = len(df) // 2
        top_companies = df.iloc[middle_idx - 5:middle_idx + 5][['NAME', 'REVENUES', 'STATE']]
    elif selection == "Filter by Industry":
        industry = st.selectbox("Select Industry", df['INDUSTRY'].unique())
        top_companies = df[df['INDUSTRY'] == industry][['NAME', 'REVENUES', 'STATE']]

    st.dataframe(top_companies)

# Main UI
st.title("Fortune 500 Data Explorer")
data_file = "Fortune 500 Corporate Headquarters.csv"
df = load_data(data_file)
industry_db = load_industry_database()
ticker_db = load_ticker_database()

if not df.empty:
    # Sidebar Filters
    st.sidebar.title("Filters")
    states = st.sidebar.multiselect("Select States", df['STATE'].unique())
    industries = st.sidebar.multiselect("Select Industry", set(industry_db.values()))

    # Filter Data
    filtered_df = filter_data(df, states, industries, industry_db)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Revenue Analysis", "Employee Distribution", "Top Companies"])

    with tab1:
        create_revenue_chart(filtered_df)

    with tab2:
        create_employee_chart(filtered_df)

    with tab3:
        display_top_companies(filtered_df)
else:
    st.error("Data could not be loaded. Please check the file.")
