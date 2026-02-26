"""
VacaPlan AI — Unit Tests

Run with:  pytest tests/ -v
All tests use USE_MOCK_APIS=true (no real API calls).
"""
import os
import asyncio
import pytest

os.environ["USE_MOCK_APIS"] = "true"
os.environ["ANTHROPIC_API_KEY"] = "test-key"


# ── Tools Tests ───────────────────────────────────────────────────────────────

class TestCalendarTool:
    def test_mock_returns_date_list(self):
        from tools.calendar import _mock_availability
        slots = _mock_availability("2025-06-14", "2025-06-21")
        assert len(slots) == 8  # inclusive range
        assert slots[0] == "2025-06-14"
        assert slots[-1] == "2025-06-21"

    def test_handles_invalid_dates_gracefully(self):
        from tools.calendar import _mock_availability
        slots = _mock_availability("invalid", "invalid")
        assert isinstance(slots, list)
        assert len(slots) > 0


class TestFlightsTool:
    def test_mock_returns_list(self):
        from tools.flights import _mock_flights
        results = _mock_flights("CGK", "DPS", "2025-06-14", 2)
        assert len(results) == 3
        assert all("price_usd" in f for f in results)
        assert all("airline" in f for f in results)

    def test_price_scales_with_travelers(self):
        from tools.flights import _mock_flights
        f1 = _mock_flights("CGK", "DPS", "2025-06-14", 1)
        f2 = _mock_flights("CGK", "DPS", "2025-06-14", 2)
        # Garuda price should double
        assert f2[0]["price_usd"] == f1[0]["price_usd"] * 2


class TestHotelsTool:
    def test_mock_returns_list(self):
        from tools.hotels import _mock_hotels
        results = _mock_hotels("Bali", "2025-06-14", "2025-06-21")
        assert len(results) == 4
        assert all("price_per_night_usd" in h for h in results)
        assert all("total_usd" in h for h in results)

    def test_total_calculated_correctly(self):
        from tools.hotels import _mock_hotels
        results = _mock_hotels("Bali", "2025-06-14", "2025-06-21")
        layar = next(h for h in results if "Layar" in h["name"])
        # 7 nights × $240
        assert layar["total_usd"] == 240.0 * 7


class TestActivitiesTool:
    def test_mock_returns_activities(self):
        from tools.activities import _mock_activities
        results = _mock_activities("bali", ["beach", "culture"], 7)
        assert len(results) > 0
        assert all("name" in a for a in results)

    def test_style_tag_filtering(self):
        from tools.activities import _mock_activities
        beach_acts = _mock_activities("bali", ["beach"], 3)
        wellness_acts = _mock_activities("bali", ["wellness"], 3)
        # Beach activities should rank higher for beach style
        assert any("beach" in a.get("tags", []) for a in beach_acts[:3])

    def test_unknown_destination_uses_default(self):
        from tools.activities import _mock_activities
        results = _mock_activities("unknown-city-xyz", ["culture"], 3)
        assert len(results) > 0


class TestBudgetTool:
    def test_calculates_total(self):
        from tools.budget import calculate_total
        costs = calculate_total(
            flights=[{"price_usd": 200}],
            hotels=[{"total_usd": 1000}],
            day_plans=[{"estimated_cost_usd": 100}, {"estimated_cost_usd": 150}],
        )
        assert costs["total_usd"] == 1450.0
        assert costs["flights_usd"] == 200.0
        assert costs["hotels_usd"] == 1000.0
        assert costs["activities_usd"] == 250.0

    def test_within_budget_check(self):
        from tools.budget import is_within_budget
        costs = {"total_usd": 2500.0}
        assert is_within_budget(costs, 3000.0) is True
        assert is_within_budget(costs, 2000.0) is False

    def test_overage_calculation(self):
        from tools.budget import overage
        assert overage({"total_usd": 3500.0}, 3000.0) == 500.0
        assert overage({"total_usd": 2500.0}, 3000.0) == 0.0


# ── Booking Router Tests ──────────────────────────────────────────────────────

class TestBookingValidation:
    def test_invalid_otp_rejected(self):
        from routers.bookings import _validate_otp
        with pytest.raises(Exception):
            _validate_otp("999999", "some-session")

    def test_valid_dev_otp_accepted(self):
        from routers.bookings import _validate_otp
        os.environ["DEV_OTP"] = "123456"
        _validate_otp("123456", "some-session")  # Should not raise

    def test_mock_booking_receipt_structure(self):
        from routers.bookings import _mock_booking_receipt
        receipt = _mock_booking_receipt("test-session-id")
        assert receipt.status == "confirmed"
        assert receipt.total_charged_usd > 0
        assert receipt.confirmation_id is not None


# ── State Tests ───────────────────────────────────────────────────────────────

class TestSessionState:
    def test_initial_state(self):
        from agents.state import SessionState, TripRequest
        trip = TripRequest(
            destination="Bali, Indonesia",
            dates="2025-06-14 – 2025-06-21",
            budget=3000.0,
            travelers="2 adults",
            style="Beach & Culture",
        )
        session = SessionState(session_id="test-123", trip=trip)
        assert session.complete is False
        assert session.completed_steps == []
        assert session.itinerary is None

    def test_to_dict(self):
        from agents.state import SessionState, TripRequest
        trip = TripRequest(
            destination="Bali",
            dates="2025-06-14 – 2025-06-21",
            budget=3000.0,
            travelers="2",
            style="Beach",
        )
        session = SessionState(session_id="test-456", trip=trip)
        d = session.to_dict()
        assert "session_id" in d
        assert "completed_steps" in d
        assert "complete" in d
