"""
ChromaDB retriever for semantic search.
"""
import chromadb
from chromadb.config import Settings


def get_chroma_client(persist_directory="./chroma_db"):
    """
    Initialize ChromaDB client with persistence.
    """
    settings = Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=persist_directory,
        anonymized_telemetry=False
    )
    client = chromadb.Client(settings)
    return client


def get_or_create_collection(client, collection_name="sws_ai_docs"):
    """
    Get or create a ChromaDB collection.
    """
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def retrieve_top_chunks(collection, query_embedding, top_k=4):
    """
    Retrieve top-k chunks similar to the query embedding.
    Returns a list of chunks with metadata.
    """
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    chunks = []
    if results and results['ids'] and len(results['ids']) > 0:
        for i, chunk_id in enumerate(results['ids'][0]):
            chunk_text = results['documents'][0][i] if results['documents'] else ""
            metadata = results['metadatas'][0][i] if results['metadatas'] else {}
            distance = results['distances'][0][i] if results['distances'] else None
            
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": metadata,
                "distance": distance
            })
    
    return chunks
