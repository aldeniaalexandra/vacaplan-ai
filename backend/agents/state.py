"""
Shared Pydantic schemas and session state used across the agent graph.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from pydantic import BaseModel


# ── Input Schema ─────────────────────────────────────────────────────────────

class TripRequest(BaseModel):
    destination: str
    dates: str
    budget: float
    travelers: str
    style: str
    payment_token: str | None = None


# ── Output Schemas ───────────────────────────────────────────────────────────

class FlightOption(BaseModel):
    airline: str
    origin: str
    destination: str
    departure: str
    arrival: str
    price_usd: float
    cabin: str = "Economy"


class HotelOption(BaseModel):
    name: str
    location: str
    stars: int
    price_per_night_usd: float
    features: list[str]
    total_usd: float


class DayPlan(BaseModel):
    day: int
    title: str
    activities: list[str]
    estimated_cost_usd: float


class TripItinerary(BaseModel):
    destination: str
    dates: str
    flights: list[FlightOption]
    hotels: list[HotelOption]
    day_plans: list[DayPlan]
    total_estimated_usd: float
    budget_remaining_usd: float


# ── Session State ─────────────────────────────────────────────────────────────

@dataclass
class SessionState:
    session_id: str
    trip: TripRequest
    completed_steps: list[str] = field(default_factory=list)
    available_slots: list[str] = field(default_factory=list)
    flights: list[FlightOption] = field(default_factory=list)
    hotels: list[HotelOption] = field(default_factory=list)
    day_plans: list[DayPlan] = field(default_factory=list)
    itinerary: TripItinerary | None = None
    error: str | None = None
    complete: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "completed_steps": self.completed_steps,
            "complete": self.complete,
            "itinerary": self.itinerary.model_dump() if self.itinerary else None,
            "error": self.error,
        }
