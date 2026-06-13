import typer
from rich.console import Console

app = typer.Typer(help="Polymath — ask anything about any codebase")
console = Console()

from importlib.metadata import version as pkg_version

def version_callback(value: bool):
    if value:
        console.print("Polymath v0.1.7")
        raise typer.Exit()

@app.callback()
def main(version: bool = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True, help="Show version")):
    pass

@app.command()
def init():
    """First time setup — spins up Docker, Postgres, Qdrant"""
    from pm.utils.init import init as init_polymath
    init_polymath()

@app.command()
def doctor():
    """Check if everything is running correctly"""
    from pm.utils.doctor import doctor as polymath_doctor
    polymath_doctor()
@app.command()
def pwd():
    """Show active repository path"""
    from pm.utils.state import get_active_repo
    from pm.db.database import LocalSession
    from pm.db.queries import get_repo_by_name
    db = LocalSession()
    try:
        active = get_active_repo()
        if not active:
            console.print("[red]✗ No active repo. Run 'pm cd' first.[/red]")
            return
        repo_id, repo_name = active
        repo = get_repo_by_name(db, repo_name)
        console.print(f"[green]{repo.path}[/green]")
    finally:
        db.close()

@app.command()
def cd(path: str = typer.Argument(..., help="URL or local path to repo")):
    """Set active repository"""
    from pm.indexer.indexer import index_repo
    from pathlib import Path
    import subprocess
    from pathlib import Path

    if not path.startswith("https://") and not path.startswith("git@"):
        resolved = Path(path).resolve()
    if not resolved.exists():
        console.print(f"[red]✗ Directory not found: {path}[/red]")
        return
    if not resolved.is_dir():
        console.print(f"[red]✗ Not a directory: {path}[/red]")
        return
    if path.startswith("https://") or path.startswith("git@"):
        repo_name = path.rstrip("/").split("/")[-1].replace(".git", "")
        repos_dir = Path.home() / ".polymath" / "repos"
        repos_dir.mkdir(parents=True, exist_ok=True)
        clone_path = repos_dir / repo_name
        if clone_path.exists():
            console.print(f"[yellow]'{repo_name}' already cloned — indexing.[/yellow]")
        else:
            console.print(f"[bold]Cloning [green]{repo_name}[/green]...[/bold]")
            result = subprocess.run(["git", "clone", path, str(clone_path)], capture_output=True, text=True)
            if result.returncode != 0:
                console.print(f"[red]✗ Clone failed: {result.stderr}[/red]")
                return
            console.print(f"[green]✓ Cloned to ~/.polymath/repos/{repo_name}[/green]")
        index_repo(str(clone_path), url=path)
    else:
        index_repo(path)

@app.command()
def ask(question: str = typer.Argument(..., help="Question to ask about the codebase")):
    """Ask a question about the active repository"""
    from pm.agent.ask import ask as ask_question
    ask_question(question)

@app.command()
def ls():
    """List all indexed repositories"""
    from pm.db.database import LocalSession
    from pm.db.queries import get_all_repos
    db = LocalSession()
    try:
        repos = get_all_repos(db)
        if not repos:
            console.print("[yellow]No repos indexed yet. Run 'pm cd <path>' to index one.[/yellow]")
            return
        for repo in repos:
            console.print(f"[green]{repo.name}[/green] — {repo.path}")
    finally:
        db.close()

@app.command()
def status():
    """Show active repo and current context"""
    from pm.db.database import LocalSession
    from pm.db.models import File, Chunk
    from pm.utils.state import get_active_repo
    db = LocalSession()
    try:
        active = get_active_repo()
        if not active:
            console.print("[yellow]No active repo. Run 'pm cd <path>' first.[/yellow]")
            return
        repo_id, repo_name = active
        file_count = db.query(File).filter(File.repo_id == repo_id).count()
        chunk_count = db.query(Chunk).filter(Chunk.repo_id == repo_id).count()
        console.print(f"[bold]Active repo:[/bold] [green]{repo_name}[/green]")
        console.print(f"[bold]Files:[/bold] {file_count}")
        console.print(f"[bold]Chunks:[/bold] {chunk_count}")
    finally:
        db.close()

