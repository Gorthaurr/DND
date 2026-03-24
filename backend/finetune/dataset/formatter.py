"""Converts raw JSONL (from Claude API) into ChatML training format for Qwen 2.5."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = (
    "You are a D&D Living World game engine. "
    "Agent type: {agent_type}. "
    "Respond ONLY in valid JSON."
)


class ChatMLFormatter:
    """Converts raw JSONL dataset to ChatML training format."""

    def format_sample(self, sample: dict) -> dict:
        """Convert one raw sample to ChatML format.

        Input sample fields:
            - agent_type: str (e.g. "combat", "narrative", "world")
            - rendered_prompt: str (the user prompt sent to Claude)
            - response: dict (the JSON response from Claude)

        Returns ChatML messages structure for Qwen 2.5 SFT.
        """
        agent_type = sample["agent_type"]
        rendered_prompt = sample["rendered_prompt"]
        response = sample["response"]

        response_text = (
            json.dumps(response, ensure_ascii=False)
            if isinstance(response, dict)
            else str(response)
        )

        return {
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_TEMPLATE.format(agent_type=agent_type),
                },
                {
                    "role": "user",
                    "content": rendered_prompt,
                },
                {
                    "role": "assistant",
                    "content": response_text,
                },
            ]
        }

    def format_file(self, input_path: Path, output_path: Path) -> int:
        """Format entire JSONL file. Returns count of formatted samples."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        count = 0

        with open(input_path, "r", encoding="utf-8") as fin, \
             open(output_path, "w", encoding="utf-8") as fout:
            for line_num, line in enumerate(fin, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    sample = json.loads(line)
                    formatted = self.format_sample(sample)
                    fout.write(json.dumps(formatted, ensure_ascii=False) + "\n")
                    count += 1
                except (json.JSONDecodeError, KeyError) as exc:
                    logger.warning(
                        "Skipping line %d in %s: %s", line_num, input_path.name, exc
                    )

        logger.info("Formatted %d samples: %s -> %s", count, input_path.name, output_path.name)
        return count

    def format_all(self, raw_dir: Path, output_dir: Path) -> dict[str, int]:
        """Format all raw JSONL files in *raw_dir*.

        Each file is expected to be named ``{agent_type}.jsonl``.
        Returns mapping ``{agent_type: sample_count}``.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        stats: dict[str, int] = {}

        for raw_file in sorted(raw_dir.glob("*.jsonl")):
            agent_type = raw_file.stem
            out_file = output_dir / f"{agent_type}.jsonl"
            count = self.format_file(raw_file, out_file)
            stats[agent_type] = count

        logger.info("Total formatted: %s", stats)
        return stats
