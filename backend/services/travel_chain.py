import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from backend.config import settings

logger = logging.getLogger("travelpilot.travel_chain")

# 1. Define the exact JSON structure for UI consumption
class TravelAgentResponse(BaseModel):
    destination: str = Field(description="The active destination city, e.g., Mumbai")
    category: str = Field(description="Type of data being returned: 'accommodation', 'transportation', or 'cuisine'")
    title: str = Field(description="Name of the hotel, PG, or transit route")
    location_area: str = Field(description="Specific neighborhood or street in the city, e.g., Colaba, Bandra")
    estimated_cost: str = Field(description="Estimated price or fare in INR, e.g., ₹2,200/night or ₹50")
    booking_or_map_link: str = Field(description="A valid Google Maps or booking deep link using the location name")
    reason_or_details: str = Field(description="Short, human-like description explaining why this fits the user's schedule.")

# 2. Setup the LangChain prompt template with strict state enforcement
travel_system_prompt = """
You are "TravelPilot", an elite, autonomous agentic AI travel assistant backend. 
Your job is to dynamically fetch and generate real travel details based on the user's active trip state.

CRITICAL INSTRUCTIONS:
1. ACTIVE TRIP CONTEXT:
   - Current Destination: {active_destination}
   - User Budget: ₹{total_budget}
   - Request Type: {user_request} (e.g., book hotel, find local transit between spots)
   
2. NO HARDCODED FALLBACKS:
   - NEVER return default placeholder locations (such as Hadapsar or Kharadi, Pune) unless the active destination explicitly matches them.
   - If the active destination is "Mumbai", every hotel, stay, or transportation option MUST be strictly located in Mumbai (e.g., Colaba, Dadar, Andheri, Bandra).

3. SEQUENTIAL TRANSIT & FARES:
   - If the user asks for transportation between two spots in the itinerary, calculate the transition logically, provide the realistic mode of transport (e.g., Mumbai Local Train, Metro, or Cab), estimate the fare in INR, and build a Google Maps directions deep link.

4. HUMAN-LIKE INTERACTION:
   - Keep any conversational notes brief, warm, and natural.
   - Always output your final answer strictly adhering to the requested JSON schema.

{format_instructions}
"""

def get_ai_travel_data(destination: str, budget: float, user_query: str) -> Optional[Dict[str, Any]]:
    """Execute LangChain Pydantic Structured Output Chain for TravelPilot."""
    api_key = settings.GEMINI_API_KEY
    if not api_key or len(api_key.strip()) < 10:
        logger.warning("GEMINI_API_KEY missing for travel_chain.")
        return None

    parser = JsonOutputParser(pydantic_object=TravelAgentResponse)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", travel_system_prompt),
        ("human", "Fetch the details for my active trip. User input: '{input}'")
    ])

    for m_name in [settings.GEMINI_MODEL, "gemini-3.6-flash", "gemini-1.5-flash"]:
        try:
            llm = ChatGoogleGenerativeAI(
                model=m_name,
                google_api_key=api_key,
                temperature=0.3
            )
            chain = prompt | llm | parser

            result = chain.invoke({
                "active_destination": destination,
                "total_budget": budget,
                "user_request": user_query,
                "input": user_query,
                "format_instructions": parser.get_format_instructions()
            })
            if result:
                logger.info(f"TravelChain successfully generated response for {destination} using model {m_name}")
                return result
        except Exception as e:
            logger.warning(f"TravelChain execution failed with model {m_name}: {e}")

    return None
