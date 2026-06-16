from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MTOS API"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]
    repository_mode: str = "in_memory"
    trust_demo_headers: bool = True
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="MTOS_",
        env_file=(".env", ".env.local", "../.env", "../.env.local"),
        env_file_encoding="utf-8",
    )


settings = Settings()
