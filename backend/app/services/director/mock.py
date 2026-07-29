from app.services.director.base import DirectorProvider
from app.schemas.director import EnhancePromptResponse, StructuredDirection, PromptAnalysis
from app.core.exceptions import EmptyPromptException


class MockDirectorProvider(DirectorProvider):
    async def enhance_prompt(self, prompt: str) -> EnhancePromptResponse:
        trimmed = prompt.strip()
        if not trimmed:
            raise EmptyPromptException()

        lower = trimmed.lower()
        score = 35
        feedback = []

        if len(trimmed) > 30:
            score += 25
        if len(trimmed) > 80:
            score += 20

        if any(k in lower for k in ["bottle", "car", "person", "astronaut", "warrior"]):
            score += 10
        else:
            feedback.append("Specify a clearer main subject or object")

        if any(k in lower for k in ["lighting", "golden", "neon", "volumetric", "spotlight"]):
            score += 10
        else:
            feedback.append("Add lighting notes (e.g. warm golden, volumetric)")

        score = min(100, max(15, score))
        label = "Director Level" if score > 85 else "Detailed" if score > 60 else "Moderate" if score > 35 else "Basic"

        # Structured direction breakdown
        subject = "Main subject focused in central frame"
        if "bottle" in lower:
            subject = "Sleek obsidian perfume bottle with embossed gold typography"
        elif "car" in lower:
            subject = "Matte-black aerodynamic hypercar with glowing cyan LED accents"
        elif "astronaut" in lower:
            subject = "Solo explorer wearing tactical deep-space EVA suit"
        elif "warrior" in lower:
            subject = "Heroic anime character with glowing energy katana"

        environment = "Atmospheric studio backdrop with soft volumetric fog"
        if "marble" in lower:
            environment = "Wet polished obsidian marble reflecting warm ambient highlights"
        elif "tokyo" in lower or "neon" in lower:
            environment = "Dystopian rainy metropolis streets bathed in glowing neon signs"
        elif "mars" in lower or "dunes" in lower:
            environment = "Swirling crimson sand dunes beneath dual celestial moons"

        camera = "35mm anamorphic prime lens with shallow depth of field"
        if "macro" in lower or "rotating" in lower:
            camera = "Low-angle 360-degree orbital macro tracking shot"

        lighting = "Warm 3200K cinematic spotlight with subtle dust motes"
        if "neon" in lower:
            lighting = "High-contrast cyan & magenta neon backlight"
        elif "golden" in lower:
            lighting = "Warm golden hour volumetric rays with specular caustics"

        structured = StructuredDirection(
            subject=subject,
            environment=environment,
            action="Smooth slow-motion progression at 60fps with fluid dynamics",
            camera=camera,
            lighting=lighting,
            mood="Sophisticated, cinematic, high-end commercial aesthetic"
        )

        enhanced_str = (
            f"{trimmed} Rendered in 35mm anamorphic film style with {lighting.lower()}. "
            f"{camera}. Subject: {subject}. Setting: {environment}. Highly detailed 8K resolution."
        )

        return EnhancePromptResponse(
            original_prompt=trimmed,
            enhanced_prompt=enhanced_str,
            structured_direction=structured,
            analysis=PromptAnalysis(score=score, label=label, feedback=feedback)
        )
