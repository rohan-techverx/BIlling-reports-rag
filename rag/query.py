"""
Query System for RAG
Allows querying the billing documentation using natural language questions.
"""

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
import re
from dotenv import load_dotenv

# Load environment variables (works locally)
load_dotenv()

# Get API key from Streamlit secrets (for Streamlit Cloud) or environment variable
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

# Initialize embeddings with API key
api_key = get_openai_api_key()
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in Streamlit Cloud secrets or .env file.")

embeddings = OpenAIEmbeddings(openai_api_key=api_key)

# Load vector database
vector_db = Chroma(
    persist_directory="vector_db",
    embedding_function=embeddings
)

# Create retriever - Optimized for concise answers
retriever = vector_db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}  # 3 chunks for focused, concise answers
)

# Initialize LLM - Low temperature for concise, factual responses
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,  # Zero temperature for most concise, factual answers
    openai_api_key=api_key
)

# Format documents function - Clean formatting for concise answers
def format_docs(docs):
    # Simple, clean format without extra markers for more focused context
    return "\n\n".join(doc.page_content for doc in docs)

# Custom prompt template for ChatModel - Concise and focused answers
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are an expert assistant specializing in Brokered and Consulting Customer Billing Report documentation. 
Your role is to provide concise, accurate, and directly relevant answers.

CRITICAL INSTRUCTIONS:
- Provide SHORT, CONCISE answers (2-4 sentences maximum)
- Answer ONLY what is asked - be direct and to the point
- Extract the most relevant information from the context
- Use bullet points or numbered lists for multiple items
- Include specific formulas, percentages, or numbers when mentioned in context
- If context has relevant information, provide it - never say "I don't know" if context exists
- Focus on the key facts, not explanations
- Be precise and factual

IMPORTANT - When information is not available:
- If asked about a feature for Brokered reports but the context only mentions it for Consulting reports (or vice versa), clearly state this distinction
- Example: If asked "How are benchmark fees applied on brokered customer?" but context only mentions benchmark fees for consulting, respond: "Benchmark fees are used in Consulting Customer Billing Reports, not in Brokered Customer Billing Reports. Benchmark fees are not applicable to brokered customers."
- Provide helpful context about which report type uses the feature when relevant
- Only reference information that actually exists in the provided context"""),
    ("human", """Context from Documentation:
{context}

Question: {question}

Provide a concise, direct answer:""")
])

# Create QA chain using LCEL
qa_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt_template
    | llm
    | StrOutputParser()
)

def check_source_relevance(source_content: str, question: str, answer: str) -> bool:
    """
    Check if a source document is relevant to the question and answer.
    
    Returns True if the source appears to be relevant, False otherwise.
    """
    # Normalize for comparison
    source_lower = source_content.lower()
    question_lower = question.lower()
    answer_lower = answer.lower()
    
    # Extract key terms from question (excluding common words)
    common_words = {'the', 'a', 'an', 'is', 'are', 'how', 'what', 'when', 'where', 'why', 'does', 'do', 'on', 'in', 'for', 'to', 'of', 'and', 'or', 'are', 'applied'}
    question_words = [word for word in re.findall(r'\b\w+\b', question_lower) if word not in common_words and len(word) > 3]
    
    # Check if source contains key question terms
    has_question_terms = any(word in source_lower for word in question_words)
    
    # Check if answer indicates information is not available or not applicable
    not_applicable_indicators = [
        'does not provide',
        'not available',
        'not applicable',
        'not found',
        'no information',
        'not mentioned',
        'not in',
        'not used in',
        'not applicable to'
    ]
    
    answer_says_not_found = any(indicator in answer_lower for indicator in not_applicable_indicators)
    
    # If answer says info is not available/not applicable, be more strict about relevance
    if answer_says_not_found:
        # Extract report type from question
        is_brokered_question = 'brokered' in question_lower
        is_consulting_question = 'consulting' in question_lower
        
        # Check for report type mismatch
        if is_brokered_question:
            # Question is about brokered
            source_is_consulting_only = 'consulting' in source_lower and 'brokered' not in source_lower
            source_is_brokered = 'brokered' in source_lower
            
            # If source only mentions consulting (not brokered) and mentions the feature, it's irrelevant
            if source_is_consulting_only and has_question_terms:
                return False
            
            # If source is about brokered but doesn't have the feature terms, might still be irrelevant
            if source_is_brokered and not has_question_terms:
                return False
        
        elif is_consulting_question:
            # Question is about consulting
            source_is_brokered_only = 'brokered' in source_lower and 'consulting' not in source_lower
            source_is_consulting = 'consulting' in source_lower
            
            # If source only mentions brokered (not consulting) and mentions the feature, it's irrelevant
            if source_is_brokered_only and has_question_terms:
                return False
            
            # If source is about consulting but doesn't have the feature terms, might still be irrelevant
            if source_is_consulting and not has_question_terms:
                return False
        
        # If answer says not found and source doesn't have question terms, filter it out
        if not has_question_terms:
            return False
    
    # Default: consider relevant if it has question terms
    # Also consider relevant if it's about the same report type (even without exact terms)
    return has_question_terms

def query(question: str):
    """
    Query the RAG system with a question.
    
    Args:
        question: The question to ask about the billing documentation
        
    Returns:
        Dictionary with 'result' (answer), 'source_documents', and 'relevant_sources'
    """
    # Get source documents first
    source_docs = retriever.invoke(question)
    
    # Get answer from chain
    answer = qa_chain.invoke(question)
    
    # Filter relevant sources
    relevant_sources = []
    for doc in source_docs:
        if check_source_relevance(doc.page_content, question, answer):
            relevant_sources.append(doc)
    
    return {
        "result": answer,
        "source_documents": relevant_sources if relevant_sources else source_docs,  # Fallback to all if none are relevant
        "all_source_documents": source_docs  # Keep original for reference
    }

def interactive_query():
    """Interactive command-line interface for querying."""
    print("\n" + "="*60)
    print("Billing Report AI Assistant")
    print("="*60)
    print("Ask questions about Brokered and Consulting Customer Billing Reports.")
    print("Type 'exit' to quit.\n")
    
    while True:
        question = input("\nAsk question: ").strip()
        
        if question.lower() == "exit":
            print("\nGoodbye!")
            break
        
        if not question:
            continue
        
        try:
            result = query(question)
            print("\n" + "-"*60)
            print("Answer:")
            print("-"*60)
            print(result["result"])
            
            # Optionally show source documents
            if result.get("source_documents"):
                print("\n" + "-"*60)
                print("Sources:")
                print("-"*60)
                for i, doc in enumerate(result["source_documents"], 1):
                    print(f"\n[{i}] {doc.page_content[:200]}...")
                    
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please check your OpenAI API key and ensure documents are indexed.")

if __name__ == "__main__":
    # Check if vector database exists
    if not os.path.exists("vector_db"):
        print("❌ Vector database not found!")
        print("Please run 'python rag/ingest.py' first to index the documents.")
    else:
        # Check if OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY not found in environment variables.")
            print("Please set it in .env file.")
        else:
            interactive_query()
