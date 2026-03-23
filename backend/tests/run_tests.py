#!/usr/bin/env python3
"""
Единая точка входа для тестирования DND backend.

Использование:
    python tests/run_tests.py                    # Все тесты
    python tests/run_tests.py --module dice      # Конкретный модуль
    python tests/run_tests.py --module agents    # Все агенты
    python tests/run_tests.py --cov              # С покрытием
    python tests/run_tests.py --module rules --cov  # Модуль + покрытие
    python tests/run_tests.py --list             # Показать доступные модули

Модули сгруппированы по категориям:
    dnd:        dice, classes, races, equipment, rules, combat_narrator
    models:     character, player, quest, scenario, world, schemas, npc_models, archetypes, memory, world_store
    agents:     base, speech_patterns, dm, npc, event, report, narrator, faction, memory_architect
    simulation: economy, evolution, environment, schedule, reputation, quests, analytics,
                ticker, background, events, interaction, scheduler
    graph:      queries, connection
    api:        routes, world_builder, websocket
    llm:        llm, providers
    utils:      embeddings, config, auth
    worldgen:   generator
"""

import argparse
import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent
BACKEND_DIR = TESTS_DIR.parent

# --- Module -> test file mapping ---

MODULE_MAP = {
    # === DND Core ===
    "dice":             "test_dnd_dice.py",
    "classes":          "test_dnd_classes.py",
    "races":            "test_dnd_races.py",
    "equipment":        "test_dnd_equipment.py",
    "rules":            "test_dnd_rules.py",
    "combat_narrator":  "test_dnd_combat_narrator.py",

    # === Models ===
    "character":        "test_character_model.py",
    "player":           "test_models_pydantic.py",
    "quest":            "test_models_pydantic.py",
    "scenario":         "test_models_pydantic.py",
    "world":            "test_models_pydantic.py",
    "schemas":          "test_models_pydantic.py",
    "npc_models":       "test_npc_models.py",
    "archetypes":       "test_archetypes.py",
    "memory":           "test_models_memory.py",
    "world_store":      "test_models_world_store.py",

    # === Agents ===
    "base":             "test_base_agent.py",
    "speech_patterns":  "test_speech_patterns.py",
    "dm":               "test_agents_dm.py",
    "npc":              "test_agents_npc.py",
    "event":            "test_agents_event.py",
    "report":           "test_agents_report.py",
    "narrator":         "test_agents_narrator.py",
    "faction":          "test_faction_agent.py",
    "memory_architect": "test_agents_memory_architect.py",

    # === Simulation ===
    "economy":          "test_economy.py",
    "evolution":        "test_evolution.py",
    "environment":      "test_environment.py",
    "schedule":         "test_simulation_schedule_full.py",
    "reputation":       "test_reputation.py",
    "quests":           "test_simulation_quests_full.py",
    "analytics":        "test_simulation_analytics_full.py",
    "ticker":           "test_simulation_ticker.py",
    "background":       "test_simulation_background.py",
    "events":           "test_simulation_events.py",
    "interaction":      "test_simulation_interaction.py",
    "scheduler":        "test_schedule.py",

    # === Graph ===
    "queries":          "test_graph_queries.py",
    "connection":       "test_graph_connection.py",

    # === API ===
    "routes":           "test_api_routes.py",
    "world_builder":    "test_api_world_builder.py",
    "websocket":        "test_websocket_rooms.py",
    "character_api":    "test_api_character.py",
    "rooms":            "test_api_rooms.py",

    # === LLM ===
    "llm":              "test_llm_full.py",
    "providers":        "test_llm_providers_full.py",

    # === Utils ===
    "embeddings":       "test_embeddings.py",
    "config":           "test_config.py",
    "auth":             "test_auth.py",
    "auth_routes":      "test_auth_routes.py",

    # === Graph (extra) ===
    "schema":           "test_graph_schema.py",

    # === DB ===
    "postgres":         "test_db_postgres.py",

    # === Main ===
    "main":             "test_main_app.py",

    # === Worldgen ===
    "generator":        "test_worldgen.py",
}

