# src/tools.py
"""
Tools (ferramentas) para o agente de compliance.
Cada tool é uma função que o agente pode chamar.
"""

from typing import List, Dict
from src.retriever import ComplianceRetriever
from src.email_retriever import EmailRetriever
from rich.console import Console

# Importar agente de conspiração
import sys
from pathlib import Path

# Adicionar path do agente
agent_path = Path(__file__).parent.parent / "agent_conspiracy"
if str(agent_path) not in sys.path:
    sys.path.insert(0, str(agent_path))

## from agent_conspiracy.agent import root_agent as conspiracy_agent

console = Console()

# Inicializar retriever globalmente (será usado pelas tools)
_retriever = None
_email_retriever = None


def get_retriever() -> ComplianceRetriever:
    """Retorna instância do retriever (singleton)."""
    global _retriever
    if _retriever is None:
        _retriever = ComplianceRetriever()
    return _retriever


def get_email_retriever() -> EmailRetriever:
    """Retorna instância do email retriever (singleton)."""
    global _email_retriever
    if _email_retriever is None:
        _email_retriever = EmailRetriever()
    return _email_retriever


def search_compliance_policies(query: str, top_k: int = 5) -> dict:
    """
    Busca informações nas políticas de compliance da Dunder Mifflin.
    
    Args:
        query: Pergunta ou termo de busca sobre políticas de compliance
        top_k: Número de trechos relevantes a retornar (padrão: 5)
    
    Returns:
        Dicionário com status, trechos encontrados e metadados
    """
    try:
        retriever = get_retriever()
        
        console.print(f"[yellow]🔍 Tool chamada: search_compliance_policies[/yellow]")
        console.print(f"[cyan]   Query: {query}[/cyan]")
        console.print(f"[cyan]   Top-K: {top_k}[/cyan]\n")
        
        # Buscar chunks relevantes
        chunks = retriever.retrieve(query, top_k=top_k, show_details=False)
        
        if not chunks:
            return {
                "status": "no_results",
                "message": "Nenhuma informação relevante encontrada nas políticas.",
                "chunks": []
            }
        
        # Formatar chunks para retorno COM PREVIEW
        formatted_chunks = []
        for i, chunk in enumerate(chunks, 1):
            # Extrair preview (primeiras palavras do chunk)
            text = chunk['text']
            words = text.split()
            
            # Preview: primeiras 8-10 palavras
            preview_words = words[:10]
            preview = " ".join(preview_words)
            if len(words) > 10:
                preview += "..."
            
            formatted_chunks.append({
                "rank": i,
                "id": chunk['id'],
                "text": text,
                "preview": preview,  # ✅ NOVO: Preview para citação
                "similarity": round(chunk['similarity_score'], 4),
                "metadata": chunk['metadata']
            })
        
        console.print(f"[green]✅ {len(formatted_chunks)} trechos encontrados[/green]\n")
        
        return {
            "status": "success",
            "message": f"Encontrados {len(formatted_chunks)} trechos relevantes.",
            "chunks": formatted_chunks,
            "query": query
        }
        
    except Exception as e:
        console.print(f"[red]❌ Erro na tool: {e}[/red]\n")
        return {
            "status": "error",
            "message": f"Erro ao buscar políticas: {str(e)}",
            "chunks": []
        }


