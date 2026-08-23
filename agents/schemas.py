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

