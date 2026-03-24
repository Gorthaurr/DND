"""Stratified train/val/test split for ChatML-formatted JSONL datasets."""

import json
import logging
import random
from pathlib import Path

logger = logging.getLogger(__name__)


class DatasetSplitter:
    """Splits formatted JSONL data into train/val/test with stratification by agent_type."""

    def __init__(
        self,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seed: int = 42,
    ):
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, (
            "Ratios must sum to 1.0"
        )
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.seed = seed

    def _extract_agent_type(self, sample: dict) -> str:
        """Extract agent_type from system message content."""
        system_msg = sample["messages"][0]["content"]
        prefix = "Agent type: "
        start = system_msg.index(prefix) + len(prefix)
        end = system_msg.index(".", start)
        return system_msg[start:end]

    def split(self, input_dir: Path, output_dir: Path) -> dict:
        """Read all formatted JSONL files, split stratified by agent_type.

        Writes train.jsonl, val.jsonl, test.jsonl into *output_dir*.
        Returns split statistics.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Group samples by agent_type
        by_type: dict[str, list[dict]] = {}
        for jsonl_file in sorted(input_dir.glob("*.jsonl")):
            with open(jsonl_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    sample = json.loads(line)
                    agent_type = self._extract_agent_type(sample)
                    by_type.setdefault(agent_type, []).append(sample)

        rng = random.Random(self.seed)
        splits: dict[str, list[dict]] = {"train": [], "val": [], "test": []}
        by_type_stats: dict[str, dict[str, int]] = {}

        for agent_type, samples in sorted(by_type.items()):
            rng.shuffle(samples)
            n = len(samples)
            n_train = max(1, round(n * self.train_ratio))
            n_val = max(1, round(n * self.val_ratio)) if n > 2 else 0
            n_test = n - n_train - n_val

            splits["train"].extend(samples[:n_train])
            splits["val"].extend(samples[n_train : n_train + n_val])
            splits["test"].extend(samples[n_train + n_val :])

            by_type_stats[agent_type] = {
                "train": n_train,
                "val": n_val,
                "test": n_test,
            }
            logger.info(
                "Agent '%s': %d train / %d val / %d test",
                agent_type, n_train, n_val, n_test,
            )

        # Shuffle each split for training stability
        for key in splits:
            rng.shuffle(splits[key])

        # Write output files
        for split_name, samples in splits.items():
            out_path = output_dir / f"{split_name}.jsonl"
            with open(out_path, "w", encoding="utf-8") as f:
                for sample in samples:
                    f.write(json.dumps(sample, ensure_ascii=False) + "\n")

        result = {
            "train": len(splits["train"]),
            "val": len(splits["val"]),
            "test": len(splits["test"]),
            "by_type": by_type_stats,
        }
        logger.info("Split complete: %s", {k: v for k, v in result.items() if k != "by_type"})
        return result
