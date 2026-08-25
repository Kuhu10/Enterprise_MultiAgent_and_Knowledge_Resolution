from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class Incident(BaseModel):
    incident_id: str
    severity: str
    affected_service: str
    error_message: str
    timestamp: str
    # Keeping these for backwards compatibility or if passed in, but tools will fetch them primarily now.
    logs: Optional[List[str]] = Field(default_factory=list)
    traces: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    recent_changes: Optional[List[str]] = Field(default_factory=list)

class IncidentSummary(BaseModel):
    incident_id: str = Field(description="The unique identifier for the incident.")
    severity: str = Field(description="The severity level of the incident.")
    affected_service: str = Field(description="The primary service affected.")
    detected_time: str = Field(description="The time the incident was detected.")
    symptoms: List[str] = Field(description="List of extracted symptoms.")

class EvidenceItem(BaseModel):
    source: str = Field(description="The source of the evidence (e.g., application logs, CPU metrics, traces).")
    timestamp: str = Field(description="The timestamp associated with the evidence.")
    observation: str = Field(description="A clear description of what the evidence shows.")
    relevance: str = Field(description="Why this evidence is relevant to the diagnosis.")

class AlternativeHypothesis(BaseModel):
    hypothesis: str = Field(description="A clear description of the alternative hypothesis.")
    supporting_evidence: List[str] = Field(description="List of evidence observations supporting this hypothesis.")
    contradicting_evidence: List[str] = Field(description="List of evidence observations contradicting this hypothesis.")
    confidence: float = Field(description="Confidence score for this hypothesis (0.0 to 1.0).")

class RootCauseAnalysis(BaseModel):
    primary_root_cause: str = Field(description="The most likely primary root cause. If evidence is insufficient, use: 'Root cause could not be determined with sufficient confidence.'")
    contributing_factors: List[str] = Field(description="Other factors contributing to the incident, including cascading failures.")
    affected_components: List[str] = Field(description="List of components affected by the root cause.")
    root_cause_confidence: float = Field(description="Confidence score for the primary root cause (0.0 to 1.0).")

class ImpactAnalysis(BaseModel):
    affected_services: List[str] = Field(description="All downstream or upstream services impacted by the incident.")
    estimated_user_impact: str = Field(description="The estimated impact on end users (e.g., 500s returned to users, slow logins).")
    operational_impact: str = Field(description="The impact on system operations.")
    data_impact: Optional[str] = Field(description="Any potential data corruption or loss.")

class DiagnosticConclusion(BaseModel):
    root_cause: str = Field(description="A concise summary of the primary root cause.")
    confidence: float = Field(description="The overall confidence score.")
    explanation: str = Field(description="A detailed explanation of how the root cause led to the symptoms.")
    evidence_summary: str = Field(description="A brief summary of the key evidence used to reach this conclusion.")

class ComprehensiveDiagnosticResult(BaseModel):
    incident_summary: IncidentSummary
    evidence: List[EvidenceItem]
    root_cause_analysis: RootCauseAnalysis
    hypotheses: List[AlternativeHypothesis]
    impact_analysis: ImpactAnalysis
    diagnostic_conclusion: DiagnosticConclusion

class IncidentContext(BaseModel):
    incident_id: str = Field(description="The unique identifier for the incident.")
    severity: str = Field(description="The severity level of the incident.")
    affected_service: str = Field(description="The primary service affected.")

class DiagnosticContext(BaseModel):
    root_cause: str = Field(description="The diagnosed root cause.")
    diagnostic_confidence: float = Field(description="Confidence score of the diagnosis.")
    evidence_summary: str = Field(description="Summary of the evidence supporting the diagnosis.")

class RecommendedAction(BaseModel):
    action: str = Field(description="The recommended remediation action.")
    rationale: str = Field(description="Why this action is recommended.")
    expected_outcome: str = Field(description="What this action will achieve.")
    confidence: float = Field(description="Confidence score for this recommendation.")
    risk_level: str = Field(description="Risk level (e.g., Low, Medium, High, Critical).")
    reversibility: str = Field(description="Can it be rolled back?")
    estimated_impact: str = Field(description="Estimated impact of executing this action.")

class SupportingKnowledge(BaseModel):
    sop_reference: Optional[str] = Field(description="Reference to an SOP or runbook.")
    historical_incident_reference: Optional[str] = Field(description="Reference to a past incident.")
    enterprise_documentation: Optional[str] = Field(description="Reference to other enterprise docs.")

class AlternativeAction(BaseModel):
    action: str = Field(description="The alternative remediation action.")
    rationale: str = Field(description="Why this is a valid alternative.")
    confidence: float = Field(description="Confidence score for this alternative.")
    risk_level: str = Field(description="Risk level of this alternative.")
    why_it_is_not_the_primary_choice: str = Field(description="Reason for not selecting this as the primary recommendation.")

class ApprovalRequirement(BaseModel):
    requires_human_approval: bool = Field(description="Whether human approval is required. MUST be true for high-risk or destructive actions.")
    approval_reason: str = Field(description="Reason why approval is or isn't required.")

class ExecutionHandoff(BaseModel):
    execution_type: str = Field(description="e.g., 'API_CALL', 'SSH_COMMAND', 'MANUAL_INTERVENTION'")
    commands_or_scripts: List[str] = Field(description="The exact commands, API endpoints, or scripts to execute.")
    target_environment: str = Field(description="The environment where the execution should happen.")

class FinalRecommendationOutput(BaseModel):
    incident: IncidentContext
    diagnosis: DiagnosticContext
    recommended_action: RecommendedAction
    supporting_knowledge: SupportingKnowledge
    alternative_actions: List[AlternativeAction]
    approval_requirement: ApprovalRequirement
    execution_handoff: ExecutionHandoff
