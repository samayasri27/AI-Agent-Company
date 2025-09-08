import { useState, useEffect } from 'react';
import Head from 'next/head';
import { Activity, Clock, CheckCircle, AlertCircle, Play, Pause, Plus, Send } from 'lucide-react';
import Layout from '../components/Layout';
import { apiClient, taskAPI } from '../lib/api';

interface Task {
  id: string;
  description: string;
  type: string;
  priority: string;
  department?: string;
  status: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [taskForm, setTaskForm] = useState({
    description: '',
    type: 'general',
    priority: 'medium',
    department: ''
  });

  useEffect(() => {
    fetchTasks();
  }, [filter]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await apiClient.get('/tasks', { params });
      setTasks(response.data.tasks || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      setError('Failed to load tasks. Please check if the API server is running.');
      setTasks([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-success-400" />;
      case 'in_progress':
        return <Play className="w-5 h-5 text-primary-400" />;
      case 'queued':
        return <Clock className="w-5 h-5 text-warning-400" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-error-400" />;
      case 'cancelled':
        return <Pause className="w-5 h-5 text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'text-error-400';
      case 'medium':
        return 'text-warning-400';
      case 'low':
        return 'text-success-400';
      default:
        return 'text-gray-400';
    }
  };

  const getDepartmentColor = (department: string) => {
    const colors = {
      'sales': 'bg-green-600',
      'rnd': 'bg-indigo-600',
      'product': 'bg-orange-600',
      'support': 'bg-teal-600',
      'marketing': 'bg-pink-600',
      'finance': 'bg-yellow-600',
      'engineering': 'bg-blue-600',
    };
    return colors[department as keyof typeof colors] || 'bg-gray-600';
  };

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch {
      return 'Unknown';
    }
  };

  const filteredTasks = tasks.filter(task => 
    filter === 'all' || task.status === filter
  );

  const handleSubmitTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskForm.description.trim()) return;

    try {
      setSubmitting(true);
      const result = await taskAPI.submitTask({
        task_description: taskForm.description,
        task_type: taskForm.type,
        priority: taskForm.priority,
        department: taskForm.department || undefined
      });

      // Reset form and refresh tasks
      setTaskForm({
        description: '',
        type: 'general',
        priority: 'medium',
        department: ''
      });
      setShowTaskForm(false);
      fetchTasks();
      
    } catch (error) {
      console.error('Failed to submit task:', error);
      setError('Failed to submit task');
    } finally {
      setSubmitting(false);
    }
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
        <title>Tasks - AI Agent Company</title>
        <meta name="description" content="Monitor and manage tasks" />
      </Head>

      <Layout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Tasks</h1>
              <p className="text-gray-400 mt-1">
                Monitor task execution and progress across all departments
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-400">
                Total Tasks: {tasks.length}
              </div>
              <button
                onClick={() => setShowTaskForm(!showTaskForm)}
                className="btn btn-primary flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>New Task</span>
              </button>
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

          {/* Task Submission Form */}
          {showTaskForm && (
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">Submit New Task</h2>
              </div>
              <div className="card-content">
                <form onSubmit={handleSubmitTask} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Task Description *
                    </label>
                    <textarea
                      required
                      rows={3}
                      value={taskForm.description}
                      onChange={(e) => setTaskForm(prev => ({ ...prev, description: e.target.value }))}
                      className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Describe the task you want the AI agents to perform..."
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-white mb-2">
                        Task Type
                      </label>
                      <select
                        value={taskForm.type}
                        onChange={(e) => setTaskForm(prev => ({ ...prev, type: e.target.value }))}
                        className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="general">General</option>
                        <option value="research">Research</option>
                        <option value="analysis">Analysis</option>
                        <option value="lead_generation">Lead Generation</option>
                        <option value="product_development">Product Development</option>
                        <option value="customer_support">Customer Support</option>
                        <option value="marketing">Marketing</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-white mb-2">
                        Priority
                      </label>
                      <select
                        value={taskForm.priority}
                        onChange={(e) => setTaskForm(prev => ({ ...prev, priority: e.target.value }))}
                        className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-white mb-2">
                        Department (Optional)
                      </label>
                      <select
                        value={taskForm.department}
                        onChange={(e) => setTaskForm(prev => ({ ...prev, department: e.target.value }))}
                        className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="">Auto-assign</option>
                        <option value="sales">Sales</option>
                        <option value="rnd">R&D</option>
                        <option value="product">Product</option>
                        <option value="support">Support</option>
                        <option value="marketing">Marketing</option>
                        <option value="finance">Finance</option>
                        <option value="engineering">Engineering</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex justify-end space-x-3">
                    <button
                      type="button"
                      onClick={() => setShowTaskForm(false)}
                      className="btn btn-secondary"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={submitting || !taskForm.description.trim()}
                      className="btn btn-primary flex items-center space-x-2"
                    >
                      {submitting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Submitting...</span>
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          <span>Submit Task</span>
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Filters */}
          <div className="flex space-x-2">
            {['all', 'queued', 'in_progress', 'completed', 'failed'].map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  filter === status
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
                }`}
              >
                {status.replace('_', ' ').toUpperCase()}
              </button>
            ))}
          </div>

          {/* Tasks List */}
          <div className="space-y-4">
            {filteredTasks.map((task) => (
              <div key={task.id} className="card">
                <div className="card-content">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="flex-shrink-0 mt-1">
                        {getStatusIcon(task.status)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-semibold text-white truncate">{task.description}</h3>
                          <span className="text-xs text-gray-500">{task.id}</span>
                        </div>
                        
                        <div className="flex items-center space-x-4 mb-3">
                          <span className="text-sm text-gray-400">Type: {task.type}</span>
                          <span className={`text-sm font-medium ${getPriorityColor(task.priority)}`}>
                            {task.priority.toUpperCase()}
                          </span>
                          {task.department && (
                            <span className={`px-2 py-1 rounded text-xs text-white ${getDepartmentColor(task.department)}`}>
                              {task.department}
                            </span>
                          )}
                        </div>

                        {task.status === 'in_progress' && (
                          <div className="mb-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm text-gray-400">Progress</span>
                              <span className="text-sm text-white">{task.progress}%</span>
                            </div>
                            <div className="w-full bg-dark-700 rounded-full h-2">
                              <div 
                                className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${task.progress}%` }}
                              ></div>
                            </div>
                          </div>
                        )}

                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>Created: {formatTime(task.created_at)}</span>
                          <span>Updated: {formatTime(task.updated_at)}</span>
                        </div>
                      </div>
                    </div>

                    <div className={`status-badge ${
                      task.status === 'completed' ? 'status-active' : 
                      task.status === 'failed' ? 'status-error' : 
                      task.status === 'in_progress' ? 'status-warning' :
                      'status-inactive'
                    }`}>
                      {task.status.replace('_', ' ')}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredTasks.length === 0 && !loading && (
            <div className="text-center py-12">
              <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">No Tasks Found</h3>
              <p className="text-gray-400">
                {filter === 'all' ? 'No tasks are currently available.' : `No ${filter} tasks found.`}
              </p>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}