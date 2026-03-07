"""
FastAPI Backend for AI Clone System
Provides REST API for chat, PDF upload, and memory management
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import numpy as np
from PyPDF2 import PdfReader
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
import uuid

# Simple message classes
class HumanMessage:
    def __init__(self, content):
        self.content = content

class SystemMessage:
    def __init__(self, content):
        self.content = content

# Initialize FastAPI app
app = FastAPI(title="AI Clone API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PYDANTIC MODELS ====================

class ChatRequest(BaseModel):
    query: str
    use_pdf_only: bool = False

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    relevance_score: float
    memory_count: int

class SystemStatus(BaseModel):
    status: str
    pdf_loaded: bool
    memory_size: int

# ==================== INITIALIZE COMPONENTS ====================

print("🚀 Initializing AI Clone Backend...")

# Initialize semantic model
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Semantic model loaded")

# Initialize Qdrant (in-memory for simplicity, or use persistent client)
try:
    qdrant_client = QdrantClient(":memory:")
    print("✅ Qdrant vector database initialized")
except Exception as e:
    print(f"⚠️ Qdrant error: {e}")
    qdrant_client = None

# Initialize Groq Chat Model
try:
    from langchain_groq import ChatGroq
    
    # Check if API key is available
    if not os.getenv("GROQ_API_KEY"):
        print(f"⚠️ GROQ_API_KEY not set - chat will use fallback responses")
        chat = None
    else:
        chat = ChatGroq(temperature=0.7, model_name="llama-3.1-70b-versatile")
        print("✅ Groq chat model initialized")
except Exception as e:
    print(f"⚠️ Could not initialize Groq: {e}")
    chat = None

# Initialize Memory
try:
    from langchain.memory import ConversationBufferMemory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    print("✅ Conversation memory initialized")
except Exception as e:
    print(f"⚠️ Memory error: {e}")
    memory = None

# Knowledge base state
knowledge_base = []
collection_name = "ai_clone_knowledge"
pdf_loaded = False

# ==================== HELPER FUNCTIONS ====================

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF"""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> List[str]:
    """Split text into chunks"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - chunk_overlap
    
    return chunks

def add_to_knowledge_base(text: str) -> int:
    """Add text chunks to Qdrant"""
    global pdf_loaded
    
    chunks = chunk_text(text)
    embeddings = semantic_model.encode(chunks)
    
    # Create collection if it doesn't exist
    try:
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
    except:
        pass
    
    # Upload vectors
    points = [
        models.PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload={"text": chunk}
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
    
    qdrant_client.upsert(collection_name, points)
    pdf_loaded = True
    knowledge_base.extend(chunks)
    
    return len(chunks)

def search_knowledge(query: str, top_k: int = 3) -> List[str]:
    """Search knowledge base for relevant chunks"""
    if not pdf_loaded or not knowledge_base:
        return []
    
    try:
        query_embedding = semantic_model.encode(query).tolist()
        results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=0.3
        )
        
        return [result.payload["text"] for result in results]
    except Exception as e:
        print(f"Search error: {e}")
        return []

def evaluate_response_quality(query: str, response: str, sources: List[str]) -> float:
    """Evaluate response relevance score"""
    try:
        query_embedding = semantic_model.encode(query)
        response_embedding = semantic_model.encode(response)
        
        similarity = np.dot(query_embedding, response_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(response_embedding)
        )
        
        # Normalize to 0-1
        score = max(0, min(1, (similarity + 1) / 2))
        return score
    except:
        return 0.5

def get_memory_count() -> int:
    """Get number of stored interactions"""
    if memory:
        return len(memory.chat_memory.messages) // 2  # Divide by 2 (user + bot)
    return 0

# ==================== API ENDPOINTS ====================

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get system status"""
    return SystemStatus(
        status="running",
        pdf_loaded=pdf_loaded,
        memory_size=get_memory_count()
    )

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF and add to knowledge base"""
    try:
        contents = await file.read()
        
        # Save temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Extract and add to knowledge base
        with open(temp_path, "rb") as f:
            text = extract_text_from_pdf(f)
        
        chunks_added = add_to_knowledge_base(text)
        
        # Clean up
        os.remove(temp_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_added": chunks_added,
            "message": f"PDF loaded successfully with {chunks_added} chunks"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the AI clone"""
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Retrieve relevant knowledge
        sources = search_knowledge(query) if pdf_loaded and not request.use_pdf_only else []
        
        # Build context
        system_prompt = """You are an AI assistant representing HiDevs.
- Focused on AI education and workforce development
- Mentor-style communication
- No robotic phrases - speak like a human
- Short, clear responses"""
        
        if sources:
            context = f"Knowledge: {' | '.join(sources[:2])}\n\nUser question: {query}"
        else:
            context = query
        
        # Generate response
        if chat:
            try:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=context)
                ]
                response = chat.invoke(messages)
                generated_response = response.content
            except Exception as e:
                print(f"Chat error: {e}")
                generated_response = f"I understand you're asking about '{query}'. Based on the knowledge available, this is a great question!"
        else:
            # Fallback response when Groq is not available
            if sources:
                generated_response = f"Based on the available documents, regarding '{query}': This is an interesting topic related to the content in your uploaded materials. The system found {len(sources)} relevant sections that could help answer this question."
            else:
                generated_response = f"I understand you're asking about '{query}'. To give you better answers, please upload a PDF document first, or feel free to ask me anything!"
        
        # Save to memory if available
        if memory:
            try:
                memory.save_context({"input": query}, {"output": generated_response})
            except:
                pass
        
        # Evaluate
        relevance_score = evaluate_response_quality(query, generated_response, sources)
        
        return ChatResponse(
            response=generated_response,
            sources=sources[:2] if sources else [],
            relevance_score=relevance_score,
            memory_count=get_memory_count()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-memory")
async def clear_memory():
    """Clear conversation memory"""
    if memory:
        memory.clear()
    return {"status": "success", "message": "Memory cleared"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "semantic_model": "✅",
            "qdrant": "✅" if qdrant_client else "❌",
            "chat_model": "✅" if chat else "❌",
            "memory": "✅" if memory else "❌"
        }
    }

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "name": "AI Clone API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
