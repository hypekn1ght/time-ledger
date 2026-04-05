import { useWeeklyAggregate } from '../hooks/useAggregates';
import { TIER_COLORS, ALL_TIERS } from '../types';
import WeeklyChart from './WeeklyChart';


export default function Dashboard() {
  const { data: week, isLoading, error } = useWeeklyAggregate();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="skeleton h-32 rounded-lg" />
        <div className="skeleton h-64 rounded-lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16">
        <p className="text-text-secondary">Failed to load dashboard data.</p>
        <p className="text-sm text-text-secondary mt-2">{String(error)}</p>
      </div>
    );
  }

  if (!week || !week.totals || Object.keys(week.totals).length === 0) {
    return (
      <div className="text-center py-16 border border-dashed border-border rounded-lg">
        <div className="w-16 h-16 bg-surface rounded-full mx-auto mb-4 flex items-center justify-center">
          <svg className="w-8 h-8 text-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold mb-2">No data yet</h2>
        <p className="text-text-secondary">Connect your calendars in Settings to start tracking your time.</p>
      </div>
    );
  }

  const grandTotalHours = Math.round(week.grand_total_minutes / 60 * 10) / 10;

  return (
    <div className="space-y-6">
      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Hours */}
        <div className="lg:col-span-1 bg-surface border border-border rounded-lg p-5">
          <p className="text-text-secondary text-sm font-medium mb-1">This Week</p>
          <p className="font-mono text-4xl font-bold number-transition">
            {grandTotalHours}<span className="text-lg text-text-secondary ml-1">hrs</span>
          </p>
          <p className="text-text-secondary text-xs mt-1 font-mono">
            {week.start_date} → {week.end_date}
          </p>
        </div>

        {/* Tier breakdown */}
        {ALL_TIERS.map((tier) => {
          const tierData = week.totals?.[tier];
          const hours = tierData ? Math.round(tierData.minutes / 60 * 10) / 10 : 0;
          const pct = grandTotalHours > 0 ? Math.round((hours / grandTotalHours) * 100) : 0;

          return (
            <div key={tier} className="bg-surface border border-border rounded-lg p-5 card-hover">
              <div className="flex items-center gap-2 mb-2">
                <div 
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: TIER_COLORS[tier] }}
                />
                <p className="text-text-secondary text-sm font-medium">{tier}</p>
              </div>
              <p className="font-mono text-2xl font-bold number-transition">
                {hours}<span className="text-sm text-text-secondary ml-1">hrs</span>
              </p>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="text-xs text-text-secondary">{pct}%</span>
                <span className="text-xs text-text-secondary">of total</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Weekly Chart */}
      <div className="bg-surface border border-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-semibold text-lg">Weekly Breakdown</h2>
          <div className="flex gap-4 text-xs">
            {ALL_TIERS.map((tier) => (
              <div key={tier} className="flex items-center gap-1.5">
                <div 
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: TIER_COLORS[tier] }}
                />
                <span className="text-text-secondary">{tier}</span>
              </div>
            ))}
          </div>
        </div>
        <WeeklyChart dailyBreakdown={week.daily_breakdown} />
      </div>
    </div>
  );
}
