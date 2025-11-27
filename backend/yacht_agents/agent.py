# agent.py — corrected for sync invocation of async runner
import asyncio
from dotenv import load_dotenv

from google.adk.agents.llm_agent import Agent
# from google.adk.models.google_llm import Gemini
# from google.adk.sessions import DatabaseSessionService
from google.adk.runners import InMemoryRunner
from .sub_agents.needs_interpreter_agent import needs_interpreter_agent
from .sub_agents.planning_agent import planning_agent
from google.adk.tools import AgentTool, FunctionTool


import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)



# load .env (optional; or set GOOGLE_API_KEY in env)
load_dotenv()



# Example using a local SQLite file:
# db_url = "sqlite:///./my_agent_data.db"
# session_service = DatabaseSessionService(db_url=db_url)



gemini_model = "gemini-2.0-flash"

# --- 3. Supervisor (Router) ---

needs_agent_tool = AgentTool(agent=needs_interpreter_agent)
planning_agent_tool = AgentTool(agent=planning_agent)



root_agent = Agent(
    name="Supervisor",
    model=gemini_model,
    instruction="""You are the Supervisor Agent for the Yacht Matchmaker AI system.

                Your responsibilities:
                1. First confirm the location ( mumbai or goa ), date, time, duration, number of guests, occasion, budget, and any special requirements from the user and coordinate all with sub agents.
                2. ALWAYS call needs_agent_tool first to convert the user input into structured JSON.
                3. After interpretation, call the planning_agent_tool to get the below plan:
                - ThemeAgent: for theme, music, decor, vibe
                - RouteAgent: for route options and timing
                - SafetyAgent: for weather, tides, safetyScore
                - PricingAgent: for cost breakdown and budgetFit
                - EvaluatorAgent: overall feasibility scoring
                - PresentationAgent: to generate Google Slides or formatted itinerary text

                Core Workflow:
                1. User input → NeedsInterpreter → parsed JSON.
                2. Based on parsed JSON:
                - Call planning_agent_tool
                3. Collect all agent outputs.
                4. Call EvaluatorAgent to validate feasibility and compute scores:
                - safety score
                - vibe match score
                - budget match score
                5. If the user said “generate slides”, or “presentation”, or “make deck”, call PresentationAgent.
                6. Otherwise, Return a clean itinerary summary OR a slide deck link (if PresentationAgent invoked).

                Rules:
                - Do NOT interpret user text yourself; always rely on NeedsInterpreter.
                - Use other agents only after NeedsInterpreter output is available.
                - ALWAYS wait for each agent’s output before calling the next.
                - Combine outputs into a clear final plan unless PresentationAgent is requested.
                - Include: yacht details, theme, route, safety window, pricing, and evaluator feedback.
                - Keep your final message concise unless the user asks for full detail.
                - Maintain observability: briefly state which agents were used in this run.

                Your output to the user should be:
                - A human-friendly itinerary OR
                - A link/confirmation from PresentationAgent if slides were generated.
                """,
     tools=[needs_agent_tool, planning_agent_tool]
)

# --- 4. Interactive Execution Loop ---
# if __name__ == "__main__":
#     # Create the runner once (this holds the agent instance)
#     runner = InMemoryRunner(agent=root_agent)
    
#     print("--------------------------------------------------")
#     print("⚓ Yacht Matchmaker Online. Type 'exit' to quit.")
#     print("--------------------------------------------------")

#     async def chat_loop():
#         # Ideally, we maintain a session ID if the Runner supports it, 
#         # but for local testing, many runners keep internal state or we pass history.
#         # If the agent 'forgets' context, we can add explicit session handling later.
        
#         while True:
#             try:
#                 user_input = input("\nYou: ").strip()
                
#                 if not user_input:
#                     continue
                    
#                 if user_input.lower() in ["exit", "quit"]:
#                     print("👋 Fair winds! Closing session.")
#                     break
                
#                 print("Thinking... ⏳")
                
#                 # Run the agent
#                 result = await runner.run_debug(user_input)
                
#                 # Print response
#                 # print(f"🤖 Agent: {result.text}")
                
#             except KeyboardInterrupt:
#                 print("\n👋 Force Quit.")
#                 break
#             except Exception as e:
#                 print(f"❌ Error: {e}")

#     # Run the loop
#     asyncio.run(chat_loop())


# runner = InMemoryRunner(agent=root_agent)
# print("✅ Runner created.")

# # run the async call in a sync script
# async def main():
#     response = await runner.run_debug(
#         "i need yacht for new year party on 31/12/2025 in goa , budget 30k and we are 5 people"
#     )
#     return response

# response = asyncio.run(main())