@app.command()
def rm(repo: str = typer.Argument(..., help="Repo name to remove")):
    """Remove an indexed repository"""
    from pm.db.database import LocalSession
    from pm.db.queries import get_repo_by_name, delete_repo_data, delete_repo
    from pm.vector.store import delete_repo_vectors
    db = LocalSession()
    try:
        repo_record = get_repo_by_name(db, repo)
        if not repo_record:
            console.print(f"[red]✗ Repo '{repo}' not found. Run 'pm ls' to see indexed repos.[/red]")
            return
        delete_repo_data(db, repo_record.id)
        delete_repo(db, repo_record.id)
        delete_repo_vectors(repo_record.id)
        console.print(f"[green]✓ Removed '{repo}' successfully[/green]")
    finally:
        db.close()

@app.command()
def refresh():
    """Re-index the active repository"""
    from pm.db.database import LocalSession
    from pm.db.queries import get_repo_by_name
    from pm.indexer.indexer import reindex_repo
    from pm.utils.state import get_active_repo
    db = LocalSession()
    try:
        active = get_active_repo()
        if not active:
            console.print("[yellow]No active repo. Run 'pm cd <path>' first.[/yellow]")
            return
        repo_id, repo_name = active
        repo = get_repo_by_name(db, repo_name)
        path = repo.path
    finally:
        db.close()
    reindex_repo(repo_id, path, repo_name)

@app.command()
def find(query: str = typer.Argument(..., help="Keyword to search for")):
    """Find files and functions containing a keyword"""
    from pm.db.database import LocalSession
    from pm.db.models import Chunk
    from pm.utils.state import get_active_repo
    from rich.syntax import Syntax
    db = LocalSession()
    try:
        active = get_active_repo()
        if not active:
            console.print("[red]✗ No active repo. Run 'pm cd' first.[/red]")
            return
        repo_id, repo_name = active
        results = db.query(Chunk).filter(
            Chunk.repo_id == repo_id,
            Chunk.content.ilike(f"%{query}%")
        ).limit(10).all()
        if not results:
            console.print(f"[yellow]No results found for '{query}'[/yellow]")
            return
        console.print(f"\n[bold]Found {len(results)} results for '[green]{query}[/green]'[/bold]\n")
        for r in results:
            console.print(f"[cyan]{r.file_path}[/cyan] lines {r.start_line}-{r.end_line}")
            syntax = Syntax(r.content[:300], "python", line_numbers=True, start_line=r.start_line, theme="monokai")
            console.print(syntax)
            console.print()
    finally:
        db.close()

@app.command()
def cat(file: str = typer.Argument(..., help="File path, optionally with line range e.g. auth.py:23-45")):
    """Read a file with syntax highlighting"""
    from rich.syntax import Syntax
    from pathlib import Path
    if ":" in file:
        path_str, line_range = file.rsplit(":", 1)
        if "-" in line_range:
            start, end = map(int, line_range.split("-"))
        else:
            start = end = int(line_range)
    else:
        path_str = file
        start = end = None
    path = Path(path_str)
    if not path.exists():
        console.print(f"[red]✗ File not found: {path_str}[/red]")
        return
    content = path.read_text()
    if start and end:
        lines = content.splitlines()
        content = "\n".join(lines[start-1:end])
    syntax = Syntax(content, path.suffix.lstrip(".") or "text", line_numbers=True, start_line=start or 1, theme="monokai")
    console.print(syntax)

@app.command()
def explain(file: str = typer.Argument(..., help="File to explain")):
    """Explain an entire file"""
    from pm.agent.ask import ask as ask_question
    from pathlib import Path
    path = Path(file)
    if not path.exists():
        console.print(f"[red]✗ File not found: {file}[/red]")
        return
    content = path.read_text()
    ask_question(f"Explain this entire file in detail:\n\n```\n{content}\n```")

