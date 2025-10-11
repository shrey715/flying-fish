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
    display_metrics, create_trend_chart, call_and_display_agents
)
from styles import get_prediction_box_html

def show(model, X_processed, y, feature_cols, explainer, label_encoders, X_original):
    """Display the single customer analysis page"""
    
    st.title("👤 Single Customer Churn Analysis")
    st.markdown("""
    Analyze individual customers to understand their churn risk and the key factors driving their behavior.
    Select a customer from the dataset or input custom details.
    """)
    
    # Customer selection sidebar
    with st.sidebar:
        st.markdown("---")
        st.header("🔍 Customer Selection")
        
        # Mode selection
        input_mode = st.radio(
            "Choose Input Mode:",
            ["Select Real Customer", "Random Customer", "Top 10 Most Important Features"],
            help="Choose how to select a customer for analysis"
        )
    
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
    
    # AI Agent Analysis Section
    st.markdown("---")
    st.markdown("## 🤖 AI Agent Analysis")
    st.markdown("""
    **Advanced AI Insights**: Our AI agents analyze the prediction using cutting-edge language models 
    to provide deeper insights, speculation on churn reasons, and actionable recommendations.
    """)
    
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
    
    # What-If Scenario Planner
    st.markdown("---")
    st.markdown("## 🕹️ What-If Scenario Planner")
    st.markdown("""
    **Interactive Retention Tool**: Adjust key customer features to see real-time impact on churn risk.
    Find the optimal interventions to retain this customer.
    """)
    
    # Add what-if analysis
    display_whatif_planner(
        model, sample_customer, X_original, feature_cols, 
        explainer, probability, feature_contributions
    )
    
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


def display_whatif_planner(model, sample_customer, X_original, feature_cols, 
                           explainer, baseline_probability, feature_contributions):
    """Display the What-If Scenario Planner"""
    import plotly.graph_objects as go
    
    # Introduction
    col_intro1, col_intro2 = st.columns([2, 1])
    
    with col_intro1:
        st.info("""
        💡 **How to use**: Adjust the sliders below to simulate changes to the customer's profile.
        The model will instantly recalculate the churn probability and show you the impact of your intervention.
        """)
    
    with col_intro2:
        st.metric(
            "Baseline Churn Risk",
            f"{baseline_probability*100:.1f}%",
            help="Original churn probability before any changes"
        )
    
    # Get top actionable features (numeric features with high impact)
    actionable_features = get_actionable_features(
        feature_contributions, sample_customer, X_original, feature_cols
    )
    
    if not actionable_features:
        st.warning("No actionable numeric features found for this customer.")
        return
    
    # Create a copy of the customer data for modifications
    modified_customer = sample_customer.copy()
    
    # Scenario selection
    st.markdown("### 🎯 Intervention Scenarios")
    
    scenario_type = st.radio(
        "Choose scenario type:",
        ["Custom Adjustments", "Pre-defined Scenarios", "Goal-Seeking"],
        horizontal=True,
        help="Select how you want to adjust the customer features"
    )
    
    if scenario_type == "Custom Adjustments":
        display_custom_adjustments(
            model, modified_customer, actionable_features, 
            baseline_probability, explainer, feature_cols
        )
    
    elif scenario_type == "Pre-defined Scenarios":
        display_predefined_scenarios(
            model, modified_customer, actionable_features, 
            baseline_probability, sample_customer
        )
    
    else:  # Goal-Seeking
        display_goal_seeking(
            model, modified_customer, actionable_features, 
            baseline_probability, sample_customer
        )


