import json
import chromadb
from chromadb.config import Settings
import subprocess
import uuid
import ollama

def embed_text(text):
    response = ollama.embeddings(
        model="mxbai-embed-large",
        prompt=text
    )
    return response["embedding"]

# Load trails.json
with open("data/trails_with_stations.json", "r") as f:
    trails = json.load(f)

# Initialise ChromaDB
client = chromadb.PersistentClient(path="db", settings=Settings(anonymized_telemetry=False))
collection = client.get_or_create_collection("trails")

def safe_text(trail):
    raw = (
        f"{trail['name']}. "
        f"{trail['difficulty']} difficulty. "
        f"{trail['distance_km']} km hike. "
        f"Nearest train station: {trail.get('nearest_station')}. "
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


