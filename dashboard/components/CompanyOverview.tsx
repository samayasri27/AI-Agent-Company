import { Building2, Users, Activity, TrendingUp, Clock, CheckCircle } from 'lucide-react';

interface Department {
  name: string;
  agent_count: number;
  active_agents: number;
  current_tasks: Array<{
    agent: string;
    task: string;
  }>;
}

interface CompanyInfo {
  company_name: string;
  description: string;
  status: string;
  uptime: string;
  departments: Department[];
  total_agents: number;
  active_agents: number;
  task_statistics: {
    total_tasks: number;
    completed_tasks: number;
    in_progress_tasks: number;
    queued_tasks: number;
    failed_tasks: number;
  };
  success_rate: number;
  performance_metrics: {
    avg_response_time: string;
    system_load: string;
    memory_usage: string;
    api_calls_today: number;
  };
}

interface CompanyOverviewProps {
  companyInfo: CompanyInfo;
}

export default function CompanyOverview({ companyInfo }: CompanyOverviewProps) {
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

  return (
    <div className="space-y-6">
      {/* Company Header */}
      <div className="card">
        <div className="card-content">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <Building2 className="w-12 h-12 text-primary-500" />
              <div>
                <h1 className="text-2xl font-bold text-white">{companyInfo.company_name}</h1>
                <p className="text-gray-400 mt-1">{companyInfo.description}</p>
                <div className="flex items-center space-x-4 mt-2">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${
                      companyInfo.status === 'operational' ? 'bg-success-500' : 'bg-error-500'
                    }`}></div>
                    <span className="text-sm text-gray-300 capitalize">{companyInfo.status}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-300">Uptime: {companyInfo.uptime}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-3xl font-bold text-success-400">{companyInfo.success_rate}%</div>
              <div className="text-sm text-gray-400">Success Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-white">{companyInfo.total_agents}</div>
                <div className="text-sm text-gray-400">Total Agents</div>
                <div className="text-sm text-success-400 mt-1">{companyInfo.active_agents} active</div>
              </div>
              <Users className="w-8 h-8 text-primary-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-white">{companyInfo.task_statistics.total_tasks}</div>
                <div className="text-sm text-gray-400">Total Tasks</div>
                <div className="text-sm text-warning-400 mt-1">{companyInfo.task_statistics.in_progress_tasks} running</div>
              </div>
              <Activity className="w-8 h-8 text-primary-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-white">{companyInfo.task_statistics.completed_tasks}</div>
                <div className="text-sm text-gray-400">Completed</div>
                <div className="text-sm text-success-400 mt-1">
                  +{Math.floor(companyInfo.task_statistics.completed_tasks * 0.12)} today
                </div>
              </div>
              <CheckCircle className="w-8 h-8 text-primary-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-white">{companyInfo.performance_metrics.avg_response_time}</div>
                <div className="text-sm text-gray-400">Avg Response</div>
                <div className="text-sm text-success-400 mt-1">-0.3s this week</div>
              </div>
              <TrendingUp className="w-8 h-8 text-primary-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Departments Overview */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-white">Department Operations</h2>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {companyInfo.departments.map((dept, index) => (
              <div key={index} className="bg-dark-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${getDepartmentColor(dept.name)}`}></div>
                    <h3 className="font-semibold text-white">{dept.name}</h3>
                  </div>
                  <div className="text-sm text-gray-400">
                    {dept.active_agents}/{dept.agent_count} active
                  </div>
                </div>
                
                {dept.current_tasks.length > 0 ? (
                  <div className="space-y-2">
                    <div className="text-xs text-gray-400 mb-2">Current Tasks:</div>
                    {dept.current_tasks.slice(0, 2).map((task, taskIndex) => (
                      <div key={taskIndex} className="bg-dark-800 rounded p-2">
                        <div className="text-xs font-medium text-primary-400">{task.agent}</div>
                        <div className="text-xs text-gray-300 truncate">{task.task}</div>
                      </div>
                    ))}
                    {dept.current_tasks.length > 2 && (
                      <div className="text-xs text-gray-400 text-center">
                        +{dept.current_tasks.length - 2} more tasks
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-xs text-gray-500 italic">No active tasks</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* System Performance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-white">Task Distribution</h2>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Completed</span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-dark-700 rounded-full h-2">
                    <div 
                      className="bg-success-500 h-2 rounded-full" 
                      style={{ 
                        width: `${(companyInfo.task_statistics.completed_tasks / companyInfo.task_statistics.total_tasks) * 100}%` 
                      }}
                    ></div>
                  </div>
                  <span className="text-white text-sm">{companyInfo.task_statistics.completed_tasks}</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-400">In Progress</span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-dark-700 rounded-full h-2">
                    <div 
                      className="bg-warning-500 h-2 rounded-full" 
                      style={{ 
                        width: `${(companyInfo.task_statistics.in_progress_tasks / companyInfo.task_statistics.total_tasks) * 100}%` 
                      }}
                    ></div>
                  </div>
                  <span className="text-white text-sm">{companyInfo.task_statistics.in_progress_tasks}</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Queued</span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-dark-700 rounded-full h-2">
                    <div 
                      className="bg-primary-500 h-2 rounded-full" 
                      style={{ 
                        width: `${(companyInfo.task_statistics.queued_tasks / companyInfo.task_statistics.total_tasks) * 100}%` 
                      }}
                    ></div>
                  </div>
                  <span className="text-white text-sm">{companyInfo.task_statistics.queued_tasks}</span>
                </div>
              </div>
              
              {companyInfo.task_statistics.failed_tasks > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Failed</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-dark-700 rounded-full h-2">
                      <div 
                        className="bg-error-500 h-2 rounded-full" 
                        style={{ 
                          width: `${(companyInfo.task_statistics.failed_tasks / companyInfo.task_statistics.total_tasks) * 100}%` 
                        }}
                      ></div>
                    </div>
                    <span className="text-white text-sm">{companyInfo.task_statistics.failed_tasks}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-white">System Performance</h2>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">System Load</span>
                <span className="text-white">{companyInfo.performance_metrics.system_load}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Memory Usage</span>
                <span className="text-white">{companyInfo.performance_metrics.memory_usage}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-400">API Calls Today</span>
                <span className="text-white">{companyInfo.performance_metrics.api_calls_today.toLocaleString()}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Response Time</span>
                <span className="text-success-400">{companyInfo.performance_metrics.avg_response_time}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}