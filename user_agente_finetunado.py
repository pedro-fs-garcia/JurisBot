import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel, PeftConfig
import os

def carregar_modelo(base_model_name="HuggingFaceH4/zephyr-7b-beta", 
                   peft_model_path="zephyr-juridico-lora"):
    """
    Carrega o modelo base e aplica os pesos do fine-tuning
    """
    # Cria diretório para offload se não existir
    offload_dir = "model_offload"
    os.makedirs(offload_dir, exist_ok=True)
    
    print("Carregando configuração...")
    config = PeftConfig.from_pretrained(peft_model_path)
    
    print("Carregando tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Configuração de quantização para economizar memória
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    print("Carregando modelo base...")
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
        quantization_config=quantization_config,
        offload_folder=offload_dir
    )
    
    print("Aplicando pesos do fine-tuning...")
    model = PeftModel.from_pretrained(
        model, 
        peft_model_path,
        offload_folder=offload_dir,
        device_map="auto"
    )
    
    # Otimizações para inferência
    model.eval()
    if torch.cuda.is_available():
        model = model.to("cuda")
    
    return model, tokenizer

def gerar_resposta(prompt, model, tokenizer, max_length=512, temperature=0.7):
    """
    Gera uma resposta para o prompt dado
    """
    # Formata o prompt no estilo Zephyr
    formatted_prompt = f"<|user|> {prompt}\n<|assistant|>"
    
    # Tokeniza o input
    inputs = tokenizer(formatted_prompt, return_tensors="pt", truncation=True, max_length=max_length)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # Gera a resposta
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=temperature,
            do_sample=True,
            top_p=0.95,
            top_k=50,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1
        )
    
    # Decodifica a resposta
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Remove o prompt original da resposta
    response = response.replace(formatted_prompt, "").strip()
    return response

def main():
    print("Iniciando carregamento do modelo...")
    try:
        model, tokenizer = carregar_modelo()
        
        print("\nModelo carregado! Você pode começar a fazer perguntas.")
        print("Digite 'sair' para encerrar.")
        
        while True:
            prompt = input("\nSua pergunta: ")
            if prompt.lower() == 'sair':
                break
                
            try:
                print("\nGerando resposta...")
                resposta = gerar_resposta(prompt, model, tokenizer)
                print("\nResposta:", resposta)
            except Exception as e:
                print(f"Erro ao gerar resposta: {e}")
    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")
        print("Certifique-se de que o modelo fine-tuned existe no diretório correto.")

if __name__ == "__main__":
    main() 