from agents.agent_base import AgentBase
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
import asyncio
import os
from dotenv import load_dotenv

class FinancialAnalystAgent(AgentBase):
    def __init__(self, name="Financial Analyst", department="finance", role="Financial Analyst", memory=None, memory_manager=None):
        super().__init__(name, department, role, memory, memory_manager)
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            self.llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192", api_key=api_key)  # Groq LLM setup

    async def execute_task(self, task: str):
        self.log(f"📊 Received financial analysis task: {task}")

        # Use Groq for deep financial analysis
        analysis = await self.call_groq_for_analysis(task)
        self.log(f"💡 Financial Analysis:\n{analysis}")

        # Send analysis to CFO for review
        self.send_message_to("CFOAgent", f"Financial analysis for {task}:\n{analysis}")
        self.save_to_memory(task, analysis)

        return f"Financial analysis completed for: {task}"

    async def call_groq_for_analysis(self, task_description: str):
        prompt = f"Perform a deep financial analysis for the following task: {task_description}. Provide key financial insights, profitability forecasts, and cost-benefit analysis."
        response = self.llm([HumanMessage(content=prompt)])
        return response.content.strip()