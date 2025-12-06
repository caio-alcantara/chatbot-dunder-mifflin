# src/email_parser.py

import re
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime
from rich.console import Console

console = Console()


@dataclass
class Email:
    """Estrutura de um email."""
    email_id: str
    sender: str
    sender_name: str
    recipients: List[str]
    recipient_names: List[str]
    date: str
    timestamp: int
    subject: str
    body: str
    
    # Flags de análise
    is_from_michael: bool
    mentions_toby: bool
    mentions_toby_keywords: List[str]
    preview: str
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return asdict(self)
    
    def to_chroma_format(self) -> tuple[str, str, dict]:
        """
        Converte para formato ChromaDB.
        
        Returns:
            (id, document, metadata)
        """
        # Document = subject + body (para embedding semântico)
        document = f"{self.subject}\n\n{self.body}"
        
        # Metadata = tudo exceto o body (para filtros)
        metadata = {
            "email_id": self.email_id,
            "from": self.sender,
            "from_name": self.sender_name,
            "to": ",".join(self.recipients),  # ChromaDB não suporta listas
            "to_names": ",".join(self.recipient_names),
            "date": self.date,
            "timestamp": self.timestamp,
            "subject": self.subject,
            "body": self.body,  # Manter para retrieval
            "is_from_michael": self.is_from_michael,
            "mentions_toby": self.mentions_toby,
            "mentions_toby_keywords": ",".join(self.mentions_toby_keywords),
            "preview": self.preview
        }
        
        return self.email_id, document, metadata


