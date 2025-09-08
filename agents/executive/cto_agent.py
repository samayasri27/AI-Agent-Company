from agents.agent_base import AgentBase
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
import asyncio
import os
from dotenv import load_dotenv

class CTOAgent(AgentBase):
    def __init__(self, name="CTO Agent", department="executive", role="Chief Technology Officer", memory=None, memory_manager=None):
        super().__init__(name, department, role, memory, memory_manager)
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            self.llm = ChatGroq(temperature=0.4, model_name="llama3-8b-8192", api_key=api_key)  # Groq LLM setup

    async def execute_task(self, task: str):
        self.log(f"💻 Received tech task: {task}")

        # Use Groq to analyze tech requirements
        tech_recommendations = await self.call_groq_for_technology(task)
        self.log(f"🔧 Technology Recommendations:\n{tech_recommendations}")

        # Send recommendations to CEO or Engineering Manager
        self.send_message_to("EngineeringManagerAgent", f"Tech recommendations for {task}:\n{tech_recommendations}")
        self.save_to_memory(task, tech_recommendations)

        return f"Technology recommendations generated for: {task}"

    async def call_groq_for_technology(self, task_description: str):
        prompt = f"Provide technology strategy recommendations for the following business objective: {task_description}. Include recommendations for technology stack, tools, and potential architecture decisions."
        response = self.llm([HumanMessage(content=prompt)])
        return response.content.strip()