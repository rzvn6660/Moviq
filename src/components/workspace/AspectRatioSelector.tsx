import React from 'react';
import type { AspectRatio, ModelCapability } from '../../types/video';
import { ASPECT_RATIOS } from '../../constants/presets';
import { Monitor, Smartphone, Square } from 'lucide-react';

interface AspectRatioSelectorProps {
  selectedRatio: AspectRatio;
  setSelectedRatio: (ratio: AspectRatio) => void;
  modelCapability?: ModelCapability;
}

export const AspectRatioSelector: React.FC<AspectRatioSelectorProps> = ({
  selectedRatio,
  setSelectedRatio,
  modelCapability,
}) => {
  const getIcon = (ratio: AspectRatio) => {
    switch (ratio) {
      case '16:9':
        return <Monitor className="w-3.5 h-3.5" aria-hidden="true" />;
      case '9:16':
        return <Smartphone className="w-3.5 h-3.5" aria-hidden="true" />;
      case '1:1':
        return <Square className="w-3.5 h-3.5" aria-hidden="true" />;
    }
  };

  const isSupported = (ratio: AspectRatio) => {
    if (!modelCapability) return true;
    return modelCapability.supportedAspectRatios.includes(ratio);
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label id="aspect-ratio-label" className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
          Aspect Ratio
        </label>
        <span className="text-[10px] text-amber-400 font-mono font-medium">{selectedRatio}</span>
      </div>

      <div className="grid grid-cols-3 gap-1 p-1 bg-[#090e1c] rounded-xl border border-[#23293c]" role="group" aria-labelledby="aspect-ratio-label">
        {ASPECT_RATIOS.map((option) => {
          const isSelected = selectedRatio === option.id;
          const supported = isSupported(option.id);

          return (
            <button
              key={option.id}
              type="button"
              disabled={!supported}
              onClick={() => supported && setSelectedRatio(option.id)}
              aria-pressed={isSelected}
              title={!supported ? `Not supported by ${modelCapability?.name}` : option.label}
              className={`py-1.5 px-2 rounded-lg flex items-center justify-center gap-1.5 transition-all text-xs font-mono font-bold focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-500 ${
                !supported
                  ? 'text-slate-600 cursor-not-allowed opacity-40'
                  : isSelected
                  ? 'bg-[#151b2d] text-amber-300 border border-amber-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#151b2d]/50'
              }`}
            >
              <span className={isSelected ? 'text-amber-400' : 'text-slate-400'}>{getIcon(option.id)}</span>
              <span>{option.id}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

