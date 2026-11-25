"""Quality & Guardrail Auditor Agent.

Runs strict input and output validations:
- Adversarial prompt injection defense
- International travel advisory checks
- Opening hours & temporal overlap verification
- Financial budget cap compliance
"""

import logging
from typing import Dict, Any, List
from backend.guardrails.safety_guardrails import safety_guardrails, GuardrailValidationResult

logger = logging.getLogger("travelpilot.auditor_agent")

class AuditorAgent:
    def audit_inputs(self, trip_data: Dict[str, Any]) -> GuardrailValidationResult:
        """Executes input guardrails before workflow begins."""
        logger.info(f"AuditorAgent auditing inputs for destination '{trip_data.get('destination')}'")
        return safety_guardrails.validate_trip_inputs(trip_data)

    def audit_itinerary(
        self,
        draft_itinerary: List[Dict[str, Any]],
        budget: float,
        currency: str = "INR"
    ) -> GuardrailValidationResult:
        """Executes output guardrails on the final assembled plan."""
        logger.info(f"AuditorAgent auditing assembled itinerary against {currency} {budget} budget")
        return safety_guardrails.audit_itinerary_safety(draft_itinerary, budget, currency)

auditor_agent = AuditorAgent()
