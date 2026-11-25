from typing import Dict, Any, List

class BudgetTool:
    def calculate_allocation(self, total_budget: float, travel_style: str = "Balanced") -> Dict[str, float]:
        """Divide budget into functional spending categories based on travel style."""
        style = travel_style.lower()

        if "luxury" in style:
            ratios = {"accommodation": 0.45, "dining": 0.25, "activities": 0.15, "transportation": 0.10, "miscellaneous": 0.05}
        elif "budget" in style or "backpacker" in style:
            ratios = {"accommodation": 0.30, "dining": 0.25, "activities": 0.25, "transportation": 0.15, "miscellaneous": 0.05}
        else:  # Balanced / Moderate
            ratios = {"accommodation": 0.35, "dining": 0.25, "activities": 0.20, "transportation": 0.15, "miscellaneous": 0.05}

        return {cat: round(total_budget * pct, 2) for cat, pct in ratios.items()}

    def evaluate_itinerary_budget(self, total_budget: float, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sum costs and verify compliance with budget limit."""
        activities_cost = sum(act.get("estimated_cost", 0.0) for act in activities if act.get("category") != "Restaurant" and act.get("category") != "Hotel")
        dining_cost = sum(act.get("estimated_cost", 0.0) for act in activities if act.get("category") == "Restaurant")
        hotel_cost = sum(act.get("estimated_cost", 0.0) for act in activities if act.get("category") == "Hotel")
        transport_cost = sum(act.get("estimated_cost", 0.0) for act in activities if act.get("category") == "Transport")

        # Estimate missing transport if 0
        if transport_cost == 0:
            transport_cost = len(activities) * 8.0

        estimated_total = round(activities_cost + dining_cost + hotel_cost + transport_cost, 2)
        remaining = round(total_budget - estimated_total, 2)
        is_overflow = estimated_total > total_budget

        allocations = self.calculate_allocation(total_budget)

        return {
            "total_budget": total_budget,
            "estimated_total_cost": estimated_total,
            "remaining_budget": remaining,
            "is_overflow": is_overflow,
            "overflow_amount": abs(remaining) if is_overflow else 0.0,
            "breakdown": {
                "accommodation": hotel_cost or allocations["accommodation"],
                "dining": dining_cost or allocations["dining"],
                "transportation": transport_cost or allocations["transportation"],
                "activities": activities_cost or allocations["activities"],
                "miscellaneous": allocations["miscellaneous"],
            },
            "category_percentages": {
                "accommodation": round(((hotel_cost or allocations["accommodation"]) / total_budget) * 100, 1),
                "dining": round(((dining_cost or allocations["dining"]) / total_budget) * 100, 1),
                "transportation": round(((transport_cost or allocations["transportation"]) / total_budget) * 100, 1),
                "activities": round(((activities_cost or allocations["activities"]) / total_budget) * 100, 1),
                "miscellaneous": 5.0,
            }
        }

budget_tool = BudgetTool()
