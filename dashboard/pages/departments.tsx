import { useState, useEffect } from 'react';
import Head from 'next/head';
import { Briefcase, Users, Activity, TrendingUp, AlertCircle } from 'lucide-react';
import Layout from '../components/Layout';
import { apiClient } from '../lib/api';

interface Department {
  name: string;
  agents: any[];
  active_agents: number;
  total_agents: number;
  active_tasks: number;
  completed_tasks: number;
  success_rate: number;
  capabilities: string[];
}

export default function DepartmentsPage() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDepartments();
  }, []);

  const fetchDepartments = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/departments');
      setDepartments(response.data.departments);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch departments:', err);
      setError('Failed to load departments. Please check if the API server is running.');
      setDepartments([]);
    } finally {
      setLoading(false);
    }
  };

  const getDepartmentColor = (departmentName: string) => {
    const colors: { [key: string]: string } = {
      'Sales': 'bg-green-600',
      'R&D': 'bg-indigo-600', 
      'Product': 'bg-orange-600',
      'Support': 'bg-teal-600',
      'Engineering': 'bg-blue-600',
      'Marketing': 'bg-pink-600',
      'Finance': 'bg-yellow-600',
      'Executive': 'bg-purple-600',
      'Memory': 'bg-cyan-600'
    };
    return colors[departmentName] || 'bg-gray-600';
  };

  const getDepartmentDescription = (departmentName: string) => {
    const descriptions: { [key: string]: string } = {
      'Sales': 'Lead generation and customer outreach',
      'R&D': 'Research and innovation analysis', 
      'Product': 'Product strategy and roadmap development',
      'Support': 'Customer support and ticket management',
      'Engineering': 'Software development and architecture',
      'Marketing': 'Marketing campaigns and content strategy',
      'Finance': 'Financial analysis and reporting',
      'Executive': 'Strategic planning and coordination',
      'Memory': 'Centralized memory and knowledge management'
    };
    return descriptions[departmentName] || 'Department operations and management';
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
        <title>Departments - AI Agent Company</title>
        <meta name="description" content="Department overview and management" />
      </Head>

      <Layout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-white">Departments</h1>
            <p className="text-gray-400 mt-1">
              Overview of all departments and their performance
            </p>
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

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {departments.map((dept) => (
              <div key={dept.name} className="card">
                <div className="card-content">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full ${getDepartmentColor(dept.name)}`}></div>
                      <div>
                        <h3 className="font-semibold text-white">{dept.name}</h3>
                        <p className="text-sm text-gray-400">{getDepartmentDescription(dept.name)}</p>
                      </div>
                    </div>
                    <Briefcase className="w-5 h-5 text-gray-400" />
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center p-3 bg-dark-700 rounded-lg">
                      <div className="flex items-center justify-center mb-1">
                        <Users className="w-4 h-4 text-primary-400 mr-1" />
                        <span className="text-lg font-bold text-white">{dept.total_agents}</span>
                      </div>
                      <div className="text-xs text-gray-400">Agents</div>
                    </div>
                    
                    <div className="text-center p-3 bg-dark-700 rounded-lg">
                      <div className="flex items-center justify-center mb-1">
                        <Activity className="w-4 h-4 text-warning-400 mr-1" />
                        <span className="text-lg font-bold text-white">{dept.active_tasks}</span>
                      </div>
                      <div className="text-xs text-gray-400">Active</div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Completed Tasks</span>
                      <span className="text-sm text-white font-medium">{dept.completed_tasks}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Success Rate</span>
                      <div className="flex items-center space-x-1">
                        <TrendingUp className="w-3 h-3 text-success-400" />
                        <span className="text-sm text-success-400 font-medium">{dept.success_rate.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-medium text-white mb-2">Key Capabilities</h4>
                    <div className="space-y-1">
                      {dept.capabilities.length > 0 ? (
                        dept.capabilities.map((capability, index) => (
                          <div key={index} className="text-xs text-gray-300 bg-dark-700 px-2 py-1 rounded">
                            {capability}
                          </div>
                        ))
                      ) : (
                        <div className="text-xs text-gray-400 italic">No capabilities defined</div>
                      )}
                    </div>
                  </div>

                  {/* Show agents in department */}
                  <div className="mt-4 pt-4 border-t border-dark-700">
                    <h4 className="text-sm font-medium text-white mb-2">Agents ({dept.active_agents}/{dept.total_agents} active)</h4>
                    <div className="space-y-1">
                      {dept.agents.slice(0, 3).map((agent, index) => (
                        <div key={index} className="flex items-center justify-between text-xs">
                          <span className="text-gray-300">{agent.name}</span>
                          <span className={`px-1 py-0.5 rounded text-xs ${
                            agent.status === 'active' ? 'bg-success-900 text-success-300' : 'bg-error-900 text-error-300'
                          }`}>
                            {agent.status}
                          </span>
                        </div>
                      ))}
                      {dept.agents.length > 3 && (
                        <div className="text-xs text-gray-400 italic">
                          +{dept.agents.length - 3} more agents
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {departments.length === 0 && !loading && (
            <div className="text-center py-12">
              <Briefcase className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">No Departments Found</h3>
              <p className="text-gray-400">No departments are currently available.</p>
            </div>
          )}

          {departments.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">Department Performance Summary</h2>
              </div>
              <div className="card-content">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white mb-1">
                      {departments.reduce((sum, dept) => sum + dept.total_agents, 0)}
                    </div>
                    <div className="text-sm text-gray-400">Total Agents</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white mb-1">
                      {departments.reduce((sum, dept) => sum + dept.active_tasks, 0)}
                    </div>
                    <div className="text-sm text-gray-400">Active Tasks</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white mb-1">
                      {departments.reduce((sum, dept) => sum + dept.completed_tasks, 0)}
                    </div>
                    <div className="text-sm text-gray-400">Completed Tasks</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-3xl font-bold text-success-400 mb-1">
                      {departments.length > 0 ? 
                        (departments.reduce((sum, dept) => sum + dept.success_rate, 0) / departments.length).toFixed(1) : 
                        '0.0'
                      }%
                    </div>
                    <div className="text-sm text-gray-400">Avg Success Rate</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}