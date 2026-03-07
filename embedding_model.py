# 🤖 INITIALIZING THE EMBEDDING MODEL

print("🚀 Loading Embedding Model: All-MiniLM-L6-v2")
print("=" * 60)

# Try to import from langchain_huggingface first
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    print("✅ Using langchain_huggingface (professional integration)")
    print("   Benefits: Caching, batching, LangChain compatibility")

except ImportError:
    print("⚠️ langchain_huggingface not available")
    print("   Falling back to direct sentence-transformers")

    from sentence_transformers import SentenceTransformer

    # Create a compatible wrapper
    class HuggingFaceEmbeddings:
        """Wrapper to make SentenceTransformer work like LangChain's HuggingFaceEmbeddings"""

        def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
            print(f"   Loading model: {model_name}")
            self.model = SentenceTransformer(model_name)
            print(f"   Model loaded! Dimension: {self.model.get_sentence_embedding_dimension()}")

        def embed_query(self, text):
            """Convert a single text to embedding vector"""
            return self.model.encode(text).tolist()

        def embed_documents(self, texts):
            """Convert multiple texts to embedding vectors"""
            return self.model.encode(texts).tolist()

    print("✅ Created HuggingFaceEmbeddings wrapper")

# 🎯 FUNCTION TO INITIALIZE EMBEDDING MODEL
def initialize_embedding_model():
    """
    Initialize and test the HuggingFace embedding model.

    This model will be our 'understanding engine' that converts
    text into mathematical representations (vectors).
    """

    print("🔧 Initializing embedding model...")

    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    print(f"   Model: {model_name}")
    print(f"   Expected dimension: 384")
    print(f"   This might take a minute to download the first time...")

    # Initialize the model
    embedding_model = HuggingFaceEmbeddings(model_name=model_name)

    # Test the model with a simple example
    print("🧪 Testing embedding model...")

    test_sentences = [
        "Artificial Intelligence is amazing",
        "AI technology is incredible",
        "I ate an apple for breakfast"
    ]

    # Generate embeddings
    embeddings = []
    for sentence in test_sentences:
        embedding = embedding_model.embed_query(sentence)
        embeddings.append(embedding)

        # Show basic info
        print(f"   • '{sentence[:30]}...' → Vector length: {len(embedding)}")

    # Verify dimensions
    expected_dim = 384
    actual_dim = len(embeddings[0])

    if actual_dim == expected_dim:
        print(f"✅ Model initialized correctly!")
        print(f"   • Dimension: {actual_dim} (matches expected {expected_dim})")
        print(f"   • Type: Float vectors")
        print(f"   • Range: Typically -1.0 to 1.0")
    else:
        print(f"⚠️ Unexpected dimension: {actual_dim} (expected {expected_dim})")

    # Demonstrate similarity
    print("🔍 Testing semantic similarity:")

    # Calculate cosine similarity between first two sentences
    import numpy as np
    from numpy.linalg import norm

    vec1 = np.array(embeddings[0])
    vec2 = np.array(embeddings[1])
    vec3 = np.array(embeddings[2])

    # Cosine similarity formula
    cos_sim_1_2 = np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))
    cos_sim_1_3 = np.dot(vec1, vec3) / (norm(vec1) * norm(vec3))

    print(f"   • Similar sentences (AI-related): {cos_sim_1_2:.3f}")
    print(f"   • Different sentences (AI vs breakfast): {cos_sim_1_3:.3f}")

    # Interpretation
    print("📊 Similarity Interpretation:")
    print("   • 0.00: No relationship")
    print("   • 0.00-0.30: Weak relationship")
    print("   • 0.30-0.70: Moderate relationship")
    print("   • 0.70-1.00: Strong relationship")

    if cos_sim_1_2 > 0.5:
        print(f"✅ Success! Model correctly identifies similar meanings!")

    return embedding_model

# 🚀 INITIALIZE THE MODEL
embedding_model = initialize_embedding_model()

# 💡 KEY INSIGHTS
print("🌟 What We've Accomplished:")
print("1. 🔤 Loaded a state-of-the-art language understanding model")
print("2. 🧮 Successfully converted text to numerical vectors")
print("3. 🔍 Verified semantic similarity works correctly")
print("4. ⚡ Ready to process our knowledge base chunks")

# 🎯 NEXT: We'll use this model to convert our text chunks into vectors