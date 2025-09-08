# AI Agent Company System

A sophisticated multi-agent AI system that simulates a complete company with specialized departments, centralized memory management, and intelligent task routing. The system features autonomous agents that collaborate to execute complex business tasks across marketing, engineering, finance, and research departments.

## 🚀 Latest Updates (v3.0) - FULLY FUNCTIONAL DASHBOARD

### ✅ **Complete Web Dashboard & Real Company Operations**
- **🏢 Company Setup**: Configure your actual company profile, goals, and target market
- **📊 Live Dashboard**: Real-time monitoring of your AI agent company operations
- **🎯 Task Management**: Submit real tasks and watch AI agents execute them
- **⚙️ Settings Management**: Configure API keys and system preferences through web UI
- **📈 Performance Analytics**: Live metrics, success rates, and system health monitoring
- **🤖 Agent Monitoring**: See which agents are active and what tasks they're working on

### ✅ **Real Business Simulation**
- **Functional AI Company**: Not just a demo - actually runs business operations
- **Live Task Processing**: Submit tasks like "Generate sales leads for fintech startup in India"
- **Department Operations**: Sales, R&D, Product, and Support agents working autonomously
- **Real Data Flow**: Tasks → Agent Assignment → Processing → Results → Dashboard Updates
- **Company Analytics**: Track task completion rates, agent performance, department efficiency

### ✅ **Production-Ready Features**
- **API Gateway**: Full REST API with authentication for external integrations
- **Configuration Management**: Web-based API key and system configuration
- **Real-time Updates**: Live dashboard updates as agents complete tasks
- **Task History**: Complete audit trail of all company activities
- **System Health**: Monitor API connectivity, agent status, and performance metrics

### ✅ **Enhanced Agent Architecture**
- **Centralized Memory System**: Shared knowledge base across all agents
- **Intelligent Task Routing**: Automatic assignment to appropriate departments
- **Cross-Agent Communication**: Agents share insights and collaborate on complex tasks
- **Fallback Mode**: System works without external APIs for development/testing

## 🏗️ System Architecture

```
CEO Agent (Task Router)
├── Marketing Head
│   └── Marketing Agent
├── Engineering Head
│   ├── Developer Agent
│   ├── QA Agent
│   ├── DevOps Agent
│   └── Tech Lead Agent
├── Finance Head
│   ├── Accountant Agent
│   ├── Financial Analyst
│   └── Treasurer Agent
└── Research Agent

Memory System
├── Memory Manager Agent
├── Knowledge Agent (Data Storage)
├── History Agent (Conversations & Actions)
└── Learning Agent (Pattern Analysis)
```

## 🛠️ External Tools & Integrations

### **AI/LLM Services**
- **Groq API**: Primary LLM service for all agent reasoning
  - Models: `llama3-8b-8192`, `mixtral-8x7b-32768`
  - Used for: Strategic analysis, content generation, decision making
  - Fallback: System works without LLM (limited functionality)

### **Database & Memory**
- **Supabase**: PostgreSQL database with vector extensions
  - Used for: Centralized memory storage, vector similarity search
  - Extensions: `pgvector` for embedding storage
  - Fallback: In-memory storage when not configured

### **Development Tools**
- **GitHub Integration**: Code deployment and version control
  - Used by: Deployment Agent for code management
  - Optional: System works without GitHub integration

### **Web Services**
- **HTTP Requests**: External API integrations
  - Used for: Research data gathering, external service calls
  - Libraries: `requests`, `aiohttp`

## 🔑 Required API Keys

### **Essential (for full functionality)**
```bash
# Groq API Keys (Primary LLM Service)
GROQ_API_KEY=your_groq_api_key_here
GROQ_API_KEY_1=your_primary_groq_key_here
GROQ_API_KEY_2=your_backup_groq_key_here

# Supabase Database (Centralized Memory)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here
```

### **Optional (for enhanced features)**
```bash
# GitHub Integration (for deployment features)
GITHUB_TOKEN=your_github_token_here

# OpenAI (alternative embedding service)
OPENAI_API_KEY=your_openai_key_here

# Model Configuration
MODEL_NAME=mixtral-8x7b-32768
EMBEDDING_MODEL=text-embedding-ada-002
```

## 📦 Installation

### **1. Clone Repository**
```bash
git clone <repository-url>
cd ai-agent-company
```

### **2. Set Up Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env
```

### **4. Set Up Database (Optional)**
```bash
# Validate memory system configuration
python scripts/validate_memory_config.py

