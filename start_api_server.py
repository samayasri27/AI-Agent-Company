#!/usr/bin/env python3
"""
Simple script to start the API server for the AI Agent Company
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Start the API server"""
    try:
        # Import and start the API gateway
        from api.gateway import APIGateway
        
        print("🚀 Starting AI Agent Company API Server...")
        print("📡 Server will be available at: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔑 Default credentials: admin/admin123")
        print("=" * 50)
        
        # Create and run the gateway
        gateway = APIGateway(host="localhost", port=8000)
        gateway.run(debug=False)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down API server...")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check if port 8000 is available")
        print("3. Verify .env file exists with proper configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()