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
  const currentPreset = STYLE_PRESETS.find((p) => p.id === selectedStyle) || STYLE_PRESETS[0];

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label id="style-preset-label" className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
          <Sliders className="w-3.5 h-3.5 text-amber-400" />
          <span>Style Preset</span>
        </label>
        <span className="text-[10px] text-amber-400 font-mono font-medium">{selectedStyle}</span>
      </div>

      {/* Compact Segmented Buttons */}
      <div className="grid grid-cols-4 gap-1.5 p-1 bg-[#090e1c] rounded-xl border border-[#23293c]" role="group" aria-labelledby="style-preset-label">
        {STYLE_PRESETS.map((preset) => {
          const isSelected = selectedStyle === preset.id;
          return (
            <button
              key={preset.id}
              type="button"
              onClick={() => setSelectedStyle(preset.id)}
              aria-pressed={isSelected}
              className={`py-1.5 px-2 rounded-lg text-xs font-medium transition-all text-center focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-500 ${
                isSelected
                  ? 'bg-[#151b2d] text-amber-300 border border-amber-500/40 shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#151b2d]/50'
              }`}
            >
              {preset.name}
            </button>
          );
        })}
      </div>

      {/* Selected Style Subtitle */}
      {currentPreset && (
        <p className="text-[11px] text-slate-400 font-sans px-1 line-clamp-1">
          <span className="text-amber-400 font-mono font-medium">{currentPreset.name}:</span> {currentPreset.description}
        </p>
      )}
    </div>
  );
};

