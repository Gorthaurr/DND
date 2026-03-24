"""Run QLoRA fine-tuning with Unsloth.

Usage:
    python -m finetune.scripts.04_train [--epochs 3] [--batch-size 2] [--lr 2e-4]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from finetune.config import (
    BASE_MODEL,
    BATCH_SIZE,
    EPOCHS,
    GRAD_ACCUM,
    LEARNING_RATE,
    LORA_ALPHA,
    LORA_DROPOUT,
    LORA_RANK,
    MAX_SEQ_LENGTH,
    MODELS_DIR,
    PROCESSED_DIR,
    TARGET_MODULES,
    WARMUP_RATIO,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run QLoRA fine-tuning with Unsloth.")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help=f"Training epochs (default: {EPOCHS}).")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help=f"Batch size (default: {BATCH_SIZE}).")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help=f"Learning rate (default: {LEARNING_RATE}).")
    parser.add_argument("--grad-accum", type=int, default=GRAD_ACCUM, help=f"Gradient accumulation steps (default: {GRAD_ACCUM}).")
    parser.add_argument("--max-seq-length", type=int, default=MAX_SEQ_LENGTH, help=f"Max sequence length (default: {MAX_SEQ_LENGTH}).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    train_path = PROCESSED_DIR / "train.jsonl"
    val_path = PROCESSED_DIR / "val.jsonl"
    output_dir = MODELS_DIR / "lora"

    if not train_path.exists():
        logger.error("Training data not found: %s. Run 03_prepare_training first.", train_path)
        sys.exit(1)

    # Count samples
    with open(train_path, "r", encoding="utf-8") as f:
        train_count = sum(1 for line in f if line.strip())
    val_count = 0
    if val_path.exists():
        with open(val_path, "r", encoding="utf-8") as f:
            val_count = sum(1 for line in f if line.strip())

    print(f"\n=== QLoRA Fine-Tuning ===")
    print(f"  Base model:     {BASE_MODEL}")
    print(f"  LoRA rank:      {LORA_RANK}, alpha: {LORA_ALPHA}, dropout: {LORA_DROPOUT}")
    print(f"  Train samples:  {train_count}")
    print(f"  Val samples:    {val_count}")
    print(f"  Epochs:         {args.epochs}")
    print(f"  Batch size:     {args.batch_size}")
    print(f"  Grad accum:     {args.grad_accum}")
    print(f"  Learning rate:  {args.lr}")
    print(f"  Max seq length: {args.max_seq_length}")
    print(f"  Output dir:     {output_dir}")
    print()

    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import load_dataset
    except ImportError as exc:
        logger.error(
            "Missing dependency: %s. Install with: pip install unsloth trl transformers datasets",
            exc,
        )
        sys.exit(1)

    # Load model with Unsloth
    logger.info("Loading base model: %s", BASE_MODEL)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=args.max_seq_length,
        load_in_4bit=True,
    )

    # Apply LoRA adapters
    logger.info("Applying LoRA adapters (rank=%d, alpha=%d)...", LORA_RANK, LORA_ALPHA)
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES,
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    # Load dataset
    logger.info("Loading training data from %s ...", train_path)
    dataset = load_dataset("json", data_files={"train": str(train_path), "val": str(val_path)})

    def formatting_func(examples):
        """Format ChatML messages into tokenizer chat template."""
        texts = []
        for messages in examples["messages"]:
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            texts.append(text)
        return {"text": texts}

    dataset = dataset.map(formatting_func, batched=True, remove_columns=dataset["train"].column_names)

    # Training arguments
    output_dir.mkdir(parents=True, exist_ok=True)
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        warmup_ratio=WARMUP_RATIO,
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="epoch" if val_path.exists() else "no",
        fp16=True,
        optim="adamw_8bit",
        report_to="none",
        seed=42,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset.get("val"),
        args=training_args,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
    )

    logger.info("Starting training...")
    train_result = trainer.train()

    # Save
    logger.info("Saving LoRA adapter to %s ...", output_dir)
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    print(f"\n=== Training Complete ===")
    print(f"  Train loss:     {train_result.training_loss:.4f}")
    print(f"  Train runtime:  {train_result.metrics.get('train_runtime', 0):.1f}s")
    print(f"  Saved to:       {output_dir}")


if __name__ == "__main__":
    main()
