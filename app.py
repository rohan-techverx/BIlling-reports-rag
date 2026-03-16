"""
FastAPI Backend for Billing Documentation RAG System
Provides REST API endpoints for querying the billing documentation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.query import query
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Billing Report AI Assistant API",
    description="RAG-based API for querying Brokered and Consulting Customer Billing Report documentation",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Billing Report AI Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "/ask": "POST - Ask a question about billing documentation",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    # Check if vector database exists
    if not os.path.exists("vector_db"):
        raise HTTPException(status_code=503, detail="Vector database not found. Please run ingestion first.")
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")
    
    return {"status": "healthy", "vector_db": "ready", "api_key": "configured"}

@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """
    Ask a question about the billing documentation.
    
    Args:
        request: QuestionRequest containing the question
        
    Returns:
        AnswerResponse with answer and source documents
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = query(request.question)
        
        # Extract source document snippets
        sources = []
        if result.get("source_documents"):
            sources = [doc.page_content[:300] + "..." for doc in result["source_documents"]]
        
        return AnswerResponse(
            answer=result["result"],
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
