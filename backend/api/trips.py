from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.models import User, Trip
from backend.schemas.schemas import TripCreate, TripUpdate, TripOut
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(
    trip_in: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = Trip(
        user_id=current_user.id,
        destination=trip_in.destination,
        start_date=trip_in.start_date,
        end_date=trip_in.end_date,
        budget=trip_in.budget,
        currency=trip_in.currency,
        travelers=trip_in.travelers,
        travel_style=trip_in.travel_style,
        interests=trip_in.interests,
        food_preferences=trip_in.food_preferences,
        accommodation_preference=trip_in.accommodation_preference,
        transportation_preference=trip_in.transportation_preference,
        activity_intensity=trip_in.activity_intensity,
        status="Draft"
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("", response_model=List[TripOut])
def list_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trips = db.query(Trip).filter(Trip.user_id == current_user.id).all()
    return trips


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@router.put("/{trip_id}", response_model=TripOut)
def update_trip(
    trip_id: int,
    trip_in: TripUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    for field, val in trip_in.model_dump(exclude_unset=True).items():
        setattr(trip, field, val)

    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    db.delete(trip)
    db.commit()
    return None
