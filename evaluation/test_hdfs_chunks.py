from pathlib import Path
from collections import Counter
import csv

from agents.execution_agent import ExecutionAgent
from agents.reporting_verification_agent import ReportingVerificationAgent
from evaluation.incident_detector import detect_incident


def generate_post_action_state(execution_result, chunk_id):
    """
    Generate simulated post-action evidence.

    This is only for testing the Execution and
    Verification Agents.

    Every 10th chunk -> PENDING
    Every 5th chunk  -> verification failure
    Other chunks     -> successful verification
    """

    if execution_result.get("status") == "FAILED":
        return {
            "service_running": False,
            "health_check_passed": False,
            "error_still_present": True
        }

    # Simulate pending cases
    if chunk_id % 10 == 0:
        execution_result["status"] = "PENDING"
        return None

    # Simulate unsuccessful remediation
    if chunk_id % 5 == 0:
        return {
            "service_running": False,
            "health_check_passed": False,
            "error_still_present": True
        }

    # Simulate successful remediation
    return {
        "service_running": True,
        "health_check_passed": True,
        "error_still_present": False
    }


def main():

    # --------------------------------------------------
    # DATASET
    # --------------------------------------------------

    log_file = Path("data/raw_logs/HDFS_2k.log")

    if not log_file.exists():
        raise FileNotFoundError(
            f"Dataset not found: {log_file}"
        )

    lines = log_file.read_text(
        encoding="utf-8",
        errors="ignore"
    ).splitlines()

    chunk_size = 25

    print("\n==========================================")
    print("       HDFS MULTI-AGENT EVALUATION")
    print("==========================================")

    print(f"Dataset: {log_file}")
    print(f"Total log lines: {len(lines)}")
    print(f"Chunk size: {chunk_size}")

    # --------------------------------------------------
    # CREATE AGENTS
    # --------------------------------------------------

    execution_agent = ExecutionAgent(
        simulation_mode=True
    )

    verification_agent = ReportingVerificationAgent()

    # --------------------------------------------------
    # COUNTERS
    # --------------------------------------------------

    incident_counter = Counter()
    action_counter = Counter()
    execution_counter = Counter()
    verification_counter = Counter()
    final_status_counter = Counter()

    results = []

    total_chunks = 0

    # --------------------------------------------------
    # PROCESS DATASET
    # --------------------------------------------------

    for start in range(0, len(lines), chunk_size):

        total_chunks += 1

        chunk_lines = lines[
            start:start + chunk_size
        ]

        chunk_text = "\n".join(chunk_lines)

        incident_id = (
            f"INC-CHUNK-{total_chunks:03d}"
        )

        # ==============================================
        # STEP 1 - INCIDENT DETECTOR
        # ==============================================

        resolution_output = detect_incident(
            chunk_text,
            incident_id
        )

        # ==============================================
        # STEP 2 - EXECUTION AGENT
        # ==============================================

        execution_result = execution_agent.execute(
            resolution_output
        )

        # ==============================================
        # STEP 3 - POST-ACTION EVIDENCE
        # ==============================================

        post_action_state = generate_post_action_state(
            execution_result,
            total_chunks
        )

        # ==============================================
        # STEP 4 - REPORTING & VERIFICATION AGENT
        # ==============================================

        final_report = verification_agent.verify(
            execution_result,
            resolution_output,
            post_action_state
        )

        # ==============================================
        # EXTRACT RESULTS
        # ==============================================

        incident_type = resolution_output[
            "incident_type"
        ]

        action = resolution_output[
            "recommended_action"
        ]

        confidence = resolution_output[
            "confidence_score"
        ]

        execution_status = execution_result[
            "status"
        ]

        verification_status = final_report[
            "verification_status"
        ]

        final_status = final_report[
            "final_status"
        ]

        # ==============================================
        # UPDATE COUNTERS
        # ==============================================

        incident_counter[incident_type] += 1
        action_counter[action] += 1
        execution_counter[execution_status] += 1
        verification_counter[verification_status] += 1
        final_status_counter[final_status] += 1

        # ==============================================
        # SAVE RESULT
        # ==============================================

        result_row = {
            "chunk_id": total_chunks,
            "start_line": start + 1,
            "end_line": start + len(chunk_lines),
            "incident_id": incident_id,
            "incident_type": incident_type,
            "root_cause": resolution_output[
                "root_cause"
            ],
            "confidence_score": confidence,
            "recommended_action": action,
            "target_system": resolution_output[
                "target_system"
            ],
            "execution_status": execution_status,
            "verification_status": verification_status,
            "final_status": final_status
        }

        results.append(result_row)

        # ==============================================
        # TERMINAL OUTPUT
        # ==============================================

        print("\n------------------------------------------")

        print(
            f"Chunk {total_chunks} "
            f"(Lines {start + 1}-"
            f"{start + len(chunk_lines)})"
        )

        print(f"Incident: {incident_type}")
        print(f"Confidence: {confidence}")
        print(f"Action: {action}")
        print(f"Execution: {execution_status}")
        print(f"Verification: {verification_status}")
        print(f"Final Status: {final_status}")

    # --------------------------------------------------
    # SAVE CSV
    # --------------------------------------------------

    output_dir = Path("evaluation/results")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    csv_file = (
        output_dir /
        "hdfs_chunk_evaluation.csv"
    )

    fieldnames = [
        "chunk_id",
        "start_line",
        "end_line",
        "incident_id",
        "incident_type",
        "root_cause",
        "confidence_score",
        "recommended_action",
        "target_system",
        "execution_status",
        "verification_status",
        "final_status"
    ]

    with csv_file.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    print("\n\n==========================================")
    print("             FINAL SUMMARY")
    print("==========================================")

    print(
        f"\nTotal chunks analysed: "
        f"{total_chunks}"
    )

    print("\nIncident Distribution")
    print("------------------------------------------")

    for incident, count in incident_counter.items():
        print(f"{incident}: {count}")

    print("\nAction Distribution")
    print("------------------------------------------")

    for action, count in action_counter.items():
        print(f"{action}: {count}")

    print("\nExecution Results")
    print("------------------------------------------")

    for status, count in execution_counter.items():
        print(f"{status}: {count}")

    print("\nVerification Results")
    print("------------------------------------------")

    for status, count in verification_counter.items():
        print(f"{status}: {count}")

    print("\nFinal Incident Status")
    print("------------------------------------------")

    for status, count in final_status_counter.items():
        print(f"{status}: {count}")

    print("\nCSV Report:")
    print(csv_file)

    print("\n==========================================")
    print("MULTI-AGENT EVALUATION COMPLETE")
    print("==========================================")


if __name__ == "__main__":
    main()