#!/usr/bin/env python3
"""
Auto Startup Script for AI Agent Company
Automatically starts all services and handles error correction
"""

import os
import sys
import time
import subprocess
import signal
import json
from pathlib import Path
from datetime import datetime

class AutoStartupManager:
    """Manages automatic startup and error correction for the AI Agent Company system"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        self.startup_time = datetime.now()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        self.shutdown_all_services()
        sys.exit(0)
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_dependencies(self):
        """Check and install required dependencies"""
        self.log("🔍 Checking dependencies...")
        
        # Check Python packages
        required_packages = [
            'fastapi', 'uvicorn', 'pydantic', 'python-jose', 'passlib',
            'requests', 'python-dotenv', 'psycopg2-binary', 'supabase'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.log(f"📦 Installing missing packages: {', '.join(missing_packages)}")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '--upgrade'
                ] + missing_packages)
                self.log("✅ Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Failed to install dependencies: {e}", "ERROR")
                return False
        else:
            self.log("✅ All dependencies are satisfied")
        
        return True
    
    def setup_environment(self):
        """Setup environment variables and configuration"""
        self.log("🔧 Setting up environment...")
        
        # Create .env file if it doesn't exist
        env_file = Path('.env')
        if not env_file.exists():
            self.log("📝 Creating .env file with default configuration")
            env_content = """# AI Agent Company Configuration
# API Configuration
API_BASE_URL=http://localhost:8000
DEBUG_MODE=true

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database Configuration (Optional)
# DATABASE_URL=postgresql://user:password@localhost/ai_agent_company

