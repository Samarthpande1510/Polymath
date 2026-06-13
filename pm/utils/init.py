from pathlib import Path
from rich.console import Console
import typer

console = Console()

config_file = Path.home() / ".polymath"

def run_migrations():
    try:
        from sqlalchemy import create_engine
        from pm.db.models import Base
        db_path = Path.home() / ".polymath" / "polymath.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        console.print("[green]✓ Database ready[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Database error: {e}[/red]")
        return False

def validate_gemini_key(key: str) -> bool:
    try:
        from google import genai
        client = genai.Client(api_key=key)
        client.models.embed_content(
            model="gemini-embedding-001",
            contents="test"
        )
        return True
    except Exception:
        return False

def init():
    config_file.mkdir(parents=True, exist_ok=True)
    env_missing = not (config_file / ".env").exists()

    if env_missing:
        gemini_key = typer.prompt("Enter your Gemini API key (get one free at aistudio.google.com)")
        with console.status("[bold green]Validating API key..."):
            if not validate_gemini_key(gemini_key):
                console.print("[red]✗ Invalid API key. Get one free at aistudio.google.com[/red]")
                return
        console.print("[green]✓ API key valid[/green]")
        env_content = f"GEMINI_API_KEY={gemini_key}\n"
        (config_file / ".env").write_text(env_content)

    run_migrations()
    console.print("[green]✓ Polymath ready![/green]")
    console.print("[yellow]Tip: Free tier allows 20 questions/day. Enable billing at aistudio.google.com for unlimited usage.[/yellow]")