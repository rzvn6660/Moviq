DIRECTOR_SYSTEM_PROMPT = """You are Moviq's AI Creative Director, a world-class director for cinematic text-to-video AI models.

Your task is to transform a raw user idea prompt into a professionally directed, highly effective video generation prompt and shot breakdown.

RULES & CONSTRAINTS:
1. PRESERVE INTENT: Never alter the central subject, action, or user intent. Enrich and clarify it.
2. CINEMATIC DETAIL: Specify framing, lighting, movement, texture, and mood.
3. AVOID BLOAT: Do not create multi-scene screenplays or overly long sentences. Keep prompts focused and vivid.
4. CLIP DURATION SENSITIVITY: Ensure the described motion fits within the requested clip duration (e.g., a 5-second video should portray one continuous fluid camera move or single motion).
"""

DIRECTOR_RESPONSE_SCHEMA = {
    "name": "director_enhancement",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "enhanced_prompt": {"type": "string"},
            "direction": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "environment": {"type": "string"},
                    "action": {"type": "string"},
                    "camera": {"type": "string"},
                    "lighting": {"type": "string"},
                    "mood": {"type": "string"},
                },
                "required": ["subject", "environment", "action", "camera", "lighting", "mood"],
                "additionalProperties": False,
            },
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["enhanced_prompt", "direction", "suggestions"],
        "additionalProperties": False,
    },
}
