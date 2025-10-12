"""
FastAPI Server for Churn Prediction Workflow
Provides REST API endpoints for the React frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import sys
import json
import asyncio

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


class FeatureImpact(BaseModel):
    """Feature impact data model"""
    Feature: str = Field(..., description="Feature name")
    Value: float = Field(..., description="Feature value")
    SHAP_Value: float = Field(..., description="SHAP value for the feature")
    Impact: str = Field(..., description="Impact description")


class AgentAnalysisInput(BaseModel):
    """Input model for agent analysis"""
    customer_data: CustomerInput = Field(..., description="Customer data")
    features_dict: List[FeatureImpact] = Field(..., description="Feature impacts from SHAP analysis")
    churn_probability: float = Field(..., description="Predicted churn probability")
    prediction: int = Field(..., description="Binary prediction (0/1)")
    
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
        customer_data = customer.model_dump()
        
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
            result = await workflow.process(customer.model_dump())
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


@app.post("/api/predict-streaming")
async def predict_churn_streaming(customer: CustomerInput):
    """
    Streaming prediction endpoint - sends results as they become available
    
    Response format: Server-Sent Events (SSE)
    - Event 1: risk_assessment (after ~2s)
    - Event 2: explanation (after ~8-12s)
    - Event 3: speculation (after ~8-12s)
    - Event 4: recommendations (after ~8-12s)
    - Event 5: complete
    """
    if workflow is None:
        raise HTTPException(
            status_code=503,
            detail="Workflow not initialized."
        )
    
    async def event_generator():
        try:
            customer_data = customer.model_dump()
            
            # Step 1: Risk Assessment (fast)
            print(f"📋 Processing customer: {customer_data.get('customer_id', 'Unknown')}")
            print("   ⚙️  Step 1: Risk Assessment Agent...")
            risk_results = workflow.risk_agent.assess_risk(customer_data)
            
            # Send risk results immediately
            yield f"data: {json.dumps({'type': 'risk_assessment', 'data': risk_results})}\n\n"
            
            if workflow.ai_enabled:
                print("   ⚙️  Steps 2-4: Running AI Agents in Parallel...")
                
                # Create tasks for parallel execution
                explained_task = asyncio.create_task(
                    asyncio.to_thread(workflow.explainability_agent.explain, risk_results)
                )
                speculated_task = asyncio.create_task(
                    asyncio.to_thread(workflow.speculation_agent.speculate, risk_results)
                )
                recommended_task = asyncio.create_task(
                    asyncio.to_thread(workflow.recommendation_agent.recommend, risk_results)
                )
                
                # Wait for each to complete and stream results as they arrive
                tasks = {
                    'explanation': explained_task,
                    'speculation': speculated_task,
                    'recommendations': recommended_task
                }
                
                # Stream results as they complete (don't wait for all)
                for future in asyncio.as_completed(tasks.values()):
                    result = await future
                    # Find which task completed
                    for name, task in tasks.items():
                        if task == future:
                            yield f"data: {json.dumps({'type': name, 'data': result})}\n\n"
                            print(f"      → Streamed {name}")
                            break
            else:
                # Fallback mode
                fallback = workflow._create_fallback_results(risk_results)
                yield f"data: {json.dumps({'type': 'explanation', 'data': {'explanation': fallback['explanation']}})}\n\n"
                yield f"data: {json.dumps({'type': 'recommendations', 'data': {'recommendations': fallback['recommendations']}})}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'complete', 'status': 'success'})}\n\n"
            print("✅ Streaming complete!")
            
        except Exception as e:
            error_msg = f"Streaming prediction failed: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )


@app.post("/api/analyze-with-agents")
async def analyze_with_agents(analysis_input: AgentAnalysisInput):
    """Analyze customer with AI agents using features_dict from frontend"""
    if workflow is None:
        raise HTTPException(
            status_code=503,
            detail="Workflow not initialized. Please ensure model files are available."
        )
    
    try:
        print(f"📥 Received agent analysis request")
        
        # Extract data
        customer_data = analysis_input.customer_data.model_dump()
        features_dict = [f.model_dump() for f in analysis_input.features_dict]
        churn_probability = analysis_input.churn_probability
        prediction = analysis_input.prediction
        
        print(f"📊 Processing customer with {len(features_dict)} features, churn_prob: {churn_probability}")
        
        # Prepare data for agents
        # Convert features_dict to the format expected by agents
        top_factors = []
        for feature in features_dict[:5]:  # Top 5 features
            top_factors.append({
                'feature': feature['Feature'],
                'value': feature['Value'],
                'shap_value': feature['SHAP_Value'],
                'importance': abs(feature['SHAP_Value']),  # Add importance field
                'impact': 'increases' if feature['SHAP_Value'] > 0 else 'decreases'
            })
        
        # Determine risk category
        if churn_probability >= 0.7:
            risk_category = "HIGH"
        elif churn_probability >= 0.4:
            risk_category = "MEDIUM"
        else:
            risk_category = "LOW"
        
        print(f"🎯 Risk category: {risk_category}")
        
        # Create assessment results in the format expected by agents
        assessment_results = {
            'churn_probability': churn_probability,
            'risk_category': risk_category,
            'confidence_level': 'High',  # You can calculate this based on model confidence
            'top_factors': top_factors,
            'prediction': prediction,
            'customer_data': customer_data  # Add customer data for speculation agent
        }
        
        # Process through AI agents if available
        if workflow.ai_enabled:
            print("🤖 Processing with AI agents in parallel...")
            
            # Run all agents in parallel (same optimization as main workflow)
            explained_task = asyncio.create_task(
                asyncio.to_thread(workflow.explainability_agent.explain, assessment_results)
            )
            speculated_task = asyncio.create_task(
                asyncio.to_thread(workflow.speculation_agent.speculate, assessment_results)
            )
            recommended_task = asyncio.create_task(
                asyncio.to_thread(workflow.recommendation_agent.recommend, assessment_results)
            )
            
            # Wait for all to complete
            explained_results, speculation_results, recommendation_results = await asyncio.gather(
                explained_task,
                speculated_task,
                recommended_task
            )
            
            print("✅ AI agents completed successfully")
            
            return {
                "status": "success",
                "ai_enabled": True,
                "analysis": {
                    "risk_assessment": assessment_results,
                    "explanation": explained_results.get('explanation', ''),
                    "speculation": speculation_results.get('speculation', ''),
                    "recommendations": recommendation_results.get('recommendations', [])
                }
            }
        else:
            print("⚠️ AI agents not enabled")
            return {
                "status": "success", 
                "ai_enabled": False,
                "analysis": {
                    "risk_assessment": assessment_results,
                    "explanation": "AI agents not available - set GOOGLE_API_KEY environment variable",
                    "speculation": "AI agents not available",
                    "recommendations": []
                }
            }
        
    except Exception as e:
        print(f"❌ Error in agent analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Agent analysis failed: {str(e)}"
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
