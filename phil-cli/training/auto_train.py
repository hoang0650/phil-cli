from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

def train_self():
    print(">>> BẮT ĐẦU TỰ NÂNG CẤP (SELF-EVOLUTION) <<<")
    # Load model gốc
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = "casperhansen/llama-3-70b-instruct-awq",
        max_seq_length = 2048,
        dtype = None,
        load_in_4bit = True,
    )
    
    # Tạo LoRA adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r = 16,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha = 16,
        lora_dropout = 0, 
        bias = "none", 
        use_gradient_checkpointing = True, 
        random_state = 3407,
    )

    # Load dữ liệu (Cần cơ chế log lại các task thành công vào file jsonl này)
    dataset = load_dataset("json", data_files="training/successful_memories.jsonl", split="train")

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = 2048,
        args = TrainingArguments(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            warmup_steps = 5,
            max_steps = 60,
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            output_dir = "models/evolved_adapter",
            optim = "adamw_8bit",
        ),
    )
    trainer.train()
    model.save_pretrained("models/evolved_adapter")
    print(">>> NÂNG CẤP HOÀN TẤT. VUI LÒNG RELOAD MODEL. <<<")

if __name__ == "__main__":
    train_self()