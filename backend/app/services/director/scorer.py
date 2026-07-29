from typing import List, Dict, Any, Tuple


class PromptScorer:
    """
    Deterministic Python Prompt Quality Scorer for AI Video Generation.
    Evaluates prompts across 6 core cinematic dimensions:
    - Length & Detail Specificity
    - Subject Clarity
    - Environment & Context
    - Action & Motion Dynamics
    - Camera Angle & Optics
    - Lighting & Volumetrics
    """

    SUBJECT_KEYWORDS = [
        "bottle", "car", "person", "astronaut", "warrior", "cat", "dog", "robot",
        "building", "eye", "flower", "ship", "hand", "face", "statue", "dragon",
        "phone", "watch", "vehicle", "creature", "character", "model", "shoe"
    ]

    ENVIRONMENT_KEYWORDS = [
        "marble", "tokyo", "street", "forest", "dunes", "mars", "room", "ocean",
        "studio", "desert", "space", "city", "rain", "cyberpunk", "temple",
        "ruins", "landscape", "interior", "background", "backdrop", "mountain"
    ]

    MOTION_KEYWORDS = [
        "rotating", "spinning", "drifting", "running", "walking", "flying",
        "unsheathing", "speeding", "moving", "opening", "flowing", "swirling",
        "slow motion", "60fps", "fast", "floating", "falling", "turning"
    ]

    CAMERA_KEYWORDS = [
        "shot", "macro", "angle", "tracking", "anamorphic", "lens", "pan",
        "zoom", "tilt", "close-up", "wide shot", "drone", "orbit", "push-in",
        "depth of field", "bokeh", "35mm"
    ]

    LIGHTING_KEYWORDS = [
        "lighting", "spotlight", "sunlight", "golden", "neon", "shadows",
        "raytracing", "volumetric", "tungsten", "caustics", "backlight",
        "reflections", "twilight", "glow", "cinematic lighting"
    ]

    @classmethod
    def evaluate(cls, prompt: str) -> Tuple[int, str, List[str]]:
        trimmed = prompt.strip()
        if not trimmed:
            return 0, "Basic", ["Prompt is empty. Please enter a description."]

        score = 15  # Base score for valid input
        feedback: List[str] = []
        lower = trimmed.lower()

        # 1. Length & Specificity (max 25 pts)
        char_len = len(trimmed)
        if char_len >= 120:
            score += 25
        elif char_len >= 70:
            score += 18
        elif char_len >= 30:
            score += 10
        else:
            feedback.append("Add more descriptive detail (aim for 30+ characters)")

        # 2. Subject Clarity (max 15 pts)
        has_subject = any(k in lower for k in cls.SUBJECT_KEYWORDS)
        if has_subject:
            score += 15
        else:
            feedback.append("Specify a clearer main subject or key object")

        # 3. Environment & Context (max 15 pts)
        has_env = any(k in lower for k in cls.ENVIRONMENT_KEYWORDS)
        if has_env:
            score += 15
        else:
            feedback.append("Describe the environment or backdrop setting")

        # 4. Motion Dynamics (max 15 pts)
        has_motion = any(k in lower for k in cls.MOTION_KEYWORDS)
        if has_motion:
            score += 15
        else:
            feedback.append("Specify subject movement or motion dynamics (e.g. slow motion, spinning)")

        # 5. Camera Optics (max 15 pts)
        has_camera = any(k in lower for k in cls.CAMERA_KEYWORDS)
        if has_camera:
            score += 15
        else:
            feedback.append("Add camera direction or lens specs (e.g. macro tracking, anamorphic 35mm)")

        # 6. Lighting (max 15 pts)
        has_lighting = any(k in lower for k in cls.LIGHTING_KEYWORDS)
        if has_lighting:
            score += 15
        else:
            feedback.append("Include lighting cues (e.g. warm golden volumetric rays, neon backlight)")

        # Bound score to [0, 100]
        final_score = min(100, max(0, score))

        # Assign rating label
        if final_score >= 85:
            label = "Director Level"
        elif final_score >= 60:
            label = "Detailed"
        elif final_score >= 35:
            label = "Moderate"
        else:
            label = "Basic"

        return final_score, label, feedback
