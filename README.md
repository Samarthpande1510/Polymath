<div align="center">

# Polymath

**Ask anything about any codebase. Instant answers, zero data leaks.**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## What is Polymath?

Polymath is a local-first codebase intelligence CLI. Point it at any repository — public or private — and ask questions in plain English. It indexes your code into a local vector database, retrieves the most relevant chunks, and answers with exact file citations and line numbers.

**Your code never leaves your machine.**

```bash
pm cd https://github.com/pallets/click
pm ask "how does argument parsing work?"
```

```
## Argument Parsing in Click

Click's argument parsing is handled in `src/click/core.py` lines 1089-1134.
When a command is invoked, `Command.make_context()` creates a `Context` object
and calls `Command.parse_args()` which delegates to each parameter's
`Parameter.consume_value()` method...

## How to use this in your codebase

from click import argument, command

@command()
@argument('filename')
def process(filename):
    click.echo(f'Processing {filename}')
```

---

## Why Polymath?

| Feature | Polymath | GitHub Copilot | ChatGPT |
|--------|----------|----------------|---------|
| Works on private repos | ✅ Local only | ❌ Sends to GitHub | ❌ Sends to OpenAI |
| No internet required | ✅ Fully offline | ❌ Cloud dependent | ❌ Cloud dependent |
| Remembers conversation | ✅ Per-repo history | ❌ No memory | ❌ Resets each chat |
| Any language | ✅ All languages | ✅ All languages | ✅ All languages |
| Free | ✅ Always | ❌ $10/month | ❌ $20/month |
| Cites exact lines | ✅ Always | ❌ No citations | ❌ No citations |

---

## Requirements

