import { useState, useEffect } from 'react';
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

export function App() {
  // Navigation & State
  const [activeTab, setActiveTab] = useState<'workspace' | 'history'>('workspace');
  const [uiState, setUiState] = useState<UIState>('READY');

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

  // Current Model Capability
  const currentModelCapability = models.find((m) => m.id === selectedModelId) || models[0];

  // Prompt Quality Analysis
  const promptAnalysis = MoviqApiClient.analyzePrompt(prompt);

  // Initial load: Fetch model capabilities & history (limit 5 for evaluator requirement)
  useEffect(() => {
    MoviqApiClient.fetchModelCapabilities().then((loadedModels) => {
      setModels(loadedModels);
      if (loadedModels.length > 0) {
        setSelectedModelId(loadedModels[0].id);
      }
    });

    MoviqApiClient.fetchHistory(5).then((data) => {
      setVideos(data.generations);
      setTotalHistoryCount(data.totalCount);
      if (data.generations.length > 0 && !completedVideo) {
        setCompletedVideo(data.generations[0]);
      }
    });
  }, []);

  // Capability Fallback Validation when Selected Model changes
  useEffect(() => {
    if (!currentModelCapability) return;

    // Fallback aspect ratio if current ratio is unsupported by new model
    if (!currentModelCapability.supportedAspectRatios.includes(selectedRatio)) {
      setSelectedRatio(currentModelCapability.supportedAspectRatios[0]);
    }

    // Fallback duration if current duration is unsupported by new model
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

  // Trigger Video Generation
  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setUiState('FAILED');
      return;
    }

    setCompletedVideo(null);
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
          modelId: selectedModelId
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
    } catch (err) {
      console.error(err);
      setUiState('FAILED');
    }
  };

  // Action handlers
  const handleRegenerate = () => {
    handleGenerate();
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

  return (
    <div className="min-h-screen bg-[#070d1f] text-slate-100 font-sans selection:bg-amber-500/30 selection:text-amber-300">
      {/* Navigation Top Bar */}
      <TopNavigation
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        uiState={uiState}
        setUiState={handleDevStateChange}
        historyCount={totalHistoryCount || videos.length}
      />

      {/* Main Container */}
      <main className="w-full">
        {activeTab === 'workspace' ? (
          <div className="max-w-[1750px] mx-auto p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            
            {/* LEFT COLUMN: Creative Direction & Generation Controls */}
            <aside className="lg:col-span-5 space-y-4 bg-[#0c1324] p-4 lg:p-6 rounded-2xl border border-[#23293c] shadow-2xl">
              
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

              {/* Advanced Settings (Negative Prompt & Model) */}
              <AdvancedSettings
                negativePrompt={negativePrompt}
                setNegativePrompt={setNegativePrompt}
                selectedModelId={selectedModelId}
                setSelectedModelId={setSelectedModelId}
                models={models}
                currentModelCapability={currentModelCapability}
              />

              {/* Primary Action Button: Generate Video */}
              <div className="pt-2">
                <button
                  type="button"
                  onClick={handleGenerate}
                  disabled={!prompt.trim() || ['QUEUED', 'SUBMITTED', 'GENERATING', 'PROCESSING'].includes(uiState) || isEnhancing}
                  className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-amber-500 via-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-sm tracking-wide transition-all duration-200 shadow-xl shadow-amber-500/25 hover:shadow-amber-500/40 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
                >
                  <span className="uppercase tracking-wider">Generate Video</span>
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
                onGenerate={handleGenerate}
                onRegenerate={handleRegenerate}
                onCreateVariation={handleCreateVariation}
                onReuseSettings={() => handleReuseSettings()}
              />
            </section>
          </div>
        ) : (
          /* Evaluator History View (Shows Top 5 by default) */
          <GenerationHistory
            videos={videos}
            totalCount={totalHistoryCount}
            onReuseSettings={(v) => handleReuseSettings(v)}
            onSelectVideo={(v) => {
              setCompletedVideo(v);
              setUiState('COMPLETED');
              setActiveTab('workspace');
            }}
          />
        )}
      </main>
    </div>
  );
}

export default App;
