# agent.py — corrected for sync invocation of async runner
import asyncio
from dotenv import load_dotenv

from google.adk.agents.llm_agent import Agent
# from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from sub_agents.web_agent import websearch_agent
from google.adk.tools import AgentTool, FunctionTool


# load .env (optional; or set GOOGLE_API_KEY in env)
load_dotenv()

gemini_model = "gemini-2.0-flash"

# --- 1. Tools Setup ---
def search_weather(location: str, date: str) -> str:
    """Fetches weather forecast for maritime safety."""
    # (Mock for now - Connect to OpenMeteo later)
    return f"Weather in {location} on {date}: Clear skies, Wind 10kn (Safe)."

# weather_tool = Tool.from_function(search_weather
weather_tool = FunctionTool(search_weather)

# --- 2. Micro-Agents ---
needs_agent = Agent(
    name="NeedsInterpreter",
    model=gemini_model, # Speed
    instruction="Extract location, pax, and budget. Return JSON."
)

planning_agent = Agent(
    name="YachtPlanner",
    model=gemini_model, # Reasoning Power
    instruction="""
    You are the Senior Yacht Architect. 
    1. Check weather using the tool.
    2. Design the route based on safe tides.
    3. Generate the itinerary.
    """,
    tools=[weather_tool]
)


# --- 3. Supervisor (Router) ---

needs_agent_tool = AgentTool(agent=needs_agent)
planning_agent_tool = AgentTool(agent=planning_agent)

root_agent = Agent(
    name="Supervisor",
    model=gemini_model,
    instruction="Route user to 'NeedsInterpreter' first, then 'YachtPlanner' once intent is clear.",
    tools=[needs_agent_tool, planning_agent_tool]
)

# --- 4. Interactive Execution Loop ---
if __name__ == "__main__":
    # Create the runner once (this holds the agent instance)
    runner = InMemoryRunner(agent=root_agent)
    
    print("--------------------------------------------------")
    print("⚓ Yacht Matchmaker Online. Type 'exit' to quit.")
    print("--------------------------------------------------")

    async def chat_loop():
        # Ideally, we maintain a session ID if the Runner supports it, 
        # but for local testing, many runners keep internal state or we pass history.
        # If the agent 'forgets' context, we can add explicit session handling later.
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ["exit", "quit"]:
                    print("👋 Fair winds! Closing session.")
                    break
                
                print("Thinking... ⏳")
                
                # Run the agent
                result = await runner.run_debug(user_input)
                
                # Print response
                # print(f"🤖 Agent: {result.text}")
                
            except KeyboardInterrupt:
                print("\n👋 Force Quit.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    # Run the loop
    asyncio.run(chat_loop())


# runner = InMemoryRunner(agent=supervisor)
# print("✅ Runner created.")

# # run the async call in a sync script
# async def main():
#     response = await runner.run_debug(
#         "i need yacht for new year party on 31/12/2025 in goa , budget 30k and we are 5 people"
#     )
#     return response

# response = asyncio.run(main())

