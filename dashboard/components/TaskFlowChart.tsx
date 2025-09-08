import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { time: '00:00', tasks: 12, completed: 8 },
  { time: '04:00', tasks: 8, completed: 6 },
  { time: '08:00', tasks: 25, completed: 18 },
  { time: '12:00', tasks: 35, completed: 28 },
  { time: '16:00', tasks: 42, completed: 35 },
  { time: '20:00', tasks: 28, completed: 22 },
];

export default function TaskFlowChart() {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="time" 
            stroke="#9CA3AF"
            fontSize={12}
          />
          <YAxis 
            stroke="#9CA3AF"
            fontSize={12}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '6px',
              color: '#F9FAFB'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="tasks" 
            stroke="#3B82F6" 
            strokeWidth={2}
            name="Active Tasks"
          />
          <Line 
            type="monotone" 
            dataKey="completed" 
            stroke="#10B981" 
            strokeWidth={2}
            name="Completed"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}