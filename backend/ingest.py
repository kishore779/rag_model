"""
Ingestion pipeline to load PDFs, chunk, embed, and store in ChromaDB.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.embeddings import get_embeddings_model, embed_text
from rag.retriever import get_chroma_client, get_or_create_collection


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using pdfplumber.
    Returns a list of (text, page_number) tuples.
    """
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():  # Only add non-empty pages
                pages.append((text, page_num + 1))  # 1-indexed page numbers
    return pages


def chunk_text(text, chunk_size=500, chunk_overlap=50):
    """
    Split text into chunks using RecursiveCharacterTextSplitter.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)
    return [c for c in chunks if c.strip()]  # Filter out empty chunks


def ingest_documents(documents_dir="./documents", chroma_dir="./chroma_db"):
    """
    Main ingestion pipeline:
    1. Load all PDFs from documents folder
    2. Extract and chunk text
    3. Generate embeddings
    4. Store in ChromaDB
    """
    print("Starting document ingestion pipeline...")
    
    # Initialize ChromaDB
    client = get_chroma_client(chroma_dir)
    collection = get_or_create_collection(client, "sws_ai_docs")
    
    # Load embedding model
    print("Loading embedding model...")
    embeddings_model = get_embeddings_model()
    
    # Get all PDF files
    pdf_files = list(Path(documents_dir).glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {documents_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s)")
    
    total_chunks = 0
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        
        try:
            # Extract text from PDF
            pages = extract_text_from_pdf(str(pdf_file))
            print(f"  Extracted {len(pages)} page(s)")
            
            chunk_index = 0
            for page_text, page_num in pages:
                # Chunk the text
                chunks = chunk_text(page_text)
                
                for chunk in chunks:
                    # Generate embedding
                    embedding = embed_text(embeddings_model, chunk)
                    
                    # Create unique ID
                    chunk_id = f"{pdf_file.stem}_page{page_num}_chunk{chunk_index}"
                    
                    # Prepare metadata
                    metadata = {
                        "source": pdf_file.name,
                        "page_number": page_num,
                        "chunk_index": chunk_index
                    }
                    
                    # Add to ChromaDB
                    collection.add(
                        ids=[chunk_id],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[metadata]
                    )
                    
                    chunk_index += 1
                    total_chunks += 1
            
            print(f"  Stored {chunk_index} chunk(s) from {pdf_file.name}")
            
        except Exception as e:
            print(f"  Error processing {pdf_file.name}: {str(e)}")
    
    print(f"\n✓ Ingestion complete. Total chunks stored: {total_chunks}")


if __name__ == "__main__":
    ingest_documents()
