import csv
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent

HISTORY_DIR = PROJECT_ROOT / "evaluation" / "results"

HISTORY_FILE = HISTORY_DIR / "incident_history.csv"


def save_incident_history(
    resolution_output,
    execution_result,
    final_report
):
    """
    Save completed incident information to CSV.
    """

    HISTORY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    row = {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "incident_id": resolution_output.get(
            "incident_id",
            ""
        ),

        "incident_type": resolution_output.get(
            "incident_type",
            ""
        ),

        "root_cause": resolution_output.get(
            "root_cause",
            ""
        ),

        "recommended_action": resolution_output.get(
            "recommended_action",
            ""
        ),

        "target_system": resolution_output.get(
            "target_system",
            ""
        ),

        "confidence_score": resolution_output.get(
            "confidence_score",
            ""
        ),

        "execution_status": execution_result.get(
            "status",
            ""
        ),

        "verification_status": final_report.get(
            "verification_status",
            ""
        ),

        "final_status": final_report.get(
            "final_status",
            ""
        )
    }

    file_exists = HISTORY_FILE.exists()

    with HISTORY_FILE.open(
        mode="a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=row.keys()
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

    return HISTORY_FILE