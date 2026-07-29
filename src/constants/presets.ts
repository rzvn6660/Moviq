import type { StylePreset, AspectRatio, Duration, ModelCapability } from '../types/video';

export interface StyleOption {
  id: StylePreset;
  name: string;
  description: string;
  badge: string;
  bgGradient: string;
}

export interface AspectRatioOption {
  id: AspectRatio;
  label: string;
  dimensions: string;
  iconAspect: string;
}

export const SAMPLE_PROMPTS = [
  "A luxury perfume bottle rotating on black marble with warm golden lighting.",
  "Cinematic macro shot of an iris opening in slow motion with iridescent blue reflections.",
  "A futuristic sports car drifting through neon-lit rainy Tokyo streets at midnight.",
  "An ancient mystical camera lens focusing in an overgrown mossy temple ruin.",
  "Dynamic tracking shot of an astronaut running across crimson sand dunes on Mars."
];

export const STYLE_PRESETS: StyleOption[] = [
  {
    id: 'Cinematic',
    name: 'Cinematic',
    description: '35mm film aesthetic, rich shadows & anamorphic lens flare',
    badge: '35mm Anamorphic',
    bgGradient: 'from-amber-900/40 via-amber-950/20 to-slate-900'
  },
  {
    id: 'Realistic',
    name: 'Realistic',
    description: 'Ultra-photorealistic 8K optics & true-to-life lighting',
    badge: 'Photoreal 8K',
    bgGradient: 'from-blue-900/40 via-slate-900 to-slate-900'
  },
  {
    id: 'Anime',
    name: 'Anime',
    description: 'Hand-drawn aesthetic with vibrant keyframe shading',
    badge: 'Studio Hand-Drawn',
    bgGradient: 'from-purple-900/40 via-purple-950/20 to-slate-900'
  },
  {
    id: '3D',
    name: '3D Render',
    description: 'Octane Render with subsurface raytracing',
    badge: 'Octane CGI',
    bgGradient: 'from-emerald-900/40 via-slate-900 to-slate-900'
  }
];

export const ASPECT_RATIOS: AspectRatioOption[] = [
  { id: '16:9', label: '16:9 Landscape', dimensions: '1920 × 1080', iconAspect: 'w-8 h-4.5' },
  { id: '9:16', label: '9:16 Vertical', dimensions: '1080 × 1920', iconAspect: 'w-4.5 h-8' },
  { id: '1:1', label: '1:1 Square', dimensions: '1080 × 1080', iconAspect: 'w-6 h-6' }
];

export const DURATIONS: Duration[] = ['5s', '10s', '15s'];

export const MOCK_MODEL_CAPABILITIES: ModelCapability[] = [
  {
    id: 'hunyuan-video-v1',
    name: 'Moviq Core (Hunyuan-Video)',
    provider: 'fal-ai',
    tag: 'Fast & High Fidelity',
    description: 'High-speed open video model with anamorphic depth controls.',
    supportedAspectRatios: ['16:9', '9:16', '1:1'],
    supportedDurations: ['5s', '10s'],
    supportsNegativePrompt: true,
    maxDurationSeconds: 10,
    isAvailable: true
  },
  {
    id: 'luma-dream-machine',
    name: 'Dream Machine v2.5',
    provider: 'luma-ai',
    tag: 'Ultra Dynamic Motion',
    description: 'Physics-informed realistic motion engine with high coherence.',
    supportedAspectRatios: ['16:9', '9:16'],
    supportedDurations: ['5s', '10s'],
    supportsNegativePrompt: false,
    maxDurationSeconds: 10,
    isAvailable: true
  },
  {
    id: 'runway-gen3-alpha',
    name: 'Gen-3 Alpha Turbo',
    provider: 'runway',
    tag: 'Cinematic Framing',
    description: 'Industry standard video generation with extended 15s clips.',
    supportedAspectRatios: ['16:9', '9:16', '1:1'],
    supportedDurations: ['5s', '10s', '15s'],
    supportsNegativePrompt: true,
    maxDurationSeconds: 15,
    isAvailable: true
  },
  {
    id: 'pika-v2.0',
    name: 'Pika 2.0 Motion',
    provider: 'pika-labs',
    tag: 'Stylized Realism',
    description: 'Specialized stylized rendering for anime and artistic video.',
    supportedAspectRatios: ['16:9', '1:1'],
    supportedDurations: ['5s'],
    supportsNegativePrompt: true,
    maxDurationSeconds: 5,
    isAvailable: true
  }
];
