from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag import generate_itinerary, plan_trail, pre_load, suprise_trail

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the embedder / Chroma / Anthropic client
    pre_load()
    yield

app = FastAPI(title="TrackAndTrail API", lifespan=lifespan)

class PlanRequest(BaseModel):
    query: str
    difficulty: str = "all"        # "all" | "Easy" | "Moderate" | "Hard"
    short_only: bool = False       # only trails under 5 miles
    surprise: bool = False         # pick randomly
    include_itinerary: bool = True # ask Claude for the itinerary


def to_response(trail, itinerary=None):
    km = float(trail["distance_km"])

    # Fall back to the trailhead if a station coord is missing,
    station_lat = trail.get("station_lat", trail["start_lat"])
    station_lon = trail.get("station_lon", trail["start_lon"])

    return {
        "id": trail["name"].lower().replace(" ", "-"),
        "name": trail["name"],
        "location": trail.get("country", ""),
        "difficulty": trail.get("difficulty", "Moderate"),
        "distanceKm": km,
        "distanceMi": round(km * 0.621371, 1),
        "station": trail.get("nearest_station", ""),
        "stationCoords": [trail["start_lat"] if station_lat is None else station_lat,
                          station_lon],
        "trailCoords": [trail["start_lat"], trail["start_lon"]],
        "description": trail.get("description", ""),
        "itinerary": itinerary,
    }


@app.post("/api/trails/plan")
def plan(req: PlanRequest):
    if req.surprise:
        trail = suprise_trail()
    else:
        trail = plan_trail(req.query, difficulty=req.difficulty, short_only=req.short_only)

    if trail is None:
        raise HTTPException(status_code=404, detail="No trail matches those filters")

    itinerary_query = "Recommend this trail to me." if req.surprise else req.query
    itinerary = generate_itinerary(itinerary_query, [trail]) if req.include_itinerary else None

    if itinerary and itinerary.strip().splitlines()[0].startswith("NO_MATCH"):
        raise HTTPException(status_code=404, detail="No trails match that location and filters")

    return to_response(trail, itinerary)


from src.rag import get_collection

@app.get("/api/debug")
def debug():
    coll = get_collection()
    results = coll.query(query_texts=["hike near Edale"], n_results=3,
                         include=["metadatas", "distances"])
    return {
        "count": coll.count(),
        "sample_distances": results["distances"][0],
        "sample_names": [m["name"] for m in results["metadatas"][0]],
    }

@app.get("/api/allgood")
def allgood():
    return {"status": "ok"}