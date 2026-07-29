import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Cpu, ShieldAlert, Sparkles } from 'lucide-react';
import type { ModelCapability } from '../../types/video';

interface AdvancedSettingsProps {
  negativePrompt: string;
  setNegativePrompt: (val: string) => void;
  selectedModelId: string;
  setSelectedModelId: (val: string) => void;
  models: ModelCapability[];
  currentModelCapability?: ModelCapability;
}

export const AdvancedSettings: React.FC<AdvancedSettingsProps> = ({
  negativePrompt,
  setNegativePrompt,
  selectedModelId,
  setSelectedModelId,
  models,
  currentModelCapability,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const supportsNegative = currentModelCapability ? currentModelCapability.supportsNegativePrompt : true;

  return (
    <div className="rounded-xl bg-[#0c1324] border border-[#23293c] overflow-hidden transition-all">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        className="w-full px-4 py-3 flex items-center justify-between text-xs font-semibold text-slate-300 hover:text-slate-100 hover:bg-[#151b2d]/50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
      >
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-amber-400" aria-hidden="true" />
          <span>Advanced Engine Controls & Model Settings</span>
        </div>
        {isOpen ? (
          <ChevronUp className="w-4 h-4 text-slate-400" aria-hidden="true" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" aria-hidden="true" />
        )}
      </button>

      {isOpen && (
        <div className="p-4 border-t border-[#23293c] space-y-3.5 bg-[#090e1c]/80 text-xs">
          {/* AI Engine Model Picker */}
          <div className="space-y-1.5">
            <label htmlFor="model-picker-select" className="text-[11px] font-medium text-slate-300 flex items-center justify-between">
              <span>AI Video Engine Model</span>
              <span className="text-[10px] text-amber-400 font-mono">Capability Reactive</span>
            </label>
            <select
              id="model-picker-select"
              value={selectedModelId}
              onChange={(e) => setSelectedModelId(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[#151b2d] border border-[#23293c] text-xs text-slate-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 font-mono cursor-pointer"
            >
              {models.map((m) => (
                <option key={m.id} value={m.id} className="bg-[#0c1324] text-slate-200">
                  {m.name} ({m.provider}) - {m.tag}
                </option>
              ))}
            </select>
            {currentModelCapability?.renderProfileDescription && (
              <div className="flex items-center gap-1.5 text-[10px] text-amber-400 font-mono pt-1">
                <Sparkles className="w-3 h-3" />
                <span>Validated Render Profile: {currentModelCapability.renderProfileDescription}</span>
              </div>
            )}
          </div>

          {/* Negative Prompt Field */}
          <div className="space-y-1.5">
            <label htmlFor="negative-prompt-input" className="text-[11px] font-medium text-slate-300 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-500" aria-hidden="true" />
                <span>Negative Prompt (Elements to avoid)</span>
              </span>
              {!supportsNegative && (
                <span className="text-[10px] text-slate-500 italic">Not supported by selected model</span>
              )}
            </label>
            <input
              id="negative-prompt-input"
              type="text"
              disabled={!supportsNegative}
              value={negativePrompt}
              onChange={(e) => setNegativePrompt(e.target.value)}
              placeholder={supportsNegative ? "e.g. blurry, oversaturated, noise, extra limbs" : "Managed automatically by model provider"}
              className={`w-full px-3 py-2 rounded-lg bg-[#151b2d] border border-[#23293c] text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 ${
                !supportsNegative ? 'opacity-50 cursor-not-allowed bg-[#090e1c]' : ''
              }`}
            />
          </div>
        </div>
      )}
    </div>
  );
};
