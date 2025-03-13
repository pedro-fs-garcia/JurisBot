# Cronograma e Divisão de Tarefas para 3 Sprints de 4 Semanas

## Visão Geral do MVP
O MVP será uma aplicação web que permite:
1. Busca de jurisprudência por palavras-chave, temas ou tribunais.
2. Resumo automático de decisões judiciais.
3. Visualização de resultados com filtros básicos (data, tribunal, tema).

---

## Sprint 1: Definição e Infraestrutura Básica
**Objetivo:** Configurar o ambiente de desenvolvimento, definir a arquitetura e criar a base do projeto.

### Tarefas:
1. **Definição do Escopo e Requisitos (Semana 1)**
   - Reunião para definir funcionalidades do MVP.
   - Documentação dos requisitos (Markdown ou ferramenta de gestão de projetos).
   - **Responsável:** Todos.

2. **Configuração do Ambiente de Desenvolvimento (Semana 1)**
   - Configurar repositório Git (GitHub/GitLab).
   - Configurar ambiente Python (virtualenv ou Docker).
   - Instalar bibliotecas básicas (FastAPI/Flask, SpaCy, Hugging Face, etc.).
   - **Responsável:** Pessoa 1.

3. **Definição da Arquitetura (Semana 2)**
   - Decidir sobre a estrutura do projeto (frontend, backend, banco de dados).
   - Criar diagrama da arquitetura.
   - **Responsável:** Pessoa 2.

4. **Configuração do Banco de Dados (Semana 2)**
   - Escolher e configurar o banco de dados (PostgreSQL).
   - Criar esquema inicial para armazenar decisões judiciais e metadados.
   - **Responsável:** Pessoa 3.

5. **Desenvolvimento do Backend Básico (Semana 3-4)**
   - Criar API básica com FastAPI/Flask para receber buscas.
   - Implementar endpoints iniciais (`/search`, `/summarize`).
   - **Responsável:** Pessoa 1 e Pessoa 2.

6. **Integração com NLP (Semana 4)**
   - Integrar SpaCy ou Hugging Face para pré-processamento de textos.
   - Criar função básica para resumir textos.
   - **Responsável:** Pessoa 3.

---

## Sprint 2: Desenvolvimento das Funcionalidades Principais
**Objetivo:** Implementar as funcionalidades principais do MVP.

### Tarefas:
1. **Desenvolvimento do Frontend (Semana 5-6)**
   - Criar interface básica com React.js ou Vue.js.
   - Implementar campo de busca e exibição de resultados.
   - **Responsável:** Pessoa 1.

2. **Melhoria do Backend (Semana 5-6)**
   - Implementar busca no banco de dados com filtros (tribunal, data, tema).
   - Melhorar a API para suportar paginação e ordenação de resultados.
   - **Responsável:** Pessoa 2.

3. **Integração Completa de NLP (Semana 6-7)**
   - Implementar resumo automático de decisões judiciais.
   - Adicionar suporte para identificação de termos jurídicos.
   - **Responsável:** Pessoa 3.

4. **Testes e Validação (Semana 7-8)**
   - Escrever testes unitários para o backend.
   - Validar funcionalidades com dados reais (exemplos de jurisprudência).
   - **Responsável:** Todos.

---

## Sprint 3: Polimento e Entrega do MVP
**Objetivo:** Refinar o MVP, corrigir bugs e preparar para a entrega.

### Tarefas:
1. **Melhoria da Interface do Usuário (Semana 9-10)**
   - Adicionar filtros avançados (data, tribunal, tema).
   - Melhorar a exibição de resultados (resumos, highlights de termos importantes).
   - **Responsável:** Pessoa 1.

2. **Otimização do Backend (Semana 9-10)**
   - Melhorar a performance das buscas (indexação no banco de dados).
   - Adicionar cache para consultas frequentes.
   - **Responsável:** Pessoa 2.

3. **Integração com Fontes de Dados (Semana 10-11)**
   - Implementar coleta automática de decisões judiciais (web scraping ou APIs).
   - Normalizar e armazenar dados no banco de dados.
   - **Responsável:** Pessoa 3.

4. **Testes Finais e Correção de Bugs (Semana 11-12)**
   - Realizar testes de carga e performance.
   - Corrigir bugs identificados.
   - **Responsável:** Todos.

5. **Preparação para Deploy (Semana 12)**
   - Configurar ambiente de produção (Heroku, AWS, ou similar).
   - Fazer deploy da aplicação.
   - **Responsável:** Pessoa 1 e Pessoa 2.

---

## Divisão de Responsabilidades por Pessoa

### Pessoa 1:
- Frontend (React.js).
- Configuração do ambiente e deploy.
- Auxílio no backend (APIs básicas).

### Pessoa 2:
- Backend (FastAPI/Flask).
- Banco de dados e otimização de buscas.
- Auxílio no frontend (integração com APIs).

### Pessoa 3:
- NLP (SpaCy, Hugging Face).
- Integração com fontes de dados.
- Testes e validação.

---

## Entregas Esperadas ao Final de Cada Sprint

### Sprint 1:
- Ambiente de desenvolvimento configurado.
- Arquitetura definida e documentada.
- API básica funcionando com integração inicial de NLP.

### Sprint 2:
- Frontend básico funcionando.
- Busca e resumo automático integrados.
- Testes unitários implementados.

### Sprint 3:
- MVP completo e funcional.
- Interface polida e otimizada.
- Aplicação deployada e pronta para uso.

---