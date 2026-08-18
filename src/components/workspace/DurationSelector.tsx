import React from 'react';
import type { Duration, ModelCapability } from '../../types/video';
import { DURATIONS } from '../../constants/presets';
import { Clock } from 'lucide-react';

interface DurationSelectorProps {
  selectedDuration: Duration;
  setSelectedDuration: (duration: Duration) => void;
  modelCapability?: ModelCapability;
}

export const DurationSelector: React.FC<DurationSelectorProps> = ({
  selectedDuration,
  setSelectedDuration,
  modelCapability,
}) => {
  const isSupported = (dur: Duration) => {
    if (!modelCapability) return true;
    return modelCapability.supportedDurations.includes(dur);
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label id="duration-label" className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
          <Clock className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
          <span>Duration</span>
        </label>
        <span className="text-[10px] text-amber-400 font-mono font-medium">{selectedDuration}</span>
      </div>

      <div className="grid grid-cols-3 gap-1 p-1 bg-[#090e1c] rounded-xl border border-[#23293c]" role="group" aria-labelledby="duration-label">
        {DURATIONS.map((dur) => {
          const isSelected = selectedDuration === dur;
          const supported = isSupported(dur);

          return (
            <button
              key={dur}
              type="button"
              disabled={!supported}
              onClick={() => supported && setSelectedDuration(dur)}
              aria-pressed={isSelected}
              title={!supported ? `Not supported by ${modelCapability?.name}` : `${dur} clip`}
              className={`py-1.5 px-2 rounded-lg font-mono text-xs font-bold transition-all text-center focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-500 ${
                !supported
                  ? 'text-slate-600 cursor-not-allowed opacity-40'
                  : isSelected
                  ? 'bg-[#151b2d] text-amber-300 border border-amber-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#151b2d]/50'
              }`}
            >
              {dur}
            </button>
          );
        })}
      </div>
    </div>
  );
};

