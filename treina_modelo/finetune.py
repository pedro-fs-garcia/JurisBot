import os
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import BitsAndBytesConfig

# 1. Configurações iniciais
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"
DATA_PATH = "dados_juridicos.json"  # JSON com estrutura de "conversations"
OUTPUT_DIR = "zephyr-juridico-lora"

# 2. BitsAndBytes para reduzir uso de memória
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# 3. Carrega modelo e tokenizer
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# 4. Prepara modelo para LoRA
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)

# 5. Carrega dados
raw_dataset = load_dataset("json", data_files=DATA_PATH)

# 6. Prepara os dados
def format_chat(example):
    conversation = example["conversations"]
    prompt = ""
    for turn in conversation:
        role = turn["from"]
        content = turn["value"]
        if role == "human":
            prompt += f"<|user|> {content}\n"
        else:
            prompt += f"<|assistant|> {content}\n"
    return {"text": prompt}

formatted_dataset = raw_dataset["train"].map(format_chat)

# 7. Tokeniza os dados
def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        max_length=1024,
        padding="max_length"
    )

tokenized_dataset = formatted_dataset.map(tokenize)

# 8. Configura o treinamento
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    num_train_epochs=3,
    logging_steps=10,
    save_strategy="epoch",
    fp16=True,
    remove_unused_columns=False,
    report_to="none"
)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator
)

# 9. Treina o modelo
trainer.train()

# 10. Salva o modelo fine-tunado
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("Treinamento concluído e modelo salvo em:", OUTPUT_DIR)