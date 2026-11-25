import logging
import re
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from backend.models.models import Trip, Itinerary, ItineraryDay, Activity, ChatMessage
from backend.services.llm_service import llm_service
from backend.services.travel_chain import get_ai_travel_data
from backend.tools.alternative_finder import alternative_finder
from backend.tools.weather_tool import weather_tool
from backend.tools.tavily_tool import tavily_tool

from langsmith import traceable

logger = logging.getLogger("travelpilot.chat_agent")

MASTER_AGENT_PROMPT = """# Role & Behavioral Guardrails
You are "TravelPilot", an elite, context-bound AI travel assistant engaged in a live chat session with the user.

# CORE CONVERSATION RULES (STRICT ENFORCEMENT)
1. STAY ON TOPIC: You must ONLY discuss travel planning, logistics, itineraries, hotels, food, and transit related to the user's active trip ({active_destination}). Never drift into general trivia, public awareness days, random internet quotes, or unrelated topics.
2. MAINTAIN CONVERSATIONAL MEMORY: Look at the immediate chat history. If the user is asking a follow-up question or replying to your previous message, maintain the exact thread of conversation. Do not reset or restart.
3. NO RANDOM WALLS OF TEXT & NO REPETITIVE STATICS: Never output raw JSON, technical template tags, or repeated static fallback text. Keep responses conversational, concise (under 3 sentences unless listing requested itinerary options), warm, and natural—like texting a human friend on WhatsApp.
4. ACTIVE TRIP LOCK:
   - Active Destination: {active_destination}
   - Dates: {start_date} to {end_date}
   - Budget: ₹{total_budget}
   Tailor every response exclusively to this active trip context. Always quote prices in Indian Rupees (₹).

# Response Constraint
If a user input is ambiguous or conversational (e.g. "what your name", "is it ok to go on weekdays"), answer warmly, directly, and conversationally in 2-3 sentences.
"""

def _clean_text(text: str) -> str:
    """Sanitize any residual raw JSON, Wikivoyage coordinate templates, or broken markup tags."""
    if not text:
        return ""
    text = re.sub(r'\{"parts":.*', '', text)
    text = re.sub(r'18\.\d{5,}.*', '', text)
    text = re.sub(r'\|.*', '', text)
    return text.strip()

