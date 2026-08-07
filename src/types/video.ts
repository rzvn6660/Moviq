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
export type ExecutionMode = 'Hosted Inference' | 'Hosted API' | 'Self-Hosted GPU' | 'External Web' | 'Simulation / Demo';

export interface HistoryFilterOptions {
  limit?: number;
  offset?: number;
  search?: string;
  filter?: 'all' | 'favorites' | 'completed' | 'failed' | 'queued';
  provider?: string;
  modelId?: string;
  sortBy?: 'newest' | 'oldest' | 'alphabetical' | 'generation_date' | 'favorite_date';
}

export interface ModelCapability {
  id: string;
  name: string;
  provider: string;
  executionMode?: ExecutionMode;
  tag: string;
  description: string;
  supportedAspectRatios: AspectRatio[];
  supportedDurations: Duration[];
  supportsNegativePrompt: boolean;
  maxDurationSeconds?: number;
  renderProfileDescription?: string;
  isAvailable: boolean;
  configured?: boolean;
  statusLabel?: string;
  externalUrl?: string;
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
  executionMode?: string;
  style: StylePreset;
  aspectRatio: AspectRatio;
  duration: Duration;
  generationTimeSeconds: number;
  createdAt: string;
  resolution: string;
  fps: number;
  isSynthetic?: boolean;
  fidelityScore?: number;
  fidelityLabel?: string;
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
  status: 'completed' | 'generating' | 'queued' | 'failed' | 'cancelled' | 'timed_out';
  timestamp: string;
  metadata: GenerationMetadata;
  smartFailover?: boolean;
  isFavorite?: boolean;
  favoriteAt?: string;
  isSynthetic?: boolean;
  fidelityScore?: number;
  fidelityLabel?: string;
  errorMessage?: string;
}

export interface PaginatedGenerationsResponse {
  generations: VideoItem[];
  totalCount: number;
  limit: number;
  offset: number;
}

export interface EnhancePromptRequest {
  prompt: string;
}

export interface EnhancePromptResponse {
  original_prompt: string;
  enhanced_prompt: string;
  structured_direction: StructuredDirection;
  analysis: PromptAnalysis;
}

export interface CreateGenerationRequest {
  prompt: string;
  enhancedPrompt?: string;
  structuredDirection?: StructuredDirection;
  style: StylePreset;
  aspectRatio: AspectRatio;
  duration: Duration;
  negativePrompt?: string;
  modelId: string;
  smartFailover?: boolean;
}

export type GenerationRequest = CreateGenerationRequest;

export interface GenerationEventResponse {
  id: string;
  generationId: string;
  step: string;
  status: string;
  startedAt: string;
  completedAt?: string;
  durationMs: number;
  details?: Record<string, any>;
}

// Moviq v2.1 Intelligence & Orchestration Types
export interface ProviderCreditsInfo {
  known: boolean;
  remaining?: number | null;
}

export interface ProviderHealthInfo {
  provider: string;
  status: 'ONLINE' | 'DEGRADED' | 'OFFLINE' | 'AUTH_FAILED' | 'QUOTA_EXHAUSTED' | 'GPU_BUSY' | 'CONFIG_MISSING';
  latency_ms: number;
  queue_status: 'LOW' | 'MEDIUM' | 'HIGH' | 'FULL' | 'UNKNOWN';
  configured: boolean;
  authenticated: boolean;
  available_models: number;
  estimated_wait: number;
  credits: ProviderCreditsInfo;
  message?: string;
}

export interface ProviderHealthListResponse {
  providers: ProviderHealthInfo[];
  cached_at: string;
}

export interface RecommendProviderRequest {
  prompt: string;
  aspectRatio?: AspectRatio;
  duration?: Duration;
  priority?: 'quality' | 'speed' | 'cost' | 'local';
}

export interface RecommendProviderResponse {
  recommended_provider: string;
  recommended_model_id: string;
  confidence: number;
  reason: string;
  fallback_providers: string[];
}

export interface CostEstimateRequest {
  modelId: string;
  duration?: Duration;
  aspectRatio?: AspectRatio;
}

export interface CostEstimateResponse {
  model_id: string;
  provider: string;
  estimated_cost_usd?: number | null;
  estimated_credits?: number | null;
  estimated_queue_seconds: number;
  estimated_runtime_seconds: number;
  resolution: string;
  pricing_known: boolean;
  notes: string;
}

export interface ProviderBenchmarkMetric {
  provider: string;
  name: string;
  avg_generation_time_seconds: number;
  avg_queue_time_seconds: number;
  success_rate_percentage: number;
  total_generations: number;
  supported_resolutions: string[];
  typical_duration: string;
  estimated_cost_per_sec?: number | null;
  motion_quality_score: number;
  realism_score: number;
  reliability_score: number;
  overall_rating: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR';
}

export interface ProviderBenchmarkListResponse {
  benchmarks: ProviderBenchmarkMetric[];
}
