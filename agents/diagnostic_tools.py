from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from .schemas import (
    IncidentSummary, EvidenceItem, RootCauseAnalysis, 
    AlternativeHypothesis, ImpactAnalysis, DiagnosticConclusion,
    ComprehensiveDiagnosticResult
)

# Since this is a modular architecture, we mock the external services here. 
# In a real environment, these would query Elasticsearch, Prometheus, Jaeger, etc.

@tool
def search_logs(query: str, component: str = None) -> List[str]:
    """
    Search application, server, and error logs for specific patterns or errors.
    
    Args:
        query: The search term, error message, or pattern to look for.
        component: Optional component or service name to filter logs.
    
    Returns:
        A list of matching log lines.
    """
    # Mock implementation - in reality, it would query a log aggregator
    return [f"[ERROR] Mock log entry matching '{query}' in {component or 'unknown system'}"]

@tool
def get_metrics(metric_name: str, component: str = None) -> Dict[str, Any]:
    """
    Retrieve metrics (e.g., cpu_utilization, memory, latency, error_rate) for a service.
    
    Args:
        metric_name: The name of the metric to fetch.
        component: The service or component name.
        
    Returns:
        A dictionary containing the requested metrics.
    """
    # Mock implementation
    return {"metric": metric_name, "component": component, "value": "mock_value_spike", "status": "abnormal"}

@tool
def get_traces(trace_id: str = None, component: str = None) -> List[Dict[str, Any]]:
    """
    Retrieve distributed traces to identify slow services, failed spans, or dependency failures.
    
    Args:
        trace_id: A specific trace ID to look up (if known).
        component: The service name to find recent slow/failed traces for.
        
    Returns:
        A list of trace spans and their statuses.
    """
    # Mock implementation
    return [{"span_id": "span-123", "service": component, "status": "timeout", "duration_ms": 5000}]

@tool
def get_recent_changes(component: str = None) -> List[str]:
    """
    Fetch recent deployments, configuration changes, or infrastructure updates.
    
    Args:
        component: The service or component name to check for changes.
        
    Returns:
        A list of recent change events.
    """
    # Mock implementation
    return [f"Deployed v2.0 to {component or 'system'} 5 minutes ago"]

@tool
def submit_diagnosis(
    incident_summary: dict,
    evidence: List[dict],
    root_cause_analysis: dict,
    hypotheses: List[dict],
    impact_analysis: dict,
    diagnostic_conclusion: dict
) -> str:
    """
    Submit the final diagnostic conclusion. Call this tool ONLY when you have evaluated the evidence and are ready to finalize the root cause.
    
    Args:
        incident_summary: A dict matching IncidentSummary (incident_id, severity, affected_service, detected_time, symptoms).
        evidence: A list of dicts matching EvidenceItem (source, timestamp, observation, relevance).
        root_cause_analysis: A dict matching RootCauseAnalysis (primary_root_cause, contributing_factors, affected_components, root_cause_confidence).
        hypotheses: A list of dicts matching AlternativeHypothesis (hypothesis, supporting_evidence, contradicting_evidence, confidence).
        impact_analysis: A dict matching ImpactAnalysis (affected_services, estimated_user_impact, operational_impact, data_impact).
        diagnostic_conclusion: A dict matching DiagnosticConclusion (root_cause, confidence, explanation, evidence_summary).
        
    Returns:
        A success message indicating the diagnosis has been recorded.
    """
    # In a real environment, this might write to a database or pass state forward in LangGraph
    return "Diagnosis submitted successfully. Structured output recorded for Recommendation Agent."
