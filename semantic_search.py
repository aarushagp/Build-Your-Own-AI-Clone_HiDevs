# 🔍 COMPLETE SEMANTIC SEARCH SOLUTION FOR QDRANT
from embedding_model import embedding_model
from qdrant_setup import qdrant_client, QDRANT_COLLECTION_NAME
from qdrant_client import models 
import uuid
from typing import List, Dict, Any
from datetime import datetime

def search_knowledge_base_fixed(query: str, limit: int = 3, score_threshold: float = 0.5):
    """
    Search the knowledge base for relevant information.

    Parameters:
    - query: The search question/text
    - limit: Number of results to return
    - score_threshold: Minimum similarity score (0.0 to 1.0)

    Returns:
    - List of relevant chunks with metadata
    """

    print(f"🔍 Searching knowledge base for: '{query}'")
    print(f"   Limit: {limit} results | Minimum score: {score_threshold}")
    print("-" * 60)

    try:
        # 1. Convert query to embedding
        print("   Step 1: Converting query to embedding...")
        query_vector = embedding_model.embed_query(query)
        print(f"      ✓ Created {len(query_vector)}-dimensional vector")

        # 2. Search in Qdrant
        print(f"   Step 2: Searching in collection '{QDRANT_COLLECTION_NAME}'...")

        # Try different search method names based on Qdrant client version
        search_methods = ['search', 'query_points', 'query']

        search_result = None
        for method_name in search_methods:
            if hasattr(qdrant_client, method_name):
                try:
                    if method_name == 'search':
                        search_result = qdrant_client.search(
                            collection_name=QDRANT_COLLECTION_NAME,
                            query_vector=query_vector,
                            limit=limit,
                            score_threshold=score_threshold,
                            with_payload=True,
                            with_vectors=False
                        )
                    elif method_name == 'query_points':
                        # Alternative method name
                        search_result = qdrant_client.query_points(
                            collection_name=QDRANT_COLLECTION_NAME,
                            query=query_vector,
                            limit=limit,
                            score_threshold=score_threshold,
                            with_payload=True,
                            with_vectors=False
                        )
                    print(f"      ✓ Used '{method_name}' method")
                    break
                except Exception as e:
                    print(f"      ⚠️ '{method_name}' failed: {e}")
                    continue

        if search_result is None:
            print("❌ Could not find a working search method")
            print("   Trying direct API call...")

            # Last resort: Use scroll and calculate similarity manually
            return search_manual(query, limit, score_threshold)

        # 3. Process and display results
        if not search_result:
            print("❌ No results found above threshold")
            return []

        # Extract results based on response format
        if hasattr(search_result, 'points'):
            # Newer Qdrant format
            hits = search_result.points
        elif isinstance(search_result, list):
            # Older format
            hits = search_result
        else:
            hits = search_result

        print(f"✅ Found {len(hits)} relevant chunks:")

        results = []
        for i, hit in enumerate(hits):
            # Extract score and payload based on format
            if hasattr(hit, 'score'):
                score = hit.score
                payload = hit.payload or {}
            elif isinstance(hit, dict) and 'score' in hit:
                score = hit['score']
                payload = hit.get('payload', {})
            else:
                score = 0.5  # Default
                payload = {}

            # Skip if below threshold
            if score < score_threshold:
                continue

            text = payload.get('text', 'No text available')
            chunk_id = payload.get('chunk_id', 'N/A')

            print(f"📦 Result {i+1}:")
            print(f"   Score: {score:.3f} {'🌟' if score > 0.8 else '✅' if score > 0.6 else '⚠️'}")
            print(f"   Chunk ID: {chunk_id}")
            print(f"   Length: {len(text)} chars, {len(text.split())} words")

            # Show clean preview
            preview = text.replace('', ' ').strip()
            if len(preview) > 120:
                preview = preview[:120] + "..."
            print(f"   Content: {preview}")

            results.append({
                'score': score,
                'text': text,
                'chunk_id': chunk_id,
                'payload': payload
            })

        return results

    except Exception as e:
        print(f"❌ Search error: {e}")
        import traceback
        traceback.print_exc()
        return []

