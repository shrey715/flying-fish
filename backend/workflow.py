"""
LangChain Workflow for Customer Churn Assessment
Orchestrates multiple agents in sequence
"""

from typing import Dict, Any
from agents.risk_assessment_agent import RiskAssessmentAgent
from agents.explainability_agent import ExplainabilityAgent
from agents.speculation_agent import SpeculationAgent
from agents.recommendation_agent import RecommendationAgent
import os


class ChurnWorkflow:
    """
    Main workflow orchestrator for customer churn assessment
    
    Flow:
    1. Customer Data → Risk Assessment Agent → Risk Metrics + SHAP
    2. Risk Results → Explainability Agent → Natural Language Explanation
    3. Explained Results → Speculation Agent → Churn Reasons
    4. Speculated Results → Recommendation Agent → Retention Strategies
    5. Return Complete Assessment
    """
    
    def __init__(
        self,
        model_path: str,
        scaler_path: str,
        features_path: str,
        api_key: str = None
    ):
        """Initialize all agents in the workflow"""
        
        print("🚀 Initializing Churn Assessment Workflow...")
        print("=" * 60)
        
        # Initialize risk agent (always required)
        self.risk_agent = RiskAssessmentAgent(
            model_path=model_path,
            scaler_path=scaler_path,
            features_path=features_path
        )
        
        # Initialize AI agents (optional - will work without API key)
        self.ai_enabled = False
        try:
            self.explainability_agent = ExplainabilityAgent(api_key=api_key)
            self.speculation_agent = SpeculationAgent(api_key=api_key)
            self.recommendation_agent = RecommendationAgent(api_key=api_key)
            self.ai_enabled = True
            print("✅ AI Agents initialized (LangChain + Gemini)")
        except Exception as e:
            print(f"⚠️  AI Agents disabled: {str(e)[:80]}")
            print("   → Workflow will run with ML predictions and SHAP only")
            self.explainability_agent = None
            self.speculation_agent = None
            self.recommendation_agent = None
        
        print("=" * 60)
        print("✅ Workflow Ready!")
        print()
    
    async def process(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process customer through the complete workflow
        
        Args:
            customer_data: Dictionary with customer attributes
                Required fields:
                - days_tenure: int
                - curr_ann_amt: float
                - age_in_years: int
                - income_filled: float
                - has_children: int (0 or 1)
                - home_owner: int (0 or 1)
                - college_degree: int (0 or 1)
                - good_credit: int (0 or 1)
                - is_married: int (0 or 1)
                - length_of_residence_filled: float
                
        Returns:
            Complete assessment with all agent outputs
        """
        print(f"📋 Processing customer: {customer_data.get('customer_id', 'Unknown')}")
        
        # Step 1: Risk Assessment with SHAP (always runs)
        print("   ⚙️  Step 1: Risk Assessment Agent...")
        risk_results = self.risk_agent.assess_risk(customer_data)
        print(f"      → Churn Probability: {risk_results['churn_probability']:.2%}")
        print(f"      → Risk Category: {risk_results['risk_category']}")
        
        # Initialize with risk results
        final_results = risk_results
        
        if self.ai_enabled:
            # Steps 2-4: Run AI agents in PARALLEL (major performance boost!)
            print("   ⚙️  Steps 2-4: Running AI Agents in Parallel...")
            
            import asyncio
            
            # Run all three agents concurrently - they all only need risk_results
            explained_task = asyncio.create_task(
                asyncio.to_thread(self.explainability_agent.explain, risk_results)
            )
            speculated_task = asyncio.create_task(
                asyncio.to_thread(self.speculation_agent.speculate, risk_results)
            )
            recommended_task = asyncio.create_task(
                asyncio.to_thread(self.recommendation_agent.recommend, risk_results)
            )
            
            # Wait for all agents to complete
            explained_results, speculated_results, recommended_results = await asyncio.gather(
                explained_task, 
                speculated_task,
                recommended_task
            )
            
            print(f"      → Generated explanation")
            print(f"      → Generated {len(speculated_results.get('speculation_items', []))} speculation items")
            print(f"      → Generated {len(recommended_results.get('recommendations', []))} recommendations")
            
            # Merge all results
            final_results = risk_results.copy()
            final_results.update(explained_results)
            final_results.update(speculated_results)
            final_results.update(recommended_results)
        else:
            # Use fallback explanations based on SHAP values
            print("   ⚙️  Steps 2-4: Using SHAP-based fallback explanations...")
            final_results = self._create_fallback_results(risk_results)
            print(f"      → Generated basic explanations and recommendations")
        
        print("✅ Processing complete!")
        print()
        
        return self._format_output(final_results)
    
    def _create_fallback_results(self, risk_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic explanations when AI agents are not available"""
        
        # Generate explanation from SHAP values
        top_factors = risk_results['top_factors']
        prob = risk_results['churn_probability']
        risk_cat = risk_results['risk_category']
        
        # Build explanation
        explanation_parts = [
            f"This customer has a {risk_cat.lower()} churn risk with a {prob:.1%} probability of churning."
        ]
        
        if top_factors:
            increasing = [f for f in top_factors if f['shap_value'] > 0]
            decreasing = [f for f in top_factors if f['shap_value'] < 0]
            
            if increasing:
                explanation_parts.append(
                    f"Key risk factors include: {', '.join([f['feature'] for f in increasing[:3]])}."
                )
            
            if decreasing:
                explanation_parts.append(
                    f"Protective factors include: {', '.join([f['feature'] for f in decreasing[:2]])}."
                )
        
        explanation = " ".join(explanation_parts)
        
        # Create basic recommendations
        recommendations = []
        
        if prob > 0.7:
            recommendations.append({
                'action': 'Immediate contact required - High churn risk detected',
                'expected_impact': 'High - Urgent intervention needed',
                'timeline': 'Immediate (24-48 hours)',
                'priority': 'high'
            })
        
        if prob > 0.5:
            recommendations.append({
                'action': 'Review account and offer retention incentives',
                'expected_impact': 'Medium - May prevent churn',
                'timeline': 'Short-term (1-2 weeks)',
                'priority': 'high' if prob > 0.7 else 'medium'
            })
        
        recommendations.append({
            'action': 'Monitor customer engagement and satisfaction',
            'expected_impact': 'Medium - Ongoing risk assessment',
            'timeline': 'Ongoing',
            'priority': 'medium'
        })
        
        # Add factor-specific recommendations
        for factor in top_factors[:3]:
            if factor['shap_value'] > 0:
                feature_name = factor['feature'].replace('_', ' ').title()
                recommendations.append({
                    'action': f'Address {feature_name} - identified as key risk factor',
                    'expected_impact': 'Medium',
                    'timeline': 'Short-term (2-4 weeks)',
                    'priority': 'medium'
                })
        
        # Build result
        result = risk_results.copy()
        result['explanation'] = explanation
        result['detailed_factors'] = [
            f"{f['feature']}: {f['impact']} churn risk by {abs(f['shap_value']):.3f}"
            for f in top_factors[:5]
        ]
        result['risk_indicators'] = [f['feature'] for f in top_factors if f['shap_value'] > 0]
        result['speculation'] = f"Based on ML analysis, primary risk factors are: {', '.join([f['feature'] for f in top_factors[:3]])}."
        result['speculation_items'] = [
            f"Risk Factor: {f['feature']} (impact: {abs(f['shap_value']):.3f})"
            for f in top_factors[:5]
        ]
        result['recommendations'] = recommendations
        
        return result
    
    def _format_output(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format final output for frontend consumption"""
        return {
            'workflow_status': 'completed',
            'customer_type': results['customer_data'].get('customer_type', 'existing'),
            
            # Risk Assessment section
            'risk_assessment': {
                'churn_probability': results['churn_probability'],
                'risk_category': results['risk_category'],
                'confidence': results['confidence_score'],
                'top_factors': results['top_factors']
            },
            
            # Explainability section
            'explanation': {
                'explanation': results['explanation'],
                'detailed_factors': results.get('detailed_factors', []),
                'risk_indicators': results.get('risk_indicators', [])
            },
            
            # Speculation section
            'speculation': {
                'primary_reasons': self._extract_reasons(results.get('speculation', '')),
                'churn_triggers': self._extract_triggers(results.get('speculation', '')),
                'risk_timeline': [],
                'behavioral_indicators': []
            },
            
            # Recommendations section
            'recommendations': {
                'immediate_actions': [r for r in results.get('recommendations', []) if r.get('priority') == 'high'],
                'short_term_strategies': [r for r in results.get('recommendations', []) if r.get('timeline') and '3-5' in r.get('timeline', '')],
                'long_term_initiatives': [r for r in results.get('recommendations', []) if r.get('priority') == 'medium'],
                'priority_scores': {r['action']: r.get('priority', 'medium') for r in results.get('recommendations', [])}
            },
            
            # Processing metadata
            'processing_steps': [
                'Risk Assessment with ML + SHAP',
                'Explainability Analysis',
                'Churn Speculation',
                'Retention Recommendations'
            ]
        }
    
    def _extract_reasons(self, text: str) -> list:
        """Extract primary reasons from speculation text"""
        if not text:
            return []
        # Split by numbered sections and take first 3
        sections = []
        for line in text.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.')) and 'Primary' in line or 'Secondary' in line or 'External' in line:
                sections.append(line.strip())
        return sections[:3] if sections else [text[:200]]
    
    def _extract_triggers(self, text: str) -> list:
        """Extract churn triggers from speculation text"""
        if not text:
            return []
        triggers = []
        for line in text.split('\n'):
            if 'trigger' in line.lower() or 'catalyst' in line.lower():
                triggers.append(line.strip())
        return triggers[:5] if triggers else []
    
    def process_sync(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of process (for non-async contexts)"""
        import asyncio
        return asyncio.run(self.process(customer_data))
