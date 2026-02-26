"""
Flights Tool — Amadeus Flight Offers API

Free tier: https://developers.amadeus.com/self-service/category/air/api-doc/flight-offers-search
In production: swap USE_MOCK_APIS=false and provide AMADEUS_API_KEY + AMADEUS_API_SECRET.
"""
import os
import httpx


AMADEUS_BASE = "https://test.api.amadeus.com/v2"  # Use production URL in prod


async def search_flights(
    origin: str,
    destination: str,
    date: str,
    travelers: int = 2,
    budget: float = 3000.0,
) -> list[dict]:
    """
    Search for flight offers. Returns a list of raw flight option dicts.
    """
    use_mock = os.getenv("USE_MOCK_APIS", "true").lower() == "true"
    if use_mock:
        return _mock_flights(origin, destination, date, travelers)

    token = await _get_amadeus_token()
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": date,
        "adults": travelers,
        "currencyCode": "USD",
        "max": 10,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AMADEUS_BASE}/shopping/flight-offers",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

    return _parse_amadeus_response(data)


async def _get_amadeus_token() -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://test.api.amadeus.com/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": os.environ["AMADEUS_API_KEY"],
                "client_secret": os.environ["AMADEUS_API_SECRET"],
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


def _parse_amadeus_response(data: dict) -> list[dict]:
    offers = []
    for offer in data.get("data", []):
        itinerary = offer["itineraries"][0]
        segment = itinerary["segments"][0]
        price = float(offer["price"]["grandTotal"])
        offers.append({
            "airline": segment["carrierCode"],
            "origin": segment["departure"]["iataCode"],
            "destination": segment["arrival"]["iataCode"],
            "departure": segment["departure"]["at"],
            "arrival": segment["arrival"]["at"],
            "price_usd": price,
            "cabin": offer["travelerPricings"][0]["fareDetailsBySegment"][0].get("cabin", "ECONOMY"),
        })
    return offers


def _mock_flights(origin: str, destination: str, date: str, travelers: int) -> list[dict]:
    return [
        {
            "airline": "Garuda Indonesia",
            "origin": origin,
            "destination": "DPS",
            "departure": f"{date}T06:30:00",
            "arrival": f"{date}T08:45:00",
            "price_usd": 89.0 * travelers,
            "cabin": "ECONOMY",
        },
        {
            "airline": "Lion Air",
            "origin": origin,
            "destination": "DPS",
            "departure": f"{date}T14:00:00",
            "arrival": f"{date}T16:15:00",
            "price_usd": 74.0 * travelers,
            "cabin": "ECONOMY",
        },
        {
            "airline": "Batik Air",
            "origin": origin,
            "destination": "DPS",
            "departure": f"{date}T09:00:00",
            "arrival": f"{date}T11:20:00",
            "price_usd": 105.0 * travelers,
            "cabin": "ECONOMY",
        },
    ]
