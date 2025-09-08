import { useState } from 'react';
import { Building2, Save, ArrowRight } from 'lucide-react';
import { systemAPI } from '../lib/api';

interface CompanySetupProps {
  onComplete: (companyData: any) => void;
}

export default function CompanySetup({ onComplete }: CompanySetupProps) {
  const [formData, setFormData] = useState({
    company_name: '',
    description: '',
    budget: '',
    sector: '',
    goal: '',
    target_location: 'India'
  });

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Submit company profile to API
      const result = await systemAPI.setupCompany({
        ...formData,
        budget: parseFloat(formData.budget) || 0
      });
      
      onComplete(result);
    } catch (error) {
      console.error('Error setting up company:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="min-h-screen bg-dark-900 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <Building2 className="w-16 h-16 text-primary-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-white mb-2">Setup Your AI Agent Company</h1>
          <p className="text-gray-400">Configure your company profile to get started with autonomous operations</p>
        </div>

        <div className="card">
          <div className="card-content">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.company_name}
                    onChange={(e) => handleInputChange('company_name', e.target.value)}
                    className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Enter your company name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Industry/Sector *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.sector}
                    onChange={(e) => handleInputChange('sector', e.target.value)}
                    className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="e.g., Technology, Healthcare, Finance"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Company Description *
                </label>
                <textarea
                  required
                  rows={3}
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Describe what your company does..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Budget (INR)
                  </label>
                  <input
                    type="number"
                    value={formData.budget}
                    onChange={(e) => handleInputChange('budget', e.target.value)}
                    className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Enter budget amount"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Target Location
                  </label>
                  <select
                    value={formData.target_location}
                    onChange={(e) => handleInputChange('target_location', e.target.value)}
                    className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="India">India</option>
                    <option value="United States">United States</option>
                    <option value="United Kingdom">United Kingdom</option>
                    <option value="Canada">Canada</option>
                    <option value="Australia">Australia</option>
                    <option value="Global">Global</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Primary Goal/Objective *
                </label>
                <textarea
                  required
                  rows={2}
                  value={formData.goal}
                  onChange={(e) => handleInputChange('goal', e.target.value)}
                  className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="What is your company's main goal or objective?"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-primary flex items-center space-x-2"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Setting up...</span>
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      <span>Setup Company</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="mt-6 text-center text-sm text-gray-400">
          <p>Once setup is complete, your AI agents will be initialized and ready to work!</p>
        </div>
      </div>
    </div>
  );
}