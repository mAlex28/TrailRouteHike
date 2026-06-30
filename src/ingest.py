import json
import chromadb
from chromadb.config import Settings

from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")  
def embed_text(text):
    return _model.encode(text).tolist()

# Load trails.json
with open("data/trails_with_stations.json", "r") as f:
    trails = json.load(f)

# Initialise ChromaDB
client = chromadb.PersistentClient(path="db", settings=Settings(anonymized_telemetry=False))
collection = client.get_or_create_collection("trails")

def safe_text(trail):
    raw = (
        f"{trail['name']}. "
        f"Located near {trail.get('nearest_station')}. "
        f"{trail['difficulty']} difficulty. "
        f"{trail['distance_km']} km hike. "
        f"{trail['description']}"
    )
    return raw[:1500] 

# Ingest trails
for trail in trails:
    trail_id = f"{trail['name']}_{trail['nearest_station']}"
    text = safe_text(trail)
    embedding = embed_text(text)
    collection.add(
        ids=[trail_id],
        embeddings=[embedding],
        metadatas=[trail],
        documents=[text]
    )

print("Ingestion complete")