@app.command()
def diff():
    """Explain the last git commit"""
    import subprocess
    from pm.agent.ask import ask as ask_question
    result = subprocess.run(["git", "diff", "HEAD~1", "HEAD"], capture_output=True, text=True)
    if result.returncode != 0:
        console.print("[red]✗ Not a git repo or no commits yet.[/red]")
        return
    if not result.stdout:
        console.print("[yellow]No changes in last commit.[/yellow]")
        return
    ask_question(f"Explain what changed in this git diff and why:\n\n```diff\n{result.stdout[:3000]}\n```")

@app.command()
def history():
    """Show conversation history"""
    from pm.db.database import LocalSession
    from pm.db.queries import get_recent_conversation
    from pm.utils.state import get_active_repo
    db = LocalSession()
    try:
        active = get_active_repo()
        if not active:
            console.print("[red]✗ No active repo. Run 'pm cd' first.[/red]")
            return
        repo_id, repo_name = active
        convos = get_recent_conversation(db, repo_id=repo_id, limit=20)
        if not convos:
            console.print("[yellow]No conversation history yet.[/yellow]")
            return
        for c in reversed(convos):
            role_color = "green" if c.role == "user" else "blue"
            console.print(f"[{role_color}]{c.role.upper()}:[/{role_color}] {c.content[:200]}")
            console.print()
    finally:
        db.close()

@app.command()
def clear():
    """Clear conversation history"""
    from pm.db.database import LocalSession
    from pm.db.models import Conversation
    from pm.utils.state import get_active_repo
    db = LocalSession()
    try:
        active = get_active_repo()
        if not active:
            console.print("[red]✗ No active repo. Run 'pm cd' first.[/red]")
            return
        repo_id, repo_name = active
        db.query(Conversation).filter(Conversation.repo_id == repo_id).delete()
        db.commit()
        console.print(f"[green]✓ Cleared conversation history for '{repo_name}'[/green]")
    finally:
        db.close()

@app.command()
def save(name: str = typer.Argument(..., help="Name for the saved conversation")):
    """Save conversation to markdown file"""
    from pm.db.database import LocalSession
    from pm.db.queries import get_recent_conversation
    from pm.utils.state import get_active_repo
    from pathlib import Path
    db = LocalSession()
    try:
        active = get_active_repo()
        if not active:
            console.print("[red]✗ No active repo. Run 'pm cd' first.[/red]")
            return
        repo_id, repo_name = active
        convos = get_recent_conversation(db, repo_id=repo_id, limit=100)
        if not convos:
            console.print("[yellow]No conversation history to save.[/yellow]")
            return
        output = f"# Polymath — {repo_name}\n\n"
        for c in reversed(convos):
            role = "**You**" if c.role == "user" else "**Polymath**"
            output += f"{role}\n\n{c.content}\n\n---\n\n"
        path = Path(f"{name}.md")
        path.write_text(output)
        console.print(f"[green]✓ Saved to {path}[/green]")
    finally:
        db.close()

@app.command()
def export():
    """Export conversation as markdown to clipboard"""
    from pm.db.database import LocalSession
    from pm.db.queries import get_recent_conversation
    from pm.utils.state import get_active_repo
    import subprocess
    db = LocalSession()
    try:
        active = get_active_repo()
        if not active:
            console.print("[red]✗ No active repo. Run 'pm cd' first.[/red]")
            return
        repo_id, repo_name = active
        convos = get_recent_conversation(db, repo_id=repo_id, limit=100)
        if not convos:
            console.print("[yellow]No conversation history to export.[/yellow]")
            return
        output = f"# Polymath — {repo_name}\n\n"
        for c in reversed(convos):
            role = "**You**" if c.role == "user" else "**Polymath**"
            output += f"{role}\n\n{c.content}\n\n---\n\n"
        subprocess.run(["pbcopy"], input=output.encode())
        console.print("[green]✓ Conversation copied to clipboard[/green]")
    finally:
        db.close()

@app.command()
def share():
    """Generate shareable link for active repo"""
    console.print("[green]Coming soon — web interface in development[/green]")

if __name__ == "__main__":
    app()