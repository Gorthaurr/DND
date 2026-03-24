"""Prepare training data: format to ChatML + stratified split.

Usage:
    python -m finetune.scripts.03_prepare_training
"""

from __future__ import annotations

import argparse
import json
import logging
import random
from collections import defaultdict
from pathlib import Path

from finetune.config import (
    PROCESSED_DIR,
    RAW_DIR,
    TEST_RATIO,
    TRAIN_RATIO,
    VAL_RATIO,
)
from finetune.dataset.formatter import ChatMLFormatter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare training data: format + split.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for splitting.")
    return parser.parse_args()


class DatasetSplitter:
    """Stratified split of ChatML samples by agent_type into train/val/test."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)

    def split(
        self,
        samples: list[dict],
        train_ratio: float = TRAIN_RATIO,
        val_ratio: float = VAL_RATIO,
        test_ratio: float = TEST_RATIO,
    ) -> tuple[list[dict], list[dict], list[dict]]:
        """Stratified split preserving agent_type distribution."""
        # Group by agent_type (extract from system message)
        groups: dict[str, list[dict]] = defaultdict(list)
        for sample in samples:
            at = self._extract_agent_type(sample)
            groups[at].append(sample)

        train, val, test = [], [], []

        for at, items in groups.items():
            self.rng.shuffle(items)
            n = len(items)
            n_train = max(1, int(n * train_ratio))
            n_val = max(1, int(n * val_ratio))

            train.extend(items[:n_train])
            val.extend(items[n_train : n_train + n_val])
            test.extend(items[n_train + n_val :])

        self.rng.shuffle(train)
        self.rng.shuffle(val)
        self.rng.shuffle(test)

        return train, val, test

    @staticmethod
    def _extract_agent_type(sample: dict) -> str:
        """Extract agent type from ChatML system message."""
        messages = sample.get("messages", [])
        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content", "")
                marker = "Agent type: "
                if marker in content:
                    return content.split(marker, 1)[1].split(".")[0].strip()
        return "unknown"


def save_jsonl(samples: list[dict], path: Path) -> None:
    """Write samples to JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
    logger.info("Wrote %d samples to %s", len(samples), path)


def count_by_type(samples: list[dict], splitter: DatasetSplitter) -> dict[str, int]:
    """Count samples per agent type."""
    counts: dict[str, int] = defaultdict(int)
    for s in samples:
        at = splitter._extract_agent_type(s)
        counts[at] += 1
    return dict(counts)


def main() -> None:
    args = parse_args()

    # Step 1: Format raw -> ChatML
    formatter = ChatMLFormatter()
    logger.info("Formatting raw data from %s ...", RAW_DIR)

    if not RAW_DIR.exists() or not list(RAW_DIR.glob("*.jsonl")):
        logger.error("No raw JSONL files found in %s. Run 02_generate_dataset first.", RAW_DIR)
        return

    format_stats = formatter.format_all(RAW_DIR, PROCESSED_DIR / "formatted")
    print("\n=== Formatting Stats ===")
    for at, count in format_stats.items():
        print(f"  {at:25s} {count:>6d} samples")
    print(f"  {'TOTAL':25s} {sum(format_stats.values()):>6d} samples")

    # Step 2: Load all formatted samples
    all_samples: list[dict] = []
    formatted_dir = PROCESSED_DIR / "formatted"
    for f in sorted(formatted_dir.glob("*.jsonl")):
        with open(f, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    all_samples.append(json.loads(line))

    if not all_samples:
        logger.error("No formatted samples found. Check formatting step.")
        return

    # Step 3: Stratified split
    splitter = DatasetSplitter(seed=args.seed)
    train, val, test = splitter.split(all_samples)

    save_jsonl(train, PROCESSED_DIR / "train.jsonl")
    save_jsonl(val, PROCESSED_DIR / "val.jsonl")
    save_jsonl(test, PROCESSED_DIR / "test.jsonl")

    # Step 4: Print distribution
    print("\n=== Split Distribution ===")
    print(f"  Train: {len(train):>6d} ({len(train)/len(all_samples):.1%})")
    print(f"  Val:   {len(val):>6d} ({len(val)/len(all_samples):.1%})")
    print(f"  Test:  {len(test):>6d} ({len(test)/len(all_samples):.1%})")
    print(f"  Total: {len(all_samples):>6d}")

    print("\n=== Per-Type Distribution (train) ===")
    train_counts = count_by_type(train, splitter)
    for at, n in sorted(train_counts.items()):
        print(f"  {at:25s} {n:>6d}")


if __name__ == "__main__":
    main()