class EmailParser:
    """Parser de dump de emails."""
    
    # Regex patterns
    SEPARATOR = r"-{79,}"  # 79 ou mais hífens
    EMAIL_PATTERN = r"<([^>]+)>"
    
    # Keywords para detectar menções a Toby
    TOBY_KEYWORDS = [
        "toby", "flenderson", "toby flenderson",
        "hr", "recursos humanos", "rh"
    ]
    
    def __init__(self):
        self.emails: List[Email] = []
    
    def parse_dump(self, file_path: str) -> List[Email]:
        """
        Parse do dump de emails.
        
        Args:
            file_path: Caminho para o arquivo .txt
        
        Returns:
            Lista de objetos Email
        """
        console.print(f"[cyan]📧 Parseando dump de emails: {file_path}[/cyan]")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dividir por separadores
        raw_emails = re.split(self.SEPARATOR, content)
        
        # Remover header do dump (primeira seção)
        raw_emails = [e.strip() for e in raw_emails if e.strip()]
        if "DUMP DE SERVIDOR" in raw_emails[0]:
            raw_emails = raw_emails[1:]
        
        console.print(f"[cyan]📊 Encontrados {len(raw_emails)} emails brutos[/cyan]")
        
        # Parse cada email
        for idx, raw_email in enumerate(raw_emails):
            try:
                email = self._parse_single_email(raw_email, idx)
                if email:
                    self.emails.append(email)
            except Exception as e:
                console.print(f"[yellow]⚠️  Erro ao parsear email {idx}: {e}[/yellow]")
                continue
        
        console.print(f"[green]✅ {len(self.emails)} emails parseados com sucesso[/green]\n")
        
        return self.emails
    
    def _parse_single_email(self, raw_email: str, idx: int) -> Optional[Email]:
        """Parse de um único email."""
        lines = raw_email.strip().split('\n')
        
        if len(lines) < 5:
            return None
        
        # Extrair campos
        sender = ""
        sender_name = ""
        recipients = []
        recipient_names = []
        date = ""
        subject = ""
        body = ""
        
        in_body = False
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            if line.startswith("De:"):
                sender, sender_name = self._extract_email_and_name(line[3:])
            
            elif line.startswith("Para:"):
                # Pode ter múltiplos destinatários
                recipients_raw = line[5:].strip()
                for recipient in recipients_raw.split(','):
                    email, name = self._extract_email_and_name(recipient.strip())
                    if email:
                        recipients.append(email)
                        recipient_names.append(name)
            
            elif line.startswith("Data:"):
                date = line[5:].strip()
            
            elif line.startswith("Assunto:"):
                subject = line[8:].strip()
            
            elif line.startswith("Mensagem:"):
                in_body = True
                continue
            
            elif in_body:
                body += line + "\n"
        
        # Validação
        if not sender or not date or not subject:
            return None
        
        # Gerar ID
        email_id = f"email_{idx:04d}"
        
        # Timestamp
        timestamp = self._parse_timestamp(date)
        
        # Flags de análise
        is_from_michael = "michael.scott" in sender.lower()
        mentions_toby, toby_keywords = self._check_toby_mentions(subject, body)
        
        # Preview
        preview = body[:100].replace('\n', ' ').strip() + "..."
        
        return Email(
            email_id=email_id,
            sender=sender,
            sender_name=sender_name,
            recipients=recipients,
            recipient_names=recipient_names,
            date=date,
            timestamp=timestamp,
            subject=subject,
            body=body.strip(),
            is_from_michael=is_from_michael,
            mentions_toby=mentions_toby,
            mentions_toby_keywords=toby_keywords,
            preview=preview
        )
    
    def _extract_email_and_name(self, text: str) -> tuple[str, str]:
        """
        Extrai email e nome de strings como:
        - "Michael Scott <michael.scott@dundermifflin.com>"
        - "michael.scott@dundermifflin.com"
        
        Returns:
            (email, name)
        """
        email_match = re.search(self.EMAIL_PATTERN, text)
        
        if email_match:
            email = email_match.group(1).strip()
            name = text[:email_match.start()].strip()
            return email, name
        else:
            # Apenas email, sem nome
            email = text.strip()
            name = email.split('@')[0].replace('.', ' ').title()
            return email, name
    
    def _parse_timestamp(self, date_str: str) -> int:
        """
        Converte string de data para Unix timestamp.
        
        Formato esperado: "2008-04-05 14:00"
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            return int(dt.timestamp())
        except:
            return 0
    
    def _check_toby_mentions(self, subject: str, body: str) -> tuple[bool, List[str]]:
        """
        Verifica se o email menciona Toby.
        
        Returns:
            (mentions_toby, keywords_found)
        """
        text = (subject + " " + body).lower()
        
        keywords_found = []
        for keyword in self.TOBY_KEYWORDS:
            if keyword in text:
                keywords_found.append(keyword)
        
        return len(keywords_found) > 0, keywords_found
    
    def get_statistics(self) -> dict:
        """Retorna estatísticas dos emails parseados."""
        total = len(self.emails)
        from_michael = sum(1 for e in self.emails if e.is_from_michael)
        mentions_toby = sum(1 for e in self.emails if e.mentions_toby)
        from_michael_about_toby = sum(
            1 for e in self.emails 
            if e.is_from_michael and e.mentions_toby
        )
        
        return {
            "total_emails": total,
            "from_michael": from_michael,
            "mentions_toby": mentions_toby,
            "from_michael_about_toby": from_michael_about_toby,
            "date_range": self._get_date_range()
        }
    
    def _get_date_range(self) -> tuple[str, str]:
        """Retorna range de datas dos emails."""
        if not self.emails:
            return ("", "")
        
        dates = [e.date for e in self.emails if e.date]
        if not dates:
            return ("", "")
        
        return (min(dates), max(dates))


# ============================================================================
# TESTE DO PARSER
# ============================================================================

if __name__ == "__main__":
    from rich.table import Table
    from rich.panel import Panel
    
    # Parse
    parser = EmailParser()
    emails = parser.parse_dump("data/emails_internos.txt")
    
    # Estatísticas
    stats = parser.get_statistics()
    
    console.print(Panel(
        f"[bold cyan]Total de Emails:[/bold cyan] {stats['total_emails']}\n"
        f"[bold yellow]De Michael Scott:[/bold yellow] {stats['from_michael']}\n"
        f"[bold magenta]Mencionam Toby:[/bold magenta] {stats['mentions_toby']}\n"
        f"[bold red]Michael → Toby:[/bold red] {stats['from_michael_about_toby']}\n"
        f"[bold green]Período:[/bold green] {stats['date_range'][0]} a {stats['date_range'][1]}",
        title="[bold blue]📊 Estatísticas do Dump[/bold blue]",
        border_style="blue"
    ))
    
    # Mostrar primeiros 5 emails
    console.print("\n[bold cyan]📧 Primeiros 5 Emails:[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=12)
    table.add_column("De", style="yellow", width=20)
    table.add_column("Para", style="green", width=20)
    table.add_column("Assunto", style="blue", width=30)
    table.add_column("Flags", style="red", width=15)
    
    for email in emails[:5]:
        flags = []
        if email.is_from_michael:
            flags.append("🎯 Michael")
        if email.mentions_toby:
            flags.append("👤 Toby")
        
        table.add_row(
            email.email_id,
            email.sender_name[:20],
            email.recipient_names[0][:20] if email.recipient_names else "",
            email.subject[:30],
            " ".join(flags)
        )
    
    console.print(table)
    
    # Mostrar um email completo
    if emails:
        console.print("\n[bold cyan]📧 Exemplo de Email Completo:[/bold cyan]\n")
        email = emails[0]
        console.print(Panel(
            f"[bold cyan]ID:[/bold cyan] {email.email_id}\n"
            f"[bold yellow]De:[/bold yellow] {email.sender_name} <{email.sender}>\n"
            f"[bold green]Para:[/bold green] {', '.join(email.recipient_names)}\n"
            f"[bold blue]Data:[/bold blue] {email.date}\n"
            f"[bold magenta]Assunto:[/bold magenta] {email.subject}\n\n"
            f"[bold white]Mensagem:[/bold white]\n{email.body[:200]}...",
            title="[bold blue]Email Detalhado[/bold blue]",
            border_style="blue"
        ))
