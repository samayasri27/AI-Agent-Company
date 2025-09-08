from agents.agent_base import AgentBase
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage

class DevOpsAgent(AgentBase):
    def __init__(self, name="DevOps Agent", department="engineering", role="Infrastructure & Deployment", memory=None, memory_manager=None, workspace_folder=None):
        super().__init__(name, department, role, memory, memory_manager)
        self.workspace_folder = workspace_folder
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        model_name = os.getenv('MODEL_NAME', 'llama3-8b-8192')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            try:
                self.llm = ChatGroq(temperature=0.3, model_name=model_name, api_key=api_key)
            except Exception as e:
                self.log(f"⚠️ Error initializing Groq client: {str(e)}")
                self.llm = None

    async def execute_task(self, task: str):
        self.log(f"🛠️ Received deployment request: {task}")

        # Ask Groq to generate a safe deployment plan
        plan_prompt = f"""You are a DevOps engineer. The QA team has approved the following feature for deployment:\n\n'{task}'\n\nGenerate a short, professional deployment plan for pushing this to production."""
        plan = self.llm([HumanMessage(content=plan_prompt)]).content.strip()

        self.log(f"📦 Deployment Plan:\n{plan}")

        # Simulate deployment
        await asyncio.sleep(1)
        deploy_msg = f"🚀 Successfully deployed: {task}"
        self.log(deploy_msg)

        self.save_to_memory(task, f"✅ Deployed to production.\n\n{plan}")

        # Notify Engineering Manager
        self.send_message_to("EngineeringManagerAgent", f"Deployment complete for: {task}\n\n{plan}")

        return "Deployment complete"