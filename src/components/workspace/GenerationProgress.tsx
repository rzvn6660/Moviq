import React from 'react';
import type { GenerationProgressStep, GenerationProgressInfo } from '../../types/video';
import { CheckCircle2, Loader2, Circle, Activity } from 'lucide-react';

interface GenerationProgressProps {
  steps: GenerationProgressStep[];
  progressInfo?: GenerationProgressInfo;
}

export const GenerationProgress: React.FC<GenerationProgressProps> = ({
  steps,
  progressInfo,
}) => {
  const isDeterminate = progressInfo?.isDeterminate && typeof progressInfo.percentage === 'number';
  const percentage = progressInfo?.percentage;

  return (
    <div className="w-full max-w-md p-6 rounded-2xl bg-[#0c1324]/95 border border-amber-500/40 backdrop-blur-xl shadow-2xl space-y-5" role="region" aria-label="Generation progress">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <Loader2 className="w-5 h-5 text-amber-400 animate-spin" aria-hidden="true" />
          <span className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono">
            {progressInfo?.state || 'GENERATING'}
          </span>
        </div>

        {/* Truthful Percentage or Stage Badge */}
        {isDeterminate ? (
          <span className="text-sm font-mono font-bold text-amber-400" aria-label={`${percentage}% complete`}>
            {percentage}%
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-xs font-mono text-amber-400/90 px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30">
            <Activity className="w-3 h-3 animate-pulse" aria-hidden="true" />
            <span>Stage-Based Pipeline</span>
          </span>
        )}
      </div>

      {/* Progress Track (Determinate Fill OR Indeterminate Pulse/Shimmer) */}
      <div 
        className="w-full h-2 rounded-full bg-slate-800 overflow-hidden relative"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={isDeterminate ? percentage : undefined}
        aria-label={isDeterminate ? `Generation progress ${percentage}%` : 'Generation in progress'}
      >
        {isDeterminate ? (
          <div
            className="h-full bg-gradient-to-r from-amber-500 to-amber-300 transition-all duration-300 shadow-md shadow-amber-500/50"
            style={{ width: `${percentage}%` }}
          />
        ) : (
          <div className="h-full w-full bg-gradient-to-r from-transparent via-amber-500 to-transparent animate-pulse" />
        )}
      </div>

      {/* Steps Breakdown List */}
      <div className="space-y-3 pt-2">
        {steps.map((st) => (
          <div key={st.id} className="flex items-start gap-3 text-xs">
            {st.status === 'completed' && (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" aria-hidden="true" />
            )}
            {st.status === 'active' && (
              <Loader2 className="w-4 h-4 text-amber-400 animate-spin shrink-0 mt-0.5" aria-hidden="true" />
            )}
            {st.status === 'pending' && (
              <Circle className="w-4 h-4 text-slate-600 shrink-0 mt-0.5" aria-hidden="true" />
            )}
            <div>
              <p
                className={`font-semibold ${
                  st.status === 'completed'
                    ? 'text-slate-200 line-through opacity-70'
                    : st.status === 'active'
                    ? 'text-amber-400 font-bold'
                    : 'text-slate-500'
                }`}
              >
                {st.title}
              </p>
              <p className="text-[11px] text-slate-400 font-mono">{st.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
