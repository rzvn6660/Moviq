import React, { useState } from 'react';
import type { VideoItem } from '../../types/video';
import { Play, Download, Sliders, Clock, CheckCircle2 } from 'lucide-react';

interface HistoryCardProps {
  video: VideoItem;
  onReuse: (video: VideoItem) => void;
  onSelect: (video: VideoItem) => void;
}

export const HistoryCard: React.FC<HistoryCardProps> = ({ video, onReuse, onSelect }) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    const a = document.createElement('a');
    a.href = video.videoUrl;
    a.download = `${video.id}.mp4`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div
      onClick={() => onSelect(video)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="group relative rounded-2xl bg-[#0c1324] border border-[#23293c] hover:border-amber-500/50 overflow-hidden transition-all duration-300 shadow-xl cursor-pointer flex flex-col justify-between"
    >
      {/* Thumbnail & Video Preview Aspect Container */}
      <div className="relative w-full aspect-video bg-[#070d1f] overflow-hidden">
        {isHovered ? (
          <video
            src={video.videoUrl}
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover transform scale-105 transition-transform duration-500"
          />
        ) : (
          <img
            src={video.thumbnailUrl}
            alt={video.originalPrompt}
            className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500 opacity-90"
          />
        )}

        {/* Overlay Dark Gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0c1324] via-transparent to-black/30 pointer-events-none" />

        {/* Top Badges */}
        <div className="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between pointer-events-none">
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-950/80 backdrop-blur-md border border-slate-800 text-amber-400 font-mono">
            {video.style}
          </span>
          <div className="flex items-center gap-1">
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-950/80 backdrop-blur-md border border-slate-800 text-slate-300 font-mono">
              {video.aspectRatio}
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 backdrop-blur-md border border-amber-500/40 text-amber-300 font-mono">
              {video.duration}
            </span>
          </div>
        </div>

        {/* Center Hover Play Icon */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="w-10 h-10 rounded-full bg-amber-500/90 text-slate-950 flex items-center justify-center shadow-lg shadow-amber-500/30 transform group-hover:scale-110 transition-transform">
            <Play className="w-5 h-5 ml-0.5 fill-slate-950" />
          </div>
        </div>
      </div>

      {/* Details & Actions Footer */}
      <div className="p-3.5 space-y-2.5">
        <p className="text-xs text-slate-200 line-clamp-2 leading-relaxed font-sans">
          "{video.originalPrompt}"
        </p>

        <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono pt-1 border-t border-[#23293c]/80">
          <div className="flex items-center gap-1.5 text-emerald-400">
            <CheckCircle2 className="w-3 h-3" />
            <span>Ready</span>
          </div>
          <div className="flex items-center gap-1 text-slate-400">
            <Clock className="w-3 h-3" />
            <span>{video.timestamp}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-2 pt-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onReuse(video);
            }}
            className="flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] hover:border-amber-500/30 text-amber-300 text-xs font-medium transition-all"
          >
            <Sliders className="w-3 h-3" />
            <span>Reuse</span>
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] text-slate-300 hover:text-white text-xs font-medium transition-all"
          >
            <Download className="w-3 h-3" />
            <span>Download</span>
          </button>
        </div>
      </div>
    </div>
  );
};
