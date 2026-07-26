"""
Qdrant vector client — case embeddings and semantic similarity search.
"""

from typing import Any, Dict, List, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from loguru import logger

from app.config import get_settings

settings = get_settings()

_client: Optional[AsyncQdrantClient] = None


async def init_qdrant():
    global _client
    _client = AsyncQdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
    )
    # Ensure the collection exists
    collections_response = await _client.get_collections()
    existing = [c.name for c in collections_response.collections]
    if settings.QDRANT_COLLECTION not in existing:
        await _client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=settings.QDRANT_VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"Qdrant collection '{settings.QDRANT_COLLECTION}' created.")
    else:
        logger.info(f"Qdrant collection '{settings.QDRANT_COLLECTION}' verified.")


def get_qdrant() -> AsyncQdrantClient:
    if not _client:
        raise RuntimeError("Qdrant client not initialized. Call init_qdrant() first.")
    return _client


async def upsert_vectors(
    points: List[PointStruct],
    collection: Optional[str] = None,
) -> None:
    """Upsert a batch of vector points."""
    client = get_qdrant()
    await client.upsert(
        collection_name=collection or settings.QDRANT_COLLECTION,
        points=points,
    )


async def search_similar(
    query_vector: List[float],
    top_k: int = 10,
    score_threshold: float = 0.65,
    filter: Optional[Filter] = None,
    collection: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search for semantically similar cases."""
    client = get_qdrant()
    results = await client.search(
        collection_name=collection or settings.QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        score_threshold=score_threshold,
        query_filter=filter,
        with_payload=True,
    )
    return [
        {"case_id": r.payload.get("case_id"), "score": r.score, "payload": r.payload}
        for r in results
    ]
