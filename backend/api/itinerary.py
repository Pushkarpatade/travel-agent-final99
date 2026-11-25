from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.models import User, Trip, Itinerary
from backend.schemas.schemas import ItineraryOut
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/trips", tags=["Itinerary"])

@router.get("/{trip_id}/itinerary", response_model=ItineraryOut)
def get_itinerary(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    itinerary = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()
    if not itinerary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active itinerary found for this trip")

    return itinerary


@router.put("/{trip_id}/itinerary", response_model=ItineraryOut)
def update_itinerary(
    trip_id: int,
    itinerary_in: ItineraryOut,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    itinerary = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()
    if not itinerary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active itinerary found")

    itinerary.summary = itinerary_in.summary
    itinerary.total_estimated_cost = itinerary_in.total_estimated_cost
    db.commit()
    db.refresh(itinerary)
    return itinerary
