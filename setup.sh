#!/bin/bash

# Setup script for Billing Reports RAG Assistant

echo "🚀 Setting up Billing Reports RAG Assistant..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "Creating .env.example..."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env.example
    echo ""
    echo "📝 Please create a .env file with your OpenAI API key:"
    echo "   echo 'OPENAI_API_KEY=your_actual_key' > .env"
    echo ""
else
    echo "✅ .env file found"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your OpenAI API key to .env file"
echo "2. Run: python rag/ingest.py (to index documents)"
echo "3. Run: python rag/query.py (CLI) or streamlit run ui.py (Web UI)"
echo ""
