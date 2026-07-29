import type { 
  StructuredDirection, 
  PromptAnalysis, 
  StylePreset, 
  AspectRatio, 
  Duration, 
  UIState, 
  VideoItem, 
  ModelCapability, 
  GenerationProgressInfo 
} from './video';

// POST /api/v1/director/enhance
export interface EnhancePromptRequest {
  prompt: string;
}

export interface EnhancePromptResponse {
  originalPrompt: string;
  enhancedPrompt: string;
  structuredDirection: StructuredDirection;
  analysis: PromptAnalysis;
}

// POST /api/v1/generations
export interface CreateGenerationRequest {
  prompt: string;
  enhancedPrompt?: string;
  structuredDirection?: StructuredDirection;
  style: StylePreset;
  aspectRatio: AspectRatio;
  duration: Duration;
  negativePrompt?: string;
  modelId: string;
}

// GET /api/v1/generations/{id}, POST /retry, POST /variations
export interface GenerationStatusResponse {
  id: string;
  state: UIState;
  video?: VideoItem;
  progress?: GenerationProgressInfo;
  errorMessage?: string;
}

// GET /api/v1/generations?limit=5
export interface PaginatedGenerationsResponse {
  generations: VideoItem[];
  totalCount: number;
  limit: number;
  offset: number;
}

// GET /api/v1/models
export interface ModelsResponse {
  models: ModelCapability[];
}
