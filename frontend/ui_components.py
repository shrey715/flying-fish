"""
UI components for the Customer Churn Prediction Dashboard
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from styles import get_feature_impact_style

def create_sidebar(X_processed, y, feature_cols):
    """Create and populate the sidebar"""
    with st.sidebar:
        st.header("🔍 Customer Selection")
        
        # Mode selection
        input_mode = st.radio(
            "Choose Input Mode:",
            ["Select Real Customer", "Random Customer", "Top 10 Most Important Features"],
            help="Choose how to select a customer for analysis"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Dataset Stats")
        st.metric("Total Customers", f"{len(X_processed):,}")
        st.metric("Avg Churn Rate", f"{y.mean()*100:.1f}%")
        st.metric("Features Used", len(feature_cols))
        
        return input_mode

def display_customer_profile(customer_id, feature_contributions, actual_churn):
    """Display customer profile information"""
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

def create_gauge_chart(churn_prob):
    """Create gauge chart for churn probability"""
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
    return fig_gauge

def create_feature_impact_chart(features_dict):
    """Create horizontal bar chart for feature impacts"""
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
    
    return fig_features

def display_shap_analysis(positive_contribs, negative_contribs, explainer, shap_values, model, sample_customer, prediction, actual_churn):
    """Display SHAP analysis results"""
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

def display_all_feature_impacts(features):
    """Display all feature impacts in styled boxes"""
    st.markdown("### 📋 All Feature Impacts")
    for feature, value in sorted(features.items(), key=lambda x: abs(x[1]), reverse=True):
        impact = "Increases Risk" if value > 0 else "Decreases Risk"
        color = "#ff6b6b" if value > 0 else "#4ecdc4"
        
        st.markdown(f"""
        <div style="{get_feature_impact_style(color)}">
            <strong>{feature}</strong><br>
            Impact: <span style="color: {color}; font-weight: bold;">{value:+.4f}</span><br>
            <small>{impact}</small>
        </div>
        """, unsafe_allow_html=True)

def display_recommendations(churn_prob):
    """Display recommendations based on churn probability"""
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

def display_metrics(churn_prob, model, sample_customer):
    """Display additional metrics"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Comparison with average
        avg_churn = 0.325
        diff = churn_prob - avg_churn
        st.metric(
            "Churn Risk vs Average",
            f"{churn_prob*100:.1f}%",
            f"{diff*100:+.1f}%",
            delta_color="inverse"
        )

    with col2:
        # Customer segment based on prediction
        segment = "High Risk" if churn_prob >= 0.7 else "Medium Risk" if churn_prob >= 0.4 else "Low Risk"
        st.metric(
            "Risk Segment",
            segment,
            None
        )

    with col3:
        # Model accuracy info
        confidence = max(model.predict_proba(sample_customer)[0])
        st.metric(
            "Model Confidence",
            f"{confidence:.1%}",
            None
        )

def create_trend_chart(months, trend_values):
    """Create trend chart for churn risk over time"""
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
    
    return fig_trend