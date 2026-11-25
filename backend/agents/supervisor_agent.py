"""Multi-Agent Supervisor & Orchestrator with Native LangSmith Tracing.

Orchestrates the collaborative agent team:
1. Auditor Agent: Input Guardrail Validation
2. Research Agent: Tavily Search & Geocoding
3. Weather Risk Agent: Forecast & Atmospheric Risk Screening
4. Budget Optimizer Agent: Cost Allocation & Financial Caps
5. Schedule Synthesis Engine: Day-by-Day Slot Generation
6. Weather Risk Agent: Anomaly Detection & Autonomous Re-planning
7. Auditor Agent: Output Guardrail Review & Quality Certification

All pipeline steps are traced to LangSmith with rich execution telemetry.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from langsmith import traceable

from backend.config import settings
from backend.graph.state import PlannerState
from backend.agents.auditor_agent import auditor_agent
from backend.agents.research_agent import research_agent
from backend.agents.weather_risk_agent import weather_risk_agent
from backend.agents.budget_optimizer_agent import budget_optimizer_agent
from backend.graph.planning_graph import _generate_distinct_days

logger = logging.getLogger("travelpilot.supervisor_agent")

class SupervisorAgent:
    @traceable(name="auditor_agent_input_guardrail", run_type="chain")
    def _traceable_input_audit(self, destination: str, start_date: str, end_date: str, budget: float, currency: str, travelers: int):
        return auditor_agent.audit_inputs({
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget,
            "currency": currency,
            "travelers": travelers
        })

    @traceable(name="research_agent_tavily_search", run_type="tool")
    def _traceable_research(self, destination: str, interests: List[str], food_pref: str):
        return research_agent.research_destination(
            destination=destination,
            interests=interests,
            food_pref=food_pref
        )

    @traceable(name="weather_risk_agent_forecast", run_type="tool")
    def _traceable_weather(self, destination: str, days: int):
        return weather_risk_agent.analyze_weather_risks(destination, days=days)

    @traceable(name="budget_optimizer_agent", run_type="chain")
    def _traceable_budget(self, budget: float, travel_style: str, currency: str):
        return budget_optimizer_agent.optimize_budget(
            total_budget=budget,
            travel_style=travel_style,
            currency=currency
        )

    @traceable(name="weather_shield_remediation", run_type="chain")
    def _traceable_remediation(self, draft_itinerary: List[Dict[str, Any]], weather_forecast: List[Dict[str, Any]], destination: str):
        return weather_risk_agent.remediate_schedule_risks(
            draft_itinerary=draft_itinerary,
            weather_forecast=weather_forecast,
            destination=destination
        )

    @traceable(name="auditor_agent_output_guardrail", run_type="chain")
    def _traceable_output_audit(self, draft_itinerary: List[Dict[str, Any]], budget: float, currency: str):
        return auditor_agent.audit_itinerary(
            draft_itinerary=draft_itinerary,
            budget=budget,
            currency=currency
        )

    @traceable(name="travelpilot_supervisor_multiagent", run_type="chain")
    def execute_multi_agent_pipeline(self, initial_state: PlannerState) -> PlannerState:
        """Runs the multi-agent pipeline and returns the fully validated state."""
        state = initial_state
        state["logs"].append("🚀 SupervisorAgent: Initiating Multi-Agent Travel Orchestration...")
        logger.info(f"SupervisorAgent started for destination '{state['destination']}'")

        # =====================================================================
        # Step 1: Auditor Agent -> Input Guardrails
        # =====================================================================
        state["logs"].append("🛡️ AuditorAgent: Validating input parameters & safety guardrails...")
        state["current_step_status"] = "Auditor Agent: Running safety guardrails..."
        input_audit = self._traceable_input_audit(
            destination=state["destination"],
            start_date=state["start_date"],
            end_date=state["end_date"],
            budget=state["budget"],
            currency=state.get("currency", "INR"),
            travelers=state.get("travelers", 1)
        )

        if not input_audit.is_safe:
            state["logs"].append(f"❌ Input Guardrail BLOCKED: {input_audit.violations}")
            state["current_step_status"] = "Blocked by Safety Guardrails"
            state["is_valid"] = False
            state["final_itinerary_summary"] = f"Planning suspended: {'; '.join(input_audit.violations)}"
            return state

        if input_audit.violations:
            state["logs"].append(f"⚠️ Input Guardrail Notice: {input_audit.violations}")

        # =====================================================================
        # Step 2: Research Agent -> Tavily Search & Geocoding
        # =====================================================================
        state["logs"].append(f"🔍 ResearchAgent: Querying Tavily for attractions & dining in {state['destination']}...")
        state["current_step_status"] = "Research Agent: Querying live web attractions..."
        research_data = self._traceable_research(
            destination=state["destination"],
            interests=state.get("interests", ["Culture", "Food"]),
            food_pref=state.get("food_preferences", "Local Cuisine")
        )
        state["search_results"].extend(research_data.get("search_snippets", []))
        if research_data.get("center_coordinates"):
            state["locations_data"].append(research_data["center_coordinates"])

        # =====================================================================
        # Step 3: Weather Risk Agent -> Multi-Day Forecast
        # =====================================================================
        state["logs"].append(f"🌤️ WeatherRiskAgent: Evaluating meteorological alerts for {state['destination']}...")
        state["current_step_status"] = "Weather Risk Agent: Checking forecasts and rain alerts..."
        weather_data = self._traceable_weather(state["destination"], days=5)
        state["weather_forecast"] = weather_data.get("forecast", [])

        # =====================================================================
        # Step 4: Budget Optimizer Agent -> Category Breakdown
        # =====================================================================
        state["logs"].append(f"💰 BudgetOptimizerAgent: Enforcing financial allocation for {state.get('currency', 'INR')} {state['budget']}...")
        state["current_step_status"] = "Budget Optimizer Agent: Calibrating financial allocations..."
        budget_data = self._traceable_budget(
            budget=state["budget"],
            travel_style=state.get("travel_style", "Balanced"),
            currency=state.get("currency", "INR")
        )
        state["calculated_budget"] = budget_data.get("category_breakdown", {})

        # =====================================================================
        # Step 5: Day-by-Day Schedule Generation
        # =====================================================================
        state["logs"].append("🗺️ SupervisorAgent: Synthesizing day-by-day structured itinerary...")
        state["current_step_status"] = "Supervisor Agent: Structuring day-by-day activities..."
        try:
            d1 = datetime.strptime(state["start_date"], "%Y-%m-%d")
            d2 = datetime.strptime(state["end_date"], "%Y-%m-%d")
            num_days = max(1, (d2 - d1).days + 1)
        except Exception:
            num_days = 4

        days = _generate_distinct_days(state, num_days)
        state["draft_itinerary"] = days

        # =====================================================================
        # Step 6: Weather Risk Agent -> Proactive Conflict Detection & Swap
        # =====================================================================
        state["logs"].append("⚡ WeatherRiskAgent: Scanning for rain risks & schedule overlaps...")
        state["current_step_status"] = "Weather Risk Agent: Auto-remediating conflicts..."
        risk_remediation = self._traceable_remediation(
            draft_itinerary=state["draft_itinerary"],
            weather_forecast=state["weather_forecast"],
            destination=state["destination"]
        )
        state["conflicts"] = risk_remediation.get("conflicts", [])
        state["is_valid"] = risk_remediation.get("is_conflict_free", True)

        remediated_count = risk_remediation.get("remediated_count", 0)
        if remediated_count > 0:
            state["logs"].append(f"✅ Auto-swapped {remediated_count} outdoor activity to covered indoor venues.")

        # =====================================================================
        # Step 7: Auditor Agent -> Output Guardrail Review
        # =====================================================================
        state["logs"].append("🛡️ AuditorAgent: Reviewing output guardrails (budget caps, hours, overlaps)...")
        state["current_step_status"] = "Auditor Agent: Final safety & budget audit..."
        output_audit = self._traceable_output_audit(
            draft_itinerary=state["draft_itinerary"],
            budget=state["budget"],
            currency=state.get("currency", "INR")
        )

        if output_audit.violations:
            state["logs"].append(f"⚠️ Output Audit Findings: {'; '.join(output_audit.violations)}")
            for rem in output_audit.remediations:
                state["logs"].append(f"   ↳ Applied Remediation: {rem}")

        # =====================================================================
        # Step 8: Final Synthesis & Cost Calculation
        # =====================================================================
        cost_summary = budget_optimizer_agent.calibrate_activity_costs(
            draft_itinerary=state["draft_itinerary"],
            total_budget=state["budget"],
            currency=state.get("currency", "INR")
        )

        state["logs"].append(
            f"🎉 Multi-Agent Orchestration complete! Total estimated cost: "
            f"{state.get('currency', 'INR')} {cost_summary['total_estimated_cost']:,.2f}."
        )
        state["current_step_status"] = "Multi-Agent Planning Complete!"
        state["final_itinerary_summary"] = (
            f"Multi-Agent Verified {len(state['draft_itinerary'])}-day itinerary for {state['destination']} "
            f"({state['travel_style']} style, total estimated cost: {state.get('currency', 'INR')} {cost_summary['total_estimated_cost']:,.2f}). "
            f"Guardrails verified: {len(output_audit.violations)} advisory notes, {remediated_count} weather auto-swaps applied."
        )

        return state

supervisor_agent = SupervisorAgent()
