"""
Single Customer Analysis Page - Individual customer churn prediction
"""

import streamlit as st
import pandas as pd
import numpy as np

from model_operations import (
    make_prediction, calculate_shap_values, get_risk_level
)
from data_operations import get_customer_by_mode, generate_trend_data
from ui_components import (
    display_customer_profile, create_gauge_chart,
    create_feature_impact_chart, display_shap_analysis, 
    display_all_feature_impacts, display_recommendations,
    display_metrics, create_trend_chart, call_and_display_agents,
    display_enhanced_feature_impacts
)
from styles import get_prediction_box_html

def show(model, X_processed, y, feature_cols, explainer, label_encoders, X_original):
    """Display the single customer analysis page"""
    
    st.title("👤 Customer Analysis")
    st.markdown("""
    Analyze individual customers to understand their churn risk and the key factors driving their behavior.
    """)
    
    # Customer selection tabs at the top
    st.markdown("### 🔍 Customer Selection Mode")
    
    # Use Streamlit's built-in tabs for proper state management
    tab1, tab2 = st.tabs(["📊 Select Real Customer", "⚙️ Custom Feature Selection"])
    
    # Initialize variables
    sample_customer = None
    actual_churn = None
    customer_id = None
    
    with tab1:
        st.markdown("Select a customer from the dataset by their index.")
        # Get customer data for real customer selection
        sample_customer, actual_churn, customer_id = get_customer_by_mode(
            'Select Real Customer', X_processed, y, feature_cols, X_original, label_encoders, key_prefix="tab1"
        )
        
        # Process and display results for this tab
        if sample_customer is not None:
            display_customer_analysis(sample_customer, actual_churn, customer_id, model, explainer, feature_cols, X_original, tab_id="tab1")
        
    with tab2:
        st.markdown("Create a custom customer profile by adjusting key features.")
        # Get customer data for custom feature selection
        sample_customer, actual_churn, customer_id = get_customer_by_mode(
            'Custom Feature Selection', X_processed, y, feature_cols, X_original, label_encoders, key_prefix="tab2"
        )
        
        # Process and display results for this tab  
        if sample_customer is not None:
            display_customer_analysis(sample_customer, actual_churn, customer_id, model, explainer, feature_cols, X_original, tab_id="tab2")

def display_customer_analysis(sample_customer, actual_churn, customer_id, model, explainer, feature_cols, X_original, tab_id="tab1"):
    """Display the customer analysis results"""
    
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
    
    # Feature Importance Section - Full width
    st.markdown("---")
    st.markdown("## 🔍 Why This Prediction?")
    st.markdown("### Key Drivers for This Customer's Churn Risk")
    
    # Create feature impact chart - Full width
    fig_features = create_feature_impact_chart(features_dict)
    st.plotly_chart(fig_features, use_container_width=True)
    
    st.markdown("""
    **How to Read This Chart:**
    - 🔴 **Red bars (positive values)**: Features pushing toward higher churn risk
    - 🔵 **Blue bars (negative values)**: Features reducing churn risk
    - **Bar length**: Indicates the strength of impact
    """)
    
    # SHAP Analysis Results - Side by side comparison
    st.markdown("---")
    st.markdown("## 📈 SHAP Analysis Results")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### 🔴 Top 5 Driving TOWARDS CHURN")
        for i, contrib in enumerate(positive_contribs, 1):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); 
                        padding: 12px; border-radius: 8px; margin-bottom: 8px; color: white;">
                <strong>{i}. {contrib['Feature']}</strong><br>
                <small>SHAP Impact: {contrib['SHAP_Value']:+.4f} | Value: {contrib['Value']:.3f}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("### 🟢 Top 5 Driving TOWARDS RETENTION")
        for i, contrib in enumerate(negative_contribs, 1):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); 
                        padding: 12px; border-radius: 8px; margin-bottom: 8px; color: white;">
                <strong>{i}. {contrib['Feature']}</strong><br>
                <small>SHAP Impact: {contrib['SHAP_Value']:+.4f} | Value: {contrib['Value']:.3f}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced All Feature Impacts Section
    st.markdown("---")
    st.markdown("## 📋 Complete Feature Impact Analysis")
    
    # Create a better visualization for all features
    display_enhanced_feature_impacts(features_dict)
    
    # SHAP Summary and Model Performance
    col_summary1, col_summary2, col_summary3 = st.columns(3)
    
    with col_summary1:
        base_value = explainer.expected_value
        st.metric("SHAP Base Value", f"{base_value:.4f}")
    
    with col_summary2:
        shap_sum = np.sum(shap_values[0])
        st.metric("SHAP Sum", f"{shap_sum:+.4f}")
    
    with col_summary3:
        confidence = max(model.predict_proba(sample_customer)[0])
        st.metric("Model Confidence", f"{confidence:.1%}")
    
    # Recommendations
    display_recommendations(probability)
    
    # AI Agent Analysis Section
    st.markdown("---")
    st.markdown("## 🤖 AI Agent Analysis (Optional)")
    st.markdown("""
    **Advanced AI Insights**: Click the button below to get AI-powered analysis including deeper insights, 
    speculation on churn reasons, and actionable recommendations.
    
    💡 **Note**: AI analysis is only triggered when you click the button - it does NOT run automatically when you select a customer.
    """)
    
    # Add button to trigger AI analysis
    if st.button("🚀 Run AI Agent Analysis", key=f"{tab_id}_ai_analysis_btn_{customer_id}", type="primary"):
        # Prepare customer data for agents
        customer_data_for_agents = {
            'customer_id': customer_id,
            'days_tenure': 365,  # Default values - you can extract from sample_customer if available
            'curr_ann_amt': 1500,
            'age_in_years': 35,
            'income_filled': 50000,
            'has_children': 0,
            'home_owner': 0,
            'college_degree': 0,
            'good_credit': 1,
            'is_married': 0,
            'length_of_residence_filled': 5
        }
        
        # Try to extract actual values from sample_customer if possible
        try:
            # This is a simplified extraction - you might need to adjust based on your data structure
            if hasattr(sample_customer, 'iloc') and len(sample_customer) > 0:
                # Try to get some common fields
                for col in sample_customer.columns:
                    col_lower = col.lower()
                    if 'tenure' in col_lower or 'days' in col_lower:
                        customer_data_for_agents['days_tenure'] = float(sample_customer.iloc[0][col])
                    elif 'age' in col_lower:
                        customer_data_for_agents['age_in_years'] = float(sample_customer.iloc[0][col])
                    elif 'income' in col_lower:
                        customer_data_for_agents['income_filled'] = float(sample_customer.iloc[0][col])
                    elif 'premium' in col_lower or 'amount' in col_lower:
                        customer_data_for_agents['curr_ann_amt'] = float(sample_customer.iloc[0][col])
        except Exception:
            pass  # Use default values if extraction fails
        
        # Call and display agent analysis
        call_and_display_agents(
            customer_data_for_agents, 
            feature_contributions,  # Use feature_contributions instead of features_dict
            float(probability),  # Ensure it's a Python float
            int(prediction)  # Ensure it's a Python int
        )
    else:
        st.info("👆 Click the button above to run AI agent analysis (requires GOOGLE_API_KEY environment variable)")
