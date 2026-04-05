import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { TIER_COLORS, Tier, ALL_TIERS } from '../types';

interface DailyBreakdown {
  [date: string]: {
    [tier in Tier]?: number;
  };
}

interface Props {
  dailyBreakdown: DailyBreakdown;
}

const DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export default function WeeklyChart({ dailyBreakdown }: Props) {
  // Build chart data
  const data = Object.entries(dailyBreakdown)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, breakdown]) => {
      const d = new Date(date);
      const dayName = DAY_LABELS[d.getDay() === 0 ? 6 : d.getDay() - 1];
      const totalMinutes = Object.values(breakdown).reduce((sum, v) => sum + (v || 0), 0);
      return {
        date,
        dayName,
        totalHours: Math.round(totalMinutes / 60 * 10) / 10,
        ...breakdown,
      };
    });

  if (data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-text-secondary">
        No data for this week
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <XAxis 
          dataKey="dayName" 
          axisLine={false} 
          tickLine={false}
          tick={{ fill: '#A1A1AA', fontSize: 12, fontFamily: 'Inter' }}
        />
        <YAxis 
          axisLine={false} 
          tickLine={false}
          tick={{ fill: '#A1A1AA', fontSize: 12, fontFamily: 'JetBrains Mono' }}
          tickFormatter={(v) => `${v}h`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#18181B',
            border: '1px solid #27272A',
            borderRadius: 8,
            fontFamily: 'Inter',
          }}
          labelStyle={{ color: '#FAFAFA', fontWeight: 600 }}
          formatter={(value: number, name: string) => {
            const hours = Math.round(value / 60 * 10) / 10;
            return [`${hours}h`, name];
          }}
          labelFormatter={(label, payload) => {
            if (payload && payload[0]) {
              return `${payload[0].payload.dayName} (${payload[0].payload.date})`;
            }
            return label;
          }}
        />
        {ALL_TIERS.map((tier) => (
          <Bar
            key={tier}
            dataKey={tier}
            stackId="a"
            fill={TIER_COLORS[tier]}
            radius={tier === 'Routine' ? [4, 4, 0, 0] : [0, 0, 0, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
