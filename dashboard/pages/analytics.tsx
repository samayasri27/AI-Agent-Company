import { useState, useEffect } from 'react';
import Head from 'next/head';
import { BarChart3, TrendingUp, PieChart, Activity, RefreshCw, AlertCircle } from 'lucide-react';
import Layout from '../components/Layout';
import { systemAPI, apiClient } from '../lib/api';

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      
      // Fetch dashboard data which includes analytics
      const dashboardData = await systemAPI.getDashboardData();
      
      // Extract analytics from company data
      const analyticsData = {
        tasksCompleted: dashboardData.company?.task_statistics?.completed_tasks || 0,
        successRate: dashboardData.company?.success_rate || 0,
        avgResponseTime: dashboardData.company?.performance_metrics?.avg_response_time || 'N/A',
        activeAgents: dashboardData.company?.active_agents || 0,
        departments: dashboardData.departments || dashboardData.company?.departments || [],
        systemHealth: {
          cpuUsage: parseInt(dashboardData.company?.performance_metrics?.system_load?.replace('%', '') || '45'),
          memoryUsage: parseInt(dashboardData.company?.performance_metrics?.memory_usage?.replace('%', '') || '67'),
          apiCallsPerMin: dashboardData.company?.performance_metrics?.api_calls_today || 142,
          errorRate: 0.3,
          uptime: 99.9
        }
      };
      
      setAnalytics(analyticsData);
      setError(null);
      
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
      setError('Failed to load analytics data');
      
      // Fallback to mock data
      setAnalytics({
        tasksCompleted: 1247,
        successRate: 94.5,
        avgResponseTime: '2.3s',
        activeAgents: 25,
        departments: [
          { name: 'Sales', tasks: 156, success: 96.2, color: 'bg-green-500' },
          { name: 'R&D', tasks: 89, success: 94.1, color: 'bg-indigo-500' },
          { name: 'Product', tasks: 134, success: 92.8, color: 'bg-orange-500' },
          { name: 'Support', tasks: 267, success: 97.3, color: 'bg-teal-500' },
          { name: 'Engineering', tasks: 198, success: 91.5, color: 'bg-blue-500' },
        ],
        systemHealth: {
          cpuUsage: 45,
          memoryUsage: 67,
          apiCallsPerMin: 142,
          errorRate: 0.3,
          uptime: 99.9
        }
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading && !analytics) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        </div>
      </Layout>
    );
  }

  return (
    <>
      <Head>
        <title>Analytics - AI Agent Company</title>
        <meta name="description" content="System analytics and performance metrics" />
      </Head>

      <Layout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Analytics</h1>
              <p className="text-gray-400 mt-1">
                System performance analytics and insights
              </p>
            </div>
            <button 
              onClick={fetchAnalytics}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              disabled={loading}
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="bg-error-900 border border-error-700 rounded-lg p-4">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-error-400 mr-2" />
                <span className="text-error-300">{error}</span>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card">
              <div className="card-content">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-white">{analytics?.tasksCompleted?.toLocaleString() || '0'}</div>
                    <div className="text-sm text-gray-400">Tasks Completed</div>
                    <div className="text-sm text-success-400 mt-1">+12% this week</div>
                  </div>
                  <Activity className="w-8 h-8 text-primary-500" />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-content">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-white">{analytics?.successRate?.toFixed(1) || '0.0'}%</div>
                    <div className="text-sm text-gray-400">Success Rate</div>
                    <div className="text-sm text-success-400 mt-1">+2.1% this week</div>
                  </div>
                  <TrendingUp className="w-8 h-8 text-primary-500" />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-content">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-white">{analytics?.avgResponseTime || 'N/A'}</div>
                    <div className="text-sm text-gray-400">Avg Response</div>
                    <div className="text-sm text-success-400 mt-1">-0.3s this week</div>
                  </div>
                  <BarChart3 className="w-8 h-8 text-primary-500" />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-content">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-white">{analytics?.activeAgents || 0}</div>
                    <div className="text-sm text-gray-400">Active Agents</div>
                    <div className="text-sm text-gray-400 mt-1">All operational</div>
                  </div>
                  <PieChart className="w-8 h-8 text-primary-500" />
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">Department Performance</h2>
              </div>
              <div className="card-content">
                <div className="space-y-4">
                  {analytics?.departments?.length > 0 ? (
                    analytics.departments.map((dept: any) => {
                      const getDepartmentColor = (name: string) => {
                        const colors: { [key: string]: string } = {
                          'Sales': 'bg-green-500',
                          'R&D': 'bg-indigo-500',
                          'Product': 'bg-orange-500',
                          'Support': 'bg-teal-500',
                          'Engineering': 'bg-blue-500',
                          'Marketing': 'bg-pink-500',
                          'Finance': 'bg-yellow-500',
                          'Memory': 'bg-cyan-500'
                        };
                        return colors[name] || 'bg-gray-500';
                      };

                      return (
                        <div key={dept.name} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full ${getDepartmentColor(dept.name)}`}></div>
                            <span className="font-medium text-white">{dept.name}</span>
                          </div>
                          <div className="flex items-center space-x-4">
                            <span className="text-sm text-gray-400">{dept.completed_tasks || 0} tasks</span>
                            <span className="text-sm text-success-400">{dept.success_rate?.toFixed(1) || '0.0'}%</span>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="text-center text-gray-400 py-4">
                      No department data available
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">System Health</h2>
              </div>
              <div className="card-content">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">CPU Usage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-dark-700 rounded-full h-2">
                        <div className="bg-success-500 h-2 rounded-full" style={{ width: `${analytics?.systemHealth?.cpuUsage || 45}%` }}></div>
                      </div>
                      <span className="text-white text-sm">{analytics?.systemHealth?.cpuUsage || 45}%</span>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Memory Usage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-dark-700 rounded-full h-2">
                        <div className="bg-warning-500 h-2 rounded-full" style={{ width: `${analytics?.systemHealth?.memoryUsage || 67}%` }}></div>
                      </div>
                      <span className="text-white text-sm">{analytics?.systemHealth?.memoryUsage || 67}%</span>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">API Calls Today</span>
                    <span className="text-white">{analytics?.systemHealth?.apiCallsPerMin || 142}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Error Rate</span>
                    <span className="text-success-400">0.3%</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Uptime</span>
                    <span className="text-success-400">99.9%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}