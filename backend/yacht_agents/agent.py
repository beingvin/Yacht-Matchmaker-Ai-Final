# agent.py — corrected for sync invocation of async runner
import asyncio
from dotenv import load_dotenv

from google.adk.agents import Agent, SequentialAgent
# from google.adk.models.google_llm import Gemini
# from google.adk.sessions import DatabaseSessionService
from google.adk.runners import InMemoryRunner
from .sub_agents.needs_interpreter_agent import needs_interpreter_agent
from .sub_agents.planning_agents import planning_agent
from .sub_agents.compilation_agent import compilation_agent
from .sub_agents.presentation_agent import presentation_agent
from google.adk.tools import AgentTool

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)


# --- 1. # load .env (optional; or set GOOGLE_API_KEY in env)
load_dotenv()


# --- 2. # Example using a local SQLite file:
# db_url = "sqlite:///./my_agent_data.db"
# session_service = DatabaseSessionService(db_url=db_url)


# --- 3. # Set LLM model 
gemini_model = "gemini-2.0-flash"


# --- 4. # This pipeline runs the full automation Sequential Workflow : Needs -> Plan -> Present

sequential_agent = SequentialAgent(
    name="planningPipeline",
    sub_agents=[needs_interpreter_agent, planning_agent, compilation_agent, presentation_agent],
)


# --- 5. # Agentic Tools
sequential_agent_tool = AgentTool( agent=sequential_agent )


# --- 6. Supervisor Agent (Root Agent) ---

root_agent = Agent(
    name="Supervisor",
    model=gemini_model,
    instruction="""You are the Supervisor Agent for the Yacht Matchmaker AI system. 
                
                **Primary Role:** Be the user-facing coordinator. **Do not run the pipeline until you have confirmed ALL required booking details with the user.**
                
                **Required Details (Must be Explicitly Confirmed):**
                - **location** (e.g., Mumbai or Goa)
                - **date** (YYYY-MM-DD) or date range
                - **start time** (HH:MM) or time window
                - **duration** in hours (numeric)
                - **number of guests** (numeric)
                - **occasion** (e.g., bachelor, family, corporate)
                - **budget** (numeric) or budget range
                
                **Behavior Rules:**
                1.  **If any required detail is missing** or ambiguous from the conversation history, ask a **single clear follow-up question** requesting the missing detail(s). Wait for the user's response and re-check.
                2.  **Do NOT call any tools while required details are missing.**
                3.  **When ALL required details are confirmed**, call the `sequential_agent_tool` tool. Your input to the tool must be the **FULL combined user brief** summarizing all confirmed details.
                4.  The pipeline will return the final itinerary. Review it, make any necessary final formatting changes, and present the complete, charismatic itinerary to the user.
                
                **Tool Logic:**
                * `sequential_agent_tool` tool (Sequential flow: NeedsInterpreter → PlanningAgent → PresentationAgent).
                * The PlanningAgent internally handles the parallel flow (YachtSelector → Theme → Route → Safety → Pricing).
                """,
    tools=[sequential_agent_tool]
)

# --- 7. Interactive Execution Loop ---

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

# --- 8. Runner 
# runner = InMemoryRunner(agent=root_agent)
# print("✅ Runner created.")

# --- 9. run the async call in a sync script
# async def main():
#     response = await runner.run_debug(
#         "i need yacht for new year party on 31/12/2025 in goa , budget 30k and we are 5 people"
#     )
#     return response

# response = asyncio.run(main())

