# 🔍 Sistema de Auditoria Inteligente - Dunder Mifflin Paper Company (README GERADO POR I.A)

## 📋 Sobre o Projeto

Sistema de auditoria baseado em Inteligência Artificial desenvolvido para Toby Flenderson (RH da Dunder Mifflin - Scranton) para investigar violações de compliance, conspirações internas e fraudes financeiras.

O sistema utiliza **RAG (Retrieval-Augmented Generation)** com ChromaDB para vetorização de documentos e **Google ADK (Agent Development Kit)** para orquestração de múltiplos agentes especializados.

---

## 🎯 Funcionalidades Principais

O sistema atende aos três requisitos especificados:

### 1. ✅ Chatbot de Consulta de Regras de Compliance (3 pontos)
- Responde dúvidas sobre políticas de compliance da empresa
- Utiliza RAG para busca semântica no documento `politica_compliance.txt`
- Fornece respostas fundamentadas com trechos literais das políticas

### 2. 🕵️ Sistema de Verificação de Conspiração (3 pontos)
- Investiga conspirações e planos irregulares através de análise de emails
- Detecta tentativas de demissão irregular, sabotagem e ações antiéticas
- Foco especial em investigar suspeitas sobre Michael Scott

### 3. 💰 Sistema de Detecção de Fraudes Financeiras (4 pontos)

#### 3.1. Fraudes Explícitas (2 pontos)
- Analisa transações em `transacoes_bancarias.csv`
- Identifica violações diretas das políticas de compliance
- Cruza regras de compliance com dados financeiros

#### 3.2. Fraudes com Contexto de Comunicação (2 pontos)
- Detecta fraudes que exigem análise de emails
- Identifica combinações de desvio de verba via comunicação interna
- Correlaciona evidências de emails com transações financeiras

---

## 🏗️ Arquitetura do Sistema

### Visão Geral

O sistema é baseado em uma **arquitetura multi-agente orquestrada**, onde um agente principal (Compliance Agent) coordena chamadas para agentes especializados de acordo com o tipo de requisição.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USUÁRIO (Toby Flenderson)                        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃      🎯 AGENTE ORQUESTRADOR (Compliance Agent)   ┃
         ┃    - Classifica tipo de pergunta                 ┃
         ┃    - Decide qual fluxo executar                  ┃
         ┃    - Chama agentes especializados                ┃
         ┗━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│   FLUXO 1          │  │   FLUXO 2          │  │   FLUXO 3          │
│   Consulta de      │  │   Investigação de  │  │   Detecção de      │
│   Compliance       │  │   Conspiração      │  │   Fraudes          │
└────────────────────┘  └────────────────────┘  └────────────────────┘
```

### 📊 **PLACEHOLDER PARA DIAGRAMA COMPLETO DA ARQUITETURA**
<!-- Inserir aqui uma imagem mostrando todos os agentes, ferramentas e fluxos -->

---

## 🔄 Fluxos de Execução Detalhados

### **FLUXO 1: Consulta de Compliance**

Quando o usuário faz perguntas sobre políticas de compliance:

```
┌──────────────┐
│   Usuário    │ "Qual o limite de reembolso para almoços?"
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Compliance Agent (Orquestrador)         │
│  - Identifica como pergunta de política  │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Tools de Busca (RAG):                   │
│  • search_compliance_policies()          │
│  • search_by_keyword()                   │
│  • get_policy_summary()                  │
│                                          │
│  ↓ ChromaDB                              │
│  ↓ Embeddings (Google AI)                │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Resposta Formatada:                     │
│  ✓ Resposta direta                       │
│  ✓ Trechos literais das políticas        │
│  ✓ Valores relevantes                    │
│  ✓ Responsáveis                          │
└──────────────────────────────────────────┘
```

---

### **FLUXO 2: Investigação de Conspiração**

Quando detectadas palavras-chave de investigação (conspiração, fraude, plano, irregular, suspeito):

```
┌──────────────┐
│   Usuário    │ "Michael Scott está conspirando contra Toby?"
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Compliance Agent (Orquestrador)         │
│  - Detecta termos de investigação        │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  🕵️ Conspiracy Agent                     │
│  - Analisa emails internos               │
│  - Detecta ações antiéticas              │
│  - Identifica tentativas de demissão     │
│  - Avalia gastos suspeitos               │
└──────┬───────────────────────────────────┘
       │
       │ (usa investigate_conspiracy tool)
       ▼
