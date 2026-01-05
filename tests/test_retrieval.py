import os
import pytest
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from src.utils import get_device


load_dotenv()


@pytest.mark.skipif(
    not os.getenv("QDRANT_URL") or not os.getenv("QDRANT_API_KEY"),
    reason="Qdrant credentials not set"
)

@pytest.mark.skipif(
    not os.getenv("TEST_COLLECTION_NAME"),
    reason="Contract collection name not set"
)

def test_qdrant_retrieval():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("TEST_COLLECTION_NAME")
    query_text = "contract termination clauses"
    top_k = 5


    # Qdrant setup
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key
        )

    device = get_device()
    model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

    query_embedding = model.encode(query_text).tolist()
    response = client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=top_k,
        with_payload=True
        )

    points = response.points
    assert points, "No retrieval results returned"
    assert len(points) <= top_k

    top_hit = points[0]
    assert top_hit.score > 0, "Top hit has invalid similarity score"
    assert "text" in top_hit.payload, "Missing document text in payload"
    assert "metadata" in top_hit.payload, "Missing metadata in payload"
    
    # Cleanup
    # client.delete_collection(collection_name=collection_name)


