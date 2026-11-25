from typing import List, Dict, Any

class AlternativeFinder:
    def find_weather_alternatives(self, activity_name: str, destination: str) -> Dict[str, Any]:
        """Find covered indoor alternatives for a rained-out activity."""
        dest_lower = destination.lower()
        if "paris" in dest_lower:
            return {
                "name": "Musée d'Orsay & Covered Passage Walk",
                "description": "Explore impressionist masterpieces inside a renovated Beaux-Arts railway station, followed by shopping in historic glass-roofed arcades.",
                "category": "Attraction",
                "opening_hours": "09:30 - 18:00",
                "estimated_cost": 16.0,
                "notes": "Indoor rain alternative"
            }
        elif "tokyo" in dest_lower:
            return {
                "name": "Mori Building Digital Art Museum (teamLab)",
                "description": "Immersive 3D digital art exhibition entirely indoors, protected from all weather conditions.",
                "category": "Attraction",
                "opening_hours": "10:00 - 20:00",
                "estimated_cost": 32.0,
                "notes": "Indoor rain alternative"
            }
        else:
            return {
                "name": f"National Museum & Art Gallery of {destination}",
                "description": "Explore regional art collections, historical archives, and interactive exhibitions in a fully climate-controlled venue.",
                "category": "Attraction",
                "opening_hours": "10:00 - 18:00",
                "estimated_cost": 15.0,
                "notes": "Indoor rain alternative"
            }

    def find_budget_alternatives(self, activity_name: str, current_cost: float) -> Dict[str, Any]:
        """Suggest free or low-cost replacement activity."""
        return {
            "name": f"Self-Guided Historic Walking & Photo Tour",
            "description": "Discover architectural highlights, public sculptures, and vibrant local squares without entry fees.",
            "category": "Attraction",
            "opening_hours": "24/7 Open",
            "estimated_cost": 0.0,
            "notes": "Zero-cost budget alternative"
        }

alternative_finder = AlternativeFinder()
