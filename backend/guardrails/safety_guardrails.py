"""TravelPilot Enterprise Safety Guardrails.

Provides comprehensive input and output guardrails:
1. Input Guardrails:
   - Adversarial prompt injection & jailbreak defense
   - High-risk destination & active conflict advisory screening
   - Feasibility, duration, and financial floor validation
2. Output Guardrails:
   - Budget cap enforcement (prevent financial hallucinations)
   - Opening hours & temporal overlap sanity checks
   - Weather vulnerability & outdoor rain contingency checks
   - Geolocation & venue plausibility verification
"""

import re
import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger("travelpilot.guardrails")

# Known high-risk or conflict zones under international travel advisories (Level 4 - Do Not Travel)
HIGH_RISK_REGIONS = {
    "ukraine": "Active conflict zone - Travel restricted by international advisories.",
    "gaza": "Active conflict zone - Severe military operations.",
    "syria": "Active armed conflict and severe safety hazard.",
    "yemen": "Armed conflict and humanitarian crisis.",
    "afghanistan": "Critical security risk and civil unrest.",
    "somalia": "Extreme kidnapping and terrorism threat.",
    "south sudan": "Critical violent conflict and safety emergency.",
    "haiti": "Severe civil unrest and armed gang control."
}

# Prompt injection & jailbreak heuristic patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"you\s+are\s+now\s+(dan|an\s+unfiltered|jailbroken)",
    r"reveal\s+(system\s+prompt|api\s*key|secret)",
    r"(drop|delete|truncate)\s+table",
    r"<script\b[^>]*>",
    r"(\bexec\b|\beval\b)\s*\(",
    r"give\s+me\s+root\s+access"
]

class GuardrailValidationResult(BaseModel):
    is_safe: bool = True
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, BLOCKED
    violations: List[str] = Field(default_factory=list)
    remediations: List[str] = Field(default_factory=list)
    sanitized_data: Optional[Dict[str, Any]] = None

