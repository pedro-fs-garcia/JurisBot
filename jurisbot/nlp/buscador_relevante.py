from sentence_transformers import SentenceTransformer, util

modelo = SentenceTransformer('all-MiniLM-L6-v2')

def buscar_mais_relevantes(julgados, consulta, top_k=3):
    textos = [j["ementa"] or "" for j in julgados]
    emb_julgados = modelo.encode(textos, convert_to_tensor=True)
    emb_consulta = modelo.encode(consulta, convert_to_tensor=True)
    
    scores = util.pytorch_cos_sim(emb_consulta, emb_julgados)[0]
    top_resultados = scores.topk(top_k)

    resultados = []
    for score, idx in zip(top_resultados.values, top_resultados.indices):
        resultado = julgados[int(idx)]
        resultado["score"] = float(score)
        resultados.append(resultado)
    
    return resultados
