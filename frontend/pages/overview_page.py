"""
Overview Page - Landing page with summary
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def show(model, X_processed, y, feature_cols, explainer):
    """Display the overview page"""
    
    st.title("🏠 Customer Churn Prediction Dashboard")
    
    st.markdown("""
    Welcome to the **AI-Powered Customer Churn Prediction Dashboard**. This interactive tool helps you:
    
    - 🎯 **Predict individual customer churn** with high accuracy
    - 🔍 **Understand the reasons** behind churn predictions using SHAP explainability
    - 📊 **Analyze aggregate trends** across your entire customer base
    - 🗺️ **Identify regional patterns** and high-risk segments
    - 💡 **Get actionable recommendations** for customer retention
    """)
    
    # Key metrics
    st.markdown("## 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    total_customers = len(X_processed)
    churn_rate = y.mean()
    churned_customers = int(y.sum())
    retained_customers = total_customers - churned_customers
    
    with col1:
        st.metric(
            "Total Customers",
            f"{total_customers:,}",
            help="Total number of customers in the dataset"
        )
    
    with col2:
        st.metric(
            "Overall Churn Rate",
            f"{churn_rate*100:.1f}%",
            delta=f"-{(0.35-churn_rate)*100:.1f}% vs industry avg",
            delta_color="inverse",
            help="Percentage of customers who have churned"
        )
    
    with col3:
        st.metric(
            "Churned Customers",
            f"{churned_customers:,}",
            help="Number of customers who have left"
        )
    
    with col4:
        st.metric(
            "Retained Customers",
            f"{retained_customers:,}",
            help="Number of customers still active"
        )
    
    st.markdown("---")
    
    # Quick insights
    st.markdown("## 🔍 Quick Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Model Performance")
        st.info("""
        **XGBoost Model Metrics:**
        - ✅ Trained on real customer data
        - 🎯 Uses SHAP for explainability
        - 🔬 Analyzes {} features
        - ⚡ Real-time predictions
        """.format(len(feature_cols)))
    
    with col2:
        st.markdown("### 🎯 Dashboard Features")
        st.success("""
        **Available Analyses:**
        - 👤 Individual customer risk assessment
        - 📊 Population-wide churn trends
        - 🗺️ Geographic risk mapping
        - 💡 AI-driven recommendations
        - 📈 Feature importance analysis
        """)
    
    st.markdown("---")
    
    # Churn distribution
    st.markdown("## 📊 Churn Distribution")
    
    fig_dist = go.Figure()
    
    fig_dist.add_trace(go.Pie(
        labels=['Retained', 'Churned'],
        values=[retained_customers, churned_customers],
        marker=dict(
            colors=['#4ecdc4', '#ff6b6b'],
            line=dict(color='white', width=2)
        ),
        textinfo='percent',
        textfont=dict(size=16, color='white'),
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>',
        hole=0  # Simple pie chart, no hole
    ))
    
    fig_dist.update_layout(
        title="Customer Retention vs Churn",
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=150)  # Add right margin for legend
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)
    
    st.markdown("---")
    
    # Navigation guide
    st.markdown("## 🧭 How to Use This Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 👤 Single Customer Analysis
        
        Analyze individual customers to:
        - View detailed risk scores
        - Understand churn drivers for specific customers
        - Get personalized retention recommendations
        - See customer profile and history
        
        **Use when:** You need to assess or take action on individual accounts
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Aggregate Trends Dashboard
        
        Analyze your entire customer base to:
        - Identify high-risk regions and segments
        - Understand top churn drivers across all customers
        - View risk distribution and trends
        - Prioritize retention efforts at scale
        
        **Use when:** You need strategic insights for business planning
        """)
    
    st.markdown("---")
