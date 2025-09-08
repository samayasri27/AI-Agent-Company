#!/usr/bin/env python3
"""
Simple script to start the web dashboard
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    dashboard_dir = Path(__file__).parent / "dashboard"
    
    if not dashboard_dir.exists():
        print("❌ Dashboard directory not found")
        sys.exit(1)
    
    print("🎨 Starting AI Agent Company Web Dashboard")
    print("🌐 Dashboard will be available at: http://localhost:3000")
    print("=" * 50)
    
    try:
        # Check if Node.js is available
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        
        # Check if dependencies are installed
        if not (dashboard_dir / "node_modules").exists():
            print("📦 Installing dashboard dependencies...")
            subprocess.run(["npm", "install"], cwd=dashboard_dir, check=True)
        
        # Start dashboard
        print("🚀 Starting dashboard...")
        subprocess.run(["npm", "run", "dev"], cwd=dashboard_dir)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 18+ to run the dashboard.")
        print("   Visit: https://nodejs.org/")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")

if __name__ == "__main__":
    main()