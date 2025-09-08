# AI Agent Company - Quick Start Guide

## 🚀 Starting the System

The AI Agent Company system has been fixed and is now working with real data instead of mock data. Here are the different ways to start the system:

### Option 1: Full System (Recommended)
Start both API server and dashboard together:
```bash
python start_full_system.py
```

### Option 2: API Server Only
Start just the API server:
```bash
python start_api_server.py
```

### Option 3: Using the Original Runner
```bash
# API server only
python run_server.py --mode api

# Dashboard only (requires API server running)
python run_server.py --mode dashboard

# Full system
python run_server.py --mode full
```

## 🌐 Access Points

Once started, you can access:

- **Dashboard**: http://localhost:3000
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔑 Authentication

The system now supports optional authentication in development mode:

- **Default Admin**: username: `admin`, password: `admin123`
- **API User**: username: `api_user`, password: `api123`
- **Read Only**: username: `readonly`, password: `readonly123`
- **Development Token**: `dev-token` (automatically used by dashboard)

## ✅ What's Fixed

1. **Real Data Loading**: Dashboard now loads real data from the API server instead of mock data
2. **API Server**: All endpoints are working and return actual company data
3. **Memory System**: Memory search and analytics are connected to the real system
4. **Authentication**: Optional authentication in development mode
5. **Error Handling**: Better error handling and fallback mechanisms
6. **Dashboard Pages**: All pages (Memory, Analytics, Chat) now use real data

## 📊 Dashboard Features

- **Main Dashboard**: Real-time company overview with live metrics
- **Memory System**: Search and browse the centralized knowledge base
- **Analytics**: System performance and department statistics
- **Chat Interface**: Communicate with AI agents and submit tasks
- **Agent Management**: View and monitor all active agents
- **Task Management**: Track task progress and completion

## 🔧 Troubleshooting

If you encounter issues:

1. **Port Already in Use**: Kill existing processes:
   ```bash
   lsof -ti:8000 | xargs kill -9  # Kill API server
   lsof -ti:3000 | xargs kill -9  # Kill dashboard
   ```

2. **Dependencies Missing**: Install requirements:
   ```bash
   pip install -r requirements.txt
   cd dashboard && npm install
   ```

3. **Environment Variables**: Copy and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Dashboard Not Loading**: Make sure API server is running first, then start dashboard

## 🎯 Next Steps

1. Configure your company profile in the dashboard
2. Submit tasks through the chat interface
3. Monitor agent performance in the analytics section
4. Explore the memory system for knowledge management

The system is now fully operational with real data integration!