import React, { useState, useMemo } from 'react';
import type { VideoItem } from '../../types/video';
import { HistoryCard } from './HistoryCard';
import { DeleteConfirmModal } from './DeleteConfirmModal';
import { computePromptVersions } from '../../utils/formatters';
import { 
  History, 
  Film, 
  Star, 
  Search, 
  Filter, 
  Plus, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  X 
} from 'lucide-react';

interface GenerationHistoryProps {
  videos: VideoItem[];
  totalCount: number;
  activeFilter: 'all' | 'favorites' | 'completed' | 'failed' | 'queued';
  setActiveFilter: (filter: 'all' | 'favorites' | 'completed' | 'failed' | 'queued') => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  sortBy: 'newest' | 'oldest' | 'alphabetical' | 'generation_date' | 'favorite_date';
  setSortBy: (sort: 'newest' | 'oldest' | 'alphabetical' | 'generation_date' | 'favorite_date') => void;
  selectedProvider: string;
  setSelectedProvider: (provider: string) => void;
  selectedModel: string;
  setSelectedModel: (model: string) => void;
  onReuseSettings: (video: VideoItem) => void;
  onSelectVideo: (video: VideoItem) => void;
  onToggleFavorite: (video: VideoItem) => void;
  onDeleteVideo: (video: VideoItem) => Promise<void>;
  onNavigateStudio: () => void;
  onLoadMore?: () => void;
  hasMore?: boolean;
  isLoadingMore?: boolean;
}

