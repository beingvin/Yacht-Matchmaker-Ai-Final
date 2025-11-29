⚓️ Yacht Matchmaker Multi-Agent System (ADK)

This project implements a complex yacht charter booking assistant using the Agent Development Kit (ADK) to orchestrate a sequence of specialized agents and tools for planning, matching, and safety analysis.

🚀 Setup and Execution

1. Installation and Project Setup

The following commands are used to set up the environment and create the ADK project structure named yacht_agents.

# Install the Google ADK library

# Install dependencies (if requirements.txt exists)
# pip install -r requirements.txt 

# Setup the virtual environment and create the project
python -m venv .venv
.venv\Scripts\Activate.ps1

adk create yacht_agents 




2. API Key Configuration

Set your Gemini API key in a .env file in the root directory:

echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > .env


3. Running the Agent System

A. Run with ADK Command-Line Interface (CLI)

adk run yacht_agents


B. Run with ADK Web Interface

adk web --port 8000


C. Running agent.py Directly (Development Mode)

If you are developing locally within the yacht_agents directory:

# Navigate to the project directory
cd yacht_agents 


# Activate the environment (Windows Powershell Example)
.venv\Scripts\Activate.ps1

# Execute the agent script
python agent.py


🚢 Yacht Matchmaker Hierarchy & Workflow

This system is built around a sequential pipeline that coordinates specialized agents, with a core parallel execution step for maximum efficiency.

🔥 Super Short Overview

The primary sequential flow is managed by the YachtMatchPipeline. The SafetyAgent is now executed in parallel with the matching and theming tasks.

Supervisor (User Interface) → NeedsInterpreter → PlanningAgent (Parallel Flow) → CompilationAgent → PresentationAgent

✅ Full Workflow Implementation Logic (ADK)

🔵 1. Supervisor Agent (LLM Agent)

The Supervisor is ALWAYS the interface with the user.

Responsibilities:

Understand the user message.

Detect missing requirements (location, date, start time, duration, number of guests, occasion, budget).

Ask follow-up questions if needed.

When all details are confirmed: Trigger the YachtMatchPipeline via an ADK tool call.

🔵 2. NeedsInterpreterAgent (Sequential Step 1)

Action: Called by the Supervisor after requirements are gathered.

Task: Extracts the full user brief into a clean, structured JSON object.

Output Example (JSON):

{
  "location": "goa",
  "guests": 8,
  "occasion": "birthday party",
  "duration_hr": 3,
  "vibe": ["party", "energetic"],
  "budget_total": 50000,
  "...": "..."
}


🔵 3. PlanningAgent (Parallel Agent - Sequential Step 2)

The PlanningAgent is a ParallelAgent responsible for the core planning process, executing three independent tasks simultaneously: Yacht Matching, Event Theming, and Guest Safety analysis.

Sub-Agent

Task

Tool Used

YachtMatcher

Selects the best yacht (based on capacity, location, vibe).

yacht_tool

ThemeAgent

Selects the best event theme (based on occasion and vibe).

theme_tool

SafetyAgent

Fetches the weather via weather_tool and generates 5 mandatory, context-aware safety tips focused on the guest.

weather_tool

🔵 4. CompilationAgent (Sequential Step 3 - Pricing)

Task: Gathers all previous results and performs the final pricing calculation.

Logic:

Extracts yacht_id and duration_hr.

Calls the price_tool(yacht_id, duration_hr).

Compiles all data (Requirements, Yacht, Theme, Safety, and Pricing) into a single, comprehensive final JSON plan.

🔵 5. PresentationAgent (Sequential Step 4)

Input: The comprehensive final JSON plan and the Safety Summary (which is retrieved from the PlanningAgent's output).

Task: Transforms the raw planning data into a professional, engaging, and charismatic final yacht charter itinerary text.

🔵 6. Supervisor Returns Final Output

The Supervisor takes the final itinerary text from the PresentationAgent and sends the complete, formatted plan back to the user.