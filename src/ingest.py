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
with open("data/trails.json", "r") as f:
    trails = json.load(f)

# Initialise Chroma
client = chromadb.PersistentClient(path="db")
collection = client.get_or_create_collection("trails")

def safe_text(trail):
    raw = f"{trail['name']}. {trail['difficulty']}. {trail['distance_km']} km. {trail['description']}"
    return raw[:1500] 

# Ingest trails
for trail in trails:
    trail_id = str(uuid.uuid4())
    text = safe_text(trail)
    embedding = embed_text(text)
    collection.add(
        ids=[trail_id],
        embeddings=[embedding],
        metadatas=[trail],
        documents=[text]
    )

    print("Ingestion complete")


