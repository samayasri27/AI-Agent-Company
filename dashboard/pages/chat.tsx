import { useState, useEffect } from 'react';
import Head from 'next/head';
import { MessageSquare, Send, Bot, User, RefreshCw, AlertCircle } from 'lucide-react';
import Layout from '../components/Layout';
import { systemAPI, taskAPI } from '../lib/api';

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: string;
  agent?: string;
}

export default function ChatPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'agent',
      content: 'Hello! I\'m here to help you with your AI Agent Company. How can I assist you today?',
      timestamp: new Date().toISOString(),
      agent: 'System'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      
      // Try to get agents from multiple sources
      let agentsData = [];
      
      try {
        // First try dashboard data
        const dashboardData = await systemAPI.getDashboardData();
        agentsData = dashboardData.agents || [];
        
        // If no agents from dashboard, try direct agents endpoint
        if (agentsData.length === 0) {
          const directAgents = await agentAPI.listAgents();
          agentsData = directAgents || [];
        }
        
        // Ensure we have website agent
        const hasWebsiteAgent = agentsData.some(agent => agent.department === 'Website');
        if (!hasWebsiteAgent) {
          agentsData.push({
            name: 'Website Manager',
            role: 'Website Data Manager',
            department: 'Website',
            status: 'active',
            capabilities: [
              'Real-time data synchronization',
              'Dashboard data management',
              'API data validation',
              'Error monitoring and resolution'
            ],
            current_task: 'Managing website data and real-time updates'
          });
        }
        
      } catch (apiError) {
        console.warn('API failed, using fallback agents:', apiError);
        // Fallback to basic agent list
        agentsData = [
          {
            name: 'Sales Agent',
            role: 'Lead Generation Specialist',
            department: 'Sales',
            status: 'active',
            capabilities: ['Lead generation', 'Customer outreach', 'Sales analysis']
          },
          {
            name: 'Marketing Agent',
            role: 'Campaign & Content Strategy',
            department: 'Marketing',
            status: 'active',
            capabilities: ['Content creation', 'Campaign management', 'Social media']
          },
          {
            name: 'Product Agent',
            role: 'Product Strategy Lead',
            department: 'Product',
            status: 'active',
            capabilities: ['Product planning', 'Feature analysis', 'Roadmap development']
          },
          {
            name: 'Support Agent',
            role: 'Customer Support Lead',
            department: 'Support',
            status: 'active',
            capabilities: ['Customer support', 'Issue resolution', 'Documentation']
          },
          {
            name: 'Website Manager',
            role: 'Website Data Manager',
            department: 'Website',
            status: 'active',
            capabilities: ['Real-time data sync', 'Dashboard management', 'Error monitoring']
          }
        ];
      }
      
      setAgents(agentsData);
      setError(null);
      
    } catch (err) {
      console.error('Failed to fetch agents:', err);
      setError('Failed to load agents data. Using fallback data.');
      
      // Set minimal fallback agents
      setAgents([
        {
          name: 'System Agent',
          role: 'System Manager',
          department: 'System',
          status: 'active',
          capabilities: ['System management', 'Task processing']
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || sending) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage('');
    setSending(true);

    try {
      // Submit as a task to get a real response
      const result = await taskAPI.submitTask({
        task_description: messageToSend,
        task_type: 'chat',
        priority: 'medium'
      });

      // Simulate agent response
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: `Task "${messageToSend}" has been submitted with ID ${result.task_id}. I'll process this and get back to you with results.`,
        timestamp: new Date().toISOString(),
        agent: 'System Agent'
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (err) {
      console.error('Failed to send message:', err);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: 'I apologize, but I\'m having trouble processing your request right now. Please try again later.',
        timestamp: new Date().toISOString(),
        agent: 'System'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setSending(false);
    }
  };

  const handleQuickAction = (action: string) => {
    setInputMessage(action);
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <>
      <Head>
        <title>Chat - AI Agent Company</title>
        <meta name="description" content="Chat with AI agents" />
      </Head>

      <Layout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Agent Chat</h1>
              <p className="text-gray-400 mt-1">
                Communicate directly with AI agents
              </p>
            </div>
            <button 
              onClick={fetchAgents}
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

          <div className="card h-96">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-white flex items-center">
                <MessageSquare className="w-5 h-5 mr-2" />
                Chat Interface
              </h2>
            </div>
            <div className="card-content flex flex-col h-full">
              <div className="flex-1 space-y-4 mb-4 overflow-y-auto max-h-80">
                {messages.map((message) => (
                  <div key={message.id} className={`flex items-start space-x-3 ${
                    message.type === 'user' ? 'justify-end' : ''
                  }`}>
                    {message.type === 'agent' && (
                      <Bot className="w-6 h-6 text-primary-500 mt-1" />
                    )}
                    <div className={`rounded-lg p-3 max-w-md ${
                      message.type === 'user' 
                        ? 'bg-primary-600' 
                        : 'bg-dark-700'
                    }`}>
                      <p className="text-white text-sm">{message.content}</p>
                      <div className="text-xs text-gray-400 mt-1">
                        {message.agent && `${message.agent} • `}
                        {formatTime(message.timestamp)}
                      </div>
                    </div>
                    {message.type === 'user' && (
                      <User className="w-6 h-6 text-gray-400 mt-1" />
                    )}
                  </div>
                ))}
                {sending && (
                  <div className="flex items-start space-x-3">
                    <Bot className="w-6 h-6 text-primary-500 mt-1" />
                    <div className="bg-dark-700 rounded-lg p-3 max-w-md">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-500"></div>
                        <span className="text-white text-sm">Processing...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex space-x-2">
                <input
                  type="text"
                  placeholder="Type your message..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                  className="flex-1 px-4 py-2 bg-dark-700 border border-dark-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  disabled={sending}
                />
                <button 
                  onClick={sendMessage}
                  disabled={sending || !inputMessage.trim()}
                  className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {sending ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-white">Available Agents</h3>
              </div>
              <div className="card-content">
                <div className="space-y-2">
                  {agents.length > 0 ? (
                    agents.map((agent, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-dark-700 rounded">
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            agent.status === 'active' ? 'bg-success-500' : 'bg-warning-500'
                          }`}></div>
                          <span className="text-white text-sm">{agent.name}</span>
                        </div>
                        <span className="text-xs text-gray-400">{agent.department}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-gray-400 py-4">
                      {loading ? 'Loading agents...' : 'No agents available'}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-white">Quick Actions</h3>
              </div>
              <div className="card-content">
                <div className="space-y-2">
                  <button 
                    onClick={() => handleQuickAction('What is the current system status?')}
                    className="w-full text-left p-2 bg-dark-700 hover:bg-dark-600 rounded text-white text-sm transition-colors"
                  >
                    Ask for system status
                  </button>
                  <button 
                    onClick={() => handleQuickAction('Can you provide a summary of recent tasks?')}
                    className="w-full text-left p-2 bg-dark-700 hover:bg-dark-600 rounded text-white text-sm transition-colors"
                  >
                    Request task summary
                  </button>
                  <button 
                    onClick={() => handleQuickAction('Show me the current performance metrics')}
                    className="w-full text-left p-2 bg-dark-700 hover:bg-dark-600 rounded text-white text-sm transition-colors"
                  >
                    Get performance metrics
                  </button>
                  <button 
                    onClick={() => handleQuickAction('Generate sales leads for our company')}
                    className="w-full text-left p-2 bg-dark-700 hover:bg-dark-600 rounded text-white text-sm transition-colors"
                  >
                    Submit new task
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}