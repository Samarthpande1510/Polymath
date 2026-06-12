from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue

VECTOR_SIZE = 768
COLLECTION_NAME = "polymath_chunks"

_client = None
_model = None

def _get_client():
    return QdrantClient(host="localhost", port=6334)

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("BAAI/bge-base-en-v1.5")
    return _model

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
    return _get_model().encode(text).tolist()

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    return _get_model().encode(
        texts,
        batch_size=32,
        show_progress_bar=False
    ).tolist()

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