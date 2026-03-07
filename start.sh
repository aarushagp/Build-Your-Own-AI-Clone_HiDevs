#!/bin/bash

# 🚀 QUICK START GUIDE FOR AI CLONE WEBSITE

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🤖 AI CLONE WEBSITE - QUICK START GUIDE              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check API Key
echo "Step 1️⃣  Setting up API Key..."
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  GROQ_API_KEY is not set!"
    echo "   Get a free key at: https://console.groq.com"
    echo ""
    echo "   Then run:"
    echo "   export GROQ_API_KEY='gsk_your_key_here'"
    echo ""
    read -p "Enter your Groq API Key (or press Ctrl+C to quit): " api_key
    export GROQ_API_KEY="$api_key"
fi
echo "✅ API Key configured"
echo ""

# Step 2: Install
echo "Step 2️⃣  Installing dependencies..."
cd backend
pip install -q -r requirements.txt
cd ..
echo "✅ Dependencies installed"
echo ""

# Step 3: Start Backend
echo "Step 3️⃣  Starting Backend Server..."
echo ""
echo "   💡 TIP: Run this in a NEW terminal (or background)"
echo "   Command: cd backend && python main.py"
echo ""
echo "   Then press Enter to continue with frontend..."
read

# Step 4: Start Frontend
echo "Step 4️⃣  Starting Frontend Server..."
echo ""
cd frontend
echo "✅ Frontend starting on http://localhost:3000"
echo "   Press Ctrl+C to stop"
echo ""
python -m http.server 3000
