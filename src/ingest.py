import google.generativeai as genai
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from rich.console import Console
from rich.progress import track
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import (
    GOOGLE_API_KEY,
    COMPLIANCE_FILE,
    VECTOR_STORE_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL
)

console = Console()

class DocumentIngestion:
    """Ingestão de documentos."""
    
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        
        ## Utilizaremos ChromaDB como vector store
        ## por ser simples e eficiente para rodar localmente
        self.chroma_client = chromadb.PersistentClient(
            path=str(VECTOR_STORE_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection_name = "compliance_policies"
        
        ## Aqui eu pedi para o GPT deixar a CLI mais bonitinha com o Rich
        console.print("[bold green]✅ Sistema de ingestão inicializado[/bold green]")
    
    def load_document(self, file_path: Path) -> str:
        """
        Carrega o conteúdo do documento.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            Conteúdo do arquivo como string
        """
        console.print(f"[cyan]📄 Carregando documento: {file_path.name}[/cyan]")
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        console.print(f"[green]✅ Documento carregado: {len(content)} caracteres[/green]")
        return content
    
    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, 
                   overlap: int = CHUNK_OVERLAP) -> List[Dict[str, str]]:
        """
        Divide o texto em chunks com overlap.
        
        Args:
            text: Texto completo
            chunk_size: Tamanho aproximado de cada chunk (em caracteres)
            overlap: Quantidade de caracteres de sobreposição
            
        Returns:
            Lista de dicionários com chunks e metadados
        """
        console.print(f"[cyan]✂️  Dividindo texto em chunks (tamanho: {chunk_size}, overlap: {overlap})[/cyan]")
        
        # Dividir por parágrafos primeiro
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for para in paragraphs:
            # Se adicionar o parágrafo não ultrapassar o limite
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                # Salvar chunk atual se não estiver vazio
                if current_chunk.strip():
                    chunks.append({
                        'id': f'chunk_{chunk_id}',
                        'text': current_chunk.strip(),
                        'metadata': {
                            'chunk_id': chunk_id,
                            'source': 'politica_compliance.txt'
                        }
                    })
                    chunk_id += 1
                
                ## Começar novo chunk com overlap
                ## Pegar últimas palavras do chunk anterior
                words = current_chunk.split()
                overlap_text = ' '.join(words[-overlap:]) if len(words) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + para + "\n\n"

        ## Por fim, adiciona o último chunk        
        if current_chunk.strip():
            chunks.append({
                'id': f'chunk_{chunk_id}',
                'text': current_chunk.strip(),
                'metadata': {
                    'chunk_id': chunk_id,
                    'source': 'politica_compliance.txt'
                }
            })
        
        console.print(f"[green]✅ Texto dividido em {len(chunks)} chunks[/green]")
        return chunks
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos usando Gemini.
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de embeddings (vetores)
        """
        console.print(f"[cyan]🧮 Gerando embeddings para {len(texts)} chunks...[/cyan]")
        
        embeddings = []
        
        batch_size = 10
        
        for i in track(range(0, len(texts), batch_size), description="Gerando embeddings"):
            batch = texts[i:i + batch_size]
            
            try:
                for text in batch:
                    result = genai.embed_content(
                        model=EMBEDDING_MODEL,
                        content=text,
                        task_type="retrieval_document"
                    )
                    embeddings.append(result['embedding'])
                
                ## Esse delay serve para evitar rate limits
                time.sleep(0.5)
                
            except Exception as e:
                console.print(f"[red]❌ Erro ao gerar embeddings: {e}[/red]")
                raise
        
        console.print(f"[green]✅ {len(embeddings)} embeddings gerados[/green]")
        return embeddings
    
    def store_in_vectordb(self, chunks: List[Dict[str, str]], embeddings: List[List[float]]):
        """
        Armazena chunks e embeddings no ChromaDB.
        
        Args:
            chunks: Lista de chunks com metadados
            embeddings: Lista de embeddings correspondentes
        """
        console.print(f"[cyan]💾 Armazenando no vector store...[/cyan]")
        
        ## Deletar coleção existente se houver
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            console.print("[yellow]⚠️  Coleção existente deletada[/yellow]")
        except:
            pass
        
        ## Cria nova coleção
        collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"description": "Políticas de compliance da Dunder Mifflin", "hnsw:space": "cosine"} ## similaridade de cosseno
        )
        
        ids = [chunk['id'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        console.print(f"[bold green]✅ {len(chunks)} chunks armazenados com sucesso![/bold green]")

    def chunk_text_recursive(self, text: str, chunk_size: int = CHUNK_SIZE, 
                         overlap: int = CHUNK_OVERLAP) -> List[Dict[str, str]]:
        """
        Divide o texto recursivamente, tentando manter estrutura semântica.
        
        Hierarquia de separadores:
        1. Seções (==== ou ----)
        2. Parágrafos duplos (\n\n)
        3. Parágrafos simples (\n)
        4. Sentenças (. ! ?)
        5. Palavras (espaço)
        """
        
        console.print(f"[cyan]✂️  Chunking recursivo (tamanho: {chunk_size}, overlap: {overlap})[/cyan]")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=[
                "\n==============================================================================",
                "\n\n",
                "\n",
                ". ",
                "! ",
                "? ",
                " ",
                ""
            ]
        )
        
        texts = text_splitter.split_text(text)
        
        chunks = []
        for i, chunk_text in enumerate(texts):
            chunks.append({
                'id': f'chunk_{i}',
                'text': chunk_text,
                'metadata': {
                    'chunk_id': i,
                    'source': 'politica_compliance.txt',
                    'char_count': len(chunk_text)
                }
            })
        
        console.print(f"[green]✅ Texto dividido em {len(chunks)} chunks[/green]")
        
        if len(chunks) > 1:
            console.print("\n[yellow]🔍 Verificando overlap:[/yellow]")
            for i in range(min(3, len(chunks) - 1)):
                chunk_end = chunks[i]['text'][-50:]
                chunk_start = chunks[i+1]['text'][:50]
                
                end_words = set(chunk_end.split())
                start_words = set(chunk_start.split())
                common_words = end_words & start_words
                
                console.print(f"  Chunks {i}-{i+1}: {len(common_words)} palavras em comum")
        
        return chunks
    
    def ingest(self, file_path: Path = COMPLIANCE_FILE, method: str = 'chunk_text'):
        """
        Pipeline completo de ingestão.
        
        Args:
            file_path: Caminho para o arquivo a ser ingerido
        """
        console.print("\n[bold blue]🚀 Iniciando pipeline de ingestão...[/bold blue]\n")
        
        try:
            ## 1. Carregar documento
            content = self.load_document(file_path)
            
            ## 2. Dividir em chunks
            if method == 'chunk_text':
                chunks = self.chunk_text(content)
            elif method == 'chunk_text_recursive':
                chunks = self.chunk_text_recursive(content)
            else:
                raise ValueError(f"Método de chunking desconhecido: {method}")
            
            ## 3. Gerar embeddings
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.generate_embeddings(texts)
            
            ## 4. Armazenar no vector store
            self.store_in_vectordb(chunks, embeddings)
            
            console.print("\n[bold green]🎉 Ingestão concluída com sucesso![/bold green]\n")
            
            ## Estatísticas
            console.print("[bold]📊 Estatísticas:[/bold]")
            console.print(f"  • Total de chunks: {len(chunks)}")
            console.print(f"  • Tamanho médio dos chunks: {sum(len(c['text']) for c in chunks) // len(chunks)} caracteres")
            console.print(f"  • Vector store: {VECTOR_STORE_DIR}")
            
        except Exception as e:
            console.print(f"\n[bold red]❌ Erro durante a ingestão: {e}[/bold red]\n")
            raise

def main():
    ingestion = DocumentIngestion()
    ingestion.ingest(file_path=COMPLIANCE_FILE, method='chunk_text_recursive')

if __name__ == "__main__":
    main()
