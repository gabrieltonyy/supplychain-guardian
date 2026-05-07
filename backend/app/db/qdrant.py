from qdrant_client import AsyncQdrantClient

from app.core.config import settings


qdrant_client = AsyncQdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
)


async def search_similar_suppliers(
    supplier_id: str,
    top_k: int = 10,
    filters: dict | None = None,
) -> list[dict]:
    """
    Mock-first supplier vector search.

    In production, this will:
    - fetch supplier embedding by supplier_id,
    - search Qdrant supplier_profiles collection,
    - apply metadata filters,
    - return ranked suppliers.
    """

    _ = filters

    mock_results = [
        {
            "id": "SUP-ALT-001",
            "name": "Apex India Manufacturing",
            "similarity_score": 0.94,
        },
        {
            "id": "SUP-ALT-002",
            "name": "EuroTech Components",
            "similarity_score": 0.89,
        },
        {
            "id": "SUP-ALT-003",
            "name": "VietPro Industrial",
            "similarity_score": 0.84,
        },
    ]

    return mock_results[:top_k]