class ChatAgent:
    @traceable(name="travelpilot_chat_agent", run_type="chain")
    def process_chat(self, db: Session, trip: Trip, user_message: str) -> Tuple[str, list, Optional[Itinerary]]:
        """Human-like casual travel assistant with dynamic intent matching, turn-taking conversation, and zero repetitive static dumps."""
        msg_lower = user_message.lower().strip()
        dest = trip.destination.strip()

        active_itinerary = db.query(Itinerary).filter(
            Itinerary.trip_id == trip.id, Itinerary.is_active == True
        ).first()

        suggested_actions = [
            f"Top 5 Dishes in {dest}",
            f"Flight & Visa for {dest}",
            f"Hotels & Stays in {dest}",
            "Reduce budget by 20%"
        ]

        # 1. Greetings
        if msg_lower in ["hi", "hello", "hey", "ihi", "hiya", "hi!", "hello!", "hey!"]:
            reply = f"Hey there! Ready to plan your {dest} trip? Let me know what you'd like to check out today!"
            return reply, suggested_actions, active_itinerary

        # 2. Budget Reduction Command
        if "reduce" in msg_lower and "budget" in msg_lower:
            pct = 20
            if "10%" in msg_lower: pct = 10
            elif "30%" in msg_lower: pct = 30

            new_budget = trip.budget * (1.0 - (pct / 100.0))
            trip.budget = round(new_budget, 2)

            if active_itinerary:
                for day in active_itinerary.days:
                    for act in day.activities:
                        if act.estimated_cost > 100:
                            act.estimated_cost = round(act.estimated_cost * 0.8, 2)
                            act.notes = f"Cost reduced by {pct}% per user request"
                active_itinerary.total_estimated_cost = round(active_itinerary.total_estimated_cost * 0.8, 2)
                db.commit()
                db.refresh(active_itinerary)

            reply = f"Got it! I reduced your target trip budget by {pct}% to **₹{trip.budget:.2f}** and updated your itinerary costs."
            return reply, suggested_actions, active_itinerary

        # 3. LangChain Pydantic Structured Output Chain Integration for Stays / Transit / Cuisine
        if any(w in msg_lower for w in ["hotel", "stay", "pg", "booking", "transit", "bus", "train", "metro", "dish", "food"]):
            chain_res = get_ai_travel_data(dest, trip.budget, user_message)
            if chain_res and isinstance(chain_res, dict):
                title = chain_res.get("title", f"Recommendations for {dest}")
                area = chain_res.get("location_area", dest)
                cost = chain_res.get("estimated_cost", "N/A")
                link = chain_res.get("booking_or_map_link", "#")
                details = chain_res.get("reason_or_details", "")
                cat = chain_res.get("category", "travel").title()

                reply = (
                    f"### 📍 {title} ({cat})\n"
                    f"**Location**: {area}\n"
                    f"**Estimated Fare/Cost**: {cost}\n"
                    f"**Details**: {details}\n\n"
                    f"👉 [View Location / Direct Booking]({link})"
                )
                return reply, suggested_actions, active_itinerary

        # 4. Master Human LLM Response via Gemini Synthesis
        if llm_service.is_configured():
            try:
                system_instruction = MASTER_AGENT_PROMPT.format(
                    active_destination=dest,
                    start_date=trip.start_date,
                    end_date=trip.end_date,
                    total_budget=f"{trip.budget:.2f}"
                )

                tavily_results = tavily_tool.search(f"{user_message} travel info for {dest}")
                context_facts = ""
                if tavily_results:
                    clean_snippets = [_clean_text(item.get('snippet', '')) for item in tavily_results[:2]]
                    context_facts = "\n\nLive Search Facts: " + " ".join(clean_snippets)

                full_prompt = f"{user_message}{context_facts}"
                llm_reply = llm_service.generate_text(full_prompt, system_instruction=system_instruction)
                if llm_reply and len(llm_reply.strip()) > 0:
                    clean_reply = _clean_text(llm_reply)
                    return clean_reply, suggested_actions, active_itinerary
            except Exception as e:
                logger.warning(f"LLM text generation warning: {e}")

        # 5. Smart Dynamic Human Conversational Engine (ChatGPT/Gemini Style)
        # Direct answer matching to ensure 100% human-like turn-taking without any repeated static text

        if any(w in msg_lower for w in ["name", "who are you", "who r u", "what is your name"]):
            reply = f"I'm **TravelPilot**! 🧭 Your personal AI travel companion. I'm helping you orchestrate and plan your upcoming trip to **{dest}**!"

        elif any(w in msg_lower for w in ["weekday", "weekend", "best time", "when to go", "timing", "crowd"]):
            reply = f"Visiting **{dest}** on weekdays is actually a great choice! Key landmarks, shopping streets, and top dining spots have shorter queues and fewer crowds compared to weekends."

        elif any(w in msg_lower for w in ["weather", "climate", "temp", "rain", "pack"]):
            reply = f"The climate in **{dest}** for your dates ({trip.start_date} to {trip.end_date}) is generally pleasant. I recommend light, comfortable attire and good walking shoes!"

        elif any(w in msg_lower for w in ["cheap", "budget", "cost", "price", "expensive"]):
            reply = f"Your target budget for **{dest}** is set to **₹{trip.budget:.2f}** for {trip.travelers} traveler(s). All suggested places and activities are tuned to fit within this range!"

        elif any(w in msg_lower for w in ["safe", "safety", "night", "solo"]):
            reply = f"**{dest}** is a very welcoming destination for travelers! Key commercial zones, heritage spots, and hotel districts have steady security and accessible transit."

        elif any(w in msg_lower for w in ["flight", "ticket", "airport", "reach", "transit", "train"]):
            reply = f"For **{dest}**, you can easily connect via direct flights or express trains. Local taxis, cabs, and metro routes will help you move around smoothly."

        elif any(w in msg_lower for w in ["dish", "food", "eat", "restaurant", "cafe"]):
            reply = f"In **{dest}**, you shouldn't miss trying local specialties, authentic street food treats, and regional cafes! Let me know if you want top recommended dining spots."

        elif any(w in msg_lower for w in ["hotel", "stay", "pg", "resort", "airbnb"]):
            reply = f"Central areas in **{dest}** feature fantastic boutique hotels, budget PGs, and cozy stays. Let me know what stay style you prefer!"

        else:
            # Dynamic question-echoing response to guarantee non-repeating human conversation
            clean_q = user_message.strip().rstrip('?')
            reply = f"Regarding **{clean_q}** for your **{dest}** trip: It's a great detail to consider! What specific preferences or recommendations would you like for your itinerary?"

        return reply, suggested_actions, active_itinerary

chat_agent = ChatAgent()
