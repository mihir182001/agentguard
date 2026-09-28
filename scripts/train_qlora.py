from pathlib import Path
import os

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import (
    LoraConfig,
    prepare_model_for_kbit_training,
)
from trl import SFTTrainer


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRAIN_FILE = PROJECT_ROOT / "data/fine_tuning/train.jsonl"
VALIDATION_FILE = (
    PROJECT_ROOT / "data/fine_tuning/validation.jsonl"
)

OUTPUT_DIR = (
    PROJECT_ROOT / "models/agentguard-qlora"
)


MODEL_NAME = os.getenv(
    "BASE_MODEL",
    "Qwen/Qwen2.5-3B-Instruct"
)


def check_gpu():
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA GPU is required for QLoRA training. "
            "Run this script on a cloud GPU."
        )

    print(
        f"GPU: {torch.cuda.get_device_name(0)}"
    )

    print(
        f"VRAM: "
        f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB"
    )


def load_training_data():
    dataset = load_dataset(
        "json",
        data_files={
            "train": str(TRAIN_FILE),
            "validation": str(VALIDATION_FILE),
        }
    )

    return dataset


def format_example(example):
    messages = example["messages"]

    text = ""

    for message in messages:
        role = message["role"]
        content = message["content"]

        text += (
            f"<|im_start|>{role}\n"
            f"{content}"
            f"<|im_end|>\n"
        )

    return {
        "text": text
    }


def load_model_and_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
    )

    model = prepare_model_for_kbit_training(
        model
    )

    return model, tokenizer


def create_lora_config():
    return LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )


def main():
    print("Starting AgentGuard QLoRA training")

    check_gpu()

    print(
        f"Base model: {MODEL_NAME}"
    )

    dataset = load_training_data()

    print(
        f"Training examples: "
        f"{len(dataset['train'])}"
    )

    print(
        f"Validation examples: "
        f"{len(dataset['validation'])}"
    )

    dataset = dataset.map(
        format_example
    )

    model, tokenizer = (
        load_model_and_tokenizer()
    )

    lora_config = create_lora_config()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),

        num_train_epochs=3,

        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,

        gradient_accumulation_steps=8,

        learning_rate=2e-4,

        logging_steps=10,

        eval_strategy="steps",
        eval_steps=100,

        save_strategy="steps",
        save_steps=100,

        save_total_limit=2,

        bf16=True,

        gradient_checkpointing=True,

        optim="paged_adamw_8bit",

        warmup_ratio=0.05,

        lr_scheduler_type="cosine",

        report_to="none",

        remove_unused_columns=False,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,

        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],

        dataset_text_field="text",
        max_seq_length=2048,

        peft_config=lora_config,

        args=training_args,
    )

    print("Training started")

    trainer.train()

    print("Training completed")

    trainer.save_model(
        str(OUTPUT_DIR)
    )

    tokenizer.save_pretrained(
        str(OUTPUT_DIR)
    )

    print(
        f"Model saved to: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()