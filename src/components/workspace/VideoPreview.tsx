import React, { useState, useRef, useEffect } from 'react';
import type { UIState, VideoItem, GenerationProgressStep, GenerationProgressInfo } from '../../types/video';
import { GenerationProgress } from './GenerationProgress';
import { GenerationInspector } from './GenerationInspector';
import { ErrorState } from './ErrorState';
import {
  Play,
  Pause,
  RotateCcw,
  Download,
  Sparkles,
  Volume2,
  VolumeX,
  Maximize2,
  Film,
  Zap,
  Sliders
} from 'lucide-react';

interface VideoPreviewProps {
  uiState: UIState;
  completedVideo: VideoItem | null;
  progressSteps: GenerationProgressStep[];
  progressInfo?: GenerationProgressInfo;
  onGenerate: () => void;
  onRegenerate: () => void;
  onCreateVariation: () => void;
  onReuseSettings: () => void;
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({
  uiState,
  completedVideo,
  progressSteps,
  progressInfo,
  onGenerate,
  onRegenerate,
  onCreateVariation,
  onReuseSettings,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    setIsPlaying(false);
    setCurrentTime(0);
  }, [completedVideo, uiState]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
      setIsPlaying(false);
    } else {
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
      setDuration(videoRef.current.duration || 0);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleFullscreen = () => {
    if (videoRef.current) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen();
      }
    }
  };

  const handleDownload = () => {
    if (!completedVideo) return;
    const a = document.createElement('a');
    a.href = completedVideo.videoUrl;
    a.download = `${completedVideo.id}.mp4`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const formatTime = (secs: number) => {
    if (isNaN(secs)) return '00:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const isGeneratingPhase = ['QUEUED', 'SUBMITTED', 'GENERATING', 'PROCESSING'].includes(uiState);

  return (
    <div className="w-full h-full flex flex-col justify-between space-y-4">
      {/* Top Stage Bar */}
      <div className="flex items-center justify-between pb-2 border-b border-[#23293c]">
        <div className="flex items-center gap-2">
          <Film className="w-4 h-4 text-amber-400" aria-hidden="true" />
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-100">
            Video Generation Workspace
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-[#151b2d] border border-[#23293c] text-slate-400 font-mono">
            State: <strong className="text-amber-400">{uiState}</strong>
          </span>
        </div>
      </div>

      {/* Main Preview Container */}
      <div className="relative w-full min-h-[400px] lg:min-h-[480px] rounded-2xl bg-[#070d1f] border border-[#23293c] overflow-hidden flex items-center justify-center shadow-2xl">
        {/* Grid lines background */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#151b2d_1px,transparent_1px),linear-gradient(to_bottom,#151b2d_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-30" />

        {/* 1. EMPTY STATE */}
        {uiState === 'EMPTY' && (
          <div className="relative z-10 text-center p-8 max-w-md space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto shadow-xl shadow-amber-500/10">
              <Film className="w-8 h-8 text-amber-400" aria-hidden="true" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-slate-100">Your Stage is Ready</h3>
              <p className="text-xs text-slate-400">
                Type an idea in the prompt composer or pick a sample preset to start generating cinematic video.
              </p>
            </div>
          </div>
        )}

        {/* 2. READY STATE */}
        {uiState === 'READY' && (
          <div className="relative z-10 text-center p-8 max-w-md space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-amber-500/20 border border-amber-500/50 flex items-center justify-center mx-auto shadow-xl shadow-amber-500/20">
              <Zap className="w-8 h-8 text-amber-400 animate-pulse" aria-hidden="true" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-slate-100">Ready to Render</h3>
              <p className="text-xs text-slate-400">
                Click <strong className="text-amber-400">"Generate Video"</strong> on the left control panel to launch the AI pipeline.
              </p>
            </div>
            <button
              type="button"
              onClick={onGenerate}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-bold text-xs hover:from-amber-400 hover:to-amber-500 transition-all shadow-lg shadow-amber-500/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
            >
              Generate Video Now
            </button>
          </div>
        )}

        {/* 3. ENHANCING STATE */}
        {uiState === 'ENHANCING' && (
          <div className="relative z-10 text-center p-8 max-w-md space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-amber-500/20 border border-amber-500/50 flex items-center justify-center mx-auto">
              <Sparkles className="w-8 h-8 text-amber-400 animate-spin" aria-hidden="true" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-slate-100">AI Director at Work</h3>
              <p className="text-xs text-slate-400">
                Synthesizing camera angles, volumetric lighting notes, and structured breakdown...
              </p>
            </div>
          </div>
        )}

        {/* 4. ACTIVE GENERATION PHASES (QUEUED, SUBMITTED, GENERATING, PROCESSING) */}
        {isGeneratingPhase && (
          <div className="relative z-10 w-full h-full flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-gradient-to-b from-amber-500/10 via-transparent to-transparent animate-scanline opacity-60 pointer-events-none" />
            <GenerationProgress steps={progressSteps} progressInfo={progressInfo} />
          </div>
        )}

        {/* 5. COMPLETED STATE */}
        {uiState === 'COMPLETED' && completedVideo && (
          <div className="relative w-full h-full flex flex-col items-center justify-center group">
            <video
              ref={videoRef}
              src={completedVideo.videoUrl}
              poster={completedVideo.thumbnailUrl}
              onTimeUpdate={handleTimeUpdate}
              onEnded={() => setIsPlaying(false)}
              loop
              muted={isMuted}
              aria-label={`Generated video preview: ${completedVideo.originalPrompt}`}
              className="w-full h-full object-contain max-h-[460px]"
            />

            {/* Custom Accessible Video Controls Bar */}
            <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[#070d1f] via-[#070d1f]/80 to-transparent flex flex-col gap-2 transition-opacity duration-300">
              {/* Seek Bar */}
              <input
                type="range"
                min={0}
                max={duration || 100}
                value={currentTime}
                onChange={handleSeek}
                aria-label="Video playback seeker"
                className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={togglePlay}
                    aria-label={isPlaying ? "Pause video" : "Play video"}
                    className="p-2 rounded-lg bg-amber-500 text-slate-950 hover:bg-amber-400 transition-all shadow-md shadow-amber-500/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
                  </button>

                  <button
                    type="button"
                    onClick={toggleMute}
                    aria-label={isMuted ? "Unmute audio" : "Mute audio"}
                    className="text-slate-300 hover:text-white p-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 rounded"
                  >
                    {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                  </button>

                  <span className="text-xs font-mono text-slate-300" aria-label="Playback time">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[11px] px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 font-mono">
                    {completedVideo.style} • {completedVideo.aspectRatio}
                  </span>
                  <button
                    type="button"
                    onClick={handleFullscreen}
                    aria-label="Fullscreen video"
                    className="text-slate-300 hover:text-white p-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 rounded"
                  >
                    <Maximize2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 6. FAILED or TIMED_OUT STATE */}
        {(uiState === 'FAILED' || uiState === 'TIMED_OUT') && (
          <div className="relative z-10 w-full h-full flex items-center justify-center p-4">
            <ErrorState
              type={uiState}
              errorMessage={
                completedVideo?.errorMessage ||
                'Generation request timed out waiting for GPU model allocation. Prompt parameters saved.'
              }
              onRetry={onGenerate}
            />
          </div>
        )}
      </div>

      {/* Completed State Action Toolbar */}
      {uiState === 'COMPLETED' && completedVideo && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 p-3 rounded-xl bg-[#0c1324] border border-[#23293c]">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleDownload}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-amber-500 text-slate-950 font-semibold text-xs hover:bg-amber-400 transition-all shadow-md shadow-amber-500/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              >
                <Download className="w-3.5 h-3.5" aria-hidden="true" />
                <span>Download Video</span>
              </button>

              <button
                type="button"
                onClick={onRegenerate}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] text-slate-200 text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              >
                <RotateCcw className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
                <span>Regenerate</span>
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onCreateVariation}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-amber-500/30 text-amber-300 text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
                <span>Create Variation</span>
              </button>

              <button
                type="button"
                onClick={onReuseSettings}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] text-slate-300 text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              >
                <Sliders className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
                <span>Reuse Settings</span>
              </button>
            </div>
          </div>

          {/* Technical Inspector */}
          <GenerationInspector video={completedVideo} />
        </div>
      )}
    </div>
  );
};
