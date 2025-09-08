import { useState, useEffect } from 'react';
import Head from 'next/head';
import { 
  Activity, 
  Users, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  Brain,
  Database,
  Zap,
  RefreshCw
} from 'lucide-react';
import Layout from '../components/Layout';
import MetricCard from '../components/MetricCard';
import TaskFlowChart from '../components/TaskFlowChart';
import AgentStatusGrid from '../components/AgentStatusGrid';
import RecentActivity from '../components/RecentActivity';
import CompanyOverview from '../components/CompanyOverview';
import CompanySetup from '../components/CompanySetup';
import { systemAPI } from '../lib/api';

interface DashboardData {
  company: any;
  agents: any[];
  recent_tasks: any[];
  system_health: any;
  memory_stats: any;
  timestamp: string;
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSource, setDataSource] = useState<'real' | 'mock'>('real');
  const [needsSetup, setNeedsSetup] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Try to fetch real data from the new dashboard endpoint
      const dashboardData = await systemAPI.getDashboardData();
      
      // Check if company needs setup
      if (!dashboardData.company?.company_name || dashboardData.company.company_name === 'AI Agent Company') {
        setNeedsSetup(true);
        setLoading(false);
        return;
      }
      
      setData(dashboardData);
      setDataSource('real');
      setError(null);
      setNeedsSetup(false);
      
    } catch (err) {
      console.error('Failed to fetch real dashboard data:', err);
      
      // Try fallback to individual endpoints
      try {
        const [healthResponse, agentsResponse, tasksResponse] = await Promise.all([
          systemAPI.health(),
          // These might fail if API server is not running
          fetch('/api/agents').then(r => r.json()).catch(() => ({ data: [] })),
          fetch('/api/tasks?limit=10').then(r => r.json()).catch(() => ({ data: { tasks: [] } }))
        ]);

        const fallbackData: DashboardData = {
          company: {
            company_name: 'AI Agent Company',
            description: 'Autonomous AI-powered business operations platform',
            status: healthResponse.status || 'operational',
            uptime: '99.9%',
            departments: [
              { name: 'Executive', agent_count: 8, active_agents: 8, current_tasks: [] },
              { name: 'Sales', agent_count: 3, active_agents: 3, current_tasks: [{ agent: 'Sales Agent', task: 'Lead generation for Q1' }] },
              { name: 'R&D', agent_count: 3, active_agents: 3, current_tasks: [{ agent: 'R&D Agent', task: 'AI market research' }] },
              { name: 'Product', agent_count: 3, active_agents: 3, current_tasks: [] },
              { name: 'Support', agent_count: 3, active_agents: 3, current_tasks: [] },
              { name: 'Engineering', agent_count: 7, active_agents: 7, current_tasks: [] },
              { name: 'Marketing', agent_count: 2, active_agents: 2, current_tasks: [] },
              { name: 'Finance', agent_count: 3, active_agents: 3, current_tasks: [] }
            ],
            total_agents: 32,
            active_agents: 32,
            task_statistics: {
              total_tasks: 156,
              completed_tasks: 142,
              in_progress_tasks: 8,
              queued_tasks: 4,
              failed_tasks: 2
            },
            success_rate: 94.5,
            performance_metrics: {
              avg_response_time: '2.3s',
              system_load: '45%',
              memory_usage: '67%',
              api_calls_today: 2847
            }
          },
          agents: [
            { name: 'CEO Agent', department: 'Executive', status: 'active', role: 'Chief Executive Officer', capabilities: ['Strategic planning', 'Task delegation'] },
            { name: 'Sales Agent', department: 'Sales', status: 'active', role: 'Lead Generation Specialist', capabilities: ['Lead generation', 'CRM management'], current_task: 'Lead generation for Q1' },
            { name: 'R&D Agent', department: 'R&D', status: 'active', role: 'Research & Innovation Lead', capabilities: ['Technology research', 'Innovation analysis'], current_task: 'AI market research' },
            { name: 'Product Agent', department: 'Product', status: 'active', role: 'Product Strategy Lead', capabilities: ['Roadmap development', 'Feature prioritization'] },
            { name: 'Support Agent', department: 'Support', status: 'active', role: 'Customer Support Lead', capabilities: ['Ticket management', 'Knowledge base'] }
          ],
          recent_tasks: [
            { id: 'TASK-001', description: 'Generate sales leads for Q1 2024', status: 'completed', created_at: '2024-02-09T10:30:00Z', department: 'sales' },
            { id: 'TASK-002', description: 'Analyze AI market trends and opportunities', status: 'in_progress', created_at: '2024-02-09T11:15:00Z', department: 'rnd' },
            { id: 'TASK-003', description: 'Develop product roadmap for next quarter', status: 'queued', created_at: '2024-02-09T12:00:00Z', department: 'product' },
            { id: 'TASK-004', description: 'Simulate customer support ticket handling', status: 'completed', created_at: '2024-02-09T09:45:00Z', department: 'support' },
            { id: 'TASK-005', description: 'Create marketing campaign for new features', status: 'in_progress', created_at: '2024-02-09T13:20:00Z', department: 'marketing' }
          ],
          system_health: {
            overall_status: 'healthy',
            components: {
              api_gateway: 'operational',
              memory_system: 'operational',
              agents: 'operational',
              database: 'operational'
            }
          },
          memory_stats: {
            cache_hit_rate: 87.3,
            total_queries: 12847,
            cache_size: 1000,
            knowledge_items: 5432
          },
          timestamp: new Date().toISOString()
        };

        setData(fallbackData);
        setDataSource('mock');
        setError('Using mock data - API server may not be running');
        
      } catch (fallbackErr) {
        console.error('Fallback data fetch also failed:', fallbackErr);
        setError('Failed to load dashboard data - API server not available');
        setDataSource('mock');
        
        // Set minimal mock data
        setData({
          company: {
            company_name: 'AI Agent Company',
            description: 'Autonomous AI-powered business operations platform',
            status: 'unknown',
            departments: [],
            total_agents: 0,
            active_agents: 0,
            task_statistics: { total_tasks: 0, completed_tasks: 0, in_progress_tasks: 0, queued_tasks: 0, failed_tasks: 0 },
            success_rate: 0,
            performance_metrics: { avg_response_time: 'N/A', system_load: 'N/A', memory_usage: 'N/A', api_calls_today: 0 }
          },
          agents: [],
          recent_tasks: [],
          system_health: { overall_status: 'unknown' },
          memory_stats: {},
          timestamp: new Date().toISOString()
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCompanySetupComplete = (companyData: any) => {
    setNeedsSetup(false);
    fetchDashboardData();
  };

  if (loading && !data) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        </div>
      </Layout>
    );
  }

  if (needsSetup) {
    return <CompanySetup onComplete={handleCompanySetupComplete} />;
  }

  return (
    <>
      <Head>
        <title>AI Agent Company Dashboard</title>
        <meta name="description" content="Monitor and manage your AI agent company" />
      </Head>

      <Layout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">AI Agent Company Dashboard</h1>
              <p className="text-gray-400 mt-1">
                Real-time monitoring of autonomous business operations
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  data?.system_health?.overall_status === 'healthy' ? 'bg-success-500' : 'bg-error-500'
                }`}></div>
                <span className="text-sm text-gray-400">
                  {data?.system_health?.overall_status || 'Unknown'}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`px-2 py-1 rounded text-xs ${
                  dataSource === 'real' ? 'bg-success-900 text-success-300' : 'bg-warning-900 text-warning-300'
                }`}>
                  {dataSource === 'real' ? 'Live Data' : 'Mock Data'}
                </div>
                <button 
                  onClick={fetchDashboardData}
                  className="p-1 text-gray-400 hover:text-white transition-colors"
                  disabled={loading}
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="bg-error-900 border border-error-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-error-400 mr-2" />
                  <span className="text-error-300">{error}</span>
                </div>
                <button 
                  onClick={() => setError(null)}
                  className="text-error-400 hover:text-error-300"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Company Overview */}
          {data?.company && (
            <CompanyOverview companyInfo={data.company} />
          )}

          {/* System Insights Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Memory System */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <Database className="w-5 h-5 mr-2" />
                  Memory System
                </h3>
              </div>
              <div className="card-content">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Cache Hit Rate</span>
                    <span className="text-success-400 font-medium">
                      {data?.memory_stats?.cache_hit_rate || 87.3}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Total Queries</span>
                    <span className="text-white font-medium">
                      {data?.memory_stats?.total_queries?.toLocaleString() || '12,847'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Knowledge Items</span>
                    <span className="text-white font-medium">
                      {data?.memory_stats?.knowledge_items?.toLocaleString() || '5,432'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Cache Size</span>
                    <span className="text-white font-medium">
                      {data?.memory_stats?.cache_size || 1000} items
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Active Agents */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <Zap className="w-5 h-5 mr-2" />
                  Active Agents
                </h3>
              </div>
              <div className="card-content">
                <div className="space-y-3">
                  {data?.agents?.slice(0, 4).map((agent, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${
                          agent.status === 'active' ? 'bg-success-500' : 'bg-gray-500'
                        }`}></div>
                        <span className="text-white text-sm">{agent.name}</span>
                      </div>
                      <span className="text-xs text-gray-400">{agent.department}</span>
                    </div>
                  ))}
                  {data?.agents && data.agents.length > 4 && (
                    <div className="text-center text-xs text-gray-400 pt-2 border-t border-dark-700">
                      +{data.agents.length - 4} more agents
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* System Health */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <Brain className="w-5 h-5 mr-2" />
                  System Health
                </h3>
              </div>
              <div className="card-content">
                <div className="space-y-4">
                  {data?.system_health?.components && Object.entries(data.system_health.components).map(([component, status]) => (
                    <div key={component} className="flex justify-between items-center">
                      <span className="text-gray-400 capitalize">{component.replace('_', ' ')}</span>
                      <span className={`text-sm font-medium ${
                        status === 'operational' ? 'text-success-400' : 'text-error-400'
                      }`}>
                        {status as string}
                      </span>
                    </div>
                  ))}
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Data Source</span>
                    <span className={`text-sm font-medium ${
                      dataSource === 'real' ? 'text-success-400' : 'text-warning-400'
                    }`}>
                      {dataSource === 'real' ? 'Live API' : 'Mock Data'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-white flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                Recent Company Activity
              </h2>
            </div>
            <div className="card-content">
              <RecentActivity tasks={data?.recent_tasks || []} />
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}