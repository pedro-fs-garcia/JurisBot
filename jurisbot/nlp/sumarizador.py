from transformers import pipeline

# Carrega modelo de sumarização (pode demorar a primeira vez)
sumarizador = pipeline("summarization", model="t5-small")

def resumir_texto(texto, max_length=130, min_length=30):
    if not texto.strip():
        return ""
    try:
        resultado = sumarizador(texto, max_length=max_length, min_length=min_length, do_sample=False)
        return resultado[0]['summary_text']
    except Exception as e:
        print("Erro ao resumir:", e)
        return texto[:max_length]
