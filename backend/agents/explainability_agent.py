"""
Explainability Agent
Provides natural language explanations of SHAP values and risk factors
"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os


class ExplainabilityAgent:
    """Agent for explaining risk assessment results"""
    
    def __init__(self, api_key: str = None):
        """Initialize with LLM"""
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=api_key,
            temperature=0.2,  # Lower = faster, more deterministic
        )
        
        self.explanation_template = PromptTemplate(
            input_variables=["churn_probability", "risk_category", "top_factors", "confidence"],
            template="""You are an expert insurance analyst explaining customer churn risk.

Customer Churn Risk: {churn_probability}% probability
Risk Level: {risk_category}
Confidence: {confidence}

Top Contributing Factors:
{top_factors}

Provide a clear, concise 3-4 sentence explanation of:
1. Why this customer is at this risk level
2. What the key factors indicate about their behavior
3. The overall risk profile

Be specific, data-driven, and actionable. Use professional business language."""
        )
        
        print("✅ Explainability Agent initialized")
    
    def explain(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate natural language explanation of risk assessment
        
        Args:
            assessment_results: Output from Risk Assessment Agent
            
        Returns:
            Dictionary with explanation text
        """
        # Format top factors
        factors_text = "\n".join([
            f"- {f['feature']}: Value={f['value']:.2f}, SHAP={f['shap_value']:.4f} ({f['impact']} risk)"
            for f in assessment_results['top_factors'][:3]
        ])
        
        # Generate explanation
        prompt = self.explanation_template.format(
            churn_probability=f"{assessment_results['churn_probability']*100:.1f}",
            risk_category=assessment_results['risk_category'],
            top_factors=factors_text,
            confidence=assessment_results['confidence_level']
        )
        
        response = self.llm.invoke(prompt)
        explanation = response.content
        
        # Return only explanation-specific data (no copying entire result)
        return {
            'explanation': explanation
        }
