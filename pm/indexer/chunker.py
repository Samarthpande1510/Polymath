from pathlib import Path

LANGUAGE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.go': 'go',
    '.rs': 'rust',
    '.java': 'java',
    '.rb': 'ruby',
    '.cpp': 'cpp',
    '.c': 'c',
    '.cs': 'c_sharp',
}

def detect_language(file_path: Path) -> str | None:
    return LANGUAGE_MAP.get(file_path.suffix.lower())

def fallback_chunk(lines: list[str], chunk_size: int = 50, overlap: int = 10) -> list[dict]:
    chunks = []
    i = 0
    while i < len(lines):
        end = min(i + chunk_size, len(lines))
        chunk_lines = lines[i:end]
        content = "\n".join(chunk_lines)
        if content.strip():  
            chunks.append({
                "content": content,
                "start_line": i + 1,  
                "end_line": end
            })
        i += chunk_size - overlap  
    return chunks

def chunk_file(file_path: Path) -> list[dict]:
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    
    if '\x00' in content:
        return []

    lines = content.splitlines()
    if not lines:
        return []

    language = detect_language(file_path)
    return fallback_chunk(lines)

if __name__ == "__main__":
    test_file = Path("pm/cli.py")
    chunks = chunk_file(test_file)
    print(f"Found {len(chunks)} chunks")
    for c in chunks:
        print(f"  lines {c['start_line']}-{c['end_line']}: {c['content'][:50]}...")