┌──────────────────────────────────────────┐
│  Email Retriever (ChromaDB)              │
│  - Busca semântica em emails             │
│  - Filtra por metadados                  │
│  - Ordena por relevância                 │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  📋 Relatório de Investigação:           │
│  • Status (Evidências/Sem evidências)    │
│  • Resumo executivo                      │
│  • Evidências detalhadas                 │
│  • Emails suspeitos (literais)           │
│  • Violações identificadas               │
│  • Gravidade (Alta/Média/Baixa)          │
│  • Conclusão e recomendações             │
└──────────────────────────────────────────┘
```

---

### **FLUXO 3A: Violações Financeiras Explícitas**

Para fraudes que aparecem diretamente no banco de dados:

```
┌──────────────┐
│   Usuário    │ "Quais compras violam a política de compliance?"
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Compliance Agent (Orquestrador)         │
└──────┬───────────────────────────────────┘
       │
       ▼ ETAPA 1
┌──────────────────────────────────────────┐
│  📚 Summarizer Agent                     │
│  - Sumariza regras de compliance         │
│  - Gera lista de violações possíveis     │
└──────┬───────────────────────────────────┘
       │
       │ (saída integral passada adiante)
       ▼ ETAPA 2
┌──────────────────────────────────────────┐
│  📊 CSV Agent                            │
│  - Recebe regras de compliance           │
│  - Executa queries em Pandas             │
│  - Busca transações violadoras           │
│  - Retorna dados brutos do CSV           │
└──────┬───────────────────────────────────┘
       │
       │ (saída integral passada adiante)
       ▼ ETAPA 3
┌──────────────────────────────────────────┐
│  💼 Financial Interpreter Agent          │
│  - Interpreta dados financeiros          │
│  - Explica violações encontradas         │
│  - Gera relatório final                  │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Orquestrador retorna relatório ao user  │
└──────────────────────────────────────────┘
```

**⚠️ IMPORTANTE:** A saída de cada agente é passada **INTEGRALMENTE** para o próximo, sem modificações.

---

### **FLUXO 3B: Fraudes Ocultas (Contexto de Email)**

Para fraudes que não aparecem explicitamente no CSV, mas podem ser detectadas via emails:

```
┌──────────────┐
│   Usuário    │ "Existe fraude escondida nos emails?"
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Compliance Agent (Orquestrador)         │
└──────┬───────────────────────────────────┘
       │
       ▼ ETAPA 1
┌──────────────────────────────────────────┐
│  📧 Email Fraud Agent                    │
│  - Analisa emails com contexto financeiro│
│  - Detecta combinações suspeitas         │
│  - Identifica keywords de fraude         │
│  - Retorna JSON com emails suspeitos     │
└──────┬───────────────────────────────────┘
       │
       │ (JSON integral passado adiante)
       ▼ ETAPA 2
┌──────────────────────────────────────────┐
│  📊 CSV Agent                            │
│  - Recebe JSON de emails suspeitos       │
│  - Extrai keywords financeiras           │
│  - Busca transações correlacionadas      │
│  - Retorna dados do CSV                  │
└──────┬───────────────────────────────────┘
       │
       ▼ ETAPA 3
