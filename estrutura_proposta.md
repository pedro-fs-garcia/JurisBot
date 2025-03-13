# Estrutura Geral do Código

Abaixo está a estrutura de diretórios e arquivos recomendada para o projeto. Cada diretório e arquivo tem uma função específica.

---

## **Estrutura de Diretórios**
```
juris_ai/   # Diretório raiz do projeto
├── backend/    # Código do backend (API e lógica de negócio)
│ ├── api/  # Endpoints da API
│ ├── models/   # Modelos de banco de dados
│ ├── services/     # Lógica de negócio e serviços
│ ├── utils/    # Utilitários (funções auxiliares)
│ ├── main.py   # Ponto de entrada do backend
│ └── requirements.txt  # Dependências do backend
|
├── frontend/   # Código do frontend (interface do usuário)
│ ├── public/   # Arquivos estáticos (imagens, favicon, etc.)
│ ├── src/  # Código-fonte do frontend
│ │ ├── components/     # Componentes React/Vue
│ │ ├── pages/  # Páginas da aplicação
│ │ ├── services/   # Chamadas à API do backend
│ │ ├── App.jsx     # Componente principal
│ │ └── index.js    # Ponto de entrada do frontend
│ ├── package.json  # Dependências do frontend
│ └── README.md     # Documentação do frontend
|
├── nlp/    # Módulo de processamento de linguagem natural
│ ├── models/   # Modelos de NLP (SpaCy, Hugging Face)
│ ├── utils/    # Utilitários para NLP
│ ├── main.py   # Ponto de entrada do módulo NLP
│ └── requirements.txt  # Dependências do NLP
|
├── database/   # Configurações e scripts do banco de dados
│ ├── migrations/   # Migrações do banco de dados
│ ├── scripts/  # Scripts SQL ou NoSQL
│ └── config.py     # Configurações de conexão com o banco
|
├── tests/  # Testes automatizados
│ ├── unit/     # Testes unitários
│ ├── integration/  # Testes de integração
│ └── conftest.py   # Configurações para testes
|
├── .env    # Variáveis de ambiente
├── .gitignore  # Arquivos e diretórios ignorados pelo Git
├── README.md   # Documentação geral do projeto
└── requirements.txt    # Dependências gerais do projeto
```


---

## **Descrição dos Diretórios e Arquivos**

### **1. `backend/`**
Contém o código do backend, responsável por processar requisições, integrar com o banco de dados e o módulo de NLP.

- **`api/`:** Endpoints da API (por exemplo, `/search`, `/summarize`).
- **`models/`:** Modelos de banco de dados (por exemplo, `Decision`, `Court`).
- **`services/`:** Lógica de negócio (por exemplo, busca de decisões, geração de resumos).
- **`utils/`:** Funções auxiliares (por exemplo, validação de dados, formatação de textos).
- **`main.py`:** Ponto de entrada do backend (configuração do FastAPI/Flask).
- **`requirements.txt`:** Lista de dependências do backend.

### **2. `frontend/`**
Contém o código do frontend, responsável pela interface do usuário.

- **`public/`:** Arquivos estáticos (imagens, favicon, etc.).
- **`src/`:** Código-fonte do frontend.
  - **`components/`:** Componentes reutilizáveis (por exemplo, `SearchBar`, `ResultList`).
  - **`pages/`:** Páginas da aplicação (por exemplo, `HomePage`, `SearchPage`).
  - **`services/`:** Chamadas à API do backend (por exemplo, `searchDecisions`, `summarizeText`).
  - **`App.jsx`:** Componente principal da aplicação.
  - **`index.js`:** Ponto de entrada do frontend.
- **`package.json`:** Dependências do frontend.
- **`README.md`:** Documentação do frontend.

### **3. `nlp/`**
Contém o código do módulo de processamento de linguagem natural (NLP).

- **`models/`:** Modelos de NLP (por exemplo, modelos pré-treinados do SpaCy ou Hugging Face).
- **`utils/`:** Utilitários para NLP (por exemplo, tokenização, stemming).
- **`main.py`:** Ponto de entrada do módulo NLP.
- **`requirements.txt`:** Dependências do NLP.

### **4. `database/`**
Contém configurações e scripts relacionados ao banco de dados.

- **`migrations/`:** Migrações do banco de dados (se usar um ORM como SQLAlchemy).
- **`scripts/`:** Scripts SQL ou NoSQL para criação de tabelas ou índices.
- **`config.py`:** Configurações de conexão com o banco de dados.

### **5. `tests/`**
Contém testes automatizados para garantir a qualidade do código.

- **`unit/`:** Testes unitários (por exemplo, testar funções isoladas).
- **`integration/`:** Testes de integração (por exemplo, testar a interação entre módulos).
- **`conftest.py`:** Configurações para testes (por exemplo, fixtures do pytest).

### **6. Arquivos na Raiz**
- **`.env`:** Variáveis de ambiente (por exemplo, chaves de API, credenciais do banco de dados).
- **`.gitignore`:** Lista de arquivos e diretórios ignorados pelo Git (por exemplo, `venv/`, `node_modules/`).
- **`README.md`:** Documentação geral do projeto (visão geral, como executar, etc.).
- **`requirements.txt`:** Dependências gerais do projeto (backend, NLP, etc.).

---

## **Exemplo de Código Inicial**

### **Backend (`backend/main.py`)**
```python
from fastapi import FastAPI
from backend.api import search, summarize

app = FastAPI()

# Endpoints da API
app.include_router(search.router)
app.include_router(summarize.router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao agente de pesquisa de jurisprudência!"}
```

### **Frontend (`frontend/src/App.jsx`)**
```jsx
import React from "react";
import SearchBar from "./components/SearchBar";

function App() {
  return (
    <div>
      <h1>Agente de Pesquisa de Jurisprudência</h1>
      <SearchBar />
    </div>
  );
}

export default App;
```

### **NLP (`nlp/main.py`)**
```python
import spacy

nlp = spacy.load("pt_core_news_sm")

def summarize_text(text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    return " ".join(sentences[:3])  # Retorna as 3 primeiras frases
```