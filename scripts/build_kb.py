# build_kb_local.py
import re, json, uuid
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

MODEL_NAME   = "all-MiniLM-L6-v2"          # change in one place
INDEX_NAME   = "risk_tactics_kb"
embedder     = SentenceTransformer(MODEL_NAME)
DIMENSION    = embedder.get_sentence_embedding_dimension()

# Skip version compatibility check
client = QdrantClient(host="qdrant", port=6333, check_compatibility=False)

# 1. (re)create collection with correct dimension - using non-deprecated method
if client.collection_exists(INDEX_NAME):
    client.delete_collection(INDEX_NAME)

client.create_collection(
    collection_name = INDEX_NAME,
    vectors_config  = models.VectorParams(size=DIMENSION, distance=models.Distance.COSINE)
)

# 2. load and split snippets
text   = Path("/app/data/raw_strategy.md").read_text(encoding="utf-8")
chunks = re.split(r"\n---\n", text.strip())

points = []
for i, chunk in enumerate(chunks):
    chunk = chunk.strip()
    if not chunk:
        continue
    
    # Debug: print first few chunks to understand the format
    if i < 3:
        print(f"Chunk {i}: {repr(chunk[:100])}")
    
    # Check if chunk contains the expected format [tag]body
    if "]" not in chunk:
        print(f"Skipping malformed chunk {i}: {repr(chunk[:50])}")
        continue
    
    try:
        tag, body = chunk.split("]", 1)
        
        # Parse metadata from tag
        if not tag.startswith("["):
            print(f"Skipping chunk {i}: tag doesn't start with '[': {repr(tag[:50])}")
            continue
            
        meta_str = tag[1:]  # Remove opening [
        meta = {}
        
        # Parse key:value pairs separated by semicolons
        if meta_str:
            for pair in meta_str.split(";"):
                if ":" in pair:
                    key, value = pair.split(":", 1)
                    meta[key.strip()] = value.strip()
        
        body = body.strip()
        if not body:
            continue
            
        vec  = embedder.encode(body).tolist()

        points.append(models.PointStruct(
            id      = uuid.uuid4().hex,
            vector  = vec,
            payload = meta | {"snippet": body}
        ))
        
    except Exception as e:
        print(f"Error processing chunk {i}: {e}")
        print(f"Chunk content: {repr(chunk[:100])}")
        continue

client.upsert(INDEX_NAME, points, wait=True)
print(f"✅ {len(points)} snippets embedded with {MODEL_NAME}")