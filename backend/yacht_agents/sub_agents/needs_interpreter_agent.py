from google.adk.agents.llm_agent import Agent


gemini_model = "gemini-2.0-flash"

'''Interpreter Agent (Sequential Start)
This agent is the User Interface Parser.

Role: Extracts structured data from free-form user text.

Input: "4 adults, bachelor party in Goa, sunset cruise, budget 45k."

Output (Pydantic Manifest): {location: Goa, size: 4, occasion: party, budget: 45000}

Tools: LLM (Gemini 2.5 Lite), Context Compaction (ADK Memory).'''

needs_interpreter_agent = Agent(
    name="NeedsInterpreter",
    model=gemini_model, # Speed
     instruction="""
                You are the Needs Interpreter Agent for a yacht booking system.
                Your job is to read the user's text and extract structured booking details.

                Return ONLY a JSON object with:
                location, date, start_time, duration_hr, guests,
                occasion, vibe, budget_total, special_requirements, confidence.

                Rules:
                - If the user does not mention something, set it to null.
                - Use lowercase for location, occasion, vibe.
                - Vibe must be an array of strings.
                - Confidence must be 0–1.
                - Output ONLY valid JSON.
                """
)