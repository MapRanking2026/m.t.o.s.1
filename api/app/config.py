from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MTOS API"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]
    repository_mode: str = "in_memory"
    trust_demo_headers: bool = False
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    clickup_api_token: str | None = None
    clickup_team_id: str | None = None
    clickup_list_id: str | None = None
    clickup_am_custom_field_id: str | None = None
    clickup_base_url: str = "https://api.clickup.com/api/v2"
    clickup_include_closed: bool = False
    clickup_max_pages: int = 1
    clickup_max_tasks: int = 10

    model_config = SettingsConfigDict(
        env_prefix="MTOS_",
        env_file=(".env", ".env.local", "../.env", "../.env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
