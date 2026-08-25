import json
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent

from .schemas import Incident, ComprehensiveDiagnosticResult
from .diagnostic_tools import search_logs, get_metrics, get_traces, get_recent_changes, submit_diagnosis

class DiagnosticAgent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        
        self.tools = [
            search_logs,
            get_metrics,
            get_traces,
            get_recent_changes,
            submit_diagnosis
        ]
        
        system_message = """You are the Diagnostic Agent for a Multi-Agent Incident Management System.
Your responsibility is to iteratively investigate an incident using your tools and determine the root cause, outputting a machine-readable structure for the Recommendation Agent.

CRITICAL REASONING STRATEGY:
Evidence -> Hypothesis -> Evidence validation -> Confidence -> Root Cause

1. Gather Evidence using tools (search logs, check metrics, review traces, check recent changes).
2. Formulate Hypotheses. Do NOT blindly assume the first error is the root cause.
3. Validate by checking for correlating or contradicting evidence.
4. Once concluded, call `submit_diagnosis` with the comprehensive nested structure. Do NOT include remediation commands.

HANDLING EDGE CASES:
- Missing Data: Do NOT hallucinate logs, metrics, traces, or system info. Explicitly note when data is unavailable or missing in your observations.
- Conflicting Evidence: Document conflicts in the AlternativeHypothesis `contradicting_evidence` field and adjust your confidence scores accordingly.
- Low-Confidence Diagnosis: If evidence is insufficient, explicitly return "Root cause could not be determined with sufficient confidence" in the primary root cause field.
- Multiple Possible Root Causes: List them in `contributing_factors` or as distinct `AlternativeHypothesis` entries.
- Cascading Failures: Trace the dependency chain back to the origin. Document intermediate failures in `contributing_factors` and list all upstream/downstream impacted services in `ImpactAnalysis.affected_services`.
"""
        
        self.agent = create_react_agent(self.llm, tools=self.tools, prompt=system_message)

    def analyze(self, incident: Incident) -> str:
        """Analyzes an incident using a tool-based reasoning loop."""
        
        prompt = f"""Please diagnose the following incident:

Incident ID: {incident.incident_id}
Severity: {incident.severity}
Affected Service: {incident.affected_service}
Error Message: {incident.error_message}
Timestamp: {incident.timestamp}

Investigate the incident using your tools. Submit your final comprehensive diagnosis using the submit_diagnosis tool.
"""
        
        inputs = {"messages": [("user", prompt)]}
        result = self.agent.invoke(inputs)
        return result["messages"][-1].content
