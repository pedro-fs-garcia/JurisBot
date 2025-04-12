import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Caminho do modelo LoRA fine-tunado
MODEL_BASE = "HuggingFaceH4/zephyr-7b-beta"
MODEL_LORA = "zephyr-juridico-lora"

# Carrega tokenizer e modelo base
tokenizer = AutoTokenizer.from_pretrained(MODEL_LORA, trust_remote_code=True)
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_BASE,
    load_in_4bit=True,
    device_map="auto",
    trust_remote_code=True
)

# Aplica LoRA no modelo
model = PeftModel.from_pretrained(base_model, MODEL_LORA)
model.eval()

# Função de resposta
def responder(pergunta):
    prompt = f"<|user|> {pergunta}\n<|assistant|>"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=300, do_sample=True, temperature=0.7)
    resposta = tokenizer.decode(output[0], skip_special_tokens=True)
    print("\nResposta:")
    print(resposta.split("<|assistant|>")[-1].strip())

# Exemplo de uso
pergunta = input("Digite sua pergunta jurídica: ")
responder(pergunta)
