import React from 'react';
import type { StylePreset } from '../../types/video';
import { STYLE_PRESETS } from '../../constants/presets';
import { Sliders } from 'lucide-react';

interface StyleSelectorProps {
  selectedStyle: StylePreset;
  setSelectedStyle: (style: StylePreset) => void;
}

export const StyleSelector: React.FC<StyleSelectorProps> = ({
  selectedStyle,
  setSelectedStyle,
}) => {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
          <Sliders className="w-3.5 h-3.5 text-amber-400" />
          <span>Style Preset</span>
        </label>
        <span className="text-[11px] text-amber-400 font-mono font-medium">{selectedStyle}</span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {STYLE_PRESETS.map((preset) => {
          const isSelected = selectedStyle === preset.id;
          return (
            <button
              key={preset.id}
              onClick={() => setSelectedStyle(preset.id)}
              className={`p-2.5 rounded-xl text-left transition-all relative overflow-hidden border ${
                isSelected
                  ? 'bg-[#151b2d] border-amber-500/80 ring-1 ring-amber-500/40 shadow-md shadow-amber-500/10'
                  : 'bg-[#0c1324] border-[#23293c] hover:border-slate-600 hover:bg-[#151b2d]/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-xs text-slate-100">{preset.name}</span>
                {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />}
              </div>
              <p className="text-[10px] text-slate-400 line-clamp-1">{preset.description}</p>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono mt-1.5 inline-block">
                {preset.badge}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
