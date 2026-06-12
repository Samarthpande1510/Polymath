from pm.utils.state import get_active_repo
from pm.db.queries import get_recent_conversation, get_chunks_by_ids, save_conversation
import os
from dotenv import load_dotenv
from pathlib import Path
from rich.console import Console
from pm.db.database import LocalSession
from pm.vector.store import get_embedding, search
from rich.markdown import Markdown
from rich.live import Live
from google import genai
from google.genai import types
import time

console = Console()
load = Path.home() / ".polymath" / ".env"
load_dotenv(load)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask(question: str):
    db = LocalSession()
    try:
        for attempt in range(3):
            try:
                active = get_active_repo()
                if not active:
                    console.print("[red]✗ No active repo. Run 'pm cd' first.[/red]")
                    return
                repo_id, repo_name = active

                convos = get_recent_conversation(db, repo_id=repo_id)
                query_vector = get_embedding(question, is_query=True)
                result = search(repo_id=repo_id, query_vector=query_vector, limit=8)
                ids = [r["chunk_id"] for r in result]
                chunks = get_chunks_by_ids(db, chunk_ids=ids, repo_id=repo_id)

                context = "\n\n".join([
                    f"File: {c.file_path}\nLines {c.start_line}-{c.end_line}:\n{c.content}"
                    for c in chunks
                ])

                history = [
                    {"role": c.role, "content": c.content}
                    for c in convos
                ]

                history_text = ""
                if history:
                    history_text = "\n\nPREVIOUS CONVERSATION:\n"
                    for h in history:
                        role = "User" if h["role"] == "user" else "Assistant"
                        history_text += f"{role}: {h['content']}\n\n"

                prompt = f"""You are Polymath, an elite codebase intelligence assistant with deep expertise in software engineering.

You are analyzing the repository: '{repo_name}'

Your job is to give answers that are so clear and useful that a developer never needs to ask the same question twice.

When answering:
- Explain the WHAT, the WHY, and the HOW
- Always cite exact file names and line numbers
- If multiple files are involved, explain how they connect
- Mention bugs, performance issues, or better approaches you spot

End every answer with "How to use this in your codebase" with a real code example, gotchas, and what to do next.

Format in clean markdown with headers, code blocks with language tags, and bullet points.

If the answer is not in the context say: "I couldn't find this in the indexed codebase. Try 'pm refresh' or rephrase."

Never hallucinate. Only reference what you can see.

CODE CONTEXT:
{context}{history_text}"""

                full_text = ""
                with Live(console=console, refresh_per_second=10) as live:
                    for chunk in client.models.generate_content_stream(
                        model="gemini-2.5-flash",
                        contents=question,
                        config=types.GenerateContentConfig(
                            system_instruction=prompt,
                        )
                    ):
                        if chunk.text:
                            full_text += chunk.text
                            live.update(Markdown(full_text))

                save_conversation(db, repo_id=repo_id, role="user", content=question)
                save_conversation(db, repo_id=repo_id, role="assistant", content=full_text)
                break

            except Exception as e:
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    if attempt < 2:
                        console.print(f"[yellow]Gemini is busy, retrying in {2**attempt}s...[/yellow]")
                        time.sleep(2**attempt)
                        continue
                console.print(f"[red]✗ Error: {e}[/red]")
                break
    finally:
        db.close()