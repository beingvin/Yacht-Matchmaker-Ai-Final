import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools import AgentTool ,FunctionTool
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH_1 = os.path.normpath(os.path.join(CURRENT_DIR, 'yachts_seed.json'))
DATA_PATH_2 = os.path.normpath(os.path.join(CURRENT_DIR, 'theme_templates.json'))

gemini_model = "gemini-2.0-flash"


#load data from json file

# load yacht seed data 
with open(DATA_PATH_1, "r") as f:
    yacht_seed = json.load(f)
    
# Convert the yacht_seed dictionary/list into a JSON string
yacht_seed_str = json.dumps(yacht_seed, indent=2)    

# load theme templates data 
with open(DATA_PATH_2, "r") as f:
    theme_templates = json.load(f)

theme_templates_str = json.dumps(theme_templates, indent=2)    




# --- 1. Function Tools Setup ---
def search_weather(location: str, date: str) -> str:
    """Fetches weather forecast for maritime safety."""
    # (Mock for now - Connect to OpenMeteo later)
    return f"Weather in {location} on {date}: Clear skies, Wind 10kn (Safe)."

def get_total_price(base_price: str, total_hrs: str) -> str: 
    """Calculate the total sailing price based on total sailing hours."""
    try:
        # 1. Convert inputs from string to float
        price_float = float(base_price)
        hours_float = float(total_hrs)
        
        # 2. Perform the calculation
        total_price_float = price_float * hours_float
        
        # 3. Convert the result back to a string for the return value
        return str(total_price_float)
    
    except ValueError:
        # Handle cases where inputs are not valid numbers (e.g., 'abc')
        return "Error: Invalid price or hours format."


def get_available_yachts() -> str:
    """Returns the complete list of available yachts, including location, capacity, and pricing."""
    # The yacht_seed variable is already loaded at the top of the file
    return yacht_seed_str

def get_available_themes() -> str:
    """Returns the complete list of available yachts, including location, capacity, and pricing."""
    # The yacht_seed variable is already loaded at the top of the file
    return theme_templates_str


# Function Tools
weather_tool = FunctionTool(search_weather)
yacht_tool = FunctionTool(get_available_yachts)
theme_tool = FunctionTool(get_available_themes)
price_tool = FunctionTool(get_total_price)


# --- 2. Micro-Agents ---

theme_agent = Agent(
    name="ThemeAgent",
    model=gemini_model, # Reasoning Power
    instruction="""You are ThemeAgent for yacht experiences.
                1. Input: parsed selected yacht from YachtPlanner and available themes from the tool.
                2.**Call the `get_available_themes` tool** to retrieve the list of theme templates.
                3. Select the best matching theme (by music, decor, mood, food, vibe, occasion).
                Return a JSON object:
                {
                "theme_name": string,
                "music_playlist": [{"title":string,"youtube":string|null}],
                "decor": [string],
                "mood_description": string,
                "food_and_drinks": [string],
                "recommended_timing": string,
                "vibe_tags": [string],
                "confidence": number
                }

                Rules:
                - Use provided theme templates if relevant.
                - Keep decor yacht-appropriate and short (max 6 items).
                - Provide YouTube links when possible; otherwise null.
                - Confidence 0–1.
                - Return ONLY JSON.

    """,
    tools=[theme_tool]
)


route_agent = Agent(
    name="RouteAgent",
    model=gemini_model, # Reasoning Power
    instruction=""" You are RouteAgent.
                Input: parsed selected yacht from YachtPlanner, boarding_point (if available), desired duration_hr.
                Return a JSON array (up to 3) of route options:
                [
                {
                    "route_id": string,
                    "waypoints": [string],
                    "est_distance_km": number,
                    "est_duration_hr": number,
                    "map_polyline": string|null,
                    "notes": string,
                    "suitable_for": [string]
                }
                ]

                Rules:
                - Use Google Maps Directions tool externally (agent should call tool) to compute accurate distances/durations; include est_distance_km and est_duration_hr.
                - Mark scenic notes (sunset vantage points) where applicable.
                - Return ONLY JSON array.

    """,
)

