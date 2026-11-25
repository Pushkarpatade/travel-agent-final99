from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.models import User, Trip, ChatMessage
from backend.schemas.schemas import ChatRequest, ChatResponse, ItineraryOut
from backend.services.auth_service import get_current_user
from backend.agents.chat_agent import chat_agent

router = APIRouter(prefix="/chat", tags=["AI Chat Assistant"])

@router.post("", response_model=ChatResponse)
def send_chat_message(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == req.trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    # Save user message
    user_msg = ChatMessage(
        trip_id=trip.id,
        user_id=current_user.id,
        role="user",
        content=req.message
    )
    db.add(user_msg)
    db.commit()

    # Process message with ChatAgent
    reply_text, suggestions, updated_itinerary = chat_agent.process_chat(db, trip, req.message)

    # Save assistant message
    asst_msg = ChatMessage(
        trip_id=trip.id,
        user_id=current_user.id,
        role="assistant",
        content=reply_text
    )
    db.add(asst_msg)
    db.commit()

    return ChatResponse(
        reply=reply_text,
        suggested_actions=suggestions,
        updated_itinerary=ItineraryOut.model_validate(updated_itinerary) if updated_itinerary else None
    )