# External API Keys (Configure as needed)
# GROQ_API_KEY_1=your-groq-api-key-here
# GROQ_API_KEY_2=your-backup-groq-api-key-here
# SUPABASE_URL=your-supabase-url-here
# SUPABASE_ANON_KEY=your-supabase-anon-key-here
# GITHUB_TOKEN=your-github-token-here
# STRIPE_API_KEY=your-stripe-api-key-here
# HUBSPOT_API_KEY=your-hubspot-api-key-here
# GOOGLE_SEARCH_API_KEY=your-google-search-api-key-here
"""
            env_file.write_text(env_content)
        
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
            self.log("✅ Environment configuration loaded")
        except Exception as e:
            self.log(f"⚠️ Failed to load environment: {e}", "WARNING")
        
        return True
    
    def check_and_fix_imports(self):
        """Check and fix common import issues"""
        self.log("🔍 Checking and fixing import issues...")
        
        # Check if main.py can be imported
        try:
            import main
            self.log("✅ Main module imports successfully")
            return True
        except ImportError as e:
            self.log(f"❌ Import error in main module: {e}", "ERROR")
            
            # Try to fix common import issues
            self.fix_common_import_issues()
            
            # Try again
            try:
                import main
                self.log("✅ Import issues fixed successfully")
                return True
            except ImportError as e:
                self.log(f"❌ Could not fix import issues: {e}", "ERROR")
                return False
    
    def fix_common_import_issues(self):
        """Fix common import issues automatically"""
        self.log("🔧 Attempting to fix import issues...")
        
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Create __init__.py files in directories that need them
        directories_needing_init = [
            'agents', 'agents/sales', 'agents/rnd', 'agents/product', 
            'agents/support', 'agents/memory', 'api', 'config', 'utils'
        ]
        
        for directory in directories_needing_init:
            init_file = Path(directory) / '__init__.py'
            if Path(directory).exists() and not init_file.exists():
                init_file.touch()
                self.log(f"📝 Created {init_file}")
    
    def start_api_server(self):
        """Start the API server"""
        self.log("🚀 Starting API server...")
        
        try:
            # Use the existing run_server.py if it exists, otherwise start directly
            if Path('run_server.py').exists():
                process = subprocess.Popen([
                    sys.executable, 'run_server.py'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                # Start API server directly
                process = subprocess.Popen([
                    sys.executable, '-c', 
                    """
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.gateway import APIGateway
gateway = APIGateway(host='localhost', port=8000)
gateway.run(debug=True)
"""
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['api_server'] = process
            
            # Wait a moment and check if it started successfully
            time.sleep(3)
            if process.poll() is None:
                self.log("✅ API server started successfully on http://localhost:8000")
                return True
            else:
                stdout, stderr = process.communicate()
                self.log(f"❌ API server failed to start: {stderr.decode()}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to start API server: {e}", "ERROR")
            return False
    
    def start_dashboard(self):
        """Start the Next.js dashboard"""
        self.log("🎨 Starting dashboard...")
        
        dashboard_dir = Path('dashboard')
        if not dashboard_dir.exists():
            self.log("❌ Dashboard directory not found", "ERROR")
            return False
        
        try:
            # Check if node_modules exists, if not run npm install
            if not (dashboard_dir / 'node_modules').exists():
                self.log("📦 Installing dashboard dependencies...")
                install_process = subprocess.run([
                    'npm', 'install'
                ], cwd=dashboard_dir, capture_output=True, text=True)
                
                if install_process.returncode != 0:
                    self.log(f"❌ Failed to install dashboard dependencies: {install_process.stderr}", "ERROR")
                    return False
            
            # Start the dashboard
            process = subprocess.Popen([
                'npm', 'run', 'dev'
            ], cwd=dashboard_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['dashboard'] = process
            
            # Wait a moment and check if it started successfully
            time.sleep(5)
            if process.poll() is None:
                self.log("✅ Dashboard started successfully on http://localhost:3000")
                return True
            else:
                stdout, stderr = process.communicate()
                self.log(f"❌ Dashboard failed to start: {stderr.decode()}", "ERROR")
                return False
                
        except FileNotFoundError:
            self.log("❌ Node.js/npm not found. Please install Node.js to run the dashboard", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Failed to start dashboard: {e}", "ERROR")
            return False
    
    def monitor_services(self):
        """Monitor running services and restart if needed"""
        self.log("👁️ Starting service monitoring...")
        
        while self.running:
            try:
                # Check API server
                if 'api_server' in self.processes:
                    process = self.processes['api_server']
                    if process.poll() is not None:
                        self.log("⚠️ API server stopped, restarting...", "WARNING")
                        self.start_api_server()
                
                # Check dashboard
                if 'dashboard' in self.processes:
                    process = self.processes['dashboard']
                    if process.poll() is not None:
                        self.log("⚠️ Dashboard stopped, restarting...", "WARNING")
                        self.start_dashboard()
                
                # Wait before next check
                time.sleep(10)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"❌ Error in service monitoring: {e}", "ERROR")
                time.sleep(5)
    
    def shutdown_all_services(self):
        """Shutdown all running services"""
        self.log("🛑 Shutting down all services...")
        
        for service_name, process in self.processes.items():
            try:
                self.log(f"🛑 Stopping {service_name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.log(f"⚠️ Force killing {service_name}...")
                    process.kill()
                    process.wait()
                
                self.log(f"✅ {service_name} stopped")
            except Exception as e:
                self.log(f"❌ Error stopping {service_name}: {e}", "ERROR")
        
        self.processes.clear()
    
    def run(self):
        """Main startup sequence"""
        self.log("🚀 Starting AI Agent Company Auto Startup Manager")
        self.log("=" * 60)
        
        # Step 1: Check dependencies
        if not self.check_dependencies():
            self.log("❌ Dependency check failed", "ERROR")
            return False
        
        # Step 2: Setup environment
        if not self.setup_environment():
            self.log("❌ Environment setup failed", "ERROR")
            return False
        
        # Step 3: Fix import issues
        if not self.check_and_fix_imports():
            self.log("❌ Import fixes failed", "ERROR")
            return False
        
        # Step 4: Start API server
        if not self.start_api_server():
            self.log("❌ API server startup failed", "ERROR")
            return False
        
        # Step 5: Start dashboard
        dashboard_started = self.start_dashboard()
        if not dashboard_started:
            self.log("⚠️ Dashboard startup failed, continuing with API only", "WARNING")
        
        # Step 6: Show startup summary
        uptime = datetime.now() - self.startup_time
        self.log("=" * 60)
        self.log("🎉 AI Agent Company System Started Successfully!")
        self.log(f"⏱️ Startup time: {uptime.total_seconds():.2f} seconds")
        self.log("🌐 API Server: http://localhost:8000")
        if dashboard_started:
            self.log("🎨 Dashboard: http://localhost:3000")
        self.log("📚 API Documentation: http://localhost:8000/docs")
        self.log("=" * 60)
        self.log("Press Ctrl+C to stop all services")
        
        # Step 7: Monitor services
        try:
            self.monitor_services()
        except KeyboardInterrupt:
            pass
        
        return True

def main():
    """Main entry point"""
    manager = AutoStartupManager()
    
    try:
        success = manager.run()
        if not success:
            print("❌ Startup failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        manager.shutdown_all_services()

if __name__ == "__main__":
    main()