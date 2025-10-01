
from os.path import dirname, join
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = dirname(dirname(dirname(__file__)))


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./financas.db"
    ENV: str = "producao"

    model_config = SettingsConfigDict(
        env_file=join(BASE_DIR, f".env.{ENV}"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
