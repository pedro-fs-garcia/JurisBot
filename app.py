from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool
import datetime
import requests
import pytz
import yaml
from tools.final_answer import FinalAnswerTool
from huggingface_hub.utils import HfHubHTTPError
import dotenv
import os

from Gradio_UI import GradioUI

dotenv.load_dotenv()

# Below is an example of a tool that does nothing. Amaze us with your creativity !
@tool
def my_custom_tool(arg1:str, arg2:int)-> str: #it's import to specify the return type
    #Keep this format for the description / args / args description but feel free to modify the tool
    """A tool that does nothing yet 
    Args:
        arg1: the first argument
        arg2: the second argument
    """
    return "What magic will you build ?"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"


final_answer = FinalAnswerTool()
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

# Lista de modelos para fallback
MODELS_TO_TRY = [
    "https://agents-course-unit4-scoring.hf.space",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.2",
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
with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=model,
    tools=[final_answer, DuckDuckGoSearchTool()], ## add your tools here (don't remove final answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()