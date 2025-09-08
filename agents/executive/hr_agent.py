from agents.agent_base import AgentBase
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
import asyncio
import os
from dotenv import load_dotenv

class HRAgent(AgentBase):
    def __init__(self, name="HR Agent", department="executive", role="Human Resources", memory=None, memory_manager=None):
        super().__init__(name, department, role, memory, memory_manager)
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            self.llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192", api_key=api_key)  # Groq LLM setup

    async def execute_task(self, task: str):
        self.log(f"👥 Received HR task: {task}")

        # Use Groq to provide HR-related advice or actions
        hr_recommendations = await self.call_groq_for_hr(task)
        self.log(f"💬 HR Recommendations:\n{hr_recommendations}")

        # Delegate HR insights to CEO or team manager
        self.send_message_to("CEOAgent", f"HR insights for {task}:\n{hr_recommendations}")
        self.save_to_memory(task, hr_recommendations)

        return f"HR task completed for: {task}"

    async def call_groq_for_hr(self, task_description: str):
        prompt = f"Provide human resources recommendations for the following task: {task_description}. This includes team management, employee engagement, and hiring strategies."
        response = self.llm([HumanMessage(content=prompt)])
        return response.content.strip()