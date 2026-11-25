from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=False)
    budget = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    travelers = Column(Integer, default=1)
    travel_style = Column(String(50), default="Balanced")  # Budget, Luxury, Family, Backpacker, Relaxed
    interests = Column(JSON, default=list)  # ["Culture", "Food", "Nature", "Shopping"]
    food_preferences = Column(String(255), default="Local Cuisine")
    accommodation_preference = Column(String(100), default="Hotel")
    transportation_preference = Column(String(100), default="Public Transit")
    activity_intensity = Column(String(50), default="Moderate")  # Relaxed, Moderate, Packed
    status = Column(String(50), default="Draft")  # Draft, Planned, InProgress, Completed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trips")
    itineraries = relationship("Itinerary", back_populates="trip", cascade="all, delete-orphan")
    disruptions = relationship("Disruption", back_populates="trip", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="trip", cascade="all, delete-orphan")


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    total_estimated_cost = Column(Float, default=0.0)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="itineraries")
    days = relationship("ItineraryDay", back_populates="itinerary", cascade="all, delete-orphan")


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    date = Column(String(50), nullable=False)
    theme = Column(String(255), nullable=True)
    weather_summary = Column(String(255), nullable=True)

    itinerary = relationship("Itinerary", back_populates="days")
    activities = relationship("Activity", back_populates="day", cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("itinerary_days.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="Attraction")  # Attraction, Restaurant, Transport, Hotel, Relaxation
    location_name = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    start_time = Column(String(20), nullable=False)  # "09:00"
    end_time = Column(String(20), nullable=False)    # "11:30"
    duration_minutes = Column(Integer, default=60)
    estimated_cost = Column(Float, default=0.0)
    opening_hours = Column(String(100), default="09:00 - 18:00")
    travel_time_from_prev_mins = Column(Integer, default=15)
    distance_from_prev_km = Column(Float, default=2.0)
    backup_option = Column(Text, nullable=True)
    is_cancelled = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    day = relationship("ItineraryDay", back_populates="activities")


class Disruption(Base):
    __tablename__ = "disruptions"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    disruption_type = Column(String(100), nullable=False)  # weather, cancellation, schedule_conflict, budget_overflow
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    affected_date = Column(String(50), nullable=True)
    status = Column(String(50), default="active")  # active, resolved
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="disruptions")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="chat_messages")
