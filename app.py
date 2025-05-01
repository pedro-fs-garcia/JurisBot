from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool
import datetime
import requests
import pytz
import yaml
from tools.buscador_dod import BuscadorDOD
from tools.buscador_tjdft import BuscadorTJDFT
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
    """Ferramenta que realiza uma busca por jurisprudências relevantes usando os termos fornecidos.

    Esta ferramenta consulta um repositório de jurisprudência de tribunais brasileiros com base
    nos termos informados. Deve ser usada quando o objetivo for encontrar decisões judiciais
    relacionadas a um tema específico, como 'dano moral', 'responsabilidade civil', etc.

    Args:
        termos (str): Palavras-chave ou expressão descritiva que será usada na busca jurisprudencial.

    Returns:
        str: Resultados da pesquisa em formato JSON contendo decisões encontradas, ou uma mensagem de erro caso a consulta falhe.
    """
    try:
        dod = BuscadorDOD()
        resultados = dod.forward(termos)
        return json.dumps(resultados, ensure_ascii=False, indent=4)
    
    except Exception as e:
        return f"Erro ao buscar jurisprudência em Dizer o Direito: {str(e)}"


@tool
def buscar_jurisprudencia_tjdft(query:str, filtros:Dict[str, str] | None = None) -> str:
    """
    Realiza uma busca por jurisprudências diretamente na API oficial do Tribunal de Justiça do Distrito Federal e Territórios (TJDFT).

    Esta ferramenta deve ser usada para consultar decisões judiciais específicas do TJDFT. 
    Permite a inclusão de filtros avançados como nome do relator, data do julgamento e outros campos indexados pela API.

    Args:
        query (str): Termos principais da pesquisa jurisprudencial. 
                     Por exemplo: "dano moral", "violência doméstica", "revisão contratual".
                     
        filtros (Dict[str, str] | None): Filtros adicionais no formato chave:valor.
                     Exemplos de campos aceitos:
                     - "nomeRelator": nome do relator da decisão
                     - "nomeRevisor": nome do revisor
                     - "dataJulgamento": data do julgamento no formato "YYYY-MM-DD"
                     - "orgaoJulgador": nome do órgão julgador

    Returns:
        str: Resumo formatado dos resultados encontrados, contendo o número do processo, nome do relator e ementa.
             Caso ocorra um erro ou nenhum resultado seja encontrado, retorna uma mensagem adequada.
    """
    try:
        buscador = BuscadorTJDFT()
        return buscador.forward(query, filtros)
    except Exception as e:
        return f"Erro ao buscar jurisprudência do TJDF: {str(e)}"


@tool
def buscar_processo(proc:str) -> str:
    """Recupera informações detalhadas sobre um processo judicial específico a partir de seu número.

    Esta ferramenta deve ser usada quando se deseja obter dados de um processo judicial já identificado
    por seu número único (ex: número CNJ). Ela retorna informações como o andamento, partes envolvidas,
    tribunal responsável, classe processual, e outros detalhes relevantes.

    Args:
        proc (str): Número completo do processo judicial no formato oficial (ex: '0701234-56.2021.8.07.0001').

    Returns:
        str: Resumo das informações disponíveis sobre o processo informado, ou uma mensagem de erro caso não seja encontrado.
    """
    return


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