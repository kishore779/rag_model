# RAG Chatbot Application

A production-ready Retrieval-Augmented Generation (RAG) chatbot application built for an AI Engineer assessment. The system retrieves relevant company documents and uses Claude API to generate accurate, context-aware responses.

## Tech Stack

- **Backend**: Python + FastAPI
- **Vector Database**: ChromaDB (local)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **LLM**: Anthropic Claude 3.5 Sonnet
- **Frontend**: React + Vite + Tailwind CSS

## Project Structure

```
project-root/
├── backend/
│   ├── app.py                    # FastAPI application with /api/chat endpoint
│   ├── ingest.py                 # PDF ingestion pipeline
│   ├── rag/
│   │   ├── embeddings.py         # Embedding model management
│   │   ├── retriever.py          # ChromaDB semantic search
│   │   ├── prompts.py            # Prompt templates
│   │   └── llm.py                # Claude API integration
│   ├── chroma_db/                # ChromaDB persistent storage
│   ├── documents/                # PDF documents directory
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variables template
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main React component
│   │   ├── main.jsx              # React entry point
│   │   └── index.css             # Tailwind styles
│   ├── index.html                # HTML template
│   ├── vite.config.js            # Vite configuration
│   ├── tailwind.config.js        # Tailwind configuration
│   ├── postcss.config.js         # PostCSS configuration
│   ├── package.json              # NPM dependencies
│   ├── .gitignore
│   └── node_modules/
└── README.md                     # This file
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- An Anthropic API key (get from https://console.anthropic.com/)

### Backend Setup

#### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

Example `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

#### 3. Prepare PDF Documents

Place your PDF documents in the `backend/documents/` folder. These will be ingested into the vector database.

#### 4. Run the Ingestion Pipeline

```bash
python ingest.py
```

This will:
- Load all PDFs from `documents/` folder
- Extract text and split into chunks (500 chars with 50 char overlap)
- Generate embeddings using sentence-transformers
- Store chunks and embeddings in ChromaDB with metadata

**Output**: Embeddings stored in `chroma_db/` folder

#### 5. Start the FastAPI Server

```bash
python app.py
```

The backend will be available at `http://localhost:8000`

Check health: `curl http://localhost:8000/health`

### Frontend Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

#### 2. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

#### 3. Build for Production

```bash
npm run build
```

Output will be in the `dist/` folder.

## How to Use

1. **Start Backend**: Run `python app.py` from the `backend/` folder
2. **Start Frontend**: Run `npm run dev` from the `frontend/` folder
3. **Open Browser**: Navigate to `http://localhost:5173`
4. **Ask Questions**: Type questions about company policies and documents
5. **View Sources**: See which documents the AI used to answer your question

## API Endpoint

### POST /api/chat

**Request**:
```json
{
  "question": "What is our vacation policy?"
}
```

**Response**:
```json
{
  "answer": "Based on company documents, the vacation policy states...",
  "sources": ["company-handbook.pdf", "hr-policies.pdf"]
}
```

## System Architecture

### Ingestion Pipeline

```
PDF Files → Extract Text → Split Chunks (500 chars, 50 overlap)
    ↓
Generate Embeddings (sentence-transformers) → Store in ChromaDB
    ↓
Metadata: source, page_number, chunk_index
```

**Why this chunking strategy?**
- **500 character chunks**: Balances context preservation with granularity, preventing overly large or small segments
- **50 character overlap**: Maintains semantic continuity across chunk boundaries, reducing information loss at split points
- **RecursiveCharacterTextSplitter**: Preserves document structure by splitting on sentence/paragraph boundaries first

### RAG Pipeline (Per Request)

```
User Question
    ↓
Embed Question (sentence-transformers)
    ↓
Retrieve Top-4 Chunks (ChromaDB cosine similarity)
    ↓
Format Prompt with Context + Question
    ↓
Call Claude API with System Prompt
    ↓
Return Answer + Source Documents
```

## Key Design Decisions

### Embedding Model: sentence-transformers/all-MiniLM-L6-v2

- **Why this model?**
  - Lightweight (384-dimensional embeddings) yet powerful
  - Specifically fine-tuned for semantic similarity tasks
  - Fast inference (ideal for real-time chatbot applications)
  - Works well for document retrieval without fine-tuning
  - No GPU required, runs efficiently on CPU

### Vector Database: ChromaDB

- **Why ChromaDB?**
  - Local-first design (data privacy, no external dependencies)
  - Simple, easy to persist and backup
  - Built-in support for semantic search with various distance metrics
  - Lightweight for development and deployment
  - No additional infrastructure needed

### Top-K = 4

- **Why retrieve only 4 chunks?**
  - Provides sufficient context (2000-4000 characters typically)
  - Fits within Claude's context window comfortably
  - Reduces noise while maintaining relevance
  - Balances retrieval accuracy with response latency
  - Tested as optimal for accuracy/speed tradeoff

### Fallback Message Strategy

If the retrieved chunks don't contain relevant information, the system returns:
```
"I don't have that information in the company documents."
```

This prevents hallucination and maintains transparency with users.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes |

## Testing the Application

### Manual Testing

1. **Ingest sample PDFs**: Place PDFs in `backend/documents/`
2. **Run ingestion**: `python ingest.py`
3. **Start backend**: `python app.py`
4. **Start frontend**: `npm run dev`
5. **Ask questions** through the chat interface

### Example Questions

- "What is the vacation policy?"
- "How do I request time off?"
- "What are the company benefits?"
- "What is the dress code?"

## Production Deployment

### Backend

```bash
# Use production ASGI server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

### Frontend

```bash
# Build
npm run build

# Serve static files (use nginx, Apache, or cloud CDN)
# Point to dist/ folder
```

## Troubleshooting

### No documents ingested
- Check that PDFs are in `backend/documents/`
- Run `python ingest.py` again with verbose output
- Verify PDF files are readable (not corrupted)

### ChromaDB errors
- Delete `backend/chroma_db/` to reset the database
- Run `python ingest.py` to rebuild

### CORS errors
- Backend CORS is enabled for all origins (development mode)
- For production, restrict origins in `app.py` to your frontend domain

### Claude API errors
- Verify `ANTHROPIC_API_KEY` is set in `.env`
- Check API key has sufficient credits
- Verify internet connection

## Notes

- **No fine-tuning required**: The system uses pre-trained models and doesn't need domain-specific training
- **No hallucination**: Responses are strictly grounded in retrieved documents
- **Real semantic search**: Uses actual ChromaDB similarity search, not mock retrieval
- **Source attribution**: Every response includes source document names for transparency

## License

This project is provided as-is for educational and assessment purposes.
