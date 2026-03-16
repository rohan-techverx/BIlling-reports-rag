"""
Streamlit Web UI for Billing Documentation RAG System
Provides a user-friendly interface for querying the billing documentation.
"""

import streamlit as st
from rag.query import query
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clean_source_document(content: str) -> str:
    """
    Clean source document content by removing metadata and formatting artifacts.
    
    Removes:
    - Sign-Off sections
    - Prepared by / Date lines
    - Approved by lines with underscores
    - Empty separator lines
    - Other metadata that's not relevant to the answer
    """
    lines = content.split('\n')
    cleaned_lines = []
    in_signoff_section = False
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        line_stripped = line.strip()
        
        # Detect start of Sign-Off section
        if 'sign-off' in line_lower or line_lower == 'sign-off':
            in_signoff_section = True
            continue
        
        # If we're in a sign-off section, skip until we find meaningful content
        if in_signoff_section:
            # Check if this line contains actual content (not just metadata)
            if line_stripped and not any([
                'prepared by' in line_lower,
                'approved by' in line_lower,
                re.match(r'^\s*date\s*:', line_lower),
                re.match(r'^[\s_\-]+$', line_stripped),  # Just underscores/dashes
                re.match(r'^\s*date\s*:\s*[_\-\s]+$', line_lower),  # Date: __________
            ]):
                # Found actual content, exit sign-off section
                in_signoff_section = False
            else:
                # Still in sign-off section, skip this line
                continue
        
        # Skip "Prepared by" lines (with any content after it)
        if 'prepared by' in line_lower:
            continue
        
        # Skip "Date:" lines (with or without dates, including "Date: __________")
        if re.match(r'^\s*date\s*:', line_lower) or re.match(r'^\s*date\s*$', line_lower):
            continue
        
        # Skip "Approved by" lines (with or without underscores/dates)
        if 'approved by' in line_lower:
            continue
        
        # Skip lines that are just underscores, dashes, or empty after stripping
        if re.match(r'^[\s_\-]+$', line_stripped):
            continue
        
        # Skip lines that match "Approved by: _______________________ Date: __________" pattern
        if re.search(r'approved\s+by\s*:[\s_\-]+date\s*:[\s_\-]+', line_lower):
            continue
        
        # Keep empty lines only if they're between actual content
        if line_stripped == '':
            if cleaned_lines and i < len(lines) - 1:
                next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
                if next_line and not any([
                    'prepared by' in next_line.lower(),
                    'approved by' in next_line.lower(),
                    'sign-off' in next_line.lower(),
                    re.match(r'^\s*date\s*:', next_line.lower()),
                ]):
                    cleaned_lines.append('')
            continue
        
        # Add the line if it contains actual content
        cleaned_lines.append(line)
    
    # Join lines and clean up multiple consecutive empty lines
    cleaned = '\n'.join(cleaned_lines)
    # Replace 3+ consecutive newlines with 2 newlines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned

def normalize_content(content: str) -> str:
    """
    Normalize content for comparison by removing extra whitespace and converting to lowercase.
    """
    # Remove extra whitespace and normalize
    normalized = re.sub(r'\s+', ' ', content.lower().strip())
    return normalized

def deduplicate_source_documents(source_documents):
    """
    Remove duplicate source documents based on cleaned and normalized content.
    
    Returns a list of unique documents, preserving the first occurrence of each unique content.
    """
    seen_contents = set()
    unique_documents = []
    
    for doc in source_documents:
        cleaned_content = clean_source_document(doc.page_content)
        normalized_content = normalize_content(cleaned_content)
        
        # Skip if we've seen this content before
        if normalized_content in seen_contents:
            continue
        
        # Add to seen set and keep the document
        seen_contents.add(normalized_content)
        unique_documents.append({
            'document': doc,
            'cleaned_content': cleaned_content
        })
    
    return unique_documents

