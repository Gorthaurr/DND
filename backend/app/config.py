from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM Provider (ollama | openai | anthropic)
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:14b"
    ollama_temperature: float = 0.7
    # OpenAI-compatible (also works with OpenRouter, Together, vLLM)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # PostgreSQL (users, rooms, sessions)
    postgres_url: str = "postgresql+asyncpg://livingworld:livingworld@localhost:5432/livingworld"

    # JWT Auth
    jwt_secret: str = "change-me-in-production-please"
    jwt_expire_hours: int = 72

    # Neo4j (world graph)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "livingworld"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # World Simulation
    tick_interval_seconds: int = 300
    max_active_npcs_per_tick: int = 25
    memory_summarize_threshold: int = 50

    # LLM Rate Limiting & Scaling
    llm_max_concurrent: int = 5
    llm_retry_base_delay: float = 1.0
    llm_batch_size: int = 10
    priority_llm_ratio: float = 0.5  # fraction of NPC that get full LLM decisions

    # Paths
    worlds_dir: Path = Path("worlds")
    data_dir: Path = Path("data")

    # Frontend
    next_public_api_url: str = "http://localhost:8000"
    next_public_ws_url: str = "ws://localhost:8000/ws/game"


settings = Settings()
