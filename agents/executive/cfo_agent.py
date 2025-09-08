from agents.agent_base import AgentBase
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
import asyncio
import os
from dotenv import load_dotenv

class CFOAgent(AgentBase):
    def __init__(self, name="CFO Agent", department="executive", role="Chief Financial Officer", memory=None, memory_manager=None):
        super().__init__(name, department, role, memory, memory_manager)
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            self.llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192", api_key=api_key)  # Groq LLM setup

    async def execute_task(self, task: str):
        self.log(f"💼 Received financial task: {task}")

        # Use Groq for enhanced financial analysis and forecasting
        financial_plan = await self.call_groq_for_financial_forecast(task)
        self.log(f"📊 Financial Plan:\n{financial_plan}")

        # Delegate financial recommendations to CEO or COO
        self.send_message_to("CEOAgent", f"Financial insights for {task}:\n{financial_plan}")
        self.save_to_memory(task, financial_plan)

        return f"Financial analysis completed for: {task}"

    async def call_groq_for_financial_forecast(self, task_description: str):
        prompt = f"Analyze the following business task and provide financial recommendations, including budgeting, revenue forecasting, profit and loss estimates, and capital allocation: {task_description}"
        response = self.llm([HumanMessage(content=prompt)])
        return response.content.strip()

    async def generate_profit_and_loss(self):
        # Example: Generate a quarterly profit and loss statement for the company
        prompt = "Generate a quarterly profit and loss statement, considering revenue, expenses, and taxes."
        response = self.llm([HumanMessage(content=prompt)])
        return response.content.strip()

    async def provide_investment_advice(self):
        # Example: Suggest investment strategies based on current financial health
        prompt = "Provide investment advice based on the current financial status and market trends."
        response = self.llm([HumanMessage(content=prompt)])
        return response.content.strip()