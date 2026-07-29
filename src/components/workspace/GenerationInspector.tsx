import React, { useState } from 'react';
import type { VideoItem } from '../../types/video';
import { Info, Copy, Check, Sparkles, Cpu } from 'lucide-react';

interface GenerationInspectorProps {
  video: VideoItem;
}

export const GenerationInspector: React.FC<GenerationInspectorProps> = ({ video }) => {
  const [copiedOriginal, setCopiedOriginal] = useState(false);
  const [copiedEnhanced, setCopiedEnhanced] = useState(false);

  const copyToClipboard = (text: string, isEnhanced: boolean) => {
    navigator.clipboard.writeText(text);
    if (isEnhanced) {
      setCopiedEnhanced(true);
      setTimeout(() => setCopiedEnhanced(false), 2000);
    } else {
      setCopiedOriginal(true);
      setTimeout(() => setCopiedOriginal(false), 2000);
    }
  };

  const { metadata } = video;
  const isWan = metadata.provider === 'wan' || metadata.model.includes('Wan');
  const execMode = metadata.executionMode || 'Hosted Inference';

  return (
    <div className="p-4 rounded-xl bg-[#0c1324] border border-[#23293c] space-y-4 text-xs">
      <div className="flex items-center justify-between border-b border-[#23293c] pb-2.5">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-amber-400" />
          <span className="font-semibold text-slate-100 uppercase tracking-wider text-xs">Generation Inspector</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-mono">
            {execMode}
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-[#151b2d] border border-[#23293c] text-slate-400 font-mono">
            ID: {video.id}
          </span>
        </div>
      </div>

      {/* Grid of technical rendering metadata */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c]">
          <span className="text-[10px] text-slate-400 font-mono block">AI Engine</span>
          <span className="font-semibold text-slate-200 line-clamp-1">{metadata.model}</span>
        </div>
        <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c]">
          <span className="text-[10px] text-slate-400 font-mono block">Provider / Mode</span>
          <span className="font-semibold text-slate-200 line-clamp-1">
            {metadata.provider} • {execMode}
          </span>
        </div>
        <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c]">
          <span className="text-[10px] text-slate-400 font-mono block">Duration & Specs</span>
          <span className="font-semibold text-amber-400">
            {isWan ? '~2.06s (33f)' : metadata.duration} ({metadata.resolution})
          </span>
        </div>
        <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c]">
          <span className="text-[10px] text-slate-400 font-mono block">Render Time</span>
          <span className="font-semibold text-slate-200">{metadata.generationTimeSeconds}s</span>
        </div>
      </div>

      {/* Wan2.1 Open Source Verified Execution Badge if applicable */}
      {isWan && (
        <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-start gap-2.5 text-[11px] text-slate-200">
          <Cpu className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-semibold text-amber-400 block">Wan-AI Open-Source Render Profile</span>
            <span className="text-[10px] text-slate-300 font-mono block">
              Engine: {metadata.model} | Hardware Profile: Tesla P100 16GB / Serverless | Mode: {execMode}
            </span>
          </div>
        </div>
      )}

      {/* Side-by-side prompt comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
        {/* Original Prompt */}
        <div className="p-3 rounded-lg bg-[#151b2d] border border-[#23293c] relative space-y-1">
          <div className="flex items-center justify-between text-[11px] font-medium text-slate-400">
            <span>Original Idea Prompt</span>
            <button
              onClick={() => copyToClipboard(video.originalPrompt, false)}
              className="text-slate-400 hover:text-slate-200 flex items-center gap-1"
            >
              {copiedOriginal ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            </button>
          </div>
          <p className="text-slate-300 italic text-[11px] leading-relaxed">{video.originalPrompt}</p>
        </div>

        {/* Enhanced Prompt */}
        <div className="p-3 rounded-lg bg-[#151b2d] border border-amber-500/30 relative space-y-1">
          <div className="flex items-center justify-between text-[11px] font-medium text-amber-400">
            <span className="flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              AI Director Enhanced Prompt
            </span>
            <button
              onClick={() => copyToClipboard(video.enhancedPrompt, true)}
              className="text-slate-400 hover:text-slate-200 flex items-center gap-1"
            >
              {copiedEnhanced ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            </button>
          </div>
          <p className="text-slate-200 text-[11px] leading-relaxed">{video.enhancedPrompt}</p>
        </div>
      </div>
    </div>
  );
};
