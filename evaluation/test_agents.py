from agents.execution_agent import ExecutionAgent
from agents.reporting_verification_agent import ReportingVerificationAgent


def run_test(
    test_name,
    resolution_output,
    post_action_state,
    expected_status
):
    print("\n========================================")
    print(f"TEST: {test_name}")
    print("========================================")

    execution_agent = ExecutionAgent(simulation_mode=True)
    verification_agent = ReportingVerificationAgent()

    # Execute
    execution_result = execution_agent.execute(
        resolution_output
    )

    # Verify
    final_report = verification_agent.verify(
        execution_result,
        resolution_output,
        post_action_state
    )

    actual_status = final_report["final_status"]

    print(f"Action: {resolution_output.get('recommended_action')}")
    print(f"Execution: {execution_result['status']}")
    print(
        f"Verification: "
        f"{final_report['verification_status']}"
    )
    print(f"Expected: {expected_status}")
    print(f"Actual: {actual_status}")

    if actual_status == expected_status:
        print("TEST PASSED")
        return True

    print("TEST FAILED")
    return False


def main():

    tests_passed = 0
    total_tests = 0

    # ==========================================
    # TEST 1
    # Successful restart
    # ==========================================

    resolution = {
        "incident_id": "TEST-001",
        "incident_type": "HDFS DataNode Incident",
        "root_cause": "DataNode stopped",
        "recommended_action": "restart_service",
        "target_system": "hdfs-datanode"
    }

    post_state = {
        "service_running": True,
        "health_check_passed": True,
        "error_still_present": False
    }

    total_tests += 1

    if run_test(
        "Successful service restart",
        resolution,
        post_state,
        "RESOLVED"
    ):
        tests_passed += 1

    # ==========================================
    # TEST 2
    # Restart executed but problem remains
    # ==========================================

    resolution = {
        "incident_id": "TEST-002",
        "incident_type": "HDFS DataNode Incident",
        "root_cause": "DataNode stopped",
        "recommended_action": "restart_service",
        "target_system": "hdfs-datanode"
    }

    post_state = {
        "service_running": False,
        "health_check_passed": False,
        "error_still_present": True
    }

    total_tests += 1

    if run_test(
        "Restart unsuccessful",
        resolution,
        post_state,
        "UNRESOLVED"
    ):
        tests_passed += 1

    # ==========================================
    # TEST 3
    # Disk check
    # ==========================================

    resolution = {
        "incident_id": "TEST-003",
        "incident_type": "Disk Related Incident",
        "root_cause": "Possible disk problem",
        "recommended_action": "check_disk_space",
        "target_system": "hdfs-node"
    }

    post_state = {
        "service_running": True,
        "health_check_passed": True,
        "error_still_present": False
    }

    total_tests += 1

    if run_test(
        "Disk check",
        resolution,
        post_state,
        "RESOLVED"
    ):
        tests_passed += 1

    # ==========================================
    # TEST 4
    # Health check
    # ==========================================

    resolution = {
        "incident_id": "TEST-004",
        "incident_type": "General HDFS Incident",
        "root_cause": "General HDFS error",
        "recommended_action": "run_health_check",
        "target_system": "hdfs-cluster"
    }

    post_state = {
        "service_running": True,
        "health_check_passed": True,
        "error_still_present": False
    }

    total_tests += 1

    if run_test(
        "Health check",
        resolution,
        post_state,
        "RESOLVED"
    ):
        tests_passed += 1

    # ==========================================
    # TEST 5
    # Invalid action
    # ==========================================

    resolution = {
        "incident_id": "TEST-005",
        "incident_type": "Unknown Incident",
        "root_cause": "Unknown",
        "recommended_action": "delete_everything",
        "target_system": "hdfs-cluster"
    }

    post_state = {
        "service_running": False,
        "health_check_passed": False,
        "error_still_present": True
    }

    total_tests += 1

    if run_test(
        "Unsafe / invalid action rejected",
        resolution,
        post_state,
        "UNRESOLVED"
    ):
        tests_passed += 1

    # ==========================================
    # FINAL RESULT
    # ==========================================

    print("\n========================================")
    print("          AGENT TEST SUMMARY")
    print("========================================")

    print(f"Total tests: {total_tests}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {total_tests - tests_passed}")

    if tests_passed == total_tests:
        print("\nALL AGENT TESTS PASSED")
    else:
        print("\nSOME TESTS FAILED")

    print("========================================")


if __name__ == "__main__":
    main()