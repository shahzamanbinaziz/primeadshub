import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIG ---
st.set_page_config(page_title="Prime Ads Hub | Analytics", layout="wide", page_icon="📈")

# Branding CSS
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: white; }
    div[data-testid="stMetricValue"] { color: #00FFAA; font-size: 32px; }
    .stSidebar { background-color: #161B22; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data(ttl=3600)
def load_data():
    try:
        data = pd.read_csv('gam_report_data.csv')
        data['Dimension.DATE'] = pd.to_datetime(data['Dimension.DATE'])
        return data
    except:
        return None

df = load_data()

# --- SIDEBAR & BRANDING ---
st.sidebar.image("https://via.placeholder.com/150x50?text=PRIME+ADS+HUB", use_column_width=True) # Replace with your logo URL
st.sidebar.title("Reporting Filters")

if df is not None:
    # Filters
    ad_units = st.sidebar.multiselect("Select Ad Units", options=df['Dimension.AD_UNIT_NAME'].unique(), default=df['Dimension.AD_UNIT_NAME'].unique())
    countries = st.sidebar.multiselect("Select Countries", options=df['Dimension.COUNTRY_NAME'].unique(), default=df['Dimension.COUNTRY_NAME'].unique()[:5])
    
    filtered_df = df[(df['Dimension.AD_UNIT_NAME'].isin(ad_units)) & (df['Dimension.COUNTRY_NAME'].isin(countries))]

    # --- MAIN UI ---
    st.title("📊 Prime Ads Hub Command Center")
    st.markdown("---")

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Revenue", f"${filtered_df['Revenue'].sum():,.2f}")
    m2.metric("Impressions", f"{filtered_df['Column.AD_SERVER_IMPRESSIONS'].sum():,}")
    m3.metric("Global eCPM", f"${filtered_df['eCPM'].mean():,.2f}")
    m4.metric("CTR", f"{(filtered_df['Column.AD_SERVER_CLICKS'].sum()/filtered_df['Column.AD_SERVER_IMPRESSIONS'].sum()*100):,.2f}%")

    # Charts Row
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Revenue Trend (Last 30 Days)")
        fig_rev = px.line(filtered_df.groupby('Dimension.DATE')['Revenue'].sum().reset_index(), 
                          x='Dimension.DATE', y='Revenue', template="plotly_dark", color_discrete_sequence=['#00FFAA'])
        st.plotly_chart(fig_rev, use_container_width=True)

    with c2:
        st.subheader("Revenue by Ad Unit")
        fig_pie = px.pie(filtered_df, values='Revenue', names='Dimension.AD_UNIT_NAME', hole=0.4, template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Geographic Breakdown
    st.subheader("Performance by Country")
    geo_df = filtered_df.groupby('Dimension.COUNTRY_NAME')[['Revenue', 'Column.AD_SERVER_IMPRESSIONS']].sum().sort_values('Revenue', ascending=False)
    st.dataframe(geo_df, use_container_width=True)

else:
    st.warning("⚠️ No data found. Please ensure the 'fetch_gam_data.py' script has run successfully.")
