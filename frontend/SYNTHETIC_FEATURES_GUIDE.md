# Synthetic State-Specific Churn Drivers

## 📋 Complete List of Features

The regional map uses the following 30 realistic insurance churn drivers. Each state is randomly assigned 3 unique features to simulate state-specific patterns:

### Premium & Cost Related (6)
1. **High Premium Cost** - Customers facing above-market premium rates
2. **High Deductibles** - Elevated out-of-pocket costs deterring satisfaction
3. **Rate Increases** - Recent premium hikes driving churn
4. **Hidden Fees** - Unexpected charges causing dissatisfaction
5. **No Bundle Discounts** - Lack of multi-policy savings
6. **No Loyalty Benefits** - Absence of rewards for long-term customers

### Claims & Coverage (6)
7. **Multiple Claims** - High frequency of claims filed
8. **Delayed Claim Processing** - Slow claims resolution
9. **Poor Claims Experience** - Dissatisfaction with claims handling
10. **Inadequate Coverage** - Policy doesn't meet customer needs
11. **Poor Coverage Options** - Limited plan flexibility
12. **Complex Policy Terms** - Difficult to understand coverage

### Service Quality (8)
13. **Low Customer Satisfaction** - Overall service dissatisfaction
14. **Service Quality Issues** - Problems with service delivery
15. **Bad Customer Service** - Poor interaction quality
16. **Poor Communication** - Ineffective customer outreach
17. **Limited Agent Support** - Insufficient advisor availability
18. **Long Wait Times** - Extended hold times for support
19. **Poor Digital Experience** - Subpar online/app experience
20. **Poor Mobile App** - Mobile platform deficiencies

### Tenure & Relationship (2)
21. **Short Tenure** - Recently acquired customers at risk
22. **Frequent Policy Changes** - Instability in customer relationship

### Billing & Payments (2)
23. **Billing Issues** - Problems with invoicing or charges
24. **Limited Payment Options** - Restricted payment flexibility

### Market & Competition (5)
25. **Competitive Market Pressure** - Better alternatives available
26. **Competitor Better Rates** - More attractive pricing elsewhere
27. **Inflexible Terms** - Rigid policy conditions
28. **Vehicle Age Issues** - Coverage problems for older vehicles
29. **Credit Score Impact** - Adverse rating due to credit

### Overall Experience (1)
30. **Frequent Policy Changes** - Too many modifications causing frustration

## 🎲 Randomization Strategy

### How It Works:
```python
# Each state gets 3 unique random features
state_features = np.random.choice(feature_options, size=3, replace=False)

# Features are assigned as:
- top_feature_1: Primary churn driver
- top_feature_2: Secondary churn driver  
- top_feature_3: Tertiary churn driver
```

### Example State Assignments:

**California:**
- 1. Competitive Market Pressure
- 2. High Premium Cost
- 3. Poor Digital Experience

**New York:**
- 1. Rate Increases
- 2. Limited Agent Support
- 3. Multiple Claims

**Texas (Real Data):**
- Uses actual model feature importance
- Top features derived from SHAP/model analysis
- Randomly selected from real feature set

**Florida:**
- 1. Poor Claims Experience
- 2. High Deductibles
- 3. Bad Customer Service

## 🔄 Why Different Features Per State?

### Realism:
Different states have different market conditions:
- **California**: Highly competitive market, high costs
- **Florida**: Hurricane-prone, claims-heavy
- **Texas**: Large market, diverse needs
- **New York**: Urban density, service expectations
- **Rural states**: Limited agent access

### Demonstration Value:
Shows the dashboard can handle:
- State-specific insights
- Localized retention strategies
- Targeted interventions
- Regional pattern recognition

### User Experience:
- Makes the map more interesting to explore
- Provides actionable insights even with synthetic data
- Demonstrates analytical capabilities
- Engages stakeholders with relevant details

## 🎯 Business Use Cases

### With Real Data (Production):
Once you have real data for all states, the system would:
1. Calculate actual feature importance per state
2. Use SHAP values for state-level analysis
3. Identify genuine regional patterns
4. Guide localized retention strategies

### Current Implementation (Demo):
The synthetic features:
1. Demonstrate the capability
2. Provide visual appeal for presentations
3. Show stakeholders the potential insights
4. Allow testing of the interface

## 🔍 How to Extend

To use real state-specific features when data becomes available:

```python
def analyze_state_specific_features(X_original, model, explainer, state):
    # Filter data for specific state
    state_data = X_original[X_original['state'] == state]
    
    # Calculate SHAP values for state customers
    state_shap = explainer.shap_values(state_data)
    
    # Aggregate feature importance for state
    feature_importance = np.abs(state_shap).mean(axis=0)
    
    # Get top 3 features
    top_indices = feature_importance.argsort()[-3:][::-1]
    top_features = [feature_cols[i] for i in top_indices]
    
    return top_features
```

## 📊 Validation

### Synthetic Data Characteristics:
- **Seed**: 42 (for reproducibility)
- **Distribution**: Each state has unique combination
- **No Duplicates**: Within same state, all 3 features are different
- **Realistic**: All features are actual insurance churn factors
- **Diverse**: 30 options ensure variety across 50 states

### Testing:
```python
# Verify uniqueness within state
assert len(set([f1, f2, f3])) == 3

# Verify all features are valid
assert all(f in feature_options for f in [f1, f2, f3])

# Verify reproducibility
np.random.seed(42)
features_v1 = generate_features()
np.random.seed(42)
features_v2 = generate_features()
assert features_v1 == features_v2
```

## 💡 Key Insight

This approach shows how a production system would work:
1. Collect customer data by region
2. Analyze regional patterns with ML
3. Identify state-specific churn drivers
4. Develop targeted retention strategies
5. Monitor and optimize by region

The synthetic data is a **proof of concept** that demonstrates the dashboard's ability to surface actionable, localized insights for business stakeholders.

---

**Note**: When you have real data for additional states, simply remove the synthetic data generation and the system will automatically use actual calculated features from the model and SHAP analysis.
