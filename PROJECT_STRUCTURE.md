# AI Agent Company - Project Structure

## 📁 Core Directory Structure

```
ai-agent-company/
├── 📁 agents/                    # Agent implementations
│   ├── 📁 executive/            # Executive team agents
│   │   ├── ceo_agent.py         # CEO - Central task router
│   │   ├── coo_agent.py         # Chief Operating Officer
│   │   ├── cto_agent.py         # Chief Technology Officer
│   │   ├── cfo_agent.py         # Chief Financial Officer
│   │   ├── hr_agent.py          # Human Resources
│   │   ├── strategist_agent.py  # Strategy Lead
│   │   ├── marketing_head.py    # Marketing Department Head
│   │   ├── engineering_head.py  # Engineering Department Head
│   │   ├── finance_head.py      # Finance Department Head
│   │   └── department_head_base.py # Base class for department heads
│   │
│   ├── 📁 engineering/          # Engineering team agents
│   │   ├── developer_agent.py   # Software Developer
│   │   ├── qa_agent.py          # Quality Assurance
│   │   ├── devops_agent.py      # DevOps Engineer
│   │   ├── deployment_agent.py  # Deployment Specialist
│   │   ├── code_reviewer_agent.py # Code Reviewer
│   │   ├── engineering_manager_agent.py # Engineering Manager
│   │   └── tech_lead_agent.py   # Technical Lead
│   │
│   ├── 📁 marketing/            # Marketing team agents
│   │   ├── marketing_agent.py   # Marketing Specialist
│   │   └── content_strategist.py # Content Strategist
│   │
│   ├── 📁 finance/              # Finance team agents
│   │   ├── accountant_agent.py  # Accountant
│   │   ├── financial_analyst_agent.py # Financial Analyst
│   │   └── treasurer_agent.py   # Treasurer
│   │
│   ├── 📁 memory/               # Centralized memory system
│   │   ├── memory_manager_agent.py # Memory Manager (coordinator)
│   │   ├── knowledge_agent.py   # Knowledge storage & retrieval
│   │   ├── history_agent.py     # Conversation & action history
│   │   ├── learning_agent.py    # Pattern analysis & learning
│   │   ├── cache_manager.py     # Caching system
│   │   ├── connection_pool.py   # Database connection pooling
│   │   ├── security_validator.py # Security & validation
│   │   └── error_handler.py     # Error handling & recovery
│   │
│   ├── 📁 research/             # Research agents
│   │   └── research_agent.py    # Centralized research agent
│   │
│   └── agent_base.py            # Base class for all agents
│
├── 📁 config/                   # Configuration files
│   ├── company_profile.py       # Company profile management
│   └── memory_config.py         # Memory system configuration
│
├── 📁 database/                 # Database schema and models
│   ├── models.py                # SQLAlchemy models
│   ├── setup.py                 # Database setup utilities
│   ├── agent_memory.sql         # SQL schema
│   └── README.md                # Database documentation
│
├── 📁 engine/                   # Core system components
│   ├── communicator.py          # Inter-agent communication
│   ├── scheduler.py             # Task scheduling
│   └── workflow_manager.py      # Workflow orchestration
│
├── 📁 scripts/                  # Setup and utility scripts
│   ├── setup_memory_system.py   # Memory system setup
│   └── validate_memory_config.py # Configuration validation
│
├── 📁 tests/                    # Test suites
│   ├── test_memory_*.py         # Memory system tests
│   ├── test_*_agent*.py         # Agent functionality tests
│   └── test_system_*.py         # System integration tests
│
├── 📁 utils/                    # Utility functions
│   └── memory_system_init.py    # Memory system initialization
│
├── 📁 logs/                     # System logs (auto-created)
├── 📁 data/                     # Data storage (auto-created)
└── 📁 workspace/                # Agent workspace (auto-created)
```

## 🚀 Main Application Files

```
├── main.py                      # Main application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment configuration template
├── README.md                    # Project documentation
└── PROJECT_STRUCTURE.md         # This file
```

## 🧪 Test Files

```
├── exemain_test.py              # Executive team test
├── engmain_test.py              # Engineering team test
├── engupmain_test.py            # Engineering with workspace test
├── finmain_test.py              # Finance team test
├── check_system.py              # System health check
└── check_memory_config.py       # Memory configuration check
```

## 📊 Key Components Overview

### **Agent Hierarchy**
- **CEO Agent**: Central task router and strategic decision maker
- **Department Heads**: Marketing, Engineering, Finance heads
- **Specialists**: Individual agents with specific expertise
- **Memory Agents**: Specialized agents for memory management
- **Research Agent**: Centralized research and data gathering

### **Memory System**
- **Memory Manager**: Coordinates all memory operations
- **Knowledge Agent**: Handles data storage and retrieval
- **History Agent**: Manages conversation and action logs
- **Learning Agent**: Analyzes patterns and provides insights
- **Support Components**: Caching, security, error handling

### **Core Engine**
- **Workflow Manager**: Orchestrates task execution
- **Scheduler**: Manages agent task assignments
- **Communicator**: Handles inter-agent communication

### **Configuration**
- **Company Profile**: Business context and settings
- **Memory Config**: Database and memory system settings
- **Environment Variables**: API keys and external service config

## 🔧 File Responsibilities

### **Agent Files**
- Implement specific agent behaviors and capabilities
- Handle task execution and decision making
- Integrate with centralized memory system
- Communicate with other agents through established protocols

### **Memory System Files**
- Provide centralized data storage and retrieval
- Implement caching for performance optimization
- Handle security validation and error recovery
- Support vector similarity search and embeddings

### **Engine Files**
- Orchestrate multi-agent workflows
- Schedule and route tasks between agents
- Manage communication protocols
- Handle system-level coordination

### **Configuration Files**
- Define system settings and parameters
- Manage environment-specific configurations
- Handle database connection settings
- Store business context and profiles

### **Test Files**
- Validate individual agent functionality
- Test memory system integration
- Verify system-wide workflows
- Ensure backward compatibility

## 🚀 Getting Started

1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure environment**: Copy `.env.example` to `.env` and add your API keys
4. **Run system check**: `python check_system.py`
5. **Start the system**: `python main.py`

## 📝 Development Guidelines

- **Agent Development**: Extend `AgentBase` class for new agents
- **Memory Integration**: Use `memory_manager` parameter in agent constructors
- **Testing**: Add tests for new functionality in `tests/` directory
- **Configuration**: Update config files for new settings
- **Documentation**: Update README.md for new features

## 🔍 Troubleshooting

- **System Issues**: Run `python check_system.py`
- **Memory Problems**: Run `python check_memory_config.py`
- **Agent Errors**: Check individual test files
- **Configuration**: Validate `.env` file settings
- **Logs**: Check `logs/` directory for detailed error information