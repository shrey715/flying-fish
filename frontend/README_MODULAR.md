# Customer Churn Prediction Dashboard - Modular Architecture

## Overview

The original monolithic `app.py` has been refactored into a modular architecture with separate files for different concerns. This improves code maintainability, readability, and reusability.

## File Structure

```
frontend/
├── app.py                  # Main application orchestration
├── app_original.py         # Backup of original monolithic code
├── styles.py              # CSS styling and HTML templates
├── model_operations.py    # ML model operations and predictions
├── data_operations.py     # Data loading and processing
└── ui_components.py       # Streamlit UI components and visualizations
```

## Module Descriptions

### 1. `app.py` - Main Application

**Purpose**: Orchestrates the entire application by importing and using functions from other modules.

**Key Responsibilities**:

- Page configuration
- Module imports and initialization
- Main application flow control
- Layout coordination

**Dependencies**: All other custom modules

### 2. `styles.py` - Styling and Templates

**Purpose**: Contains all CSS styling and HTML templates for consistent UI appearance.

**Key Functions**:

- `get_custom_css()`: Returns main CSS styles for the dashboard
- `get_prediction_box_html()`: HTML template for prediction result display
- `get_feature_impact_style()`: Inline styles for feature impact boxes
- `get_footer_html()`: Footer HTML template

**Dependencies**: None (pure styling)

### 3. `model_operations.py` - Machine Learning Operations

**Purpose**: Handles all ML model-related operations including loading, prediction, and SHAP analysis.

**Key Functions**:

- `load_model_and_data()`: Loads XGBoost model and processes dataset
- `make_prediction()`: Makes predictions for a customer
- `calculate_shap_values()`: Computes SHAP explanations
- `get_risk_level()`: Determines risk level from probability
- `create_sample_customer_from_inputs()`: Creates customer data from user inputs
- `get_important_features()`: Returns list of most important features

**Dependencies**: joblib, shap, sklearn, pandas, numpy, streamlit

### 4. `data_operations.py` - Data Management

**Purpose**: Manages data loading, processing, and customer selection logic.

**Key Functions**:

- `load_sample_customers()`: Loads demo customer data (cached)
- `get_customer_by_mode()`: Handles different customer selection modes
- `generate_trend_data()`: Creates mock historical trend data

**Dependencies**: pandas, numpy, streamlit, model_operations

### 5. `ui_components.py` - User Interface Components

**Purpose**: Contains reusable Streamlit UI components and visualization functions.

**Key Functions**:

- `create_sidebar()`: Creates and populates the sidebar
- `display_customer_profile()`: Shows customer profile information
- `create_gauge_chart()`: Creates churn probability gauge chart
- `create_feature_impact_chart()`: Creates SHAP feature impact visualization
- `display_shap_analysis()`: Shows detailed SHAP analysis results
- `display_recommendations()`: Shows actionable recommendations
- `create_trend_chart()`: Creates historical trend visualization

**Dependencies**: streamlit, plotly, numpy, styles

## Benefits of Modular Architecture

### 1. **Separation of Concerns**

- Each module has a single, well-defined responsibility
- Easier to understand and modify specific functionality
- Reduces cognitive load when working on specific features

### 2. **Maintainability**

- Changes to styling don't affect model logic
- Model updates are isolated from UI components
- Easier to debug issues in specific areas

### 3. **Reusability**

- UI components can be reused across different views
- Model operations can be used in different contexts
- Styling can be easily applied to new components

### 4. **Testing**

- Each module can be tested independently
- Mock dependencies for isolated unit testing
- Easier to identify and fix bugs

### 5. **Collaboration**

- Different team members can work on different modules
- Reduced merge conflicts
- Clear ownership of different aspects

## Module Dependencies Graph

```
app.py
├── styles.py
├── model_operations.py
│   ├── joblib
│   ├── shap
│   ├── sklearn
│   └── streamlit
├── data_operations.py
│   ├── model_operations.py
│   └── streamlit
└── ui_components.py
    ├── styles.py
    ├── plotly
    └── streamlit
```

## How to Extend

### Adding New Features

1. **New Model**: Add functions to `model_operations.py`
2. **New Visualization**: Add components to `ui_components.py`
3. **New Styling**: Add styles to `styles.py`
4. **New Data Source**: Add functions to `data_operations.py`

### Adding New Pages

1. Create new UI component functions
2. Import and use in `app.py`
3. Add any new styling to `styles.py`

## Testing the Modules

Each module can be tested independently:

```python
# Test styles module
from styles import get_custom_css
print("Styles module works")

# Test model operations
from model_operations import get_important_features
print("Model operations module works")

# Test data operations
from data_operations import generate_trend_data
print("Data operations module works")

# Test UI components
from ui_components import create_gauge_chart
print("UI components module works")
```

## Performance Considerations

- **Caching**: `@st.cache_resource` and `@st.cache_data` decorators are preserved
- **Imports**: Only necessary imports in each module
- **Lazy Loading**: Modules are imported only when needed

## Migration Notes

- Original code is preserved in `app_original.py`
- All functionality remains exactly the same
- No changes to external API or user experience
- Same performance characteristics maintained

This modular structure makes the codebase much more maintainable and scalable while preserving all existing functionality.
