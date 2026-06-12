from sqlalchemy.orm import Session
from pm.db.models import Conversation,Repo,Chunk,File
from datetime import datetime

def create_repo(db, name: str, path: str, url: str) -> Repo:
    repos = Repo(
        name = name,
        path = path,
        url = url,
    )
    db.add(repos)
    db.commit()
    db.refresh(repos)

    return repos

def get_repo_by_path(db, path: str) -> Repo | None:
    return db.query(Repo).filter(Repo.path == path).first()

def get_repo_by_name(db, name: str) -> Repo | None:
    return db.query(Repo).filter(Repo.name == name).first()

def get_all_repos(db) -> list[Repo]:
    return db.query(Repo).all()

def delete_repo(db, repo_id: int) -> None:
    remove = db.query(Repo).filter(Repo.id == repo_id).first()
    if not remove:
        return
    db.delete(remove)
    db.commit()

def create_file(db, repo_id: int, path: str, language: str) -> File:
    files = File(
        repo_id = repo_id,
        path = path,
        language = language
    )
    db.add(files)
    db.commit()
    db.refresh(files)

    return files

def create_chunk(db, file_id, repo_id, content, start_line, end_line, file_path=""):
    chunks = Chunk(
        file_id=file_id,
        repo_id=repo_id,
        content=content,
        start_line=start_line,
        end_line=end_line,
        file_path=file_path
    )
    db.add(chunks)
    db.commit()
    db.refresh(chunks)

    return chunks

def get_chunks_by_ids(db, chunk_ids: list[int], repo_id: int) -> list[Chunk]:
   return db.query(Chunk).filter(
    Chunk.id.in_(chunk_ids),
    Chunk.repo_id == repo_id
).all()

def save_conversation(db, repo_id: int, role: str, content: str) -> Conversation:
    convo = Conversation(
        repo_id = repo_id,
        role = role,
        content = content
    )
    db.add(convo)
    db.commit()
    db.refresh(convo)

    return convo

def get_recent_conversation(db, repo_id: int, limit: int = 5) -> list[Conversation]:
    return db.query(Conversation).filter(
    Conversation.repo_id == repo_id
).order_by(Conversation.created_at.desc()).limit(limit).all()

def delete_repo_data(db, repo_id: int) -> None:
    db.query(Chunk).filter(Chunk.repo_id == repo_id).delete()
    db.query(File).filter(File.repo_id == repo_id).delete()
    db.query(Conversation).filter(Conversation.repo_id == repo_id).delete()
    db.commit()
    
    