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
        # Ensure numeric conversion for financial columns
        df['REVENUES'] = pd.to_numeric(df['REVENUES'].str.replace(',', ''), errors='coerce').fillna(0)
        df['PROFIT'] = pd.to_numeric(df['PROFIT'].str.replace(',', ''), errors='coerce').fillna(0)
        df['EMPLOYEES'] = pd.to_numeric(df['EMPLOYEES'].str.replace(',', ''), errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
data_file = 'Fortune 500 Corporate Headquarters.csv'
df = load_and_clean_data(data_file)

# Ensure data loaded correctly
if df.empty:
    st.error("No data available. Please check the CSV file.")
else:
    st.title("Fortune 500 Data Explorer")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["State Comparison", "Company Map", "Company Comparison", "Interactive Insights"])

    # Tab 1: State Comparison
    with tab1:
        st.subheader("State Comparison")
        state_list = ["All States"] + sorted(df['STATE'].unique())
        selected_state = st.selectbox("Filter by State", state_list)

        if selected_state == "All States":
            filtered_df = df
        else:
            filtered_df = df[df['STATE'] == selected_state]

        total_revenue = filtered_df['REVENUES'].sum()
        total_employees = filtered_df['EMPLOYEES'].sum()

        st.write(f"**Total Revenue**: ${total_revenue:,.2f} (In Millions)")
        st.write(f"**Total Employees**: {total_employees:,}")

        st.subheader("Heatmaps")
        st.write("**Profit by State**")
        profit_fig = px.choropleth(
            df,
            locations='STATE',
            locationmode="USA-states",
            color='PROFIT',
            scope="usa",
            title="Profit by State"
        )
        st.plotly_chart(profit_fig, use_container_width=True)

        st.write("**Revenue by State**")
        revenue_fig = px.choropleth(
            df,
            locations='STATE',
            locationmode="USA-states",
            color='REVENUES',
            scope="usa",
            title="Revenue by State"
        )
        st.plotly_chart(revenue_fig, use_container_width=True)

        st.write("**Companies by State**")
        company_fig = px.choropleth(
            df.groupby('STATE').size().reset_index(name='COMPANIES'),
            locations='STATE',
            locationmode="USA-states",
            color='COMPANIES',
            scope="usa",
            title="Companies by State"
        )
        st.plotly_chart(company_fig, use_container_width=True)

    # Tab 2: Company Map
    with tab2:
        st.subheader("Company Map")
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["LONGITUDE", "LATITUDE"],
            get_radius=30000,
            get_color=[255, 0, 0],
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=37.7749, longitude=-95.7129, zoom=3)
        company_map = pdk.Deck(layers=[layer], initial_view_state=view_state)
        st.pydeck_chart(company_map)

    # Tab 3: Company Comparison
    with tab3:
        st.subheader("Company Comparison")
        company_options = df['NAME'].unique()
        selected_companies = st.multiselect("Select Companies", company_options)

        if len(selected_companies) == 2:
            company_1 = df[df['NAME'] == selected_companies[0]].iloc[0]
            company_2 = df[df['NAME'] == selected_companies[1]].iloc[0]

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"### {company_1['NAME']}")
                st.write(f"Revenue: ${company_1['REVENUES']:,.2f} (In Millions)")
                st.write(f"Profit: ${company_1['PROFIT']:,.2f} (In Millions)")
                st.write(f"Website: [Link]({company_1['WEBSITE']})")

            with col2:
                st.write(f"### {company_2['NAME']}")
                st.write(f"Revenue: ${company_2['REVENUES']:,.2f} (In Millions)")
                st.write(f"Profit: ${company_2['PROFIT']:,.2f} (In Millions)")
                st.write(f"Website: [Link]({company_2['WEBSITE']})")
        else:
            st.info("Please select exactly two companies for comparison.")

    # Tab 4: Interactive Insights
    with tab4:
        st.subheader("Interactive Insights")
        metric = st.selectbox("Choose Metric", ["Revenue", "Profit", "Employees"])
        threshold = st.slider(f"Minimum {metric}", 0, int(df[metric.upper()].max()), step=1000)

        filtered_insights = df[df[metric.upper()] >= threshold]
        st.write(f"Companies with {metric} >= {threshold}")
        st.dataframe(filtered_insights)

        fig6 = px.bar(filtered_insights, x="NAME", y=metric.upper(), title=f"{metric} of Filtered Companies")
        st.plotly_chart(fig6, use_container_width=True)
