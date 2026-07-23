import json
from pathlib import Path
import shutil
import chromadb
from chromadb.config import Settings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "trails_with_stations.json"
DB_PATH = BASE_DIR / "db"

def safe_text(trail):
    raw = (
        f"{trail['name']}. "
        f"Located near {trail.get('nearest_station')}. "
        f"{trail['difficulty']} difficulty. "
        f"{trail['distance_km']} km hike. "
        f"{trail['description']}"
    )
    return raw[:1500]

def metadata(trail):
    """flatten the coordinate lists into individual lat/lon fields and drop anything non-scalar."""
    meta = {k: v for k, v in trail.items() if isinstance(v, (str, int, float, bool))}

    lat, lon = trail["start_coord"]
    meta["start_lat"] = float(lat)
    meta["start_lon"] = float(lon)

    if trail.get("station_coord"):
        s_lat, s_lon = trail["station_coord"]
        meta["station_lat"] = float(s_lat)
        meta["station_lon"] = float(s_lon)

    return meta

with open(DATA_PATH, "r") as f:
    trails = json.load(f)

if DB_PATH.exists():
    shutil.rmtree(DB_PATH)

client = chromadb.PersistentClient(path=str(DB_PATH), settings=Settings(anonymized_telemetry=False))
collection = client.create_collection("trails")

# Ingest trails
for trail in trails:
    trail_id = f"{trail['name']}_{trail['nearest_station']}"
    collection.add(
        ids=[trail_id],
        metadatas=[metadata(trail)],
        documents=[safe_text(trail)],   
    )

print(f"Ingestion complete — {collection.count()} trails indexed")