import torch
from datasets import load_dataset, concatenate_datasets
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model

# Dataset
print("Carregando datasets...")
ds1 = load_dataset("loremipsum3658/jur-entailment", split="train")
ds2 = load_dataset("felipeoes/br_federal_legislation_blue_amazon_chat_qa_filtered_gpt-4o", split="train")
ds3 = load_dataset("recogna-nlp/recognasumm", split="train")

# Preprocessamento simples
def preprocess(example):
    if "ementa1" in example and "ementa2" in example:
        prompt = f"Compare os textos jurídicos:\n1. {example['ementa1']}\n2. {example['ementa2']}"
        answer = f"Similaridade: {example['similarity']}"
    elif "prompt" in example and "generated_content" in example:
        prompt = example["prompt"]
        answer = example["generated_content"]
    elif "Noticia" in example and "Sumario" in example:
        prompt = f"Texto jurídico: {example['Noticia']}"
        answer = f"Resumo: {example['Sumario']}"
    else:
        return None
    return {"text": f"{prompt}\n\n{answer}"}

ds1 = ds1.map(preprocess).filter(lambda x: x is not None)
ds2 = ds2.map(preprocess).filter(lambda x: x is not None)
ds3 = ds3.map(preprocess).filter(lambda x: x is not None)

dataset = concatenate_datasets([ds1, ds2, ds3])

# Tokenização
print("Tokenizando...")
model_id = "HuggingFaceH4/zephyr-7b-beta"
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

def tokenize(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=1024)

tokenized_dataset = dataset.map(tokenize, batched=True)
tokenized_dataset.set_format(type="torch", columns=["input_ids", "attention_mask"])

# Carrega o modelo sem quantização
print("Carregando modelo base...")
model = AutoModelForCausalLM.from_pretrained(model_id)

# Configura LoRA (sem prepare_model_for_kbit_training)
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Treinamento
args = TrainingArguments(
    output_dir="./modelo_juridico",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    logging_steps=10,
    save_total_limit=2,
    learning_rate=2e-4,
    fp16=False,  # Coloque False se não tiver GPU com suporte a float16
    save_strategy="epoch",
    #evaluation_strategy="no",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

print("Iniciando treinamento...")
trainer.train()

model.save_pretrained("./modelo_juridico")
tokenizer.save_pretrained("./modelo_juridico")