def get_actionable_features(feature_contributions, sample_customer, X_original, feature_cols):
    """Get the top actionable (numeric) features that can be adjusted"""
    actionable = []
    
    # Get top 15 most impactful features (to find enough numeric ones)
    top_features = feature_contributions[:15]
    
    # Categorical feature keywords (these should use selectbox, not slider)
    categorical_keywords = ['gender', 'education', 'marital', 'employment', 'state', 
                           'vehicle_type', 'policy', 'coverage', 'sales_channel',
                           'children', 'number_of']
    
    for contrib in top_features:
        feature_name = contrib['Feature']
        
        # Check if it's a numeric feature
        if feature_name in sample_customer.columns:
            feature_idx = feature_cols.index(feature_name)
            original_value = sample_customer.iloc[0, feature_idx]
            
            # Skip categorical features
            is_categorical = any(keyword in feature_name.lower() for keyword in categorical_keywords)
            if is_categorical:
                continue
            
            # Check if it's numeric and has reasonable range
            if isinstance(original_value, (int, float, np.integer, np.floating)):
                # Get min/max from original data if available
                if feature_name in X_original.columns and X_original[feature_name].dtype in ['int64', 'float64']:
                    min_val = float(X_original[feature_name].min())
                    max_val = float(X_original[feature_name].max())
                    mean_val = float(X_original[feature_name].mean())
                    std_val = float(X_original[feature_name].std())
                else:
                    # Fallback if not in original data
                    min_val = float(original_value * 0.5)
                    max_val = float(original_value * 1.5)
                    mean_val = float(original_value)
                    std_val = float(abs(original_value * 0.2))
                
                # Ensure min != max
                if abs(max_val - min_val) < 0.01:
                    if original_value != 0:
                        min_val = original_value * 0.5
                        max_val = original_value * 1.5
                    else:
                        min_val = -10.0
                        max_val = 10.0
                
                # Ensure current value is within range
                current_val = float(original_value)
                if current_val < min_val:
                    min_val = current_val * 0.9
                if current_val > max_val:
                    max_val = current_val * 1.1
                
                # Only add if we have a valid range
                if max_val > min_val:
                    actionable.append({
                        'name': feature_name,
                        'current_value': current_val,
                        'min_value': min_val,
                        'max_value': max_val,
                        'mean_value': mean_val,
                        'std_value': std_val,
                        'shap_value': contrib['SHAP_Value'],
                        'impact_direction': 'increases' if contrib['SHAP_Value'] > 0 else 'decreases'
                    })
    
    return actionable


def display_custom_adjustments(model, modified_customer, actionable_features, 
                               baseline_probability, explainer, feature_cols):
    """Display custom adjustment controls"""
    
    st.markdown("#### Adjust Key Features")
    st.caption("Move sliders to test different intervention strategies")
    
    # Create columns for sliders
    adjustments = {}
    changes_made = False
    
    for i, feature in enumerate(actionable_features[:6]):  # Limit to top 6
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Create slider with step size
            step_size = (feature['max_value'] - feature['min_value']) / 100
            if step_size == 0:
                step_size = 0.01
            
            new_value = st.slider(
                f"**{feature['name']}**",
                min_value=feature['min_value'],
                max_value=feature['max_value'],
                value=feature['current_value'],
                step=step_size,
                key=f"slider_{feature['name']}",
                help=f"Original: {feature['current_value']:.2f} | Range: {feature['min_value']:.1f} - {feature['max_value']:.1f}"
            )
            
            adjustments[feature['name']] = new_value
            
            if abs(new_value - feature['current_value']) > 0.01:
                changes_made = True
        
        with col2:
            # Show change amount (not percentage when going to negative)
            change_amount = new_value - feature['current_value']
            if feature['current_value'] != 0:
                change_pct = (change_amount / abs(feature['current_value']) * 100)
            else:
                change_pct = 0
            
            # Display change amount clearly
            st.metric(
                "Adjustment",
                f"{change_amount:+.2f}",
                delta=f"{change_pct:+.1f}%" if abs(feature['current_value']) > 0.01 else "N/A"
            )
    
    if changes_made:
        # Apply adjustments
        for feature_name, new_value in adjustments.items():
            feature_idx = modified_customer.columns.get_loc(feature_name)
            modified_customer.iloc[0, feature_idx] = new_value
        
        # Recalculate prediction
        new_prediction, new_probability = make_prediction(model, modified_customer)
        
        # Calculate impact
        probability_change = new_probability - baseline_probability
        risk_reduction_pct_points = -probability_change * 100  # Percentage points
        
        # Display results
        st.markdown("---")
        st.markdown("### 📊 Impact Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Original Risk",
                f"{baseline_probability*100:.1f}%",
                help="Baseline churn probability before changes"
            )
        
        with col2:
            st.metric(
                "New Risk",
                f"{new_probability*100:.1f}%",
                delta=f"{probability_change*100:.1f} pts",
                delta_color="inverse",
                help="New churn probability after intervention"
            )
        
        with col3:
            old_level = get_risk_level(baseline_probability)[0]
            new_level = get_risk_level(new_probability)[0]
            level_change = "→ " + new_level if old_level != new_level else "Same"
            st.metric(
                "Risk Level",
                old_level,
                delta=level_change,
                help="Risk category before intervention"
            )
        
        with col4:
            # Show absolute change in percentage points
            st.metric(
                "Change",
                f"{abs(risk_reduction_pct_points):.1f} pts",
                delta="↓ Better" if risk_reduction_pct_points > 0 else "↑ Worse",
                delta_color="normal" if risk_reduction_pct_points > 0 else "inverse",
                help="Change in churn risk (percentage points)"
            )
        
        # Visualization
        display_scenario_comparison(baseline_probability, new_probability, adjustments, actionable_features)
        
        # AI-powered recommendations
        generate_intervention_recommendations(
            adjustments, actionable_features, probability_change, new_probability
        )


