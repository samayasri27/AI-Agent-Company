# AI Agent Company Dashboard

A modern, dark-themed web dashboard for monitoring and managing the AI Agent Company system.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation & Setup

1. **Install dependencies:**
   ```bash
   cd dashboard
   npm install
   ```

2. **Configure environment:**
   ```bash
   # Create .env.local file
   echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open dashboard:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🎨 Features

### Dashboard Pages
- **Main Dashboard** - System overview, metrics, and real-time monitoring
- **Agents** - Agent status, capabilities, and current tasks
- **Tasks** - Task monitoring, progress tracking, and filtering
- **Memory** - Memory system insights and knowledge search
- **Analytics** - Performance metrics and system analytics
- **Departments** - Department overview and performance
- **Chat** - Direct communication with AI agents
- **Settings** - System configuration and preferences

### Key Components
- **Real-time Updates** - Live system status and metrics
- **Dark Theme** - Modern, eye-friendly interface
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Interactive Charts** - Task flow visualization and analytics
- **Status Indicators** - Visual system health monitoring

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Optional: Custom port
PORT=3000
```

### API Integration
The dashboard connects to the AI Agent Company API Gateway. Make sure the API server is running on the configured URL.

## 🛠️ Development

### Available Scripts
```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Project Structure
```
dashboard/
├── components/          # Reusable React components
│   ├── Layout.tsx      # Main layout with sidebar
│   ├── Sidebar.tsx     # Navigation sidebar
│   ├── Header.tsx      # Top header with search
│   ├── MetricCard.tsx  # Metric display cards
│   └── ...
├── pages/              # Next.js pages
│   ├── index.tsx       # Main dashboard
│   ├── agents.tsx      # Agents page
│   ├── tasks.tsx       # Tasks page
│   └── ...
├── lib/                # Utilities and API client
│   └── api.ts          # API client with auth
├── styles/             # CSS and styling
│   └── globals.css     # Global styles with Tailwind
└── public/             # Static assets
```

## 🎯 Usage

### Starting the Dashboard

#### Option 1: Direct npm command
```bash
cd dashboard
npm run dev
```

#### Option 2: Using the Python script
```bash
python start_dashboard.py
```

#### Option 3: Using the main server runner
```bash
# Dashboard only
python run_server.py --mode dashboard

# Full stack (API + Dashboard)
python run_server.py --mode full
```

### Authentication
The dashboard uses token-based authentication. You'll need to:

1. Start the API server
2. Get an authentication token
3. The dashboard will handle authentication automatically

### Mock Data
If the API server is not available, the dashboard will display mock data for development and demonstration purposes.

## 🔒 Security

### Authentication
- JWT token-based authentication
- Automatic token refresh
- Secure credential storage

### API Communication
- HTTPS support in production
- CORS configuration
- Request/response validation

## 🚀 Deployment

### Production Build
```bash
npm run build
npm start
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Configuration
```bash
# Production environment
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
NODE_ENV=production
```

## 🐛 Troubleshooting

### Common Issues

#### Dashboard won't start
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules .next
npm install
```

#### API connection issues
```bash
# Check API server is running
curl http://localhost:8000/health

# Verify environment variables
cat .env.local
```

#### Build errors
```bash
# Check TypeScript errors
npm run build

# Fix linting issues
npm run lint
```

### Debug Mode
```bash
# Enable debug logging
DEBUG=* npm run dev

# Check browser console for errors
# Open browser dev tools (F12)
```

## 📊 Performance

### Optimization Features
- Code splitting and lazy loading
- Image optimization
- Static generation where possible
- Efficient re-rendering with React

### Monitoring
- Real-time performance metrics
- Error boundary handling
- Loading states and fallbacks
- Responsive design optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Guidelines
- Follow TypeScript best practices
- Use Tailwind CSS for styling
- Maintain responsive design
- Add proper error handling
- Write meaningful commit messages

## 📄 License

This project is part of the AI Agent Company system and follows the same license terms.

## 🆘 Support

For dashboard-specific issues:
1. Check the browser console for errors
2. Verify API server connectivity
3. Review environment configuration
4. Check Node.js and npm versions

For system-wide issues, refer to the main project documentation.

---

**Dashboard Status**: ✅ **FULLY FUNCTIONAL**

The AI Agent Company Dashboard provides a complete web interface for monitoring and managing your AI agent system with real-time updates, modern design, and comprehensive functionality.