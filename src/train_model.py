"""
Fine-tune Flan-T5 for cyber report generation.
M3 — Model fine-tuning.
"""

import argparse
from pathlib import Path

# Use HF token from huggingface-api.json for model downloads/push
from src.hf_auth import login as hf_login

hf_login()

import pandas as pd
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)


def load_csv_data(train_path: str, val_path: str):
    """Load train/val CSV with input_text, target_report columns."""
    train_df = pd.read_csv(train_path, encoding="utf-8")
    val_df = pd.read_csv(val_path, encoding="utf-8")
    return Dataset.from_pandas(train_df), Dataset.from_pandas(val_df)


def preprocess_function(examples, tokenizer, max_input_length: int, max_target_length: int):
    """Tokenize inputs and targets for seq2seq."""
    model_inputs = tokenizer(
        examples["input_text"],
        max_length=max_input_length,
        truncation=True,
        padding=False,
    )
    labels = tokenizer(
        examples["target_report"],
        max_length=max_target_length,
        truncation=True,
        padding=False,
    )
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def main():
    parser = argparse.ArgumentParser(description="Fine-tune Flan-T5 for cyber report generation")
    parser.add_argument("--model_name", default="google/flan-t5-base")
    parser.add_argument("--train", default="data/train.csv")
    parser.add_argument("--val", default="data/val.csv")
    parser.add_argument("--output_dir", default="models/flan_t5_report")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=3e-5)
    parser.add_argument("--max_input_length", type=int, default=512)
    parser.add_argument("--max_target_length", type=int, default=128)
    args = parser.parse_args()

    print("Loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)

    print("Loading datasets...")
    train_ds, val_ds = load_csv_data(args.train, args.val)

    def tokenize_fn(examples):
        return preprocess_function(
            examples, tokenizer, args.max_input_length, args.max_target_length
        )

    train_ds = train_ds.map(tokenize_fn, batched=True, remove_columns=train_ds.column_names)
    val_ds = val_ds.map(tokenize_fn, batched=True, remove_columns=val_ds.column_names)

    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer, model=model, padding=True, return_tensors="pt"
    )

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        warmup_ratio=0.1,
        logging_steps=20,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        report_to="none",
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    print("Starting training...")
    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"Model saved to {args.output_dir}")


if __name__ == "__main__":
    main()
