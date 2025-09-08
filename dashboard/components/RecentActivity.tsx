import { Clock, CheckCircle, AlertCircle, Play } from 'lucide-react';

interface Task {
  id: string;
  description: string;
  status: string;
  timestamp: string;
}

interface RecentActivityProps {
  tasks: Task[];
}

export default function RecentActivity({ tasks }: RecentActivityProps) {
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-success-400" />;
      case 'in_progress':
        return <Play className="w-4 h-4 text-primary-400" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-error-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch {
      return 'Unknown';
    }
  };

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <div key={task.id} className="flex items-start space-x-3 p-3 bg-dark-700 rounded-lg">
          <div className="flex-shrink-0 mt-1">
            {getStatusIcon(task.status)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-white truncate">
              {task.description}
            </div>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-xs text-gray-400">{task.id}</span>
              <span className="text-xs text-gray-500">•</span>
              <span className="text-xs text-gray-400">{formatTime(task.timestamp)}</span>
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
      ))}
      
      {tasks.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          No recent activity
        </div>
      )}
    </div>
  );
}