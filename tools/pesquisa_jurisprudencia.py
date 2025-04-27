from smolagents.tools import Tool


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

from tools.web_search import DuckDuckGoSearchTool


class PesquisaJurisprudencia(Tool):    
    def __init__(self):
        return
    

    def busca_duckduckgo(self):
        DuckDuckGoSearchTool()



    def buscar_julgados_tre_sp(self, consulta: str, max_resultados: int = 10):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 30)

        try:
            driver.get("https://jurisprudencia.tre-sp.jus.br/#/pesquisa")

            # Aguarda até que a URL mude para incluir o caminho real da página (evita erros de JS não carregado)
            wait.until(lambda d: "/pesquisa" in d.current_url)

            print("🔄 Esperando carregamento da página...")
            time.sleep(5)  # Espera extra pra garantir que o Vue carregou tudo

            # Tenta buscar o input pelo placeholder
            input_busca = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//input[@placeholder='Pesquisa livre']"))
            )
            input_busca.clear()
            input_busca.send_keys(consulta)

            print("🔍 Iniciando pesquisa...")
            botao_pesquisar = driver.find_element(By.XPATH, "//button[.//span[text()='Pesquisar']]")
            botao_pesquisar.click()

            print("⏳ Aguardando resultados...")
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-jurisprudencia")))
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            cards = soup.select(".card-jurisprudencia")
            resultados = []

            for card in cards[:max_resultados]:
                titulo = card.select_one(".titulo-jurisprudencia").get_text(strip=True)
                corpo = card.select_one(".texto-jurisprudencia").get_text(strip=True)
                resultados.append({
                    "titulo": titulo,
                    "conteudo": corpo
                })

            return resultados

        except Exception as e:
            print(f"❌ Erro ao buscar julgados: {e}")
            return []

        finally:
            driver.quit()