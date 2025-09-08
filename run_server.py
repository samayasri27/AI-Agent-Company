#!/usr/bin/env python3
"""
AI Agent Company Server Runner
Supports both terminal mode and web API mode
"""
import os
import sys
import argparse
import asyncio
import subprocess
from typing import Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import AIAgentCompany
from api.gateway import APIGateway


def run_terminal_mode():
    """Run the AI Agent Company in terminal mode"""
    print("🚀 Starting AI Agent Company in Terminal Mode")
    print("=" * 50)
    
    try:
        company = AIAgentCompany()
        company.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down AI Agent Company...")
    except Exception as e:
        print(f"❌ Error running company: {e}")
        sys.exit(1)


def run_api_mode(host: str = "localhost", port: int = 8000, debug: bool = False):
    """Run the AI Agent Company in API mode"""
    print(f"🌐 Starting AI Agent Company API Server")
    print(f"📡 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print("=" * 50)
    
    try:
        gateway = APIGateway(host=host, port=port)
        gateway.run(debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Shutting down API server...")
    except Exception as e:
        print(f"❌ Error running API server: {e}")
        sys.exit(1)


def run_dashboard(dashboard_port: int = 3000):
    """Run the web dashboard"""
    dashboard_dir = project_root / "dashboard"
    
    if not dashboard_dir.exists():
        print("❌ Dashboard directory not found")
        return False
    
    print(f"🎨 Starting Web Dashboard")
    print(f"🌐 Dashboard: http://localhost:{dashboard_port}")
    print("=" * 50)
    
    try:
        # Check if Node.js is available
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        
        # Install dependencies if needed
        if not (dashboard_dir / "node_modules").exists():
            print("📦 Installing dashboard dependencies...")
            subprocess.run(["npm", "install"], cwd=dashboard_dir, check=True)
        
        # Set environment variables
        env = os.environ.copy()
        env["PORT"] = str(dashboard_port)
        env["NEXT_PUBLIC_API_BASE_URL"] = f"http://localhost:8000"
        
        # Run dashboard
        subprocess.run(["npm", "run", "dev"], cwd=dashboard_dir, env=env)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running dashboard: {e}")
        return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js to run the dashboard.")
        return False
    except KeyboardInterrupt:
        print("\n👋 Shutting down dashboard...")
        return True


def run_full_stack(api_host: str = "localhost", api_port: int = 8000, dashboard_port: int = 3000):
    """Run both API server and dashboard"""
    import threading
    import time
    
    print("🚀 Starting Full Stack AI Agent Company")
    print(f"📡 API Server: http://{api_host}:{api_port}")
    print(f"🎨 Dashboard: http://localhost:{dashboard_port}")
    print("=" * 50)
    
    # Start API server in a separate thread
    def run_api():
        gateway = APIGateway(host=api_host, port=api_port)
        gateway.run(debug=False)
    
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Wait a moment for API server to start
    time.sleep(3)
    
    # Start dashboard
    try:
        run_dashboard(dashboard_port)
    except KeyboardInterrupt:
        print("\n👋 Shutting down full stack...")


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        print("✅ API dependencies available")
    except ImportError:
        print("❌ API dependencies missing. Install with: pip install fastapi uvicorn")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="AI Agent Company Server Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_server.py                          # Terminal mode
  python run_server.py --mode api               # API server only
  python run_server.py --mode dashboard         # Dashboard only
  python run_server.py --mode full              # API + Dashboard
  python run_server.py --mode api --port 9000   # Custom port
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["terminal", "api", "dashboard", "full"],
        default="terminal",
        help="Run mode (default: terminal)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="API server host (default: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    
    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=3000,
        help="Dashboard port (default: 3000)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Check environment
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found. Copy .env.example to .env and configure your API keys.")
    
    # Run based on mode
    if args.mode == "terminal":
        run_terminal_mode()
    
    elif args.mode == "api":
        if not check_dependencies():
            sys.exit(1)
        run_api_mode(args.host, args.port, args.debug)
    
    elif args.mode == "dashboard":
        run_dashboard(args.dashboard_port)
    
    elif args.mode == "full":
        if not check_dependencies():
            sys.exit(1)
        run_full_stack(args.host, args.port, args.dashboard_port)


if __name__ == "__main__":
    main()