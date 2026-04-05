export type Tier = '$1000/hr' | '$100/hr' | 'Learning' | 'Routine';

export interface Calendar {
  id: number;
  name: string;
  caldav_url: string;
  tier: Tier;
  is_connected: boolean;
  last_sync: string | null;
}

export interface SyncStatus {
  is_syncing: boolean;
  last_sync: string | null;
  last_error: string | null;
  events_synced: number;
}

export interface TierMinutes {
  minutes: number;
  hours: number;
  event_count?: number;
}

export interface DailyBreakdown {
  [date: string]: {
    [tier in Tier]?: number;
  };
}

export interface WeeklyAggregate {
  week: string;
  start_date: string;
  end_date: string;
  totals: {
    [key in Tier]?: TierMinutes;
  };
  grand_total_minutes: number;
  daily_breakdown: DailyBreakdown;
}

export interface DailyAggregate {
  date: string;
  totals: {
    [key in Tier]?: TierMinutes;
  };
  grand_total_minutes: number;
}

export const TIER_COLORS: Record<Tier, string> = {
  '$1000/hr': '#E5A50A',
  '$100/hr': '#3B82F6',
  'Learning': '#A855F7',
  'Routine': '#64748B',
};

export const TIER_LABELS: Record<Tier, string> = {
  '$1000/hr': '$1000/hr',
  '$100/hr': '$100/hr',
  'Learning': 'Learning',
  'Routine': 'Routine',
};

export const ALL_TIERS: Tier[] = ['$1000/hr', '$100/hr', 'Learning', 'Routine'];
