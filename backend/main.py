"""
VacaPlan AI — FastAPI Entry Point
"""
import uuid
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents.graph import run_planning_graph
from agents.state import TripRequest, SessionState
from routers import bookings

app = FastAPI(title="VacaPlan AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bookings.router, prefix="/booking", tags=["Booking"])

# In-memory session store (use Redis in production)
sessions: dict[str, SessionState] = {}


# ── Schemas ─────────────────────────────────────────────────────────────────

class PlanRequest(BaseModel):
    destination: str
    dates: str
    budget: float
    travelers: str
    style: str
    payment_token: str | None = None  # Stripe vault token


class PlanResponse(BaseModel):
    session_id: str
    message: str


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.post("/plan", response_model=PlanResponse)
async def create_plan(req: PlanRequest):
    """
    Start an async planning session. Returns a session_id.
    Poll /status/{session_id} or stream /stream/{session_id} for updates.
    """
    session_id = str(uuid.uuid4())

    trip = TripRequest(
        destination=req.destination,
        dates=req.dates,
        budget=req.budget,
        travelers=req.travelers,
        style=req.style,
        payment_token=req.payment_token,
    )

    # Kick off background planning task
    sessions[session_id] = SessionState(session_id=session_id, trip=trip)
    asyncio.create_task(run_planning_graph(session_id, trip, sessions))

    return PlanResponse(session_id=session_id, message="Planning started")


@app.get("/status/{session_id}")
async def get_status(session_id: str):
    """Poll the current status and partial results for a planning session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id].to_dict()


@app.get("/stream/{session_id}")
async def stream_updates(session_id: str):
    """
    Server-Sent Events stream — emits a JSON event for every completed agent step.
    The frontend subscribes to this for real-time updates.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator():
        session = sessions[session_id]
        sent_steps = set()

        while not session.complete:
            for step in session.completed_steps:
                if step not in sent_steps:
                    yield f"data: {step}\n\n"
                    sent_steps.add(step)
            await asyncio.sleep(0.5)

        # Flush any remaining steps
        for step in session.completed_steps:
            if step not in sent_steps:
                yield f"data: {step}\n\n"

        yield "data: DONE\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "ok"}
