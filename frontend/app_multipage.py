"""
Customer Churn Prediction Dashboard - Multi-Page Application
"""

import streamlit as st
import pandas as pd
import numpy as np

# Import custom modules
from styles import get_custom_css, get_footer_html
from model_operations import load_model_and_data

# Page configuration
st.set_page_config(
    page_title="Customer Churn Prediction Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Enhanced navbar CSS
st.markdown("""
<style>
.nav-container {
    background: linear-gradient(90deg, #1f77b4 0%, #2c87c8 100%);
    padding: 15px 20px;
    border-radius: 12px;
    margin: 10px 0 20px 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.nav-title {
    color: white;
    font-size: 28px;
    font-weight: bold;
    text-align: center;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.nav-subtitle {
    color: rgba(255, 255, 255, 0.9);
    font-size: 16px;
    text-align: center;
    margin: 5px 0 15px 0;
}

.nav-tabs {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 15px;
}

.nav-tab {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    padding: 8px 20px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.nav-tab:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.nav-tab.active {
    background: white;
    color: #1f77b4;
    border: 2px solid #1f77b4;
    font-weight: bold;
}

.stSelectbox > div > div {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    border: none;
}

.stSelectbox > div > div > div {
    color: white;
    font-weight: 500;
}

/* Hide sidebar completely */
.css-1d391kg {
    display: none;
}

.css-1v3fvcr {
    display: none;
}

[data-testid="stSidebar"] {
    display: none;
}

[data-testid="stSidebarNav"] {
    display: none;
}

/* Remove sidebar button */
button[kind="header"] {
    display: none;
}

.css-uf99v8 {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# Load model and data (cached globally)
model, X_processed, y, feature_cols, explainer, label_encoders, X_original = load_model_and_data()

if model is None:
    st.error("Failed to load model or data. Please check if files exist.")
    st.stop()

# Beautiful Navigation Header
st.markdown("""
<div class="nav-container">
    <h1 class="nav-title">🎯 Customer Churn Prediction Dashboard</h1>
    <p class="nav-subtitle">Advanced ML-powered churn analysis with real-time insights</p>
</div>
""", unsafe_allow_html=True)

# Set default page if not set
if 'page' not in st.session_state:
    st.session_state.page = '🏠 Overview'

# Clean navigation tabs with proper color handling
col1, col2, col3 = st.columns(3)
with col1:
    overview_btn = st.button("🏠 Overview", use_container_width=True, 
                           type="primary" if st.session_state.page == '🏠 Overview' else "secondary",
                           key="nav_overview_btn")
    if overview_btn:
        st.session_state.page = '🏠 Overview'
        st.rerun()

with col2:
    customer_btn = st.button("👤 Customer Analysis", use_container_width=True, 
                           type="primary" if st.session_state.page == '👤 Customer Analysis' else "secondary",
                           key="nav_customer_btn")
    if customer_btn:
        st.session_state.page = '👤 Customer Analysis'
        st.rerun()

with col3:
    trends_btn = st.button("📊 Aggregate Trends Dashboard", use_container_width=True, 
                          type="primary" if st.session_state.page == '📊 Aggregate Trends Dashboard' else "secondary",
                          key="nav_trends_btn")
    if trends_btn:
        st.session_state.page = '📊 Aggregate Trends Dashboard'
        st.rerun()

page = st.session_state.page

# Display dataset stats at the top instead of sidebar
st.markdown("### 📊 Dataset Statistics")
col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    st.metric("Total Customers", f"{len(X_processed):,}")
with col_stat2:
    st.metric("Avg Churn Rate", f"{y.mean()*100:.1f}%")
with col_stat3:
    st.metric("Features Used", len(feature_cols))

st.markdown("---")

# Page routing
if page == "🏠 Overview":
    from pages import overview_page
    overview_page.show(model, X_processed, y, feature_cols, explainer)

elif page == "👤 Customer Analysis":
    from pages import single_customer_page
    single_customer_page.show(model, X_processed, y, feature_cols, explainer, label_encoders, X_original)

elif page == "📊 Aggregate Trends Dashboard":
    from pages import aggregate_dashboard_page
    aggregate_dashboard_page.show(model, X_processed, y, feature_cols, explainer, X_original)

# Footer
st.markdown("---")
st.markdown(get_footer_html(), unsafe_allow_html=True)
