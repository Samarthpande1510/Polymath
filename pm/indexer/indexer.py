from pathlib import Path
from pm.indexer.crawler import crawl
from pm.indexer.chunker import chunk_file, detect_language
from pm.db.database import LocalSession
from pm.db.queries import create_repo, create_file, create_chunk, get_repo_by_path, delete_repo
from pm.db.models import Repo
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from pm.utils.state import set_active_repo
from pm.vector.store import init_collection, get_embedding, store_embedding, get_embeddings_batch
console = Console()

def index_repo(path: str, url: str = None) -> Repo:
    root = Path(path).resolve()
    name = root.name
    db = LocalSession()
    try:
        existing = get_repo_by_path(db, str(root))
        if existing:
            console.print(f"[yellow]'{name}' already indexed — switching to it.[/yellow]")
            set_active_repo(existing.id, existing.name)
            return existing

        console.print(f"[bold]Indexing [green]{name}[/green]...[/bold]")
        repo = create_repo(db, name, str(root), url)
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
                if not chunks:
                    progress.advance(task)
                    continue
                
                # batch embed all chunks in this file at once
                texts = [chunk["content"] for chunk in chunks]
                vectors = get_embeddings_batch(texts)
                
                for chunk, vector in zip(chunks, vectors):
                    chunk_record = create_chunk(
                        db,
                        file_id=file.id,
                        repo_id=repo.id,
                        content=chunk["content"],
                        start_line=chunk["start_line"],
                        end_line=chunk["end_line"],
                        file_path=str(f)
                    )
                    store_embedding(chunk_record.id, repo.id, vector, {
                        "file_path": str(f),
                        "language": detect_language(f) or "unknown",
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"]
                    })
                progress.advance(task)

        repo.indexed_at = datetime.utcnow()
        db.commit()
        set_active_repo(repo.id, repo.name)
        console.print(f"[green]✓ Indexed {name} successfully[/green]")
        return repo

    except Exception as e:
        db.rollback()
        console.print(f"[red]✗ Error: {e}[/red]")
        raise e
    finally:
        db.close()

def reindex_repo(repo_id: int, path: str, name: str):
    from pm.db.queries import delete_repo_data
    from pm.vector.store import delete_repo_vectors

    db = LocalSession()
    try:
        delete_repo_data(db, repo_id)
        delete_repo(db, repo_id)
        try:
            delete_repo_vectors(repo_id)
        except Exception:
            pass
    finally:
        db.close()

    return index_repo(path)