# 🏗️ COMPLETE AI CLONE SYSTEM IMPLEMENTATION

# First, ensure we have all necessary packages
print("📦 Installing required packages...")


print("🚀 BUILDING COMPLETE AI CLONE SYSTEM")
print("=" * 70)

# Import all necessary components
import sys
import os
import numpy as np
import uuid
from PyPDF2 import PdfReader
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer, util

print("🔧 Importing AI components...")

# Try to import LangChain components with fallbacks
components_loaded = {
    "text_splitter": False,
    "embeddings": False,
    "chat_model": False,
    "memory": False
}

# Text Splitter
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    components_loaded["text_splitter"] = True
    print("✅ RecursiveCharacterTextSplitter loaded")
except ImportError:
    print("⚠️ Creating custom text splitter")

    class RecursiveCharacterTextSplitter:
        def __init__(self, chunk_size=500, chunk_overlap=100):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap

        def split_text(self, text):
            chunks = []
            start = 0
            text_length = len(text)

            while start < text_length:
                end = start + self.chunk_size
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                start = end - self.chunk_overlap
            return chunks

# Embeddings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    components_loaded["embeddings"] = True
    print("✅ HuggingFaceEmbeddings loaded")
except ImportError:
    print("⚠️ Creating custom embeddings wrapper")

    class HuggingFaceEmbeddings:
        def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
            self.model = SentenceTransformer(model_name)

        def embed_query(self, text):
            return self.model.encode(text).tolist()

# Chat Model
try:
    from langchain_groq import ChatGroq
    components_loaded["chat_model"] = True
    print("✅ ChatGroq loaded")
except ImportError:
    print("⚠️ ChatGroq not available")
    ChatGroq = None

# Message Classes
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    print("✅ Message classes loaded")
except ImportError:
    print("⚠️ Creating custom message classes")

    class HumanMessage:
        def __init__(self, content):
            self.content = content

    class SystemMessage:
        def __init__(self, content):
            self.content = content

# Memory
try:
    from langchain.memory import ConversationBufferMemory
    components_loaded["memory"] = True
    print("✅ ConversationBufferMemory loaded")
except ImportError:
    print("⚠️ Creating custom memory system")

    class ConversationBufferMemory:
        def __init__(self, memory_key="chat_history", return_messages=True):
            self.memory_key = memory_key
            self.return_messages = return_messages
            self.chat_history = []

        def save_context(self, inputs, outputs):
            if "input" in inputs:
                self.chat_history.append({"input": inputs["input"], "output": outputs["output"]})

        def load_memory_variables(self, inputs):
            return {"chat_history": self.chat_history}

        def clear(self):
            self.chat_history = []

print("🔧 Component Summary:")
for component, loaded in components_loaded.items():
    status = "✅" if loaded else "⚠️ (custom)"
    print(f"   {status} {component}")

# ==================== KNOWLEDGE BASE SETUP ====================
print("📚 SETTING UP KNOWLEDGE BASE")
print("-" * 70)

# Load PDF if not already loaded
if 'chunks' not in locals() or len(chunks) == 0:
    print("Loading knowledge from PDF...")

    def load_pdf(file_path):
        try:
            reader = PdfReader(file_path)
            text = "".join([page.extract_text() or "" for page in reader.pages])
            print(f"✅ Loaded PDF with {len(reader.pages)} pages")
            return text
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return ""

    pdf_text = load_pdf("ITI_AITechnologyStack.pdf")

    if pdf_text:
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_text(pdf_text)
        print(f"✅ Created {len(chunks)} knowledge chunks")
    else:
        print("⚠️ No PDF text loaded. Using demo chunks.")
        chunks = [
            "Deepak Chawla is the founder of HiDevs, focused on building AI workforce.",
            "HiDevs provides GenAI education and mentorship programs.",
            "The goal is to create practical AI learning experiences."
        ]

# ==================== VECTOR DATABASE SETUP ====================
print("💾 SETTING UP VECTOR DATABASE")
print("-" * 70)

# Initialize Qdrant
try:
    qdrant_client = QdrantClient(":memory:")
    print("✅ Qdrant initialized (in-memory)")
except:
    print("⚠️ Could not initialize Qdrant")
    qdrant_client = None

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
print("✅ Embedding model loaded")

