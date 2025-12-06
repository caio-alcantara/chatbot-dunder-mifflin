# test_retriever.py
"""
Script para testar o sistema de retrieval com diferentes cenários.
"""

from src.retriever import ComplianceRetriever
from rich.console import Console

console = Console()


def test_semantic_search():
    """Testa busca semântica."""
    console.print("\n[bold blue]🧪 Teste 1: Busca Semântica[/bold blue]\n")
    
    retriever = ComplianceRetriever()
    
    # Queries semânticas (não usam palavras exatas do documento)
    queries = [
        "Posso gastar dinheiro da firma em coisas pessoais?",
        "Como funciona o reembolso de viagens?",
        "Quais são as consequências de quebrar as regras?",
    ]
    
    for query in queries:
        console.print(f"\n[cyan]Query: {query}[/cyan]")
        chunks = retriever.retrieve(query, top_k=2, show_details=True)
        input("\n[yellow]Enter para continuar...[/yellow]\n")


def test_keyword_search():
    """Testa busca por palavra-chave."""
    console.print("\n[bold blue]🧪 Teste 2: Busca por Palavra-Chave[/bold blue]\n")
    
    retriever = ComplianceRetriever()
    
    keywords = ["reembolso", "Michael Scott", "fraude"]
    
    for keyword in keywords:
        chunks = retriever.search_by_keyword(keyword)
        
        if chunks:
            console.print(f"[bold]Chunks com '{keyword}':[/bold]\n")
            for chunk in chunks[:2]:  # Mostrar só os 2 primeiros
                console.print(f"[yellow]{chunk['id']}:[/yellow]")
                console.print(f"{chunk['text'][:200]}...\n")


def test_context_generation():
    """Testa geração de contexto para LLM."""
    console.print("\n[bold blue]🧪 Teste 3: Geração de Contexto[/bold blue]\n")
    
    retriever = ComplianceRetriever()
    
    query = "Qual a política de reembolso?"
    
    console.print(f"[cyan]Query: {query}[/cyan]\n")
    
    context = retriever.retrieve_with_context(query, top_k=3)
    
    console.print("[bold]Contexto gerado para o LLM:[/bold]\n")
    console.print(f"[green]{context}[/green]")


def test_specific_chunk():
    """Testa recuperação de chunk específico."""
    console.print("\n[bold blue]🧪 Teste 4: Buscar Chunk por ID[/bold blue]\n")
    
    retriever = ComplianceRetriever()
    
    chunk_id = "chunk_0"
    
    chunk = retriever.get_chunk_by_id(chunk_id)
    
    if chunk:
        console.print(f"[bold]Chunk encontrado:[/bold]\n")
        console.print(f"[yellow]ID:[/yellow] {chunk['id']}")
        console.print(f"[yellow]Metadados:[/yellow] {chunk['metadata']}")
        console.print(f"[yellow]Texto:[/yellow]\n{chunk['text']}")


def interactive_test():
    """Teste interativo - usuário digita queries."""
    console.print("\n[bold blue]🧪 Teste Interativo[/bold blue]\n")
    
    retriever = ComplianceRetriever()
    
    console.print("[yellow]Digite suas perguntas sobre compliance (ou 'sair' para encerrar)[/yellow]\n")
    
    while True:
        query = input("\n💬 Sua pergunta: ").strip()
        
        if query.lower() in ['sair', 'exit', 'quit', '']:
            console.print("\n[green]👋 Até logo![/green]\n")
            break
        
        chunks = retriever.retrieve(query, top_k=3, show_details=True)


if __name__ == "__main__":
    # Executar todos os testes
    test_semantic_search()
    test_keyword_search()
    test_context_generation()
    test_specific_chunk()
    
    # Teste interativo (opcional)
    console.print("\n[bold yellow]Quer fazer um teste interativo? (s/n)[/bold yellow]")
    if input().lower() == 's':
        interactive_test()
