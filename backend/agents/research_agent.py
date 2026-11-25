"""Research & Attraction Specialist Agent.

Armed with live Tavily Web Search and Google Maps Geocoding.
Discovers verified landmarks, authentic dining, admission fees, and opening hours.
"""

import logging
from typing import Dict, Any, List
from backend.tools.tavily_tool import tavily_tool
from backend.tools.maps_tool import maps_tool

logger = logging.getLogger("travelpilot.research_agent")

class ResearchAgent:
    def research_destination(self, destination: str, interests: List[str], food_pref: str) -> Dict[str, Any]:
        """Conducts comprehensive web research for a destination."""
        logger.info(f"ResearchAgent searching attractions and dining for {destination}")
        interests_str = ", ".join(interests) if interests else "top attractions and landmarks"

        # 1. Search destination travel overview
        overview_query = f"top places to visit travel guide {destination}"
        overview_results = tavily_tool.search(overview_query, max_results=3)

        # 2. Search activities matching user interests
        activities_query = f"best things to do in {destination} for {interests_str} with ticket price opening hours"
        activity_results = tavily_tool.search(activities_query, max_results=3)

        # 3. Search authentic dining spots
        dining_query = f"best restaurants and local food in {destination} {food_pref}"
        dining_results = tavily_tool.search(dining_query, max_results=3)

        # 4. Geocode destination center
        loc_data = maps_tool.search_place(destination)

        combined_results = overview_results + activity_results + dining_results

        return {
            "destination": destination,
            "search_snippets": combined_results,
            "center_coordinates": {
                "latitude": loc_data.get("latitude", 18.5204),
                "longitude": loc_data.get("longitude", 73.8567)
            },
            "researched_count": len(combined_results)
        }

research_agent = ResearchAgent()
