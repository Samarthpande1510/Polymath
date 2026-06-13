from pathlib import Path
import pathspec

SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.zip', '.tar', '.gz', '.rar',
    '.pyc', '.class', '.o', '.exe', '.bin',
    '.mp4', '.mp3', '.avi', '.mov',
    '.ttf', '.woff', '.woff2','.lock'
}
SKIP_FILES = {'uv.lock', 'package-lock.json', 'yarn.lock', 'Pipfile.lock'}

SKIP_DIRS = {
    '.git', '.venv', 'venv', 'node_modules',
    '__pycache__', '.pytest_cache', 'dist', 'build',
    '.next', '.nuxt', 'coverage'
}

def load_gitignore(root: Path) -> pathspec.PathSpec:
    git_path = root / ".gitignore"
    if git_path.exists():
        lines = git_path.read_text().splitlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", lines)
    return pathspec.PathSpec.from_lines("gitwildmatch", [])
    
def crawl(root: Path) -> list[Path]:
    gitignore = load_gitignore(root)
    files = []

    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in SKIP_FILES for part in path.parts):
            continue
        if any(part in SKIP_DIRS for part in path.parts): 
            continue
        if path.suffix.lower() in SKIP_EXTENSIONS:
            continue
        relative = path.relative_to(root)
        if gitignore.match_file(str(relative)):
            continue

        files.append(path)

    return files

if __name__ == "__main__":
    root = Path(".")
    files = crawl(root)
    print(f"Found {len(files)} files")
    for f in files[:10]:
        print(f" {f}")