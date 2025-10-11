"""
Risk Assessment Agent
Runs pre-trained ML model and computes SHAP explainability
"""

import numpy as np
import pandas as pd
import joblib
import shap
from typing import Dict, Any
import os


class RiskAssessmentAgent:
    """Agent for ML-based risk assessment with SHAP explainability"""
    
    def __init__(self, model_path: str, scaler_path: str, features_path: str):
        """Initialize with model artifacts"""
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_names = joblib.load(features_path)
        
        # Initialize SHAP explainer
        self.explainer = shap.TreeExplainer(self.model)
        
        print("✅ Risk Assessment Agent initialized")
    
    def assess_risk(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess customer churn risk with explainability
        
        Args:
            customer_data: Dictionary with customer attributes
            
        Returns:
            Dictionary with risk metrics and SHAP values
        """
        # Engineer features
        processed_features = self._engineer_features(customer_data)
        
        # Create feature vector
        feature_vector = np.array([[
            processed_features.get(f, 0) for f in self.feature_names
        ]])
        
        # Scale features
        scaled_features = self.scaler.transform(feature_vector)
        
        # Make prediction
        churn_probability = float(self.model.predict_proba(scaled_features)[0, 1])
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(scaled_features)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Get feature importances
        shap_dict = {
            feat: float(val) 
            for feat, val in zip(self.feature_names, shap_values[0])
        }
        
        # Get top factors
        top_factors = sorted(
            [
                {
                    'feature': feat,
                    'value': float(processed_features.get(feat, 0)),
                    'shap_value': val,
                    'impact': 'increases' if val > 0 else 'decreases',
                    'importance': abs(val)
                }
                for feat, val in shap_dict.items()
            ],
            key=lambda x: x['importance'],
            reverse=True
        )[:5]
        
        # Determine risk category
        if churn_probability < 0.3:
            risk_category = 'Low'
        elif churn_probability < 0.5:
            risk_category = 'Medium'
        elif churn_probability < 0.7:
            risk_category = 'High'
        else:
            risk_category = 'Critical'
        
        # Calculate confidence
        confidence_score = abs(churn_probability - 0.5) * 2
        confidence_level = 'High' if confidence_score > 0.4 else 'Medium' if confidence_score > 0.2 else 'Low'
        
        return {
            'customer_data': customer_data,
            'processed_features': processed_features,
            'churn_probability': churn_probability,
            'risk_category': risk_category,
            'confidence_level': confidence_level,
            'confidence_score': confidence_score,
            'shap_values': shap_dict,
            'top_factors': top_factors,
            'base_value': float(self.explainer.expected_value[1] if isinstance(self.explainer.expected_value, np.ndarray) else self.explainer.expected_value)
        }
    
    def _engineer_features(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Engineer features from raw customer data"""
        processed = customer_data.copy()
        
        # Extract values
        days_tenure = customer_data.get('days_tenure', 730)
        curr_ann_amt = customer_data.get('curr_ann_amt', 1000)
        income = customer_data.get('income_filled', 50000)
        good_credit = customer_data.get('good_credit', 1)
        home_owner = customer_data.get('home_owner', 1)
        length_res = customer_data.get('length_of_residence_filled', 0)
        
        # Tenure features
        processed['account_age_years'] = days_tenure / 365.25
        processed['very_short_tenure'] = 1 if days_tenure < 180 else 0
        processed['very_long_tenure'] = 1 if days_tenure > 3650 else 0
        
        # Premium features
        processed['premium_per_day'] = curr_ann_amt / 365
        
        # Income features
        processed['income_available'] = 1
        processed['income_to_premium_ratio'] = income / (curr_ann_amt + 1)
        
        # Residence features
        processed['is_stable_resident'] = 1 if length_res >= 5 else 0
        
        # Risk score
        processed['risk_score'] = (
            (1 - good_credit) * 0.3 +
            (1 - home_owner) * 0.2 +
            processed['very_short_tenure'] * 0.3 +
            (1 if processed['income_to_premium_ratio'] < 50 else 0) * 0.2
        )
        
        # Categorical encoding defaults
        processed['cust_orig_year'] = 2020
        processed['cust_orig_month'] = 1
        processed['cust_orig_quarter'] = 1
        processed['tenure_segment_encoded'] = 2
        processed['premium_segment_encoded'] = 2
        processed['age_group_encoded'] = 2
        processed['income_segment_encoded'] = 2
        processed['state_filled_encoded'] = 0
        processed['home_value_status_encoded'] = 0
        
        # Ensure all expected features exist
        for feat in self.feature_names:
            if feat not in processed:
                processed[feat] = 0
        
        return processed
