# agents/research/research_agent.py

from agents.agent_base import AgentBase
from config.company_profile import company_profile
from utils.llm_planner import call_llm
import asyncio

class ResearchAgent(AgentBase):
    """Centralized research agent accessible by all departments"""
    
    def __init__(self, name="Research Agent", department="research", role="Knowledge Specialist", memory=None, memory_manager=None, fallback_mode=False):
        super().__init__(name, department, role, memory, memory_manager)
        self.research_cache = {}  # Cache for frequently requested research
        self.fallback_mode = fallback_mode  # Use simple responses instead of LLM
        
    async def execute_task(self, task: str):
        """Execute research task with Indian market focus"""
        self.log(f"🔍 Research task received: {task}")
        
        # Get company context for targeted research
        company_context = company_profile.get_context()
        
        # Enhanced prompt with Indian market focus
        research_prompt = f"""
You are a research specialist for {company_context['company_name']} in the {company_context['sector']} sector.
Company Description: {company_context['description']}
Target Market: {company_context['target_location']} - {company_context['market_focus']}
Budget: {company_context['budget']} {company_context['currency']}

Research Task: {task}

Provide comprehensive research with specific focus on:
1. Indian market dynamics and consumer behavior
2. Local competition and market leaders
3. Regulatory requirements in India
4. Cultural considerations and preferences
5. Pricing strategies suitable for Indian market
6. Distribution channels and partnerships
7. Digital adoption trends in India
8. Regional variations (North, South, East, West India)

Format your response with clear sections and actionable insights.
"""
        
        # Check cache first
        cache_key = f"{task}_{company_context['sector']}_{company_context['target_location']}"
        if cache_key in self.research_cache:
            self.log("📋 Using cached research data")
            cached_result = self.research_cache[cache_key]
            return f"🔍 Research Complete (Cached): {cached_result}"
        
        # Perform new research
        if self.fallback_mode:
            research_result = f"""
Research Summary for: {task}

Key Findings for Indian Market:
1. Market Size: Large and growing market opportunity in {company_context['target_location']}
2. Competition: Moderate to high competition with established players
3. Consumer Behavior: Price-sensitive customers with mobile-first preferences
4. Regulatory Environment: Standard Indian business regulations apply
5. Technology Adoption: High smartphone penetration, growing digital adoption
6. Cultural Factors: Festival seasons and regional preferences important
7. Distribution: Digital channels and local partnerships recommended
8. Pricing Strategy: Competitive pricing with value-based positioning

Recommendation: Proceed with localized approach focusing on Indian market needs.
"""
        else:
            research_result = call_llm(research_prompt)
        
        # Cache the result
        self.research_cache[cache_key] = research_result
        
        # Save to memory
        self.save_to_memory(task, research_result)
        
        self.log("✅ Research completed and cached")
        return f"🔍 Research Complete: {research_result}"
    
    async def get_market_insights(self, query: str):
        """Specialized method for market research"""
        market_task = f"Market insights for: {query}"
        return await self.execute_task(market_task)
    
    async def get_competitor_analysis(self, sector: str):
        """Specialized method for competitor analysis"""
        competitor_task = f"Competitor analysis in {sector} sector for Indian market"
        return await self.execute_task(competitor_task)
    
    async def get_regulatory_info(self, business_type: str):
        """Specialized method for regulatory research"""
        regulatory_task = f"Regulatory requirements for {business_type} business in India"
        return await self.execute_task(regulatory_task)
    
    async def get_pricing_strategy(self, product_type: str, target_segment: str):
        """Specialized method for pricing research"""
        pricing_task = f"Pricing strategy for {product_type} targeting {target_segment} in Indian market"
        return await self.execute_task(pricing_task)
    
    def clear_cache(self):
        """Clear research cache"""
        self.research_cache.clear()
        self.log("🗑️ Research cache cleared")
    
    def get_cached_research(self):
        """Get all cached research topics"""
        return list(self.research_cache.keys())