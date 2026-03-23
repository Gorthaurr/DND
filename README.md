# Living World Engine

AI Dungeon Master with a living, breathing world. NPCs are AI agents with unique personalities, long-term memory, and evolving relationships. The world simulates autonomously between player sessions.

## Features

- **AI-Powered NPCs** — Each NPC has Big Five personality traits, goals, backstory, archetypes, and semantic memory
- **Living World Simulation** — NPCs make autonomous decisions, interact with each other, spread rumors, form alliances and rivalries
- **D&D 5e Combat** — d20 attack rolls, armor class, damage dice, NPC death with witness notifications
- **Graph-Based World** — Neo4j stores all entities, relationships, and world state
- **Semantic Memory** — NPCs remember interactions using embedding-based similarity search (offline, no SaaS dependency)
- **Dynamic Scenarios** — Multi-phase story arcs with tension escalation, NPC directives, and twist injection
- **Quest Generation** — Quests emerge naturally from NPC conflicts and world tensions
- **World Generation from Text** — Pipeline to create full worlds from text descriptions (text -> entities -> world JSON)
- **World Analytics & Reports** — LLM-generated narrative summaries of what happened over N ticks
- **Priority-Based Scaling** — Batch LLM processing with NPC prioritization for 100+ agent simulations
- **Observer Mode** — Watch NPCs interact with each other in real-time

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Celery
- **Frontend:** Next.js 14, React, TailwindCSS
- **Graph DB:** Neo4j 5.x
- **LLM:** Ollama (qwen2.5:14b locally) with rate limiting, exponential backoff, and fallback
- **Memory:** SQLite + sentence-transformers (fully offline)
- **Queue:** Celery + Redis

## Quick Start

### Prerequisites

- Docker Desktop
- Ollama with `qwen2.5:14b` model
- NVIDIA GPU (recommended: RTX 3080+)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/living-world-engine.git
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
World Tick (Celery Beat, every 5 min) →
    1. Scenario Lifecycle (advance/generate story arcs)
    2. World Events (LLM + predefined pool)
    3. NPC Decisions (priority-based: LLM for key NPCs, deterministic for background)
    4. NPC Interactions (pair resolution with relationship/mood changes)
    5. Rumor Propagation (NPCs share memories across locations)
    6. Memory Consolidation (summarize old memories, purge excess)
                ↓
         WebSocket Push → Frontend
```

## World Preset: Oakhollow Village

A medieval village with 9 locations, 10+ NPCs, 3 factions, 8 scenario templates, and 10+ event types.

**NPCs include:** Elder Marta (village leader & secret archmage), Torvin the Smith, Lira the Merchant, Goran the Hunter, Sister Elara (healer), Finn the Troublemaker, and more.

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/action` | POST | Player action |
| `/api/dialogue` | POST | Talk to NPC |
| `/api/look` | GET | Current location |
| `/api/world/state` | GET | World state |
| `/api/world/map` | GET | Map data |
| `/api/world/tick` | POST | Manual tick |
| `/api/world/tick/stream` | POST | Stream tick progress (SSE) |
| `/api/world/report` | GET | World analytics report with narrative |
| `/api/world/timeline` | GET | Chronological event timeline |
| `/api/world/generate` | POST | Generate world from text description |
| `/api/world/save` | POST | Save game state |
| `/api/world/load/{file}` | POST | Load saved game |
| `/api/world/reset` | POST | Reset world |
| `/api/npc/:id` | GET | NPC info |
| `/api/npc/:id/observe` | GET | Full NPC state (debug) |
| `/api/npcs` | GET | List all NPCs |
| `/api/npcs/graph` | GET | Relationship graph |
| `/api/quests` | GET | List quests |
| `/ws/game` | WS | Real-time updates |

## Development

### Running Tests

```bash
cd backend
pip install -e ".[dev]"
pytest tests/ -v
```

### Linting

```bash
ruff check backend/
mypy backend/app/
```

### Project Structure

```
backend/
  app/
    agents/         # AI agents (DM, NPC, Event, Scenario, Report)
    api/            # REST API + WebSocket
    dnd/            # D&D 5e rules engine
    graph/          # Neo4j database layer
    models/         # Data models + NPC memory
    simulation/     # World tick, interactions, rumors, analytics
    utils/          # LLM client, embeddings, logger
    worldgen/       # Text → World generation pipeline
  tests/            # pytest test suite
frontend/           # Next.js React frontend
worlds/             # World presets and saves
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Run tests: `cd backend && pytest tests/ -v`
4. Run linter: `ruff check backend/`
5. Submit a pull request

## License

[MIT](LICENSE)
