"""
VacaPlan AI — LangGraph Node Implementations

Each node receives the full GraphState dict and returns a partial update dict.
Nodes call the appropriate tools and use Claude for reasoning/generation.
"""
import json
import os
from anthropic import AsyncAnthropic

from tools import calendar, flights, hotels, activities, budget

client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-20250514"


# ── Helper: call Claude ───────────────────────────────────────────────────────

async def claude(system: str, user: str, max_tokens: int = 1024) -> str:
    """Simple Claude call, returns the text content."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


async def claude_json(system: str, user: str, max_tokens: int = 2048) -> dict | list:
    """Claude call that parses JSON response."""
    text = await claude(system + "\n\nRespond ONLY with valid JSON, no markdown.", user, max_tokens)
    # Strip potential markdown fences
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


# ── Node 1: Preference Parser ─────────────────────────────────────────────────

async def preference_parser(state: dict) -> dict:
    """
    Validates and enriches the raw TripRequest into a structured, normalized form.
    Uses Claude to extract implicit preferences (e.g., 'budget beach trip' → style tags).
    """
    trip = state["trip"]

    enriched = await claude_json(
        system="You are a travel preference parser. Extract and enrich vacation preferences.",
        user=f"""
Given this trip request, return a JSON object with these fields:
- destination_city (string)
- destination_country (string)
- start_date (ISO 8601)
- end_date (ISO 8601)
- duration_nights (int)
- budget_usd (float)
- traveler_count (int)
- style_tags (list of strings from: beach, culture, adventure, food, wellness, family, luxury, budget)
- preferred_activities (list of strings, inferred from style)

Trip request: {json.dumps(trip)}
""",
    )

    return {"trip": {**trip, **enriched}}


# ── Node 2: Calendar Checker ──────────────────────────────────────────────────

async def calendar_checker(state: dict) -> dict:
    """
    Checks the user's Google Calendar for availability in the requested date range.
    Returns a list of confirmed free windows.
    """
    trip = state["trip"]
    slots = await calendar.check_availability(
        start_date=trip.get("start_date", trip["dates"].split("–")[0].strip()),
        end_date=trip.get("end_date", trip["dates"].split("–")[-1].strip()),
    )
    return {"available_slots": slots}


# ── Node 3: Flight Searcher ───────────────────────────────────────────────────

async def flight_searcher(state: dict) -> dict:
    """
    Queries the flight search tool (Amadeus API) and uses Claude to rank results
    by value score (price, convenience, airline rating).
    """
    trip = state["trip"]

    raw_flights = await flights.search_flights(
        origin=trip.get("origin", "CGK"),  # Default Jakarta
        destination=trip.get("destination_city", trip["destination"]),
        date=trip.get("start_date", trip["dates"].split("–")[0].strip()),
        travelers=trip.get("traveler_count", 2),
        budget=trip.get("budget_usd", trip["budget"]),
    )

    # Ask Claude to pick the top 2 by value
    ranked = await claude_json(
        system="You are a flight value analyst. Rank flights by value score (price, duration, airline quality).",
        user=f"From these options, return the top 2 as a JSON list. Each item: airline, origin, destination, departure, arrival, price_usd, cabin.\n\n{json.dumps(raw_flights)}",
    )

    return {"flights": ranked}


# ── Node 4: Hotel Searcher ────────────────────────────────────────────────────

async def hotel_searcher(state: dict) -> dict:
    """
    Queries hotel search tool and uses Claude to filter by style match and budget fit.
    """
    trip = state["trip"]
    duration = trip.get("duration_nights", 7)
    budget = trip.get("budget_usd", trip["budget"])

    raw_hotels = await hotels.search_hotels(
        destination=trip.get("destination_city", trip["destination"]),
        check_in=trip.get("start_date", ""),
        check_out=trip.get("end_date", ""),
        travelers=trip.get("traveler_count", 2),
        style_tags=trip.get("style_tags", ["beach"]),
    )

    ranked = await claude_json(
        system="You are a hotel curator. Select the best 2 hotels that match the traveler's style and fit the budget.",
        user=f"""
Trip style tags: {trip.get('style_tags', [])}
Total budget: ${budget} USD
Duration: {duration} nights

From these options, return the top 2 as a JSON list.
Each item: name, location, stars, price_per_night_usd, features (list), total_usd.

