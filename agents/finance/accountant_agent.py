from agents.agent_base import AgentBase
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
import asyncio
import os
from dotenv import load_dotenv

class AccountantAgent(AgentBase):
    def __init__(self, name="Accountant", department="finance", role="Accountant", memory=None, memory_manager=None):
        super().__init__(name, department, role, memory, memory_manager)
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            self.llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192", api_key=api_key)  # Groq LLM setup

    async def execute_task(self, task: str):
        self.log(f"💼 Received accounting task: {task}")

        # Use Groq for financial record management
        accounting_tasks = await self.call_groq_for_accounting(task)
        self.log(f"📚 Accounting Tasks:\n{accounting_tasks}")

        # Send task completion to CFO for approval
        self.send_message_to("CFOAgent", f"Accounting task completed for {task}:\n{accounting_tasks}")
        self.save_to_memory(task, accounting_tasks)

        return f"Accounting task completed for: {task}"

    async def call_groq_for_accounting(self, task_description: str):
        prompt = f"Generate the necessary accounting procedures for the following task: {task_description}. Ensure tax compliance, bookkeeping accuracy, and regulatory standards are met."
        response = self.llm([HumanMessage(content=prompt)])
        return response.content.strip()