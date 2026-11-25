"""Budget & Financial Optimization Agent.

Analyzes trip expenditure tiers, calculates optimal allocations across
stay, dining, sightseeing, and contingency, and enforces strict financial guardrails.
"""

import logging
from typing import Dict, Any, List
from backend.tools.budget_tool import budget_tool

logger = logging.getLogger("travelpilot.budget_optimizer_agent")

class BudgetOptimizerAgent:
    def optimize_budget(self, total_budget: float, travel_style: str = "Balanced", currency: str = "INR") -> Dict[str, Any]:
        """Calculates itemized budget allocation across categories."""
        allocation = budget_tool.calculate_allocation(total_budget, travel_style)
        return {
            "total_budget": total_budget,
            "currency": currency,
            "travel_style": travel_style,
            "category_breakdown": allocation,
            "daily_target": round(total_budget / 4, 2)  # default estimate
        }

    def calibrate_activity_costs(
        self,
        draft_itinerary: List[Dict[str, Any]],
        total_budget: float,
        currency: str = "INR"
    ) -> Dict[str, Any]:
        """Calculates total activity expenditure and checks if downscaling is required."""
        total_cost = 0.0
        for day in draft_itinerary:
            for act in day.get("activities", []):
                total_cost += float(act.get("estimated_cost", 0.0) or 0.0)

        total_cost = round(total_cost, 2)
        within_budget = total_budget <= 0 or total_cost <= total_budget * 1.15

        savings_recommendation = None
        if not within_budget:
            excess = round(total_cost - total_budget, 2)
            savings_recommendation = (
                f"Expenditure ({currency} {total_cost:,.2f}) exceeds target budget ({currency} {total_budget:,.2f}) "
                f"by {currency} {excess:,.2f}. Swap high-ticket dinners with authentic street bistros."
            )

        return {
            "total_estimated_cost": total_cost,
            "within_budget": within_budget,
            "savings_recommendation": savings_recommendation
        }

budget_optimizer_agent = BudgetOptimizerAgent()
