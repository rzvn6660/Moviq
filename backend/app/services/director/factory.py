from app.services.director.base import DirectorProvider
from app.core.config import settings


def get_director_provider() -> DirectorProvider:
    provider_name = settings.DIRECTOR_PROVIDER.lower()
    if provider_name == "groq":
        from app.services.director.groq import GroqDirectorProvider
        return GroqDirectorProvider()
    else:
        from app.services.director.mock import MockDirectorProvider
        return MockDirectorProvider()
