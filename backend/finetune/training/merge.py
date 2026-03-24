"""Merge LoRA adapters into base model and save as full HuggingFace model."""

import logging
from pathlib import Path

from unsloth import FastLanguageModel

logger = logging.getLogger(__name__)


def merge_lora(
    lora_dir: Path,
    output_dir: Path,
    max_seq_length: int = 4096,
):
    """Load LoRA checkpoint, merge into base model, save full merged model.

    Args:
        lora_dir: Path to the saved LoRA adapter directory.
        output_dir: Path where the merged full model will be written.
        max_seq_length: Maximum sequence length (must match training).
    """
    lora_dir = Path(lora_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading LoRA checkpoint from %s", lora_dir)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(lora_dir),
        max_seq_length=max_seq_length,
        load_in_4bit=False,
    )

    logger.info("Merging LoRA adapters into base model...")
    merged_model = model.merge_and_unload()

    logger.info("Saving merged model to %s", output_dir)
    merged_model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    logger.info("Merge complete: %s", output_dir)
    return output_dir
