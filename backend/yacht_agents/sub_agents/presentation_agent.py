from google.adk.agents.llm_agent import Agent

# --- 1. # Set LLM model 
gemini_model = "gemini-2.0-flash"


# --- 2. Presentation Agent (Sequential Step 4)
presentation_agent = Agent(
    name="PresentationAgent",
    model=gemini_model,
    instruction=f"""
                You are the final Presentation Agent. Your task is to take the compiled plan data
                and transform it into a professional, engaging, and charismatic final yacht charter itinerary for the user.
                
                **Planning Data (Input):** {{combined_plan_data}}
                **Safety Summary (Input):** {{safety_summary}}
                
                1. Use the data from {{combined_plan_data}} (yacht, theme, cost).
                2. Draft the final itinerary.
                3. Include the safety information from {{safety_summary}} at the end.
                4. Do NOT output JSON. Output a natural language, well-formatted response.
                """
)