# Set up database schema
python scripts/setup_memory_system.py
```

## 🚀 Extended Features (NEW!)

### **New Departments Added**
- 🏢 **Sales Department** - Lead generation, CRM integration, outreach strategy
- 🔬 **R&D Department** - Research reports, innovation analysis, patent research  
- 📦 **Product Department** - Roadmap development, feature prioritization
- 🎧 **Support Department** - Ticket simulation, automated responses, KB management

### **External API Integrations**
- 📊 **Marketing** → Google Workspace APIs (Docs, Sheets, Gmail)
- 💰 **Finance** → Payment APIs (Stripe, Razorpay, Plaid)
- 👨‍💻 **Engineering** → GitHub API (repos, PRs, issues)
- 🔍 **Research** → Search APIs (Google, ArXiv, PubMed)
- 📞 **Sales/CRM** → CRM APIs (HubSpot, Zoho)

### **Web Dashboard & API Gateway**
- 🎨 **Dark-themed React/Next.js dashboard** with real-time monitoring
- 🔌 **REST API Gateway** with token-based authentication
- 📈 **Task flow visualization** and agent status tracking
- 🧠 **Memory system insights** and performance analytics

## 🚀 Quick Start - Run Your AI Company

### **🎯 Recommended: Full System (One Command)**
```bash
python start_full_system.py
```
**What this does:**
- Starts API server on http://localhost:8000
- Starts web dashboard on http://localhost:3000
- Opens your browser to the company setup page
- Ready to use in 30 seconds!

### **🌐 Access Your AI Company**
1. **Dashboard**: http://localhost:3000 - Main company interface
2. **API Server**: http://localhost:8000 - REST API endpoints  
3. **API Docs**: http://localhost:8000/docs - Interactive API documentation

### **🏢 First Time Setup**
1. Open http://localhost:3000
2. Complete the company setup form:
   - Company name and description
   - Industry sector (Technology, Healthcare, Finance, etc.)
   - Budget and business goals
   - Target market location
3. Start submitting tasks to your AI agents!

### **💼 Example Tasks to Try**
- "Generate 50 sales leads for our fintech startup targeting Indian SMEs"
- "Research AI market trends in India and create a competitive analysis report"
- "Develop a product roadmap for our mobile banking app"
- "Create a Diwali marketing campaign for our e-commerce platform"
- "Analyze competitor pricing strategies in the Indian market"

### **Alternative Run Modes**

#### **API Server Only**
```bash
python run_server.py --mode api --port 8000
```
- REST API endpoints for external access
- Token-based authentication
- Programmatic task submission

#### **Dashboard Only**
```bash
python run_server.py --mode dashboard --dashboard-port 3000
```
- Modern React-based web interface
- Real-time system monitoring
- Visual task flow tracking

#### **Terminal Mode (CLI)**
```bash
python run_server.py --mode terminal
# or
python main.py
```
- Interactive command-line interface
- Direct agent interaction
- Good for development/testing

### **Legacy Modes**

#### **Demo Mode**
- Runs predefined sample tasks
- Demonstrates system capabilities
- Shows agent collaboration

#### **Interactive Mode**
- Enter custom tasks for CEO processing
- Real-time task execution
- Company status monitoring

### **Available Commands**
```bash
# System validation
python check_system.py

# Memory system health check
python check_memory_config.py

# Run specific agent tests
python exemain_test.py    # Executive agents
python engmain_test.py    # Engineering agents
python finmain_test.py    # Finance agents
```

## 🧪 Testing

### **Core Tests**
```bash
# Memory system integration
python -m pytest tests/test_memory_*

# Agent functionality
python -m pytest tests/test_*_agent*

