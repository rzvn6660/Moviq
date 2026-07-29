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
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label id="duration-label" className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
          <span>Duration</span>
        </label>
        <span className="text-[11px] text-amber-400 font-mono font-medium">{selectedDuration}</span>
      </div>

      <div className="grid grid-cols-3 gap-2" role="group" aria-labelledby="duration-label">
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
              className={`py-2 px-3 rounded-xl font-mono text-xs font-semibold transition-all border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 ${
                !supported
                  ? 'bg-[#090e1c] border-[#1c2235] text-slate-600 cursor-not-allowed opacity-50'
                  : isSelected
                  ? 'bg-[#151b2d] border-amber-500/80 text-amber-400 ring-1 ring-amber-500/30'
                  : 'bg-[#0c1324] border-[#23293c] text-slate-400 hover:border-slate-600 hover:text-slate-200'
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