- **Python 3.11+**
- **Docker Desktop** — [download here](https://www.docker.com/products/docker-desktop/)
- **Gemini API key** — free at [aistudio.google.com](https://aistudio.google.com)
- macOS or Linux

---

## Installation

### Recommended — pipx (works on any Mac)

```bash
brew install pipx
pipx install polymath-cli
```

pipx handles Python version management automatically. No need to worry about which Python version you have.

### Alternative — pip (requires Python 3.11+)

```bash
pip install polymath-cli
```

### First time setup

Make sure Docker Desktop is running, then:

```bash
pm init
```

This will:
1. Ask for your Gemini API key (get one free at [aistudio.google.com](https://aistudio.google.com))
2. Create `~/.polymath/` config directory
3. Spin up local Postgres and Qdrant via Docker
4. Write your config to `~/.polymath/.env`

Run once, never again.

### Health check

```bash
pm doctor
```

All three should be green before using Polymath.

---

## Quick Start

```bash
# index a repo
pm cd .                                      # index current directory
pm cd https://github.com/pallets/click       # clone and index a public repo

# ask questions
pm ask "how does authentication work?"
pm ask "where is the database connection set up?"

# read code
pm cat src/auth.py:23-45                     # read specific lines
pm find "jwt"                                # find all mentions of jwt
```

---

## Commands

### Indexing

```bash
pm cd .                                      # index current directory
pm cd /path/to/project                       # index any local path
pm cd https://github.com/user/repo           # clone and index a public repo
pm refresh                                   # re-index the active repo
pm rm <repo-name>                            # remove an indexed repo
```

### Asking Questions

```bash
pm ask "how does authentication work?"
pm ask "where is the database connection set up?"
pm ask "what happens when a user signs up?"
pm explain src/auth.py                       # explain an entire file
pm diff                                      # explain the last git commit
```

### Reading Code

```bash
pm cat src/auth.py                           # read file with syntax highlighting
pm cat src/auth.py:23-45                     # read specific lines
pm find "jwt"                                # find all chunks containing a keyword
```

### Conversation

```bash
pm history                                   # show conversation history
pm clear                                     # clear conversation history
pm save my-session                           # save conversation to markdown
pm export                                    # copy conversation to clipboard
```

### Repo Management

```bash
pm ls                                        # list all indexed repos
pm status                                    # show active repo and stats
```

### Setup

```bash
pm init                                      # first time setup
pm doctor                                    # check Docker, Postgres, Qdrant health
```

---

## How it works

```
pm cd <repo>
  → crawl all files (respects .gitignore)
  → chunk code at 50-line boundaries
  → embed each chunk with BGE-base-en-v1.5
  → store vectors in local Qdrant
  → store metadata in local Postgres

pm ask "question"
  → embed the question
  → search Qdrant for top 8 most relevant chunks
  → fetch full chunk content from Postgres
  → inject context + conversation history into prompt
  → stream answer from Gemini 2.5 Flash
  → save to conversation history
```

All vector search and storage happens locally. Only the question + relevant code snippets are sent to Gemini to generate the answer.

---

## Architecture

```
polymath/
  pm/
    cli.py           # Typer commands — the user interface
    agent/
      ask.py         # retrieval + LLM + streaming answer
    indexer/
      crawler.py     # file discovery, respects .gitignore
      chunker.py     # 50-line chunks with overlap
      indexer.py     # orchestrates the full indexing pipeline
    db/
      models.py      # SQLAlchemy: repos, files, chunks, conversations
      queries.py     # all Postgres operations
      database.py    # engine + session factory
    vector/
      store.py       # Qdrant operations + BGE embeddings
    utils/
      init.py        # pm init — Docker setup + API key prompt
      doctor.py      # pm doctor — health checks
      state.py       # active repo tracking via ~/.polymath/.env
```

**Data stores:**
- `~/.polymath/` — config, docker-compose, .env
- `~/.polymath/repos/` — cloned GitHub repos
- Postgres (port 5433) — repo metadata, file records, chunks, conversation history
- Qdrant (port 6334) — vector embeddings for semantic search

---

## Security

Polymath is designed with privacy as a first principle.

- **Code stays local** — indexing runs entirely on your machine
- **Vectors stay local** — Qdrant runs in Docker on your machine
- **Only snippets leave** — when you ask a question, the relevant code chunks (not your entire codebase) are sent to Gemini to generate the answer
- **No accounts** — no login, no tracking, no telemetry
- **Private repos** — clone them yourself, `pm cd` the local path. Nothing is uploaded

If you need 100% air-gapped operation, swap Gemini for a local Ollama model — only the `ask.py` file needs changing.

---

## Configuration

Polymath stores all config in `~/.polymath/.env`:

```env
DATABASE_URL=postgresql://polymath:polymath@localhost:5433/polymath
QDRANT_HOST=localhost
QDRANT_PORT=6334
GEMINI_API_KEY=your-key-here
ACTIVE_REPO_ID=1
ACTIVE_REPO_NAME=myproject
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com).

---

## Troubleshooting

**`pm init` fails with Docker error**
Make sure Docker Desktop is running before running `pm init`.

**`pm doctor` shows Postgres not running**
Run `pm init` again — it will restart the Docker containers without overwriting your config.

**Python version error during install**
Use pipx instead:
```bash
brew install pipx
pipx install polymath-cli
```

**Command not found after install**
Add pipx to your PATH:
```bash
pipx ensurepath
source ~/.zshrc
```

---

## Roadmap

- [ ] Tree-sitter AST chunking — chunk at function/class boundaries for better context
- [ ] Multi-query RAG Fusion — generate query variations for better retrieval
- [ ] `pm share` — generate shareable links for public repos
- [ ] Web interface — browser-based chat UI
- [ ] Ollama support — 100% offline mode with local LLMs
- [ ] GitHub OAuth — index private repos without cloning manually
- [ ] VS Code extension

---

## Contributing

```bash
git clone https://github.com/Samarthpande1510/Polymath
cd Polymath
uv install
pm init
pm cd .
pm ask "how does the indexer work?"
```

---

## License

MIT — do whatever you want with it.

---

<div align="center">
Built with Python, Qdrant, PostgreSQL, BGE embeddings, and Gemini 2.5 Flash.
</div>