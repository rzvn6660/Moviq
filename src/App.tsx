import { useState, useEffect, useMemo } from 'react';
import { Sparkles, Zap, ShieldCheck } from 'lucide-react';
import { TopNavigation } from './components/layout/TopNavigation';
import { PromptComposer } from './components/workspace/PromptComposer';
import { AIDirector } from './components/workspace/AIDirector';
import { StyleSelector } from './components/workspace/StyleSelector';
import { AspectRatioSelector } from './components/workspace/AspectRatioSelector';
import { DurationSelector } from './components/workspace/DurationSelector';
import { AdvancedSettings } from './components/workspace/AdvancedSettings';
import { VideoPreview } from './components/workspace/VideoPreview';
import { GenerationHistory } from './components/history/GenerationHistory';
import type { 
  UIState, 
  StylePreset, 
  AspectRatio, 
  Duration, 
  VideoItem, 
  StructuredDirection, 
  GenerationProgressStep,
  GenerationProgressInfo,
  ModelCapability
} from './types/video';
import { MoviqApiClient } from './services/apiClient';

import { ProviderHealthPage } from './pages/ProviderHealth';

export function App() {
  // Navigation & Execution Mode State
  const [activeTab, setActiveTab] = useState<'workspace' | 'history' | 'favorites' | 'health'>('workspace');
  const [uiState, setUiState] = useState<UIState>('READY');
  const [executionMode, setExecutionMode] = useState<'safe' | 'live'>('safe');
  const [showLiveConfirmModal, setShowLiveConfirmModal] = useState<boolean>(false);
  const [showRetryConfirmModal, setShowRetryConfirmModal] = useState<boolean>(false);

  // Input & Option State
  const [prompt, setPrompt] = useState<string>(
    'A luxury perfume bottle rotating on black marble with warm golden lighting.'
  );
  const [enhancedPrompt, setEnhancedPrompt] = useState<string>('');
  const [structuredDirection, setStructuredDirection] = useState<StructuredDirection | null>(null);

  const [selectedStyle, setSelectedStyle] = useState<StylePreset>('Cinematic');
  const [selectedRatio, setSelectedRatio] = useState<AspectRatio>('16:9');
  const [selectedDuration, setSelectedDuration] = useState<Duration>('5s');
  const [negativePrompt, setNegativePrompt] = useState<string>('blurry, low resolution, noise, glitchy');

  // Model Capabilities
  const [models, setModels] = useState<ModelCapability[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string>('Wan-AI/Wan2.2-TI2V-5B');

  // History & Completed Output
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [totalHistoryCount, setTotalHistoryCount] = useState<number>(0);
  const [completedVideo, setCompletedVideo] = useState<VideoItem | null>(null);
  const [generationError, setGenerationError] = useState<string | undefined>(undefined);

  // History Search & Filter Options
  const [historyFilter, setHistoryFilter] = useState<'all' | 'favorites' | 'completed' | 'failed' | 'queued'>('all');
  const [historySearch, setHistorySearch] = useState<string>('');
  const [historySort, setHistorySort] = useState<'newest' | 'oldest' | 'alphabetical' | 'generation_date' | 'favorite_date'>('newest');
  const [historyProvider, setHistoryProvider] = useState<string>('');
  const [historyModel, setHistoryModel] = useState<string>('');
  const [isLoadingMoreHistory, setIsLoadingMoreHistory] = useState<boolean>(false);
  const [historyOffset, setHistoryOffset] = useState<number>(0);

  // Progress Tracking
  const [isEnhancing, setIsEnhancing] = useState<boolean>(false);
  const [progressInfo, setProgressInfo] = useState<GenerationProgressInfo | undefined>(undefined);
  const [progressSteps, setProgressSteps] = useState<GenerationProgressStep[]>([
    { id: 1, state: 'QUEUED', title: 'Analyzing idea', description: 'Deconstructing prompt & lighting parameters', status: 'pending' },
    { id: 2, state: 'ENHANCING', title: 'Enhancing direction', description: 'Building AI Director camera keyframes & mood map', status: 'pending' },
    { id: 3, state: 'SUBMITTED', title: 'Preparing generation', description: 'Initializing model latent space', status: 'pending' },
    { id: 4, state: 'GENERATING', title: 'Generating video', description: 'Rendering diffusion frames in high resolution', status: 'pending' },
    { id: 5, state: 'PROCESSING', title: 'Processing output', description: 'Applying color grade & encoding H.264 video container', status: 'pending' }
  ]);

  const [smartFailover, setSmartFailover] = useState<boolean>(false);

  // Current Model Capability
  const currentModelCapability = models.find((m) => m.id === selectedModelId) || models[0];

  // Prompt Quality Analysis
  const promptAnalysis = MoviqApiClient.analyzePrompt(prompt);

  // Synchronize Tab with Filter state
  useEffect(() => {
    if (activeTab === 'favorites') {
      setHistoryFilter('favorites');
    } else if (activeTab === 'history' && historyFilter === 'favorites') {
      setHistoryFilter('all');
    }
  }, [activeTab]);

  // Initial load: Fetch execution mode, model capabilities & history
  useEffect(() => {
    MoviqApiClient.fetchExecutionMode().then((res) => {
      if (res && res.executionMode) {
        setExecutionMode(res.executionMode);
      }
    });

    MoviqApiClient.fetchModelCapabilities().then((loadedModels) => {
      setModels(loadedModels);
      if (loadedModels.length > 0) {
        setSelectedModelId(loadedModels[0].id);
      }
    });
  }, []);

  const handleToggleExecutionMode = async (newMode: 'safe' | 'live') => {
    try {
      const res = await MoviqApiClient.updateExecutionMode(newMode);
      setExecutionMode(res.executionMode);
    } catch (err) {
      console.error("Failed to update execution mode:", err);
      setExecutionMode(newMode);
    }
  };

  // Fetch History whenever search, filters, or sorting changes
  const loadHistory = async (offsetVal = 0, isAppend = false) => {
    try {
      setIsLoadingMoreHistory(true);
      const res = await MoviqApiClient.fetchHistory({
        limit: 20,
        offset: offsetVal,
        search: historySearch,
        filter: historyFilter,
        provider: historyProvider,
        modelId: historyModel,
        sortBy: historySort,
      });

      if (isAppend) {
        setVideos((prev) => [...prev, ...res.generations]);
      } else {
        setVideos(res.generations);
        if (res.generations.length > 0 && !completedVideo) {
          setCompletedVideo(res.generations[0]);
        }
      }
      setTotalHistoryCount(res.totalCount);
      setHistoryOffset(offsetVal);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setIsLoadingMoreHistory(false);
    }
  };

  useEffect(() => {
    loadHistory(0, false);
  }, [historySearch, historyFilter, historySort, historyProvider, historyModel]);

  const handleLoadMoreHistory = () => {
    if (videos.length < totalHistoryCount && !isLoadingMoreHistory) {
      loadHistory(historyOffset + 20, true);
    }
  };

  // Toggle Favorite Optimistic UI & API Update
  const handleToggleFavorite = async (targetVideo: VideoItem) => {
    const newFav = !targetVideo.isFavorite;

    // Optimistic state update
    setVideos((prev) =>
      prev.map((v) => (v.id === targetVideo.id ? { ...v, isFavorite: newFav, favoriteAt: newFav ? new Date().toISOString() : undefined } : v))
    );
    if (completedVideo && completedVideo.id === targetVideo.id) {
      setCompletedVideo({ ...completedVideo, isFavorite: newFav, favoriteAt: newFav ? new Date().toISOString() : undefined });
    }

    try {
      await MoviqApiClient.toggleFavorite(targetVideo.id, newFav);
    } catch (err) {
      console.error("Failed to toggle favorite:", err);
      // Revert optimistic update on error
      setVideos((prev) =>
        prev.map((v) => (v.id === targetVideo.id ? { ...v, isFavorite: targetVideo.isFavorite } : v))
      );
      if (completedVideo && completedVideo.id === targetVideo.id) {
        setCompletedVideo({ ...completedVideo, isFavorite: targetVideo.isFavorite });
      }
    }
  };

  // Delete Generation Handler
  const handleDeleteVideo = async (targetVideo: VideoItem) => {
    await MoviqApiClient.deleteGeneration(targetVideo.id);

    setVideos((prev) => prev.filter((v) => v.id !== targetVideo.id));
    setTotalHistoryCount((prev) => Math.max(0, prev - 1));

    if (completedVideo && completedVideo.id === targetVideo.id) {
      setCompletedVideo(null);
      setUiState('READY');
    }
  };

  // Capability Fallback Validation when Selected Model changes
  useEffect(() => {
    if (!currentModelCapability) return;

    if (!currentModelCapability.supportedAspectRatios.includes(selectedRatio)) {
      setSelectedRatio(currentModelCapability.supportedAspectRatios[0]);
    }

    if (!currentModelCapability.supportedDurations.includes(selectedDuration)) {
      setSelectedDuration(currentModelCapability.supportedDurations[0]);
    }
  }, [selectedModelId, currentModelCapability]);

  // Sync state helper for Dev Switcher dropdown
  const handleDevStateChange = (newState: UIState) => {
    setUiState(newState);
    if (newState === 'COMPLETED' && (!completedVideo && videos.length > 0)) {
      setCompletedVideo(videos[0]);
    } else if (['QUEUED', 'SUBMITTED', 'GENERATING', 'PROCESSING'].includes(newState)) {
      setProgressInfo({
        state: newState,
        currentStepIndex: 4,
        totalSteps: 5,
        stepTitle: 'Generating video',
        stepDescription: 'Rendering diffusion frames in high resolution',
        percentage: newState === 'GENERATING' ? 60 : undefined,
        isDeterminate: newState === 'GENERATING',
        estimatedRemainingSeconds: 6
      });
    }
  };

  // Enhance Prompt via AI Director
  const handleEnhancePrompt = async () => {
    if (!prompt.trim()) return;
    setIsEnhancing(true);
    setUiState('ENHANCING');

    try {
      const res = await MoviqApiClient.enhancePrompt(prompt);
      setEnhancedPrompt(res.enhancedPrompt);
      setStructuredDirection(res.structuredDirection);
      setUiState('READY');
    } catch (err) {
      console.error(err);
      setUiState('FAILED');
    } finally {
      setIsEnhancing(false);
    }
  };

  // Internal Execution Core
  const executeGeneration = async () => {
    if (!prompt.trim()) {
      setUiState('FAILED');
      return;
    }

    setCompletedVideo(null);
    setGenerationError(undefined);
    setUiState('QUEUED');

    try {
      const newVideo = await MoviqApiClient.generateVideo(
        {
          prompt,
          enhancedPrompt: enhancedPrompt || prompt,
          structuredDirection: structuredDirection || undefined,
          style: selectedStyle,
          aspectRatio: selectedRatio,
          duration: selectedDuration,
          negativePrompt: currentModelCapability?.supportsNegativePrompt ? negativePrompt : undefined,
          modelId: selectedModelId,
          smartFailover: smartFailover
        },
        (info, step) => {
          setUiState(info.state);
          setProgressInfo(info);
          setProgressSteps((prev) =>
            prev.map((s) => (s.id === step.id ? { ...s, status: step.status } : s))
          );
        }
      );

      setCompletedVideo(newVideo);
      setVideos((prev) => [newVideo, ...prev]);
      setTotalHistoryCount((prev) => prev + 1);
      setUiState('COMPLETED');
    } catch (err: any) {
      console.error(err);
      setGenerationError(err?.message || 'Video generation could not be completed.');
      setUiState('FAILED');
    }
  };

  // Trigger Video Generation with Safety Checks
  const handleGenerate = () => {
    if (!prompt.trim()) return;

    if (executionMode === 'live') {
      setShowLiveConfirmModal(true);
    } else {
      executeGeneration();
    }
  };

  const handleConfirmLiveGenerate = () => {
    setShowLiveConfirmModal(false);
    executeGeneration();
  };

  // Action handlers
  const handleRegenerate = () => {
    if (executionMode === 'live') {
      setShowRetryConfirmModal(true);
    } else {
      executeGeneration();
    }
  };

  const handleConfirmLiveRetry = () => {
    setShowRetryConfirmModal(false);
    executeGeneration();
  };

  const handleCreateVariation = () => {
    const variationPrompt = `${prompt} [Variation: Dynamic wide angle panning shot with vibrant golden caustics]`;
    setPrompt(variationPrompt);
    setEnhancedPrompt(`${enhancedPrompt} Modified with dynamic wider orbital camera tracking.`);
    setUiState('READY');
  };

  const handleReuseSettings = (videoToReuse?: VideoItem) => {
    const target = videoToReuse || completedVideo;
    if (!target) return;

    setPrompt(target.originalPrompt);
    setEnhancedPrompt(target.enhancedPrompt);
    setStructuredDirection(target.structuredDirection);
    setSelectedStyle(target.style);
    setSelectedRatio(target.aspectRatio);
    setSelectedDuration(target.duration);

    if (target.negativePrompt) {
      setNegativePrompt(target.negativePrompt);
    }

    setActiveTab('workspace');
    setUiState('READY');
  };

  const favoriteCount = useMemo(() => videos.filter((v) => v.isFavorite).length, [videos]);

  return (
    <div className="min-h-screen bg-[#070d1f] text-slate-100 font-sans selection:bg-amber-500/30 selection:text-amber-300">
      {/* Navigation Top Bar */}
      <TopNavigation
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        uiState={uiState}
        setUiState={handleDevStateChange}
        historyCount={totalHistoryCount || videos.length}
        favoriteCount={favoriteCount}
        executionMode={executionMode}
        onToggleExecutionMode={handleToggleExecutionMode}
      />

      {/* Main Container */}
      <main className="w-full">
        {activeTab === 'workspace' ? (
          <div className="max-w-[1750px] mx-auto p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            
            {/* LEFT COLUMN: Creative Direction & Generation Controls */}
            <aside className="lg:col-span-5 space-y-4 bg-[#0c1324] p-4 lg:p-6 rounded-2xl border border-[#23293c] shadow-2xl">
              
              {/* Active Execution Mode Status Banner */}
              <div className={`p-3.5 rounded-xl border flex items-center justify-between gap-3 text-xs transition-all ${
                executionMode === 'safe'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-amber-500/15 border-amber-500/40 text-amber-300'
              }`}>
                <div className="flex items-center gap-2.5">
                  {executionMode === 'safe' ? (
                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : (
                    <Zap className="w-4 h-4 text-amber-400 fill-amber-400 shrink-0 animate-pulse" />
                  )}
                  <div>
                    <span className="font-mono font-bold block text-xs">
                      {executionMode === 'safe' ? 'SAFE MODE • LOCAL SYNTHETIC' : 'LIVE MODE • KIE.AI'}
                    </span>
                    <span className="text-[11px] opacity-80 block font-normal">
                      {executionMode === 'safe'
                        ? 'Testing & UI development. No provider credits consumed.'
                        : 'Generation requests may consume provider credits.'}
                    </span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => handleToggleExecutionMode(executionMode === 'safe' ? 'live' : 'safe')}
                  className="px-2.5 py-1 rounded-lg bg-slate-900/60 hover:bg-slate-900 border border-slate-700/50 text-[11px] font-mono font-semibold transition-colors cursor-pointer shrink-0"
                >
                  Switch to {executionMode === 'safe' ? 'Live' : 'Safe'} Mode
                </button>
              </div>

              {/* Prompt Composer */}
              <PromptComposer
                prompt={prompt}
                setPrompt={setPrompt}
                onEnhance={handleEnhancePrompt}
                isEnhancing={isEnhancing}
                analysis={promptAnalysis}
              />

              {/* AI Director Panel */}
              <AIDirector
                originalPrompt={prompt}
                enhancedPrompt={enhancedPrompt}
                setEnhancedPrompt={setEnhancedPrompt}
                structuredDirection={structuredDirection}
                isEnhancing={isEnhancing}
              />

              {/* Style Selector */}
              <StyleSelector
                selectedStyle={selectedStyle}
                setSelectedStyle={setSelectedStyle}
              />

              {/* Aspect Ratio & Duration */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <AspectRatioSelector
                  selectedRatio={selectedRatio}
                  setSelectedRatio={setSelectedRatio}
                  modelCapability={currentModelCapability}
                />
                <DurationSelector
                  selectedDuration={selectedDuration}
                  setSelectedDuration={setSelectedDuration}
                  modelCapability={currentModelCapability}
                />
              </div>

              {/* Advanced Settings (Negative Prompt, Model & Smart Failover) */}
              <AdvancedSettings
                negativePrompt={negativePrompt}
                setNegativePrompt={setNegativePrompt}
                selectedModelId={selectedModelId}
                setSelectedModelId={setSelectedModelId}
                models={models}
                currentModelCapability={currentModelCapability}
                smartFailover={smartFailover}
                setSmartFailover={setSmartFailover}
              />

              {/* Primary Action Button: Generate Video */}
              <div className="pt-1">
                <button
                  type="button"
                  onClick={handleGenerate}
                  disabled={!prompt.trim() || ['QUEUED', 'SUBMITTED', 'GENERATING', 'PROCESSING'].includes(uiState) || isEnhancing}
                  className={`w-full py-3 px-6 rounded-xl font-bold text-sm tracking-wide transition-all duration-200 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 focus-visible:outline-none focus-visible:ring-2 cursor-pointer ${
                    executionMode === 'live'
                      ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 focus-visible:ring-amber-500 shadow-amber-500/25 hover:shadow-amber-500/40'
                      : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 focus-visible:ring-emerald-500 shadow-emerald-500/20 hover:shadow-emerald-500/35'
                  }`}
                >
                  <Sparkles className="w-4 h-4 text-slate-950 fill-slate-950" aria-hidden="true" />
                  <span className="font-mono uppercase tracking-wider text-xs font-bold">Generate Video</span>
                  <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-950/15 text-slate-950 ml-1">
                    {selectedDuration} • {selectedRatio}
                  </span>
                </button>
              </div>
            </aside>

            {/* RIGHT COLUMN: Video Workspace Stage */}
            <section className="lg:col-span-7 bg-[#0c1324] p-4 lg:p-6 rounded-2xl border border-[#23293c] shadow-2xl min-h-[640px] flex flex-col justify-between">
              <VideoPreview
                uiState={uiState}
                completedVideo={completedVideo}
                progressSteps={progressSteps}
                progressInfo={progressInfo}
                errorMessage={generationError}
                onGenerate={handleGenerate}
                onRegenerate={handleRegenerate}
                onCreateVariation={handleCreateVariation}
                onReuseSettings={() => handleReuseSettings()}
                onToggleFavorite={handleToggleFavorite}
              />
            </section>
          </div>
        ) : activeTab === 'health' ? (
          <ProviderHealthPage />
        ) : (
          /* History & Favorites View */
          <GenerationHistory
            videos={videos}
            totalCount={totalHistoryCount}
            activeFilter={historyFilter}
            setActiveFilter={setHistoryFilter}
            searchQuery={historySearch}
            setSearchQuery={setHistorySearch}
            sortBy={historySort}
            setSortBy={setHistorySort}
            selectedProvider={historyProvider}
            setSelectedProvider={setHistoryProvider}
            selectedModel={historyModel}
            setSelectedModel={setHistoryModel}
            onReuseSettings={(v) => handleReuseSettings(v)}
            onSelectVideo={(v) => {
              setCompletedVideo(v);
              setUiState('COMPLETED');
              setActiveTab('workspace');
            }}
            onToggleFavorite={handleToggleFavorite}
            onDeleteVideo={handleDeleteVideo}
            onNavigateStudio={() => setActiveTab('workspace')}
            onLoadMore={handleLoadMoreHistory}
            hasMore={videos.length < totalHistoryCount}
            isLoadingMore={isLoadingMoreHistory}
          />
        )}
      </main>

      {/* Live Generation Confirmation Modal */}
      {showLiveConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-[#0c1324] border border-amber-500/40 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 shrink-0">
                <Zap className="w-5 h-5 fill-amber-400 animate-pulse" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white font-mono">Live Video Generation</h3>
                <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono font-semibold">
                  LIVE MODE • KIE.AI
                </span>
              </div>
            </div>

            <p className="text-sm text-slate-200 leading-relaxed font-medium">
              Live generation uses Kie.ai credits.
            </p>

            <p className="text-xs text-slate-400 leading-relaxed">
              Proceeding will submit a commercial video task to Kie.ai ({selectedModelId}).
            </p>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowLiveConfirmModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmLiveGenerate}
                className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-mono font-bold tracking-wide transition-all shadow-lg shadow-amber-500/20 cursor-pointer"
              >
                Generate
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Live Retry Confirmation Modal */}
      {showRetryConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-[#0c1324] border border-amber-500/40 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 shrink-0">
                <Zap className="w-5 h-5 fill-amber-400" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white font-mono">Retry Live Generation</h3>
                <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono font-semibold">
                  LIVE MODE • KIE.AI
                </span>
              </div>
            </div>

            <p className="text-sm text-slate-200 leading-relaxed font-medium">
              Retrying will create a new Kie.ai generation and may consume additional credits.
            </p>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowRetryConfirmModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmLiveRetry}
                className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-mono font-bold tracking-wide transition-all shadow-lg shadow-amber-500/20 cursor-pointer"
              >
                Retry Generation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
