from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    test_database_url: str = ""
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:12b"
    secret_key: str
    access_token_expire_minutes: int = 10080

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
