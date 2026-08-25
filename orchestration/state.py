from typing import TypedDict, Optional, List, Dict, Any
from agents.schemas import Incident, ComprehensiveDiagnosticResult, FinalRecommendationOutput

class IncidentState(TypedDict):
    incident: Optional[Incident]
    diagnostic_result: Optional[ComprehensiveDiagnosticResult]
    retrieved_knowledge: Optional[List[Dict[str, str]]]
    recommendation_result: Optional[FinalRecommendationOutput]
    execution_status: Optional[str]
    errors: List[str]
