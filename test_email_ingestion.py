# test_email_ingestion.py
import google.generativeai as genai
import chromadb
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.config import (
    VECTOR_STORE_DIR,
    EMBEDDING_MODEL,
    GOOGLE_API_KEY
)

console = Console()


def test_email_collection():
    """Testa a coleção de emails no ChromaDB."""
    
    # Conectar
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    
    # Listar coleções
    collections = client.list_collections()
    console.print(f"\n[cyan]📚 Coleções disponíveis:[/cyan]")
    for col in collections:
        console.print(f"   - {col.name}")
    
    # Acessar coleção de emails
    try:
        collection = client.get_collection(name="emails")
    except:
        console.print("[red]❌ Coleção 'internal_emails' não encontrada![/red]")
        console.print("[yellow]Execute: python -m src.conspiracy.ingest_emails[/yellow]")
        return
    
    # Estatísticas
    total = collection.count()
    console.print(f"\n[green]✅ Coleção 'internal_emails' encontrada![/green]")
    console.print(f"[cyan]Total de emails: {total}[/cyan]\n")
    
    # Pegar alguns emails
    results = collection.get(limit=5, include=["documents", "metadatas"])
    
    # Mostrar em tabela
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=12)
    table.add_column("De", style="yellow", width=25)
    table.add_column("Para", style="green", width=25)
    table.add_column("Assunto", style="blue", width=35)
    table.add_column("Flags", style="red", width=15)
    
    for i, metadata in enumerate(results['metadatas']):
        flags = []
        if metadata.get('is_from_michael'):
            flags.append("🎯 Michael")
        if metadata.get('mentions_toby'):
            flags.append("👤 Toby")
        
        table.add_row(
            metadata['email_id'],
            metadata['from_name'][:25],
            metadata['to_names'].split(',')[0][:25],
            metadata['subject'][:35],
            " ".join(flags)
        )
    
    console.print(table)
    
    # Testar busca semântica
    console.print("\n[bold cyan]🔍 Teste de Busca Semântica:[/bold cyan]")
    console.print("[yellow]Query: 'emails onde Michael reclama de alguém'[/yellow]\n")
    
    
    genai.configure(api_key=GOOGLE_API_KEY)
    
    query = "emails onde Michael reclama de alguém"
    query_embedding = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=query,
        task_type="retrieval_query"
    )['embedding']
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )
    
    for i, (doc, meta, dist) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        console.print(Panel(
            f"[bold cyan]De:[/bold cyan] {meta['from_name']}\n"
            f"[bold green]Para:[/bold green] {meta['to_names']}\n"
            f"[bold yellow]Data:[/bold yellow] {meta['date']}\n"
            f"[bold magenta]Assunto:[/bold magenta] {meta['subject']}\n"
            f"[bold blue]Distância:[/bold blue] {dist:.4f}\n\n"
            f"[bold white]Preview:[/bold white]\n{meta['preview']}",
            title=f"[bold blue]Resultado {i+1}[/bold blue]",
            border_style="blue"
        ))
    
    # Testar filtros
    console.print("\n[bold cyan]🔍 Teste de Filtros:[/bold cyan]")
    console.print("[yellow]Filtro: is_from_michael=True AND mentions_toby=True[/yellow]\n")
    
    results = collection.get(
        where={
            "$and": [
                {"is_from_michael": True},
                {"mentions_toby": True}
            ]
        },
        limit=3,
        include=["metadatas"]
    )
    
    console.print(f"[green]Encontrados: {len(results['metadatas'])} emails[/green]\n")
    
    for meta in results['metadatas']:
        console.print(f"  📧 {meta['email_id']}: {meta['subject']}")


if __name__ == "__main__":
    test_email_collection()
