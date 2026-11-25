"""Weather & Disruption Risk Agent.

Monitors real-time weather forecasts, evaluates outdoor event vulnerabilities,
detects rain/storm conflicts, and synthesizes high-quality indoor alternatives.
"""

import logging
from typing import Dict, Any, List
from backend.tools.weather_tool import weather_tool
from backend.tools.conflict_detector import conflict_detector
from backend.tools.alternative_finder import alternative_finder

logger = logging.getLogger("travelpilot.weather_risk_agent")

class WeatherRiskAgent:
    def analyze_weather_risks(self, destination: str, days: int = 5) -> Dict[str, Any]:
        """Fetches forecast and summarizes meteorological threats."""
        forecast_res = weather_tool.get_forecast(destination, days=days)
        forecast_list = forecast_res.get("forecast", [])

        has_rain_threat = any(
            any(w in str(d.get("condition", "")).lower() for w in ["rain", "storm", "shower", "thunder"])
            for d in forecast_list
        )

        return {
            "destination": destination,
            "forecast": forecast_list,
            "has_rain_threat": has_rain_threat,
            "provider": forecast_res.get("provider", "Weather Forecast Engine")
        }

    def remediate_schedule_risks(
        self,
        draft_itinerary: List[Dict[str, Any]],
        weather_forecast: List[Dict[str, Any]],
        destination: str
    ) -> Dict[str, Any]:
        """Detects weather conflicts and auto-swaps outdoor activities to indoor backup venues."""
        conflicts = conflict_detector.detect_conflicts(draft_itinerary, weather_forecast)
        remediated_count = 0

        for conf in conflicts:
            if not conf.get("reason"):
                if conf.get("type") == "weather_conflict":
                    conf["reason"] = f"Reason: Expected adverse weather alert ({conf.get('description')}), auto-shifted to indoor cultural spot."
                else:
                    conf["reason"] = f"Reason: Schedule buffer or transit constraint detected for {conf.get('activity_name', 'activity')}."

            # Perform intelligent swap if outdoor conflict
            if conf.get("type") == "weather_conflict":
                day_num = conf.get("day_number")
                act_name = conf.get("activity_name")
                for day in draft_itinerary:
                    if day.get("day_number") == day_num:
                        for act in day.get("activities", []):
                            if act.get("name") == act_name:
                                alt = alternative_finder.find_weather_alternatives(act_name, destination)
                                act["name"] = alt["name"]
                                act["description"] = alt["description"]
                                act["notes"] = f"Weather Shield: Shifted from outdoor venue due to expected rain ({conf.get('description')})."
                                act["backup_option"] = f"Original outdoor activity: {act_name}"
                                remediated_count += 1

        return {
            "conflicts": conflicts,
            "remediated_count": remediated_count,
            "is_conflict_free": len(conflicts) == 0 or remediated_count > 0
        }

weather_risk_agent = WeatherRiskAgent()
