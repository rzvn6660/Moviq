import React, { useState } from 'react';
import { Film, Edit3, Camera, Sun, Smile, Move, Box, MapPin } from 'lucide-react';
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
  const [activeTab, setActiveTab] = useState<'enhanced' | 'original' | 'structured'>('enhanced');

  if (isEnhancing) {
    return (
      <div className="p-4 rounded-xl bg-[#0c1324] border border-amber-500/30 space-y-3 animate-pulse">
        <div className="flex items-center gap-2 text-amber-400 font-medium text-xs">
          <Film className="w-4 h-4 animate-spin" />
          <span>AI Director is constructing shot list & camera angles...</span>
        </div>
        <div className="h-16 bg-[#151b2d] rounded-lg"></div>
        <div className="grid grid-cols-2 gap-2">
          <div className="h-10 bg-[#151b2d] rounded-md"></div>
          <div className="h-10 bg-[#151b2d] rounded-md"></div>
        </div>
      </div>
    );
  }

  if (!enhancedPrompt && !structuredDirection) {
    return null;
  }

  return (
    <div className="p-4 rounded-xl bg-[#0c1324] border border-[#23293c] space-y-3">
      {/* Header & View Switcher */}
      <div className="flex items-center justify-between border-b border-[#23293c] pb-2.5">
        <div className="flex items-center gap-2">
          <Film className="w-4 h-4 text-amber-400" />
          <span className="text-xs font-semibold text-slate-100 uppercase tracking-wider">AI Director</span>
        </div>

        {/* Comparison Tabs */}
        <div className="flex items-center gap-1 bg-[#151b2d] p-0.5 rounded-lg border border-[#23293c] text-[11px]">
          <button
            onClick={() => setActiveTab('enhanced')}
            className={`px-2.5 py-1 rounded-md transition-all ${
              activeTab === 'enhanced'
                ? 'bg-amber-500/20 text-amber-400 font-medium'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Enhanced Prompt
          </button>
          <button
            onClick={() => setActiveTab('original')}
            className={`px-2.5 py-1 rounded-md transition-all ${
              activeTab === 'original'
                ? 'bg-amber-500/20 text-amber-400 font-medium'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Original
          </button>
          <button
            onClick={() => setActiveTab('structured')}
            className={`px-2.5 py-1 rounded-md transition-all ${
              activeTab === 'structured'
                ? 'bg-amber-500/20 text-amber-400 font-medium'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Director Shot List
          </button>
        </div>
      </div>

      {/* Content depending on active tab */}
      {activeTab === 'enhanced' && (
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-amber-400/90 font-medium flex items-center gap-1">
              <Edit3 className="w-3 h-3" />
              Editable Enhanced Prompt
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

      {activeTab === 'original' && (
        <div className="p-3 rounded-lg bg-[#151b2d] border border-[#23293c] text-xs text-slate-400">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Your Raw Prompt:</span>
          <p className="italic">{originalPrompt || 'No prompt entered yet.'}</p>
        </div>
      )}

      {activeTab === 'structured' && structuredDirection && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
          <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c]">
            <div className="flex items-center gap-1.5 text-amber-400 font-medium mb-1">
              <Box className="w-3.5 h-3.5" />
              <span>Subject</span>
            </div>
            <p className="text-slate-300 text-[11px] line-clamp-2">{structuredDirection.subject}</p>
          </div>

          <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c]">
            <div className="flex items-center gap-1.5 text-amber-400 font-medium mb-1">
              <MapPin className="w-3.5 h-3.5" />
              <span>Environment</span>
            </div>
            <p className="text-slate-300 text-[11px] line-clamp-2">{structuredDirection.environment}</p>
          </div>

          <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c]">
            <div className="flex items-center gap-1.5 text-amber-400 font-medium mb-1">
              <Camera className="w-3.5 h-3.5" />
              <span>Camera</span>
            </div>
            <p className="text-slate-300 text-[11px] line-clamp-2">{structuredDirection.camera}</p>
          </div>

          <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c]">
            <div className="flex items-center gap-1.5 text-amber-400 font-medium mb-1">
              <Sun className="w-3.5 h-3.5" />
              <span>Lighting</span>
            </div>
            <p className="text-slate-300 text-[11px] line-clamp-2">{structuredDirection.lighting}</p>
          </div>

          <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c]">
            <div className="flex items-center gap-1.5 text-amber-400 font-medium mb-1">
              <Move className="w-3.5 h-3.5" />
              <span>Action</span>
            </div>
            <p className="text-slate-300 text-[11px] line-clamp-2">{structuredDirection.action}</p>
          </div>

          <div className="p-2.5 rounded-lg bg-[#151b2d] border border-[#23293c]">
            <div className="flex items-center gap-1.5 text-amber-400 font-medium mb-1">
              <Smile className="w-3.5 h-3.5" />
              <span>Mood</span>
            </div>
            <p className="text-slate-300 text-[11px] line-clamp-2">{structuredDirection.mood}</p>
          </div>
        </div>
      )}
    </div>
  );
};