def search_by_keyword(keyword: str) -> dict:
    """
    Busca trechos que contenham uma palavra-chave específica nas políticas.
    Útil para buscas exatas (não semânticas).
    
    Args:
        keyword: Palavra-chave exata a buscar
    
    Returns:
        Dicionário com status e trechos que contêm a palavra-chave
    """
    try:
        retriever = get_retriever()
        
        console.print(f"[yellow]🔍 Tool chamada: search_by_keyword[/yellow]")
        console.print(f"[cyan]   Keyword: {keyword}[/cyan]\n")
        
        # Buscar por palavra-chave
        chunks = retriever.search_by_keyword(keyword, case_sensitive=False)
        
        if not chunks:
            return {
                "status": "no_results",
                "message": f"Palavra-chave '{keyword}' não encontrada nas políticas.",
                "chunks": []
            }
        
        # Formatar chunks COM PREVIEW
        formatted_chunks = []
        for chunk in chunks:
            text = chunk['text']
            words = text.split()
            
            # Preview
            preview_words = words[:10]
            preview = " ".join(preview_words)
            if len(words) > 10:
                preview += "..."
            
            formatted_chunks.append({
                "id": chunk['id'],
                "text": text,
                "preview": preview,  # ✅ NOVO
                "metadata": chunk['metadata']
            })
        
        console.print(f"[green]✅ {len(formatted_chunks)} trechos com '{keyword}'[/green]\n")
        
        return {
            "status": "success",
            "message": f"Encontrados {len(formatted_chunks)} trechos com '{keyword}'.",
            "chunks": formatted_chunks,
            "keyword": keyword
        }
        
    except Exception as e:
        console.print(f"[red]❌ Erro na tool: {e}[/red]\n")
        return {
            "status": "error",
            "message": f"Erro ao buscar palavra-chave: {str(e)}",
            "chunks": []
        }


def get_policy_summary() -> dict:
    """
    Retorna um resumo geral das políticas de compliance disponíveis.
    
    Returns:
        Dicionário com estatísticas sobre as políticas
    """
    try:
        retriever = get_retriever()
        
        console.print(f"[yellow]🔍 Tool chamada: get_policy_summary[/yellow]\n")
        
        # Pegar estatísticas da coleção
        collection = retriever.collection
        count = collection.count()
        
        # Pegar alguns chunks para análise
        sample = collection.get(limit=min(10, count))
        
        # Calcular estatísticas
        if sample['documents']:
            avg_length = sum(len(doc) for doc in sample['documents']) / len(sample['documents'])
            total_chars = sum(len(doc) for doc in sample['documents'])
        else:
            avg_length = 0
            total_chars = 0
        
        console.print(f"[green]✅ Resumo gerado[/green]\n")
        
        return {
            "status": "success",
            "total_chunks": count,
            "average_chunk_length": round(avg_length, 2),
            "sample_size": len(sample['documents']),
            "total_characters_sampled": total_chars,
            "message": f"Base de conhecimento contém {count} trechos de políticas de compliance."
        }
        
    except Exception as e:
        console.print(f"[red]❌ Erro na tool: {e}[/red]\n")
        return {
            "status": "error",
            "message": f"Erro ao obter resumo: {str(e)}"
        }

# src/tools.py
"""
Tools (ferramentas) para o agente de compliance.
Cada tool é uma função que o agente pode chamar.
"""

from typing import List, Dict
from src.retriever import ComplianceRetriever
from src.email_retriever import EmailRetriever
from rich.console import Console

console = Console()

# Inicializar retriever globalmente (será usado pelas tools)
_retriever = None
_email_retriever = None


def get_retriever() -> ComplianceRetriever:
    """Retorna instância do retriever (singleton)."""
    global _retriever
    if _retriever is None:
        _retriever = ComplianceRetriever()
    return _retriever


def get_email_retriever() -> EmailRetriever:
    """Retorna instância do email retriever (singleton)."""
    global _email_retriever
    if _email_retriever is None:
        _email_retriever = EmailRetriever()
    return _email_retriever


