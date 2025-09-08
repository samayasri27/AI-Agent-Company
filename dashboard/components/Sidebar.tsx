import Link from 'next/link';
import { useRouter } from 'next/router';
import { 
  Home, 
  Users, 
  Activity, 
  Database, 
  Settings, 
  BarChart3,
  Brain,
  Briefcase,
  MessageSquare
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Agents', href: '/agents', icon: Users },
  { name: 'Tasks', href: '/tasks', icon: Activity },
  { name: 'Memory', href: '/memory', icon: Database },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Departments', href: '/departments', icon: Briefcase },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const router = useRouter();

  return (
    <div className="w-64 bg-dark-800 border-r border-dark-700 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-dark-700">
        <div className="flex items-center">
          <Brain className="w-8 h-8 text-primary-500" />
          <div className="ml-3">
            <h1 className="text-lg font-bold text-white">AI Company</h1>
            <p className="text-xs text-gray-400">Agent Dashboard</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = router.pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors
                ${isActive 
                  ? 'bg-primary-600 text-white' 
                  : 'text-gray-300 hover:bg-dark-700 hover:text-white'
                }
              `}
            >
              <item.icon className="w-5 h-5 mr-3" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Status */}
      <div className="p-4 border-t border-dark-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-success-500 rounded-full"></div>
            <span className="ml-2 text-sm text-gray-400">System Online</span>
          </div>
          <div className="text-xs text-gray-500">v1.0.0</div>
        </div>
      </div>
    </div>
  );
}