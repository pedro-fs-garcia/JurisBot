from smolagents import CodeAgent, DuckDuckGoSearchTool, load_tool, tool
import datetime
import requests
import pytz
import yaml
from tools.buscador_dod import BuscadorDOD
from tools.buscador_tjdft import BuscadorTJDFT
from tools.final_answer import FinalAnswerTool
import dotenv
import os
import json
from typing import List, Dict, Optional, Any
import markdown

from Gradio_UI import GradioUI
from tools.visit_webpage import VisitWebpageTool

dotenv.load_dotenv()


@tool
def buscar_jurisprudencia(termos: str, tribunal:str|None = None, limit:int = 5) -> str:
    """Tool that performs a search for relevant case law using the provided terms.

    This tool queries a repository of Brazilian court decisions based on
    the provided terms. It should be used when the objective is to find judicial decisions
    related to a specific topic, such as 'moral damages', 'civil liability', etc.

    Args:
        termos (str): Keywords or descriptive expression that will be used in the case law search.
        tribunal(str): Name of the brazilian court that will be used in the case law search.
        limit: (int): Number to limit the number of results per search

    Returns:
        str: Search results in JSON format containing found decisions, or an error message if the query fails.
    """
    try:
        dod = BuscadorDOD()
        resultados = dod.forward(termos)
        return json.dumps(resultados, ensure_ascii=False, indent=4)
    
    except Exception as e:
        return f"Error searching case law in Dizer o Direito: {str(e)}"


@tool
def buscar_jurisprudencia_tjdft(query:str, filtros:Dict[str, str] | None = None) -> str:
    """
    Tool that performs a search for case law directly in the official API of the Court of Justice of the Federal District and Territories (TJDFT).

    This tool should be used to consult specific judicial decisions from TJDFT.
    Allows for advanced filters such as judge's name, judgment date, and other fields indexed by the API.

    Args:
        query (str): Main terms of the case law search.
                     For example: "moral damages", "domestic violence", "contract review".
                     
        filtros (Dict[str, str] | None): Additional filters in key:value format.
                     Examples of accepted fields:
                     - "nomeRelator": name of the decision's judge
                     - "nomeRevisor": name of the reviewer
                     - "dataJulgamento": judgment date in "YYYY-MM-DD" format
                     - "orgaoJulgador": name of the judging body

    Returns:
        str: Formatted summary of found results, containing the process number, judge's name, and summary.
             If an error occurs or no results are found, returns an appropriate message.
    """
    try:
        buscador = BuscadorTJDFT()
        return buscador.forward(query, filtros)
    except Exception as e:
        return f"Error searching TJDFT case law: {str(e)}"


