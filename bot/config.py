from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    TELEGRAM_BOT_TOKEN: str = ""
    MINI_APP_URL: str = "https://shopwriter.botapps.pro"
    BACKEND_URL: str = "http://localhost:8008"
    SUPPORT_USERNAME: str = "@your_support"
    ADMIN_TELEGRAM_ID: int = 0
    ADMIN_TOKEN: str = "change-me-secret"


settings = BotSettings()
