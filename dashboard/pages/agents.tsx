import { useState, useEffect } from 'react';
import Head from 'next/head';
import { Users, Activity, CheckCircle, AlertCircle } from 'lucide-react';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api';

interface Agent {
  name: string;
  role: string;
  department: string;
  status: string;
  capabilities: string[];
  current_task?: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/agents');
      setAgents(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch agents:', err);
      setError('Failed to load agents. Please check if the API server is running.');
      setAgents([]); // Clear agents on error
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-success-500';
      case 'busy':
        return 'bg-warning-500';
      case 'idle':
        return 'bg-gray-500';
      case 'error':
        return 'bg-error-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getDepartmentColor = (department: string) => {
    const colors = {
      'Executive': 'bg-purple-600',
      'Engineering': 'bg-blue-600',
      'Sales': 'bg-green-600',
      'Marketing': 'bg-pink-600',
      'Finance': 'bg-yellow-600',
      'R&D': 'bg-indigo-600',
      'Product': 'bg-orange-600',
      'Support': 'bg-teal-600',
    };
    return colors[department as keyof typeof colors] || 'bg-gray-600';
  };

  if (loading) {
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
        <title>Agents - AI Agent Company</title>
        <meta name="description" content="Manage and monitor AI agents" />
      </Head>

      <Layout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Agents</h1>
              <p className="text-gray-400 mt-1">
                Monitor and manage your AI agents across all departments
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-400">
                Total Agents: {agents.length}
              </div>
            </div>
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

          {/* Agents Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent, index) => (
              <div key={index} className="card">
                <div className="card-content">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full ${getStatusColor(agent.status)}`}></div>
                      <div>
                        <h3 className="font-semibold text-white">{agent.name}</h3>
                        <p className="text-sm text-gray-400">{agent.role}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs text-white ${getDepartmentColor(agent.department)}`}>
                      {agent.department}
                    </span>
                  </div>

                  {agent.current_task && (
                    <div className="mb-4 p-3 bg-dark-700 rounded-lg">
                      <div className="flex items-center space-x-2 mb-1">
                        <Activity className="w-4 h-4 text-primary-400" />
                        <span className="text-sm font-medium text-white">Current Task</span>
                      </div>
                      <p className="text-sm text-gray-300">{agent.current_task}</p>
                    </div>
                  )}

                  <div>
                    <h4 className="text-sm font-medium text-white mb-2">Capabilities</h4>
                    <div className="space-y-1">
                      {agent.capabilities.map((capability, capIndex) => (
                        <div key={capIndex} className="flex items-center space-x-2">
                          <CheckCircle className="w-3 h-3 text-success-400" />
                          <span className="text-xs text-gray-300">{capability}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-dark-700">
                    <div className={`status-badge ${
                      agent.status === 'active' ? 'status-active' : 
                      agent.status === 'error' ? 'status-error' : 
                      'status-inactive'
                    }`}>
                      {agent.status}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {agents.length === 0 && !loading && (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">No Agents Found</h3>
              <p className="text-gray-400">No agents are currently available.</p>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}