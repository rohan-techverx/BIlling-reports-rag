# Quick Start Guide

Get your Billing Documentation AI Assistant running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or use the setup script:
```bash
./setup.sh
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

Replace `your_actual_api_key_here` with your actual OpenAI API key.

### 3. Index the Documentation

This step loads and indexes your billing documentation:

```bash
python rag/ingest.py
```

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

⏱️ This takes about 1-2 minutes depending on your internet connection.

### 4. Start Using the System

Choose one of three interfaces:

#### Option A: Command Line (Simplest)

```bash
python rag/query.py
```

Then ask questions:
```
Ask question: How is hauler cost calculated?
```

#### Option B: Web UI (Recommended)

```bash
streamlit run ui.py
```

Open `http://localhost:8501` in your browser.

#### Option C: API Server

```bash
python app.py
```

Or:
```bash
uvicorn app:app --reload
```

Access API docs at: `http://localhost:8000/docs`

## Example Questions to Try

- "How is hauler cost calculated?"
- "What determines whether a customer appears in the report?"
- "How are management fees applied?"
- "Why are zero-priced monthly services shown?"
- "How are annual price increases calculated?"
- "What billing dates are allowed?"

## Troubleshooting

### "Vector database not found"
→ Run `python rag/ingest.py` first

### "OPENAI_API_KEY not found"
→ Create `.env` file with your API key

### Import errors
→ Run `pip install -r requirements.txt`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize chunk size in `rag/ingest.py` if needed
- Adjust retrieval parameters in `rag/query.py`

## Need Help?

Check the main [README.md](README.md) for comprehensive documentation and troubleshooting tips.
