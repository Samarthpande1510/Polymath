# Polymath

Ask anything about any codebase. Local, private, fast.

```
pm cd https://github.com/pallets/click
pm ask "how does argument parsing work?"
```

Polymath indexes your code into a local vector database and answers questions in plain English with exact file citations and line numbers. Your code never leaves your machine.

---

## How it works

```
pm cd <repo>
  → clone repo to current directory (if URL)
  → crawl all files (respects .gitignore)
  → chunk code at 50-line boundaries
  → embed each chunk with Gemini embeddings
  → store vectors locally in Qdrant
  → store metadata in SQLite

pm ask "question"
  → embed the question
  → search local Qdrant for top 8 relevant chunks
  → fetch full chunk content from SQLite
  → inject context + conversation history into prompt
  → stream answer from Gemini 2.5 Flash or Ollama
  → save to conversation history
```

Embeddings and vector search run entirely on your machine. Only the question + relevant code snippets are sent to the LLM.

---

## Requirements

- Python 3.11+
- Gemini API key — free at [aistudio.google.com](https://aistudio.google.com)
- For Ollama mode: [Ollama](https://ollama.com) installed and running
- Git (for cloning GitHub repos)

No Docker. No Postgres. No extra services.

---

## Install

### Recommended

```bash
brew install pipx
pipx install polymath-cli
pipx ensurepath
source ~/.zshrc
```

### pip

```bash
pip install polymath-cli
```

### Binary (no Python needed)

Download `pm` from [GitHub Releases](https://github.com/Samarthpande1510/Polymath/releases), then:

```bash
chmod +x pm
sudo mv pm /usr/local/bin/pm
```

---

## First time setup

```bash
pm init
```

This asks you to choose an AI provider and enter your API key. Everything is stored in `~/.polymath/`.

```bash
pm doctor    # verify everything is ready
```

---

## Quick start

```bash
# index a GitHub repo — clones it to your current directory AND indexes it
pm cd https://github.com/pallets/click

# index a local project
pm cd .
pm cd /path/to/your/project

# ask questions
pm ask "how does authentication work?"
pm ask "where is the database connection set up?"

# ask follow up questions — Polymath remembers context
pm ask "what happens if the connection fails?"
```

---

## AI providers

### Gemini (default)

Uses Gemini 2.5 Flash for generation and Gemini embeddings for indexing.

- One API key, free at [aistudio.google.com](https://aistudio.google.com)
- Free tier: 20 requests/day
- Enable billing for unlimited usage at essentially $0 for personal use

```bash
pm init   # choose gemini
```

If your quota runs out:

```bash
# option 1 — use a new API key
pm config GEMINI_API_KEY your-new-key

# option 2 — switch to Ollama
pm config LLM_PROVIDER ollama
```

### Ollama (fully offline)

Uses a local model for generation. No API key needed for questions after initial setup.

```bash
pm init   # choose ollama
```

Recommended models for code Q&A:

| Model | Size | Best for |
|-------|------|----------|
| `qwen2.5-coder:7b` | 4GB | Best for code, excellent quality |
| `qwen2.5-coder:1.5b` | 1GB | Code focused, fast and small |
| `mistral:7b` | 4GB | Great general purpose |
| `llama3.2:1b` | 1GB | Tiny and fast |

Avoid `codellama` — poor instruction following leads to hallucinations.

```bash
ollama pull qwen2.5-coder:7b
pm config OLLAMA_MODEL qwen2.5-coder:7b
```

Note: Ollama mode still uses Gemini embeddings for indexing. Embeddings only run once per repo — after that everything is fully offline.

Switch providers or models anytime:

```bash
pm config LLM_PROVIDER ollama
pm config LLM_PROVIDER gemini
pm config OLLAMA_MODEL qwen2.5-coder:7b
pm config GEMINI_API_KEY your-new-key
```

---

## Commands

### Setup

```bash
pm init                    # first time setup
pm doctor                  # check database, Qdrant, Ollama health
```

### Indexing

`pm cd` with a GitHub URL clones the repo directly into your current directory and indexes it — you get the code AND the intelligence in one command.

```bash
pm cd https://github.com/user/repo          # clone to current dir + index
pm cd .                                     # index current directory
pm cd /path/to/project                      # index any local path
pm refresh                                  # re-index the active repo
pm ls                                       # list all indexed repos
pm status                                   # show active repo and stats
pm pwd                                      # show active repo path
```

### Removing repos

```bash
pm rm <repo-name>                           # remove from index only
pm rm <repo-name> -r                        # remove from index AND delete folder from disk
```

### Asking questions

```bash
pm ask "how does authentication work?"
pm ask "where is the database connection set up?"
pm ask "what happens when a user signs up?"
pm explain src/auth.py                      # explain an entire file
pm diff                                     # explain the last git commit
```

### Reading code

```bash
pm cat src/auth.py                          # read file with syntax highlighting
pm cat src/auth.py:23-45                    # read specific lines
pm find "jwt"                               # find all chunks containing a keyword
```

### Conversation

```bash
pm history                                  # show conversation history
pm clear                                    # clear conversation history
pm save my-session                          # save conversation to markdown
pm export                                   # copy conversation to clipboard
```

### Config

```bash
pm config LLM_PROVIDER ollama
pm config LLM_PROVIDER gemini
pm config OLLAMA_MODEL qwen2.5-coder:7b
pm config GEMINI_API_KEY your-new-key
```

---

## Architecture

```
polymath/
  pm/
    cli.py              # Typer commands
    agent/
      ask.py            # retrieval + LLM + streaming
    indexer/
      crawler.py        # file discovery, respects .gitignore
      chunker.py        # 50-line chunks with overlap
      indexer.py        # orchestrates indexing pipeline
    db/
      models.py         # SQLAlchemy models
      queries.py        # database operations
      database.py       # SQLite engine
    vector/
      store.py          # embedded Qdrant + Gemini embeddings
    utils/
      init.py           # pm init
      doctor.py         # pm doctor
      state.py          # active repo tracking
```

Data stored in `~/.polymath/`:

```
~/.polymath/
  .env                  # config and API keys
  polymath.db           # SQLite database
  qdrant_data/          # local vector store
```

---

## Security

- Code stays local — indexing runs entirely on your machine
- Vectors stay local — Qdrant runs embedded, no server
- Only snippets leave — relevant code chunks sent to LLM for generation
- No accounts — no login, no tracking, no telemetry
- Private repos — clone locally, `pm cd` the path, nothing uploaded
- Ollama mode — 100% offline after initial indexing

---

## Platform support

- macOS — fully supported
- Linux — should work, not fully tested
- Windows — supported, requires Git for Windows for GitHub URL cloning

---

## Troubleshooting

**Python version error**

Polymath requires Python 3.11+. Use pipx which handles this automatically:

```bash
brew install pipx
pipx install polymath-cli
```

**Command not found after install**

```bash
pipx ensurepath
source ~/.zshrc
pm --version
```

**Ollama not responding**

```bash
ollama serve
ollama pull qwen2.5-coder:7b
pm doctor
```

**Gemini quota exceeded during indexing**

```bash
pm config GEMINI_API_KEY your-new-key
# or enable billing at aistudio.google.com
# or switch to Ollama (still needs Gemini for embeddings)
```

**Gemini quota exceeded during pm ask**

```bash
pm config LLM_PROVIDER ollama   # switch to fully offline generation
# or
pm config GEMINI_API_KEY your-new-key
```

**Re-initialize config**

```bash
rm ~/.polymath/.env
pm init
```

**Windows: Git not found**

Download Git from [git-scm.com/download/win](https://git-scm.com/download/win) and restart your terminal.

---

## Roadmap

- Tree-sitter AST chunking — chunk at function/class boundaries
- Multi-query RAG Fusion — better retrieval quality
- VS Code extension
- Homebrew formula
- Web interface

---

## Contributing

```bash
git clone https://github.com/Samarthpande1510/Polymath
cd Polymath
uv sync
pm init
pm cd .
pm ask "how does the indexer work?"
```

---

## License

MIT