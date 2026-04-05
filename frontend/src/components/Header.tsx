import clsx from 'clsx';

interface Props {
  activeTab: 'dashboard' | 'settings';
  onTabChange: (tab: 'dashboard' | 'settings') => void;
}

export default function Header({ activeTab, onTabChange }: Props) {
  const tabs = [
    { id: 'dashboard' as const, label: 'Dashboard' },
    { id: 'settings' as const, label: 'Calendars' },
  ];

  return (
    <header className="border-b border-border">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-gold to-blue rounded flex items-center justify-center">
              <span className="font-mono font-bold text-bg text-sm">TL</span>
            </div>
            <span className="font-mono font-semibold text-lg tracking-tight">Time Ledger</span>
          </div>
          
          <nav className="flex gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={clsx(
                  'px-4 py-2 text-sm font-medium rounded transition-colors',
                  activeTab === tab.id
                    ? 'bg-surface text-text-primary border border-border'
                    : 'text-text-secondary hover:text-text-primary'
                )}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
