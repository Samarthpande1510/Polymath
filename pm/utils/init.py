from pathlib import Path
import subprocess
from rich.console import Console
import typer

console = Console()

config_file = Path.home() / ".polymath"

DOCKER_COMPOSE = """services:
  polymath-db:
    image: postgres:16
    ports:
      - "5433:5432"
    environment:
      POSTGRES_USER: polymath
      POSTGRES_PASSWORD: polymath
      POSTGRES_DB: polymath
    volumes:
      - polymath_postgres:/var/lib/postgresql/data

  polymath-qdrant:
    image: qdrant/qdrant
    ports:
      - "6334:6333"
    volumes:
      - polymath_qdrant:/qdrant/storage

volumes:
  polymath_postgres:
  polymath_qdrant:
"""

def init():
    first_time = not (config_file / "docker-compose.yml").exists()
    env_missing = not (config_file / ".env").exists()

    if first_time or env_missing:
        gemini_key = typer.prompt("Enter your Gemini API key (get one free at aistudio.google.com)")
        config_file.mkdir(parents=True, exist_ok=True)
        (config_file / "docker-compose.yml").write_text(DOCKER_COMPOSE)
        env_content = f"""DATABASE_URL=postgresql://polymath:polymath@localhost:5433/polymath
QDRANT_HOST=localhost
QDRANT_PORT=6334
GEMINI_API_KEY={gemini_key}
"""
        (config_file / ".env").write_text(env_content)
        console.print("[bold green]First time setup — initializing Polymath...[/bold green]")
    else:
        console.print("[bold green]Starting Polymath services...[/bold green]")

    with console.status("[bold green]Starting Docker containers..."):
        result = subprocess.run(
            ["docker", "compose", "-f", str(config_file / "docker-compose.yml"), "up", "-d"],
            capture_output=True,
            text=True
        )

    if result.returncode != 0:
        if "Cannot connect to the Docker daemon" in result.stderr:
            console.print("[red]✗ Docker is not running. Please start Docker Desktop and try again.[/red]")
        else:
            console.print(f"[red]✗ Error: {result.stderr}[/red]")
        return

    console.print("[green]✓ Polymath ready![/green]")