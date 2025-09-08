from agents.agent_base import AgentBase
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
import asyncio
import os
from dotenv import load_dotenv

class TreasurerAgent(AgentBase):
    def __init__(self, name="Treasurer", department="finance", role="Treasurer", memory=None, memory_manager=None):
        super().__init__(name, department, role, memory, memory_manager)
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            self.llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192", api_key=api_key)  # Groq LLM setup

    async def execute_task(self, task: str):
        self.log(f"💸 Received treasury task: {task}")

        # Use Groq for capital management and investment strategy
        treasury_advice = await self.call_groq_for_treasury(task)
        self.log(f"📈 Treasury Advice:\n{treasury_advice}")

        # Send advice to CFO for further action
        self.send_message_to("CFOAgent", f"Treasury advice for {task}:\n{treasury_advice}")
        self.save_to_memory(task, treasury_advice)

        return f"Treasury task completed for: {task}"

    async def call_groq_for_treasury(self, task_description: str):
        prompt = f"Provide financial advice for managing the company's capital, including cash flow optimization, investment strategies, and financial risk mitigation for: {task_description}"
        response = self.llm([HumanMessage(content=prompt)])
        return response.content.strip()