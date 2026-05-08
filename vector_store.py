from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from encryption import encrypt, decrypt
import config, hashlib
from datetime import datetime

pc         = Pinecone(api_key=config.PINECONE_API_KEY)
INDEX_NAME = "butler-memory"
DIMENSION  = 384

_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model

def get_index():
    existing = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME, dimension=DIMENSION, metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(INDEX_NAME)

def save_memory(text: str, category: str = "conversation", rating: int = 0) -> str:
    try:
        index    = get_index()
        mem_id   = hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()
        embedding = get_embed_model().encode(text).tolist()
        index.upsert(vectors=[(mem_id, embedding, {
            "encrypted_text": encrypt(text),
            "category":       category,
            "timestamp":      str(datetime.now()),
            "rating":         rating
        })])
        return mem_id
    except Exception as e:
        print(f"Memory save error: {e}")
        return ""

def recall_memory(query: str, top_k: int = 4) -> list:
    if not query.strip():
        return []
    try:
        index          = get_index()
        query_embedding = get_embed_model().encode(query).tolist()
        results        = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
        memories = []
        for match in results.matches:
            if match.score > 0.4:
                try:
                    memories.append({
                        "text":      decrypt(match.metadata["encrypted_text"]),
                        "relevance": round(match.score, 2),
                        "category":  match.metadata.get("category", "general"),
                        "rating":    match.metadata.get("rating", 0)
                    })
                except Exception:
                    pass
        return memories
    except Exception as e:
        print(f"Memory recall error: {e}")
        return []

def save_feedback(response_preview: str, rating: int):
    category = "success_pattern" if rating >= 4 else "correction_note"
    save_memory(f"[FEEDBACK {rating}/5] {response_preview[:300]}", category, rating)
