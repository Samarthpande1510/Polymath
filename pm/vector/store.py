from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

client = QdrantClient(host="localhost",port=6334)
VECTOR_SIZE = 768
COLLECTION_NAME = "polymath_chunks"
model = SentenceTransformer("BAAI/bge-base-en-v1.5")


def init_collection():
    existing = client.get_collections().collections
    names = [c.name for c in existing]
    if COLLECTION_NAME not in names:
        client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE,distance=Distance.COSINE)
        )
    
def get_embedding(text: str, is_query: bool = False) -> list[float]:
    if is_query:
        text = f"Represent this sentence for searching relevant passages: {text}"
    return model.encode(text).tolist()
    
def store_embedding(chunk_id: int, repo_id: int, vector: list[float], payload: dict):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct
            (
                id=chunk_id,
                vector=vector,
                payload={"repo_id": repo_id, **payload}
            )
        ]
    )

def search(repo_id: int, query_vector: list[float], limit: int = 10) -> list[dict]:
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=[FieldCondition(key="repo_id", match=MatchValue(value=repo_id))]
        ),
        limit=limit
    )
    return [{"chunk_id": r.id, "score": r.score, **r.payload} for r in results.points]



