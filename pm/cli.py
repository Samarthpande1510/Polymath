import typer
from rich.console import Console
from pm.utils.__init__ import init as init_polymath
from pm.utils.doctor import doctor as polymath_doctor
from pm.indexer.indexer import index_repo
from pm.agent.ask import ask as ask_question
app = typer.Typer(help="Polymath — ask anything about any codebase")
console = Console()

@app.command()
def cd(path: str = typer.Argument(..., help="URL or local path to repo")):
    """Set active repository"""
    index_repo(path)

@app.command()
def cat(file: str = typer.Argument(..., help="File path, optionally with line range e.g. auth.py:23-45")):
    """Read a file with syntax highlighting"""
    console.print(f"[green]Reading: {file}[/green]")

@app.command()
def ask(question: str = typer.Argument(..., help="Question to ask about the codebase")):
    """Ask a question about the active repository"""
    ask_question(question)

@app.command()
def ls():
    """List all indexed repositories"""
    console.print("[green]Listing repos...[/green]")

@app.command()
def status():
    """Show active repo and current context"""
    console.print("[green]Status...[/green]")

@app.command()
def rm(repo: str = typer.Argument(..., help="Repo name to remove")):
    """Remove an indexed repository"""
    console.print(f"[green]Removing: {repo}[/green]")

@app.command()
def refresh():
    """Re-index the active repository"""
    console.print("[green]Refreshing...[/green]")

@app.command()
def find(query: str = typer.Argument(..., help="Keyword to search for")):
    """Find files and functions by keyword"""
    console.print(f"[green]Finding: {query}[/green]")

@app.command()
def explain(file: str = typer.Argument(..., help="File to explain")):
    """Explain an entire file"""
    console.print(f"[green]Explaining: {file}[/green]")

@app.command()
def diff():
    """Explain the last git commit"""
    console.print("[green]Diffing...[/green]")

@app.command()
def history():
    """Show conversation history"""
    console.print("[green]History...[/green]")

@app.command()
def clear():
    """Clear conversation history"""
    console.print("[green]Clearing history...[/green]")

@app.command()
def save(name: str = typer.Argument(..., help="Name for the saved conversation")):
    """Save conversation to markdown"""
    console.print(f"[green]Saving as: {name}[/green]")

@app.command()
def init():
    """First time setup — spins up Docker, Postgres, Qdrant"""
    init_polymath()

@app.command()
def doctor():
    """Check if everything is running correctly"""
    polymath_doctor()

@app.command()
def share():
    """Generate shareable link for active repo"""
    console.print("[green]Generating share link...[/green]")

@app.command()
def export():
    """Export conversation as markdown"""
    console.print("[green]Exporting...[/green]")

if __name__ == "__main__":
    app()