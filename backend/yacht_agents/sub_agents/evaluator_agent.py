from google.adk.agents.llm_agent import Agent


# --- 1. # Set LLM model 
gemini_model = "gemini-2.0-flash"


# --- 2. # evaluator_agent = Agent(
#     name="evaluator",
#     model=gemini_model, # Reasoning Power
#     instruction="""
#     You are the Senior Yacht Architect. 
#     1. Check weather using the tool.
#     2. Design the route based on safe tides.
#     3. Generate the itinerary.
#     """,
# )
