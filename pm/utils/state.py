from pathlib import Path
from dotenv import load_dotenv
import os

def set_active_repo(repo_id: int, repo_name: str):
    env_path = Path.home() / ".polymath" / ".env"
    lines = env_path.read_text().splitlines()
    lines = [l for l in lines if not l.startswith("ACTIVE_REPO")]
    lines.append(f"ACTIVE_REPO_ID={repo_id}")
    lines.append(f"ACTIVE_REPO_NAME={repo_name}")
    env_path.write_text("\n".join(lines))

def get_active_repo() -> tuple[int, str] | None:
    env_path = Path.home() / ".polymath" / ".env"
    load_dotenv(env_path, override=True)
    repo_id = os.getenv("ACTIVE_REPO_ID")
    repo_name = os.getenv("ACTIVE_REPO_NAME")
    if not repo_id:
        return None
    return int(repo_id), repo_name