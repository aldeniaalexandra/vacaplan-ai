"""
Activities Tool — ChromaDB Vector Store + Semantic Retrieval

Stores a curated activity knowledge base per destination.
Uses nomic-embed-text (via Ollama) for embeddings.
Falls back to a mock list when USE_MOCK_APIS=true.
"""
import os
import json


ACTIVITY_DB: dict[str, list[dict]] = {
    "bali": [
        {"name": "Tegallalang Rice Terraces", "tags": ["culture", "nature"], "cost_usd": 5, "duration_hours": 3},
        {"name": "Tirta Empul Holy Spring Temple", "tags": ["culture", "spiritual"], "cost_usd": 3, "duration_hours": 2},
        {"name": "Scuba diving at Crystal Bay", "tags": ["adventure", "beach"], "cost_usd": 80, "duration_hours": 4},
        {"name": "Kecak Fire Dance at Uluwatu", "tags": ["culture", "evening"], "cost_usd": 15, "duration_hours": 2},
        {"name": "Mount Batur Volcano Sunrise Trek", "tags": ["adventure", "nature"], "cost_usd": 60, "duration_hours": 6},
        {"name": "Traditional Balinese Cooking Class", "tags": ["food", "culture"], "cost_usd": 45, "duration_hours": 4},
        {"name": "Canggu Surf Lesson", "tags": ["adventure", "beach"], "cost_usd": 35, "duration_hours": 2},
        {"name": "Tanah Lot Sea Temple", "tags": ["culture", "sunset"], "cost_usd": 5, "duration_hours": 2},
        {"name": "Ubud Monkey Forest", "tags": ["nature", "family"], "cost_usd": 5, "duration_hours": 2},
        {"name": "Jimbaran Seafood BBQ Dinner", "tags": ["food", "beach", "evening"], "cost_usd": 30, "duration_hours": 2},
        {"name": "Kintamani Coffee Plantation Tour", "tags": ["food", "culture"], "cost_usd": 20, "duration_hours": 3},
        {"name": "Nusa Lembongan Island Day Trip", "tags": ["beach", "adventure"], "cost_usd": 50, "duration_hours": 8},
        {"name": "Balinese Spa & Traditional Massage", "tags": ["wellness"], "cost_usd": 25, "duration_hours": 2},
        {"name": "Seminyak Boutique Shopping", "tags": ["shopping", "leisure"], "cost_usd": 0, "duration_hours": 3},
        {"name": "Potato Head Beach Club", "tags": ["beach", "leisure", "evening"], "cost_usd": 20, "duration_hours": 4},
    ],
    "default": [
        {"name": "City Walking Tour", "tags": ["culture"], "cost_usd": 20, "duration_hours": 3},
        {"name": "Local Food Market Visit", "tags": ["food"], "cost_usd": 15, "duration_hours": 2},
        {"name": "Museum & Heritage Sites", "tags": ["culture"], "cost_usd": 10, "duration_hours": 3},
        {"name": "Day Hike / Nature Walk", "tags": ["adventure", "nature"], "cost_usd": 10, "duration_hours": 5},
        {"name": "Cooking Class", "tags": ["food", "culture"], "cost_usd": 50, "duration_hours": 4},
        {"name": "Sunset Boat Cruise", "tags": ["leisure", "sunset"], "cost_usd": 40, "duration_hours": 2},
        {"name": "Spa Day", "tags": ["wellness"], "cost_usd": 60, "duration_hours": 3},
    ],
}


async def get_activity_suggestions(
    destination: str,
    style_tags: list[str],
    duration_days: int,
) -> list[dict]:
    """
    Returns a curated list of activities for the destination.
    In production: uses ChromaDB vector similarity to match style_tags.
    In mock mode: returns the hardcoded DB filtered by tag overlap.
    """
    use_mock = os.getenv("USE_MOCK_APIS", "true").lower() == "true"

    if use_mock:
        return _mock_activities(destination, style_tags, duration_days)

    return await _chroma_search(destination, style_tags, duration_days)


def _mock_activities(destination: str, style_tags: list[str], duration_days: int) -> list[dict]:
    key = destination.lower().split(",")[0].strip()
    pool = ACTIVITY_DB.get(key, ACTIVITY_DB["default"])

    # Score by tag overlap with user style
    scored = []
    for act in pool:
        overlap = len(set(act["tags"]) & set(style_tags))
        scored.append((overlap, act))

    scored.sort(key=lambda x: x[0], reverse=True)
    # Return enough activities to fill the itinerary (4 per day max)
    return [a for _, a in scored[: duration_days * 4]]


async def _chroma_search(destination: str, style_tags: list[str], duration_days: int) -> list[dict]:
    """
    Production: embed the style tags query and search ChromaDB collection.
    Requires Ollama running with nomic-embed-text model.
    """
    import chromadb
    from chromadb.utils import embedding_functions

    chroma = chromadb.HttpClient(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", 8000)),
    )

    ef = embedding_functions.OllamaEmbeddingFunction(
        url=os.getenv("OLLAMA_URL", "http://localhost:11434/api/embeddings"),
        model_name="nomic-embed-text",
    )

    collection = chroma.get_or_create_collection(
        name=f"activities_{destination.lower().replace(' ', '_')}",
        embedding_function=ef,
    )

    query_text = f"Activities for {destination} with style: {', '.join(style_tags)}"
    results = collection.query(
        query_texts=[query_text],
        n_results=min(duration_days * 4, 20),
    )

    activities = []
    for i, doc in enumerate(results["documents"][0]):
        try:
            activities.append(json.loads(doc))
        except json.JSONDecodeError:
            activities.append({"name": doc, "tags": style_tags, "cost_usd": 20, "duration_hours": 2})

    return activities
