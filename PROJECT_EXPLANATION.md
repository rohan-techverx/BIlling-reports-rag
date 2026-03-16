# Complete Project Explanation: Billing Reports RAG System

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [What is RAG?](#what-is-rag)
3. [Technologies Used](#technologies-used)
4. [Why These Technologies?](#why-these-technologies)
5. [System Architecture](#system-architecture)
6. [How It Works - Step by Step](#how-it-works---step-by-step)
7. [Key Components Explained](#key-components-explained)
8. [Data Flow](#data-flow)
9. [Results and Output](#results-and-output)

---

## 🎯 Project Overview

**Goal**: Create an AI assistant that can answer questions about the Brokered Customer Billing Report documentation using natural language.

**Problem Solved**: Instead of manually searching through 350+ lines of technical documentation, users can ask questions in plain English and get accurate, context-aware answers.

**Solution**: RAG (Retrieval-Augmented Generation) system that combines:
- **Document Search** (finding relevant sections)
- **AI Understanding** (interpreting and answering)

---

## 🤔 What is RAG?

**RAG = Retrieval-Augmented Generation**

RAG is a technique that enhances AI responses by:
1. **Retrieval**: Finding relevant information from your documents
2. **Augmentation**: Adding that information to the AI's context
3. **Generation**: Creating accurate answers based on the retrieved context

**Why RAG?**
- ✅ AI answers are based on YOUR documentation (not general knowledge)
- ✅ Can cite sources (shows which parts of docs were used)
- ✅ More accurate than pure AI (reduces hallucinations)
- ✅ Works with private/internal documents

---

## 🛠️ Technologies Used

### Core Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python 3.10** | Programming language | 3.10+ |
| **LangChain** | RAG framework | 1.2.12 |
| **OpenAI** | Embeddings & LLM | GPT-4o-mini |
| **ChromaDB** | Vector database | 1.5.5 |
| **Streamlit** | Web UI | 1.55.0 |
| **FastAPI** | REST API | Latest |
| **python-dotenv** | Environment variables | Latest |

### Supporting Libraries

- **langchain-community**: Community integrations
- **langchain-openai**: OpenAI integrations
- **langchain-text-splitters**: Text chunking
- **tiktoken**: Token counting
- **uvicorn**: ASGI server

---

## 💡 Why These Technologies?

### 1. **LangChain** - Why?
- **Purpose**: Provides pre-built RAG components
- **Benefits**:
  - Handles complex chain orchestration
  - Supports multiple LLM providers
  - Built-in document loaders and splitters
  - Easy to customize and extend

**Alternative**: Could use LlamaIndex, but LangChain is more flexible for custom workflows.

### 2. **OpenAI Embeddings** - Why?
- **Purpose**: Convert text to numerical vectors (embeddings)
- **Benefits**:
  - High-quality semantic understanding
  - Captures meaning, not just keywords
  - Works well for technical documentation

**How it works**: 
- "How are APIs calculated?" → [0.23, -0.45, 0.67, ...] (1536 numbers)
- Similar questions get similar vectors
- Enables semantic search

### 3. **ChromaDB** - Why?
- **Purpose**: Store and search embeddings efficiently
- **Benefits**:
  - Fast similarity search
  - Persistent storage (saves to disk)
  - Lightweight and easy to use
  - No external database needed

**Alternative**: Could use Pinecone, Weaviate, or PostgreSQL with pgvector, but ChromaDB is simplest for local development.

### 4. **GPT-4o-mini** - Why?
- **Purpose**: Generate human-like answers
- **Benefits**:
  - Cost-effective ($0.15 per 1M tokens)
  - Fast response times
  - Good understanding of technical content
  - Reliable API

**Alternative**: Could use GPT-4, Claude, or local models, but GPT-4o-mini offers best balance of cost/performance.

### 5. **Streamlit** - Why?
- **Purpose**: Quick web UI development
- **Benefits**:
  - No HTML/CSS/JavaScript needed
  - Python-only development
  - Built-in components (text input, buttons, etc.)
  - Fast prototyping

**Alternative**: Could use React/Vue, but Streamlit is fastest for internal tools.

### 6. **FastAPI** - Why?
- **Purpose**: REST API for integration
- **Benefits**:
  - Fast performance
  - Automatic API documentation
  - Type validation
  - Easy to integrate with other systems

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                     │
├─────────────────┬───────────────────┬───────────────────────┤
│  Streamlit UI   │   FastAPI REST    │   CLI Interface       │
│   (ui.py)       │     (app.py)      │   (query.py)          │
└────────┬────────┴──────────┬────────┴──────────┬────────────┘
         │                   │                    │
         └───────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Query System  │
                    │   (query.py)    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
    │ Retriever│        │   LLM   │        │ Prompt  │
    │ (Chroma) │        │ (OpenAI)│        │ Template│
    └────┬────┘        └────┬────┘        └────┬────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Vector Store   │
                    │   (ChromaDB)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Embeddings    │
                    │   (OpenAI API)  │
                    └─────────────────┘
```

---

## 🔄 How It Works - Step by Step

### Phase 1: Document Ingestion (`rag/ingest.py`)

**Goal**: Prepare documents for search

#### Step 1: Load Document
```python
loader = TextLoader("data/billing_requirements.txt")
documents = loader.load()
```
- Reads the billing requirements text file
- Creates Document objects with metadata

#### Step 2: Split into Chunks
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,      # Each chunk = 800 characters
    chunk_overlap=100    # Overlap 100 chars between chunks
)
chunks = text_splitter.split_documents(documents)
```

**Why chunking?**
- LLMs have token limits (can't process entire doc at once)
- Smaller chunks = better retrieval precision
- Overlap ensures context isn't lost at boundaries

**Example**:
```
Original: "REQ-6.1 Selective Application. Customers select which contract years..."
Chunk 1: "REQ-6.1 Selective Application. Customers select which contract years apply an annual price increase..."
Chunk 2: "...annual price increase. Only selected years trigger a percentage adjustment. REQ-6.2 Custom..."
```

#### Step 3: Create Embeddings
```python
embeddings = OpenAIEmbeddings()
# Each chunk → vector of 1536 numbers
```

**What happens**:
- Each chunk is sent to OpenAI Embeddings API
- Returns a vector (list of 1536 numbers)
- Similar chunks get similar vectors

**Example**:
```
Chunk: "How are APIs calculated?"
Vector: [0.23, -0.45, 0.67, 0.12, ..., 0.89] (1536 numbers)

Chunk: "Annual Price Increases calculation"
Vector: [0.25, -0.43, 0.65, 0.14, ..., 0.87] (similar!)
```

#### Step 4: Store in Vector Database
```python
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="vector_db"
)
```

**What happens**:
- Stores chunks + their embeddings in ChromaDB
- Creates index for fast similarity search
- Saves to disk (`vector_db/` folder)

**Result**: 23 chunks indexed and searchable!

---

### Phase 2: Query Processing (`rag/query.py`)

**Goal**: Answer user questions using indexed documents

#### Step 1: User Asks Question
```
User: "How do APIs work in billing report?"
```

#### Step 2: Convert Question to Embedding
```python
question_embedding = embeddings.embed_query(question)
# "How do APIs work?" → [0.24, -0.44, 0.66, ...]
```

#### Step 3: Find Similar Chunks (Retrieval)
```python
retriever = vector_db.as_retriever(search_kwargs={"k": 3})
relevant_docs = retriever.invoke(question)
```

**What happens**:
- Compares question embedding with all chunk embeddings
- Uses cosine similarity (measures angle between vectors)
- Returns top 3 most similar chunks

**Example Results**:
```
Top 3 chunks found:
1. "6. Annual Price Increases (APIs) REQ-6.1 Selective Application..."
2. "REQ-6.3 Compounding Calculation. Each increase is calculated..."
3. "REQ-6.5 Year Determination. The system calculates applicable APIs..."
```

#### Step 4: Format Context
```python
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

context = format_docs(relevant_docs)
```

**Result**:
```
Context:
"6. Annual Price Increases (APIs) REQ-6.1 Selective Application. Customers select which contract years apply an annual price increase...

REQ-6.3 Compounding Calculation. Each increase is calculated on the previous year's final price...

REQ-6.5 Year Determination. The system calculates applicable APIs using the calendar year difference..."
```

#### Step 5: Create Prompt
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant..."),
    ("human", "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:")
])
```

**Final Prompt Sent to LLM**:
```
System: You are a helpful assistant that answers questions about the Brokered Customer Billing Report documentation. Use the provided context to answer questions accurately.

Human: Context:
6. Annual Price Increases (APIs) REQ-6.1 Selective Application. Customers select which contract years apply an annual price increase. Only selected years trigger a percentage adjustment...

Question: How do APIs work in billing report?

Answer:
```

#### Step 6: Generate Answer
```python
llm = ChatOpenAI(model="gpt-4o-mini")
answer = llm.invoke(prompt)
```

**LLM Processing**:
1. Reads the context (relevant documentation chunks)
2. Understands the question
3. Generates answer based ONLY on the context
4. Returns natural language response

**Example Answer**:
```
"Annual Price Increases (APIs) in the billing report work as follows:

1. Selective Application: Customers choose which contract years should have price increases applied.

2. Compounding Calculation: Each increase is calculated on the previous year's final price, not the original base price, creating a compounding effect.

3. Year Determination: The system calculates which year applies based on the calendar year difference between the contract effective date and the billing month..."
```

#### Step 7: Return Results
```python
return {
    "result": answer,
    "source_documents": relevant_docs  # Shows which chunks were used
}
```

---

## 🔧 Key Components Explained

### 1. **Document Loader** (`TextLoader`)
- **What**: Reads text files
- **Why**: Converts raw text into LangChain Document format
- **Input**: `billing_requirements.txt`
- **Output**: Document objects with metadata

### 2. **Text Splitter** (`RecursiveCharacterTextSplitter`)
- **What**: Splits documents into smaller chunks
- **Why**: 
  - LLM context limits
  - Better retrieval precision
  - Maintains semantic meaning
- **Settings**:
  - `chunk_size=800`: Each chunk ~800 characters
  - `chunk_overlap=100`: Overlap prevents context loss

### 3. **Embeddings** (`OpenAIEmbeddings`)
- **What**: Converts text → numbers (vectors)
- **Why**: Enables semantic search (meaning-based, not keyword-based)
- **How**: Uses OpenAI's `text-embedding-3-small` model
- **Output**: 1536-dimensional vectors

### 4. **Vector Store** (`ChromaDB`)
- **What**: Database for storing embeddings
- **Why**: Fast similarity search
- **Features**:
  - Persistent storage (saves to disk)
  - Automatic indexing
  - Similarity search in milliseconds

### 5. **Retriever** (`as_retriever`)
- **What**: Finds relevant documents for a question
- **How**: 
  - Converts question to embedding
  - Searches vector database
  - Returns top K most similar chunks
- **Settings**: `k=3` (returns top 3 chunks)

### 6. **LLM** (`ChatOpenAI`)
- **What**: Language model that generates answers
- **Model**: `gpt-4o-mini`
- **Why**: 
  - Cost-effective
  - Fast
  - Good for technical content
- **Temperature**: `0` (deterministic, factual responses)

### 7. **Prompt Template** (`ChatPromptTemplate`)
- **What**: Structures the prompt sent to LLM
- **Components**:
  - System message: Sets AI's role
  - Human message: Provides context + question
- **Why**: Ensures consistent, accurate responses

### 8. **QA Chain** (LCEL Pipeline)
- **What**: Orchestrates the entire RAG flow
- **Flow**:
  ```
  Question → Retriever → Format Docs → Prompt → LLM → Answer
  ```
- **Why LCEL**: 
  - Declarative syntax
  - Easy to customize
  - Composable

---

## 📊 Data Flow

### Ingestion Flow
```
billing_requirements.txt
    ↓
TextLoader (load document)
    ↓
RecursiveCharacterTextSplitter (split into 23 chunks)
    ↓
OpenAIEmbeddings (convert to vectors)
    ↓
ChromaDB (store chunks + vectors)
    ↓
vector_db/ (persistent storage)
```

### Query Flow
```
User Question: "How do APIs work?"
    ↓
OpenAIEmbeddings (question → vector)
    ↓
ChromaDB Retriever (find top 3 similar chunks)
    ↓
Format Docs (combine chunks into context)
    ↓
ChatPromptTemplate (create prompt with context)
    ↓
ChatOpenAI (generate answer)
    ↓
StrOutputParser (extract text)
    ↓
Answer + Source Documents
```

---

## 📈 Results and Output

### What You Get

1. **Accurate Answers**
   - Based on YOUR documentation
   - Not generic AI responses
   - Cites sources

2. **Source Citations**
   - Shows which parts of docs were used
   - Users can verify answers
   - Transparency

3. **Natural Language**
   - Ask questions like talking to a person
   - No need to know exact terminology
   - Understands context

### Example Interaction

**User Question**:
```
"How are hauler costs calculated?"
```

**System Process**:
1. Finds chunks about "hauler cost calculation"
2. Retrieves REQ-9.4 (Proration Methodology)
3. Formats context
4. Generates answer

**Answer**:
```
"Hauler costs are calculated using proration based on calendar days overlap:

Prorated Amount = Invoice Amount × (Overlap Days ÷ Total Invoice Days)

Where:
- Overlap Days: Count of days where invoice service period intersects with billing period
- Total Invoice Days: Count of days in the invoice's full service period

Invoices are included only when:
- invoice.service_from ≤ billing period end date
- invoice.service_to ≥ billing period start date
- Both service dates are not null
- invoice.is_duplicate = False"
```

**Source Documents**: Shows the exact chunks from documentation used

---

## 🎯 Key Benefits

1. **Time Saving**: No manual document searching
2. **Accuracy**: Answers based on official documentation
3. **Accessibility**: Natural language queries
4. **Transparency**: Shows sources
5. **Scalable**: Can add more documents easily
6. **Multiple Interfaces**: Web UI, API, CLI

---

## 🔍 Technical Deep Dive

### Why Embeddings Work

Embeddings capture semantic meaning:
- "How are APIs calculated?" 
- "What is the annual price increase method?"
- "Explain API calculation"

All get similar embeddings because they mean the same thing!

### Why Chunking Matters

**Too Large**: 
- Hard to find specific information
- Wastes tokens
- Less precise retrieval

**Too Small**:
- Loses context
- Fragmented information
- More chunks to search

**Just Right (800 chars)**:
- Balanced context
- Precise retrieval
- Efficient processing

### Why Top K = 3?

- **Too Few (1)**: Might miss relevant info
- **Too Many (10)**: Wastes tokens, slower
- **Just Right (3)**: Good balance of coverage and efficiency

---

## 🚀 Future Enhancements

Possible improvements:
1. **Multi-document support**: Add more docs
2. **Conversation history**: Remember previous questions
3. **Better chunking**: Semantic chunking
4. **Hybrid search**: Combine keyword + semantic
5. **Fine-tuning**: Custom model for billing domain
6. **Caching**: Cache common questions
7. **Analytics**: Track popular questions

---

## 📝 Summary

This RAG system transforms a static documentation file into an interactive AI assistant by:

1. **Indexing**: Converting documents into searchable embeddings
2. **Retrieving**: Finding relevant information for questions
3. **Generating**: Creating accurate answers using AI

The result: Users can ask questions in plain English and get accurate, source-cited answers from your billing documentation!

---

**Project Status**: ✅ Fully Functional
**Documentation Indexed**: 23 chunks
**Interfaces**: Web UI, REST API, CLI
**Ready for**: Production use with proper API key management
