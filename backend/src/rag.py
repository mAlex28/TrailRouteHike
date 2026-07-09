
from pathlib import Path
import chromadb
from chromadb.config import Settings
import anthropic
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent 
DB_PATH = BASE_DIR / "db"  # ChromaDB path

_embedder = None
_collection = None
_client = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")  
    return _embedder

def get_collection():
    global _collection
    if _collection is None: 
        client = chromadb.PersistentClient(path=str(DB_PATH), settings=Settings(anonymized_telemetry=False))
        _collection = client.get_or_create_collection("trails")

    return _collection

def get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client

def pre_load():
    """Preload everything. Call once at server startup so the first
    request doesn't pay the model-loading cost."""
    get_embedder()
    get_collection()
    get_client()


def embed_text(text):
    return get_embedder().encode(text).tolist()

def retrieve_trails(query, top_k=3):
    """Embed the query and return the top_k matching trails' metadata."""
    results = get_collection().query(
        query_embeddings=[embed_text(query)],
        n_results=top_k,
        # Step 2 will add: where={...} filters for difficulty / distance
    )
    return results["metadatas"][0]

def generate_itinerary(query, trails):
    """Build the context block from retrieved trails and ask client
    for a recommendation."""
    context_blocks = []

    for trail in trails:
        block = (
            f"Trail name: {trail['name']}\n"
            f"Difficulty: {trail.get('difficulty')}\n"
            f"Distance: {trail.get('distance_km')} km\n"
            f"Nearest station: {trail.get('nearest_station')}\n"
            f"Station distance: {trail.get('station_distance_km')} km\n"
            f"Description: {trail.get('description')}\n"
        )
        context_blocks.append(block)
    
    context = "\n".join(context_blocks)

    prompt = (
        "You are a hiking assistant.\n"
        "Use ONLY the provided trail context.\n"
        "Do not invent trails that are not in the context.\n\n"

        f"User question: {query}\n\n"
        f"Relevant trails:\n{context}\n\n"

        "Respond EXACTLY in this format:\n\n"

        "Recommended trail: <trail name>\n"
        "Location: <location and country>\n"
        "Difficulty: <difficulty>\n"
        "Distance: <distance>\n"
        "Train station: <station>\n\n"

        "Simple Itinerary:\n"
    )

    response = get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return next(b.text for b in response.content if b.type == "text")

def answer_question(query, top_k=3):
    trails = retrieve_trails(query, top_k=top_k)
    if not trails:
        return None, None
    text = generate_itinerary(query, trails)
    return text, trails[0]
    

