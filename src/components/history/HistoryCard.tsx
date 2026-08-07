import React, { useState } from 'react';
import type { VideoItem } from '../../types/video';
import { 
  Play, 
  Download, 
  Sliders, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  XCircle, 
  Loader2, 
  Star, 
  Trash2, 
  Eye, 
  ChevronDown, 
  ChevronUp, 
  Sparkles, 
  Film 
} from 'lucide-react';
import { resolveMediaUrl, formatRelativeTime, triggerFileDownload } from '../../utils/formatters';

interface HistoryCardProps {
  video: VideoItem;
  version?: number;
  onReuse: (video: VideoItem) => void;
  onSelect: (video: VideoItem) => void;
  onDelete: (video: VideoItem) => void;
  onToggleFavorite: (video: VideoItem) => void;
}

export const HistoryCard: React.FC<HistoryCardProps> = ({
  video,
  version,
  onReuse,
  onSelect,
  onDelete,
  onToggleFavorite,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [imgError, setImgError] = useState(false);

  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation();
    const downloadUrl = resolveMediaUrl(`/api/v1/generations/${video.id}/download`);
    await triggerFileDownload(downloadUrl, `moviq-${video.id}.mp4`);
  };

  const handleToggleFav = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleFavorite(video);
  };

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(video);
  };

  const handleReuseClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onReuse(video);
  };

  const handleSelectClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSelect(video);
  };

  // Status Badge Config
  const getStatusBadge = () => {
    const st = (video.status || 'completed').toLowerCase();
    switch (st) {
      case 'completed':
        return (
          <span className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono">
            <CheckCircle2 className="w-3 h-3" />
            <span>Completed</span>
          </span>
        );
      case 'generating':
      case 'processing':
      case 'submitted':
        return (
          <span className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 font-mono animate-pulse">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span className="capitalize">{st}</span>
          </span>
        );
      case 'queued':
        return (
          <span className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 font-mono">
            <Clock className="w-3 h-3" />
            <span>Queued</span>
          </span>
        );
      case 'failed':
        return (
          <span className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 font-mono">
            <AlertCircle className="w-3 h-3" />
            <span>Failed</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-slate-500/10 border border-slate-500/30 text-slate-400 font-mono">
            <XCircle className="w-3 h-3" />
            <span className="capitalize">{st}</span>
          </span>
        );
    }
  };

  const resolvedThumb = resolveMediaUrl(video.thumbnailUrl);
  const resolvedVideo = resolveMediaUrl(video.videoUrl);

  return (
    <div
      tabIndex={0}
      role="button"
      aria-label={`Generation: ${video.originalPrompt}`}
      onClick={() => onSelect(video)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect(video);
        }
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="group relative rounded-2xl bg-[#0c1324] border border-[#23293c] hover:border-amber-500/50 overflow-hidden transition-all duration-300 shadow-xl hover:shadow-2xl hover:shadow-amber-500/10 transform hover:-translate-y-0.5 hover:scale-[1.01] cursor-pointer flex flex-col justify-between focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
    >
      {/* Top Media Aspect Container */}
      <div className="relative w-full aspect-video bg-[#070d1f] overflow-hidden">
        {isHovered && resolvedVideo ? (
          <video
            src={resolvedVideo}
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover transform scale-105 transition-transform duration-500"
          />
        ) : !imgError && resolvedThumb ? (
          <img
            src={resolvedThumb}
            alt=""
            onError={() => setImgError(true)}
            className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500 opacity-90"
          />
        ) : (
          /* Placeholder fallback when frame extraction/thumb unavailable */
          <div className="w-full h-full flex flex-col items-center justify-center p-4 bg-gradient-to-br from-[#0c1324] via-[#151b2d] to-[#070d1f] space-y-2 text-center">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Film className="w-5 h-5" />
            </div>
            <span className="text-[11px] font-mono text-slate-400 tracking-wide uppercase">
              {video.metadata?.model?.split('/')[1] || video.metadata?.model || 'Wan 2.2'}
            </span>
          </div>
        )}

        {/* Overlay Dark Gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0c1324] via-transparent to-black/40 pointer-events-none" />

        {/* Top Floating Badges & Favorite Star */}
        <div className="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between z-10">
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-950/80 backdrop-blur-md border border-slate-800 text-amber-400 font-mono font-medium">
              {video.style}
            </span>
            {(video.isSynthetic || video.metadata?.isSynthetic) && (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-950/90 backdrop-blur-md border border-indigo-500/40 text-indigo-300 font-mono font-semibold">
                Synthetic Preview
              </span>
            )}
            {version && version > 1 && (
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-500/20 backdrop-blur-md border border-amber-500/40 text-amber-300 font-mono font-bold">
                v{version}
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={handleToggleFav}
              aria-label={video.isFavorite ? "Remove from Favorites" : "Add to Favorites"}
              className={`p-1.5 rounded-full backdrop-blur-md transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 ${
                video.isFavorite
                  ? 'bg-amber-500/30 border border-amber-400 text-amber-400 shadow-lg shadow-amber-500/30 scale-110'
                  : 'bg-slate-950/70 border border-slate-800 text-slate-400 hover:text-amber-400 hover:scale-110'
              }`}
            >
              <Star className={`w-3.5 h-3.5 ${video.isFavorite ? 'fill-amber-400 text-amber-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Center Hover Play Icon */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="w-10 h-10 rounded-full bg-amber-500/90 text-slate-950 flex items-center justify-center shadow-lg shadow-amber-500/40 transform group-hover:scale-110 transition-transform">
            <Play className="w-5 h-5 ml-0.5 fill-slate-950" />
          </div>
        </div>

        {/* Bottom Media Badges */}
        <div className="absolute bottom-2 left-2.5 right-2.5 flex items-center justify-between text-[10px] text-slate-300 font-mono pointer-events-none">
          <span className="px-2 py-0.5 rounded bg-slate-950/80 backdrop-blur-md border border-slate-800">
            {video.aspectRatio}
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-950/80 backdrop-blur-md border border-slate-800">
            {video.duration}
          </span>
        </div>
      </div>

      {/* Details & Info Section */}
      <div className="p-4 space-y-3 flex-1 flex flex-col justify-between">
        <div className="space-y-2">
          {/* Prompt Header */}
          <div className="flex items-start justify-between gap-2">
            <p className="text-xs text-slate-100 line-clamp-2 leading-relaxed font-sans font-medium">
              "{video.originalPrompt}"
            </p>
          </div>

          {/* Collapsible Director Enhanced Prompt */}
          {video.enhancedPrompt && video.enhancedPrompt !== video.originalPrompt && (
            <div className="pt-1">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsExpanded(!isExpanded);
                }}
                className="flex items-center gap-1 text-[11px] text-amber-400/90 hover:text-amber-300 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-500 rounded"
              >
                <Sparkles className="w-3 h-3" />
                <span>{isExpanded ? 'Hide Director Prompt' : 'View Enhanced Prompt'}</span>
                {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>

              {isExpanded && (
                <div className="mt-1.5 p-2.5 rounded-lg bg-[#070d1f] border border-[#23293c] text-[11px] text-slate-300 font-sans leading-relaxed animate-fadeIn">
                  {video.enhancedPrompt}
                </div>
              )}
            </div>
          )}

          {/* Metadata Badges Bar */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[10px] font-mono text-slate-400">
            <span className="px-2 py-0.5 rounded bg-[#151b2d] border border-[#23293c]">
              Provider: <strong className="text-slate-200">
                {video.isSynthetic || video.metadata?.isSynthetic ? 'Synthetic Preview' : (video.metadata?.provider || 'fal-ai')}
              </strong>
            </span>
            <span className="px-2 py-0.5 rounded bg-[#151b2d] border border-[#23293c]">
              Model: <strong className="text-slate-200">{video.metadata?.model?.split('/')[1] || video.metadata?.model || 'Wan2.2'}</strong>
            </span>
            {video.fidelityLabel && (
              <span className={`px-2 py-0.5 rounded border ${
                video.fidelityLabel === 'Low Prompt Fidelity'
                  ? 'bg-rose-500/10 border-rose-500/30 text-rose-300 font-bold'
                  : 'bg-[#151b2d] border-[#23293c] text-slate-300'
              }`}>
                Fidelity: <strong>{video.fidelityLabel}</strong>
              </span>
            )}
            {video.metadata?.generationTimeSeconds && (
              <span className="px-2 py-0.5 rounded bg-[#151b2d] border border-[#23293c]">
                Time: <strong className="text-amber-400">{video.metadata.generationTimeSeconds}s</strong>
              </span>
            )}
          </div>
        </div>

        {/* Status & Relative Timestamp Footer */}
        <div className="pt-2 border-t border-[#23293c]/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <div>{getStatusBadge()}</div>
          <div className="flex items-center gap-1 text-slate-400">
            <Clock className="w-3 h-3" />
            <span>{formatRelativeTime(video.timestamp)}</span>
          </div>
        </div>

        {/* Action Toolbar Grid */}
        <div className="grid grid-cols-4 gap-1.5 pt-1">
          <button
            type="button"
            onClick={handleSelectClick}
            aria-label="View video details"
            className="flex items-center justify-center gap-1 py-1.5 px-2 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] text-slate-300 hover:text-white text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-500"
          >
            <Eye className="w-3 h-3 text-amber-400" />
            <span className="hidden sm:inline">View</span>
          </button>

          <button
            type="button"
            onClick={handleDownload}
            aria-label="Download MP4 video"
            className="flex items-center justify-center gap-1 py-1.5 px-2 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] text-slate-300 hover:text-white text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-500"
          >
            <Download className="w-3 h-3 text-slate-300" />
            <span className="hidden sm:inline">Download</span>
          </button>

          <button
            type="button"
            onClick={handleReuseClick}
            aria-label="Reuse generation settings"
            className="flex items-center justify-center gap-1 py-1.5 px-2 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] text-amber-300 text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-500"
          >
            <Sliders className="w-3 h-3 text-amber-400" />
            <span className="hidden sm:inline">Reuse</span>
          </button>

          <button
            type="button"
            onClick={handleDeleteClick}
            aria-label="Delete video generation"
            className="flex items-center justify-center gap-1 py-1.5 px-2 rounded-lg bg-[#151b2d] hover:bg-rose-500/20 border border-[#23293c] hover:border-rose-500/40 text-slate-400 hover:text-rose-300 text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-rose-500"
          >
            <Trash2 className="w-3 h-3" />
            <span className="hidden sm:inline">Delete</span>
          </button>
        </div>
      </div>
    </div>
  );
};
