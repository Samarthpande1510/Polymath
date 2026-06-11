from pathlib import Path
from pm.indexer.crawler import crawl
from pm.indexer.chunker import chunk_file, detect_language
from pm.vector.store import init_collection, get_embedding, store_embedding
from pm.db.database import LocalSession
from pm.db.queries import create_repo, create_file, create_chunk, get_repo_by_path
from pm.db.models import Repo
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def index_repo(path: str, url: str = None) -> Repo:
    root = Path(path).resolve()
    name = root.name
    db = LocalSession()
    try:
        console.print(f"[bold]Indexing [green]{name}[/green]...[/bold]")
        repo = create_repo(db, name, path, url)
        init_collection()
        files = crawl(root)
        console.print(f"Found [green]{len(files)}[/green] files")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Indexing files...", total=len(files))
            for f in files:
                progress.update(task, description=f"Indexing [cyan]{f.name}[/cyan]")
                file = create_file(db, repo.id, str(f), detect_language(f))
                chunks = chunk_file(f)
                for chunk in chunks:
                    chunk_record = create_chunk(
                        db,
                        file_id=file.id,
                        repo_id=repo.id,
                        content=chunk["content"],
                        start_line=chunk["start_line"],
                        end_line=chunk["end_line"]
                    )
                    vector = get_embedding(chunk["content"])
                    store_embedding(chunk_record.id, repo.id, vector, {
                        "file_path": str(f),
                        "language": detect_language(f) or "unknown",
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"]
                    })
                progress.advance(task)

        repo.indexed_at = datetime.utcnow()
        db.commit()
        console.print(f"[green]✓ Indexed {name} successfully[/green]")
        return repo

    except Exception as e:
        db.rollback()
        console.print(f"[red]✗ Error: {e}[/red]")
        raise e
    finally:
        db.close()

