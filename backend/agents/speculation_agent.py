"""
Speculation Agent
Analyzes patterns and speculates on future customer behavior
"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os


class SpeculationAgent:
    """Agent for speculating on customer churn reasons and future behavior"""
    
    def __init__(self, api_key: str = None):
        """Initialize with LLM"""
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.8  # Higher temperature for creative speculation
        )
        
        self.speculation_template = PromptTemplate(
            input_variables=["customer_profile", "risk_level", "key_factors"],
            template="""You are a customer behavior analyst specializing in insurance churn prediction.

Customer Profile:
- Tenure: {customer_profile[days_tenure]} days
- Premium: ${customer_profile[curr_ann_amt]}/year
- Age: {customer_profile[age_in_years]} years
- Income: ${customer_profile[income_filled]}
- Home Owner: {customer_profile[home_owner]}
- Good Credit: {customer_profile[good_credit]}

Risk Level: {risk_level}

Key Risk Factors:
{key_factors}

Speculate on 3 likely reasons why this customer might churn:
1. Primary behavioral pattern (most likely)
2. Secondary factor (contributing cause)
3. External trigger (potential catalyst)

For each reason:
- State the speculation clearly
- Provide reasoning based on the data
- Estimate likelihood (High/Medium/Low)

Be insightful, creative, but grounded in the customer data."""
        )
        
        print("✅ Speculation Agent initialized")
    
    def speculate(self, explained_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Speculate on reasons for customer churn
        
        Args:
            explained_results: Output from Explainability Agent
            
        Returns:
            Dictionary with speculation insights
        """
        # Format key factors
        factors_text = "\n".join([
            f"- {f['feature']}: {f['impact']} risk by {abs(f['shap_value']):.3f}"
            for f in explained_results['top_factors'][:3]
        ])
        
        # Generate speculation
        prompt = self.speculation_template.format(
            customer_profile=explained_results['customer_data'],
            risk_level=explained_results['risk_category'],
            key_factors=factors_text
        )
        
        response = self.llm.invoke(prompt)
        speculation_text = response.content
        
        # Parse speculation into structured format
        speculations = self._parse_speculation(speculation_text)
        
        # Add to results
        result = explained_results.copy()
        result['speculation'] = speculation_text
        result['speculation_items'] = speculations
        
        return result
    
    def _parse_speculation(self, text: str) -> list:
        """Parse speculation text into structured items"""
        # Basic parsing - extract numbered items
        items = []
        lines = text.split('\n')
        
        current_item = None
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.')):
                if current_item:
                    items.append(current_item)
                current_item = {'text': line, 'type': 'speculation'}
            elif current_item and line:
                current_item['text'] += ' ' + line
        
        if current_item:
            items.append(current_item)
        
        return items if items else [{'text': text, 'type': 'speculation'}]
