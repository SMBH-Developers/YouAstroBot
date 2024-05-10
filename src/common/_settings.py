from pydantic_settings import BaseSettings, SettingsConfigDict
from ..constants import BASE_DIR


class _Settings(BaseSettings):
    tg_token: str
    sqlalchemy_url: str
    redis_db: int

    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env', env_file_encoding="utf-8", extra="ignore")


settings = _Settings()