export const GenerationHistory: React.FC<GenerationHistoryProps> = ({
  videos,
  totalCount,
  activeFilter,
  setActiveFilter,
  searchQuery,
  setSearchQuery,
  sortBy,
  setSortBy,
  selectedProvider,
  setSelectedProvider,
  selectedModel,
  setSelectedModel,
  onReuseSettings,
  onSelectVideo,
  onToggleFavorite,
  onDeleteVideo,
  onNavigateStudio,
  onLoadMore,
  hasMore = false,
  isLoadingMore = false,
}) => {
  const [videoToDelete, setVideoToDelete] = useState<VideoItem | null>(null);

  // Compute version numbers for duplicate prompts
  const versionMap = useMemo(() => computePromptVersions(videos), [videos]);

  // Extract unique providers and models for dropdown filters
  const uniqueProviders = useMemo(() => {
    const set = new Set<string>();
    videos.forEach(v => {
      if (v.metadata?.provider) set.add(v.metadata.provider);
    });
    return Array.from(set);
  }, [videos]);

  const uniqueModels = useMemo(() => {
    const set = new Set<string>();
    videos.forEach(v => {
      if (v.metadata?.model) set.add(v.metadata.model);
    });
    return Array.from(set);
  }, [videos]);

  const resetFilters = () => {
    setSearchQuery('');
    setActiveFilter('all');
    setSelectedProvider('');
    setSelectedModel('');
    setSortBy('newest');
  };

  const isFilterActive = searchQuery || activeFilter !== 'all' || selectedProvider || selectedModel || sortBy !== 'newest';

  return (
    <div className="space-y-6 max-w-[1750px] mx-auto p-4 lg:p-8 animate-fadeIn">
      {/* Page Title & Stats Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-[#23293c]">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-amber-500/20 to-amber-700/20 border border-amber-500/30 flex items-center justify-center text-amber-400 shadow-xl shadow-amber-500/10">
            {activeFilter === 'favorites' ? <Star className="w-6 h-6 fill-amber-400 text-amber-400" /> : <History className="w-6 h-6" />}
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <span>{activeFilter === 'favorites' ? '⭐ Saved Favorites' : 'Recent Generations'}</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 font-mono font-medium">
                {totalCount} {totalCount === 1 ? 'item' : 'items'}
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              {activeFilter === 'favorites'
                ? 'Your curated collection of top-tier AI video generations.'
                : 'Search, filter, inspect settings, and reuse camera directions from past generations.'}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onNavigateStudio}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
        >
          <Plus className="w-4 h-4" />
          <span>Create New Video</span>
        </button>
      </div>

      {/* Search, Filter Bar & Controls */}
      <div className="p-4 rounded-2xl bg-[#0c1324] border border-[#23293c] space-y-4 shadow-xl">
        {/* Top Controls Row */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
          {/* Search Input */}
          <div className="md:col-span-5 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search prompts or direction keywords..."
              className="w-full pl-10 pr-9 py-2.5 rounded-xl bg-[#070d1f] border border-[#23293c] focus:border-amber-500 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition-all"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Provider Filter */}
          <div className="md:col-span-3">
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="w-full py-2.5 px-3 rounded-xl bg-[#070d1f] border border-[#23293c] text-xs text-slate-300 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 cursor-pointer"
            >
              <option value="">All Providers</option>
              {uniqueProviders.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          {/* Model Filter */}
          <div className="md:col-span-2">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full py-2.5 px-3 rounded-xl bg-[#070d1f] border border-[#23293c] text-xs text-slate-300 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 cursor-pointer"
            >
              <option value="">All Models</option>
              {uniqueModels.map(m => (
                <option key={m} value={m}>{m.split('/')[1] || m}</option>
              ))}
            </select>
          </div>

          {/* Sorting */}
          <div className="md:col-span-2">
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="w-full py-2.5 px-3 pr-8 rounded-xl bg-[#070d1f] border border-[#23293c] text-xs text-amber-400 font-medium focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 cursor-pointer"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="favorite_date">Favorite Date</option>
                <option value="alphabetical">Alphabetical</option>
              </select>
            </div>
          </div>
        </div>

        {/* Filter Pills Bar */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-[#23293c]/80">
          <div className="flex flex-wrap items-center gap-1.5" role="tablist" aria-label="History Filters">
            <button
              type="button"
              onClick={() => setActiveFilter('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeFilter === 'all'
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20'
                  : 'bg-[#070d1f] border border-[#23293c] text-slate-400 hover:text-slate-200'
              }`}
            >
              All ({totalCount})
            </button>

            <button
              type="button"
              onClick={() => setActiveFilter('favorites')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeFilter === 'favorites'
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20'
                  : 'bg-[#070d1f] border border-amber-500/30 text-amber-300 hover:bg-amber-500/10'
              }`}
            >
              <Star className={`w-3.5 h-3.5 ${activeFilter === 'favorites' ? 'fill-slate-950' : 'fill-amber-400 text-amber-400'}`} />
              <span>Favorites</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveFilter('completed')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeFilter === 'completed'
                  ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20'
                  : 'bg-[#070d1f] border border-[#23293c] text-slate-400 hover:text-slate-200'
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Completed</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveFilter('queued')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeFilter === 'queued'
                  ? 'bg-indigo-500 text-white font-bold shadow-md shadow-indigo-500/20'
                  : 'bg-[#070d1f] border border-[#23293c] text-slate-400 hover:text-slate-200'
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Queued / In Progress</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveFilter('failed')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeFilter === 'failed'
                  ? 'bg-rose-500 text-white font-bold shadow-md shadow-rose-500/20'
                  : 'bg-[#070d1f] border border-[#23293c] text-slate-400 hover:text-slate-200'
              }`}
            >
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Failed</span>
            </button>
          </div>

          {isFilterActive && (
            <button
              type="button"
              onClick={resetFilters}
              className="text-xs text-amber-400 hover:text-amber-300 font-mono underline"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Visual Cards Grid */}
      {videos.length > 0 ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {videos.map((video) => (
              <HistoryCard
                key={video.id}
                video={video}
                version={versionMap.get(video.id)}
                onReuse={onReuseSettings}
                onSelect={onSelectVideo}
                onDelete={(v) => setVideoToDelete(v)}
                onToggleFavorite={onToggleFavorite}
              />
            ))}
          </div>

          {/* Load More Pagination / Lazy Loading */}
          {hasMore && onLoadMore && (
            <div className="text-center pt-4">
              <button
                type="button"
                onClick={onLoadMore}
                disabled={isLoadingMore}
                className="px-6 py-2.5 rounded-xl bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] hover:border-amber-500/40 text-amber-400 font-semibold text-xs transition-all shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              >
                {isLoadingMore ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Loading more generations...</span>
                  </span>
                ) : (
                  <span>Load More Generations ({videos.length} of {totalCount})</span>
                )}
              </button>
            </div>
          )}
        </div>
      ) : (
        /* Empty State Views */
        <div className="p-16 text-center bg-[#0c1324] rounded-2xl border border-[#23293c] space-y-4 max-w-md mx-auto shadow-2xl">
          {activeFilter === 'favorites' ? (
            <>
              <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto text-amber-400 shadow-xl shadow-amber-500/10">
                <Star className="w-8 h-8 fill-amber-400" />
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-bold text-slate-100">No favorite videos yet.</h3>
                <p className="text-xs text-slate-400">
                  Click the star (⭐) on any completed generation to save it to your favorites collection.
                </p>
              </div>
              <button
                type="button"
                onClick={onNavigateStudio}
                className="px-6 py-2.5 rounded-xl bg-amber-500 text-slate-950 font-bold text-xs hover:bg-amber-400 transition-all shadow-lg shadow-amber-500/20"
              >
                Go to Studio
              </button>
            </>
          ) : isFilterActive ? (
            <>
              <div className="w-16 h-16 rounded-2xl bg-slate-800/50 border border-slate-700 flex items-center justify-center mx-auto text-slate-400">
                <Filter className="w-8 h-8" />
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-bold text-slate-100">No matching generations found.</h3>
                <p className="text-xs text-slate-400">
                  No video results match your current search query or active filter selections.
                </p>
              </div>
              <button
                type="button"
                onClick={resetFilters}
                className="px-6 py-2.5 rounded-xl bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] text-amber-400 font-semibold text-xs transition-all"
              >
                Reset All Filters
              </button>
            </>
          ) : (
            <>
              <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto text-amber-400 shadow-xl shadow-amber-500/10">
                <Film className="w-8 h-8" />
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-bold text-slate-100">No videos generated yet.</h3>
                <p className="text-xs text-slate-400">
                  Launch your first cinematic AI video project in Create Studio to begin building your history library.
                </p>
              </div>
              <button
                type="button"
                onClick={onNavigateStudio}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-bold text-xs hover:from-amber-400 hover:to-amber-500 transition-all shadow-lg shadow-amber-500/20"
              >
                Create Studio
              </button>
            </>
          )}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        video={videoToDelete}
        onClose={() => setVideoToDelete(null)}
        onConfirmDelete={onDeleteVideo}
      />
    </div>
  );
};
