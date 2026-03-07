import chromadb
import ollama

def embed_text(text):
    response = ollama.embeddings(
        model="mxbai-embed-large",
        prompt=text
    )
    return response["embedding"]

def answer_question(query, top_k=3):
    # Connect to Vector DB
    client = chromadb.PersistentClient(path="db")
    collection = client.get_or_create_collection("trails")

    # Embed user question
    question_embed = embed_text(query)

    # Retrieve relevant trails
    results = collection.query(
        query_embeddings=[question_embed],
        n_results=top_k
    )

    # Build context for LLM metadata
    context_blocks = []
    for trail in results["metadatas"][0]:
        block = (
            f"Trail name: {trail['name']}\n"
            f"Difficulty: {trail.get('difficulty')}\n"
            f"Distance: {trail.get('distance_km')} km\n"
            f"Description: {trail.get('description')}\n"
        )
        context_blocks.append(block)
    
    context = "\n".join(context_blocks)

    # Prompt for Llama 3
    prompt = (
        "You are a hiking assistant.\n"
        "Use ONLY the provided trail context to answer the user.\n"
        "Do not invent trails that are not in the context.\n\n"
        f"User question: {query}\n\n"
        f"Relevant trails:\n{context}\n"
        "\nFormat the answer with:\n"
        "- Recommended trail\n"
        "- Train station to get off (if known or implied)\n"
        "- Simple itinerary\n"
    )

    # Call LLM
    response = ollama.generate(
        model="llama3",
        prompt=prompt
    )

    return response["response"]