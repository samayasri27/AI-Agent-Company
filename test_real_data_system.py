#!/usr/bin/env python3
"""
Test Script for Real Data System
Verifies that all components are working with real data
"""

import asyncio
import sys
import os
import requests
import time
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def log(message: str, level: str = "INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_imports():
    """Test that all required modules can be imported"""
    log("🔍 Testing imports...")
    
    try:
        from main import AIAgentCompany
        log("✅ Main system imports successfully")
        
        from api.gateway import APIGateway
        log("✅ API Gateway imports successfully")
        
        from config.company_profile import company_profile
        log("✅ Company profile imports successfully")
        
        return True
    except ImportError as e:
        log(f"❌ Import error: {e}", "ERROR")
        return False

def test_company_system():
    """Test the main company system"""
    log("🏢 Testing company system...")
    
    try:
        from main import AIAgentCompany
        
        # Initialize company
        company = AIAgentCompany()
        
        # Test company info
        company_info = company.get_company_info()
        log(f"✅ Company info retrieved: {company_info['company_name']}")
        
        # Test agents info
        agents_info = company.get_agents_info()
        log(f"✅ Agents info retrieved: {len(agents_info)} agents")
        
        # Test departments info
        departments_info = company.get_departments()
        log(f"✅ Departments info retrieved: {len(departments_info)} departments")
        
        return True
    except Exception as e:
        log(f"❌ Company system error: {e}", "ERROR")
        return False

async def test_task_submission():
    """Test task submission and processing"""
    log("📋 Testing task submission...")
    
    try:
        from main import AIAgentCompany
        
        company = AIAgentCompany()
        
        # Submit a test task
        task_id = await company.submit_task(
            task_description="Test task for system verification",
            task_type="general",
            priority="medium"
        )
        
        log(f"✅ Task submitted successfully: {task_id}")
        
        # Wait a moment for processing
        await asyncio.sleep(2)
        
        # Check task status
        if task_id in company.active_tasks:
            task_status = company.active_tasks[task_id]
            log(f"✅ Task status: {task_status['status']}")
        
        return True
    except Exception as e:
        log(f"❌ Task submission error: {e}", "ERROR")
        return False

def test_api_server():
    """Test API server functionality"""
    log("🌐 Testing API server...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            log("✅ API server health check passed")
            return True
        else:
            log(f"❌ API server health check failed: {response.status_code}", "ERROR")
            return False
    except requests.exceptions.ConnectionError:
        log("⚠️ API server not running (this is expected if not started)", "WARNING")
        return False
    except Exception as e:
        log(f"❌ API server test error: {e}", "ERROR")
        return False

def test_configuration():
    """Test configuration system"""
    log("⚙️ Testing configuration...")
    
    try:
        from config.company_profile import company_profile
        
        # Test profile loading
        profile_dict = company_profile.to_dict()
        log(f"✅ Company profile loaded: {profile_dict['is_configured']}")
        
        # Test context generation
        context = company_profile.get_context()
        log("✅ Company context generated successfully")
        
        return True
    except Exception as e:
        log(f"❌ Configuration test error: {e}", "ERROR")
        return False

async def run_all_tests():
    """Run all tests"""
    log("🚀 Starting Real Data System Tests")
    log("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_configuration),
        ("Company System Tests", test_company_system),
        ("Task Submission Tests", test_task_submission),
        ("API Server Tests", test_api_server)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        log(f"\n📋 Running {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            log(f"❌ {test_name} failed with exception: {e}", "ERROR")
            results[test_name] = False
    
    # Summary
    log("\n" + "=" * 50)
    log("📊 Test Results Summary")
    log("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log(f"{status} - {test_name}")
        if result:
            passed += 1
    
    log("=" * 50)
    log(f"📈 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        log("🎉 All tests passed! Real data system is working correctly.")
        return True
    else:
        log("⚠️ Some tests failed. Check the logs above for details.")
        return False

def main():
    """Main test function"""
    try:
        success = asyncio.run(run_all_tests())
        
        if success:
            log("\n🎯 Next Steps:")
            log("1. Run 'python auto_startup.py' to start the full system")
            log("2. Open http://localhost:3000 to access the dashboard")
            log("3. Complete company setup and start submitting tasks")
            sys.exit(0)
        else:
            log("\n🔧 Troubleshooting:")
            log("1. Check that all dependencies are installed: pip install -r requirements.txt")
            log("2. Verify that all files are in the correct locations")
            log("3. Run 'python auto_startup.py' to automatically fix common issues")
            sys.exit(1)
            
    except KeyboardInterrupt:
        log("\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        log(f"\n❌ Unexpected error during testing: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()