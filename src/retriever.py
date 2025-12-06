# src/retriever.py
"""
Sistema de recuperação (retrieval) de chunks relevantes.
Busca os chunks mais similares a uma query usando embeddings.
"""

import google.generativeai as genai
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.config import (
    GOOGLE_API_KEY,
    VECTOR_STORE_DIR,
    EMBEDDING_MODEL,
    TOP_K_RESULTS
)

console = Console()


class ComplianceRetriever:
    """Classe responsável pela recuperação de chunks relevantes (Singleton)."""
    
    _instance = None
    _chroma_client = None
    _collection = None
    _initialized = False
    
    def __new__(cls, collection_name: str = "compliance_policies"):
        """Garante que apenas uma instância seja criada (Singleton)."""
        if cls._instance is None:
            cls._instance = super(ComplianceRetriever, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, collection_name: str = "compliance_policies"):
        """
        Inicializa o retriever (apenas uma vez).
        
        Args:
            collection_name: Nome da coleção no ChromaDB
        """
        # Se já foi inicializado, reutiliza as instâncias
        if ComplianceRetriever._initialized:
            self.chroma_client = ComplianceRetriever._chroma_client
            self.collection = ComplianceRetriever._collection
            return
        
        # Primeira inicialização
        genai.configure(api_key=GOOGLE_API_KEY)
        
        ComplianceRetriever._chroma_client = chromadb.PersistentClient(
            path=str(VECTOR_STORE_DIR),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        try:
            ComplianceRetriever._collection = ComplianceRetriever._chroma_client.get_collection(
                name=collection_name
            )
            
            metadata = ComplianceRetriever._collection.metadata
            distance_metric = metadata.get('hnsw:space', 'l2') 
            
            console.print(f"[green]✅ Coleção '{collection_name}' carregada[/green]")
            console.print(f"[cyan]📏 Métrica de distância: {distance_metric.upper()}[/cyan]")
            
            count = ComplianceRetriever._collection.count()
            console.print(f"[cyan]📊 Total de chunks disponíveis: {count}[/cyan]")
            
            ComplianceRetriever._initialized = True
            
        except Exception as e:
            console.print(f"[red]❌ Erro ao carregar coleção: {e}[/red]")
            console.print("[yellow]💡 Execute a ingestão primeiro: python -m src.ingest[/yellow]")
            raise
        
        # Atribuir às variáveis de instância
        self.chroma_client = ComplianceRetriever._chroma_client
        self.collection = ComplianceRetriever._collection
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Gera embedding para a query do usuário.
        
        Args:
            query: Pergunta do usuário
            
        Returns:
            Embedding da query (vetor)
        """
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=query,
                task_type="retrieval_query" 
            )
            return result['embedding']
        
        except Exception as e:
            console.print(f"[red]❌ Erro ao gerar embedding: {e}[/red]")
            raise
    
    def retrieve(self, query: str, top_k: int = TOP_K_RESULTS, 
                 show_details: bool = False) -> List[Dict]:
        """
        Recupera os chunks mais relevantes para a query.
        
        Args:
            query: Pergunta do usuário
            top_k: Número de chunks a recuperar
            show_details: Se True, mostra detalhes da busca
            
        Returns:
            Lista de dicionários com chunks e metadados
        """
        if show_details:
            console.print(f"\n[cyan]🔍 Buscando chunks relevantes para:[/cyan]")
            console.print(f"[bold]'{query}'[/bold]\n")
        
        ## 1. Gerar embedding da query
        query_embedding = self.generate_query_embedding(query)
        
        if show_details:
            console.print(f"[green]✅ Embedding da query gerado ({len(query_embedding)} dimensões)[/green]")
        
        ## 2. Buscar chunks similares no ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        
        ## 3. Formatar resultados
        retrieved_chunks = []
        
        for i in range(len(results['ids'][0])):
            chunk = {
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'similarity_score': 1 - results['distances'][0][i]  # Converter distância em similaridade
            }
            retrieved_chunks.append(chunk)
        
        if show_details:
            console.print(f"[green]✅ {len(retrieved_chunks)} chunks recuperados[/green]\n")
            self._display_results(query, retrieved_chunks)
        
        return retrieved_chunks
    
    def _display_results(self, query: str, chunks: List[Dict]):
        """
        Exibe os resultados da busca de forma visual.
        
        Args:
            query: Query original
            chunks: Chunks recuperados
        """
        table = Table(title=f"🔍 Resultados para: '{query}'", show_lines=True)
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Chunk ID", style="yellow", width=12)
        table.add_column("Similaridade", style="green", width=12)
        table.add_column("Preview", style="white")
        
        for i, chunk in enumerate(chunks, 1):
            similarity = f"{chunk['similarity_score']:.2%}"
            preview = chunk['text'][:80].replace('\n', ' ') + "..."
            
            table.add_row(
                f"#{i}",
                chunk['id'],
                similarity,
                preview
            )
        
        console.print(table)
        console.print()
        
        console.print("[bold]📄 Chunks Completos:[/bold]\n")
        
        for i, chunk in enumerate(chunks, 1):
            panel = Panel(
                chunk['text'],
                title=f"[bold]Rank #{i} - {chunk['id']} (Similaridade: {chunk['similarity_score']:.2%})[/bold]",
                subtitle=f"[yellow]Metadados: {chunk['metadata']}[/yellow]",
                border_style="cyan" if i == 1 else "blue"
            )
            console.print(panel)
            console.print()
    
    def retrieve_with_context(self, query: str, top_k: int = TOP_K_RESULTS) -> str:
        """
        Recupera chunks e formata como contexto para o LLM.
        
        Args:
            query: Pergunta do usuário
            top_k: Número de chunks a recuperar
            
        Returns:
            String formatada com o contexto
        """
        chunks = self.retrieve(query, top_k=top_k, show_details=False)
        
        # Formatar contexto
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[TRECHO {i} - Relevância: {chunk['similarity_score']:.2%}]")
            context_parts.append(chunk['text'])
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        return context
    
    def search_by_keyword(self, keyword: str, case_sensitive: bool = False) -> List[Dict]:
        """
        Busca chunks que contenham uma palavra-chave específica.
        Útil para buscas exatas (não semânticas).
        
        Args:
            keyword: Palavra-chave a buscar
            case_sensitive: Se a busca deve ser case-sensitive
            
        Returns:
            Lista de chunks que contêm a palavra-chave
        """
        console.print(f"\n[cyan]🔎 Buscando palavra-chave: '{keyword}'[/cyan]\n")
        
        all_docs = self.collection.get()
        
        matching_chunks = []
        
        for i, (doc_id, text, metadata) in enumerate(zip(
            all_docs['ids'], 
            all_docs['documents'], 
            all_docs['metadatas']
        )):
            search_text = text if case_sensitive else text.lower()
            search_keyword = keyword if case_sensitive else keyword.lower()
            
            if search_keyword in search_text:
                matching_chunks.append({
                    'id': doc_id,
                    'text': text,
                    'metadata': metadata
                })
        
        console.print(f"[green]✅ {len(matching_chunks)} chunks encontrados com '{keyword}'[/green]\n")
        
        return matching_chunks
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict]:
        """
        Recupera um chunk específico pelo ID.
        
        Args:
            chunk_id: ID do chunk
            
        Returns:
            Dicionário com o chunk ou None se não encontrado
        """
        try:
            result = self.collection.get(ids=[chunk_id])
            
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'text': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            else:
                console.print(f"[yellow]⚠️  Chunk '{chunk_id}' não encontrado[/yellow]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Erro ao buscar chunk: {e}[/red]")
            return None


def main():
    """Função principal para testar o retriever."""
    console.print("\n[bold blue]🧪 Testando Sistema de Retrieval[/bold blue]\n")
    
    retriever = ComplianceRetriever()
    
    test_queries = [
        "Qual é a política de reembolso de despesas?",
        "Posso usar dinheiro da empresa para fins pessoais?",
        "Quais são as regras sobre presentes e brindes?",
        "O que acontece se eu violar as políticas de compliance?"
    ]
    
    console.print("[bold]🔍 Testando queries de exemplo:[/bold]\n")
    
    for i, query in enumerate(test_queries, 1):
        console.print(f"[bold cyan]{'='*80}[/bold cyan]")
        console.print(f"[bold]Query {i}/{len(test_queries)}:[/bold]")
        
        chunks = retriever.retrieve(query, top_k=3, show_details=True)
        
        input("\n[yellow]Pressione Enter para próxima query...[/yellow]\n")


if __name__ == "__main__":
    main()