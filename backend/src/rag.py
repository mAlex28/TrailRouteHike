
import random
from pathlib import Path
import chromadb
from chromadb.config import Settings
import anthropic
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent 
DB_PATH = BASE_DIR/"db"  # ChromaDB path

_embedder = None
_collection = None
_client = None

SHORT_HIKE_MAX_KM = 8.05 # under 5 miles
RELEVANCE_MAX_DISTANCE = 1.2 # check for routes within 1.2miles

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

def _build_where(difficulty, short_only):
    """Chroma metadata filter"""
    conditions = []
    if difficulty and difficulty != "all":
        conditions.append({"difficulty": {"$eq": difficulty}})
    if short_only:
        conditions.append({"distance_km": {"$lt": SHORT_HIKE_MAX_KM}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}

def retrieve_trails(query, difficulty="all", short_only=False, top_k=3):
    """Embed the query and return the top_k matching trails' metadata."""
    results = get_collection().query(
    query_embeddings=[embed_text(query)],
    n_results=top_k,
    where=_build_where(difficulty, short_only),
    include=["metadatas", "distances"],
    )
    trails = []
    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
        if dist <= RELEVANCE_MAX_DISTANCE:
            trails.append(meta)
    return trails

def plan_trail(query, difficulty="all", short_only=False, surprise=False, top_k=3):
    """Returns one trail dict, or None if nothing matches the filters."""
    trails = retrieve_trails(query, difficulty, short_only, top_k=top_k)
    if not trails:
        return None
    return random.choice(trails) if surprise else trails[0]

def suprise_trail():
    """A completely random trail — ignores query, difficulty, and distance."""
    all_meta = get_collection().get(include=["metadatas"])["metadatas"]
    return random.choice(all_meta) if all_meta else None

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
        "Use ONLY the provided trail context. Do not invent details.\n"
        "Do not use emojis.\n\n"

        f"The user asked: {query}\n\n"
        f"Selected trail:\n{context}\n\n"

        "First decide whether this trail match the location the user asked about?\n"
        "Check whether the description, location or station is related to the asked area.\n"

        "If it does NOT match, respond with exactly one line and nothing else:\n"
        "NO_MATCH\n\n"

        "If it DOES match, respond EXACTLY in this format:\n\n"
        "Respond EXACTLY in this format:\n\n"
        "Recommended trail: <trail name>\n"
        "Location: <location and country>\n"
        "Difficulty: <difficulty>\n"
        "Distance: <distance>\n"
        "Train station: <station>\n\n"
        "A numbered simple iternary:\n"
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
    



#   "If the trail is clearly not in the area the user asked about, open with "
#         "one short sentence like: 'There are no trails matching your search near "
#         "<area>, but here is the closest option available.' Then continue normally.\n\n"