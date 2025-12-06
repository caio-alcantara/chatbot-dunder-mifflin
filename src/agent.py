# src/adk_agent.py
"""
Agente de Compliance usando Google ADK (Agent Development Kit).
Versão oficial com suporte a tools.
"""

from google.adk.agents.llm_agent import Agent
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

from src.config import MODEL_NAME
from src.tools import search_compliance_policies, search_by_keyword, get_policy_summary

console = Console()


class ADKComplianceAgent:
    """
    Agente de Compliance usando Google ADK.
    Orquestra tools para responder perguntas sobre políticas.
    """
    
    def __init__(self, temperature: float = 0.1):
        """
        Inicializa o agente ADK.
        
        Args:
            temperature: Temperatura do modelo (0 = determinístico, 1 = criativo)
        """
        console.print("[yellow]🚀 Inicializando Agente ADK...[/yellow]\n")
        
        # Criar agente com Google ADK
        self.agent = Agent(
            model=MODEL_NAME,
            name='compliance_agent',
            description="Assistente especializado em políticas de compliance da Dunder Mifflin Paper Company.",
            instruction="""Você é um assistente especializado em políticas de compliance da Dunder Mifflin Paper Company.

Suas responsabilidades:
1. Responder perguntas sobre políticas de compliance usando as tools disponíveis
2. SEMPRE usar a tool 'search_compliance_policies' para buscar informações antes de responder
3. Citar especificamente os trechos relevantes que fundamentam sua resposta
4. Se a informação não for encontrada pelas tools, dizer claramente que não encontrou
5. Ser preciso, profissional e objetivo
6. Usar linguagem clara e acessível

Formato de resposta:
- Responda diretamente a pergunta
- Cite os trechos específicos entre aspas ou em blocos
- Se houver múltiplas regras relevantes, liste-as claramente
- Seja conciso mas completo
- SEMPRE indique de qual trecho (rank/ID) veio cada informação

IMPORTANTE:
- NÃO invente informações
- NÃO use conhecimento externo
- Use APENAS as informações retornadas pelas tools
- Se a tool não retornar resultados, informe isso ao usuário

Tools disponíveis:
- search_compliance_policies: Busca semântica nas políticas (USE SEMPRE)
- search_by_keyword: Busca exata por palavra-chave
- get_policy_summary: Informações gerais sobre as políticas""",
            tools=[
                search_compliance_policies,
                search_by_keyword,
                get_policy_summary
            ],
        )
        
        console.print("[green]✅ Agente ADK inicializado[/green]")
        console.print(f"[cyan]🤖 Modelo: {MODEL_NAME}[/cyan]")
        console.print(f"[cyan]🌡️  Temperature: {temperature}[/cyan]")
        console.print(f"[cyan]🛠️  Tools: {len(self.agent.tools)}[/cyan]\n")
    
    def ask(self, query: str, show_raw: bool = False) -> dict:
        """
        Faz uma pergunta ao agente.
        
        Args:
            query: Pergunta do usuário
            show_raw: Se True, mostra a resposta raw do agente
            
        Returns:
            Dicionário com resposta e metadados
        """
        console.print(f"\n[bold cyan]💬 Pergunta:[/bold cyan] {query}\n")
        
        try:
            # Executar agente
            console.print("[yellow]🤖 Processando com ADK Agent...[/yellow]\n")
            
            response = self.agent.run(query)
            
            # Extrair resposta
            if hasattr(response, 'text'):
                answer = response.text
            elif isinstance(response, str):
                answer = response
            else:
                answer = str(response)
            
            # Mostrar resposta raw se solicitado
            if show_raw:
                console.print("[bold]🔍 Resposta Raw:[/bold]")
                console.print(response)
                console.print()
            
            # Exibir resposta formatada
            console.print("[bold green]✅ Resposta:[/bold green]\n")
            console.print(Panel(
                Markdown(answer),
                title="[bold]Assistente de Compliance (ADK)[/bold]",
                border_style="green",
                box=box.ROUNDED
            ))
            console.print()
            
            return {
                "query": query,
                "answer": answer,
                "raw_response": response,
                "model": MODEL_NAME
            }
            
        except Exception as e:
            console.print(f"[red]❌ Erro ao processar: {e}[/red]\n")
            import traceback
            traceback.print_exc()
            
            return {
                "query": query,
                "answer": f"Erro ao processar: {e}",
                "error": str(e)
            }
    
    def chat(self):
        """
        Inicia um chat interativo com o agente.
        """
        console.print("\n[bold blue]💬 Chat com Assistente de Compliance (ADK)[/bold blue]\n")
        console.print("[yellow]Digite suas perguntas sobre compliance (ou 'sair' para encerrar)[/yellow]")
        console.print("[yellow]Comandos especiais:[/yellow]")
        console.print("  • [cyan]'raw'[/cyan] - Mostra resposta raw do próximo query")
        console.print("  • [cyan]'ajuda'[/cyan] - Mostra exemplos de perguntas")
        console.print("  • [cyan]'sair'[/cyan] - Encerra o chat\n")
        
        show_raw = False
        
        while True:
            try:
                query = input("\n💬 Você: ").strip()
                
                if not query:
                    continue
                
                # Comandos especiais
                if query.lower() in ['sair', 'exit', 'quit']:
                    console.print("\n[green]👋 Até logo![/green]\n")
                    break
                
                if query.lower() == 'raw':
                    show_raw = True
                    console.print("[yellow]Modo raw ativado para próxima pergunta[/yellow]")
                    continue
                
                if query.lower() in ['ajuda', 'help']:
                    self._show_help()
                    continue
                
                # Processar pergunta
                self.ask(query, show_raw=show_raw)
                show_raw = False  # Reset após uso
                
            except KeyboardInterrupt:
                console.print("\n\n[green]👋 Chat encerrado![/green]\n")
                break
            except Exception as e:
                console.print(f"\n[red]❌ Erro: {e}[/red]\n")
    
    def _show_help(self):
        """Mostra exemplos de perguntas."""
        help_text = """
**Exemplos de perguntas:**

1. "Qual é a política de reembolso de despesas?"
2. "Posso usar dinheiro da empresa para fins pessoais?"
3. "Quais são as regras sobre presentes e brindes?"
4. "O que acontece se eu violar as políticas?"
5. "Busque informações sobre 'Michael Scott'"
6. "Me dê um resumo das políticas disponíveis"
"""
        console.print(Panel(help_text, title="[bold cyan]Ajuda[/bold cyan]", border_style="cyan"))


def main():
    """Função principal para testar o agente ADK."""
    console.print("\n[bold blue]🧪 Testando Agente ADK de Compliance[/bold blue]\n")
    
    # Inicializar agente
    agent = ADKComplianceAgent()
    
    # Perguntas de teste
    test_queries = [
        "Qual é a política de reembolso de despesas?",
        "Posso usar dinheiro da empresa para fins pessoais?",
        "Me dê um resumo das políticas disponíveis"
    ]
    
    console.print("[bold]🔍 Testando com perguntas de exemplo:[/bold]\n")
    
    for i, query in enumerate(test_queries, 1):
        console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
        console.print(f"[bold]Teste {i}/{len(test_queries)}[/bold]\n")
        
        agent.ask(query, show_raw=False)
        
        if i < len(test_queries):
            input("\n[yellow]Pressione Enter para próxima pergunta...[/yellow]")
    
    # Oferecer chat interativo
    console.print("\n[bold yellow]Quer iniciar um chat interativo? (s/n)[/bold yellow]")
    if input().lower() == 's':
        agent.chat()


if __name__ == "__main__":
    main()