# Page configuration
st.set_page_config(
    page_title="Billing Documentation AI",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b9;
        margin-bottom: 1rem;
    }
    .subtitle {
        color: #666;
        margin-bottom: 2rem;
    }
    .answer-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-top: 1rem;
    }
    .source-box {
        background-color: #fff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📄 Billing Documentation AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask questions about the Customer Billing Report documentation</div>', unsafe_allow_html=True)

# Check for API key in Streamlit secrets (for Streamlit Cloud) or environment variable
api_key = None
try:
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets['OPENAI_API_KEY']
except (AttributeError, KeyError):
    pass

if not api_key:
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEY not found! Please set it in Streamlit Cloud secrets (Settings → Secrets) or .env file.")
    st.info("💡 To set it in Streamlit Cloud: Go to 'Manage app' → 'Settings' → 'Secrets' → Add 'OPENAI_API_KEY'")
    st.stop()

# Check prerequisites and auto-create vector database if needed
if not os.path.exists("vector_db"):
    with st.spinner("🔄 Vector database not found. Creating it now (this may take a minute)..."):
        try:
            from rag.ingest import ingest_documents
            
            # Create a progress container
            progress_container = st.empty()
            progress_messages = []
            
            def progress_callback(message):
                progress_messages.append(message)
                progress_container.text("\n".join(progress_messages[-5:]))  # Show last 5 messages
            
            # Run ingestion with API key passed directly
            chunks_count = ingest_documents(progress_callback=progress_callback, api_key=api_key)
            
            progress_container.empty()
            st.success(f"✅ Vector database created successfully! Indexed {chunks_count} document chunks.")
            st.info("🔄 Please refresh the page to continue.")
            st.stop()
            
        except Exception as e:
            st.error(f"❌ Error creating vector database: {str(e)}")
            st.info("Please ensure:")
            st.info("1. OPENAI_API_KEY is set in Streamlit Cloud secrets (Settings → Secrets)")
            st.info("2. The data/billing_requirements.txt file exists")
            st.stop()

# Initialize session state
if "question_input" not in st.session_state:
    st.session_state.question_input = ""
if "search_triggered" not in st.session_state:
    st.session_state.search_triggered = False

# Sidebar with example questions
with st.sidebar:
    st.header("💡 Example Questions")
    example_questions = [
        "How is hauler cost calculated?",
        "What determines whether a customer appears in the report?",
        "How are management fees applied?",
        "Why are zero-priced monthly services shown?",
        "How are annual price increases calculated?",
        "What billing dates are allowed?",
        "How is net profit calculated?",
        "When are pass-through charges included?",
    ]
    
    for i, example in enumerate(example_questions):
        if st.button(f"📌 {example}", key=f"example_{i}", use_container_width=True):
            st.session_state.question_input = example  # Update the text input widget
            st.session_state.search_triggered = True
            st.rerun()

# Main content area - Use form to handle Enter key submission
with st.form("question_form", clear_on_submit=False):
    question = st.text_input(
        "Ask a question about the billing documentation:",
        placeholder="e.g., How is hauler cost calculated?",
        key="question_input"
    )
    submitted = st.form_submit_button("🔍 Search", type="primary", use_container_width=True)

# Determine if search should be triggered
should_search = False
if st.session_state.get("search_triggered", False):
    # Sidebar question was clicked
    should_search = True
    st.session_state.search_triggered = False  # Reset flag
elif submitted:
    # Search button was clicked or Enter was pressed
    should_search = True

# Trigger search if question is provided
if should_search and question:
    with st.spinner("🔍 Searching documentation and generating answer..."):
        try:
            result = query(question)
            
            # Display answer
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown("### 💬 Answer")
            st.markdown(result["result"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display source documents (deduplicated and filtered for relevance)
            if result.get("source_documents"):
                unique_sources = deduplicate_source_documents(result["source_documents"])
                
                if unique_sources:
                    st.markdown("### 📚 Source Documents")
                    # Show count if duplicates were removed
                    if len(unique_sources) < len(result["source_documents"]):
                        st.caption(f"Showing {len(unique_sources)} unique source(s) (removed {len(result['source_documents']) - len(unique_sources)} duplicate(s))")
                    
                    for i, source_info in enumerate(unique_sources, 1):
                        with st.expander(f"Source {i}"):
                            st.text(source_info['cleaned_content'])
                # If no relevant sources after filtering, don't show the section
                # (sources were already filtered in query.py for relevance)
                        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Please check your OpenAI API key and ensure documents are indexed.")

# Footer
st.markdown("---")
st.markdown("**Brokered Customer Billing Report Documentation v1.0** | Powered by RAG (Retrieval-Augmented Generation)")