@tool
def buscar_processo(proc:str) -> str:
    """Tool that retrieves detailed information about a specific judicial process from its number.

    This tool should be used when you want to obtain data from a judicial process already identified
    by its unique number (e.g., CNJ number). It returns information such as progress, involved parties,
    responsible court, process class, and other relevant details.

    Args:
        proc (str): Complete judicial process number in official format (e.g., '0701234-56.2021.8.07.0001').

    Returns:
        str: Summary of available information about the informed process, or an error message if not found.
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
    """Tool for formatting legal responses in a structured and readable way.
    
    Args:
        titulo: Title of the response
        conteudo: Main content of the response
        jurisprudencias: List of relevant case law
        legislacao: List of cited legal provisions
        referencias: List of additional references
    """
    try:
        # Base response structure in markdown
        resposta = f"# {titulo}\n\n"
        
        # Conteúdo principal
        resposta += f"## Análise\n{conteudo}\n\n"
        
        # Case law section
        if jurisprudencias:
            resposta += "## Jurisprudências Relevantes\n"
            for jur in jurisprudencias:
                resposta += f"### {jur.get('tribunal', '')} - {jur.get('processo', '')}\n"
                resposta += f"**Relator:** {jur.get('relator', '')}\n"
                resposta += f"**Data:** {jur.get('data', '')}\n"
                resposta += f"**Ementa:** {jur.get('ementa', '')}\n"
                resposta += f"**Decisão:** {jur.get('decisao', '')}\n\n"
        
        # Legislation section
        if legislacao:
            resposta += "## Legislação Citada\n"
            for leg in legislacao:
                resposta += f"- {leg}\n"
            resposta += "\n"
        
        # References section
        if referencias:
            resposta += "## Referências\n"
            for ref in referencias:
                resposta += f"- {ref}\n"
        
        return resposta
    except Exception as e:
        return f"Error formatting response: {str(e)}"

final_answer = FinalAnswerTool()
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

# Classe para formatar a resposta no formato esperado pelo smolagents
class ChatMessage:
    """Classe que simula o formato de resposta esperado pelo smolagents."""
    def __init__(self, content):
        self.content = content
        self.finish_reason = "stop"

# Implementação do modelo Groq compatível com smolagents
class GroqModel:
    """Wrapper para Groq API compatível com smolagents."""
    
    def __init__(self, api_key=None, model="llama3-8b-8192", max_tokens=2000, temperature=0.7):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError("⚠️ API key do Groq não encontrada. Defina a variável de ambiente GROQ_API_KEY.")
        
        # Importar a biblioteca groq
        try:
            import groq
            self.client = groq.Client(api_key=self.api_key)
            print(f"✅ Cliente Groq inicializado com sucesso. Modelo: {model}")
        except ImportError:
            raise ImportError("⚠️ Biblioteca groq não encontrada. Instale com: pip install groq")
    
    def __call__(self, messages, **kwargs):
        """Interface compatível com smolagents."""
        try:
            # Extrair parâmetros relevantes
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            temperature = kwargs.get("temperature", self.temperature)
            stop_sequences = kwargs.get("stop_sequences", None)
            
            # Converter mensagens para o formato esperado pelo Groq
            formatted_messages = []
            for msg in messages:
                if not isinstance(msg["content"], str):
                    msg["content"] = str(msg["content"])
                formatted_messages.append({
                    "role": msg["role"] if msg['role'] in ['system', 'user', 'assistant'] else 'user',
                    "content": msg["content"]
                })
            
            # Chamar a API do Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop_sequences
            )
            
            # Retornar no formato esperado pelo smolagents
            return ChatMessage(response.choices[0].message.content)
        except Exception as e:
            print(f"Erro ao chamar Groq API: {e}")
            raise RuntimeError(f"Erro ao chamar Groq API: {str(e)}")

# Função para criar o modelo Groq
def create_groq_model():
    """Cria e retorna uma instância do modelo Groq."""
    try:
        # Verificar se a API key está definida
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("API key do Groq não encontrada. Defina a variável de ambiente GROQ_API_KEY.")
        
        # Criar o modelo
        print("Inicializando modelo Groq...")
        model = GroqModel(
            api_key=api_key,
            model="llama3-8b-8192",  # Modelo rápido e eficiente
            max_tokens=2000,
            temperature=0.5
        )
        
        # Teste rápido para verificar se o modelo está funcionando
        print("Testando modelo Groq...")
        result = model(
            messages=[{"role": "user", "content": "Olá, você pode me ajudar com uma questão jurídica?"}],
            max_tokens=10
        )
        
        print("✅ Modelo Groq inicializado e testado com sucesso!")
        return model
    except Exception as e:
        print(f"❌ Erro ao inicializar modelo Groq: {e}")
        raise RuntimeError(f"Falha ao inicializar modelo Groq: {str(e)}")

# Carrega o modelo Groq
model = create_groq_model()

# Carrega prompts
with open("prompts.yaml", 'r', encoding='utf-8') as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=model,
    tools=[final_answer, DuckDuckGoSearchTool(), VisitWebpageTool(), buscar_jurisprudencia, formatar_resposta_juridica],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)

# Inicia a interface Gradio
GradioUI(agent).launch()