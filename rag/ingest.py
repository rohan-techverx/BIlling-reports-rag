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

def ingest_documents():
    """Load, chunk, and index the billing documentation."""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")
    
    print("Loading billing documentation...")
    loader = TextLoader("data/billing_requirements.txt", encoding="utf-8")
    documents = loader.load()
    
    print(f"Loaded {len(documents)} document(s)")
    
    # Split documents into chunks
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    
    # Create embeddings
    print("Creating embeddings...")
    embeddings = OpenAIEmbeddings()
    
    # Create vector store
    print("Storing in vector database...")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="vector_db"
    )
    
    # Persist the database
    vector_db.persist()
    
    print("\n✅ Documents successfully indexed!")
    print(f"Vector database stored in: vector_db/")
    print(f"Total chunks indexed: {len(chunks)}")

if __name__ == "__main__":
    ingest_documents()
