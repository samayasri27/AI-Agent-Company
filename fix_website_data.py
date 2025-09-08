#!/usr/bin/env python3
"""
Website Data Fix Script
Fixes mock data issues and ensures real data is displayed in the dashboard
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import AIAgentCompany
from agents.website.website_agent import WebsiteAgent


async def fix_website_data():
    """Fix website data issues and replace mock data with real data"""
    print("🔧 Starting website data fix...")
    
    try:
        # Initialize company system
        print("📊 Initializing AI Agent Company system...")
        company = AIAgentCompany()
        
        # Initialize website agent
        print("🌐 Initializing Website Management Agent...")
        website_agent = WebsiteAgent()
        
        # Fix mock data issues
        print("🔄 Fixing mock data issues...")
        mock_fix_result = await website_agent.fix_mock_data_issues()
        if mock_fix_result['success']:
            print(f"✅ Mock data issues fixed: {', '.join(mock_fix_result['issues_fixed'])}")
        else:
            print(f"❌ Failed to fix mock data: {mock_fix_result.get('error', 'Unknown error')}")
        
        # Sync dashboard data
        print("📈 Synchronizing dashboard data...")
        sync_result = await website_agent.sync_dashboard_data()
        if sync_result['success']:
            print(f"✅ Dashboard data synchronized:")
            print(f"   - Agents: {sync_result['agents_count']}")
            print(f"   - Departments: {sync_result['departments_count']}")
            print(f"   - Tasks: {sync_result['tasks_count']}")
        else:
            print(f"❌ Failed to sync data: {sync_result.get('error', 'Unknown error')}")
        
        # Update agent data
        print("👥 Updating agent data...")
        agent_update_result = await website_agent.update_agent_data()
        if agent_update_result['success']:
            print(f"✅ Agent data updated:")
            print(f"   - Total agents: {agent_update_result['total_agents']}")
            print(f"   - Departments found: {agent_update_result['departments_found']}")
            print(f"   - Departments: {', '.join(agent_update_result['departments'])}")
        else:
            print(f"❌ Failed to update agents: {agent_update_result.get('error', 'Unknown error')}")
        
        # Fix memory display
        print("🧠 Fixing memory system display...")
        memory_fix_result = await website_agent.fix_memory_display()
        if memory_fix_result['success']:
            print(f"✅ Memory system display fixed:")
            print(f"   - Search functional: {memory_fix_result['search_functional']}")
            print(f"   - Cache hit rate: {memory_fix_result['memory_stats']['cache_hit_rate']}%")
        else:
            print(f"❌ Failed to fix memory display: {memory_fix_result.get('error', 'Unknown error')}")
        
        # Monitor performance
        print("📊 Monitoring website performance...")
        perf_result = await website_agent.monitor_website_performance()
        if perf_result['success']:
            print(f"✅ Performance monitoring completed:")
            print(f"   - API response time: {perf_result['metrics']['api_response_time']}ms")
            print(f"   - Dashboard load time: {perf_result['metrics']['dashboard_load_time']}s")
            print(f"   - Issues found: {perf_result['issues_found']}")
            if perf_result['issues']:
                for issue in perf_result['issues']:
                    print(f"     ⚠️ {issue}")
        else:
            print(f"❌ Failed to monitor performance: {perf_result.get('error', 'Unknown error')}")
        
        # Get status report
        print("\n📋 Website Agent Status Report:")
        status_report = website_agent.get_status_report()
        print(f"   - Agent status: {status_report['agent_status']}")
        print(f"   - Last sync: {status_report['last_sync']}")
        print(f"   - Cached data types: {', '.join(status_report['cached_data_types'])}")
        print(f"   - Recent errors: {status_report['recent_errors']}")
        print(f"   - Uptime: {status_report['uptime']}")
        
        # Show error log if any
        error_log = website_agent.get_error_log()
        if error_log:
            print(f"\n⚠️ Recent errors ({len(error_log)}):")
            for error in error_log[-3:]:  # Show last 3 errors
                print(f"   - {error['timestamp']}: {error['error']}")
        
        print(f"\n✅ Website data fix completed successfully at {datetime.now().isoformat()}")
        return True
        
    except Exception as e:
        print(f"❌ Website data fix failed: {str(e)}")
        return False


def verify_real_data():
    """Verify that real data is being used instead of mock data"""
    print("\n🔍 Verifying real data usage...")
    
    try:
        # Initialize company to get real data
        company = AIAgentCompany()
        
        # Check agents
        agents = company.get_agents_info()
        print(f"✅ Found {len(agents)} real agents")
        
        # Check departments
        departments = company.get_departments()
        print(f"✅ Found {len(departments)} departments")
        
        # List all departments
        dept_names = [dept['name'] for dept in departments]
        print(f"   Departments: {', '.join(dept_names)}")
        
        # Check for website department
        if 'Website' in dept_names:
            print("✅ Website department found")
        else:
            print("⚠️ Website department not found - will be added by API")
        
        # Check for mock data patterns
        mock_patterns_found = []
        for agent in agents:
            if any(pattern in agent['name'].lower() for pattern in ['mock', 'sample', 'test', 'demo']):
                mock_patterns_found.append(agent['name'])
        
        if mock_patterns_found:
            print(f"⚠️ Found potential mock data: {', '.join(mock_patterns_found)}")
        else:
            print("✅ No mock data patterns detected in agents")
        
        return True
        
    except Exception as e:
        print(f"❌ Data verification failed: {str(e)}")
        return False


async def main():
    """Main function"""
    print("🚀 AI Agent Company - Website Data Fix Tool")
    print("=" * 50)
    
    # Fix website data
    fix_success = await fix_website_data()
    
    # Verify real data
    verify_success = verify_real_data()
    
    if fix_success and verify_success:
        print("\n🎉 All fixes completed successfully!")
        print("\n📝 Next steps:")
        print("1. Restart the API server: python start_api_server.py")
        print("2. Restart the dashboard: cd dashboard && npm run dev")
        print("3. Check the dashboard for real data display")
        return 0
    else:
        print("\n❌ Some fixes failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)