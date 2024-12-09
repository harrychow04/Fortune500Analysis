# Load the data
@st.cache_data
def load_data():
    file_path = 'Fortune 500 Corporate Headquarters.csv'
    data = pd.read_csv(file_path)
    # Clean data
    data = data.dropna(subset=['LATITUDE', 'LONGITUDE', 'NAME', 'STATE', 'REVENUES'])
    data['REVENUES'] = pd.to_numeric(data['REVENUES'], errors='coerce')
    return data

data = load_data()

# Title and description
st.title("Fortune 500 Corporate Headquarters Analysis")
st.markdown("""
This interactive app visualizes the geographic distribution of Fortune 500 companies and provides insights into regional trends and revenue distribution.
""")

# Data Overview
st.header("Data Overview")
st.markdown("A snapshot of the cleaned dataset.")
st.write(data.head())

# Interactive Map
st.header("Geographic Distribution of Headquarters")
st.markdown("Explore the locations of Fortune 500 headquarters across the USA.")
view_state = pdk.ViewState(
    latitude=data['LATITUDE'].mean(),
    longitude=data['LONGITUDE'].mean(),
    zoom=4,
    pitch=0
)

layer = pdk.Layer(
    'ScatterplotLayer',
    data=data,
    get_position='[LONGITUDE, LATITUDE]',
    get_radius=50000,
    get_color=[0, 128, 255],
    pickable=True
)

tool_tip = {"html": "Company: {NAME}<br>State: {STATE}<br>Revenue: ${REVENUES}M",
            "style": {"backgroundColor": "steelblue", "color": "white"}}

map = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tool_tip)
st.pydeck_chart(map)

# Revenue Analysis
st.header("Revenue Distribution by State")
st.markdown("This chart shows the total revenue generated by Fortune 500 companies in each state.")
revenue_by_state = data.groupby('STATE')['REVENUES'].sum().sort_values(ascending=False)
st.bar_chart(revenue_by_state)

# Top Companies by Revenue
st.header("Top Companies by Revenue")
st.markdown("A list of the top 10 companies by revenue.")
top_revenue = data.nlargest(10, 'REVENUES')[['NAME', 'REVENUES', 'STATE']]
st.write(top_revenue)

# Filtering by State
st.header("Filter by State")
states = st.multiselect("Select states to filter", data['STATE'].unique())
filtered_data = data[data['STATE'].isin(states)] if states else data
st.write(filtered_data)

# Customized Analysis
st.header("Marketing Insights")
st.markdown("""
**Key Insights:**
- States with high revenue concentrations, such as California and Texas, are critical for business development.
- Use this data to identify potential regions for marketing campaigns or financial services.
""")
