import logging
from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from .state import IncidentState
from agents.diagnostic_agent import DiagnosticAgent
from agents.recommendation_agent import RecommendationAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

# Initialize models
llm = ChatOpenAI(model="gpt-4o")
diagnostic_agent = DiagnosticAgent(llm)
recommendation_agent = RecommendationAgent(llm)

def monitoring_node(state: IncidentState):
    logger.info("--- MONITORING NODE ---")
    logger.info(f"Incoming Incident: {state.get('incident')}")
    # Stub: Normally would ingest incident data
    return state

def classification_node(state: IncidentState):
    logger.info("--- CLASSIFICATION NODE ---")
    # Stub: Normally would classify severity/service
    return state

def diagnostic_node(state: IncidentState):
    logger.info("--- DIAGNOSTIC NODE ---")
    incident = state.get('incident')
    if not incident:
        logger.error("No incident provided to Diagnostic Agent.")
        state["errors"].append("Missing incident")
        return state
    
    try:
        raw_result = diagnostic_agent.analyze(incident)
        state["diagnostic_result"] = raw_result
        logger.info(f"Diagnostic Result Generated.")
    except Exception as e:
        logger.error(f"Diagnostic Agent failed: {e}")
        if "errors" not in state or state["errors"] is None:
            state["errors"] = []
        state["errors"].append(str(e))
        
    return state

def retrieval_node(state: IncidentState):
    logger.info("--- RETRIEVAL NODE ---")
    # ONLY retrieve knowledge boundary
    diagnostic_result = state.get("diagnostic_result")
    if not diagnostic_result:
        logger.error("No diagnostic result to use for retrieval.")
        if "errors" not in state or state["errors"] is None:
            state["errors"] = []
        state["errors"].append("Missing diagnostic result")
        return state
        
    # Simulate retrieving SOPs based on diagnosis
    retrieved_knowledge = [
        {
            "id": "SOP-849",
            "title": "Handling general issues",
            "content": "Step 1: Check metrics. Step 2: Restart service safely. Step 3: Monitor.",
            "category": "SOP"
        }
    ]
    state["retrieved_knowledge"] = retrieved_knowledge
    logger.info(f"Retrieved Knowledge: {retrieved_knowledge}")
    return state

def recommendation_node(state: IncidentState):
    logger.info("--- RECOMMENDATION NODE ---")
    incident = state.get("incident")
    diagnostic_result = state.get("diagnostic_result")
    retrieved_knowledge = state.get("retrieved_knowledge")
    
    if not incident or not diagnostic_result or not retrieved_knowledge:
        if "errors" not in state or state["errors"] is None:
            state["errors"] = []
        state["errors"].append("Missing required state for Recommendation Node")
        return state
        
    try:
        raw_recommendation = recommendation_agent.recommend(incident, diagnostic_result, retrieved_knowledge)
        state["recommendation_result"] = raw_recommendation
        logger.info(f"Recommendation Result Generated.")
    except Exception as e:
        logger.error(f"Recommendation Agent failed: {e}")
        if "errors" not in state or state["errors"] is None:
            state["errors"] = []
        state["errors"].append(str(e))
        
    return state

def execution_node(state: IncidentState):
    logger.info("--- EXECUTION NODE ---")
    # Stub: Only execute approved actions
    recommendation = state.get("recommendation_result")
    # Simulated check
    logger.info("Awaiting approval before execution...")
    state["execution_status"] = "Awaiting Approval"
    return state

def reporting_node(state: IncidentState):
    logger.info("--- REPORTING NODE ---")
    # Stub: Verify recovery, generate RCA
    logger.info("Generating Incident Report.")
    return state


# Build Graph
workflow = StateGraph(IncidentState)

# Add Nodes
workflow.add_node("monitoring", monitoring_node)
workflow.add_node("classification", classification_node)
workflow.add_node("diagnostic", diagnostic_node)
workflow.add_node("retrieval", retrieval_node)
workflow.add_node("recommendation", recommendation_node)
workflow.add_node("execution", execution_node)
workflow.add_node("reporting", reporting_node)

# Add Edges
workflow.set_entry_point("monitoring")
workflow.add_edge("monitoring", "classification")
workflow.add_edge("classification", "diagnostic")
workflow.add_edge("diagnostic", "retrieval")
workflow.add_edge("retrieval", "recommendation")
workflow.add_edge("recommendation", "execution")
workflow.add_edge("execution", "reporting")
workflow.add_edge("reporting", END)

# Compile Graph
app = workflow.compile()
