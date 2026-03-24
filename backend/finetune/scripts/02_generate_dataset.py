"""Generate dataset via Claude API from scenarios.

Usage:
    python -m finetune.scripts.02_generate_dataset [--agent-type TYPE] [--budget 50.0]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from finetune.config import (
    ALL_AGENT_TYPES,
    ANTHROPIC_API_KEY,
    CACHE_DIR,
    CLAUDE_BUDGET_USD,
    RAW_DIR,
    SCENARIOS_DIR,
)
from finetune.generation.generator import DatasetGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BATCH_SIZE = 20


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate dataset via Claude API.")
    parser.add_argument(
        "--agent-type",
        choices=ALL_AGENT_TYPES,
        default=None,
        help="Process a single agent type. Default: all types.",
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=CLAUDE_BUDGET_USD,
        help=f"Max budget in USD (default: {CLAUDE_BUDGET_USD}).",
    )
    return parser.parse_args()


def load_scenarios(agent_type: str) -> list[dict]:
    """Load scenarios from JSONL file."""
    path = SCENARIOS_DIR / f"{agent_type}.jsonl"
    if not path.exists():
        logger.warning("No scenarios file found: %s", path)
        return []

    scenarios = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                scenarios.append(json.loads(line))
    return scenarios


async def process_agent_type(
    generator: DatasetGenerator,
    agent_type: str,
    scenarios: list[dict],
) -> tuple[int, int]:
    """Process all scenarios for one agent type in batches."""
    total_accepted = 0
    total_rejected = 0

    for batch_start in range(0, len(scenarios), BATCH_SIZE):
        batch = scenarios[batch_start : batch_start + BATCH_SIZE]
        logger.info(
            "[%s] Processing batch %d-%d / %d",
            agent_type,
            batch_start + 1,
            min(batch_start + BATCH_SIZE, len(scenarios)),
            len(scenarios),
        )

        accepted, rejected = await generator.process_batch(batch, agent_type)
        total_accepted += accepted
        total_rejected += rejected

    return total_accepted, total_rejected


async def run(args: argparse.Namespace) -> None:
    if not ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set. Export it before running.")
        sys.exit(1)

    generator = DatasetGenerator(
        cache_dir=CACHE_DIR,
        raw_dir=RAW_DIR,
        api_key=ANTHROPIC_API_KEY,
        budget_usd=args.budget,
    )

    types_to_process = [args.agent_type] if args.agent_type else ALL_AGENT_TYPES
    summary: dict[str, dict] = {}

    for agent_type in types_to_process:
        scenarios = load_scenarios(agent_type)
        if not scenarios:
            logger.warning("Skipping '%s': no scenarios found.", agent_type)
            summary[agent_type] = {"accepted": 0, "rejected": 0, "total": 0}
            continue

        logger.info("=== Processing '%s' (%d scenarios) ===", agent_type, len(scenarios))
        try:
            accepted, rejected = await process_agent_type(generator, agent_type, scenarios)
            summary[agent_type] = {
                "accepted": accepted,
                "rejected": rejected,
                "total": len(scenarios),
            }
        except Exception as exc:
            logger.error("Failed processing '%s': %s", agent_type, exc)
            summary[agent_type] = {"accepted": 0, "rejected": 0, "total": len(scenarios)}

    print("\n=== Dataset Generation Summary ===")
    print(f"  Budget: ${args.budget:.2f} | Estimated cost: ${generator.client.estimated_cost_usd:.4f}")
    total_acc = 0
    total_rej = 0
    for at, info in summary.items():
        acc, rej = info["accepted"], info["rejected"]
        total_acc += acc
        total_rej += rej
        print(f"  {at:25s}  accepted={acc:>5d}  rejected={rej:>5d}  total={info['total']:>5d}")
    print(f"  {'TOTAL':25s}  accepted={total_acc:>5d}  rejected={total_rej:>5d}")


def main() -> None:
    args = parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
