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

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10 or higher installed.

### Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Kuhu10/Enterprise_MultiAgent_and_Knowledge_Resolution.git
    cd Enterprise_MultiAgent_and_Knowledge_Resolution
    ```

2.  **Create a Virtual Environment:**
    ```bash
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Copy the sample environment file and add your API keys:
    ```bash
    cp .env.example .env
    ```
    Open `.env` in a text editor and fill in your `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY`.

5.  **Download Sample Logs:**
    Run the utility script to fetch log datasets:
    ```bash
    python data/download_loghub.py
    ```
