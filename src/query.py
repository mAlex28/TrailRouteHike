import chromadb
from chromadb.config import Settings
import ollama

def embed_text(text):
    response = ollama.embeddings(
        model="mxbai-embed-large",
        prompt=text
    )
    return response["embedding"]

def answer_question(query, top_k=3):
    # Connect to Vector DB
    client = chromadb.PersistentClient(path="db", settings=Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection("trails")

    # Embed user question
    question_embed = embed_text(query)

    # Retrieve relevant trails
    results = collection.query(
        query_embeddings=[question_embed],
        n_results=top_k
    )

    trails = results["metadatas"][0]

    # Build context for LLM metadata
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

    # Prompt for Llama 3
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

    response = ollama.generate(
        model="llama3",
        prompt=prompt
    )

    return response["response"], trails[0]

# if __name__ == "__main__":
#     print(answer_question("Show me hikes accessible from Wales by train"))