from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.models import User, Trip, Disruption, Itinerary
from backend.schemas.schemas import DisruptionOut, HandleDisruptionRequest, HandleDisruptionResponse, ItineraryOut
from backend.services.auth_service import get_current_user
from backend.agents.planner_agent import planner_agent

router = APIRouter(prefix="/trips", tags=["Disruptions"])

@router.get("/{trip_id}/disruptions", response_model=List[DisruptionOut])
def get_disruptions(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    disruptions = db.query(Disruption).filter(Disruption.trip_id == trip_id).all()
    return disruptions


@router.post("/{trip_id}/handle-disruption", response_model=HandleDisruptionResponse)
def handle_disruption(
    trip_id: int,
    req: HandleDisruptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    disruption = db.query(Disruption).filter(Disruption.id == req.disruption_id, Disruption.trip_id == trip_id).first()
    if not disruption:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disruption not found")

    if req.action == "auto_replan":
        itinerary = planner_agent.plan_trip(db, trip)
        disruption.status = "resolved"
        disruption.resolution_notes = "Auto-replanned by AI Agent"
        db.commit()
        return HandleDisruptionResponse(
            success=True,
            message="Disruption successfully resolved! Itinerary re-planned.",
            updated_itinerary=ItineraryOut.model_validate(itinerary)
        )
    elif req.action == "ignore":
        disruption.status = "resolved"
        disruption.resolution_notes = "Ignored by user"
        db.commit()
        return HandleDisruptionResponse(
            success=True,
            message="Disruption marked as ignored."
        )

    return HandleDisruptionResponse(success=False, message="Unknown action requested")
