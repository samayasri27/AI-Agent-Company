# agents/executive/finance_head.py

from agents.executive.department_head_base import DepartmentHeadBase
from utils.llm_planner import call_llm

class FinanceHead(DepartmentHeadBase):
    """Finance Department Head - manages financial strategy and operations"""
    
    def __init__(self, name="Finance Head", department="finance", role="Chief Financial Officer", memory=None, memory_manager=None, research_agent=None):
        super().__init__(name, department, role, memory, memory_manager, research_agent)
        
    def _should_delegate(self, task: str) -> bool:
        """Finance-specific delegation logic"""
        delegation_keywords = [
            'calculate', 'analyze financials', 'prepare budget', 'audit',
            'tax planning', 'investment analysis', 'cost analysis'
        ]
        return any(keyword in task.lower() for keyword in delegation_keywords)
        
    def _select_best_agent(self, task: str):
        """Select best finance agent for the task"""
        task_lower = task.lower()
        
        # Accounting tasks
        if any(word in task_lower for word in ['accounting', 'bookkeeping', 'ledger']):
            return self.department_agents.get('accountant')
            
        # Analysis tasks
        if any(word in task_lower for word in ['analysis', 'forecast', 'projection']):
            return self.department_agents.get('financial_analyst')
            
        # Treasury tasks
        if any(word in task_lower for word in ['cash', 'treasury', 'investment']):
            return self.department_agents.get('treasurer')
            
        # Default to first available agent
        return list(self.department_agents.values())[0] if self.department_agents else None
        
    async def _execute_directly(self, task: str, analysis: str):
        """Execute finance task directly with Indian financial landscape focus"""
        self.log(f"💰 Finance Head executing: {task}")
        
        # Get financial research
        research_query = f"Financial research for Indian market: {task}"
        research_data = await self.request_research(research_query)
        
        company_context = self.get_company_context()
        
        finance_prompt = f"""
As Chief Financial Officer of {company_context['company_name']}, execute this financial task:

Task: {task}
Analysis: {analysis}
Financial Research: {research_data}

Company Details:
- Sector: {company_context['sector']}
- Target: {company_context['target_location']}
- Budget: {company_context['budget']} {company_context['currency']}
- Goal: {company_context['goal']}

Execute with focus on:
1. Indian financial regulations and compliance (RBI, SEBI, GST)
2. Tax optimization strategies for Indian businesses
3. Currency considerations and forex management
4. Banking relationships with Indian financial institutions
5. Investment opportunities in Indian market
6. Cost optimization for Indian operations
7. Financial reporting as per Indian accounting standards
8. Risk management for Indian market volatility
9. Funding options available in India (VCs, banks, government schemes)
10. Digital payment integration and financial technology

Provide detailed financial strategy and implementation plan.
"""
        
        result = call_llm(finance_prompt)
        return f"💰 Financial Strategy: {result}"
        
    async def create_budget_plan(self, budget_requirements: str):
        """Create comprehensive budget plan"""
        self.log(f"📊 Creating budget plan: {budget_requirements}")
        
        company_context = self.get_company_context()
        
        # Get budget research
        budget_research = await self.request_research(f"Budget planning for Indian business: {budget_requirements}")
        
        budget_prompt = f"""
Create comprehensive budget plan for {company_context['company_name']}:

Budget Requirements: {budget_requirements}
Research Data: {budget_research}
Available Budget: {company_context['budget']} {company_context['currency']}
Business Sector: {company_context['sector']}

Create budget plan covering:
1. Revenue projections and assumptions
2. Operating expense breakdown
3. Capital expenditure planning
4. Marketing and sales budget allocation
5. Technology and infrastructure costs
6. Human resource and payroll planning
7. Compliance and regulatory costs
8. Contingency and risk reserves
9. Tax planning and optimization
10. Cash flow projections and management

Focus on Indian market costs, taxation, and business environment.
"""
        
        budget_plan = call_llm(budget_prompt)
        self.save_to_memory(f"Budget Plan: {budget_requirements}", budget_plan)
        
        return f"📊 Budget Plan: {budget_plan}"
        
    async def analyze_financial_performance(self, performance_period: str):
        """Analyze financial performance"""
        self.log(f"📈 Analyzing financial performance: {performance_period}")
        
        company_context = self.get_company_context()
        
        performance_prompt = f"""
Analyze financial performance for {company_context['company_name']}:

Performance Period: {performance_period}
Company Sector: {company_context['sector']}
Target Market: {company_context['target_location']}
Budget: {company_context['budget']} {company_context['currency']}

Provide analysis covering:
1. Revenue analysis and growth trends
2. Profitability and margin analysis
3. Cost structure and efficiency metrics
4. Cash flow analysis and liquidity position
5. Return on investment (ROI) calculations
6. Market performance benchmarking
7. Financial ratios and key indicators
8. Risk assessment and mitigation
9. Recommendations for improvement
10. Future financial projections

Consider Indian market dynamics and economic factors.
"""
        
        analysis = call_llm(performance_prompt)
        self.save_to_memory(f"Financial Performance: {performance_period}", analysis)
        
        return f"📈 Financial Analysis: {analysis}"