"""Evaluate fine-tuned model vs prompted baseline.

Usage:
    python -m finetune.scripts.05_evaluate [--models qwen2.5:14b,qwen2.5:14b-dnd]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from finetune.config import OLLAMA_MODEL_NAME, PROCESSED_DIR
from finetune.evaluation.evaluator import ModelEvaluator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_MODELS = f"qwen2.5:14b,{OLLAMA_MODEL_NAME}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate fine-tuned model vs baseline.")
    parser.add_argument(
        "--models",
        type=str,
        default=DEFAULT_MODELS,
        help=f"Comma-separated model names (default: {DEFAULT_MODELS}).",
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama API URL (default: http://localhost:11434).",
    )
    parser.add_argument(
        "--test-data",
        type=str,
        default=None,
        help="Path to test.jsonl (default: data/processed/test.jsonl).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save results JSON to this path.",
    )
    return parser.parse_args()


async def run(args: argparse.Namespace) -> None:
    test_path = Path(args.test_data) if args.test_data else PROCESSED_DIR / "test.jsonl"

    if not test_path.exists():
        logger.error("Test data not found: %s. Run 03_prepare_training first.", test_path)
        sys.exit(1)

    model_names = [m.strip() for m in args.models.split(",") if m.strip()]
    if not model_names:
        logger.error("No models specified.")
        sys.exit(1)

    evaluator = ModelEvaluator(test_path)
    print(f"\n=== Model Evaluation ===")
    print(f"  Test samples: {len(evaluator.samples)}")
    print(f"  Models:       {', '.join(model_names)}")
    print(f"  Ollama URL:   {args.ollama_url}")
    print()

    results: list[dict] = []
    for model_name in model_names:
        logger.info("Evaluating model: %s ...", model_name)
        try:
            result = await evaluator.evaluate_model(model_name, args.ollama_url)
            results.append(result)
            print(f"\n--- {model_name} ---")
            print(f"  JSON validity:     {result['json_validity']:.1%}")
            print(f"  Schema compliance: {result['schema_compliance']:.1%}")
            print(f"  Avg latency:       {result['avg_latency_ms']:.1f} ms")
        except Exception as exc:
            logger.error("Failed to evaluate '%s': %s", model_name, exc)

    if len(results) >= 2:
        print("\n=== Comparison Table ===\n")
        table = evaluator.compare(results)
        print(table)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {output_path}")


def main() -> None:
    args = parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