# System integration
python -m pytest tests/test_system_*
```

### **Manual Testing**
```bash
# Test individual departments
python exemain_test.py     # Executive team
python engmain_test.py     # Engineering team
python finmain_test.py     # Finance team
python engupmain_test.py   # Engineering with workspace
```

## 🏢 Agent Capabilities

### **CEO Agent**
- Strategic task analysis and planning
- Task breakdown and department routing
- Workflow management and coordination
- Company status monitoring

### **Marketing Department**
- Campaign strategy and execution
- Social media management
- Content creation and planning
- Market research integration

### **Engineering Department**
- Software development and architecture
- Mobile app development (India-focused)
- API integration and deployment
- Code review and quality assurance
- DevOps and infrastructure management

### **Finance Department**
- Financial analysis and reporting
- Budget management and planning
- Accounting and bookkeeping
- Treasury operations

### **Research Agent**
- Market research and analysis
- Competitive intelligence
- Technical research support
- Data caching and optimization

## 🧠 Memory System Features

### **Knowledge Management**
- Structured and unstructured data storage
- Vector similarity search
- Content categorization and tagging
- Cross-agent knowledge sharing

### **Conversation History**
- Complete conversation logging
- Action tracking and audit trails
- Context preservation across sessions
- Historical analysis and insights

### **Learning & Analytics**
- Pattern recognition and analysis
- Performance metrics tracking
- Success rate optimization
- Behavioral insights

### **Caching & Performance**
- Multi-level caching system
- TTL-based cache expiration
- Connection pooling
- Query optimization

## 🔧 Configuration

### **Memory System Settings**
```python
# config/memory_config.py
CACHE_SIZE = 1000
EMBEDDING_MODEL = "text-embedding-ada-002"
VECTOR_DIMENSION = 1536
CONNECTION_POOL_SIZE = 10
```

### **Agent Configuration**
```python
# Individual agent settings
TEMPERATURE = 0.3  # LLM creativity level
MODEL_NAME = "mixtral-8x7b-32768"
FALLBACK_MODE = True  # Enable fallback without external APIs
```

## 🎨 Dashboard Features

### **📊 Company Homepage**
- **Live Company Overview**: Real-time stats about your AI company
- **Department Status**: See which departments are active and what they're working on
- **Active Tasks**: Monitor current task execution and progress
- **Performance Metrics**: Success rates, response times, system health
- **Agent Activity**: Live feed of agent actions and completions

### **🎯 Task Management**
- **Submit Tasks**: Easy form to create new business tasks
- **Task Types**: Research, Sales, Product Development, Marketing, Support
- **Priority Levels**: High, Medium, Low priority assignment
- **Department Routing**: Auto-assign or manually specify department
- **Progress Tracking**: Real-time progress bars and status updates
- **Task History**: Complete audit trail with timestamps and results

### **🤖 Agent Monitoring**
- **Agent Status**: See which agents are active, idle, or working
- **Current Tasks**: What each agent is currently working on
- **Capabilities**: View each agent's skills and specializations
- **Department View**: Organized by Sales, R&D, Product, Support
- **Performance Stats**: Task completion rates per agent

### **⚙️ Settings & Configuration**
- **API Keys**: Configure Groq, Supabase, GitHub, and other integrations
- **Company Profile**: Update business information and goals
- **System Preferences**: Customize dashboard behavior and notifications
- **Integration Status**: See which external services are connected
- **Security Settings**: Manage authentication and access controls

### **📈 Analytics & Insights**
- **Task Distribution**: Visual breakdown of completed vs in-progress tasks
- **Success Metrics**: Company-wide performance analytics
- **Department Performance**: Compare efficiency across departments
- **System Health**: API connectivity, memory usage, response times
- **Growth Tracking**: Monitor your AI company's productivity over time

## 🚨 Troubleshooting

### **Common Issues**

#### **Memory System Not Available**
```bash
# Check configuration
python scripts/validate_memory_config.py

# Verify Supabase credentials
python check_memory_config.py
```

#### **LLM API Errors**
```bash
# Verify Groq API keys
echo $GROQ_API_KEY

# Test API connectivity
python check_system.py
```

#### **Agent Communication Issues**
```bash
# Check agent registration
python -c "from main import setup_agents; import asyncio; asyncio.run(setup_agents())"
```

### **Fallback Modes**
- **No Memory System**: Agents work with limited memory
- **No LLM Access**: Agents use predefined responses
- **No External APIs**: Core functionality remains available

## 📁 Project Structure

```
ai-agent-company/
├── agents/                 # Agent implementations
│   ├── executive/         # CEO, department heads
│   ├── engineering/       # Development team
│   ├── finance/          # Finance team
│   ├── marketing/        # Marketing team
│   ├── memory/           # Memory system agents
│   └── research/         # Research agent
├── config/               # Configuration files
├── database/            # Database schema and models
├── engine/              # Core system components
├── scripts/             # Setup and utility scripts
├── tests/               # Test suites
├── utils/               # Utility functions
├── main.py              # Main application entry point
└── requirements.txt     # Python dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Run system diagnostics: `python check_system.py`
3. Review logs in the `logs/` directory
4. Create an issue with system details

## 📚 Extended Documentation

For detailed information about the new features:
- **[Extended Features Documentation](EXTENDED_FEATURES_DOCUMENTATION.md)** - Complete guide to new departments, integrations, and web dashboard
- **[API Gateway Documentation](api/README.md)** - REST API endpoints and authentication
- **[Dashboard Setup Guide](dashboard/README.md)** - Web dashboard installation and configuration

## 🔮 Future Enhancements

- ✅ **Web Interface**: ~~Browser-based agent management~~ **COMPLETED**
- ✅ **API Endpoints**: ~~RESTful API for external integrations~~ **COMPLETED**
- **Advanced Analytics**: Enhanced learning and insights
- **Multi-Language Support**: Localization for global markets
- **Plugin System**: Extensible agent capabilities
- **Real-time Collaboration**: Live agent interaction monitoring
- **Microservices Architecture**: Containerized deployment
- **Advanced Security**: OAuth2, RBAC, audit logging