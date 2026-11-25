import pytest
from backend.tools.budget_tool import budget_tool
from backend.tools.weather_tool import weather_tool
from backend.tools.maps_tool import maps_tool
from backend.tools.conflict_detector import conflict_detector

def test_budget_tool_allocation():
    alloc = budget_tool.calculate_allocation(1000.0, "Balanced")
    assert alloc["accommodation"] == 350.0
    assert alloc["dining"] == 250.0
    assert sum(alloc.values()) == 1000.0

def test_weather_tool_fallback():
    forecast = weather_tool.get_forecast("Tokyo", days=3)
    assert forecast["destination"] == "Tokyo"
    assert len(forecast["forecast"]) == 3
    assert "temp_high_c" in forecast["forecast"][0]

def test_maps_tool_distance():
    dist, mins = maps_tool.calculate_distance_and_time(48.8566, 2.3522, 48.8606, 2.3376)
    assert dist > 0
    assert mins >= 5

def test_conflict_detector_rain_warning():
    days_data = [{
        "day_number": 1,
        "date": "2026-10-01",
        "activities": [{
            "name": "Botanical Garden Walking Tour",
            "start_time": "09:00",
            "end_time": "11:00",
            "category": "Attraction",
            "description": "Outdoor guided walking tour in gardens"
        }]
    }]
    weather_data = [{
        "date": "2026-10-01",
        "rain_probability_pct": 80,
        "condition": "Heavy Rain"
    }]
    conflicts = conflict_detector.detect_conflicts(days_data, weather_data)
    assert len(conflicts) >= 1
    assert conflicts[0]["type"] == "weather_conflict"
