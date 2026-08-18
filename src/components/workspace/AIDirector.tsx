import React, { useState } from 'react';
import { Film, Edit3, Camera, Sun, Smile, Move, Box, MapPin, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import type { StructuredDirection } from '../../types/video';

interface AIDirectorProps {
  originalPrompt: string;
  enhancedPrompt: string;
  setEnhancedPrompt: (val: string) => void;
  structuredDirection: StructuredDirection | null;
  isEnhancing: boolean;
}

export const AIDirector: React.FC<AIDirectorProps> = ({
  originalPrompt,
  enhancedPrompt,
  setEnhancedPrompt,
  structuredDirection,
  isEnhancing,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'enhanced' | 'structured' | 'original'>('enhanced');

  if (isEnhancing) {
    return (
      <div className="p-3 rounded-xl bg-[#090e1c] border border-amber-500/30 flex items-center justify-between text-xs text-amber-400 font-mono animate-pulse">
        <div className="flex items-center gap-2">
          <Film className="w-4 h-4 animate-spin text-amber-400" />
          <span>AI Director is constructing shot list & camera keyframes...</span>
        </div>
      </div>
    );
  }

  if (!enhancedPrompt && !structuredDirection) {
    return null;
  }

  return (
    <div className="rounded-xl bg-[#090e1c] border border-[#23293c] overflow-hidden transition-all">
      {/* Compact Bar / Toggle Header */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        className="w-full px-3.5 py-2.5 flex items-center justify-between text-xs font-semibold text-slate-200 hover:text-white hover:bg-[#151b2d]/50 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-500"
      >
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-400" aria-hidden="true" />
          <span className="font-mono text-xs uppercase tracking-wider text-amber-300">AI Director Active</span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 font-mono">
            Keyframe Direction Ready
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-slate-400 text-[11px] font-mono">
          <span>{isOpen ? 'Hide Details' : 'View Shot List'}</span>
          {isOpen ? <ChevronUp className="w-3.5 h-3.5 text-amber-400" /> : <ChevronDown className="w-3.5 h-3.5 text-amber-400" />}
        </div>
      </button>

      {/* Expanded Content Drawer */}
      {isOpen && (
        <div className="p-3.5 border-t border-[#23293c] space-y-3 bg-[#0c1324]/80 text-xs">
          {/* Comparison Tabs */}
          <div className="flex items-center gap-1 bg-[#151b2d] p-0.5 rounded-lg border border-[#23293c] text-[11px]">
            <button
              type="button"
              onClick={() => setActiveTab('enhanced')}
              className={`flex-1 py-1 rounded-md transition-all text-center ${
                activeTab === 'enhanced'
                  ? 'bg-amber-500/20 text-amber-300 font-medium border border-amber-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Enhanced Prompt
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('structured')}
              className={`flex-1 py-1 rounded-md transition-all text-center ${
                activeTab === 'structured'
                  ? 'bg-amber-500/20 text-amber-300 font-medium border border-amber-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Shot List
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('original')}
              className={`flex-1 py-1 rounded-md transition-all text-center ${
                activeTab === 'original'
                  ? 'bg-amber-500/20 text-amber-300 font-medium border border-amber-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Raw Input
            </button>
          </div>

          {/* Tab 1: Enhanced Editable Prompt */}
          {activeTab === 'enhanced' && (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-amber-400 font-mono font-medium flex items-center gap-1">
                  <Edit3 className="w-3 h-3" />
                  Editable Director Prompt:
                </span>
              </div>
              <textarea
                value={enhancedPrompt}
                onChange={(e) => setEnhancedPrompt(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 rounded-lg bg-[#151b2d] border border-amber-500/30 text-xs text-slate-200 focus:outline-none focus:border-amber-400 transition-all resize-none font-sans"
              />
            </div>
          )}

          {/* Tab 2: Raw Original Prompt */}
          {activeTab === 'original' && (
            <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c] text-xs text-slate-400 font-sans">
              <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Raw User Prompt:</span>
              <p className="italic">{originalPrompt || 'No prompt entered yet.'}</p>
            </div>
          )}

          {/* Tab 3: Structured Shot List Tags */}
          {activeTab === 'structured' && structuredDirection && (
            <div className="grid grid-cols-2 gap-1.5 text-xs font-sans">
              <div className="p-2 rounded-lg bg-[#151b2d] border border-[#23293c]">
                <div className="flex items-center gap-1 text-amber-400 font-mono text-[10px] uppercase mb-0.5">
                  <Box className="w-3 h-3" />
                  <span>Subject</span>
                </div>
                <p className="text-slate-300 text-[11px] line-clamp-1">{structuredDirection.subject}</p>
              </div>

              <div className="p-2 rounded-lg bg-[#151b2d] border border-[#23293c]">
                <div className="flex items-center gap-1 text-amber-400 font-mono text-[10px] uppercase mb-0.5">
                  <MapPin className="w-3 h-3" />
                  <span>Environment</span>
                </div>
                <p className="text-slate-300 text-[11px] line-clamp-1">{structuredDirection.environment}</p>
              </div>

              <div className="p-2 rounded-lg bg-[#151b2d] border border-[#23293c]">
                <div className="flex items-center gap-1 text-amber-400 font-mono text-[10px] uppercase mb-0.5">
                  <Camera className="w-3 h-3" />
                  <span>Camera</span>
                </div>
                <p className="text-slate-300 text-[11px] line-clamp-1">{structuredDirection.camera}</p>
              </div>

              <div className="p-2 rounded-lg bg-[#151b2d] border border-[#23293c]">
                <div className="flex items-center gap-1 text-amber-400 font-mono text-[10px] uppercase mb-0.5">
                  <Sun className="w-3 h-3" />
                  <span>Lighting</span>
                </div>
                <p className="text-slate-300 text-[11px] line-clamp-1">{structuredDirection.lighting}</p>
              </div>

              <div className="p-2 rounded-lg bg-[#151b2d] border border-[#23293c]">
                <div className="flex items-center gap-1 text-amber-400 font-mono text-[10px] uppercase mb-0.5">
                  <Move className="w-3 h-3" />
                  <span>Action</span>
                </div>
                <p className="text-slate-300 text-[11px] line-clamp-1">{structuredDirection.action}</p>
              </div>

              <div className="p-2 rounded-lg bg-[#151b2d] border border-[#23293c]">
                <div className="flex items-center gap-1 text-amber-400 font-mono text-[10px] uppercase mb-0.5">
                  <Smile className="w-3 h-3" />
                  <span>Mood</span>
                </div>
                <p className="text-slate-300 text-[11px] line-clamp-1">{structuredDirection.mood}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

