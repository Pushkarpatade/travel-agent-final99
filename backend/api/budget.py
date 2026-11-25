from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.models import User, Trip, Itinerary
from backend.schemas.schemas import BudgetBreakdown
from backend.services.auth_service import get_current_user
from backend.tools.budget_tool import budget_tool

router = APIRouter(prefix="/trips", tags=["Budget"])

@router.get("/{trip_id}/budget", response_model=BudgetBreakdown)
def get_trip_budget(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    itinerary = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()

    activities_data = []
    if itinerary:
        for day in itinerary.days:
            for act in day.activities:
                activities_data.append({
                    "name": act.name,
                    "category": act.category,
                    "estimated_cost": act.estimated_cost
                })

    res = budget_tool.evaluate_itinerary_budget(trip.budget, activities_data)

    return BudgetBreakdown(
        total_budget=trip.budget,
        currency=trip.currency or "USD",
        estimated_total_cost=res["estimated_total_cost"],
        remaining_budget=res["remaining_budget"],
        accommodation=res["breakdown"]["accommodation"],
        dining=res["breakdown"]["dining"],
        transportation=res["breakdown"]["transportation"],
        activities=res["breakdown"]["activities"],
        miscellaneous=res["breakdown"]["miscellaneous"],
        category_percentages=res["category_percentages"]
    )
