import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Map GEMINI_API_KEY to GOOGLE_API_KEY if needed
if not os.environ.get("GOOGLE_API_KEY") and os.environ.get("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from orchestration.workflow import app
from agents.schemas import Incident

# Initialize a sample incident
initial_state = {
    "incident": Incident(
        incident_id="INC-404",
        severity="High",
        affected_service="AuthenticationService",
        error_message="Database connection pool exhausted",
        timestamp="2026-08-23T16:45:00Z"
    ),
    "errors": []
}

print("Running the Multi-Agent Incident Management Workflow...\n")

# Run the workflow
final_state = app.invoke(initial_state)

print("\n--- FINAL STATE ---")
print(f"Execution Status: {final_state.get('execution_status')}")
if final_state.get("errors"):
    print(f"Errors encountered: {final_state['errors']}")
else:
    print("Workflow completed successfully with NO errors!")
    if final_state.get("diagnostic_result"):
        print("\n[Diagnostic Result]")
        print(final_state["diagnostic_result"])
    if final_state.get("recommendation_result"):
        print("\n[Recommendation Result]")
        print(final_state["recommendation_result"])
