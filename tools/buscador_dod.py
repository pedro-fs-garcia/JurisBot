from smolagents.tools import Tool
from bs4 import BeautifulSoup
from typing import List
import requests
import urllib.parse
import json


class BuscadorDOD(Tool):
    name = "buscador_dod"
    description = "Executa uma busca por jurisprudencias mais recentes nos sites dizerodireito e buscadordizerodireito. Usar para buscar jurisprudencias."
    inputs = {'query': {'type': 'string', 'description': 'Os termos que serão utilizados para pesquisar jurisprudencias'}}
    output_type = "string"

    def __init__(self):
        return


    def construir_url_dod(self, termos: str) -> str:
        """Ferramenta para construir a url de pesquisa nos sites dizerodireito e buscadordizerodireito para realização de consultas juridicas
        
        Args:
            termos: uma string contendo as palavras chave que serão usadas na busca jurídica

        """

        base_url = "https://www.buscadordizerodireito.com.br/jurisprudencia/listar/"
        parametros = {
            "palavra-chave": termos,
            "criterio-pesquisa": "e",
            "forma-exibicao": "apenas-com-informativo",
            "ordenacao": "data-julgado"
        }
        query_string = urllib.parse.urlencode(parametros)
        url_final = f"{base_url}?{query_string}"
        print(url_final)
        return url_final


    def scrape_dod(self, query:str) -> List[dict]:
        """Ferramenta de pesquisa de jurisprudencias nos sites dizerodireito e buscadordizerodireito

        Args:
            query: uma string com as palavras chave da pesquisa de jurisprudencias

        """

        url = self.construir_url_dod(query)
        # url = "https://www.buscadordizerodireito.com.br/jurisprudencia/listar/?palavra-chave=demarca%C3%A7%C3%A3o+de++terras+indigenas&criterio-pesquisa=e&forma-exibicao=apenas-com-informativo&ordenacao=data-julgado"
        try:
            # Fazendo a requisição HTTP para obter o HTML da página
            response = requests.get(url)
            response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
            
            # Carregando o HTML no BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Array para armazenar os resultados
            items = []
            
            # Selecionando todos os elementos com a classe "item"
            for element in soup.select('.item'):
                # Extraindo as informações de cada item
                title_element = element.select_one('h2.titulo strong')
                title = title_element.text.strip() if title_element else ''
                
                link_element = element.select_one('h2.titulo a')
                link = link_element.get('href') if link_element else ''
                interrogation_index = link.find("?")
                link = link[:interrogation_index]
                id = link.split('/')[-1]

                # Extraindo as categorias
                categories = []
                for category_element in element.select('.categorias strong a'):
                    categories.append(category_element.text.strip())
                
                # Extraindo a origem (STF, STJ, etc.)
                origin_element = element.select_one('span strong:first-child')
                origin = origin_element.text.strip() if origin_element else ''
                
                # Extraindo o número do informativo, se existir
                informative_element = element.select_one('span strong a')
                informative_number = informative_element.text.strip() if informative_element else ''
                
                # Extraindo a descrição
                description_element = element.select_one('.txt-descricao-julgado p')
                description = description_element.text.strip() if description_element else ''
                if title and link:
                    # Adicionando o item ao array de resultados
                    items.append({
                        'title': title,
                        'link': link,
                        'id': id,
                        'categories': categories,
                        'tribunal': origin,
                        'informative_number': informative_number,
                        'description': description
                    })
            
            # Exibindo os resultados
            print(f'Total de itens encontrados: {len(items)}')
            # print(json.dumps(items, indent=2, ensure_ascii=False))
            
            return items
        
        except Exception as e:
            print(f'Erro ao fazer scraping: {e}')
            return []


    def scrape_detalhes_dod(self, id:str) -> dict:
        """Ferramentas para acessar e extrair ementas e detalhes de jurisprudencias dos sites dizerodireito e buscadordizerodireito

            Args:
                id: string alfanumerica contendo o id da jurisprudencia nos sites dizerodireito e buscadordizerodireito
        """

        try:
            url = f'https://www.buscadordizerodireito.com.br/jurisprudencia/detalhes/{id}'
            # Fazendo a requisição HTTP para obter o HTML da página
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Carregando o HTML no BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraindo o título da página
            title = soup.title.text.strip() if soup.title else ''
            
            # Extraindo a ementa oficial
            ementa_div = soup.select_one('div.ementa')
            ementa_title = ementa_div.select_one('h3.titulos-jurisprudencia').text.strip() if ementa_div and ementa_div.select_one('h3.titulos-jurisprudencia') else ''
            ementa_text = ementa_div.select_one('p').text.strip() if ementa_div and ementa_div.select_one('p') else ''
            
            # Extraindo os comentários
            comentarios_div = soup.select_one('div.comentarios')
            comentarios_title = comentarios_div.select_one('h3.text-center').text.strip() if comentarios_div and comentarios_div.select_one('h3.text-center') else ''
            
            area_comentario = comentarios_div.select_one('div.area-comentario')
            comentarios_text = area_comentario.get_text(strip=True) if area_comentario else ''
            
            # Extraindo a citação
            citacao_div = soup.select_one('div.citacao')
            citacao_title = citacao_div.select_one('h5').text.strip() if citacao_div and citacao_div.select_one('h5') else ''
            citacao_text = citacao_div.select_one('p').text.strip() if citacao_div and citacao_div.select_one('p') else ''
            
            # Organizando os dados extraídos
            resultado = {
                'titulo': title,
                'texto': ementa_title + "\n" + ementa_text,
                'comentarios': comentarios_text,
                'citacao': citacao_text,
            }
            
            # Exibindo os resultados
            # print(json.dumps(resultado, indent=4, ensure_ascii=False))
            
            return resultado
        
        except Exception as e:
            print(f'Erro ao fazer scraping: {e}')
            return {}
    
    
    def forward(self, query:str) -> List[dict]:
        '''
        Return:
            lista de dicionários:
            {
                'titulo': ,
                'texto': ,
                'tribunal': 
            }
        '''
        items = self.scrape_dod(query)
        print(items)
        detalhes = {}
        for i in range(min(len(items),5)):
            detalhes[i] = {}
            detalhes[i]['titulo'] = items[i].get('title')
            detalhes[i]['texto'] = self.scrape_detalhes_dod(items[i].get('id'))
            detalhes[i]['tribunal'] = items[i].get('tribunal')
        return detalhes