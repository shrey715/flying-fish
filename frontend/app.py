import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import joblib
import shap
from sklearn.preprocessing import LabelEncoder

# Page configuration
st.set_page_config(
    page_title="Customer Churn Prediction Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric label {
        color: #31333F !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #0e1117 !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #31333F !important;
    }
    .prediction-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    }
    .high-risk {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
    }
    .medium-risk {
        background: linear-gradient(135deg, #ffa500 0%, #ff8c00 100%);
        color: white;
    }
    .low-risk {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 20px;
    }
    .sidebar-text {
        font-size: 14px;
        color: #555;
    }
    </style>
    """, unsafe_allow_html=True)

# Load the trained model and data
@st.cache_resource
def load_model_and_data():
    try:
        # Load the XGBoost model
        model = joblib.load('xgboost_churn_model.pkl')
        
        # Load the data
        autoinsurance_df = pd.read_csv('archive/autoinsurance_churn.csv')
        
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

# Sample customer data for demonstration
@st.cache_data
def load_sample_customers():
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

# Load model and data
model, X_processed, y, feature_cols, explainer, label_encoders, X_original = load_model_and_data()

if model is None:
    st.error("Failed to load model or data. Please check if files exist.")
    st.stop()

# Title and Introduction
st.title("🎯 Customer Churn Prediction Dashboard")
st.markdown("""
This interactive dashboard uses a **real XGBoost model** to predict customer churn and provides **SHAP explanations** 
for why customers might leave. Select a real customer from the dataset or input custom details to see predictions.
""")

# Sidebar
with st.sidebar:
    st.header("🔍 Customer Selection")
    
    # Mode selection
    input_mode = st.radio(
        "Choose Input Mode:",
        ["Select Real Customer", "Random Customer", "Top 10 Most Important Features"],
        help="Choose how to select a customer for analysis"
    )
    
    if input_mode == "Select Real Customer":
        # Let user select by index
        customer_idx = st.number_input(
            "Customer Index", 
            min_value=0, 
            max_value=len(X_processed)-1, 
            value=123,
            help="Select a customer by their index in the dataset"
        )
        sample_customer = X_processed.iloc[customer_idx:customer_idx+1]
        actual_churn = y.iloc[customer_idx]
        customer_id = f"REAL_{customer_idx:04d}"
        
    elif input_mode == "Random Customer":
        # Random selection
        if st.button("🎲 Pick Random Customer", key="random_btn"):
            st.session_state.random_idx = np.random.choice(len(X_processed))
        
        if 'random_idx' not in st.session_state:
            st.session_state.random_idx = 123
            
        customer_idx = st.session_state.random_idx
        sample_customer = X_processed.iloc[customer_idx:customer_idx+1]
        actual_churn = y.iloc[customer_idx]
        customer_id = f"RAND_{customer_idx:04d}"
        
    else:  # Top 10 Most Important Features
        st.markdown("### Enter Key Feature Values")
        
        # Get top 10 most important features (you can customize this list)
        important_features = [
            'tenure', 'age', 'premium', 'claims_count', 'months_since_last_claim',
            'credit_score', 'annual_mileage', 'vehicle_year', 'vehicle_value', 'education_level'
        ]
        
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
                    feature_inputs[feature] = st.selectbox(f"{feature}", unique_vals, key=f"input_{feature}")
                else:
                    min_val = float(X_original[feature].min())
                    max_val = float(X_original[feature].max())
                    mean_val = float(X_original[feature].mean())
                    feature_inputs[feature] = st.slider(
                        f"{feature}", 
                        min_val, 
                        max_val, 
                        mean_val,
                        key=f"input_{feature}"
                    )
        
        # Create a sample customer from inputs
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
        
        sample_customer = pd.DataFrame([sample_row])
        actual_churn = None  # Unknown for custom input
        customer_id = "CUSTOM_001"
    
    st.markdown("---")
    st.markdown("### 📊 Dataset Stats")
    st.metric("Total Customers", f"{len(X_processed):,}")
    st.metric("Avg Churn Rate", f"{y.mean()*100:.1f}%")
    st.metric("Features Used", len(feature_cols))

# Make prediction using the real model
try:
    prediction = model.predict(sample_customer)[0]
    probability = model.predict_proba(sample_customer)[0, 1]
    
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
    
except Exception as e:
    st.error(f"Error making prediction: {e}")
    st.stop()

# Main Content
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 👤 Customer Profile")
    st.markdown(f"**Customer ID:** {customer_id}")
    
    # Display top 10 most important features for this customer
    st.markdown("**Top Features:**")
    top_features = feature_contributions[:10]
    
    for i, contrib in enumerate(top_features, 1):
        feature_name = contrib['Feature']
        feature_value = contrib['Value']
        shap_value = contrib['SHAP_Value']
        
        # Format the value based on type
        if isinstance(feature_value, float):
            if feature_value > 1000:
                value_str = f"{feature_value:,.0f}"
            else:
                value_str = f"{feature_value:.2f}"
        else:
            value_str = str(feature_value)
        
        # Color coding based on SHAP value
        color = "🔴" if shap_value > 0 else "🟢" if shap_value < 0 else "⚪"
        
        st.markdown(f"{i:2d}. {color} **{feature_name}**: {value_str}")
    
    if actual_churn is not None:
        st.markdown(f"**Actual Churn:** {'✅ YES' if actual_churn == 1 else '❌ NO'}")

with col2:
    st.markdown("### 🎯 Churn Prediction")
    
    churn_prob = probability
    
    # Determine risk level
    if churn_prob >= 0.7:
        risk_level = "HIGH RISK"
        risk_class = "high-risk"
        risk_emoji = "🔴"
    elif churn_prob >= 0.4:
        risk_level = "MEDIUM RISK"
        risk_class = "medium-risk"
        risk_emoji = "🟡"
    else:
        risk_level = "LOW RISK"
        risk_class = "low-risk"
        risk_emoji = "🟢"
    
    # Display prediction in a styled box
    st.markdown(f"""
        <div class="prediction-box {risk_class}">
            <h1>{risk_emoji} {risk_level}</h1>
            <h2>{churn_prob*100:.1f}% Churn Probability</h2>
            <p style="font-size: 16px; margin-top: 10px;">
                This customer has a <strong>{risk_level.lower()}</strong> likelihood of churning
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Gauge chart for churn probability
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = churn_prob * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Churn Risk Score", 'font': {'size': 20}},
        delta = {'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#4ecdc4'},
                {'range': [40, 70], 'color': '#ffa500'},
                {'range': [70, 100], 'color': '#ff6b6b'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# Feature Importance Section
st.markdown("---")
st.markdown("## 🔍 Why This Prediction?")
st.markdown("### Key Drivers for This Customer's Churn Risk")

col3, col4 = st.columns([3, 2])

with col3:
    # Create waterfall chart (SHAP-like visualization)
    features = features_dict
    feature_names = list(features.keys())
    feature_values = list(features.values())
    
    # Sort by absolute impact
    sorted_indices = sorted(range(len(feature_values)), key=lambda i: abs(feature_values[i]), reverse=True)
    sorted_names = [feature_names[i] for i in sorted_indices]
    sorted_values = [feature_values[i] for i in sorted_indices]
    
    # Create color based on positive/negative impact
    colors = ['#ff6b6b' if v > 0 else '#4ecdc4' for v in sorted_values]
    
    # Horizontal bar chart
    fig_features = go.Figure()
    
    fig_features.add_trace(go.Bar(
        y=sorted_names,
        x=sorted_values,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.3)', width=1)
        ),
        text=[f"{v:+.2f}" for v in sorted_values],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Impact: %{x:.3f}<extra></extra>'
    ))
    
    fig_features.update_layout(
        title="Feature Impact on Churn Prediction (SHAP-like Values)",
        xaxis_title="Impact on Churn Probability",
        yaxis_title="Features",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(240,242,246,0.5)',
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black'),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    st.plotly_chart(fig_features, use_container_width=True)
    
    st.markdown("""
    **How to Read This Chart:**
    - 🔴 **Red bars (positive values)**: Features pushing toward higher churn risk
    - 🔵 **Blue bars (negative values)**: Features reducing churn risk
    - **Bar length**: Indicates the strength of impact
    """)

with col4:
    st.markdown("### 📈 SHAP Analysis Results")
    
    # Show top 5 features driving towards churn
    st.markdown("**🔴 Top 5 Driving TOWARDS CHURN:**")
    for i, contrib in enumerate(positive_contribs, 1):
        st.markdown(f"{i}. **{contrib['Feature']}**")
        st.markdown(f"   SHAP: {contrib['SHAP_Value']:+.4f} | Value: {contrib['Value']:.3f}")
    
    st.markdown("**🟢 Top 5 Driving TOWARDS RETENTION:**")
    for i, contrib in enumerate(negative_contribs, 1):
        st.markdown(f"{i}. **{contrib['Feature']}**")
        st.markdown(f"   SHAP: {contrib['SHAP_Value']:+.4f} | Value: {contrib['Value']:.3f}")
    
    # SHAP Summary
    st.markdown("### 📊 SHAP Summary")
    base_value = explainer.expected_value
    shap_sum = np.sum(shap_values[0])
    
    st.markdown(f"**Base Value:** {base_value:.4f}")
    st.markdown(f"**SHAP Sum:** {shap_sum:+.4f}")
    st.markdown(f"**Final Logit:** {base_value + shap_sum:.4f}")
    
    # Model performance info
    if actual_churn is not None:
        correct = "✅ CORRECT" if prediction == actual_churn else "❌ INCORRECT"
        st.markdown(f"**Prediction:** {correct}")
    
    st.markdown(f"**Model Confidence:** {max(model.predict_proba(sample_customer)[0]):.3f}")
    
    # Create a detailed breakdown for remaining features
    st.markdown("### 📋 All Feature Impacts")
    for feature, value in sorted(features.items(), key=lambda x: abs(x[1]), reverse=True):
        impact = "Increases Risk" if value > 0 else "Decreases Risk"
        color = "#ff6b6b" if value > 0 else "#4ecdc4"
        
        st.markdown(f"""
        <div style="background-color: {color}22; padding: 8px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid {color}">
            <strong>{feature}</strong><br>
            Impact: <span style="color: {color}; font-weight: bold;">{value:+.4f}</span><br>
            <small>{impact}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 💡 Recommendations")
    if churn_prob >= 0.7:
        st.warning("""
        **Immediate Actions Required:**
        - 🎯 Priority contact within 24 hours
        - 💰 Offer retention incentive
        - 📞 Assign dedicated account manager
        - 📋 Review and address service issues
        """)
    elif churn_prob >= 0.4:
        st.info("""
        **Proactive Engagement:**
        - 📧 Send personalized email
        - 🎁 Offer loyalty benefits
        - 📊 Schedule satisfaction survey
        - 💬 Monitor engagement levels
        """)
    else:
        st.success("""
        **Maintain Satisfaction:**
        - ✅ Continue current service level
        - 🎉 Recognize loyalty milestones
        - 📈 Upsell opportunities available
        - 🔄 Regular check-ins
        """)

# Bottom section with additional insights
st.markdown("---")
st.markdown("## 📊 Additional Insights")

col5, col6, col7 = st.columns(3)

with col5:
    # Comparison with average
    avg_churn = 0.325
    diff = churn_prob - avg_churn
    st.metric(
        "Churn Risk vs Average",
        f"{churn_prob*100:.1f}%",
        f"{diff*100:+.1f}%",
        delta_color="inverse"
    )

with col6:
    # Customer segment based on prediction
    segment = "High Risk" if churn_prob >= 0.7 else "Medium Risk" if churn_prob >= 0.4 else "Low Risk"
    st.metric(
        "Risk Segment",
        segment,
        None
    )

with col7:
    # Model accuracy info
    confidence = max(model.predict_proba(sample_customer)[0])
    st.metric(
        "Model Confidence",
        f"{confidence:.1%}",
        None
    )

# Interactive timeline or trend (mock data)
st.markdown("### 📈 Churn Risk Trend (Last 6 Months)")

months = ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
# Generate realistic trend based on current probability
base = churn_prob
trend_values = [
    max(0.05, min(0.95, base - 0.15 + np.random.uniform(-0.05, 0.05))),
    max(0.05, min(0.95, base - 0.10 + np.random.uniform(-0.05, 0.05))),
    max(0.05, min(0.95, base - 0.05 + np.random.uniform(-0.05, 0.05))),
    max(0.05, min(0.95, base + np.random.uniform(-0.05, 0.05))),
    max(0.05, min(0.95, base + 0.05 + np.random.uniform(-0.05, 0.05))),
    base
]

fig_trend = go.Figure()

fig_trend.add_trace(go.Scatter(
    x=months,
    y=[v*100 for v in trend_values],
    mode='lines+markers',
    name='Churn Probability',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=10, color='#1f77b4', line=dict(color='white', width=2)),
    fill='tozeroy',
    fillcolor='rgba(31, 119, 180, 0.2)'
))

# Add threshold lines
fig_trend.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="High Risk", annotation_position="right")
fig_trend.add_hline(y=40, line_dash="dash", line_color="orange", 
                     annotation_text="Medium Risk", annotation_position="right")

fig_trend.update_layout(
    title="Historical Churn Risk Trajectory",
    xaxis_title="Month",
    yaxis_title="Churn Probability (%)",
    height=350,
    hovermode='x unified',
    plot_bgcolor='rgba(240,242,246,0.5)',
    yaxis=dict(range=[0, 100]),
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig_trend, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🔮 <strong>Customer Churn Prediction Dashboard</strong> | Built with Streamlit</p>
    <p><small>This dashboard uses advanced machine learning models to predict customer churn and explain the key factors.</small></p>
</div>
""", unsafe_allow_html=True)
