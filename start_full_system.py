#!/usr/bin/env python3
"""
Start the complete AI Agent Company system (API + Dashboard)
"""
import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class SystemManager:
    def __init__(self):
        self.api_process = None
        self.dashboard_process = None
        self.running = True
    
    def start_api_server(self):
        """Start the API server"""
        try:
            from api.gateway import APIGateway
            
            print("🚀 Starting API Server...")
            gateway = APIGateway(host="localhost", port=8000)
            gateway.run(debug=False)
            
        except Exception as e:
            print(f"❌ API Server error: {e}")
    
    def start_dashboard(self):
        """Start the dashboard"""
        dashboard_dir = project_root / "dashboard"
        
        if not dashboard_dir.exists():
            print("❌ Dashboard directory not found")
            return
        
        try:
            print("🎨 Starting Dashboard...")
            
            # Set environment variables
            env = os.environ.copy()
            env["PORT"] = "3000"
            env["NEXT_PUBLIC_API_BASE_URL"] = "http://localhost:8000"
            
            # Check if dependencies are installed
            if not (dashboard_dir / "node_modules").exists():
                print("📦 Installing dashboard dependencies...")
                subprocess.run(["npm", "install"], cwd=dashboard_dir, check=True)
            
            # Start dashboard
            self.dashboard_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=dashboard_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            print("✅ Dashboard started on http://localhost:3000")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Dashboard error: {e}")
        except FileNotFoundError:
            print("❌ Node.js not found. Please install Node.js to run the dashboard.")
    
    def start_system(self):
        """Start the complete system"""
        print("🚀 Starting AI Agent Company Full System")
        print("=" * 50)
        print("📡 API Server: http://localhost:8000")
        print("🎨 Dashboard: http://localhost:3000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("🔑 Default credentials: admin/admin123")
        print("=" * 50)
        
        # Start API server in a separate thread
        api_thread = threading.Thread(target=self.start_api_server, daemon=True)
        api_thread.start()
        
        # Wait for API server to start
        print("⏳ Waiting for API server to start...")
        time.sleep(5)
        
        # Test API server
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API Server is running")
            else:
                print("⚠️ API Server may not be ready")
        except Exception:
            print("⚠️ Could not verify API server status")
        
        # Start dashboard
        self.start_dashboard()
        
        # Keep the main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the system"""
        print("\n👋 Shutting down AI Agent Company...")
        self.running = False
        
        if self.dashboard_process:
            self.dashboard_process.terminate()
            try:
                self.dashboard_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.dashboard_process.kill()
        
        print("✅ System shutdown complete")

def main():
    """Main entry point"""
    # Check environment
    if not os.path.exists(".env"):
        print("⚠️ Warning: .env file not found. Copy .env.example to .env and configure your API keys.")
    
    # Check dependencies
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("❌ API dependencies missing. Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Start system
    manager = SystemManager()
    
    # Handle signals
    def signal_handler(signum, frame):
        manager.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager.start_system()

if __name__ == "__main__":
    main()