Options: {json.dumps(raw_hotels)}
""",
    )

    return {"hotels": ranked}


# ── Node 5: Activity Curator ──────────────────────────────────────────────────

async def activity_curator(state: dict) -> dict:
    """
    Uses Claude to generate a day-by-day activity plan based on destination,
    style preferences, and the selected hotels' locations.
    """
    trip = state["trip"]
    selected_hotels = state.get("hotels", [])
    duration = trip.get("duration_nights", 7)

    suggestions = await activities.get_activity_suggestions(
        destination=trip.get("destination_city", trip["destination"]),
        style_tags=trip.get("style_tags", ["beach", "culture"]),
        duration_days=duration,
    )

    day_plans = await claude_json(
        system="You are an expert travel itinerary planner. Create a detailed, realistic day-by-day plan.",
        user=f"""
Create a {duration}-day itinerary for {trip['destination']}.
Style: {trip.get('style_tags', [])}
Hotels located at: {[h.get('location', '') for h in selected_hotels]}
Available activities pool: {json.dumps(suggestions)}

Return a JSON list of {duration} objects, each with:
- day (int, 1-indexed)
- title (string, evocative day theme)
- activities (list of 3-4 activity strings)
- estimated_cost_usd (float, realistic daily spend per person)
""",
        max_tokens=3000,
    )

    return {"day_plans": day_plans}


# ── Node 6: Budget Optimizer ──────────────────────────────────────────────────

async def budget_optimizer(state: dict) -> dict:
    """
    Checks if the assembled plan fits within the user's budget.
    If over budget, asks Claude to suggest swaps (downgrade hotel tier, remove costly activities).
    """
    trip = state["trip"]
    budget = float(trip.get("budget_usd", trip.get("budget", 3000)))

    flights_cost = sum(f.get("price_usd", 0) for f in state.get("flights", []))
    hotels_cost = sum(h.get("total_usd", 0) for h in state.get("hotels", []))
    activities_cost = sum(d.get("estimated_cost_usd", 0) for d in state.get("day_plans", []))
    total = flights_cost + hotels_cost + activities_cost

    if total <= budget:
        # Already within budget — build final itinerary
        return _build_itinerary(state, total, budget)

    # Over budget — ask Claude for optimizations
    optimized = await claude_json(
        system="You are a travel budget optimizer. Suggest minimal changes to fit within budget.",
        user=f"""
Budget: ${budget} USD
Current total: ${total:.2f} USD (over by ${total - budget:.2f})

Flights cost: ${flights_cost}
Hotels cost: ${hotels_cost}
Activities cost: ${activities_cost}

Day plans: {json.dumps(state.get('day_plans', []))}
Hotels: {json.dumps(state.get('hotels', []))}

Return a JSON object with:
- optimized_day_plans: adjusted day plans list (same schema)
- optimized_hotels: adjusted hotels list (same schema)
- savings_usd: float
- changes_summary: string describing what was changed
""",
    )

    new_state = {**state}
    if "optimized_day_plans" in optimized:
        new_state["day_plans"] = optimized["optimized_day_plans"]
    if "optimized_hotels" in optimized:
        new_state["hotels"] = optimized["optimized_hotels"]

    new_total = total - optimized.get("savings_usd", 0)
    return _build_itinerary(new_state, new_total, budget)


def _build_itinerary(state: dict, total: float, budget: float) -> dict:
    from agents.state import TripItinerary, FlightOption, HotelOption, DayPlan
    trip = state["trip"]

    itinerary = {
        "destination": trip["destination"],
        "dates": trip["dates"],
        "flights": state.get("flights", []),
        "hotels": state.get("hotels", []),
        "day_plans": state.get("day_plans", []),
        "total_estimated_usd": round(total, 2),
        "budget_remaining_usd": round(budget - total, 2),
    }
    return {"itinerary": itinerary}


# ── Node 7: Plan Reviewer ─────────────────────────────────────────────────────

async def plan_reviewer(state: dict) -> dict:
    """
    Final coherence check: Claude reviews the complete itinerary for logical issues
    (impossible travel times, activity conflicts, missing days) and assigns a
    confidence score. If score < 0.7, flags for human review.
    """
    itinerary = state.get("itinerary")
    if not itinerary:
        return {"errors": ["No itinerary to review"]}

    review = await claude_json(
        system="You are a senior travel consultant reviewing an AI-generated itinerary for quality and coherence.",
        user=f"""
Review this itinerary and return a JSON object with:
- confidence_score: float 0.0–1.0
- issues: list of strings (logical problems found, empty list if none)
- suggestions: list of strings (optional improvements)
- approved: bool (true if confidence_score >= 0.7)

Itinerary: {json.dumps(itinerary)}
""",
    )

    # Attach review metadata to itinerary
    updated_itinerary = {**itinerary, "review": review}
    return {"itinerary": updated_itinerary}
