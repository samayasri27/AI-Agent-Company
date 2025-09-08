# agents/executive/department_head_base.py

from agents.agent_base import AgentBase
from config.company_profile import company_profile
from utils.llm_planner import call_llm
import asyncio

class DepartmentHeadBase(AgentBase):
    """Base class for all department heads in the executive team"""
    
    def __init__(self, name, department, role, memory=None, memory_manager=None, research_agent=None):
        super().__init__(name, department, role, memory, memory_manager, research_agent)
        self.department_agents = {}
        self.department_tasks = []
        
    def register_department_agent(self, agent_name: str, agent):
        """Register agents within this department"""
        self.department_agents[agent_name] = agent
        self.log(f"✅ Registered department agent: {agent_name}")
        
    async def execute_task(self, task: str):
        """Department head processes tasks and delegates to department agents"""
        self.log(f"📋 Department head received task: {task}")
        
        # Analyze task from department perspective
        department_analysis = await self._analyze_department_task(task)
        
        # Determine if task needs delegation or direct execution
        if self._should_delegate(task):
            result = await self._delegate_task(task, department_analysis)
        else:
            result = await self._execute_directly(task, department_analysis)
            
        self.department_tasks.append({
            'task': task,
            'result': result,
            'timestamp': self.created_at
        })
        
        self.save_to_memory(task, result)
        return result
        
    async def _analyze_department_task(self, task: str):
        """Analyze task from department perspective"""
        company_context = self.get_company_context()
        
        analysis_prompt = f"""
You are the {self.role} of {company_context['company_name']}'s {self.department} department.
Company: {company_context['description']}
Target Market: {company_context['target_location']}
Budget: {company_context['budget']} {company_context['currency']}

Task: {task}

Analyze this task from your department's perspective:
1. Relevance to department goals and capabilities
2. Resource requirements and timeline
3. Potential challenges and solutions
4. Success criteria and deliverables
5. Coordination needs with other departments
6. Indian market specific considerations

Provide actionable analysis for department execution.
"""
        
        analysis = call_llm(analysis_prompt)
        self.log("✅ Department task analysis completed")
        return analysis
        
    def _should_delegate(self, task: str) -> bool:
        """Determine if task should be delegated to department agents"""
        # Override in specific department heads
        delegation_keywords = ['implement', 'execute', 'develop', 'create', 'build', 'design']
        return any(keyword in task.lower() for keyword in delegation_keywords)
        
    async def _delegate_task(self, task: str, analysis: str):
        """Delegate task to appropriate department agent"""
        if not self.department_agents:
            return await self._execute_directly(task, analysis)
            
        # Find best agent for the task
        best_agent = self._select_best_agent(task)
        
        if best_agent:
            self.log(f"🔄 Delegating to {best_agent.name}")
            return await best_agent.execute_task(task)
        else:
            return await self._execute_directly(task, analysis)
            
    def _select_best_agent(self, task: str):
        """Select the best agent for the task - override in specific departments"""
        if self.department_agents:
            return list(self.department_agents.values())[0]
        return None
        
    async def _execute_directly(self, task: str, analysis: str):
        """Execute task directly as department head"""
        self.log(f"⚡ Executing task directly: {task}")
        
        company_context = self.get_company_context()
        
        execution_prompt = f"""
As {self.role} of {company_context['company_name']}, execute this task:

Task: {task}
Department Analysis: {analysis}
Company Context: {company_context['description']}
Target Market: {company_context['target_location']}

Execute the task with focus on:
1. Department-specific expertise and approach
2. Indian market considerations
3. Budget efficiency ({company_context['budget']} {company_context['currency']})
4. Alignment with company goals
5. Quality deliverables and outcomes

Provide detailed execution results and next steps.
"""
        
        result = call_llm(execution_prompt)
        self.log("✅ Direct execution completed")
        return f"🎯 {self.role}: {result}"
        
    async def get_department_status(self):
        """Get status of entire department"""
        status = {
            'department': self.department,
            'head': self.name,
            'agents_count': len(self.department_agents),
            'completed_tasks': len(self.department_tasks),
            'agents': list(self.department_agents.keys())
        }
        
        return status
        
    async def coordinate_with_department(self, other_department: str, message: str):
        """Coordinate with other department heads"""
        self.log(f"🤝 Coordinating with {other_department}: {message}")
        # This would be implemented with actual inter-department communication
        return f"Coordination message sent to {other_department}"