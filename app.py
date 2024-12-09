"""
Name:       Your Name
CS230:      Section XXX
Data:       Fortune 500 Corporate Headquarters
URL:        Add your Streamlit Cloud link here

Description:    
This program creates an interactive data explorer using the Fortune 500 dataset.
It allows users to filter data, visualize distributions, and view corporate headquarters on a map.
"""

import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt

# Load Data
@st.cache
def load_data(filepath):
    try:
        data = pd.read_csv(filepath)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Data Cleaning
def clean_data(df):
    df = df.dropna()  # Drop rows with missing values
    df = df.rename(columns=lambda x: x.strip())  # Remove extra spaces
    return df

# Visualization Functions
def bar_chart(df, column):
    counts = df[column].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind='bar', ax=ax)
    ax.set_title(f"Distribution of {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Count")
    st.pyplot(fig)

def pie_chart(df, column):
    counts = df[column].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel("")
    ax.set_title(f"{column} Distribution")
    st.pyplot(fig)

def create_map(df):
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=df['latitude'].mean(),
            longitude=df['longitude'].mean(),
            zoom=4,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position='[longitude, latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=10000,
            ),
        ],
    ))

# Streamlit UI
st.title("Fortune 500 Data Explorer")
st.sidebar.title("Filters")

# Load and Clean Data
data_file = "Fortune 500 Corporate Headquarters.csv"
df = load_data(data_file)
df = clean_data(df)

if not df.empty:
    # Sidebar Filters
    states = st.sidebar.multiselect("Select States", df['state'].unique())
    industries = st.sidebar.multiselect("Select Industries", df['industry'].unique())
    
    # Filter Data
    if states:
        df = df[df['state'].isin(states)]
    if industries:
        df = df[df['industry'].isin(industries)]

    # Display Data
    st.write("Filtered Data", df)

    # Visualizations
    st.header("Visualizations")
    chart_type = st.selectbox("Choose Chart Type", ["Bar Chart", "Pie Chart", "Map"])
    
    if chart_type == "Bar Chart":
        column = st.selectbox("Choose Column for Bar Chart", ["state", "industry"])
        bar_chart(df, column)
    elif chart_type == "Pie Chart":
        column = st.selectbox("Choose Column for Pie Chart", ["state", "industry"])
        pie_chart(df, column)
    elif chart_type == "Map":
        create_map(df)
else:
    st.error("No data available. Please check the data file.")

st.sidebar.markdown("### Project by Your Name")
