# test_email_retriever_improved.py

from src.email_retriever import EmailRetriever
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_improved_search():
    retriever = EmailRetriever()
    
    # Teste 1: Busca específica com filtro
    console.print("\n[bold cyan]🔍 Teste 1: Busca Melhorada[/bold cyan]\n")
    
    queries = [
        "problemas com o toby",
        "toby é o pior",
        "dwight e michael contra toby",
        "planos contra funcionários"
    ]
    
    for query in queries:
        console.print(f"[yellow]Query: '{query}'[/yellow]")
        
        results = retriever.search_emails_from_michael(
            query=query,
            top_k=3,
            max_distance=0.35  # Threshold mais rigoroso
        )
        
        if results:
            for email in results:
                console.print(f"  ✅ {email['subject']} (dist: {email['distance']:.3f})")
        else:
            console.print(f"  ❌ Nenhum resultado relevante")
        
        console.print()
    
    # Teste 2: Todos os emails de Michael sobre Toby
    console.print("\n[bold cyan]📧 Teste 2: TODOS os Emails Suspeitos[/bold cyan]\n")
    
    all_emails = retriever.get_all_emails_from_michael_about_toby()
    
    console.print(f"[green]Total: {len(all_emails)} emails[/green]\n")
    
    for email in all_emails:
        console.print(Panel(
            f"[bold yellow]Data:[/bold yellow] {email['date']}\n"
            f"[bold green]Para:[/bold green] {email['to_names']}\n"
            f"[bold magenta]Assunto:[/bold magenta] {email['subject']}\n\n"
            f"[bold white]Body:[/bold white]\n{email['body'][:200]}...",
            title=f"[bold red]{email['email_id']}[/bold red]",
            border_style="red"
        ))

if __name__ == "__main__":
    test_improved_search()