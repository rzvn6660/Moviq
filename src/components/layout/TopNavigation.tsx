import React from 'react';
import { Sparkles, History, Clapperboard, Sliders } from 'lucide-react';
import type { UIState } from '../../types/video';

interface TopNavigationProps {
  activeTab: 'workspace' | 'history';
  setActiveTab: (tab: 'workspace' | 'history') => void;
  uiState: UIState;
  setUiState: (state: UIState) => void;
  historyCount: number;
}

export const TopNavigation: React.FC<TopNavigationProps> = ({
  activeTab,
  setActiveTab,
  uiState,
  setUiState,
  historyCount,
}) => {
  const allStates: UIState[] = [
    'EMPTY',
    'READY',
    'QUEUED',
    'ENHANCING',
    'SUBMITTED',
    'GENERATING',
    'PROCESSING',
    'COMPLETED',
    'FAILED',
    'TIMED_OUT'
  ];

  // Dev switcher only visible in Vite development mode (DEV)
  const showDevSwitcher = import.meta.env.DEV;

  return (
    <header className="sticky top-0 z-50 bg-[#070d1f]/95 backdrop-blur-md border-b border-[#23293c] px-4 lg:px-8 py-3">
      <div className="max-w-[1700px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Brand & Wordmark */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setActiveTab('workspace')}
            className="flex items-center gap-2.5 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 rounded-lg p-1"
            aria-label="Moviq Home - Turn Ideas Into Motion"
          >
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20 group-hover:scale-105 transition-transform">
              <Clapperboard className="w-5 h-5 text-slate-950 font-bold" />
            </div>
            <div className="text-left">
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-white font-mono">MOVIQ</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 font-semibold tracking-wider uppercase">
                  AI Studio
                </span>
              </div>
              <p className="text-[11px] text-slate-400 tracking-wide">Turn Ideas Into Motion.</p>
            </div>
          </button>

          {/* System Status Pill */}
          <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" aria-hidden="true" />
            <span className="font-mono text-[11px]">fal-ai Engine Operational</span>
          </div>
        </div>

        {/* Center Workspace / History Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-[#0c1324] p-1 rounded-xl border border-[#23293c]" role="tablist" aria-label="Main Navigation">
          <button
            role="tab"
            aria-selected={activeTab === 'workspace'}
            onClick={() => setActiveTab('workspace')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 ${
              activeTab === 'workspace'
                ? 'bg-[#191f31] text-amber-400 border border-amber-500/30 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Create Studio</span>
          </button>

          <button
            role="tab"
            aria-selected={activeTab === 'history'}
            onClick={() => setActiveTab('history')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 ${
              activeTab === 'history'
                ? 'bg-[#191f31] text-amber-400 border border-amber-500/30 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <History className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Recent History</span>
            <span className="px-1.5 py-0.2 rounded-full bg-slate-800 text-[10px] text-slate-300 font-mono" aria-label={`${historyCount} saved items`}>
              {historyCount}
            </span>
          </button>
        </nav>

        {/* Right Controls & Dev State Switcher (Rendered ONLY in Dev / Mock mode) */}
        {showDevSwitcher && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#0c1324] border border-[#23293c] text-xs text-slate-300">
              <Sliders className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
              <label htmlFor="dev-state-select" className="text-slate-400 hidden lg:inline cursor-pointer">
                Dev State:
              </label>
              <select
                id="dev-state-select"
                value={uiState}
                onChange={(e) => setUiState(e.target.value as UIState)}
                className="bg-transparent text-amber-400 font-mono font-medium focus:outline-none focus-visible:ring-1 focus-visible:ring-amber-500 cursor-pointer"
                aria-label="Development UI state switcher"
              >
                {allStates.map((st) => (
                  <option key={st} value={st} className="bg-[#0c1324] text-slate-200">
                    {st}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};
