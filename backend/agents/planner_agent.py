import logging
from sqlalchemy.orm import Session
from backend.models.models import Trip, Itinerary, ItineraryDay, Activity, Disruption
from backend.graph.planning_graph import planning_graph_app
from backend.agents.supervisor_agent import supervisor_agent
from backend.graph.state import PlannerState

logger = logging.getLogger("travelpilot.planner_agent")

class PlannerAgent:
    def plan_trip(self, db: Session, trip: Trip) -> Itinerary:
        """Run Multi-Agent planning pipeline for a trip and save generated itinerary to database."""
        logger.info(f"Starting Multi-Agent planning pipeline for Trip ID {trip.id} ({trip.destination})")

        # Initial state setup
        initial_state: PlannerState = {
            "trip_id": trip.id,
            "destination": trip.destination,
            "start_date": trip.start_date,
            "end_date": trip.end_date,
            "budget": trip.budget,
            "currency": trip.currency or "INR",
            "travelers": trip.travelers or 1,
            "travel_style": trip.travel_style or "Balanced",
            "interests": trip.interests or ["Culture", "Food"],
            "food_preferences": trip.food_preferences or "Local Cuisine",
            "accommodation_preference": trip.accommodation_preference or "Hotel",
            "transportation_preference": trip.transportation_preference or "Public Transit",
            "activity_intensity": trip.activity_intensity or "Moderate",
            "search_results": [],
            "weather_forecast": [],
            "locations_data": [],
            "calculated_budget": {},
            "draft_itinerary": [],
            "conflicts": [],
            "retry_count": 0,
            "is_valid": False,
            "current_step_status": "Starting AI Agent...",
            "final_itinerary_summary": "",
            "logs": []
        }

        # Execute Multi-Agent Orchestration with native LangSmith tracing & Safety Guardrails
        try:
            final_state = supervisor_agent.execute_multi_agent_pipeline(initial_state)
        except Exception as e:
            logger.warning(f"SupervisorAgent pipeline exception ({e}), falling back to planning_graph_app.")
            final_state = planning_graph_app.invoke(initial_state)

        # Deactivate previous active itineraries for this trip
        db.query(Itinerary).filter(Itinerary.trip_id == trip.id).update({"is_active": False})

        # Calculate total cost
        total_cost = 0.0
        for d_data in final_state.get("draft_itinerary", []):
            for a_data in d_data.get("activities", []):
                total_cost += a_data.get("estimated_cost", 0.0)

        # Create new Itinerary record
        itinerary = Itinerary(
            trip_id=trip.id,
            version=1,
            is_active=True,
            total_estimated_cost=round(total_cost, 2),
            summary=final_state.get("final_itinerary_summary", f"AI Generated Itinerary for {trip.destination}")
        )
        db.add(itinerary)
        db.flush()

        # Add Days & Activities
        for d_data in final_state.get("draft_itinerary", []):
            day_record = ItineraryDay(
                itinerary_id=itinerary.id,
                day_number=d_data.get("day_number", 1),
                date=d_data.get("date", trip.start_date),
                theme=d_data.get("theme", "Exploration"),
                weather_summary=d_data.get("weather_summary", "Clear")
            )
            db.add(day_record)
            db.flush()

            for a_data in d_data.get("activities", []):
                act_record = Activity(
                    day_id=day_record.id,
                    name=a_data.get("name", "Activity"),
                    description=a_data.get("description", ""),
                    category=a_data.get("category", "Attraction"),
                    location_name=a_data.get("location_name", trip.destination),
                    latitude=a_data.get("latitude"),
                    longitude=a_data.get("longitude"),
                    start_time=a_data.get("start_time", "09:00"),
                    end_time=a_data.get("end_time", "10:00"),
                    duration_minutes=a_data.get("duration_minutes", 60),
                    estimated_cost=a_data.get("estimated_cost", 0.0),
                    opening_hours=a_data.get("opening_hours", "09:00 - 18:00"),
                    travel_time_from_prev_mins=a_data.get("travel_time_from_prev_mins", 15),
                    distance_from_prev_km=a_data.get("distance_from_prev_km", 1.5),
                    backup_option=a_data.get("backup_option", None),
                    notes=a_data.get("notes", None)
                )
                db.add(act_record)

        # Save any remaining conflicts as Disruption records for the user dashboard
        for conf in final_state.get("conflicts", []):
            reason_str = conf.get("reason") or f"Reason: Detected {conf.get('type', 'conflict')} affecting schedule."
            disruption = Disruption(
                trip_id=trip.id,
                disruption_type=conf.get("type", "conflict"),
                title=f"{conf.get('type', 'Conflict').title()} on Day {conf.get('day_number')}",
                description=f"{conf.get('description', 'Disruption detected')}. {reason_str}",
                affected_date=conf.get("date"),
                status="active"
            )
            db.add(disruption)

        trip.status = "Planned"
        db.commit()
        db.refresh(itinerary)
        return itinerary

planner_agent = PlannerAgent()
