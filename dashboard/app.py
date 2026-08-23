import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from agents.execution_agent import ExecutionAgent
from agents.reporting_verification_agent import ReportingVerificationAgent
from evaluation.incident_detector import detect_incident
from evaluation.incident_history import save_incident_history


st.set_page_config(
    page_title="Multi-Agent Incident System",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ Multi-Agent Incident Resolution System")

st.write(
    "Upload an HDFS log file, detect an incident, execute remediation, "
    "and verify whether the incident is resolved."
)

uploaded_file = st.file_uploader(
    "Upload HDFS log file",
    type=["log", "txt"]
)


if uploaded_file is not None:

    log_text = uploaded_file.read().decode(
        "utf-8",
        errors="ignore"
    )

    st.success("Log file loaded successfully.")

    # ==================================================
    # INCIDENT DETECTION
    # ==================================================

    st.subheader("1. Incident Detection")

    resolution_output = detect_incident(
        log_text,
        "INC-UI-001"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "**Incident Type:**",
            resolution_output["incident_type"]
        )

        st.write(
            "**Root Cause:**",
            resolution_output["root_cause"]
        )

        st.write(
            "**Confidence:**",
            resolution_output["confidence_score"]
        )

    with col2:

        st.write(
            "**Recommended Action:**",
            resolution_output["recommended_action"]
        )

        st.write(
            "**Target System:**",
            resolution_output["target_system"]
        )

    # ==================================================
    # EXECUTION AGENT
    # ==================================================

    st.subheader("2. Execution Agent")

    if st.button("Execute Recommended Action"):

        execution_agent = ExecutionAgent(
            simulation_mode=True
        )

        execution_result = execution_agent.execute(
            resolution_output
        )

        st.session_state["execution_result"] = execution_result
        st.session_state["resolution_output"] = resolution_output

        # Clear any previous verification report
        if "final_report" in st.session_state:
            del st.session_state["final_report"]

        if execution_result["status"] == "SUCCESS":

            st.success(
                execution_result["message"]
            )

        elif execution_result["status"] == "PENDING":

            st.warning(
                execution_result["message"]
            )

        else:

            st.error(
                execution_result["message"]
            )


# ======================================================
# REPORTING & VERIFICATION AGENT
# ======================================================
# ======================================================
# REPORTING & VERIFICATION AGENT
# ======================================================

if "execution_result" in st.session_state:

    st.subheader("3. Reporting & Verification Agent")

    execution_result = st.session_state[
        "execution_result"
    ]

    resolution_output = st.session_state[
        "resolution_output"
    ]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Execution Status",
            execution_result["status"]
        )

    with col2:
        st.metric(
            "Action",
            execution_result["action"]
        )

    with col3:
        st.metric(
            "Target",
            execution_result["target_system"]
        )

    st.write("### Post-Action Verification")

    service_running = st.checkbox(
        "Service is running",
        value=True
    )

    health_check_passed = st.checkbox(
        "Health check passed",
        value=True
    )

    error_still_present = st.checkbox(
        "Original error still present",
        value=False
    )

    if st.button("Verify Incident"):

        post_action_state = {
            "service_running": service_running,
            "health_check_passed": health_check_passed,
            "error_still_present": error_still_present
        }

        verification_agent = ReportingVerificationAgent()

        final_report = verification_agent.verify(
            execution_result,
            resolution_output,
            post_action_state
        )

        # Store final report only AFTER it has been created
        st.session_state["final_report"] = final_report

        # Save incident history
        history_file = save_incident_history(
            resolution_output,
            execution_result,
            final_report
        )

        st.success(
            f"Incident report saved to {history_file.name}"
        )
# ======================================================
# FINAL REPORT
# ======================================================
if "final_report" in st.session_state:
    
    final_report = st.session_state[
        "final_report"
    ]

    st.subheader("4. Final Incident Report")

    final_status = final_report["final_status"]

    if final_status == "RESOLVED":
        st.success("✅ INCIDENT RESOLVED")

    elif final_status == "UNRESOLVED":
        st.error("❌ INCIDENT UNRESOLVED")

    elif final_status == "PENDING":
        st.warning("⏳ INCIDENT PENDING")

    else:
        st.info("ℹ️ INCIDENT UNVERIFIED")

    st.write(
        "**Verification Status:**",
        final_report["verification_status"]
    )

    st.write(
        "**Verification Message:**",
        final_report["verification_message"]
    )

    st.write(
        "**Root Cause:**",
        final_report.get(
            "root_cause",
            "Unknown"
        )
    )

    st.write(
        "**Recommended Action:**",
        final_report.get(
            "recommended_action",
            "Unknown"
        )
    )

    with st.expander(
        "View Full Incident Report"
    ):
        st.json(final_report)