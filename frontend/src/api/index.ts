// Backend URL configuration:
// - Local dev: http://localhost:8000
// - Production: VITE_PUBLIC_BACKEND_URL env var (set in Vercel)
// 
// When backend URL is known, update Vercel env var: VITE_PUBLIC_BACKEND_URL=https://your-backend-url.onrender.com
const isProd = import.meta.env.PROD;
const BACKEND_URL = isProd 
  ? (import.meta.env.VITE_PUBLIC_BACKEND_URL || 'http://localhost:8000')
  : 'http://localhost:8000';
const BASE = `${BACKEND_URL}/api`;

function getISOWeek(date: Date): number {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
}

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
  
  getWeeklyOffset: (offset: number) => {
    // Calculate ISO week string for offset weeks from current week
    const today = new Date();
    const targetDate = new Date(today);
    targetDate.setDate(today.getDate() + (offset * 7));
    const iso = getISOWeek(targetDate);
    const year = targetDate.getFullYear();
    const weekStr = `${year}-W${String(iso).padStart(2, '0')}`;
    return fetchJSON<any>(`/aggregates/weekly?week=${encodeURIComponent(weekStr)}`);
  },
  
  getDaily: (date: string) => fetchJSON<any>(`/aggregates/daily?date=${encodeURIComponent(date)}`),
  
  // Health
  health: () => fetchJSON<{ status: string }>('/health'),
};