def display_predefined_scenarios(model, modified_customer, actionable_features, 
                                 baseline_probability, original_customer):
    """Display pre-defined intervention scenarios"""
    
    st.markdown("#### Choose Retention Strategy")
    
    scenarios = {
        "🎁 Premium Discount (10%)": {
            "description": "Reduce premium by 10% to incentivize retention",
            "adjustments": {}
        },
        "🎁 Premium Discount (20%)": {
            "description": "Aggressive 20% premium discount",
            "adjustments": {}
        },
        "💎 VIP Treatment": {
            "description": "Improve service quality and reduce claims processing time",
            "adjustments": {}
        },
        "📞 Proactive Engagement": {
            "description": "Increase customer touchpoints and reduce service calls",
            "adjustments": {}
        },
        "🔄 Policy Upgrade": {
            "description": "Improve coverage and customer satisfaction",
            "adjustments": {}
        }
    }
    
    # Build scenario adjustments based on available features
    for feature in actionable_features:
        name = feature['name'].lower()
        
        # Premium discount scenarios
        if 'premium' in name or 'price' in name or 'cost' in name:
            scenarios["🎁 Premium Discount (10%)"]["adjustments"][feature['name']] = feature['current_value'] * 0.9
            scenarios["🎁 Premium Discount (20%)"]["adjustments"][feature['name']] = feature['current_value'] * 0.8
        
        # VIP treatment
        if 'claim' in name or 'service' in name:
            if feature['shap_value'] > 0:  # If it increases risk
                scenarios["💎 VIP Treatment"]["adjustments"][feature['name']] = feature['current_value'] * 0.7
        
        # Proactive engagement
        if 'call' in name or 'contact' in name or 'complaint' in name:
            if feature['shap_value'] > 0:
                scenarios["📞 Proactive Engagement"]["adjustments"][feature['name']] = feature['current_value'] * 0.6
        
        # Policy upgrade
        if 'coverage' in name or 'satisfaction' in name or 'tenure' in name:
            if feature['shap_value'] < 0:  # If it decreases risk
                scenarios["🔄 Policy Upgrade"]["adjustments"][feature['name']] = feature['current_value'] * 1.2
    
    # Select scenario
    selected_scenario = st.selectbox(
        "Select a scenario to simulate:",
        list(scenarios.keys()),
        help="Choose a pre-defined retention strategy"
    )
    
    st.info(f"**Strategy**: {scenarios[selected_scenario]['description']}")
    
    # Apply scenario
    if st.button("🚀 Run Scenario", type="primary"):
        adjustments = scenarios[selected_scenario]['adjustments']
        
        if not adjustments:
            st.warning("No applicable adjustments for this customer's features.")
            return
        
        # Apply changes
        test_customer = original_customer.copy()
        for feature_name, new_value in adjustments.items():
            if feature_name in test_customer.columns:
                feature_idx = test_customer.columns.get_loc(feature_name)
                test_customer.iloc[0, feature_idx] = new_value
        
        # Recalculate
        new_prediction, new_probability = make_prediction(model, test_customer)
        probability_change = new_probability - baseline_probability
        
        # Display results
        st.markdown("---")
        st.markdown("### 📊 Scenario Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Original Risk",
                f"{baseline_probability*100:.1f}%"
            )
        
        with col2:
            st.metric(
                "New Risk",
                f"{new_probability*100:.1f}%",
                delta=f"{probability_change*100:.1f}%",
                delta_color="inverse"
            )
        
        with col3:
            retention_lift = -probability_change * 100
            st.metric(
                "Retention Lift",
                f"{retention_lift:.1f}%"
            )
        
        # Show what changed
        st.markdown("#### Changes Applied:")
        for feature_name, new_value in adjustments.items():
            for feature in actionable_features:
                if feature['name'] == feature_name:
                    change = new_value - feature['current_value']
                    change_pct = (change / feature['current_value'] * 100) if feature['current_value'] != 0 else 0
                    st.markdown(f"- **{feature_name}**: {feature['current_value']:.2f} → {new_value:.2f} ({change_pct:+.1f}%)")
        
        # Recommendation
        if new_probability < 0.4:
            st.success("✅ **Recommended**: This scenario successfully reduces churn risk to LOW level!")
        elif new_probability < 0.7:
            st.warning("⚠️ **Moderate Impact**: Risk reduced but still in MEDIUM range. Consider combining strategies.")
        else:
            st.error("❌ **Insufficient**: This scenario alone may not be enough. Try a more aggressive approach.")


