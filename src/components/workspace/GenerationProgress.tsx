import React from 'react';
import type { GenerationProgressStep, GenerationProgressInfo } from '../../types/video';
import { CheckCircle2, Loader2, Circle, Activity, Sparkles, Cpu, ShieldCheck, Film } from 'lucide-react';

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
  const currentState = progressInfo?.state || 'GENERATING';

  // Map state to pipeline active index (0 to 5)
  const getActivePipelineStep = (state: string) => {
    switch (state) {
      case 'QUEUED':
        return 0; // PROMPT
      case 'ENHANCING':
        return 1; // DIRECTOR
      case 'SUBMITTED':
        return 2; // RECOMMENDER
      case 'GENERATING':
        return 3; // ENGINE
      case 'PROCESSING':
        return 4; // VALIDATOR
      case 'COMPLETED':
        return 5; // VIDEO
      default:
        return 3;
    }
  };

  const activeNodeIdx = getActivePipelineStep(currentState);

  const pipelineNodes = [
    { label: 'PROMPT', icon: Sparkles },
    { label: 'DIRECTOR', icon: Film },
    { label: 'RECOMMENDER', icon: Activity },
    { label: 'ENGINE', icon: Cpu },
    { label: 'VALIDATOR', icon: ShieldCheck },
    { label: 'VIDEO', icon: CheckCircle2 }
  ];

  return (
    <div className="w-full max-w-lg p-5 rounded-2xl bg-[#090e1c]/95 border border-[#23293c] backdrop-blur-xl shadow-2xl space-y-4" role="region" aria-label="Generation progress">
      
      {/* Title & Badge */}
      <div className="flex items-center justify-between pb-2 border-b border-[#1c2338]">
        <div className="flex items-center gap-2">
          <Loader2 className="w-4 h-4 text-amber-400 animate-spin" aria-hidden="true" />
          <span className="text-xs font-bold text-slate-100 uppercase tracking-wider font-mono">
            {currentState} PIPELINE
          </span>
        </div>

        {isDeterminate ? (
          <span className="text-xs font-mono font-bold text-amber-400" aria-label={`${percentage}% complete`}>
            {percentage}%
          </span>
        ) : (
          <span className="flex items-center gap-1 text-[10px] font-mono text-amber-400 px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30">
            <Activity className="w-3 h-3" aria-hidden="true" />
            <span>Active Synthesis</span>
          </span>
        )}
      </div>

      {/* Orchestration Pipeline Node Flow (PROMPT -> DIRECTOR -> RECOMMENDER -> ENGINE -> VALIDATOR -> VIDEO) */}
      <div className="py-2">
        <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-2 text-center">
          Moviq Orchestration Engine Pipeline
        </div>
        <div className="flex items-center justify-between gap-1 overflow-x-auto py-1 px-0.5">
          {pipelineNodes.map((node, idx) => {
            const IconComp = node.icon;
            const isDone = idx < activeNodeIdx;
            const isActive = idx === activeNodeIdx;

            return (
              <React.Fragment key={node.label}>
                <div className={`flex flex-col items-center gap-1 min-w-[50px] transition-all ${
                  isActive ? 'scale-105' : ''
                }`}>
                  <div className={`w-7 h-7 rounded-lg flex items-center justify-center border transition-all ${
                    isDone
                      ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
                      : isActive
                      ? 'bg-amber-500/20 border-amber-500 text-amber-300 ring-2 ring-amber-500/20'
                      : 'bg-[#151b2d] border-[#23293c] text-slate-600'
                  }`}>
                    {isActive ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-400" />
                    ) : (
                      <IconComp className="w-3.5 h-3.5" />
                    )}
                  </div>
                  <span className={`text-[9px] font-mono font-semibold tracking-tighter ${
                    isDone
                      ? 'text-emerald-400'
                      : isActive
                      ? 'text-amber-300 font-bold'
                      : 'text-slate-600'
                  }`}>
                    {node.label}
                  </span>
                </div>

                {idx < pipelineNodes.length - 1 && (
                  <div className={`h-[2px] flex-1 min-w-[12px] transition-colors rounded-full ${
                    idx < activeNodeIdx ? 'bg-emerald-500/60' : 'bg-slate-800'
                  }`} />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Progress Track */}
      <div 
        className="w-full h-1.5 rounded-full bg-slate-900 overflow-hidden relative border border-[#1c2338]"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={isDeterminate ? percentage : undefined}
        aria-label={isDeterminate ? `Generation progress ${percentage}%` : 'Generation in progress'}
      >
        {isDeterminate ? (
          <div
            className="h-full bg-amber-500 transition-all duration-300"
            style={{ width: `${percentage}%` }}
          />
        ) : (
          <div className="h-full w-full bg-gradient-to-r from-transparent via-amber-500 to-transparent" />
        )}
      </div>

      {/* Steps Breakdown Checklist */}
      <div className="space-y-2 pt-1 border-t border-[#1c2338]">
        {steps.map((st) => (
          <div key={st.id} className="flex items-start gap-2.5 text-xs">
            {st.status === 'completed' && (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" aria-hidden="true" />
            )}
            {st.status === 'active' && (
              <Loader2 className="w-3.5 h-3.5 text-amber-400 animate-spin shrink-0 mt-0.5" aria-hidden="true" />
            )}
            {st.status === 'pending' && (
              <Circle className="w-3.5 h-3.5 text-slate-700 shrink-0 mt-0.5" aria-hidden="true" />
            )}
            <div>
              <p
                className={`font-semibold text-xs ${
                  st.status === 'completed'
                    ? 'text-slate-400 line-through'
                    : st.status === 'active'
                    ? 'text-amber-300 font-bold'
                    : 'text-slate-600'
                }`}
              >
                {st.title}
              </p>
              <p className="text-[10px] text-slate-500 font-mono">{st.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

