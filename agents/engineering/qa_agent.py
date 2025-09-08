from agents.agent_base import AgentBase
import asyncio

class QAAgent(AgentBase):
    def __init__(self, name="QAAgent", department="engineering", role="Tester", memory=None, memory_manager=None, workspace_folder=None):
        super().__init__(name, department, role, memory, memory_manager)
        self.workspace_folder = workspace_folder
    async def execute_task(self, task: str, workspace_path: str = None):
        self.log(f"Received QA task: {task}")
        import os
        if not workspace_path:
            workspace_path = os.path.join(os.getcwd(), "workspace", task.replace(" ", "_"))
        tests_dir = os.path.join(workspace_path, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        # Simulate test execution delay
        await asyncio.sleep(1)
        if "fail" in task.lower():
            result = "❌ Tests failed. Bug report generated."
            self.log(result)
            self.send_message_to("DeveloperAgent", "Tests failed. Please fix the issues.")
            log_file = os.path.join(tests_dir, "test_log.txt")
            with open(log_file, "w") as f:
                f.write(result)
        else:
            result = "✅ All tests passed. Build is ready for deployment."
            self.log(result)
            self.send_message_to("DevOpsAgent", "Tests passed. Proceed to deployment.")
            log_file = os.path.join(tests_dir, "test_log.txt")
            with open(log_file, "w") as f:
                f.write(result)
        self.save_to_memory(task, result)
        self.send_message_to("EngineeringManagerAgent", f"QA Result for '{task}': {result}")
        return result