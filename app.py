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

# Load and clean data
@st.cache_data
def load_and_clean_data(filepath):
    try:
        df = pd.read_csv(filepath)
        # Clean specific columns
        if df['REVENUES'].dtype == 'object':
            df['REVENUES'] = df['REVENUES'].str.replace(',', '').astype(float)
        else:
            df['REVENUES'] = df['REVENUES'].astype(float)

        if df['PROFIT'].dtype == 'object':
            df['PROFIT'] = df['PROFIT'].str.replace(',', '').astype(float)
        else:
            df['PROFIT'] = df['PROFIT'].astype(float)

        if df['EMPLOYEES'].dtype == 'object':
            df['EMPLOYEES'] = df['EMPLOYEES'].str.replace(',', '').astype(int)
        else:
            df['EMPLOYEES'] = df['EMPLOYEES'].astype(int)

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Calculate summary metrics
def calculate_summary(df):
    if df.empty:
        return 0, 0  # Handle empty data case
    total_revenue = df['REVENUES'].sum()
    total_employees = df['EMPLOYEES'].sum()
    return total_revenue, total_employees

# Generate heatmaps
def generate_heatmap(df, column, title):
    if column not in df.columns:
        st.error(f"{column} column not found in the data.")
        return
    fig = px.choropleth(
        df,
        locations="STATE",
        locationmode="USA-states",
        color=column,
        scope="usa",
        title=title,
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig)

# Bar plot for company comparisons
def plot_company_comparisons(df, company1, company2):
    data = df[df['NAME'].isin([company1, company2])]
    if data.empty:
        st.error("No data available for the selected companies.")
        return

    for metric in ['REVENUES', 'PROFIT']:
        fig = px.bar(
            data,
            x='NAME',
            y=metric,
            text=metric,
            title=f"{metric} Comparison (In Millions)",
            labels={metric: f"{metric} (In Millions)"}
        )
        st.plotly_chart(fig)

# Load the data
data_file = 'Fortune 500 Corporate Headquarters.csv'
df = load_and_clean_data(data_file)

# Streamlit app
st.title("Fortune 500 Data Explorer")

if df.empty:
    st.error("No data available. Please check the CSV file.")
else:
    tab1, tab2, tab3, tab4 = st.tabs(["State Comparison", "Company Map", "Company Comparison", "Interactive Insights"])

    # Tab 1: State Comparison
    with tab1:
        st.subheader("State Comparison")
        total_revenue, total_employees = calculate_summary(df)
        st.write(f"**Total Revenue**: ${total_revenue:,.2f} (In Millions)")
        st.write(f"**Total Employees**: {total_employees:,}")

        st.subheader("Heatmaps")
        st.write("Profit by State")
        generate_heatmap(df, "PROFIT", "Profit by State (In Millions)")
        st.write("Revenue by State")
        generate_heatmap(df, "REVENUES", "Revenue by State (In Millions)")
        st.write("Companies by State")
        generate_heatmap(df, "STATE", "Companies by State")

    # Tab 2: Company Map
    with tab2:
        st.subheader("Company Headquarters Map")
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["LONGITUDE", "LATITUDE"],
            get_radius=10000,  # Static radius size
            get_color=[255, 0, 0],
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=37.7749, longitude=-95.7129, zoom=3)
        map_fig = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME}"})
        st.pydeck_chart(map_fig)

    # Tab 3: Company Comparison
    with tab3:
        st.subheader("Company Comparison")
        companies = st.multiselect("Select Companies", options=df['NAME'].unique(), default=df['NAME'].unique()[:2])
        if len(companies) == 2:
            company1, company2 = companies
            st.write(f"### {company1}")
            st.write(f"Revenue: ${df[df['NAME'] == company1]['REVENUES'].sum():,.2f} (In Millions)")
            st.write(f"Profit: ${df[df['NAME'] == company1]['PROFIT'].sum():,.2f} (In Millions)")
            st.write(f"Website: [Link]({df[df['NAME'] == company1]['WEBSITE'].values[0]})")

            st.write(f"### {company2}")
            st.write(f"Revenue: ${df[df['NAME'] == company2]['REVENUES'].sum():,.2f} (In Millions)")
            st.write(f"Profit: ${df[df['NAME'] == company2]['PROFIT'].sum():,.2f} (In Millions)")
            st.write(f"Website: [Link]({df[df['NAME'] == company2]['WEBSITE'].values[0]})")

            plot_company_comparisons(df, company1, company2)
        else:
            st.info("Please select exactly two companies to compare.")

    # Tab 4: Interactive Insights
    with tab4:
        st.subheader("Interactive Insights")
        metric = st.selectbox("Choose Metric", ["REVENUES", "PROFIT"])
        threshold = st.slider(f"Minimum {metric} (In Millions)", min_value=0, max_value=int(df[metric].max()), step=1000)
        filtered_df = df[df[metric] >= threshold]
        st.write(f"Filtered Companies with {metric} greater than {threshold} (In Millions):")
        st.dataframe(filtered_df)

        if not filtered_df.empty:
            fig = px.bar(
                filtered_df,
                x="NAME",
                y=metric,
                text=metric,
                title=f"{metric} of Filtered Companies (In Millions)",
                labels={metric: f"{metric} (In Millions)"}
            )
            st.plotly_chart(fig)
