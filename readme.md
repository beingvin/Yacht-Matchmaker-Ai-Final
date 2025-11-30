# ⚓️ Yacht Matchmaker — Multi-Agent System (ADK Powered)



A multi-agent yacht charter planning system built using the **Agent Development Kit (ADK)**.
The project handles everything from user intent parsing to yacht matching, theming, safety checks, pricing, and final itinerary generation.

---

# 🌊 Overview

The system coordinates a chain of specialized agents:

```
Supervisor → NeedsInterpreter → PlanningAgent (Parallel Tasks)
           → CompilationAgent → PresentationAgent → User
```

Each stage performs a specific function, ultimately producing a professional yacht charter itinerary.

---

# 📦 Features

* Multi-agent reasoning pipeline
* Parallel processing for matching, theming, and safety
* Weather-aware safety evaluation
* Pricing engine
* Professional itinerary generation
* Web UI, CLI support, and direct Python execution
* JSON-based data templates for yachts & themes

---

# 🚀 Getting Started

## 1. 🔧 Installation & Environment Setup

```bash
# Install the Google ADK library

# Install dependencies (if requirements.txt exists)
# pip install -r requirements.txt 

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Create ADK project
adk create yacht_agents
```

---

## 2. 🔑 API Key Configuration

```bash
echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > .env
```

---

## 3. ▶️ Running the System

### A. Run from ADK CLI

```bash
adk run yacht_agents
```

### B. Run ADK Web Interface

```bash
adk web --port 8000
```

### C. Run Python agent directly

```bash
cd yacht_agents
.venv\Scripts\Activate.ps1
python agent.py
```

---

# 📂 Project Structure

```plaintext
yacht-matchmaker/
├── backend/
│   ├── .env
│   ├── requirements.txt
│   ├── readme.md
│   ├── agent.py
│   ├── yacht_agents/
│   │   ├── init.py
│   │   ├── yachts_seed.json
│   │   ├── theme_templates.json
│   │   ├── compilation_agent.py
│   │   ├── custom_tools.py
│   │   ├── evaluator_agent.py
│   │   ├── needs_interpreter_agent.py
│   │   ├── planning_agents.py
│   │   ├── presentation_agent.py
│   │   └── sub_agents/
│   │       ├── init.py
│   │       └── (additional sub-agents here)
│   └── pycache/
└── .gitignore
```

---

# 🧠 Architecture Diagram

```
User
 ↓
Supervisor Agent
 ↓
NeedsInterpreterAgent
 ↓
PlanningAgent ───────────────────────────┐
 ├─ YachtMatcher  (yacht_tool)           │  (Parallel Execution)
 ├─ ThemeAgent   (theme_tool)            │
 └─ SafetyAgent  (weather_tool) ─────────┘
 ↓
CompilationAgent (pricing, aggregation)
 ↓
PresentationAgent (itinerary text)
 ↓
Final Output
```

---

# 🌀 Full Workflow (Original Content, Preserved)

## 🔵 1. Supervisor Agent (User-Facing)

Responsibilities:

* Understand user inputs
* Detect missing requirements
* Ask follow-up questions
* Trigger the YachtMatchPipeline

---

## 🔵 2. NeedsInterpreterAgent (Step 1)

Transforms user details into structured JSON:

```json
{
  "location": "goa",
  "guests": 8,
  "occasion": "birthday party",
  "duration_hr": 3,
  "vibe": ["party", "energetic"],
  "budget_total": 50000
}
```

---

## 🔵 3. PlanningAgent (Parallel Execution)
```
| Sub-Agent    | Task                                       | Tool         |
| ------------ | ------------------------------------------ | ------------ |
| YachtMatcher | Selects best yacht                         | yacht_tool   |
| ThemeAgent   | Chooses theme based on vibe                | theme_tool   |
| SafetyAgent  | Fetches weather + generates safety summary | weather_tool |
```
---

## 🔵 4. CompilationAgent

* Combines all data
* Calls `price_tool(yacht_id, duration_hr)`
* Produces a complete JSON plan

---

## 🔵 5. PresentationAgent

* Converts structured plan + safety info into a styled itinerary

---

## 🔵 6. Final Delivery

Supervisor sends the final polished itinerary to the user.

---

# 📘 Example Output

<details>
<summary><strong>Click to view sample itinerary</strong></summary>

```
✨ Your Goa Yacht Party Plan is Ready!

Guests: 8  
Date: Dec 31  
Occasion: Birthday Party  
Theme: Energetic Neon Night  
Yacht: Sea Breeze (capacity 10)  
Safety Tips: Weather clear; maintain distance from railings, etc.

Pricing: ₹50,000 all-inclusive  
```

</details>

---

# 🛠 Tech Stack

* **Python 3.10+**
* **Google ADK**
* **Gemini API**
* JSON-based assets
* Async event-driven agent workflow

---
