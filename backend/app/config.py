from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:14b"
    ollama_temperature: float = 0.7

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "livingworld"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # World Simulation
    tick_interval_seconds: int = 300
    max_active_npcs_per_tick: int = 28
    memory_summarize_threshold: int = 50

    # Paths
    worlds_dir: Path = Path("worlds")
    data_dir: Path = Path("data")

    # Frontend
    next_public_api_url: str = "http://localhost:8000"
    next_public_ws_url: str = "ws://localhost:8000/ws/game"


settings = Settings()
