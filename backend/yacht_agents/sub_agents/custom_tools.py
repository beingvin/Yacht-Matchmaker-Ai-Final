import os
import json

# --- 1. Set path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH_1 = os.path.normpath(os.path.join(CURRENT_DIR, 'yachts_seed.json'))
DATA_PATH_2 = os.path.normpath(os.path.join(CURRENT_DIR, 'theme_templates.json'))


# --- 2. #load data from json file

# --- 2a. # load yacht seed data 
with open(DATA_PATH_1, "r") as f:
    yacht_seed = json.load(f)
    
# --- 2b. # Convert the yacht_seed dictionary/list into a JSON string
yacht_seed_str = json.dumps(yacht_seed, indent=2)    

# --- 2c. # load theme templates data 
with open(DATA_PATH_2, "r") as f:
    theme_templates = json.load(f)
    
# --- 2d. # Convert the yacht_seed dictionary/list into a JSON string
theme_templates_str = json.dumps(theme_templates, indent=2)    


# --- 3. Function Tools Setup ---


# --- 3a. Get available yacht function 
def get_available_yachts() -> str:
    """ Fetches all available yacht details from the database based on location, capacity, and vibe.
    Returns the complete list of available yachts as a JSON array for the LLM to process. """
    # The yacht_seed variable is already loaded at the top of the file
    return yacht_seed_str


# --- 3b. Get available theme function 
def get_available_themes() -> str:
    """ Fetches all available theme templates from the database.
    Returns the complete list of themes as a JSON array for the LLM to process and select from. """
    # The yacht_seed variable is already loaded at the top of the file
    return theme_templates_str


# --- 3c. Weather function
# def search_weather(location: str, date: str) -> str:
#     """    Retrieves the current and forecast weather conditions for the specified location and date. """
#     # (Mock for now - Connect to OpenMeteo later)
#     return f"Weather in {location} on {date}: Clear skies, Wind 10kn (Safe)."
    

# --- 3b. Price calculator function
def get_total_price(yacht_id: str, duration_hr: float) -> str: 
    """ Calculates the final cost for a specific yacht based on its rate_hr and the charter duration. """
    
    yacht = next((y for y in yacht_seed_str if y['id'] == yacht_id), None)
    if not yacht:
        return json.dumps({"error": f"Yacht ID {yacht_id} not found."})
    
    total_cost = yacht['rate_hr'] * duration_hr
    return json.dumps({
        "yacht_name": yacht['yacht_name'],
        "rate_per_hour": yacht['rate_hr'],
        "duration_hr": duration_hr,
        "total_charter_cost": total_cost,
        "food_included": yacht['food_included']
    })