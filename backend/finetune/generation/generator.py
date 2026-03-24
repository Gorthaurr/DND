"""Main orchestrator: cache -> Claude API -> validate -> save JSONL."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from pathlib import Path

from finetune.config import (
    CLAUDE_HAIKU_MODEL,
    CLAUDE_MAX_CONCURRENT,
    CLAUDE_SONNET_MODEL,
    SONNET_AGENT_TYPES,
)
from finetune.generation.cache import PromptCache
from finetune.generation.claude_client import ClaudeClient
from finetune.generation.validator import ResponseValidator

logger = logging.getLogger(__name__)


class DatasetGenerator:
    """Generates fine-tuning data by sending scenarios to Claude and validating responses."""

    def __init__(
        self,
        cache_dir: Path,
        raw_dir: Path,
        api_key: str,
        budget_usd: float = 50.0,
    ) -> None:
        self.cache = PromptCache(cache_dir / "prompt_cache.db")
        self.client = ClaudeClient(api_key, max_concurrent=CLAUDE_MAX_CONCURRENT)
        self.validator = ResponseValidator()
        self.budget = budget_usd
        self.raw_dir = raw_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self._results: list[dict] = []
        self._rejected: list[dict] = []

    # ── Single scenario ───────────────────────────────────────────────────────

    async def process_scenario(self, scenario: dict) -> dict | None:
        """Process one scenario: cache check -> Claude API -> validate -> return.

        Expected *scenario* keys:
            - agent_type: str
            - rendered_prompt: str
            - system_prompt: str  (optional)

        Returns the complete sample dict or None if validation failed.
        """
        agent_type: str = scenario["agent_type"]
        rendered_prompt: str = scenario["rendered_prompt"]
        system_prompt: str = scenario.get("system_prompt", "")

        prompt_hash = PromptCache.hash_prompt(rendered_prompt)

        # 1. Cache check.
        cached = self.cache.get(prompt_hash)
        if cached is not None:
            logger.debug("Cache hit for %s (hash=%s…)", agent_type, prompt_hash[:12])
            return self._build_sample(
                agent_type=agent_type,
                rendered_prompt=rendered_prompt,
                response=cached,
                model=self._model_for(agent_type),
                input_tokens=0,
                output_tokens=0,
                cached=True,
            )

        # 2. Call Claude.
        try:
            response_data = await self.client.generate(
                rendered_prompt, agent_type, system_prompt
            )
        except Exception:
            logger.exception("Claude API error for %s", agent_type)
            return None

        # 3. Sanitize + validate.
        response_data = self.validator.sanitize(agent_type, response_data)
        is_valid, error_msg = self.validator.validate(agent_type, response_data)

        if not is_valid:
            logger.warning("Validation failed for %s: %s", agent_type, error_msg)
            self._rejected.append(
                {"agent_type": agent_type, "prompt_hash": prompt_hash, "error": error_msg}
            )
            return None

        # 4. Cache the valid response.
        self.cache.put(prompt_hash, agent_type, response_data)

        return self._build_sample(
            agent_type=agent_type,
            rendered_prompt=rendered_prompt,
            response=response_data,
            model=self._model_for(agent_type),
            input_tokens=self.client.total_input_tokens,
            output_tokens=self.client.total_output_tokens,
            cached=False,
        )

    # ── Batch processing ──────────────────────────────────────────────────────

    async def process_batch(
        self, scenarios: list[dict], agent_type: str
    ) -> tuple[int, int]:
        """Process a batch of scenarios concurrently.

        Returns (accepted_count, rejected_count).
        Saves results to ``RAW_DIR/{agent_type}.jsonl`` incrementally.
        Checks budget before each batch.
        """
        if not self._check_budget():
            logger.error(
                "Budget exhausted ($%.2f / $%.2f). Stopping.",
                self.client.estimated_cost_usd,
                self.budget,
            )
            return 0, len(scenarios)

        self._results.clear()

        tasks = [
            asyncio.create_task(self.process_scenario(s))
            for s in scenarios
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        accepted = 0
        rejected = 0

        for result in results:
            if isinstance(result, Exception):
                logger.error("Unhandled error in scenario: %s", result)
                rejected += 1
            elif result is None:
                rejected += 1
            else:
                self._results.append(result)
                accepted += 1

        if self._results:
            self._save_results(agent_type)

        logger.info(
            "Batch %s done: %d accepted, %d rejected | cost ~$%.4f",
            agent_type,
            accepted,
            rejected,
            self.client.estimated_cost_usd,
        )
        return accepted, rejected

    # ── Persistence ───────────────────────────────────────────────────────────

    def _save_results(self, agent_type: str) -> None:
        """Flush accumulated results to JSONL file (append mode)."""
        path = self.raw_dir / f"{agent_type}.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            for sample in self._results:
                fh.write(json.dumps(sample, ensure_ascii=False) + "\n")
        logger.info("Wrote %d samples to %s", len(self._results), path)
        self._results.clear()

    # ── Budget guard ──────────────────────────────────────────────────────────

    def _check_budget(self) -> bool:
        """Return True if within budget."""
        return self.client.estimated_cost_usd < self.budget

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _model_for(agent_type: str) -> str:
        return CLAUDE_SONNET_MODEL if agent_type in SONNET_AGENT_TYPES else CLAUDE_HAIKU_MODEL

    @staticmethod
    def _build_sample(
        *,
        agent_type: str,
        rendered_prompt: str,
        response: dict,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached: bool,
    ) -> dict:
        return {
            "id": str(uuid.uuid4()),
            "agent_type": agent_type,
            "rendered_prompt": rendered_prompt,
            "response": response,
            "metadata": {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cached": cached,
            },
        }
