import os
import json
from dotenv import load_dotenv

# Gracefully import anthropic to allow running in mock mode even if not installed
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class IncidentClassificationAgent:
    """
    An LLM-based classification agent that analyzes logs and classifies incidents
    into predefined categories to match corresponding standard operating procedures (SOPs).
    Uses the Anthropic tool use API to enforce structured JSON responses.
    """
    def __init__(self, model_name: str = "claude-3-haiku-20240307"):
        load_dotenv()
        self.model_name = model_name
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Check if we need to run in mock mode
        self.is_mock_mode = False
        if not ANTHROPIC_AVAILABLE:
            print("[INFO] 'anthropic' package not installed. Running in MOCK mode.")
            self.is_mock_mode = True
        elif not self.api_key or self.api_key.startswith("your_"):
            print("[INFO] ANTHROPIC_API_KEY is missing or set to placeholder. Running in MOCK mode.")
            self.is_mock_mode = True

    def classify_incident(self, incident: dict) -> dict:
        """
        Classifies an incident dictionary into a structured category, severity, and service.
        Guarantees structured outputs using Anthropic's tool-calling API.
        """
        raw_log = incident.get("raw_log_snippet", "")
        context = incident.get("surrounding_context", "")
        timestamp = incident.get("timestamp", "")
        source = incident.get("source_system", "Unknown")

        # --- MOCK MODE FALLBACK ---
        if self.is_mock_mode:
            log_lower = raw_log.lower()
            affected_service = source if source and source != "Unknown" else "HDFS-Service"
            
            # Determine category based on keywords
            if "exception while serving" in log_lower or "block" in log_lower:
                category = "disk_full"
                severity = "medium"
                reasoning = "Mock LLM: HDFS logs show a block replication exception, indicating a potential storage failure on the DataNode."
            elif "timeout" in log_lower:
                category = "db_timeout"
                severity = "medium"
                reasoning = "Mock LLM: Log signature matches a network connection timeout, which correlates with DB response delays."
            elif "outofmemory" in log_lower or "oom" in log_lower:
                category = "memory_leak"
                severity = "high"
                reasoning = "Mock LLM: JVM process terminated due to OutOfMemory exception, indicating memory leakage."
            elif "cpu" in log_lower or "overload" in log_lower:
                category = "high_cpu"
                severity = "medium"
                reasoning = "Mock LLM: High CPU threshold exceeded by active threads."
            elif "crash" in log_lower or "restart" in log_lower:
                category = "crash_loop"
                severity = "high"
                reasoning = "Mock LLM: Process exited repeatedly, triggering restart loop."
            else:
                category = "other"
                severity = "low"
                reasoning = "Mock LLM: Log entries do not match any standard incident signatures."

            return {
                "severity": severity,
                "category": category,
                "affected_service": affected_service,
                "reasoning": reasoning,
                "manual_review": False
            }

        # --- REAL ANTHROPIC API CALL ---
        # Define the forced tool/schema for structured output
        tools = [
            {
                "name": "classify_incident_tool",
                "description": "Classifies the system incident based on logs and surrounding context.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "Estimated impact level: high (service outage), medium (degradation), low (warning)."
                        },
                        "category": {
                            "type": "string",
                            "enum": ["high_cpu", "db_timeout", "disk_full", "crash_loop", "api_5xx", "memory_leak", "other"],
                            "description": "Predefined category matching standard operating procedures."
                        },
                        "affected_service": {
                            "type": "string",
                            "description": "Identify the affected system or component (e.g., dfs.DataNode, auth-service, pgsql-db)."
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Brief step-by-step logic detailing why this classification was selected."
                        }
                    },
                    "required": ["severity", "category", "affected_service", "reasoning"]
                }
            }
        ]

        system_prompt = (
            "You are an expert IT Incident Classifier. You analyze logs and context window metrics "
            "and classify the incidents. Your goal is to map them to one of our standard operating "
            "procedures (SOPs) or categorize them as 'other'."
        )

        user_content = f"""
        Please classify the following incident:
        
        Timestamp: {timestamp}
        Source Component: {source}
        Raw Log Line: {raw_log}
        
        Surrounding context (prior and subsequent logs):
        {context}
        """

        # Call API with retry logic (once)
        for attempt in range(2):
            try:
                client = anthropic.Anthropic(api_key=self.api_key)
                
                response = client.messages.create(
                    model=self.model_name,
                    max_tokens=1000,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_content}
                    ],
                    tools=tools,
                    tool_choice={"type": "tool", "name": "classify_incident_tool"}
                )

                # Extract parameters from the forced tool call
                tool_use = next(block for block in response.content if block.type == "tool_use")
                result = tool_use.input
                result["manual_review"] = False
                return result

            except Exception as e:
                print(f"[WARNING] API attempt {attempt + 1} failed: {e}")
                if attempt == 0:
                    print("Retrying API request...")
                    continue

        # Fallback response if all API attempts fail
        return {
            "severity": "medium",
            "category": "other",
            "affected_service": source if source else "Unknown",
            "reasoning": "LLM call failed or timed out. Defaulted classification rules applied.",
            "manual_review": True
        }

if __name__ == "__main__":
    import sys
    # Import monitoring agent to retrieve real log examples
    # Add project root to path if needed
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agents.monitoring_agent import LogMonitoringAgent
    
    # 1. Fetch some sample incidents from the monitoring agent
    log_file = os.path.join("data", "raw_logs", "HDFS_2k.log")
    if not os.path.exists(log_file):
        print(f"Error: Could not find HDFS log file at '{log_file}'. Run download_loghub.py first.")
        sys.exit(1)

    print("Fetching incidents from logs...")
    monitoring_agent = LogMonitoringAgent()
    incidents = monitoring_agent.get_incidents(log_file)
    
    if not incidents:
        print("No incidents found to test classification on.")
        sys.exit(0)

    # 2. Select 5 test incidents
    test_incidents = incidents[:5]
    print(f"Selected {len(test_incidents)} incidents for testing.")

    # 3. Classify each incident
    classifier = IncidentClassificationAgent()
    
    print("\n--- Running Incident Classification ---")
    for idx, incident in enumerate(test_incidents, 1):
        print(f"\nIncident #{idx}:")
        print(f"  Line:      {incident['line_number']}")
        print(f"  Raw Log:   {incident['raw_log_snippet']}")
        
        result = classifier.classify_incident(incident)
        
        print(f"  Classification Output:")
        print(json.dumps(result, indent=4))
        print("-" * 50)