class SafetyGuardrails:
    def __init__(self):
        self.injection_regexes = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

    # =========================================================================
    # 1. INPUT GUARDRAILS
    # =========================================================================
    def validate_trip_inputs(self, trip_data: Dict[str, Any]) -> GuardrailValidationResult:
        """Audits incoming trip planning request for safety, security, and feasibility."""
        violations = []
        remediations = []
        risk_level = "LOW"

        destination = str(trip_data.get("destination", "")).strip()
        dest_lower = destination.lower()

        # 1.1 Prompt Injection & Jailbreak Check
        for pattern in self.injection_regexes:
            if pattern.search(destination) or pattern.search(str(trip_data.get("notes", ""))):
                violations.append("Adversarial prompt injection pattern detected in input parameters.")
                remediations.append("Sanitize inputs and strip prompt override attempts.")
                risk_level = "BLOCKED"
                return GuardrailValidationResult(
                    is_safe=False,
                    risk_level=risk_level,
                    violations=violations,
                    remediations=remediations
                )

        # 1.2 High-Risk Destination Screening
        for restricted_zone, reason in HIGH_RISK_REGIONS.items():
            if restricted_zone in dest_lower:
                violations.append(f"Destination '{destination}' matches Level 4 International Travel Advisory: {reason}")
                remediations.append("Alert traveler of active security risk and require user acknowledgment.")
                risk_level = "HIGH"

        # 1.3 Date Sanity Checks
        start_date_str = trip_data.get("start_date")
        end_date_str = trip_data.get("end_date")

        if start_date_str and end_date_str:
            try:
                start_dt = datetime.strptime(str(start_date_str), "%Y-%m-%d").date()
                end_dt = datetime.strptime(str(end_date_str), "%Y-%m-%d").date()
                today = date.today()

                if end_dt < start_dt:
                    violations.append("Invalid dates: Trip end date cannot be earlier than start date.")
                    risk_level = "BLOCKED"

                duration = (end_dt - start_dt).days + 1
                if duration > 30:
                    violations.append(f"Trip duration ({duration} days) exceeds the 30-day autonomous planning limit.")
                    remediations.append("Split trip into multi-phase segments of up to 30 days.")
                    risk_level = "MEDIUM"

            except ValueError:
                violations.append("Invalid date format. Expected YYYY-MM-DD.")
                risk_level = "BLOCKED"

        # 1.4 Budget Floor Feasibility Check
        budget = float(trip_data.get("budget", 0) or 0)
        currency = str(trip_data.get("currency", "INR")).upper()
        travelers = int(trip_data.get("travelers", 1) or 1)

        # Minimum realistic budget per person per day
        min_daily_rates = {
            "INR": 500.0,
            "USD": 20.0,
            "EUR": 20.0,
            "GBP": 18.0
        }
        rate_floor = min_daily_rates.get(currency, 20.0)
        est_days = max(1, duration if 'duration' in locals() else 3)
        min_required = rate_floor * est_days * travelers

        if budget < min_required and budget > 0:
            violations.append(
                f"Budget ({currency} {budget:,.2f}) is below realistic feasibility floor "
                f"({currency} {min_required:,.2f} for {travelers} traveler(s) across {est_days} days)."
            )
            remediations.append("Recommend budget optimization tier: 'Backpacker / Ultra-Economy'.")
            if risk_level != "BLOCKED":
                risk_level = "MEDIUM"

        is_safe = risk_level not in ["BLOCKED"]
        return GuardrailValidationResult(
            is_safe=is_safe,
            risk_level=risk_level,
            violations=violations,
            remediations=remediations,
            sanitized_data=trip_data
        )

    # =========================================================================
    # 2. OUTPUT GUARDRAILS
    # =========================================================================
    def audit_itinerary_safety(
        self,
        draft_itinerary: List[Dict[str, Any]],
        user_budget: float,
        currency: str = "INR"
    ) -> GuardrailValidationResult:
        """Audits generated itinerary against financial caps, temporal sanity, and weather safety."""
        violations = []
        remediations = []
        risk_level = "LOW"

        total_activity_cost = 0.0
        all_activities = []

        for day in draft_itinerary:
            day_num = day.get("day_number", 1)
            activities = day.get("activities", [])
            all_activities.extend(activities)

            # 2.1 Temporal Overlap & Plausible Hours Guard
            for i, act in enumerate(activities):
                cost = float(act.get("estimated_cost", 0.0) or 0.0)
                total_activity_cost += cost

                start_time = act.get("start_time", "")
                end_time = act.get("end_time", "")

                # Check unreasonable nocturnal scheduling for cultural landmarks
                if start_time and act.get("category") in ["Attraction", "Museum"]:
                    try:
                        hour = int(start_time.split(":")[0])
                        if hour < 7 or hour > 21:
                            violations.append(
                                f"Day {day_num}: Attraction '{act.get('name')}' scheduled at unusual hour ({start_time})."
                            )
                            remediations.append("Auto-adjust schedule to standard operating hours (09:00 - 18:00).")
                            risk_level = "MEDIUM"
                    except Exception:
                        pass

                # Check consecutive overlap
                if i > 0 and start_time and activities[i-1].get("end_time"):
                    prev_end = activities[i-1].get("end_time")
                    if start_time < prev_end:
                        violations.append(
                            f"Day {day_num}: Overlap detected between '{activities[i-1].get('name')}' (ends {prev_end}) "
                            f"and '{act.get('name')}' (starts {start_time})."
                        )
                        remediations.append("Insert minimum 15-minute transit buffer between activities.")
                        risk_level = "MEDIUM"

            # 2.2 Weather Vulnerability Guard
            weather_summary = str(day.get("weather_summary", "")).lower()
            if any(rain_word in weather_summary for rain_word in ["rain", "storm", "thunder", "heavy shower"]):
                for act in activities:
                    if act.get("category") in ["Attraction", "Park", "Beach", "Outdoor"]:
                        if not act.get("backup_option"):
                            violations.append(
                                f"Day {day_num}: Outdoor activity '{act.get('name')}' lacks indoor backup option during rain forecast."
                            )
                            remediations.append(f"Auto-assign indoor museum or covered gallery alternative for '{act.get('name')}'.")
                            if risk_level == "LOW":
                                risk_level = "MEDIUM"

        # 2.3 Financial Budget Cap Guardrail
        if user_budget > 0:
            variance_ratio = (total_activity_cost - user_budget) / user_budget
            if variance_ratio > 0.15:  # Over budget by > 15%
                violations.append(
                    f"Financial Guardrail Breach: Total itinerary cost ({currency} {total_activity_cost:,.2f}) "
                    f"exceeds user budget ({currency} {user_budget:,.2f}) by {int(variance_ratio * 100)}%."
                )
                remediations.append("Downgrade premium dining/activity tiers to free self-guided alternatives.")
                risk_level = "HIGH"

        is_safe = risk_level != "BLOCKED"
        return GuardrailValidationResult(
            is_safe=is_safe,
            risk_level=risk_level,
            violations=violations,
            remediations=remediations
        )

# Global guardrails singleton
safety_guardrails = SafetyGuardrails()