# Store chunks if Qdrant is available
if qdrant_client and 'chunks' in locals() and chunks:
    # Create collection
    try:
        qdrant_client.create_collection(
            collection_name="ai_clone_kb",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

        # Store chunks
        points = []
        for i, chunk in enumerate(chunks):
            embedding = embedding_model.embed_query(chunk)
            points.append(models.PointStruct(
                id=str(uuid.uuid4()),
                payload={"text": chunk, "chunk_id": i},
                vector=embedding,
            ))

        qdrant_client.upsert(
            collection_name="ai_clone_kb",
            wait=True,
            points=points
        )

        print(f"✅ Stored {len(chunks)} knowledge chunks")
    except Exception as e:
        print(f"⚠️ Could not store chunks: {e}")

# ==================== AI MODEL SETUP ====================
print("🤖 SETTING UP AI MODELS")
print("-" * 70)

# Initialize semantic model for evaluation
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Semantic evaluation model loaded")

# Initialize Groq Chat Model
if ChatGroq:
    try:
        # Use environment variable for API key (set GROQ_API_KEY in your environment)
        chat = ChatGroq(temperature=0.7, model_name="openai/gpt-oss-20b")
        print("✅ Groq chat model initialized")
    except Exception as e:
        print(f"⚠️ Could not initialize Groq: {e}")
        chat = None
else:
    print("⚠️ ChatGroq not available")
    chat = None

# Initialize Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
print("✅ Conversation memory initialized")

# ==================== HELPER FUNCTIONS ====================
print("🔧 SETTING UP HELPER FUNCTIONS")
print("-" * 70)

def get_recent_chat_history(n=8):
    """Get recent conversation history"""
    past_chat_history = memory.load_memory_variables({}).get("chat_history", [])
    return past_chat_history[-n:] if past_chat_history else ["No recent conversation"]

def get_memory_usage():
    """Get number of stored interactions"""
    chat_history = memory.load_memory_variables({}).get("chat_history", [])
    return len(chat_history)

def retrieve_context_from_qdrant(query, top_k=3):
    """Retrieve relevant knowledge from vector database"""
    try:
        if not qdrant_client:
            return ["Knowledge base not available"]

        query_embedding = embedding_model.embed_query(query)

        # Search for similar vectors
        search_result = qdrant_client.query_points(
            collection_name="ai_clone_kb",
            query=query_embedding,
            limit=top_k,
            with_payload=True,
            with_vectors=False
        )

        if search_result and hasattr(search_result, 'points'):
            contexts = []
            for point in search_result.points:
                if hasattr(point, 'payload') and 'text' in point.payload:
                    contexts.append(point.payload['text'])
            return contexts if contexts else ["No relevant knowledge found"]
        else:
            return ["Search failed"]

    except Exception as e:
        return [f"Error: {str(e)}"]

def evaluate_response(user_query, generated_response, context):
    """Evaluate how relevant the response is to the context"""
    try:
        if not context or context[0] in ["No relevant knowledge found", "Search failed", "Knowledge base not available"]:
            return 0.0

        response_embedding = semantic_model.encode(generated_response, convert_to_tensor=True)
        context_text = " ".join(context) if isinstance(context, list) else str(context)
        context_embedding = semantic_model.encode(context_text, convert_to_tensor=True)

        similarity = util.pytorch_cos_sim(response_embedding, context_embedding)[0][0].item()
        return max(0.0, min(1.0, similarity))  # Clamp to 0-1 range

    except:
        return 0.0

# ==================== MAIN AI CLONE FUNCTION ====================
print("🎭 DEFINING AI CLONE PERSONALITY")
print("-" * 70)

def query_ai_clone(user_query):
    """
    Main function to interact with the AI clone.
    Combines: personality + memory + knowledge + LLM
    """

    # 🎭 Personality definition
    system_prompt = """You are an AI representation of Deepak Chawla, founder of HiDevs.

CORE PERSONALITY:
- Direct, practical, results-oriented
- Focused on AI education and workforce development
- Mentor-style communication
- No robotic phrases - speak like a human
- Short, clear responses

KNOWLEDGE AREAS:
- HiDevs mission and programs
- Generative AI education
- Building tech products
- Career development in AI

COMMUNICATION RULES:
1. Never say you're an AI/assistant
2. Respond based on your knowledge
3. Be helpful but direct
4. Focus on actionable advice
"""

    # 🧠 Get conversation context
    past_chat = get_recent_chat_history()
    retrieved_knowledge = retrieve_context_from_qdrant(user_query)

    # 📦 Assemble context
    context = f"""Past conversation: {past_chat}

Relevant knowledge:
{' | '.join(retrieved_knowledge)}

Current question: {user_query}"""

    # 🤖 Generate response
    if chat:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=context)
        ]

        try:
            response = chat.invoke(messages)
            generated_response = response.content
        except Exception as e:
            generated_response = f"I understand you're asking about '{user_query}'. Based on what I know, this seems relevant to our work at HiDevs."
    else:
        # Fallback response
        generated_response = f"Regarding '{user_query}', this relates to our focus on AI education and building practical skills."

    # 💾 Save to memory
    memory.save_context({"input": user_query}, {"output": generated_response})

    # 📊 Evaluate response quality
    evaluation_score = evaluate_response(user_query, generated_response, retrieved_knowledge)

    # 📝 Display information
    memory_usage = get_memory_usage()
    print(f"💭 Memory: {memory_usage} past interactions")
    print(f"📊 Relevance score: {evaluation_score:.2f}/1.00")

    if retrieved_knowledge and retrieved_knowledge[0] not in ["No relevant knowledge found", "Search failed"]:
        print(f"📚 Knowledge used: {len(retrieved_knowledge)} chunks")
        for i, ctx in enumerate(retrieved_knowledge[:2]):
            print(f"   {i+1}. {ctx[:80]}...")

    return generated_response