def search_compliance_policies(query: str, top_k: int = 5) -> dict:
    """
    Busca informações nas políticas de compliance da Dunder Mifflin.
    
    Args:
        query: Pergunta ou termo de busca sobre políticas de compliance
        top_k: Número de trechos relevantes a retornar (padrão: 5)
    
    Returns:
        Dicionário com status, trechos encontrados e metadados
    """
    try:
        retriever = get_retriever()
        
        console.print(f"[yellow]🔍 Tool chamada: search_compliance_policies[/yellow]")
        console.print(f"[cyan]   Query: {query}[/cyan]")
        console.print(f"[cyan]   Top-K: {top_k}[/cyan]\n")
        
        # Buscar chunks relevantes
        chunks = retriever.retrieve(query, top_k=top_k, show_details=False)
        
        if not chunks:
            return {
                "status": "no_results",
                "message": "Nenhuma informação relevante encontrada nas políticas.",
                "chunks": []
            }
        
        # Formatar chunks para retorno COM PREVIEW
        formatted_chunks = []
        for i, chunk in enumerate(chunks, 1):
            # Extrair preview (primeiras palavras do chunk)
            text = chunk['text']
            words = text.split()
            
            # Preview: primeiras 8-10 palavras
            preview_words = words[:10]
            preview = " ".join(preview_words)
            if len(words) > 10:
                preview += "..."
            
            formatted_chunks.append({
                "rank": i,
                "id": chunk['id'],
                "text": text,
                "preview": preview,
                "similarity": round(chunk['similarity_score'], 4),
                "metadata": chunk['metadata']
            })
        
        console.print(f"[green]✅ {len(formatted_chunks)} trechos encontrados[/green]\n")
        
        return {
            "status": "success",
            "message": f"Encontrados {len(formatted_chunks)} trechos relevantes.",
            "chunks": formatted_chunks,
            "query": query
        }
        
    except Exception as e:
        console.print(f"[red]❌ Erro na tool: {e}[/red]\n")
        return {
            "status": "error",
            "message": f"Erro ao buscar políticas: {str(e)}",
            "chunks": []
        }


def search_by_keyword(keyword: str) -> dict:
    """
    Busca trechos que contenham uma palavra-chave específica nas políticas.
    Útil para buscas exatas (não semânticas).
    
    Args:
        keyword: Palavra-chave exata a buscar
    
    Returns:
        Dicionário com status e trechos que contêm a palavra-chave
    """
    try:
        retriever = get_retriever()
        
        console.print(f"[yellow]🔍 Tool chamada: search_by_keyword[/yellow]")
        console.print(f"[cyan]   Keyword: {keyword}[/cyan]\n")
        
        # Buscar por palavra-chave
        chunks = retriever.search_by_keyword(keyword, case_sensitive=False)
        
        if not chunks:
            return {
                "status": "no_results",
                "message": f"Palavra-chave '{keyword}' não encontrada nas políticas.",
                "chunks": []
            }
        
        # Formatar chunks COM PREVIEW
        formatted_chunks = []
        for chunk in chunks:
            text = chunk['text']
            words = text.split()
            
            # Preview
            preview_words = words[:10]
            preview = " ".join(preview_words)
            if len(words) > 10:
                preview += "..."
            
            formatted_chunks.append({
                "id": chunk['id'],
                "text": text,
                "preview": preview,
                "metadata": chunk['metadata']
            })
        
        console.print(f"[green]✅ {len(formatted_chunks)} trechos com '{keyword}'[/green]\n")
        
        return {
            "status": "success",
            "message": f"Encontrados {len(formatted_chunks)} trechos com '{keyword}'.",
            "chunks": formatted_chunks,
            "keyword": keyword
        }
        
    except Exception as e:
        console.print(f"[red]❌ Erro na tool: {e}[/red]\n")
        return {
            "status": "error",
            "message": f"Erro ao buscar palavra-chave: {str(e)}",
            "chunks": []
        }


def get_policy_summary() -> dict:
    """
    Retorna um resumo geral das políticas de compliance disponíveis.
    
    Returns:
        Dicionário com estatísticas sobre as políticas
    """
    try:
        retriever = get_retriever()
        
        console.print(f"[yellow]🔍 Tool chamada: get_policy_summary[/yellow]\n")
        
        # Pegar estatísticas da coleção
        collection = retriever.collection
        count = collection.count()
        
        # Pegar alguns chunks para análise
        sample = collection.get(limit=min(10, count))
        
        # Calcular estatísticas
        if sample['documents']:
            avg_length = sum(len(doc) for doc in sample['documents']) / len(sample['documents'])
            total_chars = sum(len(doc) for doc in sample['documents'])
        else:
            avg_length = 0
            total_chars = 0
        
        console.print(f"[green]✅ Resumo gerado[/green]\n")
        
        return {
            "status": "success",
            "total_chunks": count,
            "average_chunk_length": round(avg_length, 2),
            "sample_size": len(sample['documents']),
            "total_characters_sampled": total_chars,
            "message": f"Base de conhecimento contém {count} trechos de políticas de compliance."
        }
        
    except Exception as e:
        console.print(f"[red]❌ Erro na tool: {e}[/red]\n")
        return {
            "status": "error",
            "message": f"Erro ao obter resumo: {str(e)}"
        }

