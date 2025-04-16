import os
import torch
from datasets import load_dataset, concatenate_datasets
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model

# 1. Configurações iniciais
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"
DATA_PATH = "treina_modelo/dados_juridicos.json"  # Caminho correto para o arquivo
OUTPUT_DIR = "zephyr-juridico-lora"

# Verificação e configuração da GPU
import torch.cuda
if not torch.cuda.is_available():
    raise RuntimeError("CUDA não está disponível. Verifique se os drivers NVIDIA estão instalados corretamente.")

device = torch.device("cuda")
print(f"Usando GPU: {torch.cuda.get_device_name(0)}")
print(f"Memória GPU Total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

# 2. Carrega modelo e tokenizer
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float16,
    device_map={"": 0},
    use_cache=False
)

# Configura o modelo para treinamento
model.config.use_cache = False
model.gradient_checkpointing_enable()
model.enable_input_require_grads()

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"  # Importante para o treinamento

# 3. Aplica LoRA
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    inference_mode=False  # Importante para treinamento
)

# Aplica LoRA e move para GPU
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# 4. Carrega datasets
raw_dataset = load_dataset("json", data_files=DATA_PATH)

# ds1 = load_dataset("loremipsum3658/jur-entailment", split="train")
# ds2 = load_dataset("felipeoes/br_federal_legislation_blue_amazon_chat_qa_filtered_gpt-4o", split="train")
# ds3 = load_dataset("recogna-nlp/recognasumm", split="train")

# 5. Prepara e formata os datasets

# Dados no estilo Zephyr Chat (json local)
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

formatted_raw = raw_dataset["train"].map(format_chat)

# Outros datasets no estilo Q&A simples
def format_qa(example):
    if "question" in example and "answer" in example:
        return {
            "text": f"<|user|> {example['question']}\n<|assistant|> {example['answer']}\n"
        }
    else:
        return {"text": ""}

# formatted_ds1 = ds1.map(format_qa)
# formatted_ds2 = ds2.map(format_qa)
# formatted_ds3 = ds3.map(format_qa)

# Combina tudo em um único dataset
# combined_dataset = concatenate_datasets([formatted_raw, formatted_ds1, formatted_ds2, formatted_ds3])
combined_dataset = concatenate_datasets([formatted_raw])

# 6. Tokeniza os dados
def tokenize(example):
    # Adiciona tokens especiais e padding
    result = tokenizer(
        example["text"],
        truncation=True,
        max_length=1024,
        padding="max_length",
        return_tensors=None  # Importante para o treinamento
    )
    result["labels"] = result["input_ids"].copy()
    return result

tokenized_dataset = combined_dataset.map(tokenize, batched=True, remove_columns=combined_dataset.column_names)

# 7. Configura o treinamento
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    num_train_epochs=3,
    logging_steps=10,
    save_strategy="epoch",
    fp16=True,
    bf16=False,
    half_precision_backend="auto",
    remove_unused_columns=False,
    report_to="none",
    gradient_checkpointing=True,
    optim="adamw_torch",
    max_grad_norm=0.3,
    warmup_ratio=0.03,  # Adiciona warmup
    lr_scheduler_type="cosine",  # Usa scheduler cosine
)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

trainer = Trainer(
    model=model,  # O modelo já está na GPU
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator
)

# 8. Treina o modelo
trainer.train()

# 9. Salva modelo e tokenizer
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("✅ Fine-tuning concluído e modelo salvo em:", OUTPUT_DIR)
