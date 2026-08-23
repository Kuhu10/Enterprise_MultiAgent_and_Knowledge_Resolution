from pathlib import Path

from agents.execution_agent import ExecutionAgent
from agents.reporting_verification_agent import ReportingVerificationAgent


def analyse_hdfs_log(log_file):
    """
    Temporary dataset adapter.

    Reads HDFS log data and creates
    Resolution Agent-style output.
    """

    log_path = Path(log_file)

    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_path}")

    text = log_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    text_lower = text.lower()

    print(f"\nDataset loaded: {log_path}")
    print(f"Total lines: {len(text.splitlines())}")
    print(f"Total characters: {len(text)}")

    # Basic pattern counts
    pattern_counts = {
        "datanode": text_lower.count("datanode"),
        "disk": text_lower.count("disk"),
        "heartbeat": text_lower.count("heartbeat"),
        "error": text_lower.count("error"),
        "fail": text_lower.count("fail"),
        "exception": text_lower.count("exception")
    }

    print("\nDetected Pattern Counts")
    print("--------------------------------------")

    for key, value in pattern_counts.items():
        print(f"{key}: {value}")

    # --------------------------------------------------
    # Temporary incident classification logic
    # --------------------------------------------------

    if (
        "datanode" in text_lower
        and "heartbeat" in text_lower
    ):
        resolution_output = {
            "incident_id": "INC-HDFS-001",
            "incident_type": "HDFS DataNode Incident",
            "root_cause": (
                "Possible DataNode heartbeat/service issue "
                "detected from logs"
            ),
            "recommended_action": "restart_service",
            "target_system": "hdfs-datanode"
        }

    elif (
        "disk" in text_lower
        and (
            "space" in text_lower
            or "full" in text_lower
        )
    ):
        resolution_output = {
            "incident_id": "INC-HDFS-002",
            "incident_type": "Disk Related Incident",
            "root_cause": (
                "Possible disk capacity issue detected"
            ),
            "recommended_action": "check_disk_space",
            "target_system": "hdfs-node"
        }

    elif (
        "error" in text_lower
        or "exception" in text_lower
        or "fail" in text_lower
    ):
        resolution_output = {
            "incident_id": "INC-HDFS-003",
            "incident_type": "General HDFS Incident",
            "root_cause": (
                "Error/failure pattern detected in HDFS logs"
            ),
            "recommended_action": "run_health_check",
            "target_system": "hdfs-cluster"
        }

    else:
        resolution_output = {
            "incident_id": "INC-HDFS-004",
            "incident_type": "HDFS Status Check",
            "root_cause": (
                "No major incident pattern detected"
            ),
            "recommended_action": "check_service_status",
            "target_system": "hdfs-cluster"
        }

    return resolution_output


def generate_post_action_state(execution_result):
    """
    Temporary simulator for post-action verification evidence.

    In the real system, this data should come from
    actual monitoring/log/health-check systems.
    """

    status = execution_result.get("status")
    action = execution_result.get("action")

    if status != "SUCCESS":
        return {
            "service_running": False,
            "health_check_passed": False,
            "error_still_present": True
        }

    # Simulated successful outcome
    if action == "restart_service":
        return {
            "service_running": True,
            "health_check_passed": True,
            "error_still_present": False
        }

    if action == "check_service_status":
        return {
            "service_running": True,
            "health_check_passed": True,
            "error_still_present": False
        }

    if action == "check_disk_space":
        return {
            "service_running": True,
            "health_check_passed": True,
            "error_still_present": False
        }

    if action == "run_health_check":
        return {
            "service_running": True,
            "health_check_passed": True,
            "error_still_present": False
        }

    return {
        "service_running": False,
        "health_check_passed": False,
        "error_still_present": True
    }


if __name__ == "__main__":

    log_file = "data/raw_logs/HDFS_2k.log"

    print("\n======================================")
    print("        FULL INCIDENT PIPELINE")
    print("======================================")

    # --------------------------------------------------
    # STEP 1 - Dataset analysis
    # --------------------------------------------------

    resolution_output = analyse_hdfs_log(log_file)

    print("\nGenerated Resolution Output")
    print("--------------------------------------")

    for key, value in resolution_output.items():
        print(f"{key}: {value}")

    # --------------------------------------------------
    # STEP 2 - Execution Agent
    # --------------------------------------------------

    execution_agent = ExecutionAgent(
        simulation_mode=True
    )

    execution_result = execution_agent.execute(
        resolution_output
    )

    print("\nExecution Agent Result")
    print("--------------------------------------")

    for key, value in execution_result.items():
        print(f"{key}: {value}")

    # --------------------------------------------------
    # STEP 3 - Generate post-action evidence
    # --------------------------------------------------

    post_action_state = generate_post_action_state(
        execution_result
    )

    print("\nPost-Action Verification Evidence")
    print("--------------------------------------")

    for key, value in post_action_state.items():
        print(f"{key}: {value}")

    # --------------------------------------------------
    # STEP 4 - Reporting & Verification Agent
    # --------------------------------------------------

    verification_agent = ReportingVerificationAgent()

    final_report = verification_agent.verify(
        execution_result,
        resolution_output,
        post_action_state
    )

    # --------------------------------------------------
    # STEP 5 - Final incident report
    # --------------------------------------------------

    print("\n======================================")
    print("         FINAL INCIDENT REPORT")
    print("======================================")

    for key, value in final_report.items():
        print(f"{key}: {value}")

    print("--------------------------------------")

    if final_report["final_status"] == "RESOLVED":
        print("\nFINAL RESULT: INCIDENT RESOLVED")

    elif final_report["final_status"] == "UNRESOLVED":
        print("\nFINAL RESULT: INCIDENT UNRESOLVED")

    elif final_report["final_status"] == "PENDING":
        print("\nFINAL RESULT: VERIFICATION PENDING")

    else:
        print("\nFINAL RESULT: INCIDENT UNVERIFIED")