def display_goal_seeking(model, modified_customer, actionable_features, 
                        baseline_probability, original_customer):
    """Display goal-seeking analysis"""
    
    st.markdown("#### 🎯 Find Optimal Intervention")
    st.caption("Set your target churn risk, and we'll suggest the minimum changes needed")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        target_risk = st.slider(
            "Target Churn Risk (%)",
            min_value=0.0,
            max_value=100.0,
            value=max(0.0, (baseline_probability - 0.2) * 100),
            step=5.0,
            help="Set your desired churn risk level"
        ) / 100
    
    with col2:
        required_reduction = (baseline_probability - target_risk) * 100
        st.metric(
            "Required Reduction",
            f"{required_reduction:.1f}%"
        )
    
    # Select primary intervention
    intervention_feature = st.selectbox(
        "Primary Intervention Feature:",
        [f['name'] for f in actionable_features],
        help="Select the main feature you want to adjust"
    )
    
    if st.button("🔍 Calculate Required Change", type="primary"):
        # Find the required change through binary search
        feature_data = next(f for f in actionable_features if f['name'] == intervention_feature)
        
        # Binary search for optimal value
        optimal_value = find_optimal_value(
            model, original_customer, intervention_feature, 
            feature_data, target_risk, baseline_probability
        )
        
        if optimal_value is not None:
            # Apply the optimal value
            test_customer = original_customer.copy()
            feature_idx = test_customer.columns.get_loc(intervention_feature)
            test_customer.iloc[0, feature_idx] = optimal_value
            
            # Verify
            _, achieved_probability = make_prediction(model, test_customer)
            
            st.markdown("---")
            st.markdown("### 💡 Recommended Intervention")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    f"Adjust {intervention_feature}",
                    f"{optimal_value:.2f}",
                    delta=f"{optimal_value - feature_data['current_value']:.2f}"
                )
            
            with col2:
                change_pct = ((optimal_value - feature_data['current_value']) / feature_data['current_value'] * 100) if feature_data['current_value'] != 0 else 0
                st.metric(
                    "Change Required",
                    f"{change_pct:+.1f}%"
                )
            
            with col3:
                st.metric(
                    "Achieved Risk",
                    f"{achieved_probability*100:.1f}%",
                    delta=f"{(achieved_probability - baseline_probability)*100:.1f}%",
                    delta_color="inverse"
                )
            
            # Actionable advice
            if abs(change_pct) < 5:
                st.success(f"✅ **Minor adjustment needed**: A small {abs(change_pct):.1f}% change in {intervention_feature} should achieve your target.")
            elif abs(change_pct) < 15:
                st.info(f"💡 **Moderate intervention**: Adjust {intervention_feature} by {abs(change_pct):.1f}% to reach your goal.")
            else:
                st.warning(f"⚠️ **Significant change required**: {abs(change_pct):.1f}% adjustment needed. Consider combining multiple interventions.")
        else:
            st.error("❌ Unable to find a solution within reasonable bounds. Try a different target or feature.")


def find_optimal_value(model, customer, feature_name, feature_data, target_risk, baseline_risk):
    """Binary search to find optimal feature value"""
    current_value = feature_data['current_value']
    min_val = feature_data['min_value']
    max_val = feature_data['max_value']
    
    # Determine search direction based on SHAP value
    if feature_data['shap_value'] > 0:  # Positive SHAP = increases risk
        # Need to decrease this feature to reduce risk
        search_min = min_val
        search_max = current_value
    else:  # Negative SHAP = decreases risk
        # Need to increase this feature to reduce risk
        search_min = current_value
        search_max = max_val
    
    # Binary search
    iterations = 20
    tolerance = 0.01
    
    for _ in range(iterations):
        mid_value = (search_min + search_max) / 2
        
        # Test this value
        test_customer = customer.copy()
        feature_idx = test_customer.columns.get_loc(feature_name)
        test_customer.iloc[0, feature_idx] = mid_value
        
        _, test_probability = make_prediction(model, test_customer)
        
        if abs(test_probability - target_risk) < tolerance:
            return mid_value
        
        # Adjust search range
        if feature_data['shap_value'] > 0:  # Decreasing feature
            if test_probability > target_risk:
                search_max = mid_value
            else:
                search_min = mid_value
        else:  # Increasing feature
            if test_probability > target_risk:
                search_min = mid_value
            else:
                search_max = mid_value
    
    return mid_value


