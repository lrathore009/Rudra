"""Rudra configuration — environment-driven, privacy-first."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root is three levels up from this file: backend/rudra/core/config.py
_REPO_ROOT = Path(__file__).resolve().parents[3]
# Load the repo-root .env first, then an optional backend-local .env (which wins).
_ENV_FILES = (str(_REPO_ROOT / ".env"), str(_REPO_ROOT / "backend" / ".env"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    rudra_env: Literal["development", "staging", "production"] = "development"
    rudra_secret_key: SecretStr = Field(default=SecretStr("dev-secret-change-me"))
    rudra_encryption_key: SecretStr = Field(default=SecretStr("dev-encryption-key-32bytes!!"))

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "rudra"
    postgres_password: SecretStr = Field(default=SecretStr("rudra_dev_password"))
    postgres_db: str = "rudra"

    # Full DATABASE_URL override (e.g. Supabase). Takes precedence over postgres_* parts.
    database_url_override: str | None = None

    # Supabase (hosted Postgres + pgvector)
    supabase_url: str | None = None
    supabase_anon_key: SecretStr | None = None
    supabase_publishable_key: SecretStr | None = None
    supabase_service_role_key: SecretStr | None = None

    # Vector DB
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: SecretStr | None = None

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AI Providers
    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    google_ai_api_key: SecretStr | None = None
    ollama_base_url: str = "http://localhost:11434"
    # Local chat model used by Ollama. Upgrade to e.g. "qwen2.5:7b" or "llama3.1:8b"
    # for noticeably better reasoning (still free) — just pull it and set this.
    ollama_chat_model: str = "llama3.2"

    # Embeddings (free, local-first)
    embedding_provider: Literal["auto", "ollama", "gemini", "openai"] = "auto"
    embedding_dim: int = 768
    embedding_model_ollama: str = "nomic-embed-text"
    embedding_model_gemini: str = "models/text-embedding-004"

    # Research
    tavily_api_key: SecretStr | None = None
    serpapi_key: SecretStr | None = None

    # Security
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    audit_log_retention_days: int = 365

    # CORS — browsers calling the API from the frontend.
    # Comma-separated exact origins, plus a regex for dynamic Vercel domains.
    cors_allow_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    cors_allow_origin_regex: str = r"https://.*\.vercel\.app"

    # Auth — real JWT login (local-first single owner).
    auth_required: bool = True
    owner_username: str = "owner"
    owner_password: SecretStr = Field(default=SecretStr("rudra_dev_password"))
    rate_limit_per_minute: int = 120

    # Feature flags
    enable_voice: bool = False
    enable_autonomous_research: bool = False
    enable_luxury_module: bool = True
    # light = memories + skills only (fast, fits Vercel 60s proxy). full = web + luxury research.
    command_enrichment: Literal["light", "full"] = "light"

    # Autonomy layer (P1–P5) — env-driven, safe defaults.
    agent_max_steps: int = 6  # P1: ReAct loop step cap
    enable_code_execution: bool = False  # P4: CodeAct off by default (needs real sandbox)
    code_exec_timeout_seconds: int = 10
    enable_scheduler: bool = True  # P3: in-process scheduler
    morning_digest_time: str = "07:30"  # local HH:MM for the daily digest
    skills_dir: str = str(_REPO_ROOT / "skills")  # P2: SKILL.md folder
    data_dir: str = str(_REPO_ROOT / ".data")  # P5: trace store
    uploads_dir: str = str(_REPO_ROOT / "data" / "uploads")
    processed_dir: str = str(_REPO_ROOT / "data" / "processed")
    document_chunks_dir: str = str(_REPO_ROOT / "data" / "document_chunks")
    stream_enrich_budget_seconds: float = 3.0  # Phase 4: cap enrichment wall-time before streaming
    free_sources_budget_seconds: float = 3.0  # Phase 3: cap live free-source HTTP per request
    document_chunk_size: int = 900
    document_chunk_overlap: int = 120

    # Jarvis supreme-assistant layer (OpenJarvis-inspired)
    jarvis_persona: str = "jarvis"
    jarvis_honorific: str = "sir"
    enable_jarvis_tts: bool = True
    tts_backend: Literal["openai", "browser"] = "openai"
    tts_openai_model: str = "tts-1"
    tts_openai_voice: str = "onyx"
    enable_operators: bool = True
    enable_minions_routing: bool = True
    enable_guardrails: bool = True
    rudra_spec_path: str | None = None
    google_client_id: str | None = None
    google_client_secret: SecretStr | None = None
    slack_signing_secret: SecretStr | None = None
    slack_bot_token: SecretStr | None = None
    slack_default_channel: str = "general"
    notion_api_token: str | None = None
    linear_api_key: str | None = None
    ea_weather_city: str = "Dubai"
    ea_weather_lat: float = 25.2048
    ea_weather_lon: float = 55.2708
    ea_news_feeds: str = (
        "https://feeds.bbci.co.uk/news/world/rss.xml,"
        "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml,"
        "https://feeds.arstechnica.com/arstechnica/index,"
        "https://www.technologyreview.com/feed/,"
        "https://feeds.reuters.com/reuters/businessNews,"
        "https://www.ft.com/?format=rss,"
        "https://hnrss.org/frontpage,"
        "https://www.producthunt.com/feed,"
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
    )
    enable_ea_auto_sync: bool = True
    enable_ea_free_sources: bool = True
    enable_agent_free_sources: bool = True
    # Calendar / tasks (free tier)
    ea_caldav_urls: str = ""
    ea_todoist_token: SecretStr | None = None
    ea_github_token: SecretStr | None = None
    ea_github_repos: str = ""
    ea_trello_key: str | None = None
    ea_trello_token: SecretStr | None = None
    ea_trello_board_id: str | None = None
    # Email / documents
    ea_imap_host: str | None = None
    ea_imap_port: int = 993
    ea_imap_user: str | None = None
    ea_imap_password: SecretStr | None = None
    ea_obsidian_vault_path: str | None = None
    # News APIs (optional keys)
    guardian_api_key: SecretStr | None = None
    newsapi_key: SecretStr | None = None
    mediastack_api_key: SecretStr | None = None
    ea_reddit_subreddits: str = "technology,worldnews,business"
    # Finance (optional keys)
    fred_api_key: SecretStr | None = None
    alpha_vantage_api_key: SecretStr | None = None
    companies_house_api_key: str | None = None
    ea_finance_watchlist: str = "SPY,AAPL,MSFT"
    ea_edgar_watch_query: str = "artificial intelligence"
    # Travel
    amadeus_api_secret: SecretStr | None = None
    ea_travel_home_country: str = "AE"
    # Health export path (Apple Health / Google Fit CSV)
    ea_health_export_path: str | None = None
    # Knowledge / intel
    nasa_api_key: str = "DEMO_KEY"
    ea_knowledge_topics: str = "artificial intelligence,macroeconomics"
    ea_wikidata_entities: str = ""
    yelp_api_key: SecretStr | None = None
    europeana_api_key: str | None = None
    unsplash_access_key: SecretStr | None = None
    mcp_servers_json: str | None = None
    research_min_confidence_cache: float = 0.75
    research_auto_save: bool = True
    bloomberg_api_key: str | None = None
    factset_api_key: str | None = None
    chrono24_api_key: str | None = None
    artsy_api_key: str | None = None
    virtuoso_api_key: str | None = None
    amex_fhr_enabled: bool = False
    tripit_api_token: str | None = None
    amadeus_api_key: str | None = None
    wake_word: str = "rudra"
    stt_backend: Literal["openai", "browser"] = "openai"
    use_sandbox_code_exec: bool = True
    command_use_react_for_ea: bool = True

    @field_validator(
        "openai_api_key",
        "anthropic_api_key",
        "google_ai_api_key",
        "google_client_secret",
        "slack_signing_secret",
        "slack_bot_token",
        "notion_api_token",
        "linear_api_key",
        "bloomberg_api_key",
        "factset_api_key",
        "chrono24_api_key",
        "artsy_api_key",
        "virtuoso_api_key",
        "tripit_api_token",
        "amadeus_api_key",
        "amadeus_api_secret",
        "tavily_api_key",
        "serpapi_key",
        "ea_todoist_token",
        "ea_github_token",
        "ea_trello_token",
        "ea_imap_password",
        "guardian_api_key",
        "newsapi_key",
        "mediastack_api_key",
        "fred_api_key",
        "alpha_vantage_api_key",
        "yelp_api_key",
        "unsplash_access_key",
        "qdrant_api_key",
        "supabase_anon_key",
        "supabase_publishable_key",
        "supabase_service_role_key",
        mode="before",
    )
    @classmethod
    def _empty_secret_is_none(cls, v: object) -> object:
        """Treat blank env values (e.g. OPENAI_API_KEY=) as 'not configured'."""
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("database_url_override", "supabase_url", mode="before")
    @classmethod
    def _empty_str_is_none(cls, v: object) -> object:
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self._normalize_async_url(self.database_url_override)
        pwd = self.postgres_password.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{pwd}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @staticmethod
    def _normalize_async_url(url: str) -> str:
        """Ensure the URL uses the asyncpg driver for SQLAlchemy."""
        if url.startswith("postgresql+asyncpg://"):
            return url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.rudra_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
