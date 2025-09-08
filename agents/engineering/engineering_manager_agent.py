from agents.agent_base import AgentBase
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage

class EngineeringManagerAgent(AgentBase):
    def __init__(self, name="Engineering Manager", department="engineering", role="Team Lead", memory=None, memory_manager=None, workspace_folder=None):
        super().__init__(name, department, role, memory, memory_manager)
        self.workspace_folder = workspace_folder
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        model_name = os.getenv('MODEL_NAME', 'llama3-8b-8192')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            try:
                self.llm = ChatGroq(temperature=0.4, model_name=model_name, api_key=api_key)
            except Exception as e:
                self.log(f"⚠️ Error initializing Groq client: {str(e)}")
                self.llm = None

    def receive_message(self, sender_name, message):
        self.log(f"📩 Update from {sender_name}: {message}")
        self.save_to_memory(f"From {sender_name}", message)

    async def execute_task(self, task: str):
        self.log(f"🧠 Received team management task: {task}")

        # Ask Groq to analyze the engineering task or team load
        prompt = f"""You are an engineering manager. Based on the following situation or task, plan what to do:\n\n'{task}'"""
        response = self.llm([HumanMessage(content=prompt)]).content.strip()

        self.log(f"📋 Strategy Plan:\n{response}")
        self.save_to_memory(task, response)

        # Optionally communicate with Developer
        if "developer" in task.lower():
            self.send_message_to("DeveloperAgent", f"Priority update: {task}")
        elif "qa" in task.lower():
            self.send_message_to("QAAgent", f"Please reverify: {task}")
        elif "devops" in task.lower():
            self.send_message_to("DevOpsAgent", f"Prepare rollback plan for: {task}")
        # After code reviewer and manager approval, delegate deployment
        if "deployment approved" in task.lower() or "ready for deployment" in task.lower():
            self.send_message_to("DeploymentAgent", f"Deploy: {task}")

        return "Engineering plan processed and delegated."