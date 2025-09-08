# agents/executive/ceo_agent.py

from agents.agent_base import AgentBase
from config.company_profile import company_profile
from utils.llm_planner import call_llm
from engine.workflow_manager import Task, ExecutionPhase
import asyncio

class CEOAgent(AgentBase):
    """CEO Agent - Central task router and strategic decision maker"""
    
    def __init__(self, name="CEO", department="executive", role="Chief Executive Officer", memory=None, memory_manager=None, research_agent=None, workflow_manager=None):
        super().__init__(name, department, role, memory, memory_manager, research_agent)
        self.workflow_manager = workflow_manager
        self.department_heads = {}
        self.task_counter = 0
        
    def register_department_head(self, department: str, head_agent):
        """Register department head agents"""
        self.department_heads[department] = head_agent
        self.log(f"✅ Registered {department} department head: {head_agent.name}")
        
    async def execute_task(self, task: str):
        """CEO processes and routes tasks through proper hierarchy"""
        self.log(f"🎯 CEO received task: {task}")
        
        # Get company context for decision making
        company_context = self.get_company_context()
        
        # Analyze task and create strategic plan
        strategic_analysis = await self._analyze_task_strategically(task, company_context)
        
        # Break down task into department-specific subtasks
        subtasks = await self._break_down_task(task, strategic_analysis)
        
        # Route tasks through workflow manager
        if self.workflow_manager and subtasks:
            await self._route_through_workflow(subtasks)
            
        self.save_to_memory(task, f"Strategic analysis completed and tasks routed: {strategic_analysis}")
        return f"🎯 CEO: Strategic plan executed for '{task}'"
        
    async def _analyze_task_strategically(self, task: str, company_context: dict):
        """Analyze task from strategic perspective"""
        self.log("🧠 Conducting strategic analysis...")
        
        # Request market research if needed
        if "market" in task.lower() or "launch" in task.lower() or "competition" in task.lower():
            research_query = f"Strategic market analysis for: {task}"
            research_data = await self.request_research(research_query)
        else:
            research_data = "No additional research required"
        
        strategic_prompt = f"""
You are the CEO of {company_context['company_name']}, a {company_context['sector']} company in {company_context['target_location']}.
Company Description: {company_context['description']}
Budget: {company_context['budget']} {company_context['currency']}
Goal: {company_context['goal']}

Task to analyze: {task}

Research Data: {research_data}

As CEO, provide strategic analysis covering:
1. Strategic importance and alignment with company goals
2. Resource requirements and budget implications
3. Risk assessment and mitigation strategies
4. Timeline and priority level
5. Success metrics and KPIs
6. Stakeholder impact analysis
7. Market positioning implications for Indian market

Provide clear, actionable strategic insights.
"""
        
        strategic_analysis = call_llm(strategic_prompt)
        
        # Fallback if LLM fails
        if "Error:" in strategic_analysis or "failed" in strategic_analysis.lower():
            strategic_analysis = f"""
Strategic Analysis for: {task}

1. Strategic Importance: This task aligns with {company_context['company_name']}'s goal of {company_context['goal']} in the {company_context['sector']} sector.

2. Resource Requirements: Budget allocation from {company_context['budget']} {company_context['currency']} will be required for execution.

3. Risk Assessment: Standard business risks apply. Mitigation through proper planning and execution.

4. Timeline: Standard project timeline with phased approach recommended.

5. Success Metrics: Achievement of task objectives within budget and timeline.

6. Market Positioning: Focused on {company_context['target_location']} market dynamics.

Recommendation: Proceed with task execution through appropriate departments.
"""
        
        self.log("✅ Strategic analysis completed")
        return strategic_analysis
        
    async def _break_down_task(self, original_task: str, strategic_analysis: str):
        """Break down task into department-specific subtasks"""
        self.log("📋 Breaking down task into department subtasks...")
        
        # Use rule-based task routing instead of LLM parsing to avoid API issues
        subtasks = self._create_rule_based_subtasks(original_task)
        
        self.log(f"📋 Created {len(subtasks)} department subtasks")
        return subtasks
        
    def _create_rule_based_subtasks(self, original_task: str):
        """Create subtasks based on task content and available departments"""
        subtasks = []
        task_lower = original_task.lower()
        
        # Marketing tasks
        if any(word in task_lower for word in ['marketing', 'campaign', 'promotion', 'brand', 'social', 'content', 'diwali', 'festival']):
            subtasks.append(self._create_task_from_dict({
                'department': 'marketing',
                'description': f"Execute marketing strategy for: {original_task}",
                'phase': ExecutionPhase.PARALLEL,
                'priority': 2,
                'dependencies': []
            }))
        
        # Engineering/Development tasks
        if any(word in task_lower for word in ['develop', 'app', 'platform', 'software', 'code', 'technical', 'system', 'upi', 'payment', 'e-commerce', 'mobile']):
            subtasks.append(self._create_task_from_dict({
                'department': 'engineering',
                'description': f"Develop technical solution for: {original_task}",
                'phase': ExecutionPhase.PARALLEL,
                'priority': 1,
                'dependencies': []
            }))
        
        # Research tasks
        if any(word in task_lower for word in ['research', 'analysis', 'competitor', 'market', 'study']):
            subtasks.append(self._create_task_from_dict({
                'department': 'research',
                'description': f"Conduct research for: {original_task}",
                'phase': ExecutionPhase.SEQUENTIAL,
                'priority': 1,
                'dependencies': []
            }))
        
        # If no specific department identified, create a general strategic task
        if not subtasks:
            # Route to the most appropriate department based on company sector
            company_context = self.get_company_context()
            if 'tech' in company_context['sector'].lower() or 'it' in company_context['sector'].lower():
                dept = 'engineering'
            else:
                dept = 'marketing'
                
            subtasks.append(self._create_task_from_dict({
                'department': dept,
                'description': f"Handle strategic task: {original_task}",
                'phase': ExecutionPhase.PARALLEL,
                'priority': 2,
                'dependencies': []
            }))
        
        return subtasks
        
    def _parse_task_breakdown(self, breakdown_text: str):
        """Parse LLM breakdown into structured Task objects"""
        subtasks = []
        current_task = {}
        
        for line in breakdown_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Department:'):
                if current_task:
                    subtasks.append(self._create_task_from_dict(current_task))
                current_task = {'department': line.split(':', 1)[1].strip().lower()}
                
            elif line.startswith('Task:'):
                current_task['description'] = line.split(':', 1)[1].strip()
                
            elif line.startswith('Phase:'):
                phase_str = line.split(':', 1)[1].strip().lower()
                current_task['phase'] = ExecutionPhase.SEQUENTIAL if 'sequential' in phase_str else ExecutionPhase.PARALLEL
                
            elif line.startswith('Priority:'):
                try:
                    current_task['priority'] = int(line.split(':', 1)[1].strip())
                except:
                    current_task['priority'] = 3
                    
            elif line.startswith('Dependencies:'):
                deps = line.split(':', 1)[1].strip()
                current_task['dependencies'] = [d.strip() for d in deps.split(',') if d.strip() and d.strip().lower() != 'none']
        
        # Add the last task
        if current_task:
            subtasks.append(self._create_task_from_dict(current_task))
            
        return subtasks
        
    def _create_task_from_dict(self, task_dict: dict):
        """Create Task object from dictionary"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        return Task(
            id=task_id,
            description=task_dict.get('description', 'Undefined task'),
            department=task_dict.get('department', 'general'),
            dependencies=task_dict.get('dependencies', []),
            phase=task_dict.get('phase', ExecutionPhase.PARALLEL),
            priority=task_dict.get('priority', 3)
        )
        
    async def _route_through_workflow(self, subtasks: list):
        """Route tasks through workflow manager"""
        self.log(f"🔄 Routing {len(subtasks)} tasks through workflow manager...")
        self.log(f"📋 Available departments: {list(self.department_heads.keys())}")
        
        # Add tasks to workflow manager
        tasks_added = 0
        for task in subtasks:
            self.log(f"📝 Processing task for department: {task.department}")
            if task.department in self.department_heads:
                self.workflow_manager.add_task(task)
                tasks_added += 1
                self.log(f"✅ Added task to {task.department}: {task.description}")
            else:
                self.log(f"⚠️ No department head found for: {task.department}")
        
        self.log(f"📊 Added {tasks_added} tasks to workflow manager")
        
        # Plan and execute workflow
        if tasks_added > 0:
            self.workflow_manager.plan_execution()
            await self.workflow_manager.execute_workflow()
        else:
            self.log("⚠️ No tasks were added to workflow manager")
        
    async def get_company_status(self):
        """Get overall company status from all departments"""
        self.log("📊 Gathering company status from all departments...")
        
        status_reports = {}
        for dept_name, dept_head in self.department_heads.items():
            try:
                status = await dept_head.execute_task("Provide department status report")
                status_reports[dept_name] = status
            except Exception as e:
                status_reports[dept_name] = f"Error getting status: {e}"
                
        return status_reports
        
    async def make_strategic_decision(self, decision_context: str):
        """Make strategic decisions based on context"""
        self.log(f"🎯 Making strategic decision: {decision_context}")
        
        # Get research data for decision making
        research_data = await self.request_research(f"Strategic decision support: {decision_context}")
        
        company_context = self.get_company_context()
        
        decision_prompt = f"""
As CEO of {company_context['company_name']}, make a strategic decision:

Context: {decision_context}
Research Data: {research_data}
Company Budget: {company_context['budget']} {company_context['currency']}
Company Goal: {company_context['goal']}
Target Market: {company_context['target_location']}

Provide:
1. Decision recommendation
2. Rationale and supporting factors
3. Resource allocation requirements
4. Risk mitigation strategies
5. Implementation timeline
6. Success metrics

Focus on Indian market dynamics and cultural considerations.
"""
        
        decision = call_llm(decision_prompt)
        self.save_to_memory(f"Strategic Decision: {decision_context}", decision)
        
        return decision