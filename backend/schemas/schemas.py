from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str
    password: Optional[str] = None
    full_name: Optional[str] = None

class FirebaseAuthRequest(BaseModel):
    email: EmailStr
    full_name: str
    firebase_uid: Optional[str] = None
    photo_url: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Trip Schemas ---
class TripCreate(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
    currency: str = "USD"
    travelers: int = 1
    travel_style: str = "Balanced"
    interests: List[str] = []
    food_preferences: str = "Local Cuisine"
    accommodation_preference: str = "Hotel"
    transportation_preference: str = "Public Transit"
    activity_intensity: str = "Moderate"

class TripUpdate(BaseModel):
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = None
    travelers: Optional[int] = None
    travel_style: Optional[str] = None
    interests: Optional[List[str]] = None

class TripOut(BaseModel):
    id: int
    user_id: int
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
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Activity & Itinerary Schemas ---
class ActivitySchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    category: str = "Attraction"
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_time: str
    end_time: str
    duration_minutes: int = 60
    estimated_cost: float = 0.0
    opening_hours: str = "09:00 - 18:00"
    travel_time_from_prev_mins: int = 15
    distance_from_prev_km: float = 2.0
    backup_option: Optional[str] = None
    is_cancelled: bool = False
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class ItineraryDaySchema(BaseModel):
    id: Optional[int] = None
    day_number: int
    date: str
    theme: Optional[str] = None
    weather_summary: Optional[str] = None
    activities: List[ActivitySchema] = []

    class Config:
        from_attributes = True

class ItineraryOut(BaseModel):
    id: int
    trip_id: int
    version: int
    is_active: bool
    total_estimated_cost: float
    summary: Optional[str] = None
    days: List[ItineraryDaySchema] = []
    created_at: datetime

    class Config:
        from_attributes = True


# --- Budget Schema ---
class BudgetBreakdown(BaseModel):
    total_budget: float
    currency: str
    estimated_total_cost: float
    remaining_budget: float
    accommodation: float
    dining: float
    transportation: float
    activities: float
    miscellaneous: float
    category_percentages: Dict[str, float]


# --- Disruption Schemas ---
class DisruptionCreate(BaseModel):
    disruption_type: str  # weather, cancellation, schedule_conflict, budget_overflow
    title: str
    description: str
    affected_date: Optional[str] = None

class DisruptionOut(BaseModel):
    id: int
    trip_id: int
    disruption_type: str
    title: str
    description: str
    affected_date: Optional[str] = None
    status: str
    resolution_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class HandleDisruptionRequest(BaseModel):
    disruption_id: int
    action: str  # auto_replan, replace_activity, ignore

class HandleDisruptionResponse(BaseModel):
    success: bool
    message: str
    updated_itinerary: Optional[ItineraryOut] = None


# --- Chat Schemas ---
class ChatMessageSchema(BaseModel):
    id: Optional[int] = None
    role: str
    content: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    trip_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str
    suggested_actions: List[str] = []
    updated_itinerary: Optional[ItineraryOut] = None


# --- Weather & Search Schemas ---
class WeatherRequest(BaseModel):
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class WeatherForecastDay(BaseModel):
    date: str
    condition: str
    temp_high_c: float
    temp_low_c: float
    rain_probability_pct: int
    wind_kmh: float
    icon: str

class WeatherResponse(BaseModel):
    destination: str
    forecast: List[WeatherForecastDay]

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = "attractions"

class SearchResultItem(BaseModel):
    title: str
    snippet: str
    url: Optional[str] = None
    source: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
