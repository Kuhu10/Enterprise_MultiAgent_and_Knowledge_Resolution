from pathlib import Path
import csv
from collections import Counter


def calculate_metrics():

    csv_file = Path(
        "evaluation/results/hdfs_chunk_evaluation.csv"
    )

    if not csv_file.exists():
        raise FileNotFoundError(
            f"Evaluation file not found: {csv_file}"
        )

    rows = []

    with csv_file.open(
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)

    total = len(rows)

    if total == 0:
        print("No evaluation records found.")
        return

    final_status_counter = Counter(
        row["final_status"] for row in rows
    )

    execution_counter = Counter(
        row["execution_status"] for row in rows
    )

    verification_counter = Counter(
        row["verification_status"] for row in rows
    )

    action_counter = Counter(
        row["recommended_action"] for row in rows
    )

    incident_counter = Counter(
        row["incident_type"] for row in rows
    )

    resolved = final_status_counter.get(
        "RESOLVED",
        0
    )

    unresolved = final_status_counter.get(
        "UNRESOLVED",
        0
    )

    pending = final_status_counter.get(
        "PENDING",
        0
    )

    resolved_percentage = (
        resolved / total
    ) * 100

    unresolved_percentage = (
        unresolved / total
    ) * 100

    pending_percentage = (
        pending / total
    ) * 100

    print("\n========================================")
    print("       HDFS EVALUATION METRICS")
    print("========================================")

    print(f"\nTotal chunks evaluated: {total}")

    print("\nFinal Status")
    print("----------------------------------------")

    print(
        f"Resolved: {resolved} "
        f"({resolved_percentage:.2f}%)"
    )

    print(
        f"Unresolved: {unresolved} "
        f"({unresolved_percentage:.2f}%)"
    )

    print(
        f"Pending: {pending} "
        f"({pending_percentage:.2f}%)"
    )

    print("\nExecution Status")
    print("----------------------------------------")

    for status, count in execution_counter.items():
        print(f"{status}: {count}")

    print("\nVerification Status")
    print("----------------------------------------")

    for status, count in verification_counter.items():
        print(f"{status}: {count}")

    print("\nIncident Distribution")
    print("----------------------------------------")

    for incident, count in incident_counter.items():
        percentage = (
            count / total
        ) * 100

        print(
            f"{incident}: "
            f"{count} ({percentage:.2f}%)"
        )

    print("\nAction Distribution")
    print("----------------------------------------")

    for action, count in action_counter.items():
        percentage = (
            count / total
        ) * 100

        print(
            f"{action}: "
            f"{count} ({percentage:.2f}%)"
        )

    print("\n========================================")
    print("Metrics calculated successfully.")
    print("========================================")


if __name__ == "__main__":
    calculate_metrics()