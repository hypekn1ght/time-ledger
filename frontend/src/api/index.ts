// In production, call the Tailscale backend directly to avoid Vercel serverless DNS limitations
const isProd = import.meta.env.PROD;
const BASE = isProd ? 'https://openclaw.tailcd9b6e.ts.net/api' : '/api';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Calendars
  listCalendars: () => fetchJSON<any[]>('/calendars'),
  
  addCalendar: (data: { caldav_url: string; apple_id: string; apple_password: string }) =>
    fetchJSON<{ success: boolean; calendars: any[]; error?: string }>('/calendars', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  updateTier: (calendarId: number, tier: string) =>
    fetchJSON<any>(`/calendars/${calendarId}/tier`, {
      method: 'PATCH',
      body: JSON.stringify({ tier }),
    }),
  
  deleteCalendar: (calendarId: number) =>
    fetchJSON<{ success: boolean }>(`/calendars/${calendarId}`, { method: 'DELETE' }),
  
  // Sync
  triggerSync: () => fetchJSON<{ success: boolean; message?: string; error?: string }>('/sync', { method: 'POST' }),
  
  getSyncStatus: () => fetchJSON<any>('/sync/status'),
  
  // Aggregates
  getThisWeek: () => fetchJSON<any>('/aggregates/this-week'),
  
  getWeekly: (week: string) => fetchJSON<any>(`/aggregates/weekly?week=${encodeURIComponent(week)}`),
  
  getDaily: (date: string) => fetchJSON<any>(`/aggregates/daily?date=${encodeURIComponent(date)}`),
  
  // Health
  health: () => fetchJSON<{ status: string }>('/health'),
};
