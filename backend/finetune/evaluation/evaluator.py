"""Model evaluator: compare prompted vs fine-tuned vs gold on a test set."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path

import httpx

from finetune.evaluation.metrics import (
    action_entropy,
    avg_response_length,
    json_validity_rate,
    schema_compliance_rate,
)

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Compare prompted vs fine-tuned vs Claude gold on test set."""

    def __init__(self, test_data_path: Path) -> None:
        self.test_data_path = test_data_path
        self.samples: list[dict] = []
        self._load_test_data()

    def _load_test_data(self) -> None:
        """Load test.jsonl into memory."""
        if not self.test_data_path.exists():
            raise FileNotFoundError(f"Test data not found: {self.test_data_path}")
        with open(self.test_data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.samples.append(json.loads(line))
        logger.info("Loaded %d test samples from %s", len(self.samples), self.test_data_path)

    async def evaluate_model(
        self,
        model_name: str,
        ollama_url: str = "http://localhost:11434",
    ) -> dict:
        """Run all test prompts through an Ollama model and compute metrics.

        Returns a dict with overall and per-agent-type metrics.
        """
        raw_responses: list[str] = []
        parsed_responses: list[dict] = []
        agent_types: list[str] = []
        latencies: list[float] = []

        async with httpx.AsyncClient(timeout=120.0) as client:
            for i, sample in enumerate(self.samples):
                messages = sample.get("messages", [])
                user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
                system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")

                agent_type = self._extract_agent_type(system_msg)
                agent_types.append(agent_type)

                start = time.perf_counter()
                try:
                    resp = await client.post(
                        f"{ollama_url}/api/chat",
                        json={
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": system_msg},
                                {"role": "user", "content": user_msg},
                            ],
                            "stream": False,
                        },
                    )
                    resp.raise_for_status()
                    content = resp.json()["message"]["content"]
                except Exception as exc:
                    logger.warning("Sample %d failed for model %s: %s", i, model_name, exc)
                    content = ""
                elapsed_ms = (time.perf_counter() - start) * 1000
                latencies.append(elapsed_ms)

                raw_responses.append(content)
                try:
                    parsed_responses.append(json.loads(content))
                except (json.JSONDecodeError, TypeError):
                    parsed_responses.append({})

                if (i + 1) % 10 == 0:
                    logger.info("[%s] Evaluated %d / %d samples", model_name, i + 1, len(self.samples))

        # Overall metrics
        result: dict = {
            "model": model_name,
            "total_samples": len(self.samples),
            "json_validity": json_validity_rate(raw_responses),
            "schema_compliance": self._overall_schema_compliance(agent_types, parsed_responses),
            "avg_latency_ms": sum(latencies) / max(len(latencies), 1),
            "avg_response_length": avg_response_length(raw_responses),
            "by_agent_type": {},
        }

        # Per-agent-type breakdown
        type_groups: dict[str, dict] = {}
        for at, raw, parsed in zip(agent_types, raw_responses, parsed_responses):
            if at not in type_groups:
                type_groups[at] = {"raw": [], "parsed": []}
            type_groups[at]["raw"].append(raw)
            type_groups[at]["parsed"].append(parsed)

        for at, group in type_groups.items():
            entry: dict = {
                "count": len(group["raw"]),
                "json_validity": json_validity_rate(group["raw"]),
                "schema_compliance": schema_compliance_rate(at, group["parsed"]),
            }
            if at == "npc_decision":
                entry["action_entropy"] = action_entropy(group["parsed"])
            result["by_agent_type"][at] = entry

        return result

    def compare(self, results: list[dict]) -> str:
        """Generate a markdown comparison table from multiple evaluate_model results."""
        if not results:
            return "No results to compare."

        header = "| Metric | " + " | ".join(r["model"] for r in results) + " |"
        sep = "|---|" + "|".join("---" for _ in results) + "|"

        rows = [
            self._row("Total samples", [r["total_samples"] for r in results], fmt="d"),
            self._row("JSON validity", [r["json_validity"] for r in results], fmt="%"),
            self._row("Schema compliance", [r["schema_compliance"] for r in results], fmt="%"),
            self._row("Avg latency (ms)", [r["avg_latency_ms"] for r in results], fmt=".1f"),
            self._row("Avg resp length", [r["avg_response_length"] for r in results], fmt=".0f"),
        ]

        lines = [header, sep] + rows

        # Per-agent-type sub-tables
        all_types = set()
        for r in results:
            all_types.update(r.get("by_agent_type", {}).keys())

        for at in sorted(all_types):
            lines.append(f"\n### {at}")
            sub_header = "| Metric | " + " | ".join(r["model"] for r in results) + " |"
            lines.append(sub_header)
            lines.append(sep)

            vals_jv = []
            vals_sc = []
            vals_ae = []
            for r in results:
                info = r.get("by_agent_type", {}).get(at, {})
                vals_jv.append(info.get("json_validity", 0.0))
                vals_sc.append(info.get("schema_compliance", 0.0))
                if at == "npc_decision":
                    vals_ae.append(info.get("action_entropy", 0.0))

            lines.append(self._row("JSON validity", vals_jv, fmt="%"))
            lines.append(self._row("Schema compliance", vals_sc, fmt="%"))
            if at == "npc_decision" and vals_ae:
                lines.append(self._row("Action entropy", vals_ae, fmt=".3f"))

        return "\n".join(lines)

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_agent_type(system_msg: str) -> str:
        """Extract agent type from system message."""
        marker = "Agent type: "
        if marker in system_msg:
            after = system_msg.split(marker, 1)[1]
            return after.split(".")[0].strip()
        return "unknown"

    @staticmethod
    def _overall_schema_compliance(agent_types: list[str], parsed: list[dict]) -> float:
        if not parsed:
            return 0.0
        valid = 0
        for at, p in zip(agent_types, parsed):
            from finetune.schemas import validate_response
            ok, _ = validate_response(at, p)
            if ok:
                valid += 1
        return valid / len(parsed)

    @staticmethod
    def _row(label: str, values: list, fmt: str = ".3f") -> str:
        cells = []
        for v in values:
            if fmt == "%":
                cells.append(f"{v:.1%}")
            elif fmt == "d":
                cells.append(str(int(v)))
            else:
                cells.append(f"{v:{fmt}}")
        return f"| {label} | " + " | ".join(cells) + " |"
