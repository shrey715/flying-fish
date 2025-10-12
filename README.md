# 🐟 Flying Fish - AI-Powered Customer Churn Prediction System

**An intelligent customer retention platform that predicts churn with explainable AI and provides actionable insights through an interactive dashboard.**


## 🚀 Quick Start Guide

### Installation

```bash
# Clone the repository
git clone https://github.com/shrey715/flying-fish.git
cd flying-fish

# Install dependencies
pip install -e .

# Set up environment (optional - for AI agents)
export GOOGLE_API_KEY="your_gemini_api_key"
```

### Running the Applications

#### 🖥️ **Dashboard (Streamlit)**
```bash
# Navigate to frontend
cd frontend

# Launch interactive dashboard
streamlit run app.py
```
Access at: `http://localhost:8501`

#### ⚡ **API Server (FastAPI)**
```bash
# Navigate to backend
cd backend

# Start production server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119.0+-00a393.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io/)
[![SHAP](https://img.shields.io/badge/SHAP-Explainable%20AI-orange.svg)](https://shap.readthedocs.io/)

## 📋 Project Requirements Compliance

### ✅ Prediction Model
**Model Type**: The solution uses **XGBoost** as the Primary Model

### ✅ Explainable AI (XAI) - MANDATORY COMPONENT
**SHAP Integration**: The system implements **SHAP (SHapley Additive exPlanations)** as the core explainability technique, providing both local and global interpretability.

- **SHAP TreeExplainer**: Optimized for tree-based models (XGBoost)
- **Feature Impact Analysis**: Real-time SHAP value calculation for each prediction
- **Natural Language Explanations**: AI agents convert SHAP values into business-friendly insights
- **Visual Explanations**: Interactive charts showing feature contributions to churn probability

### ✅ Interactive Dashboard
**Multi-Modal Interface**: Comprehensive dashboard with visualization of churn probabilities and their explanations across three key interfaces.

- **Single Customer Analysis**: Individual risk assessment with detailed SHAP breakdowns
- **Aggregate Analytics**: Portfolio-level churn insights and trends
- **Real-time Predictions**: Interactive input forms for new customer assessment
- **AI Agent Insights**: Automated risk assessment, explanations, and retention recommendations

---

## 🏗️ System Architecture

### 🤖 AI Agent Workflow
The system orchestrates four specialized AI agents in a sophisticated workflow:

```
Customer Data → Risk Assessment → Explainability → Speculation → Recommendations
```

#### 1. **Risk Assessment Agent** 🎯
*The ML Powerhouse*
- Loads pre-trained XGBoost model with feature scaling
- Generates churn probability predictions (0-100%)
- Computes SHAP values for feature importance
- Categorizes risk levels (Low/Medium/High)
- **Key Features**: Real-time inference, SHAP explainability, confidence scoring

#### 2. **Explainability Agent** 💡
*The AI Interpreter*
- Transforms SHAP values into natural language explanations
- Uses Google Gemini 2.5 Flash for fast, accurate interpretations
- Provides business-context explanations of risk factors
- **Key Features**: LangChain integration, temperature-controlled responses, professional tone

#### 3. **Speculation Agent** 🔮
*The Behavioral Analyst*
- Analyzes patterns to predict likely churn scenarios
- Identifies potential triggers and behavioral indicators
- Forecasts timing and probability of churn events
- **Key Features**: Pattern recognition, behavioral modeling, predictive insights

#### 4. **Recommendation Agent** 📈
*The Retention Strategist*
- Generates personalized retention strategies
- Suggests specific actions based on risk profile
- Prioritizes interventions by impact potential
- **Key Features**: Action-oriented advice, ROI considerations, implementation guidance

### 🖥️ Frontend Dashboard Components

#### **Streamlit Multi-Page Application**
A sophisticated web interface with three specialized views:

##### 📊 **Single Customer Analysis Page**
*Deep-dive individual assessment*
- **Real Customer Selection**: Browse actual customer records from dataset
- **Custom Feature Input**: Manual data entry for new customer assessment
- **Live Risk Gauge**: Visual churn probability meter with color-coded risk levels
- **SHAP Waterfall Charts**: Feature-by-feature impact visualization
- **AI Agent Integration**: Real-time explanations and recommendations
- **Trend Analysis**: Historical behavior patterns and projections

##### 📈 **Aggregate Dashboard Page**
*Portfolio-level insights and analytics*
- **Risk Distribution**: Visualize customer base by risk categories
- **Feature Importance Rankings**: Global SHAP feature significance
- **Churn Trends**: Time-series analysis of churn patterns
- **Segment Analysis**: Risk breakdown by customer demographics
- **Performance Metrics**: Model accuracy and prediction confidence

##### 🎛️ **Overview Page**
*Executive summary and navigation hub*
- **System Status**: Model health and performance indicators
- **Quick Stats**: Key metrics and recent predictions
- **Navigation Center**: Guided access to detailed analysis tools
- **Recent Activity**: Latest predictions and high-risk alerts


## 🗂️ Project Structure

```
flying-fish/
├── 🔧 Backend API
│   ├── main.py             # FastAPI application
│   ├── workflow.py         # AI agent orchestration
│   └── agents/             # Specialized AI agents
│       ├── risk_assessment_agent.py
│       ├── explainability_agent.py
│       ├── speculation_agent.py
│       └── recommendation_agent.py
│
├── 🖥️ Frontend Dashboard
│   ├── app.py              # Main Streamlit application
│   ├── pages/              # Multi-page components
│   ├── ui_components.py    # Reusable UI elements
│   └── model_operations.py # ML integration
│
├── 📊 Data
│   ├── customer.csv        # Customer master data
│   ├── demographic.csv     # Demographic information
│   ├── address.csv         # Geographic data
│   └── termination.csv     # Churn labels
│
└── 🏗️ Models (Generated)
    ├── xgb_model.pkl       # Trained XGBoost model
    ├── scaler.pkl          # Feature scaler
    └── feature_names.pkl   # Feature metadata
```

---

## 💡 Key Features

### 🎯 **Intelligent Prediction**
- Ensemble ML models with hyperparameter optimization
- Real-time inference with sub-second response times
- Confidence scoring and uncertainty quantification
- Automated model retraining capabilities

### 🔍 **Explainable AI**
- SHAP-powered feature importance analysis
- Natural language explanation generation
- Visual impact charts and waterfall plots
- Global and local model interpretability

### 📊 **Interactive Visualization**
- Real-time risk gauges and probability meters
- Dynamic feature impact charts
- Trend analysis and forecasting
- Responsive design for all screen sizes

### 🤖 **AI Agent Intelligence**
- Multi-agent workflow orchestration
- Contextual business recommendations
- Automated insight generation
- Personalized retention strategies


*Built with ❤️ for better customer retention through AI*