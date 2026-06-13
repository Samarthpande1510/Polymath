from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from dotenv import load_dotenv
from pathlib import Path
import os

VECTOR_SIZE = 768
COLLECTION_NAME = "polymath_chunks"

_genai = None

def _get_client():
    data_path = str(Path.home() / ".polymath" / "qdrant_data")
    return QdrantClient(path=data_path)

def _get_genai():
    global _genai
    if _genai is None:
        from google import genai
        load_dotenv(Path.home() / ".polymath" / ".env")
        _genai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _genai

def init_collection():
    existing = _get_client().get_collections().collections
    names = [c.name for c in existing]
    if COLLECTION_NAME not in names:
        _get_client().create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )

def get_embedding(text: str, is_query: bool = False) -> list[float]:
    if is_query:
        text = f"Represent this sentence for searching relevant passages: {text}"
    result = _get_genai().models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config={"output_dimensionality": 768}
    )
    return result.embeddings[0].values

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    result = _get_genai().models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config={"output_dimensionality": 768}
    )
    return [e.values for e in result.embeddings]

def store_embedding(chunk_id: int, repo_id: int, vector: list[float], payload: dict):
    _get_client().upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=chunk_id,
                vector=vector,
                payload={"repo_id": repo_id, **payload}
            )
        ]
    )

def store_embeddings_batch(repo_id: int, points: list[dict]):
    _get_client().upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload={"repo_id": repo_id, **p["payload"]}
            )
            for p in points
        ]
    )

def search(repo_id: int, query_vector: list[float], limit: int = 10) -> list[dict]:
    results = _get_client().query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=[FieldCondition(key="repo_id", match=MatchValue(value=repo_id))]
        ),
        limit=limit
    )
    return [{"chunk_id": r.id, "score": r.score, **r.payload} for r in results.points]

def delete_repo_vectors(repo_id: int):
    _get_client().delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[FieldCondition(key="repo_id", match=MatchValue(value=repo_id))]
        )
    )