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


def call_agent_analysis(customer_data, feature_contributions, churn_probability, prediction):
    """
    Call the backend API to analyze customer with AI agents
    
    Args:
        customer_data: Dictionary with customer information
        feature_contributions: List of feature impacts from SHAP analysis
        churn_probability: Predicted churn probability
        prediction: Binary prediction (0/1)
    
    Returns:
        Dictionary with agent analysis results
    """
    import requests
    import streamlit as st
    
    # Backend API URL
    API_URL = "http://localhost:8001/api/analyze-with-agents"
    
    try:
        # Prepare features_dict for API (convert feature_contributions to the expected format)
        features_dict_for_api = []
        for contrib in feature_contributions[:10]:  # Top 10 features
            # Ensure all values are JSON serializable
            feature_name = str(contrib['Feature'])
            feature_value = contrib['Value']
            shap_value = contrib['SHAP_Value']
            
            # Convert numpy types to Python types
            if hasattr(feature_value, 'item'):  # numpy scalar
                feature_value = feature_value.item()
            if hasattr(shap_value, 'item'):  # numpy scalar
                shap_value = shap_value.item()
                
            features_dict_for_api.append({
                "Feature": feature_name,
                "Value": float(feature_value),  # Convert to Python float
                "SHAP_Value": float(shap_value),  # Convert to Python float
                "Impact": "increases churn risk" if float(shap_value) > 0 else "decreases churn risk"
            })
        
        # Ensure customer data values are also JSON serializable
        customer_data_clean = {}
        for key, value in customer_data.items():
            if hasattr(value, 'item'):  # numpy scalar
                customer_data_clean[key] = value.item()
            else:
                customer_data_clean[key] = value
        
        # Prepare payload
        payload = {
            "customer_data": {
                "customer_type": "existing",
                "days_tenure": float(customer_data_clean.get('days_tenure', 365)),
                "curr_ann_amt": float(customer_data_clean.get('curr_ann_amt', 1500)),
                "age_in_years": float(customer_data_clean.get('age_in_years', 35)),
                "income_filled": float(customer_data_clean.get('income_filled', 50000)),
                "has_children": int(customer_data_clean.get('has_children', 0)),
                "home_owner": int(customer_data_clean.get('home_owner', 0)),
                "college_degree": int(customer_data_clean.get('college_degree', 0)),
                "good_credit": int(customer_data_clean.get('good_credit', 1)),
                "is_married": int(customer_data_clean.get('is_married', 0)),
                "length_of_residence_filled": float(customer_data_clean.get('length_of_residence_filled', 5))
            },
            "features_dict": features_dict_for_api,
            "churn_probability": float(churn_probability),
            "prediction": int(prediction)
        }
        
        # Make API call
        response = requests.post(API_URL, json=payload, timeout=60)  # Increased timeout for AI agents
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"API call failed with status {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Backend API not available. Start the backend server with: `cd backend && python main.py`")
        return None
    except requests.exceptions.Timeout:
        st.warning("⚠️ API call timed out. The agents may be processing...")
        return None
    except TypeError as e:
        if "JSON serializable" in str(e):
            st.error(f"❌ Data serialization error: {str(e)}")
            st.info("Debug info: Check that all feature values are proper Python types, not numpy types")
        else:
            st.error(f"❌ Type error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error calling agent analysis: {str(e)}")
        # Add some debug information
        st.info("Debug information:")
        st.write("Payload structure:", {
            "customer_data_keys": list(payload.get("customer_data", {}).keys()) if 'payload' in locals() else "Not created",
            "features_count": len(payload.get("features_dict", [])) if 'payload' in locals() else "Not created",
            "churn_probability_type": type(payload.get("churn_probability")) if 'payload' in locals() else "Not created"
        })
        return None