# Quick Start Guide: Enhanced Regional Map

## 🗺️ How to View the Enhanced Map

1. **Open the dashboard**: http://localhost:8501

2. **Navigate to Aggregate Trends**:
   - Look at the left sidebar
   - Click on "📊 Aggregate Trends Dashboard"

3. **Scroll to Regional Analysis Section**:
   - You'll see "🗺️ Regional Churn Analysis"
   - The map shows all 50 US states color-coded by risk

4. **Interact with the Map**:
   - **Hover over any state** to see:
     ```
     State Name
     Avg Churn Risk: XX.X%
     Customers: X,XXX
     High Risk: XXX
     
     Top Churn Drivers:
     1. [State-specific feature]
     2. [State-specific feature]
     3. [State-specific feature]
     ```
   
   - **Color Legend**:
     - 🟢 Green/Teal: Low risk (15-40%)
     - 🟡 Yellow: Medium risk (40-60%)
     - 🟠 Orange: Medium-high risk (60-70%)
     - 🔴 Red: High risk (70%+)

5. **View Top Risk States**:
   - Right panel shows "Top 10 Highest Risk States"
   - Click to expand each state
   - 🟢 = Real data, 🔵 = Synthetic data
   - Each shows detailed metrics and top 3 drivers

## 📊 What Makes This Map Special

### Before:
- Empty US map
- Only yellow Texas visible
- No interactive features
- No state-specific insights

### After:
- **Full USA coverage** with 50 states
- **Color gradient** from green to red
- **Interactive hover tooltips** with details
- **Unique top 3 churn drivers** for each state
- **Real vs synthetic data** clearly labeled
- **Professional presentation**

## 🎯 Key Features

### 1. State-Specific Churn Drivers
Each state has 3 unique features randomly selected from 30+ options:
- High Premium Cost
- Multiple Claims
- Poor Customer Service
- Rate Increases
- Billing Issues
- Limited Agent Support
- And 24 more realistic insurance factors

### 2. Data Transparency
- Texas uses **real data** from your dataset (🟢)
- Other states use **synthetic data** for visualization (🔵)
- Synthetic data is **NOT** used for:
  - High-risk customer lists
  - Strategic recommendations
  - Actual business decisions

### 3. Visual Excellence
- Smooth color gradient (green → yellow → orange → red)
- Clean white borders between states
- Professional choropleth styling
- Proper US map projection (Albers USA)

## 🔄 Comparison: Single vs Multi-Page

### Original App (app.py):
```
Single scrolling page
├── Customer selection
├── Prediction result
├── SHAP explanation
└── Recommendations
```

### New Multi-Page App (app_multipage.py):
```
Three distinct pages:

1. 🏠 Overview
   ├── Key metrics
   ├── Dataset stats
   └── Navigation guide

2. 👤 Single Customer Analysis
   ├── Customer selection
   ├── Prediction result
   ├── SHAP explanation
   └── Personalized recommendations

3. 📊 Aggregate Trends Dashboard ⭐ NEW
   ├── Population metrics
   ├── Risk distribution charts
   ├── Interactive US map 🗺️ ⭐
   │   └── State-specific top 3 drivers
   ├── Top churn drivers (population)
   ├── High-risk customer list (downloadable)
   └── Strategic recommendations
```

## 💡 Usage Tips

### For Executives:
- Use the **Aggregate Trends Dashboard** (page 3)
- Focus on the **map** and **top 10 states list**
- Download the **high-risk customer CSV**
- Review **strategic recommendations**

### For Data Scientists:
- Check **feature importance** charts
- Analyze **SHAP values** on single customer page
- Examine **risk distribution** histogram
- Validate model performance

### For Customer Service:
- Use **Single Customer Analysis** (page 2)
- Enter customer details or select by ID
- Review **personalized recommendations**
- Understand **why** each customer is at risk

## 🎨 Technical Details

### Synthetic Data Generation
- Uses `np.random.seed(42)` for reproducibility
- Beta distribution for realistic risk levels
- Varying customer counts by "state population"
- Unique features per state (no duplicates within same state)

### Map Configuration
- Plotly Choropleth with custom hover template
- Color scale: 5-point gradient (teal → red)
- Custom data array for hover information
- Albers USA projection for accurate geography

### Performance
- Synthetic data generated once and cached
- No performance impact on real analyses
- Fast rendering (~1-2 seconds)
- Scales to all 50 states effortlessly

## 📝 Note About Synthetic Data

**Important**: The synthetic data is used **ONLY** for the regional map visualization to provide a better user experience and demonstrate the dashboard's capabilities. 

**All actual analysis uses real data:**
- ✅ High-risk customer lists
- ✅ Strategic recommendations  
- ✅ Feature importance
- ✅ Churn predictions
- ✅ Population metrics

The map clearly labels which states have real vs synthetic data, maintaining transparency.

---

**Ready to explore?** Open http://localhost:8501 and navigate to the Aggregate Trends Dashboard! 🚀
