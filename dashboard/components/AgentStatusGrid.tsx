interface Agent {
  name: string;
  department: string;
  status: string;
  currentTask?: string;
}

interface AgentStatusGridProps {
  agents: Agent[];
}

export default function AgentStatusGrid({ agents }: AgentStatusGridProps) {
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

  return (
    <div className="space-y-3">
      {agents.map((agent, index) => (
        <div key={index} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)}`}></div>
            <div>
              <div className="font-medium text-white">{agent.name}</div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded text-xs text-white ${getDepartmentColor(agent.department)}`}>
                  {agent.department}
                </span>
                {agent.currentTask && (
                  <span className="text-xs text-gray-400">
                    {agent.currentTask}
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className={`status-badge ${
            agent.status === 'active' ? 'status-active' : 
            agent.status === 'error' ? 'status-error' : 
            'status-inactive'
          }`}>
            {agent.status}
          </div>
        </div>
      ))}
      
      {agents.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          No agents available
        </div>
      )}
    </div>
  );
}