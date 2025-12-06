# test_integration.py
"""
Script para testar a integração entre agentes de compliance e conspiração.
"""

from src.tools import investigate_conspiracy
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def test_conspiracy_investigation():
    """Testa a ferramenta de investigação de conspirações."""
    
    console.print(Panel(
        "[bold cyan]🧪 TESTE DE INTEGRAÇÃO: Agente Compliance + Conspiração[/bold cyan]",
        border_style="cyan"
    ))
    
    # Teste 1: Investigar planos contra Toby
    console.print("\n[bold yellow]📋 Teste 1: Investigar conspirações contra Toby[/bold yellow]\n")
    
    result = investigate_conspiracy("planos contra Toby Flenderson")
    
    console.print(Panel(
        f"[bold]Status:[/bold] {result['status']}\n"
        f"[bold]Mensagem:[/bold] {result['message']}\n"
        f"[bold]Emails Analisados:[/bold] {result['emails_analyzed']}",
        title="[bold green]Resultado da Investigação[/bold green]",
        border_style="green"
    ))
    
    if result['status'] == 'investigation_completed':
        console.print("\n[bold cyan]📄 RELATÓRIO COMPLETO:[/bold cyan]\n")
        md = Markdown(result['investigation_report'])
        console.print(md)
    
    # Teste 2: Investigar gastos suspeitos
    console.print("\n\n[bold yellow]📋 Teste 2: Investigar gastos não autorizados[/bold yellow]\n")
    
    result2 = investigate_conspiracy("gastos suspeitos e não autorizados")
    
    console.print(Panel(
        f"[bold]Status:[/bold] {result2['status']}\n"
        f"[bold]Mensagem:[/bold] {result2['message']}\n"
        f"[bold]Emails Analisados:[/bold] {result2['emails_analyzed']}",
        title="[bold green]Resultado da Investigação[/bold green]",
        border_style="green"
    ))
    
    if result2['status'] == 'investigation_completed':
        console.print("\n[bold cyan]📄 RELATÓRIO COMPLETO:[/bold cyan]\n")
        md2 = Markdown(result2['investigation_report'])
        console.print(md2)


if __name__ == "__main__":
    test_conspiracy_investigation()
