import { useState } from 'react';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import Header from './components/Header';

type Tab = 'dashboard' | 'settings';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');

  return (
    <div className="min-h-screen bg-bg text-text-primary">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'settings' && <Settings />}
      </main>
    </div>
  );
}
