from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.models import User, Trip
from backend.schemas.schemas import ItineraryOut
from backend.services.auth_service import get_current_user
from backend.agents.planner_agent import planner_agent
from backend.services.job_worker import job_worker, JobStatusResponse

router = APIRouter(prefix="/trips", tags=["AI Planning"])

@router.post("/{trip_id}/plan-async", response_model=JobStatusResponse)
def generate_plan_async(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enqueues async AI planning job with state tracking (queued -> running -> completed)."""
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    job_id = job_worker.enqueue_planning_job(trip.id)
    job_status = job_worker.get_job_status(job_id)
    return job_status

@router.get("/{trip_id}/jobs/{job_id}", response_model=JobStatusResponse)
def get_planning_job_status(
    trip_id: int,
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Poll job status and intermediate progress without timeout."""
    status_data = job_worker.get_job_status(job_id)
    if not status_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return status_data

@router.post("/{trip_id}/plan", response_model=ItineraryOut)
def generate_plan(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    itinerary = planner_agent.plan_trip(db, trip)
    return itinerary


@router.post("/{trip_id}/replan", response_model=ItineraryOut)
def replan_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    itinerary = planner_agent.plan_trip(db, trip)
    return itinerary
