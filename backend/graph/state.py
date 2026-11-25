from typing import TypedDict, List, Dict, Any, Optional

class PlannerState(TypedDict):
    trip_id: int
    destination: str
    start_date: str
    end_date: str
    budget: float
    currency: str
    travelers: int
    travel_style: str
    interests: List[str]
    food_preferences: str
    accommodation_preference: str
    transportation_preference: str
    activity_intensity: str

    search_results: List[Dict[str, Any]]
    weather_forecast: List[Dict[str, Any]]
    locations_data: List[Dict[str, Any]]
    calculated_budget: Dict[str, Any]
    
    draft_itinerary: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    
    retry_count: int
    is_valid: bool
    current_step_status: str
    final_itinerary_summary: str
    logs: List[str]
