# 🤖 AI Clone Website - Full Stack Application

A complete web application for building and deploying your own AI clone with a web interface, backend API, and PDF knowledge base integration.

## 📋 Features

✅ **Web Interface** - Beautiful, responsive chat UI
✅ **Backend API** - FastAPI REST endpoints
✅ **PDF Upload** - Add documents to knowledge base
✅ **Semantic Search** - Vector-based retrieval
✅ **Conversation Memory** - Persistent chat history
✅ **Response Evaluation** - Quality scoring system
✅ **Real-time Status** - System health monitoring

## 🏗️ Project Structure

```
Build-Your-Own-AI-Clone_HiDevs/
├── backend/                    # FastAPI server
│   ├── main.py                # API endpoints
│   └── requirements.txt        # Python dependencies
├── frontend/                   # Web UI
│   └── index.html             # Single-page application
├── ai_clone_system.py         # Original CLI version
├── SETUP.sh                   # Installation script
└── README.md                  # This file
```

## 🚀 Quick Start

### 1️⃣ Prerequisites
- Python 3.8+
- `pip` package manager
- Groq API Key (get free at https://console.groq.com)

### 2️⃣ Set API Key
```bash
export GROQ_API_KEY="gsk_your_api_key_here"
```

### 3️⃣ Install Dependencies
```bash
bash SETUP.sh
```

Or manually:
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 4️⃣ Run Backend Server
```bash
cd backend
python main.py
```

The backend will start on `http://localhost:8000`

### 5️⃣ Run Frontend (in another terminal)
```bash
cd frontend
python -m http.server 3000
```

The frontend will be available at `http://localhost:3000`

### 6️⃣ Open in Browser
Navigate to: **http://localhost:3000**

## 📚 How to Use

### Chat with AI
1. Type your question in the message box
2. Click **Send** or press `Shift+Enter`
3. The AI responds with insights from the knowledge base

### Upload PDF
1. Click **📄 Upload PDF**
2. Select a PDF file from your computer
3. Wait for confirmation (shows chunk count)
4. Now the AI will use this knowledge in responses

### View Response Quality
Each response shows:
- **📊 Score** - Relevance score (0-100%)
- **📚 Sources** - Number of knowledge chunks used
- **💾 Memory** - Total interactions stored

### Clear Memory
- Click **🧹 Clear Memory** to reset conversation
- Useful for starting a new topic

### Check System Status
- Click **📊 Status** to see system health
- Shows if PDF is loaded and memory size

## 🔌 API Endpoints

### `POST /chat`
Send a message to the AI clone
```json
{
  "query": "What is HiDevs?",
  "use_pdf_only": false
}
```

### `POST /upload-pdf`
Upload a PDF to add to knowledge base
```bash
curl -F "file=@document.pdf" http://localhost:8000/upload-pdf
```

### `POST /clear-memory`
Clear conversation history
```bash
curl -X POST http://localhost:8000/clear-memory
```

### `GET /status`
Get system status
```bash
curl http://localhost:8000/status
```

### `GET /health`
Health check
```bash
curl http://localhost:8000/health
```

## 🛠️ Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- Groq - LLM API
- Qdrant - Vector database
- LangChain - AI orchestration
- Sentence-Transformers - Embeddings

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Responsive design
- Real-time chat updates

## 🔧 Configuration

### Environment Variables
```bash
GROQ_API_KEY=your_api_key_here     # Required
```

### Backend Settings (in `backend/main.py`)
- Port: 8000
- Model: llama-3.1-70b-versatile
- Temperature: 0.7
- Vector DB: In-memory Qdrant

### Frontend Settings (in `frontend/index.html`)
- API_URL: http://localhost:8000
- Server Port: 3000

## 📊 System Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Web UI)                │
│  ├─ Chat Interface                      │
│  ├─ PDF Upload                          │
│  └─ Settings & Status                   │
└──────────────┬──────────────────────────┘
               │ HTTP/JSON
┌──────────────▼──────────────────────────┐
│      Backend (FastAPI Server)           │
│  ├─ Chat Endpoint                       │
│  ├─ PDF Processing                      │
│  ├─ Semantic Search                     │
│  └─ Memory Management                   │
└──────────────┬──────────────────────────┘
               │ Vector Search
┌──────────────▼──────────────────────────┐
│    Knowledge Base (Qdrant)               │
│  ├─ Vector Embeddings                   │
│  ├─ Document Chunks                     │
│  └─ Semantic Index                      │
└─────────────────────────────────────────┘
```

## 🐛 Troubleshooting

### ❌ "Failed to connect to backend"
- Make sure backend is running: `cd backend && python main.py`
- Check if port 8000 is available: `lsof -i :8000`

### ❌ "GROQ_API_KEY not found"
```bash
export GROQ_API_KEY="your_key_here"
```

### ❌ "Module not found" errors
```bash
cd backend
pip install -r requirements.txt
```

### ❌ "Port 3000 already in use"
```bash
# Use different port
python -m http.server 3001
```

## 🚀 Deployment

### Deploy Backend to Cloud

**Render:**
1. Push code to GitHub
2. Create new Web Service on Render
3. Set environment: `GROQ_API_KEY`
4. Deploy!

**Railway:**
```bash
railway link
railway up
```

**Heroku:**
```bash
heroku create your-app-name
git push heroku main
heroku config:set GROQ_API_KEY="..."
```

### Deploy Frontend

**Netlify:**
1. Push frontend folder to GitHub
2. Connect GitHub to Netlify
3. Set build: `None` (it's static HTML)
4. Deploy!

**Vercel:**
```bash
npm install -g vercel
vercel --cwd frontend
```

## 📝 Example Queries

After uploading a document, try:
- "What is the main topic?"
- "Summarize the document"
- "What are the key points?"
- "Tell me about [specific topic]"

## 🤝 Contributing

Feel free to extend this project:
- Add more API endpoints
- Improve the UI
- Add authentication
- Implement file persistence
- Add voice chat

## 📄 License

This project is open source and available for educational purposes.

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [LangChain Docs](https://langchain.readthedocs.io)
- [Qdrant Vector DB](https://qdrant.tech)
- [Groq API](https://console.groq.com)

---

**Need Help?** Check the `/backend/main.py` comments for detailed explanations of each component!
