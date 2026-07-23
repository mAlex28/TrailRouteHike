# 🥾 TrackAndTrail

> A RAG application that connects UK hiking trails to their nearest train station.

## 🎯 Project Purpose

Not everyone has a car — but that should not stop anyone from getting out and
exploring the UK's trails.

TrackAndTrail was built to solve a simple problem: finding hiking trails you can
reach by train. Enter a location, pick a difficulty, and the app suggests a trail
along with the nearest train station to get you there.

The project was also a way for me to learn how RAG systems work in practice — how to
combine real structured data like train stations and coordinates with unstructured
text like trail descriptions, and make them work together inside one pipeline.
Each trail is linked to its nearest station using the Haversine formula to
calculate the real distance between two coordinates on Earth.

**Version 2** rebuilds the original local prototype (Streamlit + llama3 via
Ollama) into a full web application: a Next.js frontend, a FastAPI backend
serving the RAG pipeline, and Anthropic's Claude API generating the
itineraries.

## Demo

**[Try it here]()**

Demo video of the original v1 prototype:
[![Watch the demo](https://i9.ytimg.com/vi_webp/-6zh02UyQmI/mqdefault.webp?v=69b4790f&sqp=CPjw0c0G&rs=AOn4CLAvnAsnmXDKw8gNr2BQHLBrV62Nxg)](https://youtu.be/-6zh02UyQmI)

## 🚀 How to Run Locally

### Prerequisites

- Python 3.11+
- Node.js 20+
- An [Anthropic API key](https://console.anthropic.com)

### 1. Clone the repository

```bash
git clone https://github.com/mAlex28/TrailRouteHike
cd TrailRouteHike
```

### 2. Set up backend

```bash
cd backend
conda create -n trailroutehike-env python=3.11
conda activate trailroutehike-env
pip install -r requirements.txt
python src/connect_trails_stations.py
python src/ingest.py
```

### 3. Run the backend

```bash
uvicorn main:app --reload --port 8000
```

### 4. Run the frontend (in a different terminal)

```bash
cd frontend
npm install
npm run dev
```

## 🧱 Tech Stack

- **Frontend** — Next.js (React), Leaflet + OpenStreetMap
- **Backend** — FastAPI (Python)
- **RAG pipeline** — ChromaDB vector store, sentence-transformers embeddings,
  semantic search with metadata filtering
- **LLM** — Anthropic Claude API for itinerary generation
- **Geo** — Haversine formula for trail-to-station distances

## Project structure

```
TrailRouteHike/
│
├── backend/
│   ├── main.py                        # FastAPI app and API endpoints
│   ├── src/
│   │   ├── connect_trails_stations.py # Links trails to nearest station
│   │   ├── ingest.py                  # Embeds and stores trails in ChromaDB
│   │   └── rag.py                     # RAG pipeline: retrieval, filtering, generation
│   ├── data/
│   │   ├── trails.json                # Trail data
│   │   ├── stations.json              # UK train station data
│   │   └── trails_with_stations.json  # Merged dataset
│   ├── db/                            # ChromaDB persistent storage (generated)
│   └── requirements.txt
│
├── frontend/
│   ├── app/                           # Next.js pages, layout, global styles
│   ├── components/                    # Search panel, itinerary card, map
│   ├── hooks/                         # useTrailPlanner (search state + API calls)
│   └── lib/                           # API client and formatting utilities
│
└── README.md
```

## Previous Version

v1 ran entirely locally: a Streamlit UI, llama3 through Ollama for generation,
and a Pydeck map. The rebuild swapped these for a hosted web stack while
keeping the same core RAG pipeline and dataset.
