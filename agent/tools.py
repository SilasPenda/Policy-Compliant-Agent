import os
from dotenv import load_dotenv
from langchain.tools import Tool
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.utils import get_embedding_model, db_client_connect

load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

policy_collection = os.getenv("POLICY_COLLECTION_NAME")
contract_collection = os.getenv("CONTRACT_COLLECTION_NAME")

embedding_model = get_embedding_model()


def create_chunk_embeddings(document_pages: list):
    """
    Tool to create embeddings for text chunks extracted from PDF pages using RecursiveCharacterTextSplitter.
    Args:
        document_pages (list): List of PDF pages as Document objects.

    This function uses the SentenceTransformer model to create embeddings for text chunks
    extracted from PDF pages. It splits the text into manageable chunks using RecursiveCharacterTextSplitter
    and then encodes these chunks into embeddings. The embeddings are returned as a list.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = []
    for i, page in enumerate(document_pages):
        text = page.extract_text()
        if text:
            chunks.extend(splitter.split_text(text))

    embeddings = embedding_model.encode(chunks, show_progress_bar=True, batch_size=32)

    return embeddings

chunk_embedding_tool = Tool(
    name="create_chunk_embeddings",
    func=create_chunk_embeddings,
    description="Create embeddings for text chunks extracted from PDF pages using RecursiveCharacterTextSplitter. "
)


def find_matching_policies(query: str, top_k: int=3):
    """
    Tool to find matching policies based on a query using embeddings.
    Args:
        query (str): The query to find matching policies for.
        top_k (int): The number of top matching policies to return.
    """

    client = db_client_connect(policy_collection)

    query_embedding = embedding_model.encode(query).tolist()

    results = client.search(
        collection_name=policy_collection,
        query_vector=query_embedding,
        limit=top_k,
        with_payload=True,
    )

    return results

matching_policy_tool = Tool(
    name="find_matching_policies",
    func=find_matching_policies,
    description="Find matching policies based on a query using embeddings. Returns top K matching policies with their documents and metadata."
)


def find_similar_documents(query: str, top_k: int=3):
    """
    Tool to find similar documents based on a query and policies to give more context to back up answer.
    
    Args:
        query (str): The query to find similar documents for.
        top_k (int): The number of top similar documents to return.
    """
    
    client = db_client_connect(contract_collection)
    # q_embedding = model.encode([query])[0]
    query_embedding = embedding_model.encode(query).tolist()

    results = client.search(
        collection_name=contract_collection,
        query_vector=query_embedding,
        limit=top_k,
        with_payload=True,
    )

    return results


similar_document_tool = Tool(
    name="find_similar_documents",
    func=find_similar_documents,
    description="Find similar documents based on a query and policies to give more context to back up answer. Returns top K similar documents with their metadata."
)
