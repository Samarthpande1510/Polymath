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

No Docker. No Postgres. No extra services.

---

## Install

### Recommended

```bash
brew install pipx
pipx install polymath-cli
pm init
```

### pip

```bash
pip install polymath-cli
pm init
```

### Binary (no Python needed)

Download `pm` from [GitHub Releases](https://github.com/Samarthpande1510/Polymath/releases), then:

```bash
chmod +x pm
mv pm /usr/local/bin/pm
pm init
```

---

## First time setup

Run once:

```bash
pm init
```

This asks you to choose an AI provider:

```
Choose AI provider for answering questions (gemini/ollama): gemini
Enter your Gemini API key: ...
✓ API key valid
✓ Database ready
✓ Polymath ready!
```

Everything is stored in `~/.polymath/`.

---

## AI providers

### Gemini (default)

Uses Gemini 2.5 Flash for generation and Gemini embeddings for indexing.

- One API key, free at [aistudio.google.com](https://aistudio.google.com)
- Free tier: 20 questions/day per key
- Enable billing for unlimited usage — costs ~$0 for personal use

```bash
pm init   # choose gemini
```

### Ollama (fully offline)

Uses a local model for generation. No API key needed for questions after initial setup.

```bash
pm init   # choose ollama
```

Recommended models for code Q&A:

| Model | Size | Best for |
|-------|------|----------|
| `codellama` | 4GB | Code explanation, best quality |
| `qwen2.5-coder:1.5b` | 1GB | Code focused, fast |
| `mistral` | 4GB | General purpose, good at instructions |
| `llama3.2:1b` | 1GB | Tiny and fast |

```bash
ollama pull codellama
pm config OLLAMA_MODEL codellama
pm ask "how does authentication work?"
```

Note: Ollama mode still uses Gemini embeddings for indexing (`pm cd`). Embeddings only run once per repo — after that, everything is fully offline.

Switch providers anytime:

```bash
pm config LLM_PROVIDER ollama
pm config LLM_PROVIDER gemini
pm config OLLAMA_MODEL codellama
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

```bash
pm cd .                                     # index current directory
pm cd /path/to/project                      # index any local path
pm cd https://github.com/user/repo          # clone and index a public repo
pm refresh                                  # re-index the active repo
pm rm <repo-name>                           # remove an indexed repo
pm ls                                       # list all indexed repos
pm status                                   # show active repo and stats
pm pwd                                      # show active repo path
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
pm config OLLAMA_MODEL codellama
pm config GEMINI_API_KEY your-key
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
  repos/                # cloned GitHub repos
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
ollama serve           # start Ollama
ollama pull codellama  # make sure model is downloaded
pm doctor              # verify everything is green
```

**Rate limit on Gemini free tier**

Free tier allows 20 questions/day. Enable billing at [aistudio.google.com](https://aistudio.google.com) for unlimited usage. Costs essentially nothing for personal use (~$0.15 per million tokens).

Alternatively switch to Ollama for unlimited offline usage:

```bash
pm config LLM_PROVIDER ollama
```

**Re-initialize config**

```bash
rm ~/.polymath/.env
pm init
```

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