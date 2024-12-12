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

# [DA1] Load and clean data
@st.cache_data
def load_and_clean_data(filepath):
    try:
        # Load data and strip column names
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()

        # Ensure specific columns exist
        required_columns = ["REVENUES", "EMPLOYEES", "PROFIT", "NAME", "STATE", "LATITUDE", "LONGITUDE", "WEBSITE"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = None  # Create missing columns as empty

        # Convert numeric columns to numeric and handle errors
        numeric_columns = ["REVENUES", "EMPLOYEES", "PROFIT"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).div(1e6)  # Convert to millions

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# [PY2] Calculate summary statistics
def calculate_summary(df):
    total_revenue = df["REVENUES"].sum() if "REVENUES" in df.columns else 0
    total_employees = df["EMPLOYEES"].sum() if "EMPLOYEES" in df.columns else 0
    return total_revenue, total_employees

# [PY3] Filter data
def filter_data(df, column, threshold):
    if column in df.columns:
        return df[df[column] >= threshold]
    return pd.DataFrame()

# [PY4] Validate column existence
def validate_column(df, column):
    return column in df.columns

# Load data
data_file = "Fortune 500 Corporate Headquarters.csv"
df = load_and_clean_data(data_file)

# Streamlit app structure
st.title("Fortune 500 Data Explorer")

try:
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["State Comparison", "Company Map", "Company Comparison", "Interactive Insights"]
    )

    # Tab 1: State Comparison
    with tab1:
        st.subheader("State Comparison")
        total_revenue, total_employees = calculate_summary(df)
        st.write(f"**Total Revenue**: ${total_revenue:,.2f} (In Millions)")
        st.write(f"**Total Employees**: {total_employees:,.0f}")
        
        # Heatmaps
        st.subheader("Heatmaps")
        if validate_column(df, "STATE"):
            for metric in ["PROFIT", "REVENUES", "EMPLOYEES"]:
                if validate_column(df, metric):
                    state_data = df.groupby("STATE")[metric].sum().reset_index()
                    fig = px.choropleth(
                        state_data,
                        locations="STATE",
                        locationmode="USA-states",
                        color=metric,
                        scope="usa",
                        title=f"{metric.title()} by State (In Millions)",
                    )
                    st.plotly_chart(fig)

    # Tab 2: Company Map
    with tab2:
        st.subheader("Company Map")
        if validate_column(df, "LATITUDE") and validate_column(df, "LONGITUDE"):
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position=["LONGITUDE", "LATITUDE"],
                get_radius=50000,
                get_color=[255, 0, 0],
                pickable=True,
            )
            view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=3)
            st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    # Tab 3: Company Comparison
    with tab3:
        st.subheader("Company Comparison")
        companies = st.multiselect("Select Companies", df["NAME"].dropna().unique())
        if len(companies) == 2:
            company_data = df[df["NAME"].isin(companies)]
            for _, row in company_data.iterrows():
                st.write(f"**{row['NAME']}**")
                st.write(f"Revenue: ${row['REVENUES']:,.2f} (In Millions)")
                st.write(f"Profit: ${row['PROFIT']:,.2f} (In Millions)")
                st.write(f"Website: [Link]({row['WEBSITE']})")

    # Tab 4: Interactive Insights
    with tab4:
        st.subheader("Interactive Insights")
        metric = st.selectbox("Choose Metric", ["Revenue", "Profit", "Employees"])
        metric = metric.upper()
        if validate_column(df, metric):
            threshold = st.slider(
                f"Minimum {metric} (In Millions)", min_value=0, max_value=int(df[metric].max()), step=100
            )
            filtered_insights = filter_data(df, metric, threshold)
            fig = px.bar(
                filtered_insights,
                x="NAME",
                y=metric,
                title=f"{metric.title()} of Filtered Companies (In Millions)",
            )
            st.plotly_chart(fig)

except Exception as e:
    st.error(f"An error occurred: {e}")
