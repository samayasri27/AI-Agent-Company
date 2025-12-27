# 🧠 AI Agent Company System

A production-grade **multi-agent AI system** that simulates a complete company with autonomous departments, centralized memory, and intelligent task routing.

This system is not a demo or toy simulation — it runs **real business workflows** where AI agents collaborate across departments, execute tasks, share knowledge, and expose everything through a live web dashboard.

---

## 🏢 What This System Does

* Simulates a **real company structure** using AI agents
* Routes tasks intelligently across departments
* Maintains **shared organizational memory**
* Executes tasks autonomously and tracks outcomes
* Provides **real-time visibility** via a web dashboard
* Can run **with or without external APIs** (fallback mode)

---

## 🧩 Core Features

### 🏢 Company Configuration

* Define company name, industry, goals, budget, and target market
* Update company settings dynamically through the dashboard
* Company context is shared across all agents

---

### 🤖 Multi-Agent Architecture

```
CEO Agent (Task Router)
├── Marketing Department
│   └── Marketing Agent
├── Engineering Department
│   ├── Developer Agent
│   ├── QA Agent
│   ├── DevOps Agent
│   └── Tech Lead Agent
├── Finance Department
│   ├── Accountant Agent
│   ├── Financial Analyst Agent
│   └── Treasurer Agent
├── Sales Department
├── Product Department
├── Support Department
└── Research Agent
```

* **CEO Agent** breaks down tasks and routes them
* Department heads coordinate execution
* Agents communicate and share insights internally

---

### 🧠 Centralized Memory System

A shared memory layer accessible to all agents.

**Includes:**

* Knowledge storage (structured + unstructured)
* Conversation & action history
* Vector similarity search
* Cross-agent context sharing
* Learning & performance analysis

**Storage Options:**

* Supabase (PostgreSQL + pgvector)
* Automatic fallback to in-memory storage if not configured

---

### ⚙️ Intelligent Task Routing

* Tasks are analyzed by the CEO agent
* Automatically routed to the appropriate department
* Supports priority levels (High / Medium / Low)
* Tracks full task lifecycle:

  ```
  Task → Assignment → Execution → Result → Analytics
  ```

---

### 🌐 Web Dashboard

A modern web interface for managing and monitoring the AI company.

**Dashboard Capabilities:**

* Live company overview
* Active and completed tasks
* Department & agent status
* Performance analytics
* Memory usage insights
* System health monitoring
* API key & configuration management

---

### 🔌 FastAPI Backend

* Built using **FastAPI**
* Handles:

  * Task submission
  * Agent orchestration
  * Memory operations
  * Dashboard data flow
* Automatic OpenAPI docs available
* Designed for extensibility and external integrations

---

### 📊 Analytics & Monitoring

* Task success rates
* Department efficiency tracking
* Agent-level performance metrics
* Execution timelines
* System health indicators

---

## 🛠️ Technology Stack

### Backend

* **Python**
* **FastAPI**
* Async execution model

### AI / LLM

* **Groq API**

  * `llama3-8b-8192`
  * `mixtral-8x7b-32768`
* Fallback mode supported (no LLM required)

### Memory & Database

* **Supabase (PostgreSQL)**
* `pgvector` for embeddings
* In-memory fallback supported

### Frontend

* **React / Next.js**
* Real-time dashboard updates
* Dark-themed UI

---

## 🔑 Environment Variables

### Required (Full Functionality)

```bash
# Groq (LLM)
GROQ_API_KEY=your_key_here

# Supabase (Memory)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
```

### Optional

```bash
# GitHub Integration
GITHUB_TOKEN=your_token_here

# Alternative Embeddings
OPENAI_API_KEY=your_openai_key
```

---

## 🚀 Getting Started

### 1️⃣ Clone Repository

```bash
git clone <repository-url>
cd ai-agent-company
```

### 2️⃣ Setup Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Configure Environment

```bash
cp .env.example .env
# add your API keys
```

---

## ▶️ Running the System

### Full System (Recommended)

```bash
python start_full_system.py
```

Starts:

* FastAPI backend
* Web dashboard
* Agent orchestration engine

---

### API Server Only

```bash
python run_server.py --mode api --port 8000
```

---

### Dashboard Only

```bash
python run_server.py --mode dashboard --dashboard-port 3000
```

---

### Terminal / CLI Mode

```bash
python main.py
```

---

## 💼 Example Tasks

* Generate sales leads for an Indian fintech startup
* Research AI market trends in India
* Create a product roadmap for a mobile app
* Design a marketing campaign for Diwali
* Analyze competitor pricing strategies

---

## 🧪 Testing

```bash
# Memory system
pytest tests/test_memory_*

# Agents
pytest tests/test_*_agent*

# System integration
pytest tests/test_system_*
```

---

## 🚨 Fallback Modes

The system continues to work even if:

* ❌ No database is configured
* ❌ No LLM API is available
* ❌ External APIs are disabled

Agents degrade gracefully with limited functionality.

---

## 📁 Project Structure

```
ai-agent-company/
├── agents/
├── config/
├── database/
├── engine/
├── scripts/
├── tests/
├── utils/
├── main.py
└── requirements.txt
```

---

## 🔮 Future Enhancements

* Advanced learning & optimization
* Plugin-based agent extensions
* Multi-language support
* RBAC & enterprise security
* Containerized deployment
* Inter-company agent collaboration

---

## 📄 License

MIT License
