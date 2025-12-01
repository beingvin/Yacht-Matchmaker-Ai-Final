import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware # Added CORS

# --- ADK IMPORTS ---
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import AgentTool
from google.adk.runners import InMemoryRunner, Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types 

# --- AGENT COMPONENT IMPORTS ---
# Ensure the path setup works for these imports
current_dir = os.path.dirname(os.path.abspath(__file__))
# Assumes sub_agents folder is one level up relative to where agent.py was
sys.path.insert(0, current_dir) 

try:
    from sub_agents.needs_interpreter_agent import needs_interpreter_agent
    from sub_agents.planning_agents import planning_agent
    from sub_agents.compilation_agent import compilation_agent
    from sub_agents.presentation_agent import presentation_agent
except ImportError:
    # Fallback/Debug if imports fail in the server context
    print("Error: Could not import sub_agents. Ensure sub_agents directory is on the path.")
    raise

import logging
logging.basicConfig(level=logging.ERROR)
# ----------------------------------------------------------------------

# --- GLOBAL VARIABLES FOR AGENT/DB STATE ---
session_service: DatabaseSessionService = None
root_agent: Agent = None


# --- FASTAPI SETUP ---
app = FastAPI(title="Yacht Matchmaker Agent API")


# CORS Middleware for local development between ports 3000 (Next.js) and 8000 (FastAPI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.31.51:3000/"], # Allow Next.js development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the expected request body structure
class ChatRequest(BaseModel):
    user_id: str
    message: str

# ----------------------------------------------------------------------
# 1. AGENT INITIALIZATION LOGIC (Called on Server Startup)
# ----------------------------------------------------------------------

async def initialize_adk_components():
    """Initializes the ADK Session Service, Agents, and Runner."""
    global session_service, root_agent, agent_runner

    load_dotenv()
    gemini_model = "gemini-2.0-flash"

    # Database Setup (Async)
    DB_FILE_NAME = "my_agent_data.db"
    db_path = os.path.abspath(DB_FILE_NAME)
    # Crucial for async SQLite: sqlite+aiosqlite
    db_url = f"sqlite+aiosqlite:///{db_path}" 

    print(f"Initializing DatabaseSessionService with URL: {db_url}")
    session_service = DatabaseSessionService(db_url=db_url)


    # The Sequential Agent Pipeline
    sequential_agent = SequentialAgent(
        name="planningPipeline",
        sub_agents=[needs_interpreter_agent, planning_agent, compilation_agent, presentation_agent],
    )
    sequential_agent_tool = AgentTool(agent=sequential_agent)

    # Supervisor Agent (Root Agent)
    root_agent = Agent(
        name="Supervisor",
        model=gemini_model,
        instruction="""You are the Supervisor Agent for the yacht company name. 
                
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
    
   


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager for application startup and shutdown events."""
    await initialize_adk_components()
    yield
    # Cleanup logic (optional, but good practice)
    print("Shutting down application.")

# Attach the lifespan context manager to the FastAPI app
app.router.lifespan_context = lifespan
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# 2. CHAT API ENDPOINT
# ----------------------------------------------------------------------

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Handles incoming chat requests from the frontend, ensuring session persistence via user_id.
    get_session to retrieve the existing, latest session for the user,
    or create a new one if none exists (usually only on the very first message).
    """
    # Safety check for initialization failure
    # if not agent_runner or not session_service: 
    #     raise HTTPException(status_code=503, detail="Agent service is not initialized. Check server startup logs.")


    try:
        # 1. Load the existing session for this user and app, or create a new one.
        
        # Try to find the latest active session for this user and app
        session_response = await session_service.list_sessions(
            app_name="yacht_matchmaker",
            user_id=request.user_id,
           
        )
        
        session_list = session_response.sessions 
        
        session = session_list[0] if session_list else None
        
        if not session:
            # If no session exists, create a new one (This happens only once per new user/browser)
            session = await session_service.create_session(
                app_name="yacht_matchmaker",
                user_id=request.user_id,
                state={"company_name": "Livin Charters"} 
            )

        
         # 1. Initialize the Runner
        runner = Runner(agent=root_agent, app_name=session.app_name, session_service=session_service)

        
        # 2. Prepare Message Content
        content = types.Content(role="user", parts=[types.Part(text=request.message)])
        
        final_text = ""
        
        # 3. Run the Agent Pipeline
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = event.content.parts[0].text
        
        # 4. Return the Agent's response
        return {
            "response": final_text,
            "session_id": session.id,
            "user_id": session.user_id
        }

    except Exception as e:
        print(f"An error occurred during chat processing: {e}")
        # Return a 500 status code with a helpful error message
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

# ----------------------------------------------------------------------
# 3. RUN THE SERVER (Instructions for the user)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # You run this server using uvicorn, which handles the HTTP protocol
    # Command to run: uvicorn server:app --reload --port 8000
    # The port 8000 is used by convention for local development APIs
    print("\n-------------------------------------------------")
    print("To start the server, run the following command:")
    print("uvicorn server:app --reload --port 8000")
    print("-------------------------------------------------\n")

    # We manually start uvicorn here just for the file to be self-contained and runnable
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)