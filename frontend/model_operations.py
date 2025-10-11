"""
Model operations for the Customer Churn Prediction Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
from sklearn.preprocessing import LabelEncoder
import os

@st.cache_resource
def load_model_and_data():
    """Load the trained model and process data"""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Load the XGBoost model
        model_path = os.path.join(script_dir, 'xgboost_churn_model.pkl')
        model = joblib.load(model_path)
        
        # Load the data from root/data folder
        data_path = os.path.join(project_root, 'data', 'autoinsurance_churn.csv')
        autoinsurance_df = pd.read_csv(data_path)
        
        # Define columns to exclude
        cols_to_drop = ['individual_id', 'address_id', 'date_of_birth', 'cust_orig_date', 'acct_suspd_date', 'Churn']
        
        # Get features
        feature_cols = [col for col in autoinsurance_df.columns if col not in cols_to_drop]
        X = autoinsurance_df[feature_cols].copy()
        y = autoinsurance_df['Churn']
        
        # Process features
        X_processed = X.copy()
        label_encoders = {}
        
        for col in X_processed.columns:
            if X_processed[col].dtype == 'object':
                X_processed[col] = X_processed[col].fillna('Unknown')
                le = LabelEncoder()
                X_processed[col] = le.fit_transform(X_processed[col].astype(str))
                label_encoders[col] = le
            else:
                X_processed[col] = X_processed[col].fillna(X_processed[col].median())
        
        # Create SHAP explainer
        explainer = shap.TreeExplainer(model)
        
        return model, X_processed, y, feature_cols, explainer, label_encoders, X
        
    except Exception as e:
        st.error(f"Error loading model or data: {e}")
        return None, None, None, None, None, None, None

def make_prediction(model, sample_customer):
    """Make prediction for a single customer"""
    try:
        prediction = model.predict(sample_customer)[0]
        probability = model.predict_proba(sample_customer)[0, 1]
        return prediction, probability
    except Exception as e:
        st.error(f"Error making prediction: {e}")
        return None, None

def calculate_shap_values(explainer, sample_customer, feature_cols):
    """Calculate SHAP values and feature contributions"""
    try:
        # Calculate SHAP values
        shap_values = explainer.shap_values(sample_customer)
        
        # Create feature contributions
        feature_contributions = []
        for i, feature in enumerate(feature_cols):
            shap_val = shap_values[0][i]
            feature_val = sample_customer.iloc[0, i]
            
            feature_contributions.append({
                'Feature': feature,
                'Value': feature_val,
                'SHAP_Value': shap_val,
                'Magnitude': abs(shap_val)
            })
        
        # Sort by absolute SHAP value
        feature_contributions.sort(key=lambda x: x['Magnitude'], reverse=True)
        
        # Get top contributing features
        positive_contribs = [f for f in feature_contributions if f['SHAP_Value'] > 0][:5]
        negative_contribs = [f for f in feature_contributions if f['SHAP_Value'] < 0][:5]
        
        # Create features dict for visualization
        features_dict = {f['Feature']: f['SHAP_Value'] for f in feature_contributions[:10]}
        
        return shap_values, feature_contributions, positive_contribs, negative_contribs, features_dict
        
    except Exception as e:
        st.error(f"Error calculating SHAP values: {e}")
        return None, None, None, None, None

def get_risk_level(churn_prob):
    """Determine risk level based on churn probability"""
    if churn_prob >= 0.7:
        return "HIGH RISK", "high-risk", "🔴"
    elif churn_prob >= 0.4:
        return "MEDIUM RISK", "medium-risk", "🟡"
    else:
        return "LOW RISK", "low-risk", "🟢"

def create_sample_customer_from_inputs(feature_inputs, feature_cols, X_processed, label_encoders):
    """Create a sample customer from user inputs"""
    sample_row = {}
    for col in feature_cols:
        if col in feature_inputs:
            val = feature_inputs[col]
            if col in label_encoders:
                # Encode categorical variable
                try:
                    encoded_val = label_encoders[col].transform([str(val)])[0]
                except:
                    encoded_val = 0  # Default for unknown categories
                sample_row[col] = encoded_val
            else:
                sample_row[col] = val
        else:
            # Use median for missing features
            sample_row[col] = X_processed[col].median()
    
    return pd.DataFrame([sample_row])

def get_important_features():
    """Get list of most important features for input"""
    return [
        'tenure', 'age', 'premium', 'claims_count', 'months_since_last_claim',
        'credit_score', 'annual_mileage', 'vehicle_year', 'vehicle_value', 'education_level'
    ]