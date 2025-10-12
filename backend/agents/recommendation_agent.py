"""
Recommendation Agent
Provides actionable retention strategies based on risk assessment
"""

from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os


class RecommendationAgent:
    """Agent for generating retention recommendations"""
    
    def __init__(self, api_key: str = None):
        """Initialize with LLM"""
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=api_key,
            temperature=0.5,  # Lower for more focused recommendations
        )
        
        self.recommendation_template = PromptTemplate(
            input_variables=["risk_level", "churn_prob", "top_factors", "speculation"],
            template="""You are a customer retention strategist for an insurance company.

Risk Assessment:
- Risk Level: {risk_level}
- Churn Probability: {churn_prob}%

Key Risk Factors:
{top_factors}

Speculation on Churn Reasons:
{speculation}

Generate 3-5 specific, actionable retention recommendations:

For each recommendation:
1. Action: Clear, specific action to take
2. Reasoning: Why this action addresses the risk
3. Priority: High/Medium/Low
4. Timeline: When to implement (Immediate/Within 1 week/Within 1 month)
5. Expected Impact: Potential reduction in churn risk

Format as:
**Action:** [action]
**Reasoning:** [reasoning]
**Priority:** [priority]
**Timeline:** [timeline]
**Expected Impact:** [impact]

---

Be concise and actionable."""
        )
        
        print("✅ Recommendation Agent initialized")
    
    def recommend(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate retention recommendations
        
        Args:
            assessment_results: Output from Risk Assessment Agent (works independently now)
            
        Returns:
            Dictionary with recommendations
        """
        # Format top factors
        factors_text = "\n".join([
            f"- {f['feature']}: {f['impact']} risk (importance: {f['importance']:.3f})"
            for f in assessment_results['top_factors'][:3]
        ])
        
        # Generate recommendations (no longer needs speculation - works independently)
        prompt = self.recommendation_template.format(
            risk_level=assessment_results['risk_category'],
            churn_prob=f"{assessment_results['churn_probability']*100:.1f}",
            top_factors=factors_text,
            speculation="Based on risk factors and customer profile"  # Generic placeholder
        )
        
        response = self.llm.invoke(prompt)
        recommendations_text = response.content
        
        # Parse recommendations
        recommendations = self._parse_recommendations(
            recommendations_text,
            assessment_results['risk_category']
        )
        
        # Return only recommendation-specific data (no copying entire result)
        return {
            'recommendations': recommendations,
            'recommendations_text': recommendations_text
        }
    
    def _parse_recommendations(self, text: str, risk_level: str) -> List[Dict[str, Any]]:
        """Parse recommendation text into structured items"""
        recommendations = []
        
        # Split by "---" separator
        sections = text.split('---')
        
        for section in sections:
            if not section.strip():
                continue
            
            rec = {
                'action': '',
                'reasoning': '',
                'priority': 'medium',
                'timeline': 'Within 1 week',
                'impact': ''
            }
            
            # Extract fields
            for line in section.split('\n'):
                line = line.strip()
                if line.startswith('**Action:**'):
                    rec['action'] = line.replace('**Action:**', '').strip()
                elif line.startswith('**Reasoning:**'):
                    rec['reasoning'] = line.replace('**Reasoning:**', '').strip()
                elif line.startswith('**Priority:**'):
                    priority = line.replace('**Priority:**', '').strip().lower()
                    rec['priority'] = priority if priority in ['high', 'medium', 'low'] else 'medium'
                elif line.startswith('**Timeline:**'):
                    rec['timeline'] = line.replace('**Timeline:**', '').strip()
                elif line.startswith('**Expected Impact:**'):
                    rec['impact'] = line.replace('**Expected Impact:**', '').strip()
            
            if rec['action']:
                recommendations.append(rec)
        
        # Fallback: Generate basic recommendations if parsing fails
        if not recommendations:
            recommendations = self._generate_fallback_recommendations(risk_level)
        
        return recommendations
    
    def _generate_fallback_recommendations(self, risk_level: str) -> List[Dict[str, Any]]:
        """Generate fallback recommendations based on risk level"""
        base_recommendations = {
            'Critical': [
                {
                    'action': 'Immediate Executive Contact',
                    'reasoning': 'Critical risk requires senior leadership intervention',
                    'priority': 'high',
                    'timeline': 'Immediate',
                    'impact': 'High - potential 30-40% risk reduction'
                },
                {
                    'action': 'Premium Reduction Offer',
                    'reasoning': 'Financial incentive to maintain relationship',
                    'priority': 'high',
                    'timeline': 'Within 48 hours',
                    'impact': 'Medium-High - 20-30% risk reduction'
                }
            ],
            'High': [
                {
                    'action': 'Proactive Account Manager Outreach',
                    'reasoning': 'Personal touch to address concerns before escalation',
                    'priority': 'high',
                    'timeline': 'Within 3 days',
                    'impact': 'Medium - 15-25% risk reduction'
                },
                {
                    'action': 'Personalized Service Review',
                    'reasoning': 'Identify and resolve underlying issues',
                    'priority': 'medium',
                    'timeline': 'Within 1 week',
                    'impact': 'Medium - 10-20% risk reduction'
                }
            ],
            'Medium': [
                {
                    'action': 'Customer Satisfaction Survey',
                    'reasoning': 'Early warning system for emerging issues',
                    'priority': 'medium',
                    'timeline': 'Within 2 weeks',
                    'impact': 'Low-Medium - 5-15% risk reduction'
                },
                {
                    'action': 'Loyalty Program Enrollment',
                    'reasoning': 'Increase engagement and perceived value',
                    'priority': 'medium',
                    'timeline': 'Within 1 month',
                    'impact': 'Low-Medium - 5-10% risk reduction'
                }
            ],
            'Low': [
                {
                    'action': 'Annual Policy Review',
                    'reasoning': 'Maintain relationship and identify upsell opportunities',
                    'priority': 'low',
                    'timeline': 'Within 6 months',
                    'impact': 'Low - 2-5% risk reduction'
                },
                {
                    'action': 'Referral Incentive Program',
                    'reasoning': 'Leverage satisfied customers for growth',
                    'priority': 'low',
                    'timeline': 'Ongoing',
                    'impact': 'Low - maintain current low risk'
                }
            ]
        }
        
        return base_recommendations.get(risk_level, base_recommendations['Medium'])
