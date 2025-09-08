# agents/executive/marketing_head.py

from agents.executive.department_head_base import DepartmentHeadBase
from utils.llm_planner import call_llm

class MarketingHead(DepartmentHeadBase):
    """Marketing Department Head - manages marketing strategy and campaigns"""
    
    def __init__(self, name="Marketing Head", department="marketing", role="Chief Marketing Officer", memory=None, memory_manager=None, research_agent=None):
        super().__init__(name, department, role, memory, memory_manager, research_agent)
        
    def _should_delegate(self, task: str) -> bool:
        """Marketing-specific delegation logic"""
        delegation_keywords = [
            'create content', 'write copy', 'design campaign', 'social media',
            'blog post', 'advertisement', 'promotional material', 'content strategy'
        ]
        return any(keyword in task.lower() for keyword in delegation_keywords)
        
    def _select_best_agent(self, task: str):
        """Select best marketing agent for the task"""
        task_lower = task.lower()
        
        # Content-related tasks
        if any(word in task_lower for word in ['content', 'copy', 'write', 'blog']):
            return self.department_agents.get('content_creator')
            
        # Campaign-related tasks
        if any(word in task_lower for word in ['campaign', 'strategy', 'plan']):
            return self.department_agents.get('campaign_manager')
            
        # Social media tasks
        if any(word in task_lower for word in ['social', 'instagram', 'facebook', 'twitter']):
            return self.department_agents.get('social_media_manager')
            
        # Default to first available agent
        return list(self.department_agents.values())[0] if self.department_agents else None
        
    async def _execute_directly(self, task: str, analysis: str):
        """Execute marketing task directly with Indian market focus"""
        self.log(f"📢 Marketing Head executing: {task}")
        
        # Get market research for marketing decisions
        research_query = f"Marketing research for Indian market: {task}"
        research_data = await self.request_research(research_query)
        
        company_context = self.get_company_context()
        
        marketing_prompt = f"""
As Chief Marketing Officer of {company_context['company_name']}, execute this marketing task:

Task: {task}
Analysis: {analysis}
Market Research: {research_data}

Company Details:
- Sector: {company_context['sector']}
- Target: {company_context['target_location']}
- Budget: {company_context['budget']} {company_context['currency']}
- Goal: {company_context['goal']}

Execute with focus on:
1. Indian consumer behavior and preferences
2. Cultural sensitivity and local relevance
3. Cost-effective marketing channels for Indian market
4. Regional language considerations
5. Digital-first approach suitable for Indian demographics
6. Festival and seasonal marketing opportunities
7. Tier-1, Tier-2, and Tier-3 city strategies
8. Mobile-first marketing approach

Provide detailed marketing strategy and execution plan.
"""
        
        result = call_llm(marketing_prompt)
        return f"📢 Marketing Strategy: {result}"
        
    async def create_marketing_campaign(self, campaign_objective: str):
        """Create comprehensive marketing campaign"""
        self.log(f"🎯 Creating marketing campaign: {campaign_objective}")
        
        # Get market insights
        market_research = await self.request_research(f"Campaign research: {campaign_objective}")
        
        campaign_task = f"Create comprehensive marketing campaign for: {campaign_objective}"
        return await self.execute_task(campaign_task)
        
    async def analyze_market_opportunity(self, opportunity: str):
        """Analyze market opportunity"""
        self.log(f"📊 Analyzing market opportunity: {opportunity}")
        
        research_data = await self.request_research(f"Market opportunity analysis: {opportunity}")
        
        company_context = self.get_company_context()
        
        analysis_prompt = f"""
As CMO, analyze this market opportunity for {company_context['company_name']}:

Opportunity: {opportunity}
Research Data: {research_data}
Current Focus: {company_context['sector']} in {company_context['target_location']}

Provide analysis covering:
1. Market size and potential in India
2. Target audience segmentation
3. Competitive landscape
4. Entry barriers and challenges
5. Marketing approach and channels
6. Budget requirements and ROI projections
7. Timeline and milestones
8. Risk assessment

Focus on Indian market dynamics and consumer behavior.
"""
        
        analysis = call_llm(analysis_prompt)
        self.save_to_memory(f"Market Opportunity: {opportunity}", analysis)
        
        return f"📊 Market Analysis: {analysis}"