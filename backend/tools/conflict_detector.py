import logging
from typing import List, Dict, Any

logger = logging.getLogger("travelpilot.conflict_detector")

class ConflictDetector:
    def detect_conflicts(
        self, days_data: List[Dict[str, Any]], weather_forecast: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Scan itinerary days for schedule overlaps, rain vs outdoor activity issues, and opening hours mismatches."""
        conflicts = []

        weather_by_date = {w.get("date"): w for w in weather_forecast}

        for day in days_data:
            day_num = day.get("day_number", 1)
            date_str = day.get("date", "")
            activities = day.get("activities", [])
            w_info = weather_by_date.get(date_str, {})
            rain_prob = w_info.get("rain_probability_pct", 0)

            # Sort activities by start_time
            sorted_acts = sorted(activities, key=lambda a: a.get("start_time", "00:00"))

            for i in range(len(sorted_acts)):
                act = sorted_acts[i]
                start_mins = self._time_to_minutes(act.get("start_time", "09:00"))
                end_mins = self._time_to_minutes(act.get("end_time", "10:00"))

                # 1. Check overlap with previous activity
                if i > 0:
                    prev_act = sorted_acts[i - 1]
                    prev_end = self._time_to_minutes(prev_act.get("end_time", "09:00"))
                    travel_time = act.get("travel_time_from_prev_mins", 15)

                    if start_mins < (prev_end + travel_time):
                        conflicts.append({
                            "type": "schedule_conflict",
                            "severity": "high",
                            "day_number": day_num,
                            "date": date_str,
                            "activity_name": act.get("name"),
                            "description": f"Conflict on Day {day_num}: '{act.get('name')}' starts at {act.get('start_time')}, but previous activity '{prev_act.get('name')}' finishes at {prev_act.get('end_time')} with {travel_time} mins travel time required."
                        })

                # 2. Check weather rain conflict for outdoor activities
                if rain_prob > 50:
                    cat = act.get("category", "").lower()
                    name = act.get("name", "").lower()
                    desc = act.get("description", "").lower()
                    is_outdoor = any(w in name or w in desc for w in ["park", "garden", "walk", "outdoor", "boat", "hike", "beach", "tour"])
                    
                    if is_outdoor:
                        conflicts.append({
                            "type": "weather_conflict",
                            "severity": "medium",
                            "day_number": day_num,
                            "date": date_str,
                            "activity_name": act.get("name"),
                            "description": f"Weather Alert on Day {day_num}: Rain probability is {rain_prob}% ({w_info.get('condition', 'Rain')}). Outdoor activity '{act.get('name')}' is at risk of rain disruption."
                        })

                # 3. Check opening hours conflict
                opening = act.get("opening_hours", "09:00 - 18:00")
                if "24" not in opening and "-" in opening:
                    try:
                        open_str, close_str = [s.strip() for s in opening.split("-")[:2]]
                        open_m = self._time_to_minutes(open_str)
                        close_m = self._time_to_minutes(close_str)
                        if start_mins < open_m or end_mins > close_m:
                            conflicts.append({
                                "type": "opening_hours_conflict",
                                "severity": "medium",
                                "day_number": day_num,
                                "date": date_str,
                                "activity_name": act.get("name"),
                                "description": f"Hours Conflict on Day {day_num}: '{act.get('name')}' is scheduled {act.get('start_time')}-{act.get('end_time')}, but opening hours are {opening}."
                            })
                    except Exception:
                        pass

        return conflicts

    def _time_to_minutes(self, time_str: str) -> int:
        try:
            parts = time_str.strip().split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            return 9 * 60

conflict_detector = ConflictDetector()
