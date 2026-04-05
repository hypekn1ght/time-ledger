import { useState } from 'react';
import { useCalendars, useAddCalendar, useUpdateTier, useDeleteCalendar } from '../hooks/useCalendars';
import { useSync, useSyncStatus } from '../hooks/useAggregates';
import { Tier, TIER_COLORS, ALL_TIERS } from '../types';
import clsx from 'clsx';

export default function Settings() {
  const [showConnect, setShowConnect] = useState(false);
  const [caldavUrl, setCaldavUrl] = useState('https://caldav.icloud.com/');
  const [appleId, setAppleId] = useState('');
  const [applePassword, setApplePassword] = useState('');
  const [connectError, setConnectError] = useState('');

  const { data: calendars = [], isLoading } = useCalendars();
  const addCalendar = useAddCalendar();
  const updateTier = useUpdateTier();
  const deleteCalendar = useDeleteCalendar();
  const sync = useSync();
  const { data: syncStatus } = useSyncStatus();

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    setConnectError('');

    try {
      const result = await addCalendar.mutateAsync({
        caldav_url: caldavUrl,
        apple_id: appleId,
        apple_password: applePassword,
      });

      if (!result.success) {
        // Map backend error messages to user-friendly explanations
        const errorMsg = result.error || '';
        if (errorMsg.includes('AuthorizationError') || errorMsg.includes('401') || errorMsg.includes('Forbidden')) {
          setConnectError('Wrong Apple ID or App-Specific Password. Note: Use an App-Specific Password, not your regular Apple ID password. Generate one at appleid.apple.com → Sign In → App-Specific Passwords.');
        } else if (errorMsg.includes('Connection failed') && errorMsg.includes('DAVClient')) {
          setConnectError('Could not reach iCloud CalDAV server. Check your internet connection and try again.');
        } else if (errorMsg.includes('Name or service not known') || errorMsg.includes('getaddrinfo')) {
          setConnectError('Invalid CalDAV URL. Make sure you entered: https://caldav.icloud.com/');
        } else if (errorMsg.includes('Connection failed')) {
          setConnectError('Connection refused by CalDAV server. Make sure your CalDAV URL is correct.');
        } else {
          setConnectError(result.error || 'Connection failed. Please try again.');
        }
      } else {
        setShowConnect(false);
        setAppleId('');
        setApplePassword('');
      }
    } catch (err) {
      // Network or other fetch error
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes('Failed to fetch') || msg.includes('NetworkError') || msg.includes('fetch') || msg.includes('net::')) {
        setConnectError('Cannot reach the server. Make sure the backend is running and you have an internet connection.');
      } else {
        setConnectError('Unexpected error: ' + msg);
      }
    }
  };

  const handleSync = () => {
    sync.mutate();
  };

  const handleTierChange = (calendarId: number, newTier: Tier) => {
    updateTier.mutate({ id: calendarId, tier: newTier });
  };

  const isConnected = calendars.length > 0;
  const lastSync = syncStatus?.last_sync 
    ? new Date(syncStatus.last_sync).toLocaleString() 
    : 'Never';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Calendar Connection</h1>
          <p className="text-text-secondary text-sm mt-1">
            Connect iCloud CalDAV to sync and analyze your time.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isConnected && (
            <>
              <div className="text-right mr-2">
                <p className="text-xs text-text-secondary">Last sync</p>
                <p className="text-sm font-mono">{lastSync}</p>
              </div>
              <button
                onClick={handleSync}
                disabled={sync.isPending || syncStatus?.is_syncing}
                className={clsx(
                  'px-4 py-2 rounded text-sm font-medium transition-colors flex items-center gap-2',
                  sync.isPending || syncStatus?.is_syncing
                    ? 'bg-surface text-text-secondary cursor-not-allowed'
                    : 'bg-blue text-white hover:bg-blue/90'
                )}
              >
                {sync.isPending || syncStatus?.is_syncing ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Syncing...
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Sync Now
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Connect Error */}
      {connectError && (
        <div className="bg-danger/10 border border-danger/30 rounded-lg p-4">
          <p className="text-danger text-sm font-medium">Connection Failed</p>
          <p className="text-danger/80 text-sm mt-1">{connectError}</p>
        </div>
      )}

      {/* Sync Error */}
      {syncStatus?.last_error && (
        <div className="bg-danger/10 border border-danger/30 rounded-lg p-4">
          <p className="text-danger text-sm font-medium">Sync Error</p>
          <p className="text-danger/80 text-sm mt-1">{syncStatus.last_error}</p>
        </div>
      )}

      {/* Calendars List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton h-16 rounded-lg" />
          ))}
        </div>
      ) : isConnected ? (
        <div className="space-y-3">
          {calendars.map((cal: any) => (
            <div
              key={cal.id}
              className="bg-surface border border-border rounded-lg p-4 flex items-center justify-between card-hover"
            >
              <div className="flex items-center gap-3">
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: TIER_COLORS[cal.tier as Tier] }}
                />
                <div>
                  <p className="font-medium">{cal.name}</p>
                  <p className="text-text-secondary text-xs font-mono truncate max-w-xs">
                    {cal.caldav_url}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <select
                  value={cal.tier}
                  onChange={(e) => handleTierChange(cal.id, e.target.value as Tier)}
                  className="bg-bg border border-border rounded px-3 py-1.5 text-sm font-mono focus:outline-none focus:border-blue"
                >
                  {ALL_TIERS.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                <button
                  onClick={() => deleteCalendar.mutate(cal.id)}
                  className="text-text-secondary hover:text-danger transition-colors p-1"
                  title="Remove calendar"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          ))}

          {/* Add another calendar */}
          <button
            onClick={() => { setConnectError(''); setShowConnect(true); }}
            className="w-full border border-dashed border-border rounded-lg p-4 text-text-secondary hover:text-text-primary hover:border-text-secondary transition-colors flex items-center justify-center gap-2"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
            </svg>
            Add another calendar
          </button>
        </div>
      ) : (
        /* No calendars connected */
        (<div className="text-center py-12 border border-dashed border-border rounded-lg">
          <div className="w-16 h-16 bg-surface rounded-full mx-auto mb-4 flex items-center justify-center">
            <svg className="w-8 h-8 text-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold mb-2">No calendars connected</h2>
          <p className="text-text-secondary text-sm mb-6 max-w-md mx-auto">
            Connect your iCloud account to start tracking how you spend your time across different value tiers.
          </p>
          <button
            onClick={() => { setConnectError(''); setShowConnect(true); }}
            className="px-6 py-2.5 bg-blue text-white rounded-lg font-medium hover:bg-blue/90 transition-colors"
          >
            Connect iCloud
          </button>
        </div>)
      )}

      {/* Connect Modal */}
      {showConnect && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-surface border border-border rounded-lg w-full max-w-md p-6">
            <h2 className="text-xl font-semibold mb-4">Connect iCloud Calendar</h2>
            
            <form onSubmit={handleConnect} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1.5">
                  CalDAV URL
                </label>
                <input
                  type="url"
                  value={caldavUrl}
                  onChange={(e) => setCaldavUrl(e.target.value)}
                  className="w-full bg-bg border border-border rounded-lg px-3 py-2 font-mono text-sm focus:outline-none focus:border-blue"
                  placeholder="https://caldav.icloud.com/"
                  required
                />
                <p className="text-text-secondary text-xs mt-1">
                  Use the iCloud CalDAV URL: https://caldav.icloud.com/
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1.5">
                  Apple ID
                </label>
                <input
                  type="email"
                  value={appleId}
                  onChange={(e) => setAppleId(e.target.value)}
                  className="w-full bg-bg border border-border rounded-lg px-3 py-2 font-mono text-sm focus:outline-none focus:border-blue"
                  placeholder="your@apple.id"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1.5">
                  App-Specific Password
                </label>
                <input
                  type="password"
                  value={applePassword}
                  onChange={(e) => setApplePassword(e.target.value)}
                  className="w-full bg-bg border border-border rounded-lg px-3 py-2 font-mono text-sm focus:outline-none focus:border-blue"
                  placeholder="xxxx-xxxx-xxxx-xxxx"
                  required
                />
                <p className="text-text-secondary text-xs mt-1">
                  Generate one at appleid.apple.com → Sign In → App-Specific Passwords
                </p>
              </div>

              {connectError && (
                <div className="bg-danger/10 border border-danger/30 rounded-lg p-3">
                  <p className="text-danger text-sm">{connectError}</p>
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowConnect(false);
                    setConnectError('');
                  }}
                  className="flex-1 px-4 py-2 border border-border rounded-lg text-text-secondary hover:text-text-primary transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={addCalendar.isPending}
                  className="flex-1 px-4 py-2 bg-blue text-white rounded-lg font-medium hover:bg-blue/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {addCalendar.isPending ? (
                    <>
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Connecting...
                    </>
                  ) : 'Connect'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
