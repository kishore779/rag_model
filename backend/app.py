"""
FastAPI backend for RAG chatbot.
Single endpoint: POST /api/chat
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from rag.embeddings import get_embeddings_model, embed_text
from rag.retriever import get_chroma_client, get_or_create_collection, retrieve_top_chunks
from rag.prompts import format_rag_prompt, get_system_prompt
from rag.llm import query_claude

# Load environment variables
load_dotenv()

# Verify API key
if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY not set in .env file")

# Initialize FastAPI app
app = FastAPI(title="RAG Chatbot API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models and database
print("Initializing embeddings model...")
embeddings_model = get_embeddings_model()

print("Initializing ChromaDB...")
chroma_client = get_chroma_client("./chroma_db")
chroma_collection = get_or_create_collection(chroma_client, "sws_ai_docs")


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    question: str


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    answer: str
    sources: list


@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint: process question, retrieve context, and generate response.
    """
    try:
        question = request.question.strip()
        
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Step 1: Embed the question
        question_embedding = embed_text(embeddings_model, question)
        
        # Step 2: Retrieve top 4 chunks from ChromaDB
        chunks = retrieve_top_chunks(chroma_collection, question_embedding, top_k=4)
        
        # Step 3: Format context from retrieved chunks
        context = "\n\n".join([chunk["text"] for chunk in chunks])
        
        # Extract unique source filenames
        sources = list(set([chunk["metadata"].get("source", "unknown") for chunk in chunks]))
        
        # Step 4: Format prompt with context and question
        user_prompt = format_rag_prompt(context, question)
        system_prompt = get_system_prompt()
        
        # Step 5: Query Claude
        answer = query_claude(system_prompt, user_prompt)
        
        # Step 6: Return answer and sources
        return ChatResponse(
            answer=answer,
            sources=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
