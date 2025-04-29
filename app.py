from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool
import datetime
import requests
import pytz
import yaml
from tools.buscador_dod import BuscadorDOD
from tools.final_answer import FinalAnswerTool
from huggingface_hub.utils import HfHubHTTPError
import dotenv
import os
import json
from typing import List, Dict, Optional
import markdown

from Gradio_UI import GradioUI
from tools.visit_webpage import VisitWebpageTool

dotenv.load_dotenv()


@tool
def buscar_jurisprudencia(termos: str) -> str:
    """Ferramenta para buscar jurisprudências em tribunais brasileiros.
    
    Args:
        termos: Termos de busca para a jurisprudência
    """
    try:
        # Aqui você pode implementar a lógica de busca real usando APIs dos tribunais
        # Por enquanto, retornaremos um exemplo simulado
        dod = BuscadorDOD()
        resultados = dod.forward(termos)
        return json.dumps(resultados, ensure_ascii=False, indent=4)
    
    except Exception as e:
        return f"Erro ao buscar jurisprudência: {str(e)}"

@tool
def formatar_resposta_juridica(
    titulo: str,
    conteudo: str,
    jurisprudencias: Optional[List[Dict]] = None,
    legislacao: Optional[List[str]] = None,
    referencias: Optional[List[str]] = None
) -> str:
    """Ferramenta para formatar respostas jurídicas de forma estruturada e legível.
    
    Args:
        titulo: Título da resposta
        conteudo: Conteúdo principal da resposta
        jurisprudencias: Lista de jurisprudências relevantes
        legislacao: Lista de dispositivos legais citados
        referencias: Lista de referências adicionais
    """
    try:
        # Estrutura base da resposta em markdown
        resposta = f"# {titulo}\n\n"
        
        # Conteúdo principal
        resposta += f"## Análise\n{conteudo}\n\n"
        
        # Seção de jurisprudências
        if jurisprudencias:
            resposta += "## Jurisprudências Relevantes\n"
            for jur in jurisprudencias:
                resposta += f"### {jur.get('tribunal', '')} - {jur.get('processo', '')}\n"
                resposta += f"**Relator:** {jur.get('relator', '')}\n"
                resposta += f"**Data:** {jur.get('data', '')}\n"
                resposta += f"**Ementa:** {jur.get('ementa', '')}\n"
                resposta += f"**Decisão:** {jur.get('decisao', '')}\n\n"
        
        # Seção de legislação
        if legislacao:
            resposta += "## Legislação Citada\n"
            for leg in legislacao:
                resposta += f"- {leg}\n"
            resposta += "\n"
        
        # Seção de referências
        if referencias:
            resposta += "## Referências\n"
            for ref in referencias:
                resposta += f"- {ref}\n"
        
        return resposta
    except Exception as e:
        return f"Erro ao formatar resposta: {str(e)}"

final_answer = FinalAnswerTool()
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

# Lista de modelos para fallback
MODELS_TO_TRY = [
    "mistralai/Mistral-7B-Instruct-v0.2",
    "Qwen/Qwen2.5-Coder-3B-Instruct",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud",
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
]

# Função para criar modelo com fallback
def create_model_with_fallback():
    last_exception = None
    for model_name in MODELS_TO_TRY:
        try:
            print(f"Tentando carregar modelo: {model_name}...")
            model = HfApiModel(
                model_id=model_name,
                max_tokens=2096,
                temperature=0.5,
                custom_role_conversions=None,
                token=os.getenv("HF_API_TOKEN")
            )
            # Teste opcional: fazer uma chamada pequena pra garantir
            model(
                messages=[{"role": "user", "content": "Olá"}],
                max_tokens=5
            )
            print(f"✅ Modelo {model_name} carregado com sucesso!")
            return model
        except HfHubHTTPError as e:
            print(f"⚠️ Falha no modelo {model_name}: {e}")
            last_exception = e
        except Exception as e:
            print(f"⚠️ Erro inesperado com {model_name}: {e}")
            last_exception = e
    raise RuntimeError("Nenhum modelo disponível!") from last_exception

# Carrega modelo usando fallback
model = create_model_with_fallback()

# Carrega prompts
with open("prompts.yaml", 'r', encoding='utf-8') as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=model,
    tools=[final_answer, DuckDuckGoSearchTool(), VisitWebpageTool(), buscar_jurisprudencia, formatar_resposta_juridica], ## add your tools here (don't remove final answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()