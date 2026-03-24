"""Merge LoRA, export GGUF, register in Ollama.

Usage:
    python -m finetune.scripts.06_deploy [--model-name qwen2.5:14b-dnd]
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

from finetune.config import (
    BASE_MODEL,
    GGUF_QUANTIZATION,
    MAX_SEQ_LENGTH,
    MODELS_DIR,
    OLLAMA_MODEL_NAME,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge LoRA, export GGUF, register in Ollama.")
    parser.add_argument(
        "--model-name",
        type=str,
        default=OLLAMA_MODEL_NAME,
        help=f"Ollama model name (default: {OLLAMA_MODEL_NAME}).",
    )
    parser.add_argument(
        "--lora-dir",
        type=str,
        default=None,
        help="Path to LoRA adapter dir (default: data/models/lora/).",
    )
    parser.add_argument(
        "--quantization",
        type=str,
        default=GGUF_QUANTIZATION,
        help=f"GGUF quantization type (default: {GGUF_QUANTIZATION}).",
    )
    parser.add_argument(
        "--skip-merge",
        action="store_true",
        help="Skip merge step (use pre-merged model).",
    )
    return parser.parse_args()


def merge_lora(lora_dir: Path, merged_dir: Path) -> None:
    """Merge LoRA adapter into base model using Unsloth."""
    logger.info("Merging LoRA from %s ...", lora_dir)

    try:
        from unsloth import FastLanguageModel
    except ImportError:
        logger.error("Unsloth not installed. Install with: pip install unsloth")
        sys.exit(1)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(lora_dir),
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,
    )

    merged_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Saving merged model to %s ...", merged_dir)
    model.save_pretrained_merged(str(merged_dir), tokenizer, save_method="merged_16bit")
    logger.info("Merge complete.")


def export_gguf(merged_dir: Path, output_path: Path, quantization: str) -> None:
    """Export merged model to GGUF format using llama.cpp convert script."""
    logger.info("Exporting GGUF (%s) to %s ...", quantization, output_path)

    try:
        from unsloth import FastLanguageModel
    except ImportError:
        logger.error("Unsloth not installed. Install with: pip install unsloth")
        sys.exit(1)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(merged_dir),
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=False,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Saving GGUF to %s ...", output_path)
    model.save_pretrained_gguf(
        str(output_path.parent / output_path.stem),
        tokenizer,
        quantization_method=quantization,
    )
    logger.info("GGUF export complete.")


def register_ollama(model_name: str, gguf_path: Path) -> None:
    """Register GGUF model in Ollama via Modelfile."""
    logger.info("Registering model '%s' in Ollama ...", model_name)

    modelfile_content = f"""FROM {gguf_path}

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx {MAX_SEQ_LENGTH}

SYSTEM "You are a D&D Living World game engine. Respond ONLY in valid JSON."
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".Modelfile", delete=False, encoding="utf-8") as f:
        f.write(modelfile_content)
        modelfile_path = f.name

    try:
        result = subprocess.run(
            ["ollama", "create", model_name, "-f", modelfile_path],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            logger.error("Ollama create failed: %s", result.stderr)
            sys.exit(1)
        logger.info("Model '%s' registered successfully.", model_name)
    except FileNotFoundError:
        logger.error("'ollama' command not found. Install Ollama first: https://ollama.com")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        logger.error("Ollama create timed out after 600s.")
        sys.exit(1)
    finally:
        Path(modelfile_path).unlink(missing_ok=True)


def update_config(model_name: str) -> None:
    """Update OLLAMA_MODEL_NAME in config.py."""
    config_path = Path(__file__).resolve().parent.parent / "config.py"
    if not config_path.exists():
        logger.warning("config.py not found at %s, skipping update.", config_path)
        return

    content = config_path.read_text(encoding="utf-8")
    old_line = f'OLLAMA_MODEL_NAME = "{OLLAMA_MODEL_NAME}"'
    new_line = f'OLLAMA_MODEL_NAME = "{model_name}"'

    if old_line in content:
        content = content.replace(old_line, new_line)
        config_path.write_text(content, encoding="utf-8")
        logger.info("Updated config.py: OLLAMA_MODEL_NAME = '%s'", model_name)
    else:
        logger.info("Config already up to date or line not found.")


def main() -> None:
    args = parse_args()

    lora_dir = Path(args.lora_dir) if args.lora_dir else MODELS_DIR / "lora"
    merged_dir = MODELS_DIR / "merged"
    gguf_filename = f"{args.model_name.replace(':', '-').replace('/', '-')}-{args.quantization}.gguf"
    gguf_path = MODELS_DIR / gguf_filename

    print(f"\n=== Deployment Pipeline ===")
    print(f"  LoRA dir:       {lora_dir}")
    print(f"  Merged dir:     {merged_dir}")
    print(f"  GGUF output:    {gguf_path}")
    print(f"  Model name:     {args.model_name}")
    print(f"  Quantization:   {args.quantization}")
    print()

    if not lora_dir.exists():
        logger.error("LoRA directory not found: %s. Run 04_train first.", lora_dir)
        sys.exit(1)

    # Step 1: Merge LoRA
    if not args.skip_merge:
        merge_lora(lora_dir, merged_dir)
    else:
        logger.info("Skipping merge step (--skip-merge).")

    # Step 2: Export GGUF
    export_gguf(merged_dir, gguf_path, args.quantization)

    # Step 3: Register in Ollama
    register_ollama(args.model_name, gguf_path)

    # Step 4: Update config
    update_config(args.model_name)

    print(f"\n=== Deployment Complete ===")
    print(f"  Model '{args.model_name}' is now available in Ollama.")
    print(f"  Test with: ollama run {args.model_name}")


if __name__ == "__main__":
    main()
