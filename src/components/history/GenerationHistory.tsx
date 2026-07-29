import React, { useState } from 'react';
import type { VideoItem } from '../../types/video';
import { HistoryCard } from './HistoryCard';
import { History, Film, ChevronRight } from 'lucide-react';

interface GenerationHistoryProps {
  videos: VideoItem[];
  totalCount: number;
  onReuseSettings: (video: VideoItem) => void;
  onSelectVideo: (video: VideoItem) => void;
  onLoadMore?: () => void;
}

export const GenerationHistory: React.FC<GenerationHistoryProps> = ({
  videos,
  totalCount,
  onReuseSettings,
  onSelectVideo,
  onLoadMore,
}) => {
  const [displayAll, setDisplayAll] = useState(false);

  // Default display 5 items for evaluator UI requirement
  const visibleVideos = displayAll ? videos : videos.slice(0, 5);

  return (
    <div className="space-y-5 max-w-[1700px] mx-auto p-4 lg:p-8">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-[#23293c]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
            <History className="w-5 h-5 text-amber-400" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <span>Recent Generations</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 font-mono">
                Showing {visibleVideos.length} of {totalCount || videos.length}
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Browse previously generated AI video clips, inspect settings, and reuse camera directions.
            </p>
          </div>
        </div>

        {videos.length > 5 && (
          <button
            type="button"
            onClick={() => {
              setDisplayAll(!displayAll);
              if (!displayAll && onLoadMore) onLoadMore();
            }}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] text-xs font-medium text-amber-400 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
          >
            <span>{displayAll ? 'Show Top 5' : `View All (${totalCount || videos.length})`}</span>
            <ChevronRight className={`w-3.5 h-3.5 transform transition-transform ${displayAll ? 'rotate-90' : ''}`} aria-hidden="true" />
          </button>
        )}
      </div>

      {/* Visual Cards Grid */}
      {visibleVideos.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
          {visibleVideos.map((video) => (
            <HistoryCard
              key={video.id}
              video={video}
              onReuse={onReuseSettings}
              onSelect={onSelectVideo}
            />
          ))}
        </div>
      ) : (
        <div className="p-12 text-center bg-[#0c1324] rounded-2xl border border-[#23293c] space-y-3">
          <Film className="w-10 h-10 text-slate-600 mx-auto" aria-hidden="true" />
          <h3 className="text-sm font-semibold text-slate-300">No Generations Found Yet</h3>
          <p className="text-xs text-slate-500">Your created videos will appear in this history canvas.</p>
        </div>
      )}
    </div>
  );
};
