"""
CSS styles for the Customer Churn Prediction Dashboard
"""

def get_custom_css():
    """Returns the custom CSS for the dashboard"""
    return """
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
    """

def get_feature_impact_style(color):
    """Returns inline style for feature impact display"""
    return f"""
    background-color: {color}22; 
    padding: 8px; 
    border-radius: 5px; 
    margin-bottom: 5px; 
    border-left: 3px solid {color}
    """

def get_prediction_box_html(risk_level, risk_class, risk_emoji, churn_prob):
    """Returns HTML for the prediction box"""
    return f"""
        <div class="prediction-box {risk_class}">
            <h1>{risk_emoji} {risk_level}</h1>
            <h2>{churn_prob*100:.1f}% Churn Probability</h2>
            <p style="font-size: 16px; margin-top: 10px;">
                This customer has a <strong>{risk_level.lower()}</strong> likelihood of churning
            </p>
        </div>
    """

def get_footer_html():
    """Returns HTML for the footer"""
    return """
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>🔮 <strong>Customer Churn Prediction Dashboard</strong> | Built with Streamlit</p>
        <p><small>This dashboard uses advanced machine learning models to predict customer churn and explain the key factors.</small></p>
    </div>
    """