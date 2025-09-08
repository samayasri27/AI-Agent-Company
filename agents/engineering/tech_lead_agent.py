# agents/engineering/tech_lead_agent.py

from agents.agent_base import AgentBase
from config.company_profile import company_profile
from utils.llm_planner import call_llm
import asyncio

class TechLeadAgent(AgentBase):
    """Tech Lead Agent - Technical leadership and coordination"""
    
    def __init__(self, name="Tech Lead", department="engineering", role="Technical Lead", memory=None, memory_manager=None, research_agent=None, communicator=None, message_event=None):
        super().__init__(name, department, role, memory, memory_manager, research_agent)
        self.communicator = communicator
        self.message_sent_event = message_event
        self.projects = []
        
    def receive_message(self, sender_name, message):
        """Receive message from other agents"""
        self.log(f"📥 Received message from {sender_name}: {message}")
        
        # Process the message and respond
        if "marketing" in sender_name.lower():
            self.log("🔄 Processing marketing requirements...")
            
    async def execute_task(self, task: str):
        """Execute technical leadership task"""
        self.log(f"⚙️ Tech Lead task received: {task}")
        
        # Get company context
        company_context = self.get_company_context()
        
        # Request technical research
        research_query = f"Technical leadership research: {task}"
        research_data = await self.request_research(research_query)
        
        # Execute technical leadership task
        tech_lead_prompt = f"""
You are the Technical Lead for {company_context['company_name']} in the {company_context['sector']} sector.

Company Details:
- Description: {company_context['description']}
- Target Market: {company_context['target_location']}
- Budget: {company_context['budget']} {company_context['currency']}
- Goal: {company_context['goal']}

Task: {task}
Research Data: {research_data}

As Technical Lead, provide leadership covering:
1. Technical architecture and design decisions
2. Technology stack recommendations for Indian market
3. Team coordination and development planning
4. Code quality and best practices
5. Performance optimization strategies
6. Security and compliance considerations
7. Scalability planning for Indian user base
8. Integration with Indian services and APIs
9. Mobile-first development approach
10. Cost-effective technical solutions

Provide detailed technical leadership plan and next steps.
"""
        
        result = call_llm(tech_lead_prompt)
        
        # If communicator is available, send response
        if self.communicator and "marketing" in task.lower():
            response_message = f"[Tech Integration] Technical requirements analyzed: {result[:200]}..."
            self.communicator.send_message(self.name, "Marketing", response_message)
            
            # Signal that message was sent
            if self.message_sent_event:
                self.message_sent_event.set()
        
        # Store project information
        self.projects.append({
            'task': task,
            'result': result,
            'timestamp': self.created_at,
            'status': 'completed'
        })
        
        self.save_to_memory(task, result)
        self.log("✅ Technical leadership task completed")
        
        return f"⚙️ Tech Lead Solution: {result}"
        
    async def review_technical_requirements(self, requirements: str):
        """Review and analyze technical requirements"""
        self.log(f"🔍 Reviewing technical requirements: {requirements}")
        
        company_context = self.get_company_context()
        
        review_prompt = f"""
As Technical Lead, review these technical requirements for {company_context['company_name']}:

Requirements: {requirements}
Company Sector: {company_context['sector']}
Target Market: {company_context['target_location']}
Budget: {company_context['budget']} {company_context['currency']}

Provide technical review covering:
1. Feasibility analysis
2. Technical complexity assessment
3. Resource and timeline estimation
4. Technology recommendations
5. Risk identification and mitigation
6. Architecture considerations
7. Performance and scalability planning
8. Security and compliance requirements
9. Integration challenges and solutions
10. Cost-benefit analysis

Focus on Indian market technical landscape and constraints.
"""
        
        review = call_llm(review_prompt)
        self.save_to_memory(f"Technical Review: {requirements}", review)
        
        return f"🔍 Technical Review: {review}"
        
    async def plan_development_sprint(self, sprint_goals: str):
        """Plan development sprint with team coordination"""
        self.log(f"📅 Planning development sprint: {sprint_goals}")
        
        company_context = self.get_company_context()
        
        sprint_prompt = f"""
As Technical Lead, plan development sprint for {company_context['company_name']}:

Sprint Goals: {sprint_goals}
Company Context: {company_context['description']}
Target Market: {company_context['target_location']}

Plan sprint covering:
1. Sprint objectives and deliverables
2. Task breakdown and prioritization
3. Team member assignments
4. Timeline and milestones
5. Technical dependencies
6. Quality assurance checkpoints
7. Code review processes
8. Testing and deployment strategy
9. Risk management and contingencies
10. Sprint retrospective planning

Consider Indian development team dynamics and work culture.
"""
        
        sprint_plan = call_llm(sprint_prompt)
        self.save_to_memory(f"Sprint Plan: {sprint_goals}", sprint_plan)
        
        return f"📅 Sprint Plan: {sprint_plan}"
        
    async def conduct_technical_review(self, code_or_design: str):
        """Conduct technical review of code or design"""
        self.log(f"👨‍💻 Conducting technical review: {code_or_design}")
        
        review_prompt = f"""
As Technical Lead, conduct thorough technical review:

Subject: {code_or_design}

Review criteria:
1. Code quality and best practices
2. Architecture and design patterns
3. Performance optimization
4. Security considerations
5. Scalability and maintainability
6. Documentation and comments
7. Testing coverage and quality
8. Compliance with coding standards
9. Error handling and edge cases
10. Integration and deployment readiness

Provide detailed feedback with specific recommendations for improvement.
"""
        
        review_result = call_llm(review_prompt)
        self.save_to_memory(f"Technical Review: {code_or_design}", review_result)
        
        return f"👨‍💻 Technical Review: {review_result}"
        
    async def get_project_status(self):
        """Get technical project status"""
        return {
            'total_projects': len(self.projects),
            'completed_projects': len([p for p in self.projects if p['status'] == 'completed']),
            'projects': self.projects
        }