┌──────────────────────────────────────────┐
│  🎯 Orquestrador (Compliance Agent)      │
│  - Gera RELATÓRIO FINAL                  │
│  - Conecta emails ↔ transações           │
│  - Lista evidências                      │
│  - Identifica responsáveis               │
│  - Cita valores e trechos literais       │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  📋 Relatório Final ao Usuário           │
└──────────────────────────────────────────┘
```

**⚠️ IMPORTANTE:** O relatório final é **SEMPRE** gerado pelo orquestrador, não por outros agentes.

---

## 🤖 Agentes Especializados

### 1. **Compliance Agent** (Orquestrador Principal)
- **Modelo:** `gemini-2.0-flash`
- **Função:** Classificar requisições e orquestrar fluxos
- **Ferramentas:** Todas as tools disponíveis no sistema

### 2. **Conspiracy Agent** (Investigador)
- **Modelo:** `gemini-2.0-flash`
- **Função:** Investigar conspirações e planos irregulares
- **Ferramentas:** `investigate_conspiracy()`

### 3. **Summarizer Agent**
- **Modelo:** `gemini-2.5-flash`
- **Função:** Sumarizar regras de compliance
- **Ferramentas:** `search_compliance_policies()`, `search_by_keyword()`, `get_policy_summary()`

### 4. **CSV Agent**
- **Modelo:** `gemini-2.5-flash`
- **Função:** Executar queries em dados financeiros
- **Ferramentas:** `infer_csv_schema()`, `execute_pandas_query()`, `extract_keywords_from_input()`

### 5. **Financial Interpreter Agent**
- **Modelo:** `gemini-2.5-flash`
- **Função:** Interpretar transações e explicar violações
- **Ferramentas:** `search_compliance_policies()`, `search_by_keyword()`, `get_policy_summary()`

### 6. **Email Fraud Agent**
- **Modelo:** `gemini-2.5-flash`
- **Função:** Detectar fraudes ocultas em emails
- **Ferramentas:** `find_fraud_emails()`

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Google Generative AI (Gemini)** - LLM principal
- **Google ADK** - Framework de orquestração de agentes
- **ChromaDB** - Vector store para RAG
- **LangChain** - Text splitting e processamento
- **Pandas** - Análise de dados CSV
- **Rich** - Interface de terminal colorida

---

## 📦 Estrutura do Projeto

```
chatbot_dunder_mifflin/
├── agent_compliance/       # Agente orquestrador principal
│   ├── agent.py
│   └── PROMPT.py
├── agent_conspiracy/       # Agente investigador de conspirações
│   └── agent.py
├── agent_sumarizer/       # Agente sumarizador de regras
│   ├── agent.py
│   └── PROMPT.py
├── agent_csv/             # Agente de análise CSV
│   ├── agent.py
│   └── PROMPT.py
├── agent_financial_interpreter/  # Agente intérprete financeiro
│   ├── agent.py
│   └── PROMPT.py
├── agent_email_fraud/     # Agente detector de fraudes em email
│   └── agent.py
├── src/                   # Código fonte principal
│   ├── config.py          # Configurações
│   ├── ingest.py          # Ingestão de políticas
│   ├── retriever.py       # Retriever de compliance
│   ├── email_ingestion.py # Ingestão de emails
│   ├── email_parser.py    # Parser de emails
│   ├── email_retriever.py # Retriever de emails
│   ├── tools.py           # Ferramentas dos agentes
│   └── call_agent.py      # Utilitário para chamar agentes
├── data/                  # Dados da Dunder Mifflin
│   ├── politica_compliance.txt
│   ├── transacoes_bancarias.csv
│   └── emails.txt
├── chroma_db/             # Vector store (gerado automaticamente)
├── test_*.py              # Scripts de teste
├── requirements.txt       # Dependências Python
├── adk.yaml              # Configuração ADK
└── README.md             # Este arquivo
```

---

## ⚙️ Instalação e Configuração

### Pré-requisitos

- **Python 3.10 ou superior**
- **pip** (gerenciador de pacotes Python)
- **Git**
- **Conta Google Cloud** com API Key para Gemini

### Passo 1: Clonar o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd chatbot_dunder_mifflin
```

### Passo 2: Criar Ambiente Virtual

É **altamente recomendado** usar um ambiente virtual para isolar as dependências:

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# No Linux/Mac:
source venv/bin/activate

# No Windows:
venv\Scripts\activate
```

### Passo 3: Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 4: Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
touch .env
```

Adicione sua chave de API do Google:

```env
GOOGLE_API_KEY=sua_chave_api_aqui
```

**⚠️ IMPORTANTE:** Nunca commite o arquivo `.env` no repositório!

---

## 🚀 Preparação dos Dados (OBRIGATÓRIO)

Antes de executar os agentes, você **DEVE** rodar os scripts de ingestão para popular o ChromaDB com os dados vetorizados.

### Passo 1: Ingestão das Políticas de Compliance

```bash
python3 test_ingest.py
```

Este script:
- Lê o arquivo `data/politica_compliance.txt`
- Divide em chunks usando RecursiveCharacterTextSplitter
- Gera embeddings com Google AI
- Armazena no ChromaDB na coleção `compliance_policies`

**Saída esperada:**
```
✅ 45 chunks recuperados
📋 Resumo dos Chunks
```

### Passo 2: Ingestão dos Emails Internos

```bash
python3 test_email_ingestion.py
```

Este script:
- Lê o arquivo `data/emails.txt`
- Faz parsing dos emails
- Detecta metadados (autor, destinatários, menções a Toby, etc.)
- Gera embeddings
- Armazena no ChromaDB na coleção `emails`

**Saída esperada:**
```
✅ Coleção 'emails' encontrada!
Total de emails: 87
```

---

## 🎮 Como Usar o Sistema

### Método Recomendado: Interface Web ADK

O Google ADK fornece uma interface web interativa para conversar com os agentes.

#### 1. Iniciar o Servidor ADK

```bash
adk web
```

