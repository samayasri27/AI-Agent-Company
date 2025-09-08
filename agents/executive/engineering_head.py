# agents/executive/engineering_head.py

from agents.executive.department_head_base import DepartmentHeadBase
from utils.llm_planner import call_llm

class EngineeringHead(DepartmentHeadBase):
    """Engineering Department Head - manages technical strategy and development"""
    
    def __init__(self, name="Engineering Head", department="engineering", role="Chief Technology Officer", memory=None, memory_manager=None, research_agent=None):
        super().__init__(name, department, role, memory, memory_manager, research_agent)
        
    def _should_delegate(self, task: str) -> bool:
        """Engineering-specific delegation logic"""
        delegation_keywords = [
            'develop', 'code', 'implement', 'build', 'create application',
            'write software', 'deploy', 'test', 'debug', 'review code'
        ]
        return any(keyword in task.lower() for keyword in delegation_keywords)
        
    def _select_best_agent(self, task: str):
        """Select best engineering agent for the task"""
        task_lower = task.lower()
        
        # Development tasks
        if any(word in task_lower for word in ['develop', 'code', 'implement', 'build']):
            return self.department_agents.get('developer')
            
        # Testing tasks
        if any(word in task_lower for word in ['test', 'qa', 'quality']):
            return self.department_agents.get('qa_engineer')
            
        # Deployment tasks
        if any(word in task_lower for word in ['deploy', 'devops', 'infrastructure']):
            return self.department_agents.get('devops_engineer')
            
        # Code review tasks
        if any(word in task_lower for word in ['review', 'audit', 'security']):
            return self.department_agents.get('code_reviewer')
            
        # Default to first available agent
        return list(self.department_agents.values())[0] if self.department_agents else None
        
    async def _execute_directly(self, task: str, analysis: str):
        """Execute engineering task directly with Indian tech landscape focus"""
        self.log(f"⚙️ Engineering Head executing: {task}")
        
        # Get technical research
        research_query = f"Technical research for Indian market: {task}"
        research_data = await self.request_research(research_query)
        
        company_context = self.get_company_context()
        
        engineering_prompt = f"""
As Chief Technology Officer of {company_context['company_name']}, execute this technical task:

Task: {task}
Analysis: {analysis}
Technical Research: {research_data}

Company Details:
- Sector: {company_context['sector']}
- Target: {company_context['target_location']}
- Budget: {company_context['budget']} {company_context['currency']}
- Goal: {company_context['goal']}

Execute with focus on:
1. Indian tech infrastructure and connectivity considerations
2. Mobile-first development approach for Indian users
3. Cost-effective technology stack suitable for budget
4. Scalability for Indian market size and diversity
5. Local compliance and data protection requirements
6. Integration with popular Indian payment systems
7. Multi-language support capabilities
8. Offline-first features for areas with poor connectivity
9. Performance optimization for lower-end devices

Provide detailed technical strategy and implementation plan.
"""
        
        result = call_llm(engineering_prompt)
        return f"⚙️ Technical Strategy: {result}"
        
    async def design_system_architecture(self, system_requirements: str):
        """Design system architecture"""
        self.log(f"🏗️ Designing system architecture: {system_requirements}")
        
        # Get technical research
        tech_research = await self.request_research(f"System architecture research: {system_requirements}")
        
        architecture_task = f"Design system architecture for: {system_requirements}"
        return await self.execute_task(architecture_task)
        
    async def evaluate_technology_stack(self, project_requirements: str):
        """Evaluate and recommend technology stack"""
        self.log(f"🔧 Evaluating technology stack: {project_requirements}")
        
        company_context = self.get_company_context()
        
        tech_research = await self.request_research(f"Technology stack evaluation: {project_requirements}")
        
        evaluation_prompt = f"""
As CTO, evaluate and recommend technology stack for:

Requirements: {project_requirements}
Research Data: {tech_research}
Company: {company_context['company_name']} ({company_context['sector']})
Budget: {company_context['budget']} {company_context['currency']}
Target Market: {company_context['target_location']}

Provide recommendations covering:
1. Frontend technologies (mobile-first for Indian users)
2. Backend technologies (scalable and cost-effective)
3. Database solutions (suitable for Indian data requirements)
4. Cloud infrastructure (considering Indian data centers)
5. Third-party integrations (payment gateways, etc.)
6. Development tools and frameworks
7. Security and compliance considerations
8. Cost analysis and budget alignment
9. Timeline and resource requirements

Focus on technologies popular and well-supported in India.
"""
        
        evaluation = call_llm(evaluation_prompt)
        self.save_to_memory(f"Tech Stack Evaluation: {project_requirements}", evaluation)
        
        return f"🔧 Technology Evaluation: {evaluation}"
        
    async def plan_development_roadmap(self, project_scope: str):
        """Plan development roadmap"""
        self.log(f"🗺️ Planning development roadmap: {project_scope}")
        
        company_context = self.get_company_context()
        
        roadmap_prompt = f"""
As CTO, create development roadmap for:

Project Scope: {project_scope}
Company: {company_context['company_name']}
Budget: {company_context['budget']} {company_context['currency']}
Target Market: {company_context['target_location']}

Create roadmap with:
1. Phase-wise development plan
2. Milestone definitions and timelines
3. Resource allocation and team requirements
4. Risk assessment and mitigation strategies
5. Quality assurance checkpoints
6. Deployment and launch strategy
7. Post-launch support and maintenance
8. Scalability planning for Indian market growth

Consider Indian development talent availability and costs.
"""
        
        roadmap = call_llm(roadmap_prompt)
        self.save_to_memory(f"Development Roadmap: {project_scope}", roadmap)
        
        return f"🗺️ Development Roadmap: {roadmap}"