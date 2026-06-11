from pathlib import Path
import pathspec

SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.zip', '.tar', '.gz', '.rar',
    '.pyc', '.class', '.o', '.exe', '.bin',
    '.mp4', '.mp3', '.avi', '.mov',
    '.ttf', '.woff', '.woff2',
}

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
    
def crawl(root: Path):
    gitignore = load_gitignore(root)
    files = []

    for path in root.rglob("*"):
        if path.is_dir():
            continue

        if any(path in SKIP_DIRS for path in path.parts):
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