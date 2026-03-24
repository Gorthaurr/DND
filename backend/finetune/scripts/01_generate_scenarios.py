"""Generate synthetic scenarios for all agent types.

Usage:
    python -m finetune.scripts.01_generate_scenarios [--agent-type TYPE] [--count N] [--seed 42]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from finetune.config import ALL_AGENT_TYPES, SCENARIO_COUNTS, SCENARIOS_DIR
from finetune.scenarios.npc_decision import NPCDecisionGenerator
from finetune.scenarios.npc_dialogue import NPCDialogueGenerator
from finetune.scenarios.npc_interact import NPCInteractGenerator
from finetune.scenarios.npc_interjection import NPCInterjectionGenerator
from finetune.scenarios.combat_intent import CombatIntentGenerator
from finetune.scenarios.combat_narrate import CombatNarrateGenerator
from finetune.scenarios.dm_narrate import DMNarrateGenerator
from finetune.scenarios.scenario_generate import ScenarioGenerateGenerator
from finetune.scenarios.scenario_advance import ScenarioAdvanceGenerator
from finetune.scenarios.event_generate import EventGenerateGenerator
from finetune.scenarios.quest_generate import QuestGenerateGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

GENERATOR_MAP = {
    "npc_decision": NPCDecisionGenerator,
    "npc_dialogue": NPCDialogueGenerator,
    "npc_interact": NPCInteractGenerator,
    "npc_interjection": NPCInterjectionGenerator,
    "combat_intent": CombatIntentGenerator,
    "combat_narrate": CombatNarrateGenerator,
    "dm_narrate": DMNarrateGenerator,
    "scenario_generate": ScenarioGenerateGenerator,
    "scenario_advance": ScenarioAdvanceGenerator,
    "event_generate": EventGenerateGenerator,
    "quest_generate": QuestGenerateGenerator,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic scenarios for fine-tuning.")
    parser.add_argument(
        "--agent-type",
        choices=ALL_AGENT_TYPES,
        default=None,
        help="Generate for a single agent type. Default: all types.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Override scenario count (default: from config.SCENARIO_COUNTS).",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42).")
    return parser.parse_args()


def generate_for_type(agent_type: str, count: int, seed: int, output_dir: Path) -> int:
    """Generate scenarios for one agent type, save to JSONL. Returns count written."""
    gen_cls = GENERATOR_MAP.get(agent_type)
    if gen_cls is None:
        logger.error("No generator registered for agent type: %s", agent_type)
        return 0

    logger.info("Generating %d scenarios for '%s' (seed=%d)...", count, agent_type, seed)
    generator = gen_cls(seed=seed)
    scenarios = generator.generate_batch(count)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{agent_type}.jsonl"

    with open(output_path, "w", encoding="utf-8") as f:
        for scenario in scenarios:
            f.write(json.dumps(scenario, ensure_ascii=False) + "\n")

    logger.info("  -> Wrote %d scenarios to %s", len(scenarios), output_path)
    return len(scenarios)


def main() -> None:
    args = parse_args()
    types_to_generate = [args.agent_type] if args.agent_type else ALL_AGENT_TYPES

    total = 0
    summary: dict[str, int] = {}

    for agent_type in types_to_generate:
        count = args.count if args.count is not None else SCENARIO_COUNTS.get(agent_type, 100)
        try:
            n = generate_for_type(agent_type, count, args.seed, SCENARIOS_DIR)
            summary[agent_type] = n
            total += n
        except Exception as exc:
            logger.error("Failed to generate scenarios for '%s': %s", agent_type, exc, exc_info=True)
            summary[agent_type] = 0

    print("\n=== Scenario Generation Summary ===")
    for at, n in summary.items():
        print(f"  {at:25s} {n:>6d} scenarios")
    print(f"  {'TOTAL':25s} {total:>6d} scenarios")


if __name__ == "__main__":
    main()
