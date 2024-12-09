"""
Name:       Your Name
CS230:      Section XXX
Data:       Fortune 500 Corporate Headquarters
URL:        Add your Streamlit Cloud link here

Description:    
This program creates an interactive data explorer for the Fortune 500 dataset. 
It includes financial summaries, advanced analysis, and map visualizations.
"""

import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px

# [PY3] Error checking with try/except
@st.cache
def load_data(filepath):
    try:
        data = pd.read_csv(filepath)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# [PY5] A dictionary for ticker links
@st.cache
def load_ticker_database():
    return {
        "Apple": "https://finance.yahoo.com/quote/AAPL/",
        "Microsoft": "https://finance.yahoo.com/quote/MSFT/",
        "Amazon": "https://finance.yahoo.com/quote/AMZN/",
        # Add more companies as needed
    }

# [PY1] Function with two or more parameters (one with a default value)
def clean_data(df, drop_na=True):
    # [DA1] Clean/manipulate data
    if drop_na:
        df = df.dropna()
    df.columns = df.columns.str.strip()
    return df

# [PY2] A function that returns multiple values
def get_summary_stats(df):
    total_revenue = df['REVENUES'].sum()
    total_profit = df['PROFIT'].sum()
    total_employees = df['EMPLOYEES'].sum()
    return total_revenue, total_profit, total_employees

# Visualization Functions
def display_summary(df, ticker_db):
    st.subheader("Financial Overview")
    # [PY4] List comprehension
    links = [f"- [{company}]({link})" for company, link in ticker_db.items()]
    st.markdown("\n".join(links))

    # Display summary stats
    total_revenue, total_profit, total_employees = get_summary_stats(df)
    st.write(f"**Total Revenue**: ${total_revenue:,}")
    st.write(f"**Total Profit**: ${total_profit:,}")
    st.write(f"**Total Employees**: {total_employees:,}")

def create_heatmap(df):
    # [DA2] Sort data
    state_data = df.groupby('STATE').size().reset_index(name='Headquarters Count')
    state_data = state_data.sort_values(by='Headquarters Count', ascending=False)
    fig = px.choropleth(
        state_data,
        locations='STATE',
        locationmode='USA-states',
        color='Headquarters Count',
        scope="usa",
        title="Headquarters by State"
    )
    st.plotly_chart(fig)

def create_interactive_map(df):
    # [MAP] Detailed map with hover features
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=df['LATITUDE'].mean(),
            longitude=df['LONGITUDE'].mean(),
            zoom=4,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position='[LONGITUDE, LATITUDE]',
                get_color='[200, 30, 0, 160]',
                get_radius=10000,
                pickable=True,
            ),
        ],
        tooltip={
            "text": "{NAME}\nRevenue: ${REVENUES}\nEmployees: {EMPLOYEES}"
        }
    ))

def create_charts(df):
    # [VIZ1] Bar chart
    revenue_state = df.groupby('STATE')['REVENUES'].sum().reset_index()
    fig = px.bar(revenue_state, x='STATE', y='REVENUES', title="Total Revenue by State")
    st.plotly_chart(fig)

    # [VIZ2] Pie chart
    employee_state = df.groupby('STATE')['EMPLOYEES'].sum().reset_index()
    fig = px.pie(employee_state, values='EMPLOYEES', names='STATE', title="Employee Distribution")
    st.plotly_chart(fig)

    # [DA3] Find top values
    top_companies = df.nlargest(5, 'REVENUES')[['NAME', 'REVENUES']]
    st.subheader("Top 5 Companies by Revenue")
    st.dataframe(top_companies)

# Streamlit UI
st.title("Fortune 500 Data Explorer")
st.sidebar.title("Filters")  # [ST4] Sidebar customization

# Load and Clean Data
data_file = "Fortune 500 Corporate Headquarters.csv"
df = load_data(data_file)
ticker_db = load_ticker_database()

if not df.empty:
    df = clean_data(df)

    # Tabs for Navigation
    # [ST1], [ST2], [ST3] Widgets for interaction
    tab1, tab2, tab3 = st.tabs(["Summary", "Analysis", "Map"])

    with tab1:
        display_summary(df, ticker_db)

    with tab2:
        st.sidebar.multiselect("Filter by State", df['STATE'].unique())
        create_charts(df)
        create_heatmap(df)

    with tab3:
        create_interactive_map(df)
else:
    st.error("Data could not be loaded. Please check the file.")
