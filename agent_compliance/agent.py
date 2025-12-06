# agent_compliance/agent.py
"""
Definição do agente de compliance para uso com ADK CLI.
"""

import logging
import warnings

# Suprimir logs e warnings do OpenTelemetry
logging.getLogger('opentelemetry').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=RuntimeWarning, module='opentelemetry')
warnings.filterwarnings('ignore', message='.*Context.*')

from rich.console import Console
from google.adk.agents.llm_agent import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from .PROMPT import COMPLIANCE_AGENT_INSTRUCTION
import uuid
import asyncio
from src.call_agent import call_agent
from agent_conspiracy.agent import root_agent as conspiracy_agent
from agent_sumarizer.agent import root_agent as summarize_compliance_rules_agent
from agent_csv.agent import root_agent as csv_interaction_agent
from agent_financial_interpreter.agent import root_agent as financial_interpreter_agent
from agent_email_fraud.agent import root_agent as email_fraud_agent

# Criar console do Rich para logs coloridos
console = Console()

async def _call_email_fraud_agent_async(question: str) -> str:
        session_service = InMemorySessionService()
        response = await call_agent(
            question=question,
            session_service=session_service,
            app_name="email_fraud_investigation",
            agent=email_fraud_agent
        )
        console.print("\n[bold green]Resposta do Agente de Fraude por E-mail:[/bold green]")
        console.print(f"[green]{response}[/green]")
        return response

async def _call_conspiracy_agent_async(question: str) -> str:
        session_service = InMemorySessionService()
        response = await call_agent(
            question=question,
            session_service=session_service,
            app_name="conspiracy_investigation",
            agent=conspiracy_agent
        )
        console.print("\n[bold cyan]Resposta do Agente de Conspiração:[/bold cyan]")
        console.print(f"[green]{response}[/green]")
        return response

async def _call_summarize_compliance_rules_agent_async(question: str) -> str:
        session_service = InMemorySessionService()
        response = await call_agent(
            question=question,
            session_service=session_service,
            app_name="summarize_compliance_rules",
            agent=summarize_compliance_rules_agent
        )
        console.print("\n[bold magenta]Resposta do Agente de Resumo de Regras de Compliance:[/bold magenta]")
        console.print(f"[yellow]{response}[/yellow]")
        return response

async def _call_csv_interaction_agent_async(question: str) -> str:
        session_service = InMemorySessionService()
        response = await call_agent(
            question=question,
            session_service=session_service,
            app_name="csv_interaction",
            agent=csv_interaction_agent
        )
        console.print("\n[bold blue]Resposta do Agente de Interação com CSV:[/bold blue]")
        console.print(f"[cyan]{response}[/cyan]")
        return response

async def _call_financial_interpreter_agent_async(question: str) -> str:
        session_service = InMemorySessionService()
        response = await call_agent(
            question=question,
            session_service=session_service,
            app_name="financial_interpreter",
            agent=financial_interpreter_agent
        )
        console.print("\n[bold red]Resposta do Agente Intérprete Financeiro:[/bold red]")
        console.print(f"[bright_red]{response}[/bright_red]")
        return response

# Wrappers síncronos para uso como tools (executam em thread separada)

def call_email_fraud_agent(question: str) -> str:
    """
    Investiga fraudes em emails internos.
    
    Args:
        question: Pergunta sobre possíveis fraudes
        
    Returns:
        Relatório de investigação
    """
    import concurrent.futures
    import threading
    
    def run_in_new_loop():
        # Criar novo event loop nesta thread
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(_call_email_fraud_agent_async(question))
        finally:
            new_loop.close()
    
    # Executar em thread separada para evitar conflito com loop principal
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_new_loop)
        return future.result()

def call_conspiracy_agent(question: str) -> str:
    """
    Investiga conspirações através de análise de emails internos.
    
    Args:
        question: Pergunta sobre possíveis conspirações
        
    Returns:
        Relatório de investigação
    """
    import concurrent.futures
    import threading
    
    def run_in_new_loop():
        # Criar novo event loop nesta thread
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(_call_conspiracy_agent_async(question))
        finally:
            new_loop.close()
    
    # Executar em thread separada para evitar conflito com loop principal
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_new_loop)
        return future.result()

def call_summarize_compliance_rules_agent(question: str) -> str:
    """
    Resume políticas de compliance relevantes.
    
    Args:
        question: Pergunta sobre políticas
        
    Returns:
        Resumo das políticas
    """
    import concurrent.futures
    import threading
    
    def run_in_new_loop():
        # Criar novo event loop nesta thread
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(_call_summarize_compliance_rules_agent_async(question))
        finally:
            new_loop.close()
    
    # Executar em thread separada para evitar conflito com loop principal
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_new_loop)
        return future.result()

def call_csv_interaction_agent(question: str) -> str:
    """
    Interage com dados CSV de transações financeiras.
    
    Args:
        question: Pergunta sobre transações
        
    Returns:
        Análise das transações
    """
    import concurrent.futures
    import threading
    
    def run_in_new_loop():
        # Criar novo event loop nesta thread
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(_call_csv_interaction_agent_async(question))
        finally:
            new_loop.close()
    
    # Executar em thread separada para evitar conflito com loop principal
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_new_loop)
        return future.result()

def call_financial_interpreter_agent(question: str) -> str:
    """
    Interpreta violações de compliance em transações financeiras.
    
    Args:
        question: Dados de transações para análise
        
    Returns:
        Interpretação das violações
    """
    import concurrent.futures
    import threading
    
    def run_in_new_loop():
        # Criar novo event loop nesta thread
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(_call_financial_interpreter_agent_async(question))
        finally:
            new_loop.close()
    
    # Executar em thread separada para evitar conflito com loop principal
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_new_loop)
        return future.result()

## response = asyncio.run(call_conspiracy_agent(question="Existe alguma conspiração envolvendo Michael Scott na Dunder Mifflin?"))

## Quando perguntado sobre compras registradas (por qualquer um) que violam políticas de compliance,
## o agente de compliance deve iniciar o fluxo: agente que sumariza regras de compliance
## agente que sumariza regras de compliance -> gera lista de violações que podem ocorrer sobre aquele tema
## agente que interage com csv -> busca no banco de dados se existem compras que violam aquelas regras
## agente intérprete -> explica as violações encontradas e retorna a resposta para o agente de compliance, que responde ao usuário final.

def get_tools():
    from src.tools import (
        search_compliance_policies, 
        search_by_keyword, 
        get_policy_summary,
    )
    return [
        search_compliance_policies,
        search_by_keyword,
        get_policy_summary,
        call_conspiracy_agent,
        call_csv_interaction_agent,
        call_summarize_compliance_rules_agent,
        call_financial_interpreter_agent,
        call_email_fraud_agent
    ]

# Criar agente de compliance (root agent)
root_agent = Agent(
    model='gemini-2.0-flash',
    name='compliance_agent',
    description="Assistente especializado em políticas de compliance da Dunder Mifflin Paper Company.",
    instruction=COMPLIANCE_AGENT_INSTRUCTION,
    tools=get_tools()
)
