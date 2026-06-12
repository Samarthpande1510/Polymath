import subprocess
from rich.console import Console
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine
import os
import requests

console = Console()

def load_env():
    env_path = Path.home() / ".polymath" / ".env"
    load_dotenv(env_path)

def check_docker() -> bool:
    result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
    if result.returncode == 0:
        console.print("[green]✓ Docker is running[/green]")
        return True
    console.print("[red]✗ Docker is not running[/red]")
    return False

def check_postgres() -> bool:
    try:
        load_env() 
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            console.print("[red]✗ Postgres: DATABASE_URL not set. Run 'pm init' first.[/red]")
            return False
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            console.print("[green]✓ Postgres is running[/green]")
            return True
    except Exception as e:
        console.print(f"[red]✗ Postgres is not running: {e}[/red]")
        return False

def check_qdrant() -> bool:
    try:
        response = requests.get("http://localhost:6334")
        if response.status_code == 200:
            console.print("[green]✓ Qdrant is running[/green]")
            return True
        console.print(f"[red]✗ Qdrant returned status {response.status_code}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Qdrant is not running: {e}[/red]")
        return False
    
def doctor():
    load_env()
    console.print("\n[bold]Polymath Health Check[/bold]\n")
    check_docker()
    check_postgres()
    check_qdrant()




