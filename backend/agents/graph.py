"""
VacaPlan AI — LangGraph Orchestration Graph

Graph flow:
  START
    → preference_parser
    → calendar_checker
    → flight_searcher
    → hotel_searcher
    → activity_curator
    → budget_optimizer
    → plan_reviewer
  END

The BookingAgent is triggered separately via POST /booking/confirm,
after the user explicitly approves the plan.
"""
import asyncio
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

from agents.state import TripRequest, SessionState
from agents import nodes


# ── LangGraph State Dict ──────────────────────────────────────────────────────

class GraphState(TypedDict):
    session_id: str
    trip: dict
    available_slots: list[str]
    flights: list[dict]
    hotels: list[dict]
    day_plans: list[dict]
    itinerary: dict | None
    errors: Annotated[list[str], operator.add]


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(GraphState)

    graph.add_node("preference_parser", nodes.preference_parser)
    graph.add_node("calendar_checker", nodes.calendar_checker)
    graph.add_node("flight_searcher", nodes.flight_searcher)
    graph.add_node("hotel_searcher", nodes.hotel_searcher)
    graph.add_node("activity_curator", nodes.activity_curator)
    graph.add_node("budget_optimizer", nodes.budget_optimizer)
    graph.add_node("plan_reviewer", nodes.plan_reviewer)

    graph.set_entry_point("preference_parser")
    graph.add_edge("preference_parser", "calendar_checker")
    graph.add_edge("calendar_checker", "flight_searcher")
    graph.add_edge("flight_searcher", "hotel_searcher")
    graph.add_edge("hotel_searcher", "activity_curator")
    graph.add_edge("activity_curator", "budget_optimizer")
    graph.add_edge("budget_optimizer", "plan_reviewer")
    graph.add_edge("plan_reviewer", END)

    return graph.compile()


GRAPH = build_graph()


# ── Runner ────────────────────────────────────────────────────────────────────

async def run_planning_graph(
    session_id: str,
    trip: TripRequest,
    sessions: dict[str, SessionState],
):
    """
    Runs the LangGraph planning pipeline and updates the shared session state
    after each node completes, enabling real-time SSE streaming to the frontend.
    """
    session = sessions[session_id]

    initial_state: GraphState = {
        "session_id": session_id,
        "trip": trip.model_dump(),
        "available_slots": [],
        "flights": [],
        "hotels": [],
        "day_plans": [],
        "itinerary": None,
        "errors": [],
    }

    try:
        # stream_mode="updates" emits partial state after each node
        async for update in GRAPH.astream(initial_state, stream_mode="updates"):
            node_name = list(update.keys())[0]
            node_output = update[node_name]

            # Update shared session state
            if "available_slots" in node_output:
                session.available_slots = node_output["available_slots"]
            if "flights" in node_output:
                session.flights = node_output["flights"]
            if "hotels" in node_output:
                session.hotels = node_output["hotels"]
            if "day_plans" in node_output:
                session.day_plans = node_output["day_plans"]
            if "itinerary" in node_output and node_output["itinerary"]:
                from agents.state import TripItinerary
                session.itinerary = TripItinerary(**node_output["itinerary"])

            session.completed_steps.append(node_name)
            await asyncio.sleep(0)  # yield control so SSE can flush

    except Exception as e:
        session.error = str(e)

    finally:
        session.complete = True
