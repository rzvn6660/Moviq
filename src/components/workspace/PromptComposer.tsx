import React from 'react';
import { Sparkles, Wand2, RefreshCw, X } from 'lucide-react';
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
    <div className="space-y-3">
      {/* Header Label */}
      <div className="flex items-center justify-between">
        <label htmlFor="prompt-composer-textarea" className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
          <span>Prompt & Direction</span>
        </label>
        <span className="text-[10px] text-slate-500 font-mono tracking-wider">{prompt.length} / 1000</span>
      </div>

      {/* Multiline Input Composer Box */}
      <div className="relative rounded-xl bg-[#090e1c] border border-[#23293c] focus-within:border-amber-500/70 focus-within:ring-1 focus-within:ring-amber-500/30 transition-all p-3 space-y-2.5 shadow-inner">
        <textarea
          id="prompt-composer-textarea"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your cinematic vision... e.g. A luxury perfume bottle rotating on black marble with warm golden caustics."
          rows={3}
          className="w-full bg-transparent text-xs text-slate-100 placeholder-slate-500 focus:outline-none resize-none font-sans leading-relaxed"
        />

        {/* Toolbar inside input box */}
        <div className="flex items-center justify-between pt-2 border-t border-[#1c2338]">
          <button
            type="button"
            onClick={onEnhance}
            disabled={!prompt.trim() || isEnhancing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 text-xs font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm group focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-500"
          >
            {isEnhancing ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-400" />
            ) : (
              <Wand2 className="w-3.5 h-3.5 text-amber-400 group-hover:rotate-12 transition-transform" />
            )}
            <span>{isEnhancing ? 'Enhancing...' : 'Enhance with AI Director'}</span>
          </button>

          {prompt && (
            <button
              type="button"
              onClick={() => setPrompt('')}
              className="text-[11px] text-slate-500 hover:text-slate-300 transition-colors flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-slate-800/50"
            >
              <X className="w-3 h-3" />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Prompt Quality Score Meter */}
      <PromptScore analysis={analysis} />

      {/* Inspiration Prompt Chips */}
      <div className="space-y-1.5 pt-0.5">
        <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Sample Concepts:</span>
        <div className="flex flex-wrap gap-1.5">
          {SAMPLE_PROMPTS.slice(0, 3).map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelectSample(sample)}
              className="text-[10px] px-2.5 py-1 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] hover:border-amber-500/30 text-slate-300 transition-all text-left line-clamp-1 max-w-[260px]"
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

