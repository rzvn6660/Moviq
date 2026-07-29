import React from 'react';
import type { PromptAnalysis } from '../../types/video';
import { Gauge, Info, CheckCircle } from 'lucide-react';

interface PromptScoreProps {
  analysis: PromptAnalysis;
}

export const PromptScore: React.FC<PromptScoreProps> = ({ analysis }) => {
  const { score, label, feedback } = analysis;

  const getScoreColor = () => {
    if (score >= 85) return 'from-emerald-500 to-amber-400 text-emerald-400';
    if (score >= 60) return 'from-amber-500 to-amber-400 text-amber-400';
    if (score >= 35) return 'from-amber-600 to-yellow-500 text-yellow-400';
    return 'from-slate-600 to-slate-400 text-slate-400';
  };

  return (
    <div className="p-3.5 rounded-xl bg-[#151b2d]/80 border border-[#23293c] text-xs">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Gauge className="w-4 h-4 text-amber-400" />
          <span className="font-medium text-slate-200">Prompt Score</span>
          <span
            className="px-2 py-0.5 rounded-full text-[10px] font-medium border border-amber-500/20 bg-amber-500/10 text-amber-400"
          >
            {label}
          </span>
        </div>
        <span className="font-mono font-bold text-sm text-amber-400">{score}/100</span>
      </div>

      {/* Progress Track */}
      <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden mb-2.5">
        <div
          className={`h-full bg-gradient-to-r ${getScoreColor()} transition-all duration-500`}
          style={{ width: `${score}%` }}
        />
      </div>

      {/* Dynamic Feedback Tips */}
      {feedback.length > 0 ? (
        <div className="space-y-1 mt-2">
          {feedback.map((tip, idx) => (
            <div key={idx} className="flex items-center gap-1.5 text-[11px] text-slate-400">
              <Info className="w-3 h-3 text-amber-500 shrink-0" />
              <span>{tip}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex items-center gap-1.5 text-[11px] text-emerald-400">
          <CheckCircle className="w-3 h-3 shrink-0" />
          <span>Excellent direction depth! Ready for maximum generation quality.</span>
        </div>
      )}
    </div>
  );
};
