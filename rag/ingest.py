"""
Document Ingestion Script
Loads billing documentation, splits into chunks, creates embeddings, and stores in vector database.
"""

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_api_key():
    """Get OpenAI API key from Streamlit secrets or environment variable."""
    try:
        import streamlit as st
        # Try Streamlit secrets first (for Streamlit Cloud)
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            return st.secrets['OPENAI_API_KEY']
    except (ImportError, AttributeError, KeyError):
        pass
    
    # Fall back to environment variable
    return os.getenv("OPENAI_API_KEY")

def ingest_documents(progress_callback=None):
    """
    Load, chunk, and index the billing documentation.
    
    Args:
        progress_callback: Optional function to call with progress messages (for Streamlit)
    """
    
    def log(message):
        """Log message to console or Streamlit."""
        if progress_callback:
            progress_callback(message)
        else:
            print(message)
    
    # Get API key
    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found. Please set it in Streamlit Cloud secrets or .env file.")
    
    log("Loading billing documentation...")
    loader = TextLoader("data/billing_requirements.txt", encoding="utf-8")
    documents = loader.load()
    
    log(f"Loaded {len(documents)} document(s)")
    
    # Split documents into chunks
    log("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    log(f"Created {len(chunks)} chunks")
    
    # Create embeddings
    log("Creating embeddings...")
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    
    # Create vector store
    log("Storing in vector database...")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="vector_db"
    )
    
    # Persist the database
    vector_db.persist()
    
    log("\n✅ Documents successfully indexed!")
    log(f"Vector database stored in: vector_db/")
    log(f"Total chunks indexed: {len(chunks)}")
    
    return len(chunks)

if __name__ == "__main__":
    ingest_documents()
