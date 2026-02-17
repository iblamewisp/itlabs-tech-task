from .base import IBackendAPI
from .django_backend import DjangoBackend
from bot.config import load_config


def create_backend() -> IBackendAPI:
    """Create backend instance based on config"""
    config = load_config()
    
    # Switch via .env
    backend_type = config.backend_type  # 'django' | 'mock' | 'fastapi'
    
    if backend_type == 'django':
        return DjangoBackend(base_url=config.django_api_url)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")