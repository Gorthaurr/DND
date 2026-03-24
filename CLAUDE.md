# D&D Living World Engine

## Цели проекта

### Фаза 1 — Полный D&D 5e движок (без AI) [ГОТОВО]
- [x] Полная система заклинаний — 260 spells (cantrips-5 уровень), все школы, все классы
- [x] Class features — 195 способностей для 12 классов (levels 1-20)
- [x] Система навыков — 18 skills с привязкой к ability scores, expertise, passive scores
- [x] Conditions — 16 состояний с механическими эффектами (advantage/disadvantage, auto-fail saves)
- [x] Расширенный инвентарь — 65 предметов + 24 магических предмета с MagicItem dataclass
- [x] Spell casting в боевой системе — spell_engine.py (attack rolls, saving throws, damage, healing)
- [x] Назначены всем 28 NPC заклинания, навыки и saving throw proficiencies
- [x] Feats — 40 подвигов с проверкой пререквизитов
- [x] Short rest / Long rest — hit dice spending, ресурсы по классам, полное восстановление
- [x] Death saving throws — DeathTracker, massive damage, damage while dying, stabilize
- [x] Conditions интегрированы в бой — advantage/disadvantage, incapacitated skip turn, death saves

### Фаза 2 — Сбор датасета для fine-tune [PIPELINE READY]
- [x] 11 scenario generators (~16,300 сценариев) для всех типов агентов
- [x] Claude API client (async, batching, cache, budget guard, retry)
- [x] SQLite disk cache (SHA256 промпта → ответ, без дублей)
- [x] Pydantic валидация ответов (11 схем)
- [x] ChatML formatter + stratified splitter
- [ ] Запустить генерацию сценариев: `python -m finetune.scripts.01_generate_scenarios`
- [ ] Запустить генерацию датасета: `python -m finetune.scripts.02_generate_dataset`
- [ ] Подготовить training data: `python -m finetune.scripts.03_prepare_training`

### Фаза 3 — Fine-tune Qwen 2.5 14B [PIPELINE READY]
- [x] QLoRA training script (Unsloth, rank 32, 4-bit, RTX 5080)
- [x] LoRA merge + GGUF export + Ollama registration
- [x] Evaluation framework (JSON validity, schema compliance, action entropy)
- [ ] Запустить обучение: `python -m finetune.scripts.04_train`
- [ ] Оценить: `python -m finetune.scripts.05_evaluate`
- [ ] Задеплоить: `python -m finetune.scripts.06_deploy`

### Фаза 4 — Динамическая эволюция NPC [ГОТОВО]
- [x] Динамическое изменение целей — GoalStatus (active/completed/failed/abandoned), прогресс, авто-генерация
- [x] Травмы и фобии — Fear система (trigger, intensity с decay, origin event)
- [x] Дрейф личности — TraitScale (Big Five 0.0-1.0), сдвиги от 15 типов событий
- [x] Дрейф архетипа — cosine similarity между TraitScale и 23 профилями, 5-day threshold
- [x] Теги отношений — "betrayer", "savior", "rival", "killer", "ally" с decay
- [x] Эволюция интегрирована в world tick, LLM видит fears/goals/tags в промпте
- [x] Nemesis arcs — NemesisState (5 стадий: grudge→rival→nemesis→arch_nemesis→broken), адаптации, LLM directives
- [x] Межсессионные события — inter_session.py (детерминированные события, fear decay, goal abandonment, nemesis escalation)

## Архитектура

```
backend/app/
  dnd/           # D&D 5e правила (детерминированный код, без LLM)
    dice.py      # Кубики
    rules.py     # AC, attack rolls, saving throws, XP
    classes.py   # Классы с hit die, proficiencies, spell slots
    races.py     # Расы с бонусами
    equipment.py # Оружие, броня, предметы
    spells.py        # 260 заклинаний с полными механиками
    spell_engine.py  # Движок каста (attack rolls, saves, damage, healing, conditions)
    features.py      # 195 class features по уровням
    skills.py        # 18 навыков D&D 5e
    conditions.py    # 16 состояний с механическими эффектами
    feats.py         # 40 подвигов с пререквизитами
    rest.py          # Short rest / Long rest механики
    death_saves.py   # Death saving throws, massive damage, stabilize
  simulation/
    evolution.py       # Ядро эволюции NPC (детерминированный, без LLM)
    evolution_rules.py # Таблицы сдвигов, карты страхов, шаблоны целей
    evolution_migration.py # Ленивая миграция старых NPC
  models/
    evolution.py       # TraitScale, Fear, Goal, RelationshipTag, NPCEvolutionState
  agents/        # LLM-агенты (мозг NPC и DM)
  models/        # Pydantic-модели данных
  simulation/    # World tick, события, слухи
  graph/         # Neo4j — граф мира
```

## Стек
- **Backend**: Python 3.12, FastAPI, Celery, Neo4j, SQLite
- **Frontend**: Next.js 14, React 18, TailwindCSS
- **LLM**: Ollama (qwen2.5:14b), позже — fine-tuned модель
- **DB**: Neo4j (граф мира), SQLite (память NPC)

## Правила кода
- Весь D&D движок — чистый детерминированный Python, без LLM
- LLM только для решений NPC и нарратива
- Модель НЕ бросает кубики — это делает код
- Каждый файл в dnd/ — отдельная ответственность, <150 строк где возможно
