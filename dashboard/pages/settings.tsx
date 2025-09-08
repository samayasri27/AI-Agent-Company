import { useState, useEffect } from 'react';
import Head from 'next/head';
import { Settings, Save, RefreshCw, Shield, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import Layout from '../components/Layout';
import { configAPI } from '../lib/api';

export default function SettingsPage() {
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showPasswords, setShowPasswords] = useState<{[key: string]: boolean}>({});
  
  const [formData, setFormData] = useState({
    groq_api_key_1: '',
    groq_api_key_2: '',
    supabase_url: '',
    supabase_anon_key: '',
    supabase_service_key: '',
    github_token: '',
    stripe_api_key: '',
    hubspot_api_key: '',
    google_search_api_key: '',
    api_base_url: 'http://localhost:8000',
    refresh_interval: 30,
    theme: 'dark',
    debug_mode: false,
    auto_logout: true,
    notifications: true
  });

  useEffect(() => {
    fetchCurrentConfig();
  }, []);

  const fetchCurrentConfig = async () => {
    try {
      setLoading(true);
      
      // Get both config and company info
      const [currentConfig, companyInfo] = await Promise.all([
        configAPI.getCurrentConfig(),
        apiClient.get('/company/info').catch(() => ({ data: null }))
      ]);
      
      // Combine config with company info
      const combinedConfig = {
        ...currentConfig,
        company_info: companyInfo.data
      };
      
      setConfig(combinedConfig);
      
      // Update form data with current config
      setFormData(prev => ({
        ...prev,
        api_base_url: currentConfig.api_settings?.base_url || 'http://localhost:8000',
        debug_mode: currentConfig.system_settings?.debug_mode || false,
        // Don't populate API keys for security
      }));
      
      setError(null);
    } catch (err) {
      console.error('Failed to fetch config:', err);
      setError('Failed to load current configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      // Filter out empty API keys
      const configToSave = Object.entries(formData).reduce((acc, [key, value]) => {
        if (key.includes('api_key') || key.includes('token') || key.includes('url')) {
          if (value && typeof value === 'string' && value.trim() !== '') {
            acc[key] = value;
          }
        } else {
          acc[key] = value;
        }
        return acc;
      }, {} as any);

      const result = await configAPI.updateConfig(configToSave);
      
      if (result.success) {
        setSuccess('Configuration updated successfully');
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(result.error || 'Failed to update configuration');
      }
    } catch (err) {
      console.error('Failed to save config:', err);
      setError('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const togglePasswordVisibility = (field: string) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
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
        <title>Settings - AI Agent Company</title>
        <meta name="description" content="System settings and configuration" />
      </Head>

      <Layout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-white">Settings</h1>
            <p className="text-gray-400 mt-1">
              Configure API keys, system settings, and preferences
            </p>
          </div>

          {/* Success/Error Messages */}
          {success && (
            <div className="bg-success-900 border border-success-700 rounded-lg p-4">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-success-400 mr-2" />
                <span className="text-success-300">{success}</span>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-error-900 border border-error-700 rounded-lg p-4">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-error-400 mr-2" />
                <span className="text-error-300">{error}</span>
              </div>
            </div>
          )}

          {/* API Keys Configuration */}
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-white flex items-center">
                <Shield className="w-5 h-5 mr-2" />
                API Keys Configuration
              </h2>
            </div>
            <div className="card-content">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Core System APIs */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-white border-b border-dark-700 pb-2">Core System</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Groq API Key (Primary)
                      <span className={`ml-2 text-xs ${config?.integration_settings?.groq_api_configured ? 'text-success-400' : 'text-error-400'}`}>
                        {config?.integration_settings?.groq_api_configured ? '✓ Configured' : '✗ Not configured'}
                      </span>
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type={showPasswords.groq_api_key_1 ? "text" : "password"}
                        placeholder="gsk_..."
                        value={formData.groq_api_key_1}
                        onChange={(e) => handleInputChange('groq_api_key_1', e.target.value)}
                        className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('groq_api_key_1')}
                        className="btn btn-secondary"
                      >
                        {showPasswords.groq_api_key_1 ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Groq API Key (Backup)
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type={showPasswords.groq_api_key_2 ? "text" : "password"}
                        placeholder="gsk_..."
                        value={formData.groq_api_key_2}
                        onChange={(e) => handleInputChange('groq_api_key_2', e.target.value)}
                        className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('groq_api_key_2')}
                        className="btn btn-secondary"
                      >
                        {showPasswords.groq_api_key_2 ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Supabase URL
                      <span className={`ml-2 text-xs ${config?.integration_settings?.supabase_configured ? 'text-success-400' : 'text-error-400'}`}>
                        {config?.integration_settings?.supabase_configured ? '✓ Configured' : '✗ Not configured'}
                      </span>
                    </label>
                    <input
                      type="text"
                      placeholder="https://your-project.supabase.co"
                      value={formData.supabase_url}
                      onChange={(e) => handleInputChange('supabase_url', e.target.value)}
                      className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Supabase Anon Key
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type={showPasswords.supabase_anon_key ? "text" : "password"}
                        placeholder="eyJ..."
                        value={formData.supabase_anon_key}
                        onChange={(e) => handleInputChange('supabase_anon_key', e.target.value)}
                        className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('supabase_anon_key')}
                        className="btn btn-secondary"
                      >
                        {showPasswords.supabase_anon_key ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* External Integrations */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-white border-b border-dark-700 pb-2">External Integrations</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      GitHub Token
                      <span className={`ml-2 text-xs ${config?.integration_settings?.github_configured ? 'text-success-400' : 'text-error-400'}`}>
                        {config?.integration_settings?.github_configured ? '✓ Configured' : '✗ Not configured'}
                      </span>
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type={showPasswords.github_token ? "text" : "password"}
                        placeholder="ghp_..."
                        value={formData.github_token}
                        onChange={(e) => handleInputChange('github_token', e.target.value)}
                        className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('github_token')}
                        className="btn btn-secondary"
                      >
                        {showPasswords.github_token ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Stripe API Key
                      <span className={`ml-2 text-xs ${config?.integration_settings?.stripe_configured ? 'text-success-400' : 'text-error-400'}`}>
                        {config?.integration_settings?.stripe_configured ? '✓ Configured' : '✗ Not configured'}
                      </span>
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type={showPasswords.stripe_api_key ? "text" : "password"}
                        placeholder="sk_..."
                        value={formData.stripe_api_key}
                        onChange={(e) => handleInputChange('stripe_api_key', e.target.value)}
                        className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('stripe_api_key')}
                        className="btn btn-secondary"
                      >
                        {showPasswords.stripe_api_key ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      HubSpot API Key
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type={showPasswords.hubspot_api_key ? "text" : "password"}
                        placeholder="pat-..."
                        value={formData.hubspot_api_key}
                        onChange={(e) => handleInputChange('hubspot_api_key', e.target.value)}
                        className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('hubspot_api_key')}
                        className="btn btn-secondary"
                      >
                        {showPasswords.hubspot_api_key ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Google Search API Key
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type={showPasswords.google_search_api_key ? "text" : "password"}
                        placeholder="AIza..."
                        value={formData.google_search_api_key}
                        onChange={(e) => handleInputChange('google_search_api_key', e.target.value)}
                        className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('google_search_api_key')}
                        className="btn btn-secondary"
                      >
                        {showPasswords.google_search_api_key ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* System Configuration */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white flex items-center">
                  <Settings className="w-5 h-5 mr-2" />
                  System Configuration
                </h2>
              </div>
              <div className="card-content space-y-4">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    API Base URL
                  </label>
                  <input
                    type="text"
                    value={formData.api_base_url}
                    onChange={(e) => handleInputChange('api_base_url', e.target.value)}
                    className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Refresh Interval (seconds)
                  </label>
                  <input
                    type="number"
                    value={formData.refresh_interval}
                    onChange={(e) => handleInputChange('refresh_interval', parseInt(e.target.value))}
                    className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Theme
                  </label>
                  <select 
                    value={formData.theme}
                    onChange={(e) => handleInputChange('theme', e.target.value)}
                    className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                    <option value="auto">Auto</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">Preferences</h2>
              </div>
              <div className="card-content space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white">Auto-logout after inactivity</span>
                  <input 
                    type="checkbox" 
                    checked={formData.auto_logout}
                    onChange={(e) => handleInputChange('auto_logout', e.target.checked)}
                    className="rounded" 
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white">Enable notifications</span>
                  <input 
                    type="checkbox" 
                    checked={formData.notifications}
                    onChange={(e) => handleInputChange('notifications', e.target.checked)}
                    className="rounded" 
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white">Debug mode</span>
                  <input 
                    type="checkbox" 
                    checked={formData.debug_mode}
                    onChange={(e) => handleInputChange('debug_mode', e.target.checked)}
                    className="rounded" 
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button 
              onClick={handleSave}
              disabled={saving}
              className="btn btn-primary flex items-center space-x-2"
            >
              {saving ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
            </button>
          </div>

          {/* Company Information */}
          {config && (
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">Company Information</h2>
              </div>
              <div className="card-content">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-sm font-medium text-white mb-2">Company Profile</h3>
                    <div className="space-y-1 text-sm text-gray-400">
                      <div>Name: {config.company_info?.company_name || 'Not set'}</div>
                      <div>Description: {config.company_info?.description || 'Not set'}</div>
                      <div>Status: {config.company_info?.status || 'Unknown'}</div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-white mb-2">System Metrics</h3>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Total Agents</span>
                        <span className="text-white">{config.company_info?.total_agents || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Active Agents</span>
                        <span className="text-success-400">{config.company_info?.active_agents || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Success Rate</span>
                        <span className="text-success-400">{config.company_info?.success_rate || 0}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-white">System Information</h2>
            </div>
            <div className="card-content">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-white mb-2">Version Information</h3>
                  <div className="space-y-1 text-sm text-gray-400">
                    <div>Dashboard: v1.0.0</div>
                    <div>API Gateway: v1.0.0</div>
                    <div>Core System: v1.0.0</div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-white mb-2">System Status</h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">API Server</span>
                      <span className={config ? "text-success-400" : "text-error-400"}>
                        {config ? "Online" : "Offline"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Memory System</span>
                      <span className="text-success-400">Connected</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Agents</span>
                      <span className="text-success-400">
                        {config?.company_info?.active_agents || 0} Active
                      </span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-white mb-2">Performance</h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Uptime</span>
                      <span className="text-white">{config?.company_info?.uptime || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Response Time</span>
                      <span className="text-white">
                        {config?.company_info?.performance_metrics?.avg_response_time || 'Unknown'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Success Rate</span>
                      <span className="text-success-400">
                        {config?.company_info?.success_rate || 0}%
                      </span>
                    </div>
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