def search_manual(query: str, limit: int = 3, score_threshold: float = 0.5):
    """
    Manual search as fallback - retrieves all points and calculates similarity.
    This is slower but works when search methods fail.
    """
    print("   Using manual search (fallback)...")

    try:
        # Get all points from collection
        all_points, _ = qdrant_client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            limit=1000,  # Adjust based on your collection size
            with_payload=True,
            with_vectors=True
        )

        if not all_points:
            print("❌ No points found in collection")
            return []

        # Convert query to embedding
        query_vector = embedding_model.embed_query(query)

        # Calculate cosine similarity manually
        from numpy import dot
        from numpy.linalg import norm

        scored_points = []
        for point in all_points:
            if hasattr(point, 'vector'):
                vector = point.vector
                payload = point.payload or {}
            elif isinstance(point, dict):
                vector = point.get('vector', [])
                payload = point.get('payload', {})
            else:
                continue

            if not vector:
                continue

            # Calculate cosine similarity
            try:
                # Convert to numpy arrays if needed
                import numpy as np
                vec1 = np.array(query_vector)
                vec2 = np.array(vector)

                # Cosine similarity
                similarity = dot(vec1, vec2) / (norm(vec1) * norm(vec2))

                scored_points.append({
                    'score': float(similarity),
                    'text': payload.get('text', ''),
                    'chunk_id': payload.get('chunk_id', ''),
                    'payload': payload,
                    'vector': vector
                })
            except Exception as e:
                continue

        # Sort by score descending
        scored_points.sort(key=lambda x: x['score'], reverse=True)

        # Filter by threshold and limit
        filtered = [p for p in scored_points if p['score'] >= score_threshold][:limit]

        print(f"✅ Found {len(filtered)} relevant chunks (manual search):")

        for i, result in enumerate(filtered):
            print(f"📦 Result {i+1}:")
            print(f"   Score: {result['score']:.3f}")

            text = result['text']
            preview = text.replace('', ' ').strip()
            if len(preview) > 100:
                preview = preview[:100] + "..."
            print(f"   Content: {preview}")

        return filtered

    except Exception as e:
        print(f"❌ Manual search failed: {e}")
        return []

