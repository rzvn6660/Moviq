export type UIState = 
  | 'EMPTY' 
  | 'READY' 
  | 'QUEUED'
  | 'ENHANCING' 
  | 'SUBMITTED'
  | 'GENERATING' 
  | 'PROCESSING'
  | 'COMPLETED' 
  | 'FAILED' 
  | 'TIMED_OUT';

export type StylePreset = 'Cinematic' | 'Realistic' | 'Anime' | '3D';
export type AspectRatio = '16:9' | '9:16' | '1:1';
export type Duration = '5s' | '10s' | '15s';

export interface ModelCapability {
  id: string;
  name: string;
  provider: string;
  tag: string;
  description: string;
  supportedAspectRatios: AspectRatio[];
  supportedDurations: Duration[];
  supportsNegativePrompt: boolean;
  maxDurationSeconds?: number;
  renderProfileDescription?: string;
  isAvailable: boolean;
}

export interface StructuredDirection {
  subject: string;
  environment: string;
  action: string;
  camera: string;
  lighting: string;
  mood: string;
}

export interface PromptAnalysis {
  score: number; // 0 - 100
  label: 'Basic' | 'Moderate' | 'Detailed' | 'Director Level';
  feedback: string[];
}

export interface GenerationProgressStep {
  id: number;
  state: UIState;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'completed';
}

export interface GenerationProgressInfo {
  state: UIState;
  currentStepIndex: number;
  totalSteps: number;
  stepTitle: string;
  stepDescription: string;
  percentage?: number; // Undefined when progress is stage-based / indeterminate
  isDeterminate: boolean;
  estimatedRemainingSeconds?: number;
}

export interface GenerationMetadata {
  id: string;
  model: string;
  provider: string;
  style: StylePreset;
  aspectRatio: AspectRatio;
  duration: Duration;
  generationTimeSeconds: number;
  createdAt: string;
  resolution: string;
  fps: number;
}

export interface VideoItem {
  id: string;
  originalPrompt: string;
  enhancedPrompt: string;
  structuredDirection: StructuredDirection;
  videoUrl: string;
  thumbnailUrl: string;
  style: StylePreset;
  aspectRatio: AspectRatio;
  duration: Duration;
  negativePrompt?: string;
  status: 'completed' | 'generating' | 'failed' | 'timed_out';
  timestamp: string;
  metadata: GenerationMetadata;
  errorMessage?: string;
}

export interface GenerationRequest {
  prompt: string;
  enhancedPrompt?: string;
  structuredDirection?: StructuredDirection;
  style: StylePreset;
  aspectRatio: AspectRatio;
  duration: Duration;
  negativePrompt?: string;
  modelId: string;
}
