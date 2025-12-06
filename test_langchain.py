# test_langchain.py
"""Testa se LangChain foi instalado corretamente."""

from rich.console import Console

console = Console()

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    console.print("[green]✅ LangChain instalado com sucesso![/green]")
    
    # Testar o splitter
    text = """
    Este é um texto de teste.
    Vamos ver como o LangChain divide em chunks.
    
    Este é um novo parágrafo.
    Com mais informações importantes.
    """
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=10,
        length_function=len,
    )
    
    chunks = splitter.split_text(text)
    
    console.print(f"\n[cyan]Texto dividido em {len(chunks)} chunks:[/cyan]\n")
    
    for i, chunk in enumerate(chunks):
        console.print(f"[bold]Chunk {i}:[/bold]")
        console.print(f"{chunk}\n")
    
except ImportError as e:
    console.print(f"[red]❌ Erro ao importar LangChain: {e}[/red]")
    console.print("[yellow]Execute: pip install langchain langchain-text-splitters[/yellow]")