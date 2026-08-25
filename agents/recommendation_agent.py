import json
from typing import Optional, List, Dict, Any
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent

from .schemas import Incident, ComprehensiveDiagnosticResult
from .recommendation_tools import submit_recommendation

class RecommendationAgent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        
        self.tools = [
            submit_recommendation
        ]
        
        system_message = """You are the Recommendation Agent for a Multi-Agent Incident Management System.
Your responsibility is to determine the safest remediation strategy and produce a machine-readable execution handoff.

CRITICAL WORKFLOW:
Read Diagnostic Result -> Read Retrieved Knowledge -> Formulate Action -> Risk Assessment -> Build Execution Payload -> Submit

RULES & GUARDRAILS:
1. NEVER directly execute any remediation actions yourself. You only recommend and formulate the execution payload.
2. Prioritize enterprise-approved SOPs from the provided `retrieved_knowledge`. DO NOT fabricate SOP or historical references.
3. CAUTION ON SEVERITY & RISK: For high-severity incidents OR high-risk/destructive operations, you MUST set `requires_human_approval` to True in the `ApprovalRequirement` object. Provide a clear `approval_reason`.
4. The `ExecutionHandoff` object must contain the exact commands, endpoints, or scripts required to execute the recommendation. This is what the downstream Execution Agent will consume.
5. Provide a rollback plan in the `estimated_impact` or `rationale` section of the `RecommendedAction`.
6. Once formulated, you MUST call the `submit_recommendation` tool to output the structured payload.
"""
        
        self.agent = create_react_agent(self.llm, tools=self.tools, prompt=system_message)

    def recommend(self, incident: Incident, diagnostic_result: Any, retrieved_knowledge: List[Dict[str, str]]) -> str:
        """Determines the safest remediation strategy."""
        
        prompt = f"""Please recommend a remediation strategy for the following incident:

Incident ID: {incident.incident_id}
Severity: {incident.severity}
Affected Service: {incident.affected_service}

Diagnostic Root Cause Analysis:
{diagnostic_result}

Retrieved Knowledge (SOPs, Runbooks, History):
{json.dumps(retrieved_knowledge, indent=2)}

Construct your final recommendation adhering to the strict schema and submit it using submit_recommendation.
"""
        
        inputs = {"messages": [("user", prompt)]}
        result = self.agent.invoke(inputs)
        return result["messages"][-1].content
