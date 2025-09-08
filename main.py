# main.py

import asyncio
import sys
import os
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check for required dependencies
try:
    import requests
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("Please install dependencies:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

# Import system components
try:
    from config.company_profile import company_profile
    
    # Import memory system utilities
    from utils.memory_system_init import initialize_memory_system, check_memory_system_health

    # Import available agents
    from agents.sales.sales_agent import SalesAgent
    from agents.rnd.rnd_agent import RnDAgent
    from agents.product.product_agent import ProductAgent
    from agents.support.support_agent import SupportAgent
    from agents.marketing.marketing_agent import MarketingAgent
    from agents.finance.finance_agent import FinanceAgent
    from agents.security.security_agent import SecurityAgent
    
    # Import file and session management
    from utils.file_manager import FileManager
    from utils.session_manager import SessionManager
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all files are in the correct location")
    sys.exit(1)


class AIAgentCompany:
    """Main AI Agent Company system"""
    
    def __init__(self, mode: str = "persistent", project_name: str = None):
        self.company_profile = company_profile
        self.agents = {}
        self.active_tasks = {}
        self.task_counter = 0
        self.memory_manager = None
        self.startup_time = datetime.now()
        
        # Mode and session management
        self.mode = mode
        self.project_name = project_name
        self.session_manager = SessionManager(mode)
        self.file_manager = None
        self.current_session_id = None
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the company system"""
        try:
            # Initialize memory system (only for persistent mode)
            if self.mode == "persistent":
                self.memory_manager = initialize_memory_system(fallback_mode=True)
            
            # Initialize session and file management
            self._initialize_session()
            
            # Initialize agents
            self._initialize_agents()
            
            print(f"✅ AI Agent Company system initialized successfully in {self.mode} mode")
            if self.mode == "oneshot":
                print(f"📁 Project: {self.project_name}")
                print(f"📂 Output folder: {self.file_manager.session_path}")
            
        except Exception as e:
            print(f"❌ Failed to initialize system: {e}")
    
    def _initialize_session(self):
        """Initialize session and file management"""
        try:
            # Create new session
            self.current_session_id = self.session_manager.create_session(self.project_name)
            
            # Get file manager from session manager
            self.file_manager = self.session_manager.get_file_manager()
            
            print(f"📋 Session created: {self.current_session_id}")
            
        except Exception as e:
            print(f"❌ Failed to initialize session: {e}")
            raise
    
    def _initialize_agents(self):
        """Initialize all company agents by discovering them dynamically"""
        try:
            # Dynamically discover and initialize agents from the agents directory
            self._discover_and_initialize_agents()
            
            print(f"✅ Initialized {len(self.agents)} agents across {len(self.get_departments())} departments")
            
        except Exception as e:
            print(f"❌ Failed to initialize agents: {e}")
    
    def _discover_and_initialize_agents(self):
        """Discover and initialize agents from the agents directory"""
        import importlib
        import inspect
        from pathlib import Path
        
        agents_dir = Path("agents")
        
        # Define agent configurations for each department
        agent_configs = {
            'sales': {
                'module': 'agents.sales.sales_agent',
                'class': 'SalesAgent',
                'department': 'Sales',
                'role': 'Lead Generation Specialist'
            },
            'rnd': {
                'module': 'agents.rnd.rnd_agent', 
                'class': 'RnDAgent',
                'department': 'R&D',
                'role': 'Research & Innovation Lead'
            },
            'product': {
                'module': 'agents.product.product_agent',
                'class': 'ProductAgent', 
                'department': 'Product',
                'role': 'Product Strategy Lead'
            },
            'support': {
                'module': 'agents.support.support_agent',
                'class': 'SupportAgent',
                'department': 'Support', 
                'role': 'Customer Support Lead'
            },
            'marketing': {
                'module': 'agents.marketing.marketing_agent',
                'class': 'MarketingAgent',
                'department': 'Marketing',
                'role': 'Campaign & Content Strategy'
            },
            'finance': {
                'module': 'agents.finance.finance_agent',
                'class': 'FinanceAgent',
                'department': 'Finance',
                'role': 'Financial Analysis & Budget Management'
            },
            'security': {
                'module': 'agents.security.security_agent',
                'class': 'SecurityAgent',
                'department': 'Security',
                'role': 'Security & Authentication Manager'
            }
        }
        
        # Add memory system agents
        memory_agents = {
            'memory_manager': {
                'module': 'agents.memory.memory_manager_agent',
                'class': 'MemoryManagerAgent',
                'department': 'Memory',
                'role': 'Memory System Manager'
            },
            'knowledge_agent': {
                'module': 'agents.memory.knowledge_agent',
                'class': 'KnowledgeAgent', 
                'department': 'Memory',
                'role': 'Knowledge Management Specialist'
            },
            'learning_agent': {
                'module': 'agents.memory.learning_agent',
                'class': 'LearningAgent',
                'department': 'Memory', 
                'role': 'Learning & Adaptation Specialist'
            },
            'history_agent': {
                'module': 'agents.memory.history_agent',
                'class': 'HistoryAgent',
                'department': 'Memory',
                'role': 'Historical Data Manager'
            }
        }
        
        # Add website management agent
        website_agents = {
            'website_manager': {
                'module': 'agents.website.website_agent',
                'class': 'WebsiteAgent',
                'department': 'Website',
                'role': 'Website Data Manager'
            }
        }
        
        # Combine all agent configs
        all_agent_configs = {**agent_configs, **memory_agents, **website_agents}
        
        # Initialize each agent
        for agent_id, config in all_agent_configs.items():
            try:
                # Import the module
                module = importlib.import_module(config['module'])
                agent_class = getattr(module, config['class'])
                
                # Initialize the agent
                agent_instance = agent_class()
                
                # Configure agent for current mode
                agent_instance.set_mode(self.mode)
                agent_instance.set_file_manager(self.file_manager)
                agent_instance.set_session_manager(self.session_manager)
                
                # Store agent info
                self.agents[agent_id] = {
                    'agent': agent_instance,
                    'department': config['department'],
                    'status': 'active',
                    'current_task': None,
                    'role': config['role']
                }
                
            except Exception as e:
                print(f"⚠️ Failed to initialize {agent_id}: {e}")
                # Create a placeholder for failed agents
                self.agents[agent_id] = {
                    'agent': None,
                    'department': config['department'], 
                    'status': 'error',
                    'current_task': None,
                    'role': config['role'],
                    'error': str(e)
                }
    
    def get_departments(self) -> List[Dict[str, Any]]:
        """Get all departments with their agents and statistics"""
        departments = {}
        
        for agent_id, agent_info in self.agents.items():
            dept_name = agent_info['department']
            
            if dept_name not in departments:
                departments[dept_name] = {
                    'name': dept_name,
                    'agents': [],
                    'active_agents': 0,
                    'total_agents': 0,
                    'active_tasks': 0,
                    'completed_tasks': 0,
                    'success_rate': 100.0,
                    'capabilities': set()
                }
            
            dept = departments[dept_name]
            dept['total_agents'] += 1
            
            if agent_info['status'] == 'active':
                dept['active_agents'] += 1
            
            if agent_info.get('current_task'):
                dept['active_tasks'] += 1
            
            # Add agent to department
            agent_data = {
                'id': agent_id,
                'name': agent_info['agent'].name if agent_info['agent'] else agent_id.replace('_', ' ').title(),
                'role': agent_info.get('role', 'Agent'),
                'status': agent_info['status'],
                'current_task': agent_info.get('current_task')
            }
            
            # Get capabilities if agent exists
            if agent_info['agent'] and hasattr(agent_info['agent'], 'capabilities'):
                capabilities = agent_info['agent'].capabilities
                agent_data['capabilities'] = capabilities
                dept['capabilities'].update(capabilities)
            else:
                agent_data['capabilities'] = []
            
            dept['agents'].append(agent_data)
        
        # Convert capabilities set to list and calculate stats
        for dept in departments.values():
            dept['capabilities'] = list(dept['capabilities'])
            
            # Calculate completed tasks from active_tasks history
            dept['completed_tasks'] = len([t for t in self.active_tasks.values() 
                                         if t.get('department') == dept['name'] and t.get('status') == 'completed'])
            
            # Calculate success rate
            total_dept_tasks = len([t for t in self.active_tasks.values() if t.get('department') == dept['name']])
            if total_dept_tasks > 0:
                failed_tasks = len([t for t in self.active_tasks.values() 
                                  if t.get('department') == dept['name'] and t.get('status') == 'failed'])
                dept['success_rate'] = ((total_dept_tasks - failed_tasks) / total_dept_tasks) * 100
        
        return list(departments.values())
    
    def get_company_info(self) -> Dict[str, Any]:
        """Get comprehensive company information"""
        try:
            # Calculate department statistics
            departments = {}
            for agent_id, agent_info in self.agents.items():
                dept = agent_info['department']
                if dept not in departments:
                    departments[dept] = {
                        'name': dept,
                        'agent_count': 0,
                        'active_agents': 0,
                        'current_tasks': []
                    }
                
                departments[dept]['agent_count'] += 1
                if agent_info['status'] == 'active':
                    departments[dept]['active_agents'] += 1
                
                if agent_info.get('current_task'):
                    agent_name = agent_info['agent'].name if agent_info['agent'] else agent_id.replace('_', ' ').title()
                    departments[dept]['current_tasks'].append({
                        'agent': agent_name,
                        'task': agent_info['current_task']
                    })
            
            # Get task statistics
            task_stats = {
                'total_tasks': len(self.active_tasks),
                'completed_tasks': len([t for t in self.active_tasks.values() if t.get('status') == 'completed']),
                'in_progress_tasks': len([t for t in self.active_tasks.values() if t.get('status') == 'in_progress']),
                'queued_tasks': len([t for t in self.active_tasks.values() if t.get('status') == 'queued']),
                'failed_tasks': len([t for t in self.active_tasks.values() if t.get('status') == 'failed'])
            }
            
            # Calculate success rate
            total_completed_and_failed = task_stats['completed_tasks'] + task_stats['failed_tasks']
            success_rate = (task_stats['completed_tasks'] / total_completed_and_failed * 100) if total_completed_and_failed > 0 else 100
            
            return {
                'company_name': self.company_profile.company_name or 'AI Agent Company',
                'description': self.company_profile.description or 'Autonomous AI-powered business operations platform',
                'status': 'operational',
                'uptime': self._calculate_uptime(),
                'departments': list(departments.values()),
                'total_agents': len(self.agents),
                'active_agents': len([a for a in self.agents.values() if a['status'] == 'active']),
                'task_statistics': task_stats,
                'success_rate': round(success_rate, 1),
                'performance_metrics': {
                    'avg_response_time': '2.3s',
                    'system_load': '45%',
                    'memory_usage': '67%',
                    'api_calls_today': len(self.active_tasks)
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'company_name': 'AI Agent Company',
                'description': 'Autonomous AI-powered business operations platform',
                'status': 'error',
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_agents_info(self) -> List[Dict[str, Any]]:
        """Get information about all agents"""
        agents_info = []
        
        for agent_id, agent_info in self.agents.items():
            agent = agent_info['agent']
            
            # Handle cases where agent initialization failed
            if agent is None:
                agents_info.append({
                    'name': agent_id.replace('_', ' ').title(),
                    'role': agent_info.get('role', 'Agent'),
                    'department': agent_info['department'],
                    'status': agent_info['status'],
                    'capabilities': [],
                    'current_task': agent_info.get('current_task'),
                    'error': agent_info.get('error')
                })
            else:
                agents_info.append({
                    'name': agent.name,
                    'role': agent.role,
                    'department': agent.department,
                    'status': agent_info['status'],
                    'capabilities': getattr(agent, 'capabilities', []),
                    'current_task': agent_info.get('current_task')
                })
        
        return agents_info
    
    def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent tasks"""
        tasks = list(self.active_tasks.values())
        tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return tasks[:limit]
    
    def _calculate_uptime(self) -> str:
        """Calculate system uptime"""
        uptime_seconds = (datetime.now() - self.startup_time).total_seconds()
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    async def submit_task(self, task_description: str, task_type: str = "general", 
                         department: str = None, priority: str = "medium") -> str:
        """Submit a new task to the company"""
        try:
            # Generate task ID
            self.task_counter += 1
            task_id = f"TASK-{self.task_counter:06d}"
            
            # Create task record
            task_record = {
                'id': task_id,
                'description': task_description,
                'type': task_type,
                'priority': priority,
                'department': department,
                'status': 'queued',
                'progress': 0.0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Store task
            self.active_tasks[task_id] = task_record
            
            # Assign to appropriate agent
            await self._assign_task_to_agent(task_id, task_record)
            
            return task_id
            
        except Exception as e:
            raise Exception(f"Failed to submit task: {str(e)}")
    
    async def _assign_task_to_agent(self, task_id: str, task_record: Dict[str, Any]):
        """Assign task to appropriate agent"""
        try:
            # Simple task routing based on department or task type
            department = (task_record.get('department') or '').lower()
            task_type = (task_record.get('type') or '').lower()
            
            # Determine which agent should handle the task
            target_agent = None
            
            if department == 'sales' or 'sales' in task_type or 'lead' in task_type:
                target_agent = 'sales'
            elif department == 'rnd' or department == 'r&d' or 'research' in task_type:
                target_agent = 'rnd'
            elif department == 'product' or 'product' in task_type:
                target_agent = 'product'
            elif department == 'support' or 'support' in task_type:
                target_agent = 'support'
            else:
                # Default to sales for general tasks
                target_agent = 'sales'
            
            if target_agent and target_agent in self.agents:
                # Update task status
                task_record['status'] = 'in_progress'
                task_record['assigned_agent'] = target_agent
                task_record['updated_at'] = datetime.now().isoformat()
                
                # Update agent status
                self.agents[target_agent]['current_task'] = task_record['description']
                
                # Simulate task execution
                await asyncio.sleep(1)  # Simulate processing time
                
                # Complete task
                task_record['status'] = 'completed'
                task_record['progress'] = 1.0
                task_record['result'] = f"Task completed by {self.agents[target_agent]['agent'].name}"
                task_record['updated_at'] = datetime.now().isoformat()
                
                # Clear agent task
                self.agents[target_agent]['current_task'] = None
                
        except Exception as e:
            task_record['status'] = 'failed'
            task_record['error'] = str(e)
            task_record['updated_at'] = datetime.now().isoformat()
    
    def run(self):
        """Run the company in interactive mode"""
        asyncio.run(self._run_interactive())
    
    async def _run_interactive(self):
        """Interactive mode implementation"""
        # Set up company profile if not already set
        if not self.company_profile.company_name:
            get_company_details()
        
        print(f"\n🏢 Welcome to {self.company_profile.company_name}!")
        print("=" * 50)
        print("Available commands:")
        print("  - Enter any business task")
        print("  - 'status' - Get company status")
        print("  - 'agents' - List all agents")
        print("  - 'tasks' - List recent tasks")
        print("  - 'exit' - Quit")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n💼 Enter command or task: ").strip()
                
                if user_input.lower() == 'exit':
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'status':
                    info = self.get_company_info()
                    print(f"\n📊 Company Status:")
                    print(f"   Name: {info['company_name']}")
                    print(f"   Status: {info['status']}")
                    print(f"   Uptime: {info['uptime']}")
                    print(f"   Active Agents: {info['active_agents']}/{info['total_agents']}")
                    print(f"   Success Rate: {info['success_rate']}%")
                elif user_input.lower() == 'agents':
                    agents = self.get_agents_info()
                    print(f"\n🤖 Active Agents ({len(agents)}):")
                    for agent in agents:
                        status_icon = "🟢" if agent['status'] == 'active' else "🔴"
                        task_info = f" - {agent['current_task'][:50]}..." if agent['current_task'] else ""
                        print(f"   {status_icon} {agent['name']} ({agent['department']}){task_info}")
                elif user_input.lower() == 'tasks':
                    tasks = self.get_recent_tasks(5)
                    print(f"\n📋 Recent Tasks ({len(tasks)}):")
                    for task in tasks:
                        status_icon = {"completed": "✅", "in_progress": "🔄", "queued": "⏳", "failed": "❌"}.get(task['status'], "❓")
                        print(f"   {status_icon} {task['id']}: {task['description'][:50]}...")
                elif user_input:
                    print(f"\n🎯 Processing task: {user_input}")
                    task_id = await self.submit_task(user_input)
                    print(f"✅ Task {task_id} submitted and processed")
                else:
                    print("Please enter a valid command or task.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def get_company_details():
    """Prompt user for company details"""
    print("🏢 Welcome to AI Agent Company Setup!")
    print("=" * 50)
    
    company_name = input("Enter company name: ").strip()
    description = input("Enter company description: ").strip()
    
    while True:
        try:
            budget = float(input("Enter company budget (in numbers): ").strip())
            break
        except ValueError:
            print("Please enter a valid number for budget.")
    
    sector = input("Enter company sector/industry: ").strip()
    goal = input("Enter company goal/objective: ").strip()
    
    target_location = input("Enter target location (default: India): ").strip()
    if not target_location:
        target_location = "India"
    
    # Set company profile
    company_profile.set_profile(company_name, description, budget, sector, goal, target_location)
    
    print("\n" + "=" * 50)
    print("✅ Company Profile Created!")
    print(company_profile)
    print("=" * 50)
    
    return company_profile

async def setup_agents():
    """Setup all agents with proper hierarchy and centralized memory system"""
    print("\n🤖 Setting up AI Agent System...")
    
    # Initialize core systems
    communicator = Communicator()
    scheduler = Scheduler()
    workflow_manager = WorkflowManager(scheduler)
    
    # Initialize centralized memory system
    print("🧠 Initializing centralized memory system...")
    memory_manager = initialize_memory_system(fallback_mode=True)
    
    if memory_manager:
        print("✅ Centralized memory system initialized successfully")
        # Check memory system health
        health_status = check_memory_system_health()
        print(f"📊 Memory system status: {health_status['status']}")
    else:
        print("⚠️ Running without centralized memory system (fallback mode)")
    
    # Create centralized research agent with fallback mode for demo
    research_agent = ResearchAgent(
        fallback_mode=True,
        memory_manager=memory_manager
    )
    
    # Create CEO (central task router)
    ceo = CEOAgent(
        research_agent=research_agent,
        workflow_manager=workflow_manager,
        memory_manager=memory_manager
    )
    
    # Create department heads (executive team)
    marketing_head = MarketingHead(
        research_agent=research_agent,
        memory_manager=memory_manager
    )
    engineering_head = EngineeringHead(
        research_agent=research_agent,
        memory_manager=memory_manager
    )
    
    # Create department agents
    marketing_agent = MarketingAgent(
        research_agent=research_agent,
        memory_manager=memory_manager
    )
    developer_agent = DeveloperAgent(
        research_agent=research_agent,
        memory_manager=memory_manager
    )
    
    # Register department agents with their heads
    marketing_head.register_department_agent("marketing_specialist", marketing_agent)
    engineering_head.register_department_agent("developer", developer_agent)
    
    # Register department heads with CEO
    ceo.register_department_head("marketing", marketing_head)
    ceo.register_department_head("engineering", engineering_head)
    ceo.register_department_head("research", research_agent)  # Register research agent as department head
    
    # Register agents with scheduler
    scheduler.register_agent("CEO", ceo)
    scheduler.register_agent("marketing", marketing_head)
    scheduler.register_agent("engineering", engineering_head)
    scheduler.register_agent("research", research_agent)
    
    print("✅ All agents initialized and registered with centralized memory!")
    
    return {
        'ceo': ceo,
        'marketing_head': marketing_head,
        'engineering_head': engineering_head,
        'marketing_agent': marketing_agent,
        'developer_agent': developer_agent,
        'research_agent': research_agent,
        'scheduler': scheduler,
        'workflow_manager': workflow_manager,
        'memory_manager': memory_manager
    }

async def demonstrate_system(agents):
    """Demonstrate the multi-agent system with sample tasks"""
    print("\n🚀 Demonstrating AI Agent Company System")
    print("=" * 60)
    
    ceo = agents['ceo']
    
    # Sample tasks to demonstrate the system
    sample_tasks = [
        "Launch a new mobile app for food delivery in Indian market",
        "Create marketing campaign for Diwali festival season",
        "Develop e-commerce platform with UPI payment integration",
        "Research competitor analysis for fintech sector in India"
    ]
    
    print(f"\n📋 CEO will process {len(sample_tasks)} strategic tasks:")
    for i, task in enumerate(sample_tasks, 1):
        print(f"   {i}. {task}")
    
    print("\n" + "=" * 60)
    
    # Process each task through CEO
    for i, task in enumerate(sample_tasks, 1):
        print(f"\n🎯 TASK {i}: {task}")
        print("-" * 40)
        
        try:
            result = await ceo.execute_task(task)
            print(f"✅ Task {i} completed: {result}")
        except Exception as e:
            print(f"❌ Task {i} failed: {e}")
        
        # Add delay between tasks for better readability
        await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("🎉 System demonstration completed!")

async def interactive_mode(agents):
    """Interactive mode for user to input custom tasks"""
    print("\n🎮 Interactive Mode - Enter tasks for the CEO to process")
    print("Type 'exit' to quit, 'status' for company status, 'help' for commands")
    print("=" * 60)
    
    ceo = agents['ceo']
    
    while True:
        try:
            user_input = input("\n💼 Enter task for CEO: ").strip()
            
            if user_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'status':
                print("\n📊 Getting company status...")
                status = await ceo.get_company_status()
                for dept, report in status.items():
                    print(f"   {dept.upper()}: {report}")
            elif user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  - Enter any business task for CEO to process")
                print("  - 'status' - Get company status from all departments")
                print("  - 'exit' - Quit interactive mode")
            elif user_input:
                print(f"\n🎯 Processing task: {user_input}")
                print("-" * 40)
                result = await ceo.execute_task(user_input)
                print(f"✅ Task completed: {result}")
            else:
                print("Please enter a valid task or command.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error processing task: {e}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='AI Agent Company System')
    parser.add_argument('--mode', choices=['persistent', 'oneshot'], default='persistent',
                       help='Operating mode: persistent (default) or oneshot')
    parser.add_argument('--project', type=str, help='Project name for oneshot mode')
    parser.add_argument('--interactive', action='store_true', 
                       help='Run in interactive mode')
    parser.add_argument('--demo', action='store_true',
                       help='Run demo tasks')
    
    return parser.parse_args()

async def main():
    """Main function to run the AI Agent Company system"""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Validate arguments
        if args.mode == 'oneshot' and not args.project:
            print("❌ Error: --project is required for oneshot mode")
            print("Example: python main.py --mode oneshot --project my_project")
            return
        
        # Step 1: Get company details from user (only for persistent mode)
        if args.mode == 'persistent':
            get_company_details()
        else:
            print(f"🚀 Starting AI Agent Company in oneshot mode for project: {args.project}")
        
        # Step 2: Initialize company system with mode
        company = AIAgentCompany(mode=args.mode, project_name=args.project)
        
        # Step 3: Choose operation mode
        if args.demo:
            await run_demo_mode(company)
        elif args.interactive:
            await run_interactive_mode(company)
        else:
            # Ask user for mode if not specified
            print("\n🎯 Choose operation mode:")
            print("1. Demo mode - Run sample tasks")
            print("2. Interactive mode - Enter custom tasks")
            
            while True:
                choice = input("\nEnter choice (1 or 2): ").strip()
                if choice == '1':
                    await run_demo_mode(company)
                    break
                elif choice == '2':
                    await run_interactive_mode(company)
                    break
                else:
                    print("Please enter 1 or 2.")
        
        # Step 4: Session cleanup
        await cleanup_session(company, args.mode)
        
    except KeyboardInterrupt:
        print("\n\n👋 System interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ System error: {e}")

async def run_demo_mode(company: AIAgentCompany):
    """Run demo tasks"""
    print("\n🚀 Running Demo Mode")
    print("=" * 50)
    
    demo_tasks = [
        {"description": "Generate leads for technology companies", "department": "sales"},
        {"description": "Create research report on AI market trends", "department": "rnd"},
        {"description": "Develop marketing campaign for new product launch", "department": "marketing"},
        {"description": "Create budget analysis for Q4 operations", "department": "finance"},
        {"description": "Build a simple web application for customer portal", "department": "product"}
    ]
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n🎯 Demo Task {i}: {task['description']}")
        print("-" * 40)
        
        try:
            task_id = await company.submit_task(
                task['description'], 
                department=task['department']
            )
            print(f"✅ Task {task_id} completed")
            
            # Show generated files
            if company.file_manager:
                files = company.file_manager.list_session_files()
                recent_files = [f for f in files if f['created_at'] > (datetime.now() - timedelta(minutes=1)).isoformat()]
                if recent_files:
                    print(f"📁 Generated {len(recent_files)} files:")
                    for file in recent_files:
                        print(f"   • {file['filename']} ({file['category']})")
            
        except Exception as e:
            print(f"❌ Task {i} failed: {e}")
        
        await asyncio.sleep(1)  # Brief pause between tasks

async def run_interactive_mode(company: AIAgentCompany):
    """Run interactive mode"""
    print(f"\n🎮 Interactive Mode - {company.mode.title()} Mode")
    if company.mode == "oneshot":
        print(f"📁 Project: {company.project_name}")
    print("Type 'exit' to quit, 'status' for company status, 'files' to list files")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n💼 Enter task: ").strip()
            
            if user_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'status':
                info = company.get_company_info()
                print(f"\n📊 Company Status:")
                print(f"   Mode: {company.mode}")
                print(f"   Session: {company.current_session_id}")
                print(f"   Active Agents: {info['active_agents']}/{info['total_agents']}")
                print(f"   Success Rate: {info['success_rate']}%")
            elif user_input.lower() == 'files':
                if company.file_manager:
                    files = company.file_manager.list_session_files()
                    print(f"\n📁 Session Files ({len(files)}):")
                    for file in files[-10:]:  # Show last 10 files
                        print(f"   • {file['filename']} ({file['category']}) - {file['size']} bytes")
                else:
                    print("No file manager available")
            elif user_input:
                print(f"\n🎯 Processing task: {user_input}")
                task_id = await company.submit_task(user_input)
                print(f"✅ Task {task_id} completed")
                
                # Show any generated files
                if company.file_manager:
                    files = company.file_manager.list_session_files()
                    recent_files = [f for f in files if f['created_at'] > (datetime.now() - timedelta(minutes=1)).isoformat()]
                    if recent_files:
                        print(f"📁 Generated files:")
                        for file in recent_files:
                            print(f"   • {file['filename']} ({file['category']})")
            else:
                print("Please enter a valid task or command.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def cleanup_session(company: AIAgentCompany, mode: str):
    """Cleanup session and provide summary"""
    try:
        if company.session_manager and company.current_session_id:
            # Get session stats
            stats = company.session_manager.get_session_stats(company.current_session_id)
            
            print(f"\n📊 Session Summary:")
            print(f"   Session ID: {company.current_session_id}")
            print(f"   Mode: {mode}")
            print(f"   Files Created: {stats.get('file_count', 0)}")
            print(f"   Total Size: {stats.get('total_size', 0)} bytes")
            print(f"   Departments: {', '.join(stats.get('departments_involved', []))}")
            
            if mode == "oneshot":
                # Ask if user wants to archive the project
                archive = input("\n🗃️ Archive project files? (y/n): ").strip().lower() == 'y'
                result = company.session_manager.end_session(company.current_session_id, archive)
                
                if result.get('success'):
                    if archive:
                        print(f"✅ Project archived successfully")
                    else:
                        print(f"✅ Project completed - files saved in: {company.file_manager.session_path}")
                else:
                    print(f"⚠️ Session cleanup warning: {result.get('error', 'Unknown error')}")
            else:
                # For persistent mode, just end the session
                company.session_manager.end_session(company.current_session_id)
                print("✅ Session completed")
        
        print("\n🔄 System shutdown complete.")
        
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

if __name__ == "__main__":
    print("🚀 Starting AI Agent Company System...")
    asyncio.run(main())