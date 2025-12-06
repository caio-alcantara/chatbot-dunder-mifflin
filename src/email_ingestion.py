# src/conspiracy/ingest_emails.py

import os
from dotenv import load_dotenv
import chromadb
import google.generativeai as genai
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from .config import (
    VECTOR_STORE_DIR,
    EMBEDDING_MODEL,
    GOOGLE_API_KEY
)
from .email_parser import EmailParser

console = Console()
load_dotenv()


class EmailIngestion:
    """Ingestão de emails no ChromaDB."""
    
    COLLECTION_NAME = "emails"
    
    def __init__(self):
        # Configurar Google AI
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Conectar ao ChromaDB
        self.client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
        
        console.print(f"[green]✅ Conectado ao ChromaDB: {str(VECTOR_STORE_DIR)}[/green]")
    
    def ingest(self, file_path: str, reset: bool = False):
        """
        Pipeline completo de ingestão.
        
        Args:
            file_path: Caminho para emails_internos.txt
            reset: Se True, deleta coleção existente
        """
        console.print(Panel(
            "[bold cyan]Iniciando Ingestão de Emails[/bold cyan]",
            border_style="cyan"
        ))
        
        # 1. Parse dos emails
        parser = EmailParser()
        emails = parser.parse_dump(file_path)
        
        if not emails:
            console.print("[red]❌ Nenhum email encontrado![/red]")
            return
        
        # Estatísticas
        stats = parser.get_statistics()
        console.print(f"\n[cyan]📊 Estatísticas:[/cyan]")
        console.print(f"   Total: {stats['total_emails']}")
        console.print(f"   De Michael: {stats['from_michael']}")
        console.print(f"   Mencionam Toby: {stats['mentions_toby']}")
        console.print(f"   Michael → Toby: {stats['from_michael_about_toby']}\n")
        
        # 2. Criar/resetar coleção
        collection = self._get_or_create_collection(reset)
        
        # 3. Gerar embeddings e armazenar
        self._store_emails(collection, emails)
        
        console.print(Panel(
            f"[bold green]✅ Ingestão Concluída![/bold green]\n\n"
            f"[cyan]Coleção:[/cyan] {self.COLLECTION_NAME}\n"
            f"[cyan]Total de Emails:[/cyan] {len(emails)}\n"
            f"[cyan]Embedding Model:[/cyan] {EMBEDDING_MODEL}",
            border_style="green"
        ))
    
    def _get_or_create_collection(self, reset: bool):
        """Cria ou retorna coleção existente."""
        if reset:
            try:
                self.client.delete_collection(name=self.COLLECTION_NAME)
                console.print(f"[yellow]🗑️  Coleção '{self.COLLECTION_NAME}' deletada[/yellow]")
            except:
                pass
        
        collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",  # Usar cosine similarity
                "description": "Internal emails from Dunder Mifflin"
            }
        )
        
        console.print(f"[green]✅ Coleção '{self.COLLECTION_NAME}' pronta[/green]\n")
        
        return collection
    
    def _store_emails(self, collection, emails):
        """Gera embeddings e armazena no ChromaDB."""
        console.print("[cyan]🔄 Gerando embeddings e armazenando...[/cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task(
                f"Processando {len(emails)} emails...",
                total=len(emails)
            )
            
            # Processar em batches
            batch_size = 100
            for i in range(0, len(emails), batch_size):
                batch = emails[i:i + batch_size]
                
                # Preparar dados
                ids = []
                documents = []
                metadatas = []
                
                for email in batch:
                    email_id, document, metadata = email.to_chroma_format()
                    ids.append(email_id)
                    documents.append(document)
                    metadatas.append(metadata)
                
                # Gerar embeddings
                embeddings = self._generate_embeddings(documents)
                
                # Armazenar
                collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                
                progress.update(task, advance=len(batch))
        
        console.print(f"[green]✅ {len(emails)} emails armazenados com sucesso![/green]\n")
    
    def _generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Gera embeddings usando Gemini."""
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=texts,
            task_type="retrieval_document"
        )
        return result['embedding']


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingestão de emails no ChromaDB")
    parser.add_argument(
        "--file",
        type=str,
        default="data/emails.txt",
        help="Caminho para o dump de emails"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Resetar coleção existente"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        console.print(f"[red]❌ Arquivo não encontrado: {args.file}[/red]")
        return
    
    ingestion = EmailIngestion()
    ingestion.ingest(args.file, reset=args.reset)


if __name__ == "__main__":
    main()
