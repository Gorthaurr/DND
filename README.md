# Living World Engine

AI Dungeon Master with a living, breathing world. NPCs are AI agents with unique personalities, long-term memory, and evolving relationships. The world simulates autonomously between player sessions.

## Features

- **AI-Powered NPCs** — Each NPC has Big Five personality traits, goals, backstory, and memory
- **Living World Simulation** — NPCs make autonomous decisions, interact with each other, spread rumors
- **Graph-Based World** — Neo4j stores all entities, relationships, and world state
- **Semantic Memory** — NPCs remember interactions using embedding-based search
- **Dynamic Events** — World generates organic events that affect NPC behavior
- **Quest Generation** — Quests emerge naturally from NPC conflicts and world tensions
- **Observer Mode** — Watch NPCs interact with each other in real-time

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Celery
- **Frontend:** Next.js 14, React, TailwindCSS
- **Graph DB:** Neo4j 5.x
- **LLM:** Ollama (qwen2.5:14b locally)
- **Memory:** SQLite + sentence-transformers
- **Queue:** Celery + Redis

## Quick Start

### Prerequisites

- Docker Desktop
- Ollama with `qwen2.5:14b` model
- NVIDIA GPU (recommended: RTX 3080+)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/living-world-engine.git
cd living-world-engine

# 2. Make sure Ollama is running with the model
ollama pull qwen2.5:14b

# 3. Copy environment file
cp .env.example .env

# 4. Start all services
docker compose up -d

# 5. Seed the world
docker compose exec backend python -m scripts.seed_world

# 6. Play!
# Terminal client:
python scripts/play_cli.py

# Or open http://localhost:3000 for the web interface
```

## Architecture

```
Player Action → DM Agent (narrates) → World Graph (updates)
                                          ↓
World Tick → NPC Agents (decide) → Apply to Graph → Rumor Propagation
                ↓
          Event Agent (generates events) → Affect NPCs
```

## World Preset: Oakhollow Village

A medieval village with 7 locations, 10 NPCs, 3 factions, and 22 event templates.

**NPCs include:** Elder Marta (village leader), Torvin the Smith, Lira the Merchant, Goran the Hunter, Sister Elara (healer), Finn the Troublemaker, and more.

## CLI Commands

| Command | Description |
|---------|-------------|
| `look` | Describe current location |
| `go <place>` | Move to a location |
| `talk <npc_id>` | Start dialogue with NPC |
| `say <message>` | Talk to current NPC |
| `tick` | Advance world by one day |
| `map` | Show world map |
| `observe <id>` | Observer mode (debug) |
| `reset` | Reset world to initial state |

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/action` | POST | Player action |
| `/api/dialogue` | POST | Talk to NPC |
| `/api/look` | GET | Current location |
| `/api/world/state` | GET | World state |
| `/api/world/map` | GET | Map data |
| `/api/world/tick` | POST | Manual tick |
| `/api/world/reset` | POST | Reset world |
| `/api/npc/:id` | GET | NPC info |
| `/api/npc/:id/observe` | GET | Full NPC state |
| `/ws/game` | WS | Real-time updates |

## License

MIT
