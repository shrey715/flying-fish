"""
Customer Churn Prediction Dashboard - Main Application
"""

import streamlit as st
import pandas as pd
import numpy as np

# Import custom modules
from styles import get_custom_css, get_prediction_box_html, get_footer_html
from model_operations import (
    load_model_and_data, make_prediction, calculate_shap_values, 
    get_risk_level
)
from data_operations import get_customer_by_mode, generate_trend_data
from ui_components import (
    create_sidebar_stats, display_customer_profile, create_gauge_chart,
    create_feature_impact_chart, display_shap_analysis, 
    display_all_feature_impacts, display_recommendations,
    display_metrics, create_trend_chart
)

# Page configuration
st.set_page_config(
    page_title="Customer Churn Prediction Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Load model and data
model, X_processed, y, feature_cols, explainer, label_encoders, X_original = load_model_and_data()

if model is None:
    st.error("Failed to load model or data. Please check if files exist.")
    st.stop()

# Title and Introduction
st.title("🎯 Customer Churn Prediction Dashboard")
st.markdown("""
This interactive dashboard uses a **real XGBoost model** to predict customer churn and provides **SHAP explanations** 
for why customers might leave.
""")

# Customer selection tabs at the top
st.markdown("### 🔍 Customer Selection Mode")

col1, col2 = st.columns(2)
with col1:
    real_customer_btn = st.button("📊 Select Real Customer", use_container_width=True, 
                                type="primary" if st.session_state.get('customer_mode', 'Select Real Customer') == 'Select Real Customer' else "secondary",
                                key="app_real_customer_btn")
    if real_customer_btn:
        st.session_state.customer_mode = 'Select Real Customer'

with col2:
    custom_features_btn = st.button("⚙️ Custom Feature Selection", use_container_width=True,
                                  type="primary" if st.session_state.get('customer_mode', 'Select Real Customer') == 'Custom Feature Selection' else "secondary",
                                  key="app_custom_features_btn")
    if custom_features_btn:
        st.session_state.customer_mode = 'Custom Feature Selection'

# Set default mode if not set
if 'customer_mode' not in st.session_state:
    st.session_state.customer_mode = 'Select Real Customer'

input_mode = st.session_state.customer_mode

st.markdown("---")

# Display dataset stats at the top
st.markdown("### 📊 Dataset Statistics")
col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    st.metric("Total Customers", f"{len(X_processed):,}")
with col_stat2:
    st.metric("Avg Churn Rate", f"{y.mean()*100:.1f}%")
with col_stat3:
    st.metric("Features Used", len(feature_cols))

st.markdown("---")

# Get customer data based on selected mode
sample_customer, actual_churn, customer_id = get_customer_by_mode(
    input_mode, X_processed, y, feature_cols, X_original, label_encoders
)

# Make prediction using the real model
prediction, probability = make_prediction(model, sample_customer)
if prediction is None:
    st.stop()

# Calculate SHAP values
shap_values, feature_contributions, positive_contribs, negative_contribs, features_dict = calculate_shap_values(
    explainer, sample_customer, feature_cols
)
if shap_values is None:
    st.stop()

# Get risk level
risk_level, risk_class, risk_emoji = get_risk_level(probability)

# Main Content
col1, col2 = st.columns([1, 2])

with col1:
    display_customer_profile(customer_id, feature_contributions, actual_churn)

with col2:
    st.markdown("### 🎯 Churn Prediction")
    
    # Display prediction in a styled box
    st.markdown(
        get_prediction_box_html(risk_level, risk_class, risk_emoji, probability),
        unsafe_allow_html=True
    )
    
    # Gauge chart for churn probability
    fig_gauge = create_gauge_chart(probability)
    st.plotly_chart(fig_gauge, use_container_width=True)

# Feature Importance Section
st.markdown("---")
st.markdown("## 🔍 Why This Prediction?")
st.markdown("### Key Drivers for This Customer's Churn Risk")

col3, col4 = st.columns([3, 2])

with col3:
    # Create feature impact chart
    fig_features = create_feature_impact_chart(features_dict)
    st.plotly_chart(fig_features, use_container_width=True)
    
    st.markdown("""
    **How to Read This Chart:**
    - 🔴 **Red bars (positive values)**: Features pushing toward higher churn risk
    - 🔵 **Blue bars (negative values)**: Features reducing churn risk
    - **Bar length**: Indicates the strength of impact
    """)

with col4:
    # Display SHAP analysis
    display_shap_analysis(
        positive_contribs, negative_contribs, explainer, shap_values, 
        model, sample_customer, prediction, actual_churn
    )
    
    # Display all feature impacts
    display_all_feature_impacts(features_dict)
    
    # Display recommendations
    display_recommendations(probability)

# Bottom section with additional insights
st.markdown("---")
st.markdown("## 📊 Additional Insights")

# Display metrics
display_metrics(probability, model, sample_customer)

# Interactive timeline or trend (mock data)
st.markdown("### 📈 Churn Risk Trend (Last 6 Months)")

months, trend_values = generate_trend_data(probability)
fig_trend = create_trend_chart(months, trend_values)
st.plotly_chart(fig_trend, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(get_footer_html(), unsafe_allow_html=True)