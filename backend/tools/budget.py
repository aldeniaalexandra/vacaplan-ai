"""
Budget Tool — Simple constraint utilities used by the BudgetOptimizer node.
The actual LLM-driven optimization logic lives in agents/nodes.py.
This module provides pure helper functions.
"""


def calculate_total(
    flights: list[dict],
    hotels: list[dict],
    day_plans: list[dict],
) -> dict[str, float]:
    """
    Returns a breakdown of costs across all trip components.
    """
    flights_cost = sum(f.get("price_usd", 0) for f in flights)
    hotels_cost = sum(h.get("total_usd", 0) for h in hotels)
    activities_cost = sum(d.get("estimated_cost_usd", 0) for d in day_plans)
    total = flights_cost + hotels_cost + activities_cost

    return {
        "flights_usd": round(flights_cost, 2),
        "hotels_usd": round(hotels_cost, 2),
        "activities_usd": round(activities_cost, 2),
        "total_usd": round(total, 2),
    }


def is_within_budget(costs: dict[str, float], budget: float) -> bool:
    return costs["total_usd"] <= budget


def overage(costs: dict[str, float], budget: float) -> float:
    return max(0.0, costs["total_usd"] - budget)