def display_scenario_comparison(baseline_prob, new_prob, adjustments, features):
    """Display visual comparison of scenarios"""
    import plotly.graph_objects as go
    
    # Create comparison chart
    fig = go.Figure()
    
    # Baseline
    fig.add_trace(go.Bar(
        x=['Baseline'],
        y=[baseline_prob * 100],
        name='Original',
        marker=dict(color='#ff6b6b'),
        text=[f"{baseline_prob*100:.1f}%"],
        textposition='auto',
    ))
    
    # After intervention
    fig.add_trace(go.Bar(
        x=['After Intervention'],
        y=[new_prob * 100],
        name='Modified',
        marker=dict(color='#4ecdc4'),
        text=[f"{new_prob*100:.1f}%"],
        textposition='auto',
    ))
    
    # Add threshold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="High Risk")
    fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Medium Risk")
    
    fig.update_layout(
        title="Churn Risk Comparison",
        yaxis_title="Churn Probability (%)",
        yaxis=dict(range=[0, 100]),
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(240,242,246,0.5)'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def generate_intervention_recommendations(adjustments, features, probability_change, new_probability):
    """Generate AI-powered intervention recommendations"""
    
    st.markdown("### 💡 AI-Powered Recommendations")
    
    # Analyze the intervention
    risk_reduction = -probability_change * 100
    
    # Generate recommendations based on changes
    recommendations = []
    
    for feature_name, new_value in adjustments.items():
        feature_info = next((f for f in features if f['name'] == feature_name), None)
        if feature_info:
            change = new_value - feature_info['current_value']
            change_pct = (change / feature_info['current_value'] * 100) if feature_info['current_value'] != 0 else 0
            
            if abs(change_pct) > 1:
                if 'premium' in feature_name.lower() or 'price' in feature_name.lower():
                    if change < 0:
                        recommendations.append(f"💰 **Pricing Strategy**: Offer a {abs(change_pct):.1f}% discount on premium (${abs(change):.2f} reduction)")
                    else:
                        recommendations.append(f"💰 **Pricing Strategy**: Premium increase of {change_pct:.1f}% may be acceptable")
                
                elif 'claim' in feature_name.lower():
                    if change < 0:
                        recommendations.append(f"🏥 **Claims Management**: Target {abs(change_pct):.1f}% reduction in claim frequency through preventive programs")
                
                elif 'service' in feature_name.lower() or 'call' in feature_name.lower():
                    if change < 0:
                        recommendations.append(f"📞 **Service Excellence**: Reduce service issues by {abs(change_pct):.1f}% through proactive support")
                
                elif 'tenure' in feature_name.lower():
                    recommendations.append(f"⏰ **Relationship Building**: Focus on long-term engagement strategies")
    
    # Display recommendations
    if recommendations:
        for rec in recommendations:
            st.markdown(f"- {rec}")
    
    # Overall strategy
    st.markdown("#### 🎯 Implementation Strategy:")
    
    if new_probability < 0.3:
        st.success("""
        **Excellent Result!** This intervention brings churn risk to LOW level.
        - ✅ Implement these changes immediately
        - 📊 Monitor customer response over 30 days
        - 🎯 Expected retention rate: >95%
        - 💰 ROI: High (intervention cost << customer lifetime value)
        """)
    elif new_probability < 0.5:
        st.info("""
        **Good Progress!** Risk reduced to MEDIUM level.
        - ✅ Implement as primary intervention
        - 🔄 Consider additional micro-adjustments
        - 📊 Monitor closely for 60 days
        - 💰 ROI: Positive
        """)
    else:
        st.warning("""
        **Partial Success** - Risk still elevated.
        - ⚠️ Combine with additional interventions
        - 📞 Schedule personal customer outreach
        - 🎁 Consider bundled incentive package
        - 💰 May need aggressive retention investment
        """)
