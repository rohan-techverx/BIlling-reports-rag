# Step-by-Step Guide to Run the Project

Since you already have a virtual environment created, follow these steps:

## Step 1: Activate Your Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Step 2: Install Dependencies

Try installing packages in smaller batches:

```bash
# Core packages
pip install langchain langchain-community langchain-openai

# Vector database
pip install chromadb

# Other utilities
pip install tiktoken python-dotenv

# Web frameworks
pip install fastapi uvicorn streamlit

# OpenAI SDK
pip install openai
```

If you encounter dependency conflicts, try:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-deps
pip install langchain langchain-community langchain-openai chromadb tiktoken python-dotenv fastapi uvicorn streamlit openai
```

## Step 3: Verify .env File

Make sure your `.env` file exists and contains:

```
OPENAI_API_KEY=your_api_key_here
```

## Step 4: Index the Documentation

```bash
python rag/ingest.py
```

This will:
- Load the billing documentation
- Split it into chunks
- Create embeddings
- Store in vector database

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

## Step 5: Run the Application

Choose one of three options:

### Option A: Streamlit Web UI (Recommended)

```bash
streamlit run ui.py
```

Then open your browser to: `http://localhost:8501`

### Option B: Command Line Interface

```bash
python rag/query.py
```

### Option C: FastAPI Backend

```bash
python app.py
```

Or:
```bash
uvicorn app:app --reload
```

Then visit: `http://localhost:8000/docs` for API documentation

## Troubleshooting

### If pip installation fails:
1. Upgrade pip: `pip install --upgrade pip`
2. Try installing without dependency checking: `pip install --no-deps <package>`
3. Install packages individually

### If vector_db not found:
- Make sure you ran `python rag/ingest.py` successfully

### If OpenAI API errors:
- Check your `.env` file has the correct API key
- Verify the API key is valid at https://platform.openai.com/api-keys
