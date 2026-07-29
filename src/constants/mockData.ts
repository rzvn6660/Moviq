import type { VideoItem } from '../types/video';

export const INITIAL_MOCK_VIDEOS: VideoItem[] = [
  {
    id: 'moviq-gen-8812',
    originalPrompt: 'A luxury perfume bottle rotating on black marble with warm golden lighting.',
    enhancedPrompt: 'Cinematic commercial macro shot of a sleek obsidian perfume bottle with embossed gold typography, spinning smoothly on wet black marble. Volumetric warm tungsten spotlighting casts sharp golden caustics and subtle dust particles hovering in the atmosphere. 35mm film grain, anamorphic lens flare, 60fps slow motion.',
    structuredDirection: {
      subject: 'Obsidian perfume bottle with gold embossed branding',
      environment: 'Wet black polished marble reflecting warm light reflections',
      action: 'Smooth 360-degree rotation with subtle floating dust particles',
      camera: 'Low-angle macro 35mm anamorphic tracking camera',
      lighting: 'Warm 3200K volumetric spot with high caustics contrast',
      mood: 'Sophisticated, luxurious, high-fashion commercial'
    },
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
    thumbnailUrl: 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=1200&q=80',
    style: 'Cinematic',
    aspectRatio: '16:9',
    duration: '5s',
    negativePrompt: 'blurry, oversaturated, low quality, jittery motion, extra objects, harsh shadows',
    status: 'completed',
    timestamp: '2 mins ago',
    metadata: {
      id: 'meta-8812',
      model: 'Moviq Core (Hunyuan-Video)',
      provider: 'fal-ai',
      style: 'Cinematic',
      aspectRatio: '16:9',
      duration: '5s',
      generationTimeSeconds: 8.4,
      createdAt: '2026-07-28 22:30',
      resolution: '1920 × 1080',
      fps: 60
    }
  },
  {
    id: 'moviq-gen-8811',
    originalPrompt: 'Cyberpunk futuristic supercar speeding through Tokyo neon rain at night.',
    enhancedPrompt: 'High-speed tracking shot of a matte-black futuristic hypercar with glowing cyan neon underglow, drifting through wet Tokyo streets under towering holographic billboards. Dynamic rain droplets streaking across anamorphic camera lens, reflection on asphalt puddles, atmospheric fog.',
    structuredDirection: {
      subject: 'Matte-black aerodynamic hypercar with cyan LED accents',
      environment: 'Dystopian Tokyo alleyways wet with rain and vibrant neon reflections',
      action: 'High-speed drift carving around a corner at high velocity',
      camera: 'Pursuit drone tracking camera with dynamic tilt and motion blur',
      lighting: 'High contrast cyan and magenta neon signage backlight',
      mood: 'Exhilarating, dark cyberpunk, cinematic adrenaline'
    },
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
    thumbnailUrl: 'https://images.unsplash.com/photo-1508974239320-0a029497e820?auto=format&fit=crop&w=1200&q=80',
    style: 'Realistic',
    aspectRatio: '16:9',
    duration: '10s',
    status: 'completed',
    timestamp: '15 mins ago',
    metadata: {
      id: 'meta-8811',
      model: 'Dream Machine v2.5',
      provider: 'luma-ai',
      style: 'Realistic',
      aspectRatio: '16:9',
      duration: '10s',
      generationTimeSeconds: 14.2,
      createdAt: '2026-07-28 22:15',
      resolution: '1920 × 1080',
      fps: 60
    }
  },
  {
    id: 'moviq-gen-8810',
    originalPrompt: 'An astronaut standing on crimson dunes looking at a dual moon sky.',
    enhancedPrompt: 'Ethereal wide shot of an astronaut in a worn white space suit standing on towering crimson sand dunes on a distant exoplanet. In the twilight sky, two massive ringed celestial moons glow softly. Wind swirling fine red sand across the boots in 4K resolution.',
    structuredDirection: {
      subject: 'Solo astronaut wearing detailed tactical EVA suit',
      environment: 'Alien desert dune landscape under dual celestial ringed moons',
      action: 'Slow walk toward horizon, turning head upwards toward sky',
      camera: 'Slow sweeping ultra-wide pan with shallow depth of field',
      lighting: 'Dim twilight ambient light with soft blue moonlight highlights',
      mood: 'Awe-inspiring, contemplative sci-fi mystery'
    },
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
    thumbnailUrl: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80',
    style: '3D',
    aspectRatio: '9:16',
    duration: '5s',
    status: 'completed',
    timestamp: '1 hour ago',
    metadata: {
      id: 'meta-8810',
      model: 'Gen-3 Alpha Turbo',
      provider: 'runway',
      style: '3D',
      aspectRatio: '9:16',
      duration: '5s',
      generationTimeSeconds: 6.8,
      createdAt: '2026-07-28 21:30',
      resolution: '1080 × 1920',
      fps: 30
    }
  },
  {
    id: 'moviq-gen-8809',
    originalPrompt: 'Anime warrior pulling a glowing thunder sword in an ancient bamboo forest.',
    enhancedPrompt: 'Studio Ghibli style dynamic animation. Anime warrior with flowing hair pulling a crackling lightning-infused katana from its sheath in a serene bamboo forest. Electric arcs illuminate emerald green bamboo leaves falling in slow motion.',
    structuredDirection: {
      subject: 'Anime warrior character with flowing dark hair and katana',
      environment: 'Dense bamboo forest at dusk with falling leaves',
      action: 'Sword unsheathing with violent electric aura energy',
      camera: 'Fast push-in zoom focusing on warrior eyes then sword hilt',
      lighting: 'Piercing electric blue lightning sparks against deep dark forest',
      mood: 'Epic anime climax, intense energy, graceful motion'
    },
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4',
    thumbnailUrl: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1200&q=80',
    style: 'Anime',
    aspectRatio: '1:1',
    duration: '5s',
    status: 'completed',
    timestamp: '3 hours ago',
    metadata: {
      id: 'meta-8809',
      model: 'Pika 2.0 Motion',
      provider: 'pika-labs',
      style: 'Anime',
      aspectRatio: '1:1',
      duration: '5s',
      generationTimeSeconds: 7.1,
      createdAt: '2026-07-28 19:30',
      resolution: '1080 × 1080',
      fps: 30
    }
  }
];
