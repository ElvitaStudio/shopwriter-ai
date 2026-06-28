from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    TELEGRAM_BOT_TOKEN: str = ""
    CLAUDE_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./shopwriter.db"
    MINI_APP_URL: str = "https://shopwriter.botapps.pro"
    SUPPORT_USERNAME: str = "@your_support"
    CHANNEL_USERNAME: str = "@shopwriter_hub"
    ADMIN_TELEGRAM_ID: int = 0
    ADMIN_TOKEN: str = "change-me-secret"


settings = Settings()
