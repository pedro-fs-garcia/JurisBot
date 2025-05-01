from smolagents.tools import Tool
import requests
import json
from typing import Optional, Dict


class BuscadorTJDFT(Tool):
    name = "buscador_tjdft"
    description = ('''
        Executa uma busca por jurisprudências utilizando a API oficial do Tribunal de Justiça do Distrito Federal (TJDFT).
        Use esta ferramenta para recuperar decisões judiciais com base em termos de pesquisa e filtros opcionais.
    ''')

    inputs = {
        'query': {
            'type': 'string',
            'description': 'Termos principais a serem usados na busca por jurisprudências. Ex: "dano moral", "ação revisional", etc.'
        },
        'filtros': {
            'type': 'object',
            'description': (
                'Dicionário com filtros adicionais como campo:valor. '
                'Campos válidos incluem "nomeRelator", "orgaoJulgador", "classeProcessual", "assunto", entre outros.'
            ),
            'required': False
        }
    }

    output_type = "string"

    def __init__(self):
        self.base_url = "https://jurisdf.tjdft.jus.br/api/v1/pesquisa"
        self.headers = {"Content-Type": "application/json"}
        self.query: str = ""
        self.termos_acessorios: list[Dict[str, str]] = []
        self.pagina: int = 0
        self.tamanho: int = 10

    def adicionar_filtro(self, campo: str, valor: str) -> None:
        """Adiciona um filtro (campo:valor) à pesquisa de jurisprudência."""
        self.termos_acessorios.append({
            "campo": campo,
            "valor": valor
        })

    def definir_paginacao(self, pagina: int = 0, tamanho: int = 10) -> None:
        """Define a paginação da busca (número da página e quantidade de resultados)."""
        self.pagina = pagina
        self.tamanho = tamanho

    def montar_payload(self) -> dict:
        """Monta o corpo da requisição conforme os parâmetros atuais."""
        return {
            "query": self.query,
            "termosAcessorios": self.termos_acessorios,
            "pagina": self.pagina,
            "tamanho": self.tamanho
        }

    def buscar(self) -> dict:
        """Executa a requisição POST à API do TJDFT."""
        payload = self.montar_payload()
        response = requests.post(self.base_url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro {response.status_code}: {response.text}")

    def formatar_resultados(self, resultados: dict) -> str:
        """Formata os resultados da busca em uma string legível."""
        registros = resultados.get("registros", [])
        if not registros:
            return "Nenhum resultado encontrado."

        saida = ""
        for item in registros:
            saida += f"Processo: {item.get('processo')}\n"
            saida += f"Relator: {item.get('nomeRelator')}\n"
            saida += f"Ementa: {item.get('ementa', '')}\n"
            saida += "=" * 60 + "\n"
        return saida

    def forward(self, query: str, filtros: Optional[Dict[str, str]] = None) -> str:
        """Executa a ferramenta com os parâmetros fornecidos.

        Args:
            query (str): Termo principal da busca.
            filtros (dict, opcional): Filtros adicionais no formato campo: valor.

        Returns:
            str: Resultados formatados da jurisprudência ou mensagem de erro.
        """
        self.query = query
        self.termos_acessorios = []  # zera filtros anteriores
        if filtros:
            for key, value in filtros.items():
                self.adicionar_filtro(key, value)
        self.definir_paginacao(pagina=0, tamanho=5)

        try:
            resultados = self.buscar()
            return self.formatar_resultados(resultados)
        except Exception as e:
            return f"Erro ao buscar jurisprudências: {str(e)}"
