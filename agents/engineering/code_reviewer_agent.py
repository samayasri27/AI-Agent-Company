from agents.agent_base import AgentBase
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage

class CodeReviewerAgent(AgentBase):
    def __init__(self, name="Code Reviewer", department="engineering", role="Code Quality Reviewer", memory=None, memory_manager=None, workspace_folder=None):
        super().__init__(name, department, role, memory, memory_manager)
        self.workspace_folder = workspace_folder
        api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY_1') or os.getenv('GROQ_API_KEY_2')
        model_name = os.getenv('MODEL_NAME', 'llama3-8b-8192')
        if not api_key:
            self.log("⚠️ Warning: No GROQ_API_KEY environment variables found - running in limited mode")
            self.llm = None
        else:
            try:
                self.llm = ChatGroq(temperature=0.2, model_name=model_name, api_key=api_key)
            except Exception as e:
                self.log(f"⚠️ Error initializing Groq client: {str(e)}")
                self.llm = None

    async def execute_task(self, task: str, workspace_path: str = None):
        self.log(f"🔍 Reviewing submitted code for: {task}")
        import os
        if not workspace_path:
            workspace_path = os.path.join(os.getcwd(), "workspace", task.replace(" ", "_"))
        os.makedirs(workspace_path, exist_ok=True)
        code_file = os.path.join(workspace_path, "main.py")
        code_content = "[Code file not found]"
        if os.path.exists(code_file):
            with open(code_file, "r") as f:
                code_content = f.read()
        prompt = f"""You are a senior code reviewer. Here's the code submitted for '{task}':\n\n{code_content}\n\nGive a brief review and state whether it is ready for merge or needs changes."""
        review = self.llm([HumanMessage(content=prompt)]).content.strip() if self.llm else "[Limited mode: No review performed. GROQ_API_KEY not set.]"
        self.log(f"🧾 Review Output:\n{review}")
        review_file = os.path.join(workspace_path, "review.txt")
        with open(review_file, "w") as f:
            f.write(review)
        self.save_to_memory(task, review)
        if "needs changes" in review.lower() or "rejected" in review.lower():
            self.send_message_to("DeveloperAgent", f"Code review failed for '{task}'. Feedback:\n{review}")
        else:
            self.send_message_to("EngineeringManagerAgent", f"✅ Code approved for '{task}'.\n\n{review}")
            self.send_message_to("DevOpsAgent", f"✅ Code approved for deployment: '{task}'.")
        return review