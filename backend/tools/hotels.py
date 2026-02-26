"""
Hotels Tool — Booking.com Affiliate API

Docs: https://developers.booking.com/
In production: set USE_MOCK_APIS=false and provide BOOKING_API_KEY.
"""
import os
import httpx

BOOKING_BASE = "https://distribution-xml.booking.com/2.4/json"


async def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    travelers: int = 2,
    style_tags: list[str] | None = None,
) -> list[dict]:
    """
    Search hotels for destination and date range.
    Returns a list of hotel option dicts for Claude to rank.
    """
    use_mock = os.getenv("USE_MOCK_APIS", "true").lower() == "true"
    if use_mock:
        return _mock_hotels(destination, check_in, check_out)

    # Booking.com requires a destination_id lookup first
    dest_id = await _get_destination_id(destination)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BOOKING_BASE}/hotels",
            auth=(os.environ["BOOKING_USERNAME"], os.environ["BOOKING_PASSWORD"]),
            params={
                "city_ids": dest_id,
                "checkin": check_in,
                "checkout": check_out,
                "room1": f"A,A" if travelers == 2 else f"A" * travelers,
                "rows": 10,
                "order_by": "popularity",
                "filter_by_currency": "USD",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

    return _parse_booking_response(data, check_in, check_out)


async def _get_destination_id(destination: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BOOKING_BASE}/destinations",
            auth=(os.environ["BOOKING_USERNAME"], os.environ["BOOKING_PASSWORD"]),
            params={"text": destination, "language": "en"},
        )
        resp.raise_for_status()
        results = resp.json()
        return results[0]["id"]


def _parse_booking_response(data: dict, check_in: str, check_out: str) -> list[dict]:
    from datetime import date
    try:
        nights = (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days
    except Exception:
        nights = 7

    hotels = []
    for h in data.get("result", []):
        price_per_night = float(h.get("min_total_price", 150))
        hotels.append({
            "name": h.get("hotel_name", "Unknown Hotel"),
            "location": h.get("city", ""),
            "stars": int(h.get("class", 3)),
            "price_per_night_usd": price_per_night,
            "features": h.get("facilities", [])[:4],
            "total_usd": round(price_per_night * nights, 2),
        })
    return hotels


def _mock_hotels(destination: str, check_in: str, check_out: str) -> list[dict]:
    from datetime import date
    try:
        nights = (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days
    except Exception:
        nights = 7

    return [
        {
            "name": "The Layar Private Villas",
            "location": "Seminyak",
            "stars": 5,
            "price_per_night_usd": 240.0,
            "features": ["Private pool", "Ocean view", "Breakfast included", "Butler service"],
            "total_usd": round(240.0 * nights, 2),
        },
        {
            "name": "Alaya Resort Ubud",
            "location": "Ubud",
            "stars": 4,
            "price_per_night_usd": 160.0,
            "features": ["Rice field view", "Spa", "Yoga deck", "Free shuttle"],
            "total_usd": round(160.0 * nights, 2),
        },
        {
            "name": "Katamama Hotel",
            "location": "Seminyak",
            "stars": 5,
            "price_per_night_usd": 310.0,
            "features": ["Artisan suites", "Rooftop pool", "Fine dining", "Cultural experiences"],
            "total_usd": round(310.0 * nights, 2),
        },
        {
            "name": "Bisma Eight",
            "location": "Ubud",
            "stars": 4,
            "price_per_night_usd": 120.0,
            "features": ["Jungle view", "Infinity pool", "Organic breakfast", "Spa"],
            "total_usd": round(120.0 * nights, 2),
        },
    ]
