# DND Living World Engine

## Структура проекта

```
DND/
├── backend/           # FastAPI + Python backend
│   ├── app/
│   │   ├── agents/    # LLM-агенты (DM, NPC, Event, Narrator, Faction, Report, Memory)
│   │   ├── api/       # REST routes + WebSocket + World Builder
│   │   ├── auth/      # JWT авторизация
│   │   ├── config.py  # Pydantic Settings (env-based)
│   │   ├── db/        # SQLAlchemy models
│   │   ├── dnd/       # D&D rules engine (dice, classes, races, equipment, combat)
│   │   ├── graph/     # Neo4j queries + connection
│   │   ├── models/    # Pydantic models + SQLite memory + WorldStore
│   │   ├── simulation/# Тикер, экономика, эволюция NPC, среда, расписание, репутация
│   │   ├── utils/     # LLM providers, embeddings, logger
│   │   └── worldgen/  # Генерация мира из текста
│   ├── tests/         # Тесты (pytest)
│   └── pyproject.toml
└── frontend/          # React + Vite frontend
    ├── src/
    └── e2e/           # Playwright E2E тесты
```

## Тестирование

### Backend (pytest)

**Единая точка входа:** `python tests/run_tests.py`

```bash
# Все тесты
cd backend && python tests/run_tests.py

# Конкретный модуль
python tests/run_tests.py --module dice
python tests/run_tests.py --module character

# Группа модулей
python tests/run_tests.py --module dnd        # все D&D правила
python tests/run_tests.py --module agents     # все агенты
python tests/run_tests.py --module simulation # вся симуляция
python tests/run_tests.py --module api        # все API routes
python tests/run_tests.py --module models     # все модели
python tests/run_tests.py --module llm        # LLM providers

# С покрытием
python tests/run_tests.py --cov
python tests/run_tests.py --module dnd --cov

# Показать все доступные модули
python tests/run_tests.py --list

# Напрямую через pytest
pytest tests/ -q                               # быстрый прогон
pytest tests/ --cov=app --cov-report=term      # с покрытием
pytest tests/test_dnd_dice.py -v               # конкретный файл
```

**Группы модулей:**
- `dnd` — dice, classes, races, equipment, rules, combat_narrator
- `models` — character, player, quest, scenario, world, schemas, npc_models, archetypes, memory, world_store
- `agents` — base, speech_patterns, dm, npc, event, report, narrator, faction, memory_architect
- `simulation` — economy, evolution, environment, schedule, reputation, quests, analytics, ticker, background, events, interaction, scheduler
- `graph` — queries, connection
- `api` — routes, world_builder, websocket
- `llm` — llm, providers
- `utils` — embeddings, config, auth
- `worldgen` — generator

**Стратегия моков:**
- `BaseAgent.generate_json()` / `generate_text()` — всегда мокаем LLM
- `GraphQueries` — мокаем все async методы (фикстура `mock_graph_queries` в conftest.py)
- `memory.py` — используем реальную tmp SQLite через фикстуру `memory_db`
- `httpx.AsyncClient` — мокаем для LLM providers
- `FastAPI TestClient` — для API route тестов

### Frontend (Playwright)

```bash
cd frontend
npx playwright test                    # все тесты
npx playwright test --headed           # с браузером
npx playwright test e2e/screenshots    # только скриншоты
```

Скриншоты сохраняются в `frontend/e2e/screenshots/`.

## Правила для новых фич

### ОБЯЗАТЕЛЬНО при добавлении нового функционала:

1. **Тесты** — каждый новый модуль/функция ДОЛЖЕН иметь тесты
   - Чистая логика → unit тесты без моков
   - LLM-зависимые → мок BaseAgent/generate
   - DB-зависимые → мок GraphQueries или tmp SQLite
   - API endpoints → FastAPI TestClient

2. **Регистрация в run_tests.py** — добавить новый модуль в `MODULE_MAP` и соответствующую группу в `GROUPS`

3. **Conftest фикстуры** — общие моки хранить в `tests/conftest.py`, не дублировать

4. **Coverage** — стремиться к 100% на новых модулях. Проверять: `python tests/run_tests.py --module <name> --cov`

## Агенты мира (World Agents)

Текущие агенты, отвечающие за мир:

| Агент | Файл | Роль |
|-------|------|------|
| DMAgent | agents/dm_agent.py | Нарративный DM — описывает действия игрока, генерирует квесты |
| NPCAgent | agents/npc_agent.py | Решения NPC — что делать, диалоги, взаимодействия |
| EventAgent | agents/event_agent.py | Мировые события — погода, стихии, случайности |
| NarratorAgent | agents/narrator_agent.py | Сценарист мира — анализ напряжений, сюжетные арки |
| FactionAgent | agents/faction_agent.py | Стратегии фракций — расширение, дипломатия, рейды |
| ReportAgent | agents/report_agent.py | Аналитика — обзор состояния мира |
| MemoryArchitect | agents/memory_architect.py | Консолидация памяти — сжатие, забывание, коллективная память |

### Планируемые агенты (TODO):
- **Economy Agent** — спрос/предложение, динамические цены (частично в simulation/economy.py)
- **Environment Agent** — погода, экология, стихийные бедствия (частично в simulation/environment.py)

## Ключевые зависимости

- **Neo4j** — граф мира (NPC, локации, отношения, события)
- **SQLite** — память NPC (embeddings, importance decay)
- **LLM (Ollama/OpenAI/Anthropic)** — через app/utils/llm_providers.py
- **Celery + Redis** — фоновые тики мира
- **sentence-transformers** — embeddings для семантического поиска памяти

## Конфигурация

Через `.env` или environment variables:
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- `REDIS_URL`
- `JWT_SECRET`
- `DATA_DIR` — директория с мирами