safety_agent= Agent(
    name="SafetyAgent",
    model=gemini_model, # Reasoning Power
    instruction=""" You are SafetyAgent.
                Input: selected route (one route), date (YYYY-MM-DD) and desired start_time.
                Return JSON:
                {
                "route_id": string,
                "safetyScore": number,          // 0.0 - 1.0
                "recommended_start_window": string,
                "warnings": [string],
                "required_precautions": [string],
                "confidence": number
                }

                Rules:
                - Use weather/tide tool outputs to compute safetyScore deterministically.
                - Provide concise warnings and precautions.
                - Confidence 0–1.
                - Return ONLY JSON.
    """,
    tools=[weather_tool]
)

# pricing_agent = Agent(
#     name="PricingAgent",
#     model=gemini_model, # Reasoning Power
#     instruction=""" You are PricingAgent.
#                 Input: selected yacht object, route (with est_distance_km), duration_hr, extras (if any).
#                 Return JSON:
#                 {
#                 "costBreakdown": {
#                     "base_fee": number,
#                     "fuel_est": number,
#                     "crew_fee": number,
#                     "service_charge": number,
#                     "extras": number
#                 },
#                 "totalCost": number,
#                 "budgetFit": "within_budget"|"over_budget",
#                 "upsellRecommendations": [string],
#                 "confidence": number
#                 }

#                 Rules:
#                 - Use deterministic calculations: base_fee = yacht.rate_hr * duration_hr; fuel_est = distance factor (e.g., 10% per hour or distance*rate).
#                 - Include simple, clear upsells (e.g., chef service, photographer) with rough additional cost estimates.
#                 - BudgetFit should compare provided budget_total if exists.
#                 - Confidence 0–1.
#                 - Return ONLY JSON.
#     """,
# )


evaluator_agent = Agent(
    name="evaluator",
    model=gemini_model, # Reasoning Power
    instruction="""
    You are the Senior Yacht Architect. 
    1. Check weather using the tool.
    2. Design the route based on safe tides.
    3. Generate the itinerary.
    """,
)

presentation_agent = Agent(
    name="presenter",
    model=gemini_model, # Reasoning Power
    instruction="""
    You are the Senior Yacht Architect. 
    1. Check weather using the tool.
    2. Design the route based on safe tides.
    3. Generate the itinerary.
    """,
)




# Agent Tools
theme_agent_tool = AgentTool(agent=theme_agent)
route_agent_tool = AgentTool(agent=route_agent)
safety_agent_tool = AgentTool(agent=safety_agent)
# pricing_agent_tool = AgentTool(agent=pricing_agent)
evaluator_agent_tool = AgentTool(agent=evaluator_agent)
presentation_agent_tool = AgentTool(agent=presentation_agent)


# Agent
planning_agent = Agent(
    
    name="YachtPlanner",
    model=gemini_model, # Reasoning Power
    instruction="""You are the Planning Agent.
    
                1.**Call the `get_available_yachts` tool** to retrieve the list of yachts details.
                2. Input: parsed user JSON from NeedsInterpreter and available yachts from the tool.
                3. Select the best matching yacht (by location, capacity, vibe, occasion, budget).
                4. If no exact yacht, tell user no yacht available on given budget.
                5. Then call ThemeAgen in parallel, passing the selected yacht and parsed input.
                6. Collect their JSON outputs, then **Call the `get_total_price` tool** (a function) to compute cost breakdown using selected yacht and route distance/duration.
                7. Merge into aggregated plan:
                { parsed_input, selected_yacht, theme, route_options, safety, pricing }
                8. Return aggregated JSON. Include flags: estimated (bool), selected_yacht_id, and logs of which sub-agents ran.

    """,
    tools=[yacht_tool, theme_agent_tool,  price_tool ]
    
)