def investigate_conspiracy(query: str) -> dict:
    try:
        email_retriever = get_email_retriever()
        
        console.print(f"[yellow]🔍 Tool chamada: investigate_conspiracy[/yellow]")
        console.print(f"[cyan]   Query: '{query}'[/cyan]\n")
        
        # PASSO 1: Buscar emails suspeitos de Michael sobre Toby
        console.print("[cyan]📧 Buscando emails suspeitos...[/cyan]")
        suspicious_emails = email_retriever.search_emails_from_michael_about_toby(
            query=query,
            top_k=10,
            max_distance=0.5
        )
        
        if not suspicious_emails:
            console.print("[yellow]⚠️  Nenhum email suspeito encontrado[/yellow]\n")
            return {
                "status": "no_evidence",
                "message": "Nenhuma evidência de conspiração encontrada nos emails internos.",
                "emails_analyzed": 0,
                "investigation_report": "Após análise da base de emails, não foram encontradas comunicações suspeitas relacionadas à query solicitada."
            }
        
        # PASSO 2: Formatar evidências para análise
        console.print(f"[green]✅ Encontrados {len(suspicious_emails)} emails suspeitos[/green]")
        console.print("[cyan]🕵️  Chamando agente de investigação...[/cyan]\n")
        
        evidence_text = f"""
        Você recebeu uma solicitação de investigação sobre: "{query}"

        Foram encontrados {len(suspicious_emails)} emails potencialmente suspeitos para análise.

        EVIDÊNCIAS COLETADAS:
        {'='*80}
        """
        
        for i, email in enumerate(suspicious_emails, 1):
            relevance = round(1 - email['distance'], 2)
            evidence_text += f"""
            EMAIL #{i}
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            ID: {email['email_id']}
            De: {email['from_name']} <{email['from']}>
            Para: {email['to_names']}
            Data: {email['date']}
            Assunto: {email['subject']}
            Score de Relevância: {relevance}

            CORPO DO EMAIL:
            {email['body']}
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        evidence_text += """
        TAREFA:
        Analise todos os emails acima e produza um relatório de investigação detalhado seguindo
        o formato especificado nas suas instruções. Identifique violações, avalie gravidade e
        forneça conclusões baseadas apenas nas evidências apresentadas.
        """

        return evidence_text

    except Exception as e:
        console.print(f"[red]❌ Erro na investigação: {e}[/red]\n")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Erro ao investigar conspiração: {str(e)}",
            "emails_analyzed": 0,
            "investigation_report": "Investigação falhou devido a erro técnico."
        }

def find_fraud_emails(query: str, top_k: int = 12, max_distance: float = 0.42) -> dict:
    retriever = get_email_retriever()

    console.print(f"[yellow]🔍 Tool chamada: find_fraud_emails[/yellow]")
    console.print(f"[cyan]→ Query usada: '{query}'[/cyan]\n")

    semantic_results = retriever.search_emails_with_financial_fraud(
        query=query,
        top_k=top_k,
        max_distance=max_distance
    )

    keyword_results = retriever.search_financial_keywords(top_k=top_k)

    metadata_results = retriever.search_emails_with_financial_metadata()

    combined = {}
    
    for email_list in [semantic_results, keyword_results, metadata_results]:
        for email in email_list:
            combined[email["email_id"]] = email

    final_results = list(combined.values())

    console.print(f"[yellow]📊 Total combinado antes do filtro semântico: {len(final_results)}[/yellow]\n")

    console.print(f"[green]💰 Emails finais classificados como fraude financeira: {len(final_results)}[/green]\n")

    return {
        "status": "success",
        "query": query,
        "emails": final_results
    }

