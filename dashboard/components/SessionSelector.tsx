import React, { useState, useEffect } from 'react';
import { Calendar, Folder, Users, FileText, Clock, Archive } from 'lucide-react';

interface Session {
  id: string;
  mode: string;
  project_name?: string;
  created_at: string;
  status: string;
  file_count: number;
  total_size: number;
  departments_involved: string[];
}

interface SessionSelectorProps {
  currentSessionId?: string;
  onSessionSelect: (sessionId: string) => void;
  onNewSession?: () => void;
}

const SessionSelector: React.FC<SessionSelectorProps> = ({
  currentSessionId,
  onSessionSelect,
  onNewSession
}) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'persistent' | 'oneshot'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'completed' | 'archived'>('all');

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/sessions');
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <div className="w-2 h-2 bg-green-500 rounded-full"></div>;
      case 'completed':
        return <div className="w-2 h-2 bg-blue-500 rounded-full"></div>;
      case 'archived':
        return <Archive className="w-4 h-4 text-gray-400" />;
      default:
        return <div className="w-2 h-2 bg-gray-400 rounded-full"></div>;
    }
  };

  const getModeIcon = (mode: string) => {
    return mode === 'oneshot' ? 
      <Folder className="w-4 h-4 text-purple-500" /> : 
      <Calendar className="w-4 h-4 text-blue-500" />;
  };

  const filteredSessions = sessions.filter(session => {
    const modeMatch = filter === 'all' || session.mode === filter;
    const statusMatch = statusFilter === 'all' || session.status === statusFilter;
    return modeMatch && statusMatch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600">Loading sessions...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h3 className="text-lg font-semibold text-gray-900">Sessions</h3>
          
          <div className="flex flex-col sm:flex-row gap-2">
            {/* Mode Filter */}
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as 'all' | 'persistent' | 'oneshot')}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Modes</option>
              <option value="persistent">Persistent</option>
              <option value="oneshot">One-shot</option>
            </select>
            
            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as 'all' | 'active' | 'completed' | 'archived')}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
            </select>
            
            {onNewSession && (
              <button
                onClick={onNewSession}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm"
              >
                New Session
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="p-4">
        {filteredSessions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No sessions found</p>
            <p className="text-sm">Sessions will appear here when you run the company</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredSessions.map((session) => (
              <div
                key={session.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  currentSessionId === session.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
                onClick={() => onSessionSelect(session.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      {getModeIcon(session.mode)}
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {session.project_name || `Session ${session.id.slice(0, 8)}`}
                      </h4>
                      {getStatusIcon(session.status)}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>{formatDate(session.created_at)}</span>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        <FileText className="w-3 h-3" />
                        <span>{session.file_count} files ({formatFileSize(session.total_size)})</span>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        <Users className="w-3 h-3" />
                        <span>{session.departments_involved.length} departments</span>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          session.mode === 'oneshot' 
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {session.mode}
                        </span>
                      </div>
                    </div>
                    
                    {session.departments_involved.length > 0 && (
                      <div className="mt-2">
                        <div className="flex flex-wrap gap-1">
                          {session.departments_involved.slice(0, 3).map((dept) => (
                            <span
                              key={dept}
                              className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                            >
                              {dept}
                            </span>
                          ))}
                          {session.departments_involved.length > 3 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                              +{session.departments_involved.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="ml-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      session.status === 'active' 
                        ? 'bg-green-100 text-green-800'
                        : session.status === 'completed'
                        ? 'bg-blue-100 text-blue-800'
                        : session.status === 'archived'
                        ? 'bg-gray-100 text-gray-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {session.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {filteredSessions.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 text-sm text-gray-600">
          Showing {filteredSessions.length} of {sessions.length} sessions
        </div>
      )}
    </div>
  );
};

export default SessionSelector;