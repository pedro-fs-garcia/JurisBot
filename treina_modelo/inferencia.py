# inferencia.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# Função para carregar modelo

def carregar_modelo(caminho="./modelo_juridico"):
    tokenizer = AutoTokenizer.from_pretrained(caminho)
    model = AutoModelForCausalLM.from_pretrained(
        caminho, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    model.eval()
    return tokenizer, model

# Função de geração

def gerar_resposta(prompt, tokenizer, model, max_tokens=300):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=True, temperature=0.7)
    resposta = tokenizer.decode(output[0], skip_special_tokens=True)
    return resposta

# Função de avaliação simples (modo batch)

def testar_modelo(tokenizer, model, num_exemplos=5):
    ds_teste = load_dataset("loremipsum3658/jur-entailment", split="test").select(range(num_exemplos))

    for exemplo in ds_teste:
        if "ementa1" in exemplo and "ementa2" in exemplo:
            prompt = f"Compare os textos jurídicos:\n1. {exemplo['ementa1']}\n2. {exemplo['ementa2']}"
        else:
            continue
        resposta = gerar_resposta(prompt, tokenizer, model)
        print("\n### Pergunta ###\n", prompt)
        print("\n### Resposta do modelo ###\n", resposta)

if __name__ == "__main__":
    tokenizer, model = carregar_modelo()
    escolha = input("Digite 1 para pergunta manual ou 2 para teste automático com dataset: ")

    if escolha == "1":
        pergunta = input("Digite sua pergunta jurídica: ")
        resposta = gerar_resposta(pergunta, tokenizer, model)
        print("\nResposta do modelo:\n")
        print(resposta)
    elif escolha == "2":
        testar_modelo(tokenizer, model)
    else:
        print("Escolha inválida.")
