# AI Agent Company - Extended Features Documentation

## 🚀 Overview

This document covers the extended features added to the AI Agent Company system, including new departments, external integrations, web dashboard, and API gateway.

## 📋 Table of Contents

1. [New Departments](#new-departments)
2. [External Integrations](#external-integrations)
3. [API Gateway](#api-gateway)
4. [Web Dashboard](#web-dashboard)
5. [Setup Instructions](#setup-instructions)
6. [Usage Examples](#usage-examples)
7. [Deployment Guide](#deployment-guide)

---

## 🏢 New Departments

### 1. Sales Department
**Location**: `agents/sales/`

**Agents**:
- `SalesAgent` - Lead generation and outreach strategy
- `LeadGenerationAgent` - Specialized lead generation
- `OutreachAgent` - Customer outreach automation

**Capabilities**:
- Lead generation and qualification
- Outreach strategy development
- CRM integration (HubSpot/Zoho)
- Sales pipeline analysis
- Customer segmentation
- Performance tracking

**External Integrations**:
- HubSpot CRM API
- Zoho CRM API
- Mock CRM for testing

### 2. R&D Department
**Location**: `agents/rnd/`

**Agents**:
- `RnDAgent` - Research and innovation lead
- `InnovationAgent` - Innovation opportunity identification
- `ResearchCoordinatorAgent` - Research coordination

**Capabilities**:
- Technology research and analysis
- Innovation opportunity identification
- Patent research and IP analysis
- Competitive technology assessment
- Research report generation
- Innovation roadmap development

**External Integrations**:
- ArXiv API for academic papers
- Google Custom Search API
- PubMed API for medical research

### 3. Product Department
**Location**: `agents/product/`

**Agents**:
- `ProductAgent` - Product strategy and roadmap
- `RoadmapAgent` - Product roadmap management
- `FeaturePrioritizationAgent` - Feature prioritization

**Capabilities**:
- Product roadmap development
- Feature prioritization (RICE, KANO frameworks)
- User story creation and management
- Market requirements analysis
- Competitive feature analysis
- Product metrics and KPI tracking

**External Integrations**:
- GitHub API for feature tracking
- Analytics platforms integration

### 4. Support Department
**Location**: `agents/support/`

**Agents**:
- `SupportAgent` - Customer support lead
- `TicketAgent` - Ticket management
- `KnowledgeBaseAgent` - Knowledge base management

**Capabilities**:
- Ticket triage and classification
- Automated response generation
- Knowledge base management
- Escalation handling
- Customer satisfaction tracking
- Support metrics analysis

**External Integrations**:
- Zendesk API
- Support ticket systems
- Knowledge base platforms

---

## 🌍 External Integrations

### Marketing Department Integrations

#### Google Workspace APIs
```python
# Configuration
GOOGLE_WORKSPACE_CLIENT_ID=your_client_id
GOOGLE_WORKSPACE_CLIENT_SECRET=your_client_secret
GOOGLE_WORKSPACE_REFRESH_TOKEN=your_refresh_token
```

**Supported APIs**:
- Google Docs API - Document creation and management
- Google Sheets API - Spreadsheet operations
- Gmail API - Email automation

### Finance Department Integrations

#### Payment APIs
```python
# Stripe Configuration
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Razorpay Configuration
RAZORPAY_API_KEY=rzp_test_...
RAZORPAY_API_SECRET=your_secret

# Plaid Configuration
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENVIRONMENT=sandbox
```

**Supported Operations**:
- Payment processing
- Transaction analysis
- Financial reporting
- Account management

### Engineering Department Integrations

#### GitHub API
```python
# Configuration
GITHUB_TOKEN=ghp_...
GITHUB_ORG=your_organization
GITHUB_REPO=your_repository
```

**Supported Operations**:
- Repository management
- Pull request automation
- Issue tracking
- Code review workflows

### Research Department Integrations

#### Search APIs
```python
# Google Custom Search
GOOGLE_SEARCH_API_KEY=your_api_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id

# PubMed API
PUBMED_API_KEY=your_api_key
```

**Supported Operations**:
- Academic paper search
- Market research
- Competitive analysis
- Patent research

---

## 🔌 API Gateway

### Overview
The API Gateway provides REST endpoints for external interaction with the AI Agent Company system.

**Location**: `api/`
**Main File**: `api/gateway.py`
**Authentication**: `api/auth.py`

### Endpoints

#### Core Endpoints
```
GET  /                    # API information
GET  /health             # System health check
POST /task               # Submit new task
GET  /status/{task_id}   # Get task status
GET  /agents             # List all agents
GET  /tasks              # List tasks
DELETE /tasks/{task_id}  # Cancel task
```

#### Memory System
```
POST /memory/search      # Search memory system
```

#### Authentication
```
POST /auth/login         # User login
POST /auth/api-key       # Create API key
GET  /auth/keys          # List API keys
DELETE /auth/keys/{key}  # Revoke API key
```

### Authentication Methods

#### JWT Tokens
```python
# Login to get token
POST /auth/login
{
  "username": "admin",
  "password": "admin123"
}

# Use token in requests
Authorization: Bearer <jwt_token>
```

#### API Keys
```python
# Use API key directly
Authorization: Bearer ak_test_12345
```

### Example Usage

#### Submit Task
```python
import requests

response = requests.post(
    "http://localhost:8000/task",
    headers={"Authorization": "Bearer <token>"},
    json={
        "task_description": "Generate sales leads for Q1",
        "task_type": "lead_generation",
        "priority": "high",
        "department": "sales"
    }
)
```

#### Check Task Status
```python
task_id = "TASK-000001"
response = requests.get(
    f"http://localhost:8000/status/{task_id}",
    headers={"Authorization": "Bearer <token>"}
)
```

---

## 📊 Web Dashboard

### Overview
A dark-themed React/Next.js dashboard for monitoring and managing the AI Agent Company system.

**Location**: `dashboard/`
**Framework**: Next.js 14 with TypeScript
**Styling**: Tailwind CSS (Dark theme)

### Features

#### Dashboard Pages
- **Main Dashboard** - System overview and metrics
- **Agents** - Agent status and management
- **Tasks** - Task monitoring and control
- **Memory** - Memory system insights
- **Analytics** - Performance analytics
- **Departments** - Department-specific views

#### Key Components
- **MetricCard** - Display key metrics
- **TaskFlowChart** - Task flow visualization
- **AgentStatusGrid** - Agent status overview
- **RecentActivity** - Recent task activity

#### Real-time Features
- Live system status updates
- Real-time task monitoring
- Agent status tracking
- Memory system metrics

### Dashboard Setup

#### Prerequisites
```bash
# Node.js 18+ required
node --version
npm --version
```

#### Installation
```bash
cd dashboard
npm install
```

#### Configuration
```bash
# Environment variables
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

#### Running Dashboard
```bash
# Development mode
npm run dev

# Production build
npm run build
npm start
```

---

## 🛠️ Setup Instructions

### 1. Environment Configuration

Copy and configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```bash
# Core System
GROQ_API_KEY_1=your_groq_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key

# External Integrations
GOOGLE_WORKSPACE_CLIENT_ID=your_google_client_id
STRIPE_API_KEY=your_stripe_key
GITHUB_TOKEN=your_github_token
HUBSPOT_API_KEY=your_hubspot_key
```

### 2. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Dashboard dependencies (optional)
cd dashboard && npm install
```

### 3. Database Setup

```bash
# Initialize memory system
python scripts/setup_memory_system.py

# Validate configuration
python scripts/validate_memory_config.py
```

### 4. Run the System

#### Terminal Mode (Default)
```bash
python run_server.py
# or
python main.py
```

#### API Server Mode
```bash
python run_server.py --mode api --port 8000
```

#### Dashboard Only
```bash
python run_server.py --mode dashboard --dashboard-port 3000
```

#### Full Stack Mode
```bash
python run_server.py --mode full
```

---

## 💡 Usage Examples

### 1. Sales Lead Generation

#### Via Terminal
```python
# Task: Generate leads for technology companies
task = {
    "description": "Generate 50 qualified leads for technology companies",
    "type": "lead_generation",
    "department": "sales",
    "criteria": {
        "industry": "technology",
        "company_size": "mid-market",
        "min_score": 75
    }
}
```

#### Via API
```bash
curl -X POST "http://localhost:8000/task" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Generate 50 qualified leads for technology companies",
    "task_type": "lead_generation",
    "department": "sales",
    "metadata": {
      "industry": "technology",
      "company_size": "mid-market"
    }
  }'
```

### 2. R&D Research Report

#### Via Terminal
```python
# Task: Generate AI research report
task = {
    "description": "Generate comprehensive AI research report",
    "type": "research_report",
    "department": "rnd",
    "topic": "artificial_intelligence",
    "scope": "market_analysis"
}
```

### 3. Product Roadmap Development

#### Via API
```bash
curl -X POST "http://localhost:8000/task" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Develop Q1 product roadmap",
    "task_type": "roadmap",
    "department": "product",
    "metadata": {
      "time_horizon": "3_months",
      "focus_areas": ["AI", "Automation", "Integration"]
    }
  }'
```

### 4. Support Ticket Simulation

#### Via Terminal
```python
# Task: Simulate daily support operations
task = {
    "description": "Simulate daily support ticket handling",
    "type": "ticket_simulation",
    "department": "support",
    "ticket_volume": 100,
    "time_period": "24_hours"
}
```

---

## 🚀 Deployment Guide

### 1. Production Environment Setup

#### Environment Variables
```bash
# Production API keys
GROQ_API_KEY_1=prod_groq_key
SUPABASE_URL=https://prod-project.supabase.co
JWT_SECRET_KEY=your_secure_secret_key

# External API keys
STRIPE_API_KEY=sk_live_...
GITHUB_TOKEN=ghp_prod_token
```

#### Security Configuration
```bash
# API Gateway security
JWT_SECRET_KEY=your_256_bit_secret
TOKEN_EXPIRY_HOURS=24

# CORS configuration
ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run_server.py", "--mode", "api", "--host", "0.0.0.0"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY_1=${GROQ_API_KEY_1}
      - SUPABASE_URL=${SUPABASE_URL}
    
  dashboard:
    build: ./dashboard
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://api:8000
    depends_on:
      - api
```

### 3. Cloud Deployment Options

#### AWS Deployment
- **ECS/Fargate** for containerized deployment
- **Lambda** for serverless functions
- **RDS** for database (if not using Supabase)
- **CloudFront** for dashboard CDN

#### Google Cloud Deployment
- **Cloud Run** for containerized services
- **Cloud Functions** for serverless
- **Cloud SQL** for database
- **Firebase Hosting** for dashboard

#### Heroku Deployment
```bash
# Create Heroku apps
heroku create ai-agent-company-api
heroku create ai-agent-company-dashboard

# Deploy API
git subtree push --prefix=. heroku main

# Deploy Dashboard
git subtree push --prefix=dashboard heroku-dashboard main
```

### 4. Monitoring and Logging

#### Health Checks
```python
# API health endpoint
GET /health

# Response
{
  "status": "healthy",
  "components": {
    "company_system": "operational",
    "memory_system": "operational",
    "api_gateway": "operational"
  }
}
```

#### Logging Configuration
```python
# Environment variables
LOG_LEVEL=INFO
LOG_FILE=agent_company.log
DEBUG_MEMORY=false
```

#### Metrics Collection
- Task completion rates
- Response times
- Error rates
- Memory usage
- Agent performance

---

## 🔧 Advanced Configuration

### 1. Custom Department Creation

#### Create New Department
```python
# 1. Create department directory
mkdir agents/custom_department

# 2. Create __init__.py
# 3. Create main agent class
# 4. Implement process_task method
# 5. Add external integrations
```

#### Department Template
```python
class CustomAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="Custom Agent",
            role="Custom Role",
            department="Custom",
            capabilities=["Custom capability"]
        )
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Implement custom logic
        pass
```

### 2. External API Integration

#### Add New API Integration
```python
# 1. Add API credentials to .env
# 2. Install required packages
# 3. Implement API client
# 4. Add to agent capabilities
```

#### API Client Template
```python
class CustomAPIClient:
    def __init__(self):
        self.api_key = os.getenv('CUSTOM_API_KEY')
        self.base_url = "https://api.custom.com"
    
    def make_request(self, endpoint: str, data: Dict) -> Dict:
        # Implement API request logic
        pass
```

### 3. Dashboard Customization

#### Add New Dashboard Page
```typescript
// 1. Create page in dashboard/pages/
// 2. Add navigation item
// 3. Implement components
// 4. Connect to API
```

#### Custom Component Template
```typescript
interface CustomComponentProps {
  data: any[];
}

export default function CustomComponent({ data }: CustomComponentProps) {
  return (
    <div className="card">
      {/* Custom component logic */}
    </div>
  );
}
```

---

## 📈 Performance Optimization

### 1. API Gateway Optimization
- Connection pooling
- Request caching
- Rate limiting
- Async processing

### 2. Memory System Optimization
- Vector indexing
- Query optimization
- Cache management
- Connection pooling

### 3. Dashboard Optimization
- Code splitting
- Image optimization
- API response caching
- Progressive loading

---

## 🔒 Security Best Practices

### 1. API Security
- JWT token authentication
- API key management
- Rate limiting
- Input validation
- CORS configuration

### 2. Data Security
- Environment variable protection
- Database encryption
- Secure API communications
- Access control

### 3. Deployment Security
- HTTPS enforcement
- Security headers
- Container security
- Network isolation

---

## 🐛 Troubleshooting

### Common Issues

#### API Gateway Issues
```bash
# Check if FastAPI is installed
pip install fastapi uvicorn

# Verify port availability
netstat -an | grep 8000

# Check logs
python run_server.py --mode api --debug
```

#### Dashboard Issues
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache
rm -rf dashboard/node_modules dashboard/.next
cd dashboard && npm install

# Check API connection
curl http://localhost:8000/health
```

#### External API Issues
```bash
# Verify API keys
python -c "import os; print(os.getenv('GROQ_API_KEY_1'))"

# Test API connectivity
python -c "import requests; print(requests.get('https://api.groq.com/health').status_code)"
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG_MEMORY=true
export LOG_LEVEL=DEBUG

# Run with debug
python run_server.py --mode api --debug
```

---

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)

### API References
- [Groq API](https://console.groq.com/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [GitHub API](https://docs.github.com/en/rest)
- [Stripe API](https://stripe.com/docs/api)

### Community
- GitHub Issues for bug reports
- Discussions for feature requests
- Wiki for community contributions

---

## 🎉 Conclusion

The extended AI Agent Company system now provides:

✅ **4 New Departments** with specialized capabilities
✅ **Multiple External Integrations** for real-world connectivity  
✅ **REST API Gateway** for external access
✅ **Modern Web Dashboard** for monitoring and management
✅ **Flexible Deployment Options** for various environments
✅ **Comprehensive Documentation** for easy setup and usage

The system maintains its core architecture while adding powerful new capabilities for production use, external integrations, and user-friendly interfaces.

**Status**: ✅ **PRODUCTION READY - EXTENDED FEATURES COMPLETE**