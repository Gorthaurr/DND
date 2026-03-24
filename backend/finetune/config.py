"""Fine-tuning pipeline configuration."""

from __future__ import annotations

import os
from pathlib import Path

# ── Paths ──
FINETUNE_DIR = Path(__file__).parent
DATA_DIR = FINETUNE_DIR / "data"
SCENARIOS_DIR = DATA_DIR / "scenarios"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
CACHE_DIR = DATA_DIR / "cache"

# Project paths
PROJECT_ROOT = FINETUNE_DIR.parent
PROMPTS_DIR = PROJECT_ROOT / "app" / "agents" / "prompts"

# ── Claude API ──
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_HAIKU_MODEL = "claude-haiku-4-5-20251001"
CLAUDE_SONNET_MODEL = "claude-sonnet-4-5-20241022"
CLAUDE_MAX_CONCURRENT = 10
CLAUDE_MAX_RETRIES = 3
CLAUDE_BUDGET_USD = 50.0

# Agent types that use Sonnet (creative output)
SONNET_AGENT_TYPES = {"npc_dialogue", "dm_narrate", "combat_narrate"}
# All others use Haiku

# ── Target dataset sizes ──
SCENARIO_COUNTS: dict[str, int] = {
    "npc_decision": 3000,
    "npc_dialogue": 4000,
    "npc_interact": 2000,
    "npc_interjection": 1500,
    "combat_intent": 1000,
    "combat_narrate": 800,
    "dm_narrate": 2000,
    "scenario_generate": 500,
    "scenario_advance": 500,
    "event_generate": 500,
    "quest_generate": 500,
}

ALL_AGENT_TYPES = list(SCENARIO_COUNTS.keys())

# ── Training hyperparameters ──
BASE_MODEL = "unsloth/Qwen2.5-14B-bnb-4bit"
LORA_RANK = 32
LORA_ALPHA = 64
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
EPOCHS = 3
BATCH_SIZE = 2
GRAD_ACCUM = 8
LEARNING_RATE = 2e-4
MAX_SEQ_LENGTH = 4096
WARMUP_RATIO = 0.05

# ── Data split ──
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1

# ── Ollama deployment ──
OLLAMA_MODEL_NAME = "qwen2.5:14b-dnd"
GGUF_QUANTIZATION = "q4_k_m"
