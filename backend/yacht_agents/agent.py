import os
import sys
import asyncio
from dotenv import load_dotenv

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import AgentTool
# from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner, Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.genai import types 
# CRITICAL FIX: PATH CONFIGURATION FOR MANUAL EXECUTION
# This block dynamically adds the current directory (yacht_agents) to the 
# Python path, allowing the absolute imports in step 2 to succeed when 
# running 'python agent.py' directly.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    # Insert the 'yacht_agents' directory itself into the Python path
    sys.path.insert(0, current_dir)

from sub_agents.needs_interpreter_agent import needs_interpreter_agent
from sub_agents.planning_agents import planning_agent
from sub_agents.compilation_agent import compilation_agent
from sub_agents.presentation_agent import presentation_agent

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)


# --- 1. # load .env (optional; or set GOOGLE_API_KEY in env)
load_dotenv()





# --- 2. # Example using a local SQLite file:
DB_FILE_NAME = "my_agent_data.db"
db_path = os.path.abspath(DB_FILE_NAME)
db_url = f"sqlite+aiosqlite:///{db_path}"
session_service = DatabaseSessionService(db_url=db_url)


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
    instruction="""You are the Supervisor Agent for the {{company_name}}. 
                
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


# --- 7. run the async call in a sync script
async def main():
    
    # --- 8a. Runner with single chat execution 
    # runner = InMemoryRunner(agent=root_agent)
    # print("✅ Runner created.")
    
     # response = await runner.run_debug(
    #     "i need yacht for new year party on 31/12/2025 in goa , budget 30k and we are 5 people"
    # )
    
    # --- 8b. # Create a simple session to examine its properties
    # session_service = InMemorySessionService()
    

    # --- 8c. # Create a new user session and inspect it
    
    PERSISTENCE_TEST_USER_ID = "vin"
    PERSISTENCE_TEST_SESSION_ID = "47db0c68-0092-4167-835c-dd6039475c3c"
    

    new_session = await session_service.create_session(
    app_name="yacht_matchmaker",
    user_id="user_001",
    # user_id=PERSISTENCE_TEST_USER_ID,  # <-- use the retrive saved user id 
    state={"company_name": "Livin Charters", } # State can be initialized
    )
    
    
    # --- 8d. # Display session info (useful for debugging)
    print(f"--- Examining Session Properties ---")
    print(f"ID (`id`):                {new_session.id}")
    print(f"Application Name (`app_name`): {new_session.app_name}")
    print(f"User ID (`user_id`):         {new_session.user_id}")
    print(f"State (`state`):           {new_session.state}") # Note: Only shows initial state here
    print(f"Events (`events`):         {new_session.events}") # Initially empty
    print(f"Last Update (`last_update_time`): {new_session.last_update_time:.2f}")
    print(f"---------------------------------")
    
    
    # --- 8e. # Creat Runner
    runner = Runner(agent=root_agent, app_name=new_session.app_name, session_service=session_service)
         
    # --- 8f. # Helper: send a message through the agent pipeline
    async def ask(message: str) -> str:
        # Convert plain text into ADK’s Content/Part format
        content = types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )

         # run_async streams events; we collect the final response
        final_text = ""
        async for event in runner.run_async(
            user_id=new_session.user_id,
            session_id=new_session.id,   # <-- use the for new session id
            # session_id=PERSISTENCE_TEST_SESSION_ID,   # <-- use the retrive saved session id 
            new_message=content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                # simplest: grab the first text part
                final_text = event.content.parts[0].text
        return final_text

    user_message = [  "I need a yacht for new year party on 31/12/2025 in Goa,budget 30k and we are 5 people", "Hello! What is my name?", "What is your company name?" ]
    
    # Two separate messages, same session → agent remembers context
    response_1 = await ask( user_message[0])
    # response_2 = await ask(user_message[1])
    response_3 = await ask(user_message[2])
    

    # Combine for the demo output
    response = (
    f"USER : {user_message[0]}\n"
    f"AGENT : {response_1}\n\n"
    # f"USER : {user_message[1]}\n"
    # f"AGENT : {response_2}\n\n"
    f"USER : {user_message[2]}\n"
    f"AGENT : {response_3}"
)
     # --- 8g.  Clean up (optional for this example)
    # temp_service = await session_service.delete_session(app_name=new_session.app_name,
    # user_id=new_session.user_id, session_id=PERSISTENCE_TEST_SESSION_ID)
    # print("The final status of temp_service - ", temp_service)
    
    # --- 8h. print response 
    print(response)
    
    
    
    
    return response
    

response = asyncio.run(main())



# --- 8. Interactive Execution Loop ---
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


