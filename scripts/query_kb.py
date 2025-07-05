from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

# Connect to your knowledge base - no need for check_compatibility=False now
client = QdrantClient(host="qdrant", port=6333)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def query_by_phase(phase):
    """Get all chunks for a specific phase (early, mid, late)"""
    result = client.scroll(
        collection_name="risk_tactics_kb",
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="phase",
                    match=MatchValue(value=phase)
                )
            ]
        ),
        limit=100
    )
    
    return result[0]  # Returns list of points

def query_by_cards(card_bucket):
    """Get all chunks for a specific card bucket (low, mid, high)"""
    result = client.scroll(
        collection_name="risk_tactics_kb",
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="card_bucket",
                    match=MatchValue(value=card_bucket)
                )
            ]
        ),
        limit=100
    )
    
    return result[0]

def semantic_search(query_text, limit=5):
    """Search by meaning/content similarity"""
    query_vector = embedder.encode(query_text).tolist()
    
    # Use modern query_points API
    result = client.query_points(
        collection_name="risk_tactics_kb",
        query=query_vector,
        limit=limit
    )
    
    return result.points

def combined_search(query_text, phase=None, card_bucket=None, limit=5):
    """Search with both semantic similarity and metadata filters"""
    query_vector = embedder.encode(query_text).tolist()
    
    filters = []
    if phase:
        filters.append(FieldCondition(key="phase", match=MatchValue(value=phase)))
    if card_bucket:
        filters.append(FieldCondition(key="card_bucket", match=MatchValue(value=card_bucket)))
    
    search_filter = Filter(must=filters) if filters else None
    
    # Use modern query_points API
    result = client.query_points(
        collection_name="risk_tactics_kb",
        query=query_vector,
        query_filter=search_filter,
        limit=limit
    )
    
    return result.points

# Example usage
if __name__ == "__main__":
    # Get all early phase chunks
    print("=== ALL EARLY PHASE CHUNKS ===")
    early_chunks = query_by_phase("early")
    for point in early_chunks:
        print(f"ID: {point.id}")
        print(f"Phase: {point.payload['phase']}, Cards: {point.payload['card_bucket']}")
        print(f"Snippet: {point.payload['snippet'][:100]}...")
        print("---")
    
    print(f"\n=== SEMANTIC SEARCH: 'card timing' ===")
    results = semantic_search("card timing")
    for result in results:
        print(f"Score: {result.score:.3f}")
        print(f"Phase: {result.payload['phase']}, Cards: {result.payload['card_bucket']}")
        print(f"Snippet: {result.payload['snippet'][:100]}...")
        print("---")
    
    print(f"\n=== COMBINED: 'elimination' in late game ===")
    results = combined_search("elimination", phase="late")
    for result in results:
        print(f"Score: {result.score:.3f}")
        print(f"Snippet: {result.payload['snippet'][:100]}...")
        print("---")