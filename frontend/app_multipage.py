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
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Load model and data (cached globally)
model, X_processed, y, feature_cols, explainer, label_encoders, X_original = load_model_and_data()

if model is None:
    st.error("Failed to load model or data. Please check if files exist.")
    st.stop()

# Sidebar navigation
with st.sidebar:
    st.title("🧭 Navigation")
    page = st.radio(
        "Select Page:",
        ["🏠 Overview", "👤 Single Customer Analysis", "📊 Aggregate Trends Dashboard"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Dataset Stats")
    st.metric("Total Customers", f"{len(X_processed):,}")
    st.metric("Avg Churn Rate", f"{y.mean()*100:.1f}%")
    st.metric("Features Used", len(feature_cols))

# Page routing
if page == "🏠 Overview":
    from pages import overview_page
    overview_page.show(model, X_processed, y, feature_cols, explainer)

elif page == "👤 Single Customer Analysis":
    from pages import single_customer_page
    single_customer_page.show(model, X_processed, y, feature_cols, explainer, label_encoders, X_original)

elif page == "📊 Aggregate Trends Dashboard":
    from pages import aggregate_dashboard_page
    aggregate_dashboard_page.show(model, X_processed, y, feature_cols, explainer, X_original)

# Footer
st.markdown("---")
st.markdown(get_footer_html(), unsafe_allow_html=True)
