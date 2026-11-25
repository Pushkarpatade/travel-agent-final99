import logging
import math
import requests
from typing import Dict, Any, List, Optional, Tuple
from backend.config import settings

logger = logging.getLogger("travelpilot.maps_tool")

class MapsTool:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY

    def search_place(self, query: str, location_name: Optional[str] = None) -> Dict[str, Any]:
        """Find details and lat/lng for a place."""
        if self.api_key and self.api_key.strip():
            try:
                url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={query}&inputtype=textquery&fields=name,formatted_address,geometry,opening_hours,rating&key={self.api_key}"
                res = requests.get(url, timeout=5)
                if res.status_code == 200 and res.json().get("candidates"):
                    candidate = res.json()["candidates"][0]
                    loc = candidate.get("geometry", {}).get("location", {})
                    return {
                        "name": candidate.get("name", query),
                        "address": candidate.get("formatted_address", ""),
                        "latitude": loc.get("lat", 0.0),
                        "longitude": loc.get("lng", 0.0),
                        "rating": candidate.get("rating", 4.5),
                        "source": "google_places"
                    }
            except Exception as e:
                logger.warning(f"Google Places search error: {e}")

        # Fallback coordinate generator based on string hash
        hash_val = sum(ord(c) for c in query)
        lat = 48.8566 + (hash_val % 100) * 0.001  # Centered around Paris demo area
        lng = 2.3522 + ((hash_val * 3) % 100) * 0.001

        return {
            "name": query,
            "address": f"Central District, {location_name or 'City Center'}",
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "rating": 4.6,
            "source": "simulated"
        }

    def calculate_distance_and_time(
        self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float
    ) -> Tuple[float, int]:
        """Calculate distance in km and travel time in minutes between two lat/lng pairs."""
        if self.api_key and self.api_key.strip():
            try:
                url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin_lat},{origin_lng}&destinations={dest_lat},{dest_lng}&mode=transit&key={self.api_key}"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    element = res.json()["rows"][0]["elements"][0]
                    dist_km = element.get("distance", {}).get("value", 2000) / 1000.0
                    time_min = int(element.get("duration", {}).get("value", 900) / 60.0)
                    return round(dist_km, 2), max(5, time_min)
            except Exception as e:
                logger.warning(f"Google Distance Matrix error: {e}")

        # Haversine distance formula fallback
        R = 6371.0  # Earth radius km
        dlat = math.radians(dest_lat - origin_lat)
        dlng = math.radians(dest_lng - origin_lng)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(origin_lat))
            * math.cos(math.radians(dest_lat))
            * math.sin(dlng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist_km = R * c
        # Assume average urban transit speed ~25 km/h + 5 min walking
        time_min = int((dist_km / 25.0) * 60) + 5
        return round(max(0.5, dist_km), 2), max(5, min(120, time_min))

maps_tool = MapsTool()
