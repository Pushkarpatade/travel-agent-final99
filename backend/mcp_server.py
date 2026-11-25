"""TravelPilot Official Model Context Protocol (MCP) Server.

Exposes TravelPilot's autonomous travel tools to MCP clients
(such as Claude Desktop, Cursor, Antigravity, and autonomous agent swarms).

Usage:
    python -m backend.mcp_server
"""

import sys
import os
import json
from typing import List, Dict, Any, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.mcpserver import MCPServer
from backend.agents.research_agent import research_agent
from backend.agents.weather_risk_agent import weather_risk_agent
from backend.agents.budget_optimizer_agent import budget_optimizer_agent
from backend.guardrails.safety_guardrails import safety_guardrails
from backend.services.llm_service import llm_service

# Initialize MCPServer
mcp = MCPServer(
    name="TravelPilot-AI",
    dependencies=["tavily-python", "google-genai", "langchain", "redis"]
)

@mcp.tool()
def search_attractions(destination: str, interests: List[str] = ["Culture", "Food"]) -> str:
    """Discovers real-world attractions, dining hotspots, and ticket prices via Tavily web search."""
    data = research_agent.research_destination(
        destination=destination,
        interests=interests,
        food_pref="Local Cuisine"
    )
    return json.dumps(data, indent=2)

@mcp.tool()
def check_weather_risks(destination: str, days: int = 5) -> str:
    """Analyzes multi-day meteorological forecasts, evaluates precipitation probabilities, and detects rain conflicts."""
    data = weather_risk_agent.analyze_weather_risks(destination, days=days)
    return json.dumps(data, indent=2)

@mcp.tool()
def optimize_travel_budget(total_budget: float, travel_style: str = "Balanced", currency: str = "INR") -> str:
    """Calculates optimal expenditure breakdown across stay (45%), dining (25%), sightseeing (20%), and contingency (10%)."""
    data = budget_optimizer_agent.optimize_budget(
        total_budget=total_budget,
        travel_style=travel_style,
        currency=currency
    )
    return json.dumps(data, indent=2)

@mcp.tool()
def audit_travel_guardrails(destination: str, budget: float, currency: str = "INR") -> str:
    """Audits incoming trip request for international travel advisories, prompt injection defense, and budget feasibility."""
    result = safety_guardrails.validate_trip_inputs({
        "destination": destination,
        "budget": budget,
        "currency": currency,
        "start_date": "2026-10-01",
        "end_date": "2026-10-04"
    })
    return json.dumps({
        "is_safe": result.is_safe,
        "risk_level": result.risk_level,
        "violations": result.violations,
        "remediations": result.remediations
    }, indent=2)

@mcp.tool()
def ask_travelpilot(destination: str, user_question: str) -> str:
    """Asks the TravelPilot Gemini conversational travel assistant for real-time recommendations."""
    prompt = f"User is traveling to {destination}. Question: {user_question}"
    system = f"You are TravelPilot, an expert AI travel guide for {destination}. Give a concise, warm, practical 2-3 sentence answer."
    reply = llm_service.generate_text(prompt, system_instruction=system)
    return reply or f"TravelPilot recommends exploring central landmarks in {destination}!"

if __name__ == "__main__":
    mcp.run()
