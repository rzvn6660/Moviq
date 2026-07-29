import hashlib
from typing import Dict, Optional
from app.schemas.director import EnhancePromptResponse


class DirectorEnhancementCache:
    """In-memory cache for AI Director prompt enhancements to avoid redundant LLM calls."""

    def __init__(self, max_size: int = 100):
        self._cache: Dict[str, EnhancePromptResponse] = {}
        self.max_size = max_size

    def _make_key(self, prompt: str) -> str:
        normalized = prompt.strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get(self, prompt: str) -> Optional[EnhancePromptResponse]:
        key = self._make_key(prompt)
        return self._cache.get(key)

    def set(self, prompt: str, response: EnhancePromptResponse):
        if len(self._cache) >= self.max_size:
            # Evict oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        key = self._make_key(prompt)
        self._cache[key] = response

    def clear(self):
        self._cache.clear()
