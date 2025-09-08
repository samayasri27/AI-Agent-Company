from agents.agent_base import AgentBase
import asyncio
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
import os
from dotenv import load_dotenv

class COOAgent(AgentBase):
    def __init__(self, name="COO Agent", department="leadership", role="Chief Operating Officer", memory=None, memory_manager=None, scheduler=None):
        super().__init__(name, department, role, memory, memory_manager)
        self.scheduler = scheduler
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            self.llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192", api_key=api_key)  # Groq LLM setup

    async def execute_task(self, task: str):
        self.log(f"🔄 Received high-level directive: {task}")

        # Simulate task assignment and decision-making process
        await asyncio.sleep(1)

        # Use Groq for strategic task assignment
        try:
            strategy = await self.call_groq_for_strategy(task)
        except Exception as e:
            self.log(f"Failed to get strategy from LLM: {e}")
            strategy = "COO Manual Review Required."

        self.log(f"COO Strategy Output: {strategy}")

        # Delegate tasks based on strategy output
        subtasks = self.parse_strategy(strategy)

        for dept, subtask in subtasks:
            self.log(f"Delegating to {dept}: {subtask}")
            try:
                await self.scheduler.assign_task(dept, subtask)
            except KeyError:
                self.log(f"No agent registered under department: {dept}")

        return "COO delegation complete."

    async def call_groq_for_strategy(self, task_description: str):
        prompt = f"Based on the following business objective, generate strategic task assignments for relevant departments: {task_description}"
        response = self.llm([HumanMessage(content=prompt)])
        return response.content.strip()

    def parse_strategy(self, strategy: str):
        # Simulate parsing the strategy into actionable items
        # Example strategy response parsing (this can be more complex depending on the output)
        return [
            ("Marketing", "Create a pre-launch awareness campaign"),
            ("Engineering", "Start building MVP architecture"),
            ("Product", "Define user flow and wireframes")
        ]