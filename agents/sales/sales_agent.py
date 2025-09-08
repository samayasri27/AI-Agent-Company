"""
Sales Agent - Lead generation and outreach strategy
"""
import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.agent_base import AgentBase
from utils.memory_system_init import get_memory_manager_for_agent


class SalesAgent(AgentBase):
    """Sales Agent for lead generation and outreach strategy"""
    
    def __init__(self):
        super().__init__(
            name="Sales Agent",
            role="Lead Generation & Outreach Strategy",
            department="Sales"
        )
        self.capabilities = [
            "Lead generation and qualification",
            "Outreach strategy development", 
            "CRM integration and management",
            "Sales pipeline analysis",
            "Customer segmentation",
            "Sales performance tracking"
        ]
        self.memory_system = get_memory_manager_for_agent('sales')
        self.crm_api_key = os.getenv('HUBSPOT_API_KEY') or os.getenv('ZOHO_CRM_API_KEY')
        self.crm_base_url = self._get_crm_base_url()
        
    def _get_crm_base_url(self) -> str:
        """Get CRM base URL based on available API keys"""
        if os.getenv('HUBSPOT_API_KEY'):
            return "https://api.hubapi.com"
        elif os.getenv('ZOHO_CRM_API_KEY'):
            return "https://www.zohoapis.com/crm/v2"
        else:
            return "http://localhost:3001/api/mock-crm"  # Mock CRM for testing
    
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """Execute sales-related tasks"""
        try:
            # Parse task if it's a string
            if isinstance(task, str):
                task_dict = {'description': task, 'type': 'general'}
            else:
                task_dict = task
            
            task_type = task_dict.get('type', '').lower()
            task_description = task_dict.get('description', task if isinstance(task, str) else '')
            
            if 'lead generation' in task_description or 'generate leads' in task_description:
                return self._generate_leads(task_dict)
            elif 'outreach' in task_description or 'strategy' in task_description:
                return self._develop_outreach_strategy(task_dict)
            elif 'crm' in task_description or 'pipeline' in task_description:
                return self._analyze_sales_pipeline(task_dict)
            elif 'segment' in task_description or 'customer' in task_description:
                return self._segment_customers(task_dict)
            else:
                return self._general_sales_analysis(task_dict)
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Sales task processing failed: {str(e)}",
                'agent': self.name,
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_leads(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate leads based on criteria"""
        criteria = task.get('criteria', {})
        target_count = task.get('target_count', 50)
        
        # Check memory for similar lead generation requests
        memory_query = f"lead generation {criteria.get('industry', '')} {criteria.get('company_size', '')}"
        historical_data = self.memory_system.search_knowledge(memory_query, limit=5)
        
        # Generate leads using CRM API or mock data
        leads = self._fetch_leads_from_crm(criteria, target_count)
        
        # Qualify leads based on criteria
        qualified_leads = self._qualify_leads(leads, criteria)
        
        # Store results in memory
        result = {
            'success': True,
            'leads_generated': len(qualified_leads),
            'qualified_leads': qualified_leads[:10],  # Return top 10
            'criteria_used': criteria,
            'historical_insights': len(historical_data),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in memory for future reference if using persistent mode
        if self.should_use_memory():
            self.memory_system.store_knowledge(
                f"Lead generation for {criteria.get('industry', 'general')} industry",
                json.dumps(result),
                metadata={'department': 'sales', 'type': 'lead_generation'}
            )
        
        # Generate sales report document
        try:
            doc_content = {
                'title': f'Lead Generation Report - {criteria.get("industry", "General")} Industry',
                'author': self.name,
                'subject': 'Sales Lead Analysis',
                'executive_summary': f'Generated {len(qualified_leads)} qualified leads for {criteria.get("industry", "general")} industry based on specified criteria.',
                'sections': [
                    {
                        'title': 'Lead Generation Summary',
                        'content': f'Total Qualified Leads: {len(qualified_leads)}\\nIndustry Focus: {criteria.get("industry", "General")}\\nCompany Size: {criteria.get("company_size", "All sizes")}\\nLocation: {criteria.get("location", "Global")}'
                    },
                    {
                        'title': 'Top Qualified Leads',
                        'table': {
                            'headers': ['Company', 'Contact', 'Industry', 'Size', 'Score'],
                            'rows': [[
                                lead.get('company', 'N/A'),
                                lead.get('contact_name', 'N/A'),
                                lead.get('industry', 'N/A'),
                                lead.get('company_size', 'N/A'),
                                str(lead.get('score', 0))
                            ] for lead in qualified_leads[:10]]
                        }
                    },
                    {
                        'title': 'Qualification Criteria',
                        'bullet_points': [f"{k}: {v}" for k, v in criteria.items()]
                    }
                ]
            }
            
            filename = f"lead_generation_{criteria.get('industry', 'general').replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}"
            docx_path = self.create_document(doc_content, 'docx', filename)
            
            if docx_path:
                result['generated_files'] = [docx_path]
                self.log(f"Generated lead generation report: {filename}.docx")
                
        except Exception as e:
            self.log(f"Error generating lead report document: {str(e)}")
            result['document_generation_error'] = str(e)
        
        return result
    
    def _develop_outreach_strategy(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Develop outreach strategy for leads"""
        target_audience = task.get('target_audience', {})
        campaign_type = task.get('campaign_type', 'email')
        
        # Get historical outreach performance
        memory_query = f"outreach strategy {campaign_type} {target_audience.get('industry', '')}"
        historical_data = self.memory_system.search_knowledge(memory_query, limit=3)
        
        # Develop strategy based on audience and historical data
        strategy = {
            'campaign_type': campaign_type,
            'target_segments': self._identify_target_segments(target_audience),
            'messaging_framework': self._create_messaging_framework(target_audience),
            'channel_strategy': self._recommend_channels(target_audience),
            'timeline': self._create_outreach_timeline(),
            'success_metrics': self._define_success_metrics(campaign_type),
            'historical_insights': [item.get('content', '') for item in historical_data]
        }
        
        result = {
            'success': True,
            'strategy': strategy,
            'estimated_reach': self._estimate_reach(target_audience),
            'expected_conversion_rate': self._estimate_conversion_rate(campaign_type),
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store strategy in memory
        self.memory_system.store_knowledge(
            f"Outreach strategy for {target_audience.get('industry', 'general')}",
            json.dumps(result),
            metadata={'department': 'sales', 'type': 'outreach_strategy'}
        )
        
        return result
    
    def _analyze_sales_pipeline(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sales pipeline and performance"""
        time_period = task.get('time_period', '30_days')
        
        # Fetch pipeline data from CRM
        pipeline_data = self._fetch_pipeline_data(time_period)
        
        # Analyze pipeline health
        analysis = {
            'pipeline_value': pipeline_data.get('total_value', 0),
            'deals_by_stage': pipeline_data.get('deals_by_stage', {}),
            'conversion_rates': self._calculate_conversion_rates(pipeline_data),
            'bottlenecks': self._identify_bottlenecks(pipeline_data),
            'recommendations': self._generate_pipeline_recommendations(pipeline_data),
            'forecast': self._generate_sales_forecast(pipeline_data)
        }
        
        result = {
            'success': True,
            'analysis': analysis,
            'time_period': time_period,
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store analysis in memory
        self.memory_system.store_knowledge(
            f"Sales pipeline analysis {time_period}",
            json.dumps(result),
            metadata={'department': 'sales', 'type': 'pipeline_analysis'}
        )
        
        return result
    
    def _segment_customers(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Segment customers based on various criteria"""
        segmentation_criteria = task.get('criteria', ['industry', 'company_size', 'revenue'])
        
        # Fetch customer data from CRM
        customer_data = self._fetch_customer_data()
        
        # Perform segmentation
        segments = {}
        for criterion in segmentation_criteria:
            segments[criterion] = self._segment_by_criterion(customer_data, criterion)
        
        # Generate insights for each segment
        segment_insights = {}
        for criterion, segment_data in segments.items():
            segment_insights[criterion] = self._analyze_segment_performance(segment_data)
        
        result = {
            'success': True,
            'segments': segments,
            'insights': segment_insights,
            'total_customers': len(customer_data),
            'segmentation_criteria': segmentation_criteria,
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store segmentation in memory
        self.memory_system.store_knowledge(
            f"Customer segmentation analysis",
            json.dumps(result),
            metadata={'department': 'sales', 'type': 'customer_segmentation'}
        )
        
        return result
    
    def _general_sales_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """General sales analysis and insights"""
        analysis_type = task.get('analysis_type', 'performance')
        
        # Get recent sales data and insights from memory
        memory_query = f"sales {analysis_type} performance metrics"
        historical_data = self.memory_system.search_knowledge(memory_query, limit=5)
        
        # Perform general analysis
        analysis = {
            'sales_performance': self._analyze_sales_performance(),
            'market_trends': self._analyze_market_trends(),
            'competitive_analysis': self._analyze_competition(),
            'recommendations': self._generate_sales_recommendations(),
            'historical_context': len(historical_data)
        }
        
        result = {
            'success': True,
            'analysis': analysis,
            'analysis_type': analysis_type,
            'agent': self.name,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    # Helper methods for CRM integration
    def _fetch_leads_from_crm(self, criteria: Dict, count: int) -> List[Dict]:
        """Fetch leads from CRM API or generate mock data"""
        if not self.crm_api_key:
            return self._generate_mock_leads(criteria, count)
        
        try:
            headers = {'Authorization': f'Bearer {self.crm_api_key}'}
            response = requests.get(
                f"{self.crm_base_url}/contacts",
                headers=headers,
                params={'limit': count, **criteria},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                return self._generate_mock_leads(criteria, count)
                
        except Exception:
            return self._generate_mock_leads(criteria, count)
    
    def _generate_mock_leads(self, criteria: Dict, count: int) -> List[Dict]:
        """Generate mock leads for testing"""
        industries = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail']
        company_sizes = ['Startup', 'SMB', 'Mid-market', 'Enterprise']
        
        leads = []
        for i in range(count):
            lead = {
                'id': f'lead_{i+1}',
                'company_name': f'Company {i+1}',
                'industry': criteria.get('industry') or industries[i % len(industries)],
                'company_size': criteria.get('company_size') or company_sizes[i % len(company_sizes)],
                'contact_name': f'Contact {i+1}',
                'email': f'contact{i+1}@company{i+1}.com',
                'phone': f'+1-555-{1000+i}',
                'score': 50 + (i % 50),
                'created_date': datetime.now().isoformat()
            }
            leads.append(lead)
        
        return leads
    
    def _qualify_leads(self, leads: List[Dict], criteria: Dict) -> List[Dict]:
        """Qualify leads based on criteria"""
        qualified = []
        min_score = criteria.get('min_score', 70)
        
        for lead in leads:
            if lead.get('score', 0) >= min_score:
                lead['qualification_status'] = 'qualified'
                qualified.append(lead)
            else:
                lead['qualification_status'] = 'needs_nurturing'
        
        return sorted(qualified, key=lambda x: x.get('score', 0), reverse=True)
    
    # Additional helper methods
    def _identify_target_segments(self, audience: Dict) -> List[Dict]:
        """Identify target segments for outreach"""
        return [
            {'name': 'High-value prospects', 'criteria': 'Enterprise companies', 'priority': 1},
            {'name': 'Growth companies', 'criteria': 'Mid-market with growth potential', 'priority': 2},
            {'name': 'Strategic partners', 'criteria': 'Complementary businesses', 'priority': 3}
        ]
    
    def _create_messaging_framework(self, audience: Dict) -> Dict:
        """Create messaging framework for outreach"""
        return {
            'value_proposition': 'Streamline operations with AI-powered automation',
            'pain_points': ['Manual processes', 'Inefficient workflows', 'High operational costs'],
            'benefits': ['Increased efficiency', 'Cost reduction', 'Scalable operations'],
            'call_to_action': 'Schedule a demo to see AI automation in action'
        }
    
    def _recommend_channels(self, audience: Dict) -> List[str]:
        """Recommend outreach channels"""
        return ['Email', 'LinkedIn', 'Phone calls', 'Industry events']
    
    def _create_outreach_timeline(self) -> Dict:
        """Create outreach timeline"""
        return {
            'week_1': 'Initial contact and introduction',
            'week_2': 'Follow-up with value proposition',
            'week_3': 'Demo scheduling and qualification',
            'week_4': 'Proposal and next steps'
        }
    
    def _define_success_metrics(self, campaign_type: str) -> Dict:
        """Define success metrics for campaigns"""
        return {
            'open_rate': '25%' if campaign_type == 'email' else 'N/A',
            'response_rate': '5%',
            'meeting_booking_rate': '2%',
            'conversion_rate': '0.5%'
        }
    
    def _estimate_reach(self, audience: Dict) -> int:
        """Estimate campaign reach"""
        return audience.get('estimated_size', 1000)
    
    def _estimate_conversion_rate(self, campaign_type: str) -> float:
        """Estimate conversion rate based on campaign type"""
        rates = {'email': 0.02, 'linkedin': 0.03, 'phone': 0.05, 'event': 0.08}
        return rates.get(campaign_type, 0.02)
    
    def _fetch_pipeline_data(self, time_period: str) -> Dict:
        """Fetch pipeline data from CRM"""
        # Mock pipeline data for demonstration
        return {
            'total_value': 500000,
            'deals_by_stage': {
                'prospecting': 15,
                'qualification': 12,
                'proposal': 8,
                'negotiation': 5,
                'closed_won': 3,
                'closed_lost': 2
            },
            'average_deal_size': 25000,
            'sales_cycle_length': 45
        }
    
    def _calculate_conversion_rates(self, pipeline_data: Dict) -> Dict:
        """Calculate conversion rates between stages"""
        stages = pipeline_data.get('deals_by_stage', {})
        total_deals = sum(stages.values())
        
        return {
            'prospecting_to_qualification': 0.8,
            'qualification_to_proposal': 0.67,
            'proposal_to_negotiation': 0.63,
            'negotiation_to_close': 0.6,
            'overall_win_rate': stages.get('closed_won', 0) / total_deals if total_deals > 0 else 0
        }
    
    def _identify_bottlenecks(self, pipeline_data: Dict) -> List[str]:
        """Identify pipeline bottlenecks"""
        return [
            'Long qualification process',
            'Proposal approval delays',
            'Pricing negotiations'
        ]
    
    def _generate_pipeline_recommendations(self, pipeline_data: Dict) -> List[str]:
        """Generate recommendations for pipeline improvement"""
        return [
            'Implement automated lead scoring',
            'Streamline proposal generation process',
            'Provide sales team with better negotiation tools',
            'Focus on high-value prospects'
        ]
    
    def _generate_sales_forecast(self, pipeline_data: Dict) -> Dict:
        """Generate sales forecast"""
        return {
            'next_month': 150000,
            'next_quarter': 400000,
            'confidence_level': 'Medium',
            'key_assumptions': ['Current pipeline velocity', 'Historical conversion rates']
        }
    
    def _fetch_customer_data(self) -> List[Dict]:
        """Fetch customer data for segmentation"""
        # Mock customer data
        return [
            {'id': 1, 'industry': 'Technology', 'company_size': 'Enterprise', 'revenue': 1000000},
            {'id': 2, 'industry': 'Healthcare', 'company_size': 'Mid-market', 'revenue': 500000},
            {'id': 3, 'industry': 'Finance', 'company_size': 'SMB', 'revenue': 100000}
        ]
    
    def _segment_by_criterion(self, customers: List[Dict], criterion: str) -> Dict:
        """Segment customers by specific criterion"""
        segments = {}
        for customer in customers:
            value = customer.get(criterion, 'Unknown')
            if value not in segments:
                segments[value] = []
            segments[value].append(customer)
        return segments
    
    def _analyze_segment_performance(self, segment_data: List[Dict]) -> Dict:
        """Analyze performance of customer segment"""
        return {
            'count': len(segment_data),
            'avg_revenue': sum(c.get('revenue', 0) for c in segment_data) / len(segment_data) if segment_data else 0,
            'growth_potential': 'High' if len(segment_data) > 5 else 'Medium'
        }
    
    def _analyze_sales_performance(self) -> Dict:
        """Analyze overall sales performance"""
        return {
            'monthly_revenue': 250000,
            'growth_rate': 0.15,
            'deals_closed': 12,
            'average_deal_size': 20833
        }
    
    def _analyze_market_trends(self) -> List[str]:
        """Analyze market trends"""
        return [
            'Increased demand for AI automation',
            'Remote work driving digital transformation',
            'Focus on operational efficiency'
        ]
    
    def _analyze_competition(self) -> Dict:
        """Analyze competitive landscape"""
        return {
            'main_competitors': ['Competitor A', 'Competitor B', 'Competitor C'],
            'competitive_advantages': ['AI-powered automation', 'Scalable architecture', 'Cost-effective'],
            'market_position': 'Growing challenger'
        }
    
    def _generate_sales_recommendations(self) -> List[str]:
        """Generate sales recommendations"""
        return [
            'Focus on enterprise accounts for higher deal values',
            'Develop industry-specific solutions',
            'Invest in sales automation tools',
            'Expand partner channel program'
        ]