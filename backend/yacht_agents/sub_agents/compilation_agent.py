from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from .custom_tools import get_total_price



# --- 1. # LLM model 
gemini_model = "gemini-2.0-flash"


# --- 2. # custom Tools
price_tool = FunctionTool(get_total_price)


# This agent handles the final pricing and data compilation.

# --- 3. # Compilation Agent (Sequential Step 3 )
compilation_agent = Agent(
    name="CompilationAgent",
    model=gemini_model,
     instruction=f"""
                You are the Planning Orchestrator. Your task is to compile the results from the parallel sub-agents
                and finalize the cost calculation using the `price_tool`.
                
                **User Requirements:** {{user_requirements}}
                **Yacht Match Result (JSON):** {{matched_yacht_data}}
                **Theme Result (JSON):** {{matched_theme_data}}
                
                1. Read the `yacht_match_result` to get the `id` and `duration_hr` from the original `user_requirements`.
                2. Call the `price_tool(yacht_id, duration_hr)` to calculate the final cost.
                3. Compile a single, final JSON object for the Presentation Agent containing:
                   - The original `user_requirements`.
                   - The `matched_yacht_data` (including routes).
                   - The `matched_theme_data`.
                   - The result from the `price_tool` (total cost breakdown).
                4. **STRICT OUTPUT:** Return ONLY this single, compiled JSON object.
                """,
                tools = [price_tool],
                output_key="combined_plan_data", # Saves the compiled plan
    )