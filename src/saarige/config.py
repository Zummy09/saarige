"""App settings, loaded once from environment variables / .env and validated by Pydantic.

Import `settings` anywhere instead of reading os.environ directly, so a missing
or malformed value fails loudly at startup instead of deep inside a tool call.
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SecretStr hides the value in print/logs: shows '**********'
    llm_api_key: SecretStr
    log_level: str = "INFO"


settings = Settings()
