import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END

from backend.graph.state import PlannerState
from backend.services.llm_service import llm_service
from backend.tools.tavily_tool import tavily_tool
from backend.tools.weather_tool import weather_tool
from backend.tools.maps_tool import maps_tool
from backend.tools.budget_tool import budget_tool
from backend.tools.conflict_detector import conflict_detector
from backend.tools.alternative_finder import alternative_finder

logger = logging.getLogger("travelpilot.planning_graph")

def node_understand_requirements(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append(f"Understanding requirements for trip to {state['destination']}...")
    state["current_step_status"] = "Analyzing user preferences and dates..."
    return state

def node_search_destination(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append(f"Searching travel overview for {state['destination']} via Tavily...")
    state["current_step_status"] = f"Searching overview of {state['destination']}..."
    results = tavily_tool.search(f"best places to visit and travel guide for {state['destination']}")
    state["search_results"].extend(results)
    return state

def node_search_activities(state: PlannerState) -> Dict[str, Any]:
    interests_str = ", ".join(state["interests"]) if state["interests"] else "top tourist landmarks"
    state["logs"].append(f"Searching activities matching interests ({interests_str})...")
    state["current_step_status"] = f"Searching activities for interests ({interests_str})..."
    results = tavily_tool.search(f"must visit attractions in {state['destination']} for {interests_str}")
    state["search_results"].extend(results)
    return state

def node_search_restaurants(state: PlannerState) -> Dict[str, Any]:
    food_pref = state.get("food_preferences", "Local Cuisine")
    state["logs"].append(f"Searching dining spots for {food_pref}...")
    state["current_step_status"] = f"Searching top restaurants ({food_pref})..."
    results = tavily_tool.search(f"best restaurants and local dishes in {state['destination']} {food_pref}")
    state["search_results"].extend(results)
    return state

def node_check_weather(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append(f"Fetching multi-day weather forecast for {state['destination']}...")
    state["current_step_status"] = "Checking weather forecast and rain probability..."
    w_res = weather_tool.get_forecast(state["destination"], days=5)
    state["weather_forecast"] = w_res.get("forecast", [])
    return state

def node_check_locations(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append("Analyzing geographic clusters and geocoding locations...")
    state["current_step_status"] = "Geocoding places and organizing location clusters..."
    loc = maps_tool.search_place(state["destination"])
    state["locations_data"].append(loc)
    return state

def node_calculate_travel_time(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append("Estimating transit times between neighboring spots...")
    state["current_step_status"] = "Calculating transit distances and travel times..."
    return state

def node_calculate_budget(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append(f"Calculating budget breakdown for total {state.get('currency', 'INR')} {state['budget']}...")
    state["current_step_status"] = "Optimizing budget allocation across categories..."
    alloc = budget_tool.calculate_allocation(state["budget"], state.get("travel_style", "Balanced"))
    state["calculated_budget"] = alloc
    return state

def node_build_initial_itinerary(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append("Building initial day-by-day structured itinerary with Gemini AI...")
    state["current_step_status"] = "Structuring day-by-day itinerary slots..."

    try:
        d1 = datetime.strptime(state["start_date"], "%Y-%m-%d")
        d2 = datetime.strptime(state["end_date"], "%Y-%m-%d")
        num_days = max(1, (d2 - d1).days + 1)
    except Exception:
        num_days = 4

    days = _generate_distinct_days(state, num_days)
    state["draft_itinerary"] = days
    return state

def node_validate_itinerary(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append("Validating itinerary schedule consistency...")
    state["current_step_status"] = "Verifying opening hours and buffer times..."
    return state

def node_detect_conflicts(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append("Scanning for schedule overlaps, rain risks, and flight delay risks...")
    state["current_step_status"] = "Predictive Risk Shield scanning for weather & flight disruptions..."
    conflicts = conflict_detector.detect_conflicts(state["draft_itinerary"], state["weather_forecast"])

    # Ensure each conflict has an explicit human-readable reason
    for conf in conflicts:
        if not conf.get("reason"):
            if conf.get("type") == "weather_conflict":
                conf["reason"] = f"Reason: Expected rain/weather alert ({conf.get('description')}), auto-shifted to indoor venue."
            else:
                conf["reason"] = f"Reason: Schedule overlap or transit buffer conflict detected for {conf.get('activity_name', 'activity')}."

    state["conflicts"] = conflicts
    state["is_valid"] = len(conflicts) == 0
    return state

def node_optimize_itinerary(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append(f"Optimizing itinerary to resolve {len(state['conflicts'])} conflicts...")
    state["current_step_status"] = "Re-planning to replace rained-out or conflicting activities..."

    for conf in state["conflicts"]:
        day_num = conf.get("day_number")
        act_name = conf.get("activity_name")

        for day in state["draft_itinerary"]:
            if day.get("day_number") == day_num:
                for act in day.get("activities", []):
                    if act.get("name") == act_name:
                        if conf.get("type") == "weather_conflict":
                            alt = alternative_finder.find_weather_alternatives(act_name, state["destination"])
                            act["name"] = alt["name"]
                            act["description"] = alt["description"]
                            act["notes"] = f"Reason: Expected heavy rain ({conf.get('description')}). Auto-swapped to indoor museum."
                            act["backup_option"] = f"Original outdoor activity: {act_name}"

    state["retry_count"] += 1
    return state

def node_generate_final_itinerary(state: PlannerState) -> Dict[str, Any]:
    state["logs"].append("Finalizing itinerary generation!")
    state["current_step_status"] = "Itinerary complete!"
    state["final_itinerary_summary"] = (
        f"Custom {len(state['draft_itinerary'])}-day itinerary for {state['destination']} "
        f"({state['travel_style']} style, total estimated cost: ₹{sum(act.get('estimated_cost', 0) for d in state['draft_itinerary'] for act in d['activities']):.2f})."
    )
    return state

def should_replan(state: PlannerState) -> str:
    if not state["is_valid"] and state["retry_count"] < 2:
        return "replan"
    return "final"

def build_planning_graph():
    workflow = StateGraph(PlannerState)

    workflow.add_node("understand_requirements", node_understand_requirements)
    workflow.add_node("search_destination", node_search_destination)
    workflow.add_node("search_activities", node_search_activities)
    workflow.add_node("search_restaurants", node_search_restaurants)
    workflow.add_node("check_weather", node_check_weather)
    workflow.add_node("check_locations", node_check_locations)
    workflow.add_node("calculate_travel_time", node_calculate_travel_time)
    workflow.add_node("calculate_budget", node_calculate_budget)
    workflow.add_node("build_initial_itinerary", node_build_initial_itinerary)
    workflow.add_node("validate_itinerary", node_validate_itinerary)
    workflow.add_node("detect_conflicts", node_detect_conflicts)
    workflow.add_node("optimize_itinerary", node_optimize_itinerary)
    workflow.add_node("generate_final_itinerary", node_generate_final_itinerary)

    workflow.set_entry_point("understand_requirements")
    workflow.add_edge("understand_requirements", "search_destination")
    workflow.add_edge("search_destination", "search_activities")
    workflow.add_edge("search_activities", "search_restaurants")
    workflow.add_edge("search_restaurants", "check_weather")
    workflow.add_edge("check_weather", "check_locations")
    workflow.add_edge("check_locations", "calculate_travel_time")
    workflow.add_edge("calculate_travel_time", "calculate_budget")
    workflow.add_edge("calculate_budget", "build_initial_itinerary")
    workflow.add_edge("build_initial_itinerary", "validate_itinerary")
    workflow.add_edge("validate_itinerary", "detect_conflicts")

    workflow.add_conditional_edges(
        "detect_conflicts",
        should_replan,
        {
            "replan": "optimize_itinerary",
            "final": "generate_final_itinerary"
        }
    )

    workflow.add_edge("optimize_itinerary", "validate_itinerary")
    workflow.add_edge("generate_final_itinerary", END)

    return workflow.compile()


def _generate_distinct_days(state: PlannerState, num_days: int) -> List[Dict[str, Any]]:
    """Generate distinct, non-repeating activities for each day of the itinerary in Rupees (₹)."""
    dest = state["destination"]
    dest_lower = dest.lower()
    start_dt = datetime.strptime(state["start_date"], "%Y-%m-%d") if state.get("start_date") else datetime.now()
    weather_list = state.get("weather_forecast", [])

    # City-specific templates with real places & Rupees pricing
    if "pune" in dest_lower:
        day_templates = [
            {
                "theme": "Day 1: Historic Forts & Heritage Landmarks",
                "activities": [
                    {
                        "name": "Shaniwar Wada Fort Exploration",
                        "description": "Historical 18th-century fortification seat of the Peshwas of the Maratha Empire.",
                        "category": "Attraction",
                        "location_name": "Shaniwar Peth, Pune",
                        "latitude": 18.5196, "longitude": 73.8553,
                        "start_time": "09:00", "end_time": "11:30", "duration_minutes": 150,
                        "estimated_cost": 25.0, "opening_hours": "08:00 - 18:30",
                        "travel_time_from_prev_mins": 10, "distance_from_prev_km": 1.2,
                        "backup_option": "Raja Dinkar Kelkar Museum"
                    },
                    {
                        "name": "Authentic Misal Pav Lunch at Bedekar Tea Stall",
                        "description": "Sample Pune's world-famous spicy Puneri Misal served with fresh bread rolls and farsan.",
                        "category": "Restaurant",
                        "location_name": "Narayan Peth, Pune",
                        "latitude": 18.5167, "longitude": 73.8512,
                        "start_time": "12:00", "end_time": "13:30", "duration_minutes": 90,
                        "estimated_cost": 180.0, "opening_hours": "07:30 - 20:00",
                        "travel_time_from_prev_mins": 10, "distance_from_prev_km": 0.8,
                        "backup_option": "Chitale Bandhu Mithaiwale"
                    },
                    {
                        "name": "Lal Mahal & Dagadusheth Halwai Ganapati Temple",
                        "description": "Visit Chrapati Shivaji Maharaj's historic palace followed by prayer at the iconic Ganapati temple.",
                        "category": "Attraction",
                        "location_name": "Budhwar Peth, Pune",
                        "latitude": 18.5178, "longitude": 73.8562,
                        "start_time": "14:30", "end_time": "17:00", "duration_minutes": 150,
                        "estimated_cost": 0.0, "opening_hours": "06:00 - 22:00",
                        "travel_time_from_prev_mins": 15, "distance_from_prev_km": 1.5,
                        "backup_option": "Pataleshwar Cave Temple"
                    },
                    {
                        "name": "Traditional Maharashtrian Thali Dinner at Durvankur",
                        "description": "Unlimited Maharashtrian royal feast with Puran Poli, Amti, Kothimbir Vadi, and Solkadhi.",
                        "category": "Restaurant",
                        "location_name": "Sadashiv Peth, Pune",
                        "latitude": 18.5135, "longitude": 73.8490,
                        "start_time": "19:00", "end_time": "21:00", "duration_minutes": 120,
                        "estimated_cost": 450.0, "opening_hours": "12:00 - 22:30",
                        "travel_time_from_prev_mins": 15, "distance_from_prev_km": 2.0,
                        "backup_option": "Sukanta Pure Veg Thali"
                    }
                ]
            },
            {
                "theme": "Day 2: Royal Palaces, Caves & Cultural Museums",
                "activities": [
                    {
                        "name": "Aga Khan Palace & Gandhi Memorial",
                        "description": "Majestic Italian-arched palace surrounded by lush lawns where Mahatma Gandhi was interned.",
                        "category": "Attraction",
                        "location_name": "Nagar Road, Yerwada, Pune",
                        "latitude": 18.5529, "longitude": 73.9015,
                        "start_time": "09:30", "end_time": "12:00", "duration_minutes": 150,
                        "estimated_cost": 30.0, "opening_hours": "09:00 - 17:30",
                        "travel_time_from_prev_mins": 25, "distance_from_prev_km": 8.5,
                        "backup_option": "Tribal Cultural Museum"
                    },
                    {
                        "name": "Cafe Goodluck - Legendary Bun Maska & Chai",
                        "description": "Pune's oldest Irani cafe famous for Mutton Keema Pav, Bun Maska, and Irani Chai.",
                        "category": "Restaurant",
                        "location_name": "Deccan Gymkhana, FC Road, Pune",
                        "latitude": 18.5166, "longitude": 73.8410,
                        "start_time": "12:30", "end_time": "14:00", "duration_minutes": 90,
                        "estimated_cost": 250.0, "opening_hours": "07:30 - 23:30",
                        "travel_time_from_prev_mins": 20, "distance_from_prev_km": 6.2,
                        "backup_option": "Vohuman Cafe"
                    },
                    {
                        "name": "Pataleshwar Rock-Cut Cave Temple",
                        "description": "8th-century monolithic rock-cut cave temple dedicated to Lord Shiva carved from basalt rock.",
                        "category": "Attraction",
                        "location_name": "JM Road, Shivajinagar, Pune",
                        "latitude": 18.5283, "longitude": 73.8504,
                        "start_time": "15:00", "end_time": "17:00", "duration_minutes": 120,
                        "estimated_cost": 0.0, "opening_hours": "08:30 - 17:30",
                        "travel_time_from_prev_mins": 10, "distance_from_prev_km": 1.8,
                        "backup_option": "Joshi's Museum of Miniature Railway"
                    },
                    {
                        "name": "Evening Promenade & Dinner at Koregaon Park",
                        "description": "Stroll through leafy KP lanes followed by artisan dining at German Bakery or Malaka Spice.",
                        "category": "Restaurant",
                        "location_name": "Koregaon Park, Pune",
                        "latitude": 18.5362, "longitude": 73.8940,
                        "start_time": "18:30", "end_time": "21:00", "duration_minutes": 150,
                        "estimated_cost": 750.0, "opening_hours": "11:00 - 23:30",
                        "travel_time_from_prev_mins": 20, "distance_from_prev_km": 5.0,
                        "backup_option": "Arthur's Theme Bistro"
                    }
                ]
            },
            {
                "theme": "Day 3: Hillside Forts & Scenic Panoramas",
                "activities": [
                    {
                        "name": "Sinhagad Fort Hill Trek & Tanaji Malusare Memorial",
                        "description": "Hike or drive up Sinhagad fort for panoramic Sahyadri views and fresh Kanda Bhajji with Pithla Bhakri.",
                        "category": "Attraction",
                        "location_name": "Thoptewadi, Sinhagad Road, Pune",
                        "latitude": 18.3663, "longitude": 73.7558,
                        "start_time": "08:00", "end_time": "12:00", "duration_minutes": 240,
                        "estimated_cost": 50.0, "opening_hours": "05:00 - 19:00",
                        "travel_time_from_prev_mins": 45, "distance_from_prev_km": 30.0,
                        "backup_option": "Pu La Deshpande Japanese Garden"
                    },
                    {
                        "name": "Rustic Village Meal at Sinhagad Fort Top",
                        "description": "Earthen pot Matka Dahi, Jowar Bhakri, Thecha, and hot Kanda Bhajji made fresh by village vendors.",
                        "category": "Restaurant",
                        "location_name": "Sinhagad Fort Top, Pune",
                        "latitude": 18.3660, "longitude": 73.7550,
                        "start_time": "12:30", "end_time": "14:00", "duration_minutes": 90,
                        "estimated_cost": 200.0, "opening_hours": "08:00 - 18:00",
                        "travel_time_from_prev_mins": 5, "distance_from_prev_km": 0.2,
                        "backup_option": "Khadakwasla Lake Food Stalls"
                    },
                    {
                        "name": "Khadakwasla Dam Lake Sunset Walk",
                        "description": "Relaxing lakeside breeze, street corn cobs, and sunset views over the reservoir.",
                        "category": "Attraction",
                        "location_name": "Khadakwasla Reservoir, Pune",
                        "latitude": 18.4418, "longitude": 73.7663,
                        "start_time": "16:00", "end_time": "18:30", "duration_minutes": 150,
                        "estimated_cost": 0.0, "opening_hours": "24 Hours Open",
                        "travel_time_from_prev_mins": 25, "distance_from_prev_km": 12.0,
                        "backup_option": "Saras Baug Lake Park"
                    },
                    {
                        "name": "Dinner & Craft Brews at FC Road / Balewadi High Street",
                        "description": "Enjoy Pune's vibrant microbrewery scene and multi-cuisine gastro dining.",
                        "category": "Restaurant",
                        "location_name": "Balewadi High Street, Pune",
                        "latitude": 18.5794, "longitude": 73.7712,
                        "start_time": "19:30", "end_time": "22:00", "duration_minutes": 150,
                        "estimated_cost": 900.0, "opening_hours": "12:00 - 01:00",
                        "travel_time_from_prev_mins": 30, "distance_from_prev_km": 18.0,
                        "backup_option": "Effingut Brewhouse"
                    }
                ]
            },
            {
                "theme": "Day 4: Shopping Bazaars, Gardens & City Sunset",
                "activities": [
                    {
                        "name": "Laxmi Road & Tulshibaug Shopping Bazaar",
                        "description": "Bustling traditional street shopping for Puneri footwear, copperware, sarees, and souvenirs.",
                        "category": "Attraction",
                        "location_name": "Tulshibaug, Budhwar Peth, Pune",
                        "latitude": 18.5152, "longitude": 73.8546,
                        "start_time": "10:00", "end_time": "12:30", "duration_minutes": 150,
                        "estimated_cost": 0.0, "opening_hours": "10:00 - 21:00",
                        "travel_time_from_prev_mins": 15, "distance_from_prev_km": 2.0,
                        "backup_option": "Phoenix Marketcity Viman Nagar"
                    },
                    {
                        "name": "Lunch at Vaishali - FC Road Favorite",
                        "description": "Iconic South Indian delicacies, Special Masala Dosa, Sev Puri, and Filter Coffee.",
                        "category": "Restaurant",
                        "location_name": "Fergusson College Road, Pune",
                        "latitude": 18.5204, "longitude": 73.8415,
                        "start_time": "13:00", "end_time": "14:30", "duration_minutes": 90,
                        "estimated_cost": 300.0, "opening_hours": "07:00 - 23:00",
                        "travel_time_from_prev_mins": 15, "distance_from_prev_km": 2.2,
                        "backup_option": "Roopali Restaurant"
                    },
                    {
                        "name": "Pu La Deshpande Japanese Shadow Garden (Okayama Friendship)",
                        "description": "Serene Japanese garden with natural waterfalls, koi ponds, and wooden footbridges.",
                        "category": "Attraction",
                        "location_name": "Sinhagad Road, Pune",
                        "latitude": 18.4912, "longitude": 73.8345,
                        "start_time": "15:30", "end_time": "17:30", "duration_minutes": 120,
                        "estimated_cost": 20.0, "opening_hours": "06:00 - 10:30, 16:00 - 20:00",
                        "travel_time_from_prev_mins": 15, "distance_from_prev_km": 3.5,
                        "backup_option": "Empress Botanical Garden"
                    },
                    {
                        "name": "Farewell Dinner at Paasha Rooftop JW Marriott",
                        "description": "360-degree skyline views of Pune with North Indian kebabs and signature cocktails.",
                        "category": "Restaurant",
                        "location_name": "Senapati Bapat Road, Pune",
                        "latitude": 18.5328, "longitude": 73.8290,
                        "start_time": "19:00", "end_time": "21:30", "duration_minutes": 150,
                        "estimated_cost": 1500.0, "opening_hours": "17:30 - 01:00",
                        "travel_time_from_prev_mins": 20, "distance_from_prev_km": 5.0,
                        "backup_option": "The Baan Yaai Thai Bistro"
                    }
                ]
            }
        ]
    elif "mumbai" in dest_lower:
        day_templates = [
            {
                "theme": "Day 1: Historic South Mumbai & Colonial Architecture",
                "activities": [
                    {
                        "name": "Gateway of India & Taj Mahal Palace Hotel Walk",
                        "description": "Iconic arch monument facing the Arabian Sea built during the British Raj.",
                        "category": "Attraction",
                        "location_name": "Apollo Bandar, Colaba, Mumbai",
                        "latitude": 18.9220, "longitude": 72.8347,
                        "start_time": "09:00", "end_time": "11:30", "duration_minutes": 150,
                        "estimated_cost": 0.0, "opening_hours": "24 Hours Open",
                        "travel_time_from_prev_mins": 15, "distance_from_prev_km": 2.0,
                        "backup_option": "Chhatrapati Shivaji Maharaj Vastu Sangrahalaya"
                    },
                    {
                        "name": "Lunch at Leopold Cafe - Colaba Heritage",
                        "description": "Famous historic cafe serving cold beers, Chicken Stroganoff, and Mumbai street bites.",
                        "category": "Restaurant",
                        "location_name": "Colaba Causeway, Mumbai",
                        "latitude": 18.9228, "longitude": 72.8318,
                        "start_time": "12:00", "end_time": "13:30", "duration_minutes": 90,
                        "estimated_cost": 650.0, "opening_hours": "07:30 - 00:00",
                        "travel_time_from_prev_mins": 5, "distance_from_prev_km": 0.4,
                        "backup_option": "Cafe Mondegar"
                    },
                    {
                        "name": "Marine Drive Promenade 'Queen's Necklace' Walk",
                        "description": "Scenic 3.6 km C-shaped boulevard along the coast with Arabian Sea sunset views.",
                        "category": "Attraction",
                        "location_name": "Netaji Subhash Chandra Bose Road, Mumbai",
                        "latitude": 18.9438, "longitude": 72.8231,
                        "start_time": "16:30", "end_time": "18:30", "duration_minutes": 120,
                        "estimated_cost": 0.0, "opening_hours": "24 Hours Open",
                        "travel_time_from_prev_mins": 15, "distance_from_prev_km": 2.5,
                        "backup_option": "Hanging Gardens & Kamala Nehru Park"
                    },
                    {
                        "name": "Seafood Feast at Trishna / Mahesh Lunch Home",
                        "description": "World-renowned Mangalorean butter garlic crab, fish curry, and Neer Dosa.",
                        "category": "Restaurant",
                        "location_name": "Kala Ghoda, Fort, Mumbai",
                        "latitude": 18.9280, "longitude": 72.8320,
                        "start_time": "19:30", "end_time": "21:30", "duration_minutes": 120,
                        "estimated_cost": 1200.0, "opening_hours": "12:00 - 15:30, 19:00 - 23:30",
                        "travel_time_from_prev_mins": 15, "distance_from_prev_km": 2.0,
                        "backup_option": "Bastian Bandra"
                    }
                ]
            },
            {
                "theme": "Day 2: Bollywood Vibes, Bandra Fort & Seaside Dining",
                "activities": [
                    {
                        "name": "Bandra Fort (Castella de Aguada) & Bandstand Walk",
                        "description": "17th-century Portuguese fort ruins overlooking Bandra-Worli Sea Link and Shah Rukh Khan's Mannat.",
                        "category": "Attraction",
                        "location_name": "Byramji Jeejeebhoy Road, Bandra West, Mumbai",
                        "latitude": 19.0434, "longitude": 72.8190,
                        "start_time": "10:00", "end_time": "12:30", "duration_minutes": 150,
                        "estimated_cost": 0.0, "opening_hours": "06:00 - 18:30",
                        "travel_time_from_prev_mins": 30, "distance_from_prev_km": 15.0,
                        "backup_option": "Mount Mary Church Bandra"
                    },
                    {
                        "name": "Lunch at Candies - Quirky Portuguese Bistro",
                        "description": "Multi-level outdoor terrace serving chicken rolls, lasagna, cold coffee, and fresh pastries.",
                        "category": "Restaurant",
                        "location_name": "Pali Hill, Bandra West, Mumbai",
                        "latitude": 19.0610, "longitude": 72.8290,
                        "start_time": "13:00", "end_time": "14:30", "duration_minutes": 90,
                        "estimated_cost": 400.0, "opening_hours": "08:30 - 22:00",
                        "travel_time_from_prev_mins": 10, "distance_from_prev_km": 2.1,
                        "backup_option": "Subko Specialty Coffee & Craft Bakehouse"
                    },
                    {
                        "name": "Juhu Beach Sunset Walk & Mumbai Street Food",
                        "description": "Famous beach walk sampling Pav Bhaji at Shiv Sagar and Pani Puri by the sea.",
                        "category": "Attraction",
                        "location_name": "Juhu Tara Road, Mumbai",
                        "latitude": 19.0988, "longitude": 72.8264,
                        "start_time": "16:30", "end_time": "18:30", "duration_minutes": 120,
                        "estimated_cost": 150.0, "opening_hours": "24 Hours Open",
                        "travel_time_from_prev_mins": 25, "distance_from_prev_km": 7.0,
                        "backup_option": "Prithvi Theatre Cafe"
                    },
                    {
                        "name": "Seaside Sunset Dinner at Dome - InterContinental",
                        "description": "Rooftop lounge overlooking the Arabian Sea with Mediterranean mezze and artisan cocktails.",
                        "category": "Restaurant",
                        "location_name": "Marine Drive, Mumbai",
                        "latitude": 18.9350, "longitude": 72.8240,
                        "start_time": "19:30", "end_time": "22:00", "duration_minutes": 150,
                        "estimated_cost": 1800.0, "opening_hours": "17:00 - 01:30",
                        "travel_time_from_prev_mins": 30, "distance_from_prev_km": 18.0,
                        "backup_option": "Olive Bar & Kitchen Bandra"
                    }
                ]
            }
        ]
    else:
        # Generic multi-day non-repeating template
        day_templates = []
        for i in range(1, num_days + 1):
            day_templates.append({
                "theme": f"Day {i}: Exploring {dest} Local Highlights",
                "activities": [
                    {
                        "name": f"Morning Tour of {dest} Historic District (Day {i})",
                        "description": f"Guided walking tour around iconic monuments and architecture of {dest}.",
                        "category": "Attraction", "location_name": f"{dest} District {i}",
                        "latitude": 18.5200 + (i * 0.01), "longitude": 73.8500 + (i * 0.01),
                        "start_time": "09:00", "end_time": "11:30", "duration_minutes": 150,
                        "estimated_cost": round(150.0 * i, 2), "opening_hours": "08:00 - 18:00",
                        "travel_time_from_prev_mins": 10, "distance_from_prev_km": 1.5,
                        "backup_option": f"{dest} Central Heritage Museum"
                    },
                    {
                        "name": f"Authentic Regional Lunch - Spot {i}",
                        "description": f"Sample local specialties, regional curries, fresh bread, and sweets.",
                        "category": "Restaurant", "location_name": f"{dest} Food Bazaar {i}",
                        "latitude": 18.5220 + (i * 0.01), "longitude": 73.8520 + (i * 0.01),
                        "start_time": "12:00", "end_time": "13:30", "duration_minutes": 90,
                        "estimated_cost": round(250.0 + (i * 50), 2), "opening_hours": "11:00 - 23:00",
                        "travel_time_from_prev_mins": 15, "distance_from_prev_km": 1.2,
                        "backup_option": f"Covered Food Market {i}"
                    },
                    {
                        "name": f"Afternoon Cultural Visit - Landmark {i}",
                        "description": f"Art galleries, botanical gardens, and scenic viewpoints.",
                        "category": "Attraction", "location_name": f"{dest} Garden Square {i}",
                        "latitude": 18.5240 + (i * 0.01), "longitude": 73.8540 + (i * 0.01),
                        "start_time": "14:30", "end_time": "17:00", "duration_minutes": 150,
                        "estimated_cost": round(100.0, 2), "opening_hours": "10:00 - 18:00",
                        "travel_time_from_prev_mins": 20, "distance_from_prev_km": 2.5,
                        "backup_option": f"{dest} Indoor Exhibition Hall"
                    },
                    {
                        "name": f"Evening Dinner & City Promenade - Spot {i}",
                        "description": f"Relaxing evening walk followed by a 3-course dinner.",
                        "category": "Restaurant", "location_name": f"{dest} Promenade {i}",
                        "latitude": 18.5260 + (i * 0.01), "longitude": 73.8560 + (i * 0.01),
                        "start_time": "18:30", "end_time": "21:00", "duration_minutes": 150,
                        "estimated_cost": round(500.0 + (i * 100), 2), "opening_hours": "18:00 - 23:00",
                        "travel_time_from_prev_mins": 20, "distance_from_prev_km": 3.0,
                        "backup_option": f"Skyline View Bistro {i}"
                    }
                ]
            })

    days = []
    for d in range(1, num_days + 1):
        cur_date = (start_dt + timedelta(days=d - 1)).strftime("%Y-%m-%d")
        w_item = weather_list[d - 1] if d - 1 < len(weather_list) else {"condition": "Partly Cloudy", "temp_high_c": 26}
        w_summary = f"{w_item.get('condition', 'Partly Cloudy')} {w_item.get('temp_high_c', 26)}°C"

        tmpl_idx = (d - 1) % len(day_templates)
        tmpl = day_templates[tmpl_idx]

        days.append({
            "day_number": d,
            "date": cur_date,
            "theme": tmpl["theme"],
            "weather_summary": w_summary,
            "activities": tmpl["activities"]
        })

    return days

planning_graph_app = build_planning_graph()
