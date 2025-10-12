"""
Data operations for the Customer Churn Prediction Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def load_sample_customers():
    """Load sample customer data for demonstration"""
    customers = {
        "Customer 1 - High Risk": {
            "id": "CUST001",
            "churn_probability": 0.87,
            "age": 65,
            "tenure_months": 3,
            "monthly_premium": 245,
            "claims_count": 5,
            "customer_service_calls": 8,
            "payment_method": "Manual",
            "contract_type": "Monthly",
            "features": {
                "Customer Service Calls": 0.25,
                "Claims Count": 0.22,
                "Short Tenure": 0.18,
                "Manual Payment": 0.12,
                "Monthly Contract": 0.10
            }
        },
        "Customer 2 - Medium Risk": {
            "id": "CUST002",
            "churn_probability": 0.54,
            "age": 42,
            "tenure_months": 18,
            "monthly_premium": 180,
            "claims_count": 2,
            "customer_service_calls": 4,
            "payment_method": "Auto",
            "contract_type": "Semi-Annual",
            "features": {
                "Customer Service Calls": 0.15,
                "Premium Amount": 0.12,
                "Claims Count": 0.10,
                "Tenure": 0.09,
                "Contract Type": 0.08
            }
        },
        "Customer 3 - Low Risk": {
            "id": "CUST003",
            "churn_probability": 0.18,
            "age": 35,
            "tenure_months": 48,
            "monthly_premium": 120,
            "claims_count": 0,
            "customer_service_calls": 1,
            "payment_method": "Auto",
            "contract_type": "Annual",
            "features": {
                "Long Tenure": -0.20,
                "Auto Payment": -0.15,
                "Annual Contract": -0.12,
                "Low Claims": -0.10,
                "Few Service Calls": -0.08
            }
        },
        "Customer 4 - High Risk": {
            "id": "CUST004",
            "churn_probability": 0.76,
            "age": 58,
            "tenure_months": 6,
            "monthly_premium": 310,
            "claims_count": 4,
            "customer_service_calls": 6,
            "payment_method": "Manual",
            "contract_type": "Monthly",
            "features": {
                "High Premium": 0.20,
                "Customer Service Calls": 0.18,
                "Claims Count": 0.16,
                "Manual Payment": 0.12,
                "Short Tenure": 0.10
            }
        },
        "Customer 5 - Low Risk": {
            "id": "CUST005",
            "churn_probability": 0.23,
            "age": 29,
            "tenure_months": 36,
            "monthly_premium": 95,
            "claims_count": 1,
            "customer_service_calls": 2,
            "payment_method": "Auto",
            "contract_type": "Annual",
            "features": {
                "Long Tenure": -0.18,
                "Low Premium": -0.14,
                "Annual Contract": -0.12,
                "Auto Payment": -0.10,
                "Few Service Calls": -0.08
            }
        }
    }
    return customers

def get_customer_by_mode(input_mode, X_processed, y, feature_cols, X_original, label_encoders, key_prefix=""):
    """Get customer data based on input mode selection"""
    if input_mode == "Select Real Customer":
        # Let user select by index
        customer_idx = st.number_input(
            "Customer Index", 
            min_value=0, 
            max_value=len(X_processed)-1, 
            value=123,
            help="Select a customer by their index in the dataset",
            key=f"{key_prefix}_customer_index_input"
        )
        sample_customer = X_processed.iloc[customer_idx:customer_idx+1]
        actual_churn = y.iloc[customer_idx]
        customer_id = f"REAL_{customer_idx:04d}"
        return sample_customer, actual_churn, customer_id
        
    else:  # Custom Feature Selection
        from model_operations import get_important_features, create_sample_customer_from_inputs
        
        st.markdown("### Enter Key Feature Values")
        
        # Get top 10 most important features
        important_features = get_important_features()
        
        # Filter to only features that exist in our dataset
        available_important = [f for f in important_features if f in feature_cols][:10]
        if len(available_important) < 10:
            # Fill with other available features
            remaining_features = [f for f in feature_cols if f not in available_important]
            available_important.extend(remaining_features[:10-len(available_important)])
        
        # Create input for each important feature
        feature_inputs = {}
        for feature in available_important:
            if feature in X_original.columns:
                if X_original[feature].dtype == 'object':
                    unique_vals = X_original[feature].dropna().unique()[:10]  # Limit options
                    feature_inputs[feature] = st.selectbox(f"{feature}", unique_vals, key=f"{key_prefix}_input_{feature}")
                else:
                    min_val = float(X_original[feature].min())
                    max_val = float(X_original[feature].max())
                    mean_val = float(X_original[feature].mean())
                    feature_inputs[feature] = st.slider(
                        f"{feature}", 
                        min_val, 
                        max_val, 
                        mean_val,
                        key=f"{key_prefix}_input_{feature}"
                    )
        
        # Create a sample customer from inputs
        sample_customer = create_sample_customer_from_inputs(
            feature_inputs, feature_cols, X_processed, label_encoders
        )
        actual_churn = None  # Unknown for custom input
        customer_id = "CUSTOM_001"
        return sample_customer, actual_churn, customer_id

def generate_trend_data(churn_prob):
    """Generate mock trend data for the last 6 months"""
    months = ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
    base = churn_prob
    trend_values = [
        max(0.05, min(0.95, base - 0.15 + np.random.uniform(-0.05, 0.05))),
        max(0.05, min(0.95, base - 0.10 + np.random.uniform(-0.05, 0.05))),
        max(0.05, min(0.95, base - 0.05 + np.random.uniform(-0.05, 0.05))),
        max(0.05, min(0.95, base + np.random.uniform(-0.05, 0.05))),
        max(0.05, min(0.95, base + 0.05 + np.random.uniform(-0.05, 0.05))),
        base
    ]
    return months, trend_values