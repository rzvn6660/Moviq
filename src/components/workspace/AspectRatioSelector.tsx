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
        return <Monitor className="w-4 h-4 text-amber-400" aria-hidden="true" />;
      case '9:16':
        return <Smartphone className="w-4 h-4 text-amber-400" aria-hidden="true" />;
      case '1:1':
        return <Square className="w-4 h-4 text-amber-400" aria-hidden="true" />;
    }
  };

  const isSupported = (ratio: AspectRatio) => {
    if (!modelCapability) return true;
    return modelCapability.supportedAspectRatios.includes(ratio);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label id="aspect-ratio-label" className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
          Aspect Ratio
        </label>
        <span className="text-[11px] text-amber-400 font-mono font-medium">{selectedRatio}</span>
      </div>

      <div className="grid grid-cols-3 gap-2" role="group" aria-labelledby="aspect-ratio-label">
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
              className={`p-2.5 rounded-xl flex flex-col items-center justify-center gap-1.5 transition-all border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 ${
                !supported
                  ? 'bg-[#090e1c] border-[#1c2235] text-slate-600 cursor-not-allowed opacity-50'
                  : isSelected
                  ? 'bg-[#151b2d] border-amber-500/80 ring-1 ring-amber-500/40 text-amber-300'
                  : 'bg-[#0c1324] border-[#23293c] text-slate-400 hover:border-slate-600 hover:text-slate-200'
              }`}
            >
              {getIcon(option.id)}
              <span className="text-xs font-mono font-bold">{option.id}</span>
              <span className="text-[9px] text-slate-500">{option.dimensions}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