# ==================== INTERACTIVE CHAT INTERFACE ====================
print("💬 STARTING INTERACTIVE CHAT")
print("=" * 70)
print("Type 'exit' to quit, 'clear' to reset memory, 'help' for commands")
print("-" * 70)

interaction_count = 0

while True:
    try:
        user_query = input(f"[{interaction_count}] You: ").strip()

        if not user_query:
            continue

        # Special commands
        if user_query.lower() == "exit":
            print("👋 Goodbye! Thanks for chatting with the AI clone.")
            break

        elif user_query.lower() == "clear":
            memory.clear()
            interaction_count = 0
            print("🧹 Memory cleared. Starting fresh conversation.")
            continue

        elif user_query.lower() == "help":
            print("📋 Available commands:")
            print("   • exit - End the conversation")
            print("   • clear - Reset conversation memory")
            print("   • help - Show this help message")
            print("   • Anything else - Chat with the AI clone")
            continue

        # Normal query
        print("🤖 AI Clone is thinking...")
        print("-" * 70)

        response = query_ai_clone(user_query)

        print(f"🤖 Response: {response}")

        interaction_count += 1

        # Show conversation stats every 5 interactions
        if interaction_count % 5 == 0:
            print(f"📈 Conversation stats: {interaction_count} interactions")
            print(f"   Memory contains: {get_memory_usage()} exchanges")

    except KeyboardInterrupt:
        print("👋 Interrupted. Type 'exit' to quit or continue chatting.")
    except Exception as e:
        print(f"⚠️ Error: {e}")
        print("Please try again or type 'exit' to quit.")

# ==================== FINAL SUMMARY ====================
print(" " + "=" * 70)
print("🎉 AI CLONE SYSTEM - COMPLETE!")
print("=" * 70)

print("✅ What You've Built:")
print("1. 🧠 Intelligent AI clone with specific personality")
print("2. 💾 Knowledge base from PDF documents")
print("3. 🔍 Semantic search using vector embeddings")
print("4. 💬 Conversational memory system")
print("5. 📊 Real-time response evaluation")

print("🔧 Technical Components Used:")
print("   • Llama 3 via Groq (LLM)")
print("   • All-MiniLM-L6-v2 (Embeddings)")
print("   • Qdrant (Vector Database)")
print("   • LangChain (Orchestration)")
print("   • RAG Architecture (Retrieval-Augmented Generation)")

print("🚀 Next Steps You Can Explore:")
print("   • Add more documents to the knowledge base")
print("   • Fine-tune the personality with more examples")
print("   • Add web search capability")
print("   • Create a web interface for the clone")
print("   • Deploy to cloud for 24/7 access")

print("🌟 Congratulations! You've built a complete AI clone system!")
print("   This is the foundation for countless AI applications.")