Este comando:
- Inicia um servidor local
- Abre automaticamente o navegador
- Carrega todos os agentes configurados em `adk.yaml`

#### 2. Acessar a Interface

A interface estará disponível em: `http://localhost:8000`

#### 3. Selecionar o Agente

Você verá uma lista de agentes disponíveis:

- ✅ **compliance_agent** ← **USE ESTE PARA FUNCIONALIDADE COMPLETA**
- agent_summarizer
- agent_csv
- agent_conspiracy
- agent_financial_interpreter
- agent_email_fraud

**⚠️ IMPORTANTE:** 

O agente **`compliance_agent`** é o **orquestrador principal** e oferece acesso a todas as funcionalidades do sistema. 

Os outros agentes são especializados e são chamados automaticamente pelo `compliance_agent` conforme necessário. Você pode usá-los diretamente para testes, mas para o sistema completo, **sempre use o `compliance_agent`**.

#### 4. Exemplos de Perguntas

**Consulta de Compliance:**
```
Qual é o limite de reembolso para almoços com clientes?
```

**Investigação de Conspiração:**
```
Michael Scott está conspirando contra Toby Flenderson?
```

**Fraudes Explícitas:**
```
Quais compras violam a política de compliance?
```

**Fraudes Ocultas (Email):**
```
Existe alguma fraude escondida nos emails?
```

---

## 🧪 Scripts de Teste

O projeto inclui vários scripts de teste para validar componentes individuais:

### Testar Conexão com Google AI
```bash
python3 test_conn.py
```

### Testar Retriever de Compliance
```bash
python3 test_retriever.py
```

### Testar Retriever de Emails
```bash
python3 test_email_retriever.py
```

### Testar Integração Completa
```bash
python3 test_integration.py
```

---

## 📊 Dataset da Dunder Mifflin

### 1. `politica_compliance.txt`
Documento com as regras de compliance da empresa, incluindo:
- Limites de gastos
- Reembolsos permitidos
- Itens proibidos
- Processos de autorização

### 2. `transacoes_bancarias.csv`
Extrato de gastos dos funcionários com colunas:
- Data
- Funcionário
- Valor
- Categoria
- Descrição
- Fornecedor

### 3. `emails.txt`
Dump de emails internos contendo:
- Comunicação entre funcionários
- Evidências de possíveis conspirações
- Menções a planos irregulares
- Discussões sobre gastos

---

## 🎥 Demonstração em Vídeo

**📹 PLACEHOLDER PARA LINK DO VÍDEO**

O vídeo de demonstração mostra o sistema atendendo aos três requisitos:
1. Chatbot de consulta de compliance
2. Verificação de conspiração
3. Detecção de fraudes (explícitas e ocultas)

---

## 🔒 Segurança e Boas Práticas

- ✅ API Keys armazenadas em `.env` (não commitadas)
- ✅ `.gitignore` configurado para excluir dados sensíveis
- ✅ Namespace restrito em `execute_pandas_query()` para segurança
- ✅ Validação de entrada em todas as tools
- ✅ Tratamento de erros em operações críticas

---

## 🐛 Troubleshooting

### Erro: "GOOGLE_API_KEY não encontrada"
**Solução:** Verifique se o arquivo `.env` existe e contém a chave válida.

### Erro: "Coleção não encontrada no ChromaDB"
**Solução:** Execute os scripts de ingestão (`test_ingest.py` e `test_email_ingestion.py`).

### Erro: "ModuleNotFoundError"
**Solução:** Ative o ambiente virtual e reinstale as dependências:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Agentes não respondem corretamente
**Solução:** Verifique se você está usando o `compliance_agent` (orquestrador) na interface ADK.

---

## 📝 Notas de Desenvolvimento

### Decisões de Design

1. **Arquitetura Multi-Agente:** Escolhida para separar responsabilidades e facilitar manutenção
2. **Google ADK:** Framework robusto para orquestração com suporte nativo a Gemini
3. **ChromaDB:** Vector store leve e eficiente para RAG local
4. **Fluxos Rígidos:** Garantem consistência e rastreabilidade nas investigações

### Limitações Conhecidas

- Sistema projetado para dataset específico da Dunder Mifflin
- Requer ingestão prévia dos dados
- Depende de conexão com Google AI

---

## 👥 Autor

Desenvolvido por Caio de Alcantara Santos para a atividade "Desafio: A Auditoria do Toby" - Módulo 8 - Inteli

---

## 📄 Licença

Este projeto é desenvolvido para fins educacionais e pode ser reproduzido livremente sem custos.

---
