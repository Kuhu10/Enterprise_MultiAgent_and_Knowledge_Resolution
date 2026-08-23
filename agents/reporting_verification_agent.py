from datetime import datetime


class ReportingVerificationAgent:
    """
    Reporting & Verification Agent

    Responsibilities:
    1. Receive Execution Agent result
    2. Inspect post-action evidence
    3. Decide whether the incident is resolved
    4. Generate a final incident report
    """

    def verify(
        self,
        execution_result,
        resolution_output=None,
        post_action_state=None
    ):
        incident_id = execution_result.get("incident_id")
        execution_status = execution_result.get("status")
        action = execution_result.get("action")
        target_system = execution_result.get("target_system")
        execution_message = execution_result.get("message")

        report = {
            "incident_id": incident_id,
            "verification_time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "target_system": target_system,
            "action_performed": action,
            "execution_status": execution_status,
            "verification_status": "",
            "final_status": "",
            "verification_message": ""
        }

        # Add Resolution Agent information
        if resolution_output:
            report["incident_type"] = resolution_output.get(
                "incident_type",
                "Unknown"
            )

            report["root_cause"] = resolution_output.get(
                "root_cause",
                "Unknown"
            )

            report["recommended_action"] = resolution_output.get(
                "recommended_action",
                "Unknown"
            )

        # ---------------------------------------------------
        # EXECUTION FAILED
        # ---------------------------------------------------

        if execution_status == "FAILED":
            report["verification_status"] = "FAIL"
            report["final_status"] = "UNRESOLVED"

            report["verification_message"] = (
                f"Execution failed. Details: {execution_message}"
            )

            return report

        # ---------------------------------------------------
        # EXECUTION PENDING
        # ---------------------------------------------------

        if execution_status == "PENDING":
            report["verification_status"] = "PENDING"
            report["final_status"] = "PENDING"

            report["verification_message"] = (
                "Execution is still pending. "
                "Verification cannot be completed."
            )

            return report

        # ---------------------------------------------------
        # UNKNOWN EXECUTION STATUS
        # ---------------------------------------------------

        if execution_status != "SUCCESS":
            report["verification_status"] = "UNKNOWN"
            report["final_status"] = "UNVERIFIED"

            report["verification_message"] = (
                f"Unknown execution status: {execution_status}"
            )

            return report

        # ---------------------------------------------------
        # POST-ACTION EVIDENCE REQUIRED
        # ---------------------------------------------------

        if not post_action_state:
            report["verification_status"] = "UNKNOWN"
            report["final_status"] = "UNVERIFIED"

            report["verification_message"] = (
                "Execution succeeded, but post-action "
                "verification evidence is missing."
            )

            return report

        # ---------------------------------------------------
        # READ POST-ACTION STATE
        # ---------------------------------------------------

        service_running = post_action_state.get(
            "service_running",
            False
        )

        health_check_passed = post_action_state.get(
            "health_check_passed",
            False
        )

        error_still_present = post_action_state.get(
            "error_still_present",
            True
        )

        report["service_running"] = service_running
        report["health_check_passed"] = health_check_passed
        report["error_still_present"] = error_still_present

        # ---------------------------------------------------
        # FINAL VERIFICATION DECISION
        # ---------------------------------------------------

        if (
            service_running
            and health_check_passed
            and not error_still_present
        ):
            report["verification_status"] = "PASS"
            report["final_status"] = "RESOLVED"

            report["verification_message"] = (
                "Post-action verification passed. "
                "The service is running, the health check passed, "
                "and the original error is no longer present."
            )

        else:
            report["verification_status"] = "FAIL"
            report["final_status"] = "UNRESOLVED"

            reasons = []

            if not service_running:
                reasons.append("service is not running")

            if not health_check_passed:
                reasons.append("health check failed")

            if error_still_present:
                reasons.append("original error is still present")

            report["verification_message"] = (
                "Post-action verification failed because "
                + ", ".join(reasons)
                + "."
            )

        return report


# ==========================================================
# TEST FUNCTION
# ==========================================================

def print_report(title, report):

    print("\n========================================")
    print(title)
    print("========================================")

    for key, value in report.items():
        print(f"{key}: {value}")

    print("----------------------------------------")
    print(f"FINAL RESULT: {report['final_status']}")


# ==========================================================
# MAIN TEST
# ==========================================================

if __name__ == "__main__":

    verification_agent = ReportingVerificationAgent()

    # Simulated Resolution Agent output
    resolution_output = {
        "incident_id": "INC-HDFS-001",
        "incident_type": "HDFS DataNode Incident",
        "root_cause": "DataNode service stopped",
        "recommended_action": "restart_service",
        "target_system": "hdfs-datanode"
    }

    # Simulated Execution Agent output
    execution_result = {
        "incident_id": "INC-HDFS-001",
        "target_system": "hdfs-datanode",
        "action": "restart_service",
        "execution_time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "simulation_mode": True,
        "status": "SUCCESS",
        "message": (
            "Service restart simulated successfully "
            "on hdfs-datanode."
        ),
        "error": None
    }

    # ======================================================
    # TEST 1: SUCCESSFUL VERIFICATION
    # ======================================================

    successful_state = {
        "service_running": True,
        "health_check_passed": True,
        "error_still_present": False
    }

    success_report = verification_agent.verify(
        execution_result,
        resolution_output,
        successful_state
    )

    print_report(
        "TEST 1 - SUCCESSFUL VERIFICATION",
        success_report
    )

    # ======================================================
    # TEST 2: FAILED VERIFICATION
    # ======================================================

    failed_state = {
        "service_running": False,
        "health_check_passed": False,
        "error_still_present": True
    }

    failed_report = verification_agent.verify(
        execution_result,
        resolution_output,
        failed_state
    )

    print_report(
        "TEST 2 - FAILED VERIFICATION",
        failed_report
    )