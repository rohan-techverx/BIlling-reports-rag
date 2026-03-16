# Billing Reports RAG Assistant

An AI-powered assistant for querying the Brokered Customer Billing Report documentation using Retrieval-Augmented Generation (RAG).

## 🎯 Project Overview

This project uses RAG (Retrieval-Augmented Generation) to create an AI assistant that can answer questions about the Brokered Customer Billing Report requirements. The system:

1. **Indexes** the billing documentation into a vector database
2. **Retrieves** relevant sections based on user questions
3. **Generates** accurate answers using OpenAI's language model

## 📁 Project Structure

```
billing-reports-rag/
│
├── data/
│   └── billing_requirements.txt    # Source documentation
│
├── rag/
│   ├── ingest.py                    # Document indexing script
│   └── query.py                     # Query system
│
├── vector_db/                       # Vector database (created after ingestion)
│
├── app.py                           # FastAPI backend
├── ui.py                            # Streamlit web interface
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

   Get your API key from: https://platform.openai.com/api-keys

### Step 3: Index the Documentation

Run the ingestion script to load and index the billing documentation:

```bash
python rag/ingest.py
```

This will:
- Load the billing requirements document
- Split it into chunks
- Create embeddings
- Store them in a vector database (`vector_db/`)

**Expected output:**
```
Loading billing documentation...
Loaded 1 document(s)
Splitting documents into chunks...
Created XX chunks
Creating embeddings...
Storing in vector database...
✅ Documents successfully indexed!
```

### Step 4: Query the System

You have three options to interact with the system:

#### Option A: Command-Line Interface

```bash
python rag/query.py
```

Then ask questions interactively:
```
Ask question: How is hauler cost calculated?
```

#### Option B: Streamlit Web UI

```bash
streamlit run ui.py
```

Open your browser to `http://localhost:8501` and use the web interface.

#### Option C: FastAPI Backend

```bash
python app.py
```

Or using uvicorn:
```bash
uvicorn app:app --reload
```

Then access the API at `http://localhost:8000` or use the interactive docs at `http://localhost:8000/docs`.

**Example API call:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How is hauler cost calculated?"}'
```

## 💡 Example Questions

You can ask questions like:

- **Contract Rules**: "What is the source of truth for billing data?"
- **Billing Dates**: "What billing dates are allowed?"
- **Services**: "Why are zero-priced monthly services shown?"
- **Pass-Through Charges**: "When are pass-through charges included?"
- **Hauler Costs**: "How are hauler costs prorated?"
- **Management Fees**: "How are management fees applied?"
- **Annual Price Increases**: "How are annual price increases calculated?"
- **Net Profit**: "How is net profit calculated?"

## 🔧 Technical Details

### Architecture

```
Billing Documentation
        ↓
Document Loader (TextLoader)
        ↓
Chunking (RecursiveCharacterTextSplitter)
        ↓
Embeddings (OpenAIEmbeddings)
        ↓
Vector Database (ChromaDB)
        ↓
Retriever (Similarity Search)
        ↓
LLM (GPT-4o-mini)
        ↓
AI Answers
```

### Key Components

- **LangChain**: Framework for building RAG applications
- **ChromaDB**: Vector database for storing embeddings
- **OpenAI**: Embeddings and language model
- **FastAPI**: REST API backend
- **Streamlit**: Web UI

### Configuration

- **Chunk Size**: 800 characters
- **Chunk Overlap**: 100 characters
- **Retrieval**: Top 3 most similar chunks
- **Model**: GPT-4o-mini

## 📝 Usage Examples

### Command Line

```bash
$ python rag/query.py

============================================================
Billing Documentation AI Assistant
============================================================
Ask questions about the Brokered Customer Billing Report.
Type 'exit' to quit.

Ask question: How is hauler cost calculated?

------------------------------------------------------------
Answer:
------------------------------------------------------------
Hauler cost is prorated based on overlapping days between 
the invoice service period and billing period...
```

### API

```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "How are management fees applied?"}
)

print(response.json()["answer"])
```

## 🛠️ Troubleshooting

### Vector Database Not Found
**Error**: `Vector database not found!`

**Solution**: Run `python rag/ingest.py` first to index the documents.

### OpenAI API Key Not Found
**Error**: `OPENAI_API_KEY not found`

**Solution**: 
1. Create a `.env` file from `.env.example`
2. Add your OpenAI API key to `.env`

### Import Errors
**Error**: `ModuleNotFoundError`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

## 📚 Documentation

The source documentation (`data/billing_requirements.txt`) contains:
- Customer Contract Dependencies
- Billing Date Rules
- Location & Service Management
- Multi-Location Add-On Charges
- Percentage-Based Charges
- Annual Price Increases (APIs)
- Pass-Through Charges
- Report Generation & Display
- Hauler Cost Calculation
- Q&A Section

## 🔄 Re-indexing

If you update the documentation, re-run the ingestion:

```bash
python rag/ingest.py
```

This will update the vector database with the latest content.

## 📄 License

This project is for internal use by the Techverx Development Team.

## 👥 Contributors

Prepared by: Techverx Development Team
Date: February 2026
