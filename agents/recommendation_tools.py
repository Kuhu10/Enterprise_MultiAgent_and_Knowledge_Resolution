import logging
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RecommendationAgent")

@tool
def retrieve_knowledge(query: str, category: str = None) -> List[Dict[str, str]]:
    """
    Retrieve enterprise knowledge such as SOPs, Runbooks, or past historical incidents.
    
    Args:
        query: The search term (e.g., 'database timeout SOP', 'redis latency').
        category: Optional category filter ('SOP', 'Runbook', 'HistoricalIncident').
        
    Returns:
        A list of relevant documents with their content and source IDs.
    """
    # Mock implementation - in a real system this queries the Vector Database (ChromaDB)
    return [
        {
            "id": "SOP-849",
            "title": f"Handling {query} issues",
            "content": "Step 1: Check metrics. Step 2: Restart service safely. Step 3: Monitor.",
            "category": category or "SOP"
        }
    ]

@tool
def submit_recommendation(
    incident: dict,
    diagnosis: dict,
    recommended_action: dict,
    supporting_knowledge: dict,
    alternative_actions: List[dict],
    approval_requirement: dict,
    execution_handoff: dict
) -> str:
    """
    Submit the final structured remediation recommendation. Call this ONLY when you have evaluated the actions and made a final choice.
    
    Args:
        incident: A dict matching IncidentContext.
        diagnosis: A dict matching DiagnosticContext.
        recommended_action: A dict matching RecommendedAction.
        supporting_knowledge: A dict matching SupportingKnowledge.
        alternative_actions: A list of dicts matching AlternativeAction.
        approval_requirement: A dict matching ApprovalRequirement.
        execution_handoff: A dict matching ExecutionHandoff.
        
    Returns:
        A success message indicating the recommendation has been recorded.
    """
    # Audit logging
    logger.info(f"Submitting Recommendation for Incident ID: {incident.get('incident_id')}")
    logger.info(f"Diagnosis Root Cause: {diagnosis.get('root_cause')} (Confidence: {diagnosis.get('diagnostic_confidence')})")
    logger.info(f"Recommended Action: {recommended_action.get('action')} (Risk: {recommended_action.get('risk_level')})")
    logger.info(f"Knowledge Sources: {supporting_knowledge}")
    logger.info(f"Requires Approval: {approval_requirement.get('requires_human_approval')} - {approval_requirement.get('approval_reason')}")
    logger.info(f"Execution Handoff Target: {execution_handoff.get('target_environment')} via {execution_handoff.get('execution_type')}")
    
    return "Recommendation submitted successfully and audit log generated. Awaiting human/execution agent approval."
