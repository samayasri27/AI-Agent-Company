from dotenv import load_dotenv
load_dotenv()
from agents.agent_base import AgentBase
import os
import subprocess
import logging
import requests

class GitHubTool:
    def __init__(self, repo_path, remote="origin"):
        self.repo_path = repo_path
        self.remote = remote
        self.token = os.environ.get("GITHUB_TOKEN")
        self.username = os.environ.get("GITHUB_USERNAME")

    def git_add_commit_push(self, commit_message):
        cmds = [
            ["git", "add", "."],
            ["git", "commit", "-m", commit_message]
        ]
        for cmd in cmds:
            try:
                subprocess.check_output(cmd, cwd=self.repo_path)
            except subprocess.CalledProcessError as e:
                logging.error(f"Git command failed: {e.output}")
                return False
        # Push with authentication if token is provided
        push_cmd = ["git", "push", self.remote, "HEAD"]
        env = os.environ.copy()
        if self.token and self.username:
            env["GIT_ASKPASS"] = "echo"
            env["GIT_USERNAME"] = self.username
            env["GIT_PASSWORD"] = self.token
            # Use HTTPS remote with token
            try:
                subprocess.check_output(push_cmd, cwd=self.repo_path, env=env)
            except subprocess.CalledProcessError as e:
                logging.error(f"Git push failed: {e.output}")
                return False
        else:
            try:
                subprocess.check_output(push_cmd, cwd=self.repo_path)
            except subprocess.CalledProcessError as e:
                logging.error(f"Git push failed: {e.output}")
                return False
        return True

class DeploymentTool:
    def trigger_deployment(self):
        # Example: Trigger a deployment webhook (replace URL with your actual endpoint)
        deployment_url = os.environ.get("DEPLOYMENT_WEBHOOK_URL")
        if deployment_url:
            try:
                response = requests.post(deployment_url)
                if response.status_code == 200:
                    logging.info("Deployment pipeline triggered via webhook.")
                    return True
                else:
                    logging.error(f"Deployment webhook failed: {response.text}")
                    return False
            except Exception as e:
                logging.error(f"Deployment webhook exception: {e}")
                return False
        else:
            logging.info("Deployment pipeline triggered (mock).")
            return True

class CICDTool:
    def trigger_cicd(self):
        # Example: Trigger a CI/CD webhook (replace URL with your actual endpoint)
        cicd_url = os.environ.get("CICD_WEBHOOK_URL")
        if cicd_url:
            try:
                response = requests.post(cicd_url)
                if response.status_code == 200:
                    logging.info("CI/CD workflow triggered via webhook.")
                    return True
                else:
                    logging.error(f"CI/CD webhook failed: {response.text}")
                    return False
            except Exception as e:
                logging.error(f"CI/CD webhook exception: {e}")
                return False
        else:
            logging.info("CI/CD workflow triggered (mock).")
            return True

class NotificationTool:
    def send_notification(self, message):
        # Example: Send notification to Telegram (extend for Discord, Slack, etc.)
        telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if telegram_token and telegram_chat_id:
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            data = {"chat_id": telegram_chat_id, "text": message}
            try:
                response = requests.post(url, data=data)
                if response.status_code == 200:
                    logging.info("Notification sent via Telegram.")
                    return True
                else:
                    logging.error(f"Telegram notification failed: {response.text}")
                    return False
            except Exception as e:
                logging.error(f"Telegram notification exception: {e}")
                return False
        else:
            logging.info(f"Notification sent (mock): {message}")
            return True

class DeploymentAgent(AgentBase):
    def __init__(self, name="Deployment Agent", department="engineering", role="Deployment Specialist", memory=None, memory_manager=None, workspace_folder=None):
        super().__init__(name, department, role, memory, memory_manager)
        self.workspace_folder = workspace_folder
        self.github_tool = GitHubTool(workspace_folder)
        self.deployment_tool = DeploymentTool()
        self.cicd_tool = CICDTool()
        self.notification_tool = NotificationTool()

    async def execute_task(self, task: str, workspace_path: str = None, commit_message: str = "Auto-commit by DeploymentAgent"):
        self.log(f"🚀 DeploymentAgent received task: {task}")
        import os
        import shutil
        if not workspace_path:
            workspace_path = os.path.join(os.getcwd(), "workspace", task.replace(" ", "_"))
        if not os.path.exists(workspace_path):
            self.log(f"❌ Workspace folder does not exist: {workspace_path}")
            return f"Workspace folder does not exist: {workspace_path}"
        # 1. Zip the workspace folder for deployment artifact
        zip_path = workspace_path + ".zip"
        shutil.make_archive(workspace_path, 'zip', workspace_path)
        self.log(f"📦 Zipped workspace folder at: {zip_path}")
        # 2. GitHub commit & push (from workspace folder)
        self.github_tool.repo_path = workspace_path
        if not self.github_tool.git_add_commit_push(commit_message):
            self.notification_tool.send_notification("❌ GitHub push failed.")
            return "GitHub push failed. Aborting deployment."
        self.log("✅ Code pushed to GitHub.")
        # 3. Trigger deployment
        if not self.deployment_tool.trigger_deployment():
            self.notification_tool.send_notification("❌ Deployment failed.")
            return "Deployment failed."
        self.log("✅ Deployment pipeline triggered.")
        # 4. Trigger CI/CD
        if not self.cicd_tool.trigger_cicd():
            self.notification_tool.send_notification("❌ CI/CD failed.")
            return "CI/CD failed."
        self.log("✅ CI/CD workflow triggered.")
        # 5. Notify success
        self.notification_tool.send_notification(f"✅ Deployment complete for task: {task}")
        return f"Deployment complete for task: {task}"
        # 4. Send notification
        self.notification_tool.send_notification("🎉 Deployment and CI/CD successful!")
        self.log("🎉 All actions completed and notifications sent.")
        return "Deployment, CI/CD, and notifications completed."