# test_ingest.py
"""
Script para testar o sistema de ingestão.
"""

from src.ingest import DocumentIngestion
from src.config import COMPLIANCE_FILE
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def test_ingestion():
    """Testa o pipeline de ingestão."""
    console.print("\n[bold cyan]🧪 Testando Sistema de Ingestão[/bold cyan]\n")
    
    # Verificar se arquivo existe
    if not COMPLIANCE_FILE.exists():
        console.print(f"[red]❌ Arquivo não encontrado: {COMPLIANCE_FILE}[/red]")
        console.print("[yellow]💡 Coloque o arquivo politica_compliance.txt na pasta data/[/yellow]")
        return
    
    # Executar ingestão
    ingestion = DocumentIngestion()
    ingestion.ingest(file_path=COMPLIANCE_FILE, method='chunk_text_recursive')
    
    # Testar recuperação
    console.print("\n[bold cyan]🔍 Testando recuperação de chunks...[/bold cyan]\n")
    
    collection = ingestion.chroma_client.get_collection(name="compliance_policies")
    
    # Pegar TODOS os chunks
    results = collection.get()
    
    total_chunks = len(results['ids'])
    console.print(f"[green]✅ {total_chunks} chunks recuperados[/green]\n")
    
    # Criar tabela resumida
    table = Table(title="📋 Resumo dos Chunks", show_lines=True)
    table.add_column("ID", style="cyan", width=12)
    table.add_column("Tamanho", style="green", width=10)
    table.add_column("Preview (primeiros 100 chars)", style="white")
    
    for doc_id, text in zip(results['ids'], results['documents']):
        preview = text[:100].replace('\n', ' ') + "..."
        table.add_row(doc_id, f"{len(text)} chars", preview)
    
    console.print(table)
    
    # Perguntar se quer ver chunks completos
    console.print("\n[bold yellow]💡 Quer ver os chunks completos? (s/n)[/bold yellow]")
    resposta = input().lower()
    
    if resposta == 's':
        console.print("\n[bold blue]📄 Chunks Completos:[/bold blue]\n")
        
        for i, (doc_id, text, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
            # Criar painel para cada chunk
            panel = Panel(
                text,
                title=f"[bold]Chunk {i+1}/{total_chunks} - {doc_id}[/bold]",
                subtitle=f"[yellow]{metadata}[/yellow]",
                border_style="cyan"
            )
            console.print(panel)
            console.print()
    
    # Estatísticas
    console.print("\n[bold]📊 Estatísticas:[/bold]")
    console.print(f"  • Total de chunks: {total_chunks}")
    
    if results['documents']:
        avg_length = sum(len(doc) for doc in results['documents']) / len(results['documents'])
        min_length = min(len(doc) for doc in results['documents'])
        max_length = max(len(doc) for doc in results['documents'])
        
        console.print(f"  • Tamanho médio: {avg_length:.0f} caracteres")
        console.print(f"  • Menor chunk: {min_length} caracteres")
        console.print(f"  • Maior chunk: {max_length} caracteres")


if __name__ == "__main__":
    test_ingestion()