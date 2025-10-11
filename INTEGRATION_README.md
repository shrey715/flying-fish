# Frontend-Backend Integration Guide

## 🎯 Overview

The Customer Churn Prediction application now has a fully integrated frontend-backend architecture:

- **Backend**: FastAPI server with LangChain multi-agent workflow
- **Frontend**: Streamlit dashboard for user interaction
- **Communication**: REST API with JSON payloads

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                       │
│                  (app_backend_integrated.py)                │
│                    Port: 8501                               │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST API
                        │ (JSON)
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend                          │
│                      (main.py)                              │
│                    Port: 8001                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴────────────────┐
        │                                │
        ▼                                ▼
┌───────────────┐            ┌───────────────────┐
│  ML Model     │            │  LangChain Agents │
│  (XGBoost)    │            │  - Risk           │
│  + SHAP       │            │  - Explainability │
└───────────────┘            │  - Speculation    │
                             │  - Recommendation │
                             └───────────────────┘
```

## 🚀 Quick Start

### Option 1: Use the Startup Script (Recommended)

```bash
# From project root
./start_app.sh
```

This will:
1. Start the FastAPI backend on port 8001
2. Start the Streamlit frontend on port 8501
3. Monitor both processes
4. Cleanup on exit (Ctrl+C)

### Option 2: Start Manually

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app_backend_integrated.py
```

## 📝 Environment Setup

### Required Environment Variables

Create a `.env` file in the project root (optional for LangChain agents):

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

Note: The backend will work without API key but AI agents will have limited functionality.

### Dependencies

All dependencies are in `pyproject.toml`. Install with:

```bash
uv sync
```

Key packages:
- `fastapi` - Backend API framework
- `uvicorn` - ASGI server
- `streamlit` - Frontend dashboard
- `langchain` - Agent framework
- `requests` - HTTP client for frontend
- `xgboost` - ML model
- `shap` - Explainability

## 🔌 API Endpoints

### Backend (FastAPI) - http://localhost:8001

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with service info |
| `/api/health` | GET | Health check and status |
| `/api/predict` | POST | Single customer prediction |
| `/api/batch-predict` | POST | Batch predictions |
| `/api/sample-data` | GET | Sample customer data |
| `/docs` | GET | Interactive API documentation |

### Example API Call

```python
import requests

customer_data = {
    "customer_type": "existing",
    "days_tenure": 730,
    "curr_ann_amt": 1200.0,
    "age_in_years": 45.0,
    "income_filled": 75000.0,
    "has_children": 1,
    "home_owner": 1,
    "college_degree": 1,
    "good_credit": 1,
    "is_married": 1,
    "length_of_residence_filled": 5.0
}

response = requests.post(
    "http://localhost:8001/api/predict",
    json=customer_data
)

result = response.json()
print(f"Churn Probability: {result['risk_assessment']['churn_probability']}")
```

## 📊 Frontend Features

The new integrated frontend (`app_backend_integrated.py`) provides:

1. **Real-time Backend Connection Check**
   - Validates backend availability before allowing predictions
   - Shows connection status

2. **Input Modes**
   - Use pre-configured sample customers
   - Manual input with form validation

3. **AI-Powered Analysis Display**
   - Risk Assessment with gauge chart
   - Natural language explanation
   - Churn speculation analysis
   - Personalized recommendations

4. **Multi-Agent Workflow Visualization**
   - Shows processing steps
   - Displays agent outputs

## 🔧 Configuration

### Backend Configuration (main.py)

```python
# Port
uvicorn.run(app, host="0.0.0.0", port=8001)

# CORS (for production, restrict origins)
allow_origins=["*"]  # Change to ["http://localhost:8501"] in production
```

### Frontend Configuration (app_backend_integrated.py)

```python
# Backend URL
BACKEND_URL = "http://localhost:8001"
```

## 🧪 Testing the Integration

1. **Test Backend Health:**
```bash
curl http://localhost:8001/api/health
```

2. **Test Sample Data:**
```bash
curl http://localhost:8001/api/sample-data
```

3. **Test Prediction:**
```bash
curl -X POST http://localhost:8001/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_type": "existing",
    "days_tenure": 730,
    "curr_ann_amt": 1200.0,
    "age_in_years": 45.0,
    "income_filled": 75000.0,
    "has_children": 1,
    "home_owner": 1,
    "college_degree": 1,
    "good_credit": 1,
    "is_married": 1,
    "length_of_residence_filled": 5.0
  }'
```

## 📁 File Structure

```
flying-fish/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── workflow.py             # LangChain workflow orchestrator
│   └── agents/                 # Individual AI agents
│       ├── risk_assessment_agent.py
│       ├── explainability_agent.py
│       ├── speculation_agent.py
│       └── recommendation_agent.py
├── frontend/
│   ├── app_backend_integrated.py  # NEW: Integrated Streamlit app
│   ├── app.py                     # Original standalone app
│   ├── app_modular.py             # Original modular app
│   └── [other UI components]
├── start_app.sh                # Startup script
└── INTEGRATION_README.md       # This file
```

## 🐛 Troubleshooting

### Backend Not Starting

1. Check if port 8001 is available:
```bash
lsof -i :8001
```

2. Check backend logs:
```bash
tail -f backend.log
```

3. Verify model files exist in the correct location

### Frontend Can't Connect

1. Verify backend is running:
```bash
curl http://localhost:8001/api/health
```

2. Check frontend logs:
```bash
tail -f frontend.log
```

3. Verify BACKEND_URL in `app_backend_integrated.py` matches your setup

### AI Agents Not Working

1. Check if GOOGLE_API_KEY is set
2. Verify API key is valid
3. Check backend logs for agent errors

### Port Conflicts

Change ports in:
- Backend: `main.py` - uvicorn.run() port parameter
- Frontend: `start_app.sh` - streamlit run --server.port

## 🎨 Comparison: Standalone vs Integrated

| Feature | Standalone (app.py) | Integrated (app_backend_integrated.py) |
|---------|---------------------|----------------------------------------|
| ML Model | Direct local loading | Via API |
| SHAP Values | Calculated locally | From backend |
| AI Agents | Not available | Full multi-agent workflow |
| Explainability | SHAP only | SHAP + LangChain agents |
| Recommendations | Static rules | AI-generated |
| Scalability | Single machine | Distributed possible |
| Updates | Requires restart | Backend updates independent |

## 🚀 Next Steps

1. **Production Deployment**
   - Configure proper CORS origins
   - Add authentication/authorization
   - Set up HTTPS
   - Use environment variables for secrets

2. **Monitoring**
   - Add logging middleware
   - Set up health check endpoints
   - Monitor API response times

3. **Scaling**
   - Add Redis caching for predictions
   - Implement request queuing
   - Use load balancer for multiple backend instances

4. **Features**
   - Add user authentication
   - Implement prediction history
   - Add A/B testing for recommendations
   - Export reports functionality

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [SHAP Documentation](https://shap.readthedocs.io/)

## 🤝 Contributing

When making changes:

1. **Backend Changes**: Restart backend service only
2. **Frontend Changes**: Streamlit auto-reloads
3. **Model Changes**: Update both model loading logic and API endpoints
4. **Agent Changes**: Only backend restart needed

---

**Built with ❤️ using FastAPI, Streamlit, LangChain, and XGBoost**
