import React from 'react';
import { Sparkles, Wand2, RefreshCw } from 'lucide-react';
import { SAMPLE_PROMPTS } from '../../constants/presets';
import type { PromptAnalysis } from '../../types/video';
import { PromptScore } from './PromptScore';

interface PromptComposerProps {
  prompt: string;
  setPrompt: (value: string) => void;
  onEnhance: () => void;
  isEnhancing: boolean;
  analysis: PromptAnalysis;
}

export const PromptComposer: React.FC<PromptComposerProps> = ({
  prompt,
  setPrompt,
  onEnhance,
  isEnhancing,
  analysis,
}) => {
  const handleSelectSample = (sample: string) => {
    setPrompt(sample);
  };

  return (
    <div className="space-y-3.5">
      {/* Header Label */}
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-slate-100 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-400" />
          <span>What do you want to bring to life?</span>
        </label>
        <span className="text-[11px] text-slate-500 font-mono">{prompt.length} chars</span>
      </div>

      {/* Multiline Input Composer */}
      <div className="relative group">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your scene... e.g. A luxury perfume bottle rotating on black marble with warm golden lighting."
          rows={4}
          className="w-full px-4 py-3 rounded-xl bg-[#0c1324] border border-[#23293c] text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/50 transition-all resize-none shadow-inner"
        />

        {/* Enhance Prompt CTA Button */}
        <div className="flex items-center justify-between mt-2.5">
          <button
            onClick={onEnhance}
            disabled={!prompt.trim() || isEnhancing}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-amber-500/20 to-amber-600/10 border border-amber-500/40 text-amber-300 text-xs font-medium hover:bg-amber-500/30 hover:border-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm group"
          >
            {isEnhancing ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-400" />
            ) : (
              <Wand2 className="w-3.5 h-3.5 text-amber-400 group-hover:rotate-12 transition-transform" />
            )}
            <span>{isEnhancing ? 'AI Director Enhancing...' : 'Enhance Prompt'}</span>
          </button>

          {prompt && (
            <button
              onClick={() => setPrompt('')}
              className="text-[11px] text-slate-500 hover:text-slate-300 transition-colors"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Prompt Quality / Score Meter */}
      <PromptScore analysis={analysis} />

      {/* Inspiration Prompt Chips */}
      <div className="space-y-1.5">
        <span className="text-[11px] font-medium text-slate-400">Sample Prompt Ideas:</span>
        <div className="flex flex-wrap gap-1.5">
          {SAMPLE_PROMPTS.slice(0, 3).map((sample, idx) => (
            <button
              key={idx}
              onClick={() => handleSelectSample(sample)}
              className="text-[11px] px-2.5 py-1 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] hover:border-amber-500/30 text-slate-300 transition-all text-left line-clamp-1 max-w-[280px]"
              title={sample}
            >
              {sample}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
