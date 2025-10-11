"""
FastAPI Server for Churn Prediction Workflow
Provides REST API endpoints for the React frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow import ChurnWorkflow

app = FastAPI(
    title="Churn Prediction API",
    description="AI-powered customer churn prediction with full explainability",
    version="2.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global workflow instance
workflow = None


class CustomerInput(BaseModel):
    """Customer data input model"""
    customer_type: str = Field("existing", description="Customer type: 'existing' or 'new'")
    days_tenure: float = Field(..., description="Days as customer")
    curr_ann_amt: float = Field(..., description="Current annual premium amount")
    age_in_years: float = Field(..., description="Customer age")
    income_filled: float = Field(..., description="Annual income")
    has_children: int = Field(0, ge=0, le=1, description="Has children (0/1)")
    home_owner: int = Field(0, ge=0, le=1, description="Home owner (0/1)")
    college_degree: int = Field(0, ge=0, le=1, description="College degree (0/1)")
    good_credit: int = Field(0, ge=0, le=1, description="Good credit (0/1)")
    is_married: int = Field(0, ge=0, le=1, description="Married (0/1)")
    length_of_residence_filled: float = Field(0, description="Length of residence")
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class PredictionResponse(BaseModel):
    """Complete prediction response"""
    workflow_status: str
    customer_type: str
    risk_assessment: Dict[str, Any]
    explanation: Dict[str, Any]
    speculation: Dict[str, Any]
    recommendations: Dict[str, Any]
    processing_steps: List[str]


@app.on_event("startup")
async def startup_event():
    """Initialize workflow on startup"""
    global workflow
    
    try:
        # Path to model artifacts (from main project)
        # backend/main.py -> go up one level to project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(base_dir, "models")
        
        model_path = os.path.join(model_dir, "churn_model.pkl")
        scaler_path = os.path.join(model_dir, "scaler.pkl")
        features_path = os.path.join(model_dir, "feature_names.pkl")
        
        if not all(os.path.exists(p) for p in [model_path, scaler_path, features_path]):
            print("⚠️  Warning: Model files not found. Please train model first.")
            print(f"   Expected path: {model_dir}")
            return
        
        # Initialize workflow
        workflow = ChurnWorkflow(
            model_path=model_path,
            scaler_path=scaler_path,
            features_path=features_path
        )
        
        print("\n" + "="*60)
        print("🚀 Churn Prediction Workflow API is ready!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error initializing workflow: {e}")
        workflow = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Churn Prediction Workflow API",
        "version": "2.0.0",
        "status": "operational" if workflow else "model not loaded",
        "endpoints": {
            "predict": "/api/predict",
            "health": "/api/health",
            "docs": "/docs"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "workflow_loaded": workflow is not None,
        "agents": [
            "RiskAssessmentAgent",
            "ExplainabilityAgent",
            "SpeculationAgent",
            "RecommendationAgent"
        ] if workflow else [],
        "api_version": "2.0.0"
    }


@app.post("/api/predict", response_model=PredictionResponse)
async def predict_churn(customer: CustomerInput):
    """
    Main prediction endpoint
    
    Processes customer data through complete workflow:
    1. Risk Assessment (ML + SHAP)
    2. Explainability Analysis
    3. Churn Speculation
    4. Retention Recommendations
    """
    if workflow is None:
        raise HTTPException(
            status_code=503,
            detail="Workflow not initialized. Please ensure model files are available."
        )
    
    try:
        # Convert to dict
        customer_data = customer.dict()
        
        # Process through workflow
        result = await workflow.process(customer_data)
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/api/batch-predict")
async def batch_predict(customers: List[CustomerInput]):
    """Batch prediction for multiple customers"""
    if workflow is None:
        raise HTTPException(
            status_code=503,
            detail="Workflow not initialized."
        )
    
    try:
        results = []
        for customer in customers:
            result = await workflow.process(customer.dict())
            results.append(result)
        
        return {
            "predictions": results,
            "count": len(results),
            "status": "completed"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.get("/api/sample-data")
async def get_sample_data():
    """Get sample customer data for testing"""
    return {
        "low_risk": {
            "customer_type": "existing",
            "days_tenure": 2000,
            "curr_ann_amt": 1200,
            "age_in_years": 45,
            "income_filled": 85000,
            "has_children": 1,
            "home_owner": 1,
            "college_degree": 1,
            "good_credit": 1,
            "is_married": 1,
            "length_of_residence_filled": 10
        },
        "high_risk": {
            "customer_type": "existing",
            "days_tenure": 90,
            "curr_ann_amt": 2500,
            "age_in_years": 28,
            "income_filled": 35000,
            "has_children": 0,
            "home_owner": 0,
            "college_degree": 0,
            "good_credit": 0,
            "is_married": 0,
            "length_of_residence_filled": 1
        },
        "new_customer": {
            "customer_type": "new",
            "days_tenure": 30,
            "curr_ann_amt": 1500,
            "age_in_years": 35,
            "income_filled": 60000,
            "has_children": 1,
            "home_owner": 1,
            "college_degree": 1,
            "good_credit": 1,
            "is_married": 1,
            "length_of_residence_filled": 3
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
