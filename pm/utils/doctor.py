from rich.console import Console
from pathlib import Path
from sqlalchemy import create_engine, text
import os

console = Console()

def check_sqlite() -> bool:
    try:
        db_path = Path.home() / ".polymath" / "polymath.db"
        if not db_path.exists():
            console.print("[red]✗ Database not found. Run 'pm init' first.[/red]")
            return False
        engine = create_engine(f"sqlite:///{db_path}")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        console.print("[green]✓ Database is ready[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Database error: {e}[/red]")
        return False

def check_qdrant() -> bool:
    try:
        from qdrant_client import QdrantClient
        qdrant_path = str(Path.home() / ".polymath" / "qdrant_data")
        client = QdrantClient(path=qdrant_path)
        client.get_collections()
        console.print("[green]✓ Qdrant is ready[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Qdrant error: {e}[/red]")
        return False

def check_env() -> bool:
    env_path = Path.home() / ".polymath" / ".env"
    if not env_path.exists():
        console.print("[red]✗ Not initialized. Run 'pm init' first.[/red]")
        return False
    console.print("[green]✓ Config found[/green]")
    return True

def check_ollama() -> bool:
    try:
        import requests
        response = requests.get("http://localhost:11434")
        if response.status_code == 200:
            console.print("[green]✓ Ollama is running[/green]")
            return True
        console.print("[red]✗ Ollama not responding. Run: ollama serve[/red]")
        return False
    except Exception:
        console.print("[red]✗ Ollama is not running. Run: ollama serve[/red]")
        return False

def doctor():
    from dotenv import load_dotenv
    load_dotenv(Path.home() / ".polymath" / ".env")
    provider = os.getenv("LLM_PROVIDER", "gemini")

    console.print("\n[bold]Polymath Health Check[/bold]\n")
    check_env()
    check_sqlite()
    check_qdrant()
    if provider == "ollama":
        check_ollama()