import { useState } from 'react';
import { Bell, Search, User, LogOut, Settings } from 'lucide-react';

export default function Header() {
  const [notifications] = useState(3);

  return (
    <header className="bg-dark-800 border-b border-dark-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search agents, tasks, or memory..."
              className="w-full pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="relative p-2 text-gray-400 hover:text-white transition-colors">
            <Bell className="w-5 h-5" />
            {notifications > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-error-500 text-white text-xs rounded-full flex items-center justify-center">
                {notifications}
              </span>
            )}
          </button>

          {/* User Menu */}
          <div className="relative">
            <button className="flex items-center space-x-2 p-2 text-gray-400 hover:text-white transition-colors">
              <User className="w-5 h-5" />
              <span className="text-sm">Admin</span>
            </button>
          </div>

          {/* Settings */}
          <button className="p-2 text-gray-400 hover:text-white transition-colors">
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
}