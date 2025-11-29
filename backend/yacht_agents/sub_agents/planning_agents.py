from google.adk.agents import Agent, ParallelAgent
from google.adk.tools import AgentTool ,FunctionTool
from .custom_tools import search_weather, get_available_yachts, get_available_themes



# --- 1. # Set LLM model 
gemini_model = "gemini-2.0-flash"
    


# --- 1. # custom Tools
weather_tool = FunctionTool(search_weather)
yacht_tool = FunctionTool(get_available_yachts)
theme_tool = FunctionTool(get_available_themes)


# --- 3. Parallel Sub-Agents ---

# 3a. Yacht Matcher Agent (Parallel Sub-Agent 1)
yacht_matcher_agent = Agent(
    name="yachtMatcher",
    model=gemini_model, # Reasoning Power
    instruction=f"""
                You are the Yacht Matching Specialist. Your task is to select the single best yacht
                from the `yacht_tool` data that meets the user's requirements.
                
                **User Requirements (Input):** {{user_requirements}}
                
                1. Call the `yacht_tool` to get the list of available yachts.
                2. Filter and score the yachts based on the `location`, `guests` (max_capacity), `occasion`, and `vibe`.
                3. Select the yacht that is the best overall match.
                4. Output ONLY the complete, unfiltered JSON object of the single selected yacht, ensuring 
                   the `routes` array is included in the output.
                """,
    tools=[yacht_tool],
    # input_key="user_requirements", # Explicitly consumes the JSON
    output_key="matched_yacht_data" # Saves the single yacht JSON to state
)

# 3b. Theme Agent (Parallel Sub-Agent 2)
theme_agent = Agent(
    name="ThemeAgent",
    model=gemini_model, # Reasoning Power
    instruction=f"""
                You are the Event Theme Designer. Your task is to select the single best theme 
                template from the `theme_tool` data that meets the user's requirements.
                
                **User Requirements (Input):** {{user_requirements}}
                
                1. Call the `theme_tool` to get the list of available themes.
                2. Select the theme that best matches the user's `occasion` and `vibe`.
                3. Output ONLY the complete, unfiltered JSON object of the single selected theme.
                """,
    tools=[theme_tool],
    # input_key="user_requirements", # Explicitly consumes the JSON
    output_key="matched_theme_data" # Saves the single theme JSON to state
)



# 3c. Safety Agent (Parallel Sub-Agent 3 )
safety_agent= Agent(
    name="SafetyAgent",
    model=gemini_model, # Reasoning Power
       instruction=f"""
                You are the Safety Officer. Your task is to check the weather and provide essential safety advice.
                
                **User Requirements (Input):** {{user_requirements}}
                
                1. Use the `weather_tool` with the `location` and `date` from the requirements to get the forecast.
                2. Based on the **{{user_requirements}}** (especially time) and the **weather forecast**, compile a list of **5 mandatory, key safety tips** that are highly relevant to the guest's safety, focusing on actions the Guest must take (e.g., adapting tips for daytime/nighttime, weather, and general safety protocols like following crew instructions, using handrails, securing items).
                3. Your final response MUST be a single, structured summary. Do not use JSON or markdown headings. Use the following two section titles exactly:
                   - Weather Forecast
                   - Mandatory Safety Tips for the Guest
                """,
    # input_key="user_requirements", # Explicitly consumes the JSON from NeedsInterpreter
    output_key="safety_summary", # Saves summary to state
    tools=[weather_tool]
)


# Agent Tools
# yacht_matcher_tool = AgentTool(agent=yacht_matcher_agent)
# theme_agent_tool = AgentTool(agent=theme_agent)
# route_agent_tool = AgentTool(agent=route_agent)
# safety_agent_tool = AgentTool(agent=safety_agent)
# pricing_agent_tool = AgentTool(agent=pricing_agent)


# --- 3. # Planning Agent (Parallel Container, Sequential Step 2)
planning_agent = ParallelAgent(
    name="PlanningAgent",
    sub_agents=[yacht_matcher_agent, theme_agent, safety_agent ]
)