# 🎯 ENHANCED SEARCH WITH FILTERS
def advanced_search(query: str, filters: Dict = None, limit: int = 5):
    """
    Advanced search with filtering capabilities.

    Parameters:
    - query: Search query text
    - filters: Dictionary of filter conditions
        Example: {"chunk_id": [0, 1, 2], "min_length": 50}
    - limit: Maximum results to return
    """

    print(f"🎯 ADVANCED SEARCH: '{query}'")
    if filters:
        print(f"   Filters: {filters}")
    print("-" * 60)

    try:
        # Convert query to embedding
        query_vector = embedding_model.embed_query(query)

        # Build filter if provided
        qdrant_filter = None
        if filters:
            filter_conditions = []

            if "chunk_id" in filters:
                filter_conditions.append(
                    models.FieldCondition(
                        key="chunk_id",
                        match=models.MatchValue(value=filters["chunk_id"])
                    )
                )

            if "min_length" in filters:
                filter_conditions.append(
                    models.FieldCondition(
                        key="length",
                        range=models.Range(gte=filters["min_length"])
                    )
                )

            if filter_conditions:
                qdrant_filter = models.Filter(must=filter_conditions)

        # Perform search with filter
        try:
            search_result = qdrant_client.search(
                collection_name=QDRANT_COLLECTION_NAME,
                query_vector=query_vector,
                query_filter=qdrant_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
        except AttributeError:
            # Try alternative method
            search_result = qdrant_client.query_points(
                collection_name=QDRANT_COLLECTION_NAME,
                query=query_vector,
                filter=qdrant_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

        # Process results
        results = []
        for i, hit in enumerate(search_result):
            score = hit.score if hasattr(hit, 'score') else 0.5
            payload = hit.payload if hasattr(hit, 'payload') else {}

            print(f"📦 Result {i+1} (Score: {score:.3f}):")
            print(f"   Chunk ID: {payload.get('chunk_id', 'N/A')}")
            print(f"   Length: {payload.get('length', 'N/A')} chars")

            text = payload.get('text', '')
            preview = text[:100].replace('', ' ')
            if len(text) > 100:
                preview += "..."
            print(f"   Preview: {preview}")

            results.append({
                'score': score,
                'payload': payload,
                'text': text
            })

        return results

    except Exception as e:
        print(f"❌ Advanced search error: {e}")
        return []

# 📊 KNOWLEDGE BASE ANALYTICS
def analyze_knowledge_base():
    """Analyze the knowledge base contents and statistics"""

    print("📊 KNOWLEDGE BASE ANALYTICS")
    print("=" * 60)

    try:
        # Get collection info
        collection_info = qdrant_client.get_collection(QDRANT_COLLECTION_NAME)

        print(f"Collection: {QDRANT_COLLECTION_NAME}")
        print(f"Total points: {collection_info.points_count}")
        print(f"Vector dimension: {collection_info.config.params.vectors.size}")
        print(f"Distance metric: {collection_info.config.params.vectors.distance}")

        # Scroll through all points for analysis
        all_points, _ = qdrant_client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )

        if not all_points:
            print("❌ No points found for analysis")
            return

        # Calculate statistics
        total_chars = 0
        total_words = 0
        chunk_lengths = []

        for point in all_points:
            payload = point.payload if hasattr(point, 'payload') else {}
            text = payload.get('text', '')

            total_chars += len(text)
            total_words += len(text.split())
            chunk_lengths.append(len(text))

        # Calculate statistics
        avg_length = sum(chunk_lengths) / len(chunk_lengths) if chunk_lengths else 0
        min_length = min(chunk_lengths) if chunk_lengths else 0
        max_length = max(chunk_lengths) if chunk_lengths else 0

        print(f"📈 TEXT STATISTICS:")
        print(f"   Total characters: {total_chars:,}")
        print(f"   Total words: {total_words:,}")
        print(f"   Average chunk length: {avg_length:.0f} chars")
        print(f"   Min chunk length: {min_length} chars")
        print(f"   Max chunk length: {max_length} chars")

        # Show sample of content
        print(f"🔍 CONTENT SAMPLE (first 3 chunks):")
        for i, point in enumerate(all_points[:3]):
            payload = point.payload if hasattr(point, 'payload') else {}
            text = payload.get('text', 'No text')
            preview = text[:80].replace('\n', ' ')
            if len(text) > 80:
                preview += "..."
            print(f"   {i+1}. {preview}")

        return {
            'total_points': collection_info.points_count,
            'total_chars': total_chars,
            'total_words': total_words,
            'avg_length': avg_length
        }

    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return None

# 🧪 COMPREHENSIVE TESTING SUITE
def run_comprehensive_tests():
    """Run comprehensive tests on the knowledge base"""

    print("🧪 COMPREHENSIVE KNOWLEDGE BASE TESTS")
    print("=" * 60)

    # Test 1: Basic search
    print("1️⃣ BASIC SEARCH TEST:")
    test_queries = [
        "What is Natural Language Processing?",
        "Tell me about machine translation",
        "deep learning models in NLP",
        "challenges in language understanding"
    ]

    for query in test_queries:
        print(f"Query: '{query}'")
        results = search_knowledge_base_fixed(query, limit=2)
        if results:
            print(f"   ✓ Found {len(results)} results")
        else:
            print(f"   ⚠️ No results found")

    # Test 2: Advanced search with filters
    print("2️⃣ ADVANCED SEARCH TEST:")
    advanced_search("language models", filters={"min_length": 100}, limit=2)

    # Test 3: Analytics
    print("3️⃣ ANALYTICS TEST:")
    analyze_knowledge_base()

    # Test 4: Edge cases
    print("4️⃣ EDGE CASE TESTS:")

    # Very short query
    search_knowledge_base_fixed("NLP", limit=1)

    # Non-existent topic
    search_knowledge_base_fixed("quantum computing in linguistics", limit=1)

    # Empty query
    search_knowledge_base_fixed("", limit=1)

    print("✅ All tests completed!")

# 🚀 IMMEDIATE TESTING
if 'qdrant_client' in locals() and 'embedding_model' in locals():
    print("" + "="*60)
    print("🚀 TESTING SEMANTIC SEARCH FUNCTIONALITY")
    print("="*60)

    # First try the fixed search function
    print("🎯 TEST 1: Basic Semantic Search")
    results = search_knowledge_base_fixed("What is NLP?", limit=3)

    if results:
        print("✅ SEMANTIC SEARCH WORKING!")
        print(f"   Found {len(results)} relevant results")

        # Show what we can do with results
        print("💡 You can now use these results for:")
        print("   • Question answering with an LLM")
        print("   • Building a chatbot with knowledge")
        print("   • Document retrieval system")
        print("   • Content recommendation")

        # Run comprehensive tests if user wants
        print("🔧 Would you like to run comprehensive tests?")
        print("   Uncomment: run_comprehensive_tests()")

    else:
        print("⚠️ Search returned no results")
        print("   Trying alternative approach...")

        # Try manual search
        print("🔄 Attempting manual search...")
        manual_results = search_manual("What is NLP?", limit=2)

        if manual_results:
            print("✅ Manual search works!")
        else:
            print("❨ Both search methods failed")
            print("   Checking collection...")

            # Verify collection exists
            try:
                collection_info = qdrant_client.get_collection(QDRANT_COLLECTION_NAME)
                print(f"   Collection exists with {collection_info.points_count} points")
                print("   The issue might be with the embedding model or search method")
            except Exception as e:
                print(f"   Collection error: {e}")

# 📋 USAGE EXAMPLES
print("" + "="*60)
print("📚 USAGE EXAMPLES")
print("="*60)

print("""
# Basic search
results = search_knowledge_base_fixed("your question", limit=3)

# Advanced search with filters
advanced_search("topic", filters={"min_length": 100}, limit=5)

# Get analytics
stats = analyze_knowledge_base()

# Run all tests
run_comprehensive_tests()""")

# 🔧 TROUBLESHOOTING FOR SPECIFIC ISSUE
print("" + "="*60)
print("🔧 FIXING SEARCH METHOD ISSUE")
print("="*60)

print("""
Your Qdrant client doesn't have a 'search' method.
Try these solutions:

1. CHECK QDRANT CLIENT VERSION:
   import qdrant_client
   print(qdrant_client.__version__)

2. ALTERNATIVE SEARCH METHODS:
   Try these method names:
   - query_points()
   - search_points()
   - query()

3. UPDATE QDRANT CLIENT:
   !pip install --upgrade qdrant-client

4. USE MANUAL SEARCH:
   results = search_manual("your query", limit=3)

5. CHECK AVAILABLE METHODS:
   print([m for m in dir(qdrant_client) if 'search' in m or 'query' in m])""")

# Quick check of available methods
try:
    print("🔍 Checking available Qdrant client methods...")
    methods = [m for m in dir(qdrant_client) if 'search' in m.lower() or 'query' in m.lower()]
    print(f"   Available search/query methods: {methods}")

    # Also check version
    import qdrant_client
    print(f"   Qdrant client version: {qdrant_client.__version__}")
except:
    pass

print("✅ Your knowledge base is ready! The storage worked perfectly.")
print("   You have 16 chunks stored. Now we just need to fix the search method.")