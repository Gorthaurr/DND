"""Unsloth QLoRA fine-tuning script for Qwen 2.5 14B."""

import json
import logging
from pathlib import Path

from datasets import Dataset
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastLanguageModel

logger = logging.getLogger(__name__)


def _load_jsonl(path: Path) -> list[dict]:
    """Load JSONL file into list of dicts."""
    samples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    return samples


def _apply_chat_template(sample: dict, tokenizer) -> dict:
    """Apply Qwen2.5 chat template to a messages sample."""
    text = tokenizer.apply_chat_template(
        sample["messages"],
        tokenize=False,
        add_generation_prompt=False,
    )
    return {"text": text}


def train(
    data_dir: Path,
    output_dir: Path,
    base_model: str = "unsloth/Qwen2.5-14B-bnb-4bit",
    epochs: int = 3,
    batch_size: int = 2,
    grad_accum: int = 8,
    lr: float = 2e-4,
    lora_rank: int = 32,
    lora_alpha: int = 64,
    max_seq_length: int = 4096,
):
    """Fine-tune Qwen 2.5 14B with QLoRA via Unsloth.

    Steps:
        1. Load base model in 4-bit quantization
        2. Add LoRA adapters to attention + MLP projections
        3. Load and template training data
        4. Configure SFTTrainer with cosine scheduler
        5. Train
        6. Save LoRA checkpoint
    """
    output_dir = Path(output_dir)
    lora_dir = output_dir / "lora"
    lora_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load base model
    logger.info("Loading base model: %s", base_model)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=base_model,
        max_seq_length=max_seq_length,
        load_in_4bit=True,
    )

    # 2. Add LoRA adapters
    logger.info("Adding LoRA adapters (rank=%d, alpha=%d)", lora_rank, lora_alpha)
    model = FastLanguageModel.get_peft_model(
        model,
        r=lora_rank,
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    # 3. Load training data
    train_path = Path(data_dir) / "train.jsonl"
    logger.info("Loading training data from %s", train_path)
    raw_samples = _load_jsonl(train_path)
    dataset = Dataset.from_list(raw_samples)
    dataset = dataset.map(
        lambda sample: _apply_chat_template(sample, tokenizer),
        remove_columns=dataset.column_names,
    )
    logger.info("Training samples: %d", len(dataset))

    # 4. Configure trainer
    training_args = TrainingArguments(
        output_dir=str(output_dir / "checkpoints"),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        learning_rate=lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        weight_decay=0.01,
        bf16=True,
        logging_steps=10,
        save_strategy="epoch",
        optim="adamw_8bit",
        seed=42,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=training_args,
        max_seq_length=max_seq_length,
    )

    # 5. Train
    logger.info("Starting training for %d epochs", epochs)
    trainer.train()

    # 6. Save LoRA checkpoint
    logger.info("Saving LoRA checkpoint to %s", lora_dir)
    model.save_pretrained(str(lora_dir))
    tokenizer.save_pretrained(str(lora_dir))

    logger.info("Training complete.")
    return lora_dir
