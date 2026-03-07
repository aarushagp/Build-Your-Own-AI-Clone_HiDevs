#!/bin/bash

# Setup and run the AI Clone website locally

echo "🚀 Setting up AI Clone Website"
echo "=============================="

# Set API URL for frontend
export GROQ_API_KEY=${GROQ_API_KEY:-""}

if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  Warning: GROQ_API_KEY not set. Please set it:"
    echo "   export GROQ_API_KEY='your-key-here'"
    echo ""
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To run the application:"
echo ""
echo "  Terminal 1 (Backend):"
echo "  ├─ cd backend"
echo "  └─ python main.py"
echo ""
echo "  Terminal 2 (Frontend):"
echo "  ├─ cd frontend"
echo "  └─ python -m http.server 3000"
echo ""
echo "  Then open: http://localhost:3000"
echo ""
echo "💡 Environment Setup:"
echo "   export GROQ_API_KEY='your-groq-api-key'"
echo ""
