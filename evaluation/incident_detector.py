def detect_incident(text, incident_id="INC-TEST-001"):
    """
    Simple deterministic HDFS incident detector.

    Priority:
    1. Disk issue
    2. DataNode issue
    3. General failure
    4. Healthy / status check
    """

    text_lower = text.lower()

    # --------------------------------------------------
    # Detect patterns
    # --------------------------------------------------

    disk_signals = [
        "disk full",
        "disk space",
        "storage full",
        "insufficient space",
        "no space left",
        "capacity",
    ]

    datanode_signals = [
        "datanode heartbeat",
        "heartbeat lost",
        "datanode service",
        "connection timeout",
        "datanode unavailable",
    ]

    general_failure_signals = [
        "exception",
        "operation failed",
        "replication failed",
        "service failed",
        "fatal error",
    ]

    healthy_signals = [
        "running normally",
        "cluster started normally",
        "health check completed successfully",
        "all nodes operational",
        "service healthy",
    ]

    disk_matches = [
        signal
        for signal in disk_signals
        if signal in text_lower
    ]

    datanode_matches = [
        signal
        for signal in datanode_signals
        if signal in text_lower
    ]

    failure_matches = [
        signal
        for signal in general_failure_signals
        if signal in text_lower
    ]

    healthy_matches = [
        signal
        for signal in healthy_signals
        if signal in text_lower
    ]

    # --------------------------------------------------
    # Classification
    # --------------------------------------------------

    if disk_matches:

        result = {
            "incident_id": incident_id,
            "incident_type": "Disk Related Incident",
            "root_cause": (
                "Disk capacity or storage-related "
                "failure pattern detected"
            ),
            "recommended_action": "check_disk_space",
            "target_system": "hdfs-node",
            "confidence_score": min(
                0.60 + (0.10 * len(disk_matches)),
                0.95
            ),
        }

        matched_patterns = disk_matches

    elif datanode_matches:

        result = {
            "incident_id": incident_id,
            "incident_type": "HDFS DataNode Incident",
            "root_cause": (
                "DataNode heartbeat, connectivity, "
                "or service failure detected"
            ),
            "recommended_action": "restart_service",
            "target_system": "hdfs-datanode",
            "confidence_score": min(
                0.60 + (0.10 * len(datanode_matches)),
                0.95
            ),
        }

        matched_patterns = datanode_matches

    elif failure_matches:

        result = {
            "incident_id": incident_id,
            "incident_type": "General HDFS Incident",
            "root_cause": (
                "General HDFS failure or exception detected"
            ),
            "recommended_action": "run_health_check",
            "target_system": "hdfs-cluster",
            "confidence_score": min(
                0.55 + (0.10 * len(failure_matches)),
                0.90
            ),
        }

        matched_patterns = failure_matches

    elif healthy_matches:

        result = {
            "incident_id": incident_id,
            "incident_type": "HDFS Status Check",
            "root_cause": (
                "No significant failure pattern detected"
            ),
            "recommended_action": "check_service_status",
            "target_system": "hdfs-cluster",
            "confidence_score": min(
                0.65 + (0.08 * len(healthy_matches)),
                0.95
            ),
        }

        matched_patterns = healthy_matches

    else:

        result = {
            "incident_id": incident_id,
            "incident_type": "Unknown HDFS Incident",
            "root_cause": (
                "Log pattern could not be classified confidently"
            ),
            "recommended_action": "run_health_check",
            "target_system": "hdfs-cluster",
            "confidence_score": 0.30,
        }

        matched_patterns = []

    # Useful for debugging
    result["matched_patterns"] = matched_patterns

    return result


if __name__ == "__main__":

    tests = {
        "disk": """
        ERROR Disk is full.
        WARN Disk space critically low.
        Insufficient space for HDFS block.
        """,

        "datanode": """
        ERROR DataNode heartbeat lost.
        Connection timeout while contacting DataNode.
        DataNode service unavailable.
        """,

        "general": """
        ERROR HDFS operation failed.
        Unexpected exception during processing.
        Replication failed.
        """,

        "healthy": """
        Cluster started normally.
        Service running normally.
        Health check completed successfully.
        All nodes operational.
        """
    }

    for name, log in tests.items():

        result = detect_incident(
            log,
            f"TEST-{name.upper()}"
        )

        print("\n------------------------------")
        print("TEST:", name)
        print("Incident:", result["incident_type"])
        print("Action:", result["recommended_action"])
        print("Matches:", result["matched_patterns"])