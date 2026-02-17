from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class BotConfig(BaseSettings):
    """Bot configuration with Pydantic validation"""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    # Bot settings
    bot_token: str = Field(
        ...,
        description="Telegram bot token from BotFather"
    )
    
    use_webhook: bool = Field(
        default=False,
        description="Use webhook mode instead of polling"
    )
    
    webhook_url: str = Field(
        default="https://yourdomain.com",
        description="Public URL for webhook (required if use_webhook=true)"
    )
    
    # Backend settings
    backend_type: str = Field(
        default="django",
        description="Backend type: django | mock | fastapi"
    )
    
    django_api_url: str = Field(
        default="http://web:8000/api",
        description="Django REST API base URL"
    )

    internal_api_key: str = Field(
        default="",
        description="Shared secret for bot ↔ Django API auth (X-Internal-Key header)"
    )
    
    # Redis settings
    redis_fsm_url: str = Field(
        default="redis://redis:6379/1",
        description="Redis URL for FSM storage (database 1)"
    )
    
    redis_rate_limit_url: str = Field(
        default="redis://redis:6379/2",
        description="Redis URL for rate limiting (database 2)"
    )
    
    # Optional: Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG | INFO | WARNING | ERROR"
    )


# Singleton instance
_config: BotConfig | None = None


def get_config() -> BotConfig:
    """Get or create config singleton"""
    global _config
    if _config is None:
        _config = BotConfig()
    return _config


# Backward compatibility
def load_config() -> BotConfig:
    """Load configuration (alias for get_config)"""
    return get_config()