# Multi-Agent Incident System

The **Multi-Agent Incident System** is an intelligent, automated incident response and resolution platform. It orchestrates a network of specialized LLM-powered agents to triage, diagnose, and resolve system incidents (such as server outages or performance degradation) by analyzing raw system logs, referencing standard operating procedures (SOPs), and querying vector databases. By simulating collaborative agent workflows, the system automates root-cause analysis, proposes remediation steps, and provides a centralized dashboard for operators to monitor the step-by-step resolution process.

---

## 📁 Project Structure

*   `agents/` - Definitions and logic for specialized agents (e.g., Triage, Diagnostic, Resolution).
*   `orchestration/` - Workflows and agent routing using LangGraph.
*   `dashboard/` - Frontend UI (Streamlit / FastAPI) for incident visualization and agent tracking.
*   `evaluation/` - Tools for testing and evaluating agent resolution accuracy.
*   `data/raw_logs/` - Raw input log data (e.g., HDFS dataset).
*   `data/sops/` - Standard Operating Procedures (SOPs) for incident resolution.
*   `vectorstore/` - ChromaDB vector store files for document retrieval.
