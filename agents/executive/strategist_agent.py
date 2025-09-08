from agents.agent_base import AgentBase
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
import asyncio
import os
from dotenv import load_dotenv

class StrategistAgent(AgentBase):
    def __init__(self, name="Strategist Agent", department="executive", role="Strategy Lead", memory=None, memory_manager=None):
        super().__init__(name, department, role, memory, memory_manager)
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            self.llm = ChatGroq(temperature=0.4, model_name="llama3-8b-8192", api_key=api_key)  # Groq LLM setup

    async def execute_task(self, task: str):
        self.log(f"📈 Received strategic task: {task}")

        # Use Groq for strategic reasoning
        strategy_plan = await self.call_groq_for_strategy(task)
        self.log(f"💡 Strategic Plan:\n{strategy_plan}")

        # Delegate tasks based on strategy (simplified, can be made complex)
        self.send_message_to("CEOAgent", f"Strategic plan for '{task}':\n{strategy_plan}")
        self.save_to_memory(task, strategy_plan)

        return f"Strategic plan generated for: {task}"

    async def call_groq_for_strategy(self, task_description: str):
        prompt = f"Provide a high-level strategic plan to achieve the following business objective: {task_description}. Include recommendations for key actions, team responsibilities, and key metrics."
        response = self.llm([HumanMessage(content=prompt)])
        return response.content.strip()