import os
import pytest
from dotenv import load_dotenv
from qdrant_client import QdrantClient

from ingestion.chunking import Chunker
from ingestion.embed_upsert import EmbedUpsert
from src.utils import get_next_collection_name


load_dotenv()


# Fixture to provide chunked contract
@pytest.fixture
def chunked_contract():
    chunker = Chunker()
    test_pdf = "./tests/test_contract.pdf"
    texts, metadatas, ids = chunker.parse_contracts(test_pdf)

    assert texts, "Chunking failed to parse contract PDF."
    assert metadatas, "Chunking failed to extract metadata."
    assert ids, "Chunking failed to generate IDs."

    return texts, metadatas, ids


# Chunking test
def test_chunking(chunked_contract):
    texts, metadatas, ids = chunked_contract
    # Optional logging
    # logging.info("Chunking test passed ✅")


@pytest.mark.skipif(
    not os.getenv("QDRANT_URL") or not os.getenv("QDRANT_API_KEY"),
    reason="Qdrant credentials not set"
)
@pytest.mark.skipif(
    not os.getenv("TEST_COLLECTION_NAME"),
    reason="Test collection name not set"
)


def test_ingestion(chunked_contract):
    texts, metadatas, ids = chunked_contract

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")


    # Qdrant setup
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key
        )
    
    collection_name = os.getenv("TEST_COLLECTION_NAME")

    embedder = EmbedUpsert(client)
    embeddings = embedder.get_embeddings(texts)
    embedder.upsert(texts, metadatas, ids, embeddings, collection_name)