# Группы для --module group_name
GROUPS = {
    "dnd":        ["dice", "classes", "races", "equipment", "rules", "combat_narrator"],
    "models":     ["character", "player", "quest", "scenario", "world", "schemas", "npc_models",
                   "archetypes", "memory", "world_store"],
    "agents":     ["base", "speech_patterns", "dm", "npc", "event", "report", "narrator",
                   "faction", "memory_architect"],
    "simulation": ["economy", "evolution", "environment", "schedule", "reputation", "quests",
                   "analytics", "ticker", "background", "events", "interaction", "scheduler"],
    "graph":      ["queries", "connection", "schema"],
    "api":        ["routes", "world_builder", "websocket", "character_api", "rooms"],
    "llm":        ["llm", "providers"],
    "utils":      ["embeddings", "config", "auth", "auth_routes"],
    "db":         ["postgres"],
    "app":        ["main"],
    "worldgen":   ["generator"],
}

# Файлы, которые нужно игнорировать (сломанные/legacy)
IGNORE_FILES = ["test_llm.py", "test_combat.py", "test_rumors.py"]


def list_modules():
    print("\n[*] Available test modules:\n")
    for group, modules in GROUPS.items():
        print(f"  [+]  {group}:")
        for mod in modules:
            test_file = MODULE_MAP.get(mod, "?")
            exists = (TESTS_DIR / test_file).exists() if test_file != "?" else False
            status = "[OK]" if exists else "[XX]"
            print(f"      {status} {mod:20s} -> {test_file}")
    print(f"\n  Total modules: {len(MODULE_MAP)}")
    print(f"\n  Groups: {', '.join(GROUPS.keys())}")
    print(f"\n  Example: python tests/run_tests.py --module dnd")
    print(f"  Example: python tests/run_tests.py --module dice --cov\n")


def resolve_modules(name: str) -> list[str]:
    """Resolve module name or group name to list of test files."""
    if name in GROUPS:
        modules = GROUPS[name]
    elif name in MODULE_MAP:
        modules = [name]
    else:
        print(f"[XX] Unknown module: {name}")
        print(f"   Available: {', '.join(sorted(MODULE_MAP.keys()))}")
        print(f"   Groups: {', '.join(GROUPS.keys())}")
        sys.exit(1)
        return []

    files = []
    for mod in modules:
        test_file = MODULE_MAP.get(mod)
        if test_file and (TESTS_DIR / test_file).exists():
            files.append(test_file)
        else:
            print(f"  [!]  Test for '{mod}' not found: {test_file}")
    return list(set(files))  # deduplicate


def build_pytest_cmd(module: str | None, cov: bool, verbose: bool, extra_args: list) -> list[str]:
    cmd = [sys.executable, "-m", "pytest"]

    if module:
        files = resolve_modules(module)
        if not files:
            print("[XX] No test files available")
            sys.exit(1)
        for f in files:
            cmd.append(f"tests/{f}")
    else:
        cmd.append("tests/")
        for ign in IGNORE_FILES:
            cmd.extend(["--ignore", f"tests/{ign}"])

    if cov:
        cmd.extend(["--cov=app", "--cov-report=term-missing"])

    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    cmd.extend(extra_args)
    return cmd


def main():
    parser = argparse.ArgumentParser(description="DND Backend Test Runner")
    parser.add_argument("--module", "-m", help="Module or group name (dice, agents, dnd, ...)")
    parser.add_argument("--cov", action="store_true", help="Show coverage")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--list", "-l", action="store_true", help="Show all modules")
    parser.add_argument("extra", nargs="*", help="Extra pytest args")

    args = parser.parse_args()

    if args.list:
        list_modules()
        return

    cmd = build_pytest_cmd(args.module, args.cov, args.verbose, args.extra)

    print(f"[>] Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(BACKEND_DIR))
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
