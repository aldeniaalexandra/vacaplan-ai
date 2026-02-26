"""
Calendar Tool — Google Calendar Free/Busy API

Scope used: https://www.googleapis.com/auth/calendar.freebusy (read-only)
No event titles or participant data are ever accessed.

In production: swap the mock below with real OAuth2 + Google API client.
"""
import os
from datetime import date, timedelta


async def check_availability(start_date: str, end_date: str) -> list[str]:
    """
    Returns a list of ISO date strings that are free in the user's calendar.

    Production implementation would call:
        service.freebusy().query(body={
            "timeMin": f"{start_date}T00:00:00Z",
            "timeMax": f"{end_date}T23:59:59Z",
            "items": [{"id": "primary"}],
        }).execute()

    And return dates NOT in the busy blocks.
    """
    use_mock = os.getenv("USE_MOCK_APIS", "true").lower() == "true"

    if use_mock:
        return _mock_availability(start_date, end_date)

    # ── Production path ───────────────────────────────────────────────────────
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=os.environ["GOOGLE_ACCESS_TOKEN"],
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/calendar.freebusy"],
    )

    service = build("calendar", "v3", credentials=creds)
    result = service.freebusy().query(body={
        "timeMin": f"{start_date}T00:00:00Z",
        "timeMax": f"{end_date}T23:59:59Z",
        "items": [{"id": "primary"}],
    }).execute()

    busy_blocks = result["calendars"]["primary"]["busy"]
    busy_dates = {b["start"][:10] for b in busy_blocks}

    # Return all days in range that are NOT busy
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    all_dates = [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]
    return [d for d in all_dates if d not in busy_dates]


def _mock_availability(start_date: str, end_date: str) -> list[str]:
    """Returns all days in range as free (mock — no conflicts)."""
    try:
        start = date.fromisoformat(start_date.strip())
        end = date.fromisoformat(end_date.strip())
    except ValueError:
        # Fallback for natural language dates
        start = date(2025, 6, 14)
        end = date(2025, 6, 21)

    return [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]
