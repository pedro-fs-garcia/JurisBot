from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import requests
# from scraping.tre_sp_scraper import buscar_julgados
# from nlp.buscador_relevante import buscar_mais_relevantes
# from nlp.sumarizador import resumir_texto
# from scraping.tre_sp_scraper import buscar_julgados

# Carrega variáveis do .env
load_dotenv()
API_TOKEN = os.getenv("HF_API_TOKEN")
MODEL_ID = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")

API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

app = Flask(__name__)

def query_model(prompt):
    system_prompt = f"### Human:\n{prompt}\n\n### Assistant:\n"
    payload = {
        "inputs": system_prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    print("[Enviando requisição à Hugging Face API...]")
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        generated = response.json()[0]["generated_text"]
        return generated.strip()
    else:
        return f"Erro {response.status_code}: {response.text}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Mensagem não fornecida'}), 400
    
    response = query_model(data['message'])
    return jsonify({'response': response})

# def main():
#     consulta = input("🔎 Digite um termo para buscar julgados: ")
#     print("\n🔎 Buscando julgados no TRE-SP...")

#     julgados = buscar_julgados(consulta, max_resultados=5)

#     if not julgados:
#         print("Nenhum julgado encontrado.")
#         return
    
#     for i, j in enumerate(julgados, 1):
#         print(f"\n🔹 Julgado {i}")
#         print(f"Título: {j['titulo']}")
#         print(f"Conteúdo: {j['conteudo']}")

#     print("📊 Ranqueando julgados mais relevantes...")
#     relevantes = buscar_mais_relevantes(julgados, consulta)

#     print("\n🧠 Resumos dos julgados mais relevantes:\n")
#     for idx, j in enumerate(relevantes, 1):
#         resumo = resumir_texto(j["ementa"] or j["inteiroTeor"])
#         print(f"{idx}. Processo: {j['numeroProcesso']} | Órgão: {j['orgaoJulgador']}")
#         print(f"Resumo: {resumo}\n")

if __name__ == "__main__":
    app.run(debug=True)
