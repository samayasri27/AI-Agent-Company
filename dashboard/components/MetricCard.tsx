import { ReactNode } from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
}

export default function MetricCard({ 
  title, 
  value, 
  icon, 
  change, 
  changeType = 'neutral' 
}: MetricCardProps) {
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return 'text-success-400';
      case 'negative':
        return 'text-error-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="metric-card">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="metric-value">{value}</div>
          <div className="metric-label">{title}</div>
          {change && (
            <div className={`metric-change ${getChangeColor()}`}>
              {change}
            </div>
          )}
        </div>
        <div className="text-primary-500 opacity-80">
          {icon}
        </div>
      </div>
    </div>
  );
}