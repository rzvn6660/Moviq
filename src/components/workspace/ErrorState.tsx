import React from 'react';
import { AlertTriangle, RefreshCw, ShieldAlert, WifiOff, Clock } from 'lucide-react';

interface ErrorStateProps {
  type: 'FAILED' | 'TIMED_OUT' | 'EMPTY_PROMPT' | 'RATE_LIMIT';
  errorMessage?: string;
  onRetry: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  type,
  errorMessage,
  onRetry,
}) => {
  const getIcon = () => {
    switch (type) {
      case 'TIMED_OUT':
        return <Clock className="w-8 h-8 text-amber-500" />;
      case 'RATE_LIMIT':
        return <ShieldAlert className="w-8 h-8 text-amber-500" />;
      case 'EMPTY_PROMPT':
        return <AlertTriangle className="w-8 h-8 text-amber-500" />;
      case 'FAILED':
      default:
        return <WifiOff className="w-8 h-8 text-red-400" />;
    }
  };

  const getTitle = () => {
    switch (type) {
      case 'TIMED_OUT':
        return 'Generation Timeout';
      case 'RATE_LIMIT':
        return 'Provider Rate Limit Exceeded';
      case 'EMPTY_PROMPT':
        return 'Prompt Required';
      case 'FAILED':
      default:
        return 'Generation Exception Encountered';
    }
  };

  return (
    <div className="w-full max-w-lg p-6 rounded-2xl bg-[#0c1324] border border-red-500/30 shadow-2xl text-center space-y-4 my-auto">
      <div className="w-14 h-14 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center mx-auto">
        {getIcon()}
      </div>

      <div className="space-y-1">
        <h3 className="text-base font-bold text-slate-100">{getTitle()}</h3>
        <p className="text-xs text-slate-400">
          {errorMessage ||
            'The AI video model backend encountered an unexpected error. Your prompt, camera direction, and options have been preserved.'}
        </p>
      </div>

      <div className="p-3 rounded-xl bg-[#151b2d] border border-[#23293c] text-left text-xs font-mono text-slate-300">
        <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">State Log:</span>
        <p className="text-red-400 font-semibold">{type}</p>
        <p className="text-[11px] text-slate-400 mt-1">Status Code 503 / Provider Timeout. Fast-retry queue ready.</p>
      </div>

      <div className="flex items-center justify-center gap-3 pt-2">
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-bold text-xs hover:from-amber-400 hover:to-amber-500 transition-all shadow-lg shadow-amber-500/20"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Retry Generation</span>
        </button>
      </div>
    </div>
  );
};
