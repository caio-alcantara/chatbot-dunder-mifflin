# src/email_retriever.py

import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from typing import List, Dict, Optional
from rich.console import Console

from src.config import (
    VECTOR_STORE_DIR,
    EMBEDDING_MODEL,
    GOOGLE_API_KEY
)

console = Console()
load_dotenv()


class EmailRetriever:
    """Retriever de emails com busca semântica + filtros (Singleton)."""
    
    COLLECTION_NAME = "emails"
    
    _instance = None
    _client = None
    _collection = None
    _initialized = False
    
    def __new__(cls):
        """Garante que apenas uma instância seja criada (Singleton)."""
        if cls._instance is None:
            cls._instance = super(EmailRetriever, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa o email retriever (apenas uma vez)."""
        # Se já foi inicializado, reutiliza as instâncias
        if EmailRetriever._initialized:
            self.client = EmailRetriever._client
            self.collection = EmailRetriever._collection
            return
        
        # Primeira inicialização
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Conectar ao ChromaDB com as mesmas configurações
        EmailRetriever._client = chromadb.PersistentClient(
            path=str(VECTOR_STORE_DIR),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        try:
            EmailRetriever._collection = EmailRetriever._client.get_collection(
                name=self.COLLECTION_NAME
            )
            console.print(f"[green]✅ Conectado à coleção '{self.COLLECTION_NAME}'[/green]")
            console.print(f"[cyan]   Total de emails: {EmailRetriever._collection.count()}[/cyan]\n")
            
            EmailRetriever._initialized = True
            
        except Exception as e:
            console.print(f"[red]❌ Erro ao conectar: {e}[/red]")
            console.print(f"[yellow]Execute: python -m src.conspiracy.ingest_emails[/yellow]")
            raise
        
        # Atribuir às variáveis de instância
        self.client = EmailRetriever._client
        self.collection = EmailRetriever._collection
    
    def search_emails_from_michael(
        self,
        query: str,
        top_k: int = 10,
        max_distance: float = 0.4
    ) -> List[Dict]:
        """
        Busca semântica em emails DE Michael Scott.
        
        Args:
            query: Query em linguagem natural
            top_k: Número de resultados
            max_distance: Distância máxima (0-1, menor = mais similar)
        
        Returns:
            Lista de emails relevantes
        """
        console.print(f"[cyan]🔍 Buscando emails DE Michael: '{query}'[/cyan]\n")
        
        # Gerar embedding da query
        query_embedding = self._generate_query_embedding(query)
        
        # Busca com filtro
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"is_from_michael": True},  # ✅ FILTRO
            include=["documents", "metadatas", "distances"]
        )
        
        # Filtrar por distância
        filtered_results = self._filter_by_distance(results, max_distance)
        
        console.print(f"[green]✅ Encontrados {len(filtered_results)} emails relevantes[/green]\n")
        
        return filtered_results
    
    def search_emails_about_toby(
        self,
        query: str,
        top_k: int = 10,
        max_distance: float = 0.4
    ) -> List[Dict]:
        """
        Busca semântica em emails que mencionam Toby.
        """
        console.print(f"[cyan]🔍 Buscando emails SOBRE Toby: '{query}'[/cyan]\n")
        
        query_embedding = self._generate_query_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"mentions_toby": True},  # ✅ FILTRO
            include=["documents", "metadatas", "distances"]
        )
        
        filtered_results = self._filter_by_distance(results, max_distance)
        
        console.print(f"[green]✅ Encontrados {len(filtered_results)} emails relevantes[/green]\n")
        
        return filtered_results
    
    def search_emails_from_michael_about_toby(
        self,
        query: str,
        top_k: int = 10,
        max_distance: float = 0.4
    ) -> List[Dict]:
        """
        Busca semântica em emails DE Michael SOBRE Toby.
        
        ⭐ CORE DA INVESTIGAÇÃO DE CONSPIRAÇÃO
        """
        console.print(f"[cyan]🔍 Buscando emails DE Michael SOBRE Toby: '{query}'[/cyan]\n")
        
        query_embedding = self._generate_query_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "$and": [
                    {"is_from_michael": True},
                    {"mentions_toby": True}
                ]
            },  # ✅ FILTRO COMBINADO
            include=["documents", "metadatas", "distances"]
        )
        
        filtered_results = self._filter_by_distance(results, max_distance)
        
        console.print(f"[green]✅ Encontrados {len(filtered_results)} emails relevantes[/green]\n")
        
        return filtered_results
    
    def search_by_keyword(
        self,
        keyword: str,
        from_michael: bool = False,
        about_toby: bool = False
    ) -> List[Dict]:
        """
        Busca exata por palavra-chave no corpo do email.
        
        Args:
            keyword: Palavra-chave a buscar
            from_michael: Se True, filtra emails de Michael
            about_toby: Se True, filtra emails sobre Toby
        """
        console.print(f"[cyan]🔍 Buscando keyword: '{keyword}'[/cyan]\n")
        
        # Construir filtro
        where_filter = {}
        if from_michael:
            where_filter["is_from_michael"] = True
        if about_toby:
            where_filter["mentions_toby"] = True
        
        # Buscar todos os emails com filtro
        if where_filter:
            results = self.collection.get(
                where=where_filter,
                include=["documents", "metadatas"]
            )
        else:
            results = self.collection.get(
                include=["documents", "metadatas"]
            )
        
        # Filtrar por keyword no body
        filtered = []
        keyword_lower = keyword.lower()
        
        for i, metadata in enumerate(results['metadatas']):
            body = metadata.get('body', '').lower()
            subject = metadata.get('subject', '').lower()
            
            if keyword_lower in body or keyword_lower in subject:
                filtered.append({
                    'email_id': metadata['email_id'],
                    'from': metadata['from'],
                    'from_name': metadata['from_name'],
                    'to': metadata['to'],
                    'to_names': metadata['to_names'],
                    'date': metadata['date'],
                    'subject': metadata['subject'],
                    'body': metadata['body'],
                    'preview': metadata['preview'],
                    'is_from_michael': metadata['is_from_michael'],
                    'mentions_toby': metadata['mentions_toby']
                })
        
        console.print(f"[green]✅ Encontrados {len(filtered)} emails com '{keyword}'[/green]\n")
        
        return filtered
    
    def get_all_emails_from_michael_about_toby(self) -> List[Dict]:
        """
        Retorna TODOS os emails de Michael sobre Toby (sem busca semântica).
        
        Útil para análise completa.
        """
        console.print(f"[cyan]📧 Buscando TODOS os emails de Michael sobre Toby[/cyan]\n")
        
        results = self.collection.get(
            where={
                "$and": [
                    {"is_from_michael": True},
                    {"mentions_toby": True}
                ]
            },
            include=["metadatas"]
        )
        
        emails = []
        for metadata in results['metadatas']:
            emails.append({
                'email_id': metadata['email_id'],
                'from': metadata['from'],
                'from_name': metadata['from_name'],
                'to': metadata['to'],
                'to_names': metadata['to_names'],
                'date': metadata['date'],
                'timestamp': metadata['timestamp'],
                'subject': metadata['subject'],
                'body': metadata['body'],
                'preview': metadata['preview'],
                'is_from_michael': metadata['is_from_michael'],
                'mentions_toby': metadata['mentions_toby'],
                'mentions_toby_keywords': metadata.get('mentions_toby_keywords', '')
            })
        
        # Ordenar por data
        emails.sort(key=lambda x: x['timestamp'])
        
        console.print(f"[green]✅ Encontrados {len(emails)} emails[/green]\n")
        
        return emails
    
    def search_emails_with_financial_fraud(self, query: str, top_k: int = 10, max_distance: float = 0.4) -> List[Dict]:
        """
        Busca semântica em emails relacionados a fraudes financeiras.
        
        Args:
            query: Query em linguagem natural
            top_k: Número de resultados
            max_distance: Distância máxima (0-1, menor = mais similar)
        
        Returns:
            Lista de emails relevantes
        """
        console.print(f"[cyan]🔍 Buscando emails sobre fraude financeira: '{query}'[/cyan]\n")
        
        # Gerar embedding da query
        query_embedding = self._generate_query_embedding(query)
        
        # Busca com filtro
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Filtrar por distância
        filtered_results = self._filter_by_distance(results, max_distance)
        
        console.print(f"[green]✅ Encontrados {len(filtered_results)} emails relevantes sobre fraude financeira[/green]\n")
        
        return filtered_results
    
    def _generate_query_embedding(self, query: str) -> List[float]:
        """Gera embedding para query."""
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=query,
            task_type="retrieval_query"
        )
        return result['embedding']
    
    def _filter_by_distance(
        self,
        results: Dict,
        max_distance: float
    ) -> List[Dict]:
        """
        Filtra resultados por distância máxima.
        
        Args:
            results: Resultados do ChromaDB
            max_distance: Distância máxima (0-1)
        
        Returns:
            Lista de emails filtrados
        """
        filtered = []
        
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            if dist <= max_distance:
                filtered.append({
                    'email_id': meta['email_id'],
                    'from': meta['from'],
                    'from_name': meta['from_name'],
                    'to': meta['to'],
                    'to_names': meta['to_names'],
                    'date': meta['date'],
                    'subject': meta['subject'],
                    'body': meta['body'],
                    'preview': meta['preview'],
                    'distance': dist,
                    'is_from_michael': meta['is_from_michael'],
                    'mentions_toby': meta['mentions_toby']
                })
        
        return filtered

    # ============================================================
    # 📌 Função 1 — Busca por palavras-chave financeiras
    # ============================================================

    def search_financial_keywords(
        self,
        keywords: Optional[List[str]] = None,
        top_k: int = 20
    ) -> List[Dict]:

        if keywords is None:
            keywords = [
                "reembolso", "nota fiscal", "despesa", "pagamento",
                "cartão corporativo", "corporate card", "expense",
                "caixa", "adiantamento", "verba", "budget", "gasto",
                "almoço", "refeição", "gift", "bribe", "spa", "hotel",
                "travel expense", "entertainment expense"
            ]

        console.print(f"[cyan]🔍 Buscando emails por keywords financeiras...[/cyan]\n")

        results = self.collection.get(include=["documents", "metadatas"])

        matched = []
        for metadata in results["metadatas"]:
            body = metadata.get("body", "").lower()
            subject = metadata.get("subject", "").lower()

            if any(k.lower() in body or k.lower() in subject for k in keywords):
                matched.append(metadata)

            if len(matched) >= top_k:
                break

        console.print(f"[green]✅ Encontrados {len(matched)} emails com termos financeiros[/green]\n")
        return matched


    # ============================================================
    # 📌 Função 2 — Buscar emails marcados como is_financial=True
    #     (se você armazenar esse metadado no ingest)
    # ============================================================

    def search_emails_with_financial_metadata(self) -> List[Dict]:
        console.print(f"[cyan]🔍 Buscando emails com metadado financeiro[/cyan]\n")

        try:
            results = self.collection.get(
                where={"is_financial": True},
                include=["documents", "metadatas"]
            )
        except:
            console.print("[yellow]⚠️ Nenhum metadado 'is_financial' encontrado[/yellow]")
            return []

        emails = results.get("metadatas", [])
        console.print(f"[green]✅ Encontrados {len(emails)} emails marcados como financeiros[/green]\n")
        return emails


    # ============================================================
    # 📌 Função 3 — Filtro semântico com LLM: confirma SE É fraude
    # ============================================================

    def semantic_filter_financial_only(
        self,
        emails: List[Dict],
        llm_model: str = "gemini-1.5-pro"
    ) -> List[Dict]:

        filtered = []

        console.print(f"[cyan]🤖 Aplicando filtro semântico para validar fraude financeira...[/cyan]")

        for email in emails:
            text = f"Subject: {email.get('subject', '')}\n{email.get('body', '')}"

            prompt = f"""
            Você é um classificador de segurança corporativa. 
            Dado o email abaixo, responda APENAS 'true' se houver violação financeira clara, 
            como: uso indevido de verba, reembolso fraudulento, gastos pessoais pagos pela empresa,
            despesas sem aprovação, presentes/subornos, irregularidades de caixa.

            Se NÃO houver violação financeira explícita, responda 'false'.

            Email:
            {text}

            Resposta:
            """

            try:
                result = genai.generate_text(model=llm_model, prompt=prompt)
                output = result.result.strip().lower()
            except:
                continue

            if output.startswith("true"):
                filtered.append(email)

        console.print(f"[green]🎯 Emails confirmados como fraude financeira: {len(filtered)}[/green]\n")
        return filtered

# ============================================================================
# TESTE DO RETRIEVER
# ============================================================================

if __name__ == "__main__":
    from rich.panel import Panel
    from rich.table import Table
    
    retriever = EmailRetriever()
    
    # Teste 1: Busca semântica COM filtro
    console.print(Panel(
        "[bold cyan]Teste 1: Busca Semântica COM Filtro[/bold cyan]",
        border_style="cyan"
    ))
    
    results = retriever.search_emails_from_michael(
        query="reclamações sobre colegas de trabalho",
        top_k=5,
        max_distance=0.35
    )
    
    for i, email in enumerate(results, 1):
        console.print(Panel(
            f"[bold cyan]De:[/bold cyan] {email['from_name']}\n"
            f"[bold green]Para:[/bold green] {email['to_names']}\n"
            f"[bold yellow]Data:[/bold yellow] {email['date']}\n"
            f"[bold magenta]Assunto:[/bold magenta] {email['subject']}\n"
            f"[bold blue]Distância:[/bold blue] {email['distance']:.4f}\n\n"
            f"[bold white]Preview:[/bold white]\n{email['preview']}",
            title=f"[bold blue]Resultado {i}[/bold blue]",
            border_style="blue"
        ))
    
    # Teste 2: Emails de Michael sobre Toby
    console.print(Panel(
        "[bold cyan]Teste 2: Emails DE Michael SOBRE Toby[/bold cyan]",
        border_style="cyan"
    ))
    
    results = retriever.search_emails_from_michael_about_toby(
        query="problemas com Toby",
        top_k=5,
        max_distance=0.4
    )
    
    for i, email in enumerate(results, 1):
        console.print(Panel(
            f"[bold cyan]De:[/bold cyan] {email['from_name']}\n"
            f"[bold green]Para:[/bold green] {email['to_names']}\n"
            f"[bold yellow]Data:[/bold yellow] {email['date']}\n"
            f"[bold magenta]Assunto:[/bold magenta] {email['subject']}\n"
            f"[bold blue]Distância:[/bold blue] {email['distance']:.4f}\n\n"
            f"[bold white]Body:[/bold white]\n{email['body'][:300]}...",
            title=f"[bold red]🚨 Email Suspeito {i}[/bold red]",
            border_style="red"
        ))
    
    # Teste 3: TODOS os emails de Michael sobre Toby
    console.print(Panel(
        "[bold cyan]Teste 3: TODOS os Emails DE Michael SOBRE Toby[/bold cyan]",
        border_style="cyan"
    ))
    
    all_emails = retriever.get_all_emails_from_michael_about_toby()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=12)
    table.add_column("Data", style="yellow", width=16)
    table.add_column("Para", style="green", width=20)
    table.add_column("Assunto", style="blue", width=40)
    
    for email in all_emails:
        table.add_row(
            email['email_id'],
            email['date'],
            email['to_names'].split(',')[0][:20],
            email['subject'][:40]
        )
    
    console.print(table)
    
    # Teste 4: Busca por keyword
    console.print(Panel(
        "[bold cyan]Teste 4: Busca por Keyword 'conspiração'[/bold cyan]",
        border_style="cyan"
    ))
    
    results = retriever.search_by_keyword(
        keyword="conspiração",
        from_michael=True
    )
    
    console.print(f"[green]Encontrados {len(results)} emails com 'conspiração'[/green]\n")
    
    for email in results[:3]:
        console.print(f"  📧 {email['email_id']}: {email['subject']}")

    