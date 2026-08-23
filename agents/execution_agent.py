from datetime import datetime


class ExecutionAgent:
    """
    Execution Agent for the Multi-Agent Incident Resolution System.

    Responsibility:
    - Receive structured output from the Resolution Agent
    - Validate the recommended action
    - Simulate execution safely
    - Return a structured execution result
    """

    def __init__(self, simulation_mode=True):
        self.simulation_mode = simulation_mode

        self.allowed_actions = {
            "restart_service",
            "check_service_status",
            "check_disk_space",
            "run_health_check"
        }

    def execute(self, resolution_output):
        """
        Receives structured output from the Resolution Agent.
        """

        incident_id = resolution_output.get("incident_id")
        action = resolution_output.get("recommended_action")
        target_system = resolution_output.get(
            "target_system",
            "local-system"
        )

        result = {
            "incident_id": incident_id,
            "target_system": target_system,
            "action": action,
            "execution_time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "simulation_mode": self.simulation_mode,
            "status": "",
            "message": "",
            "error": None
        }

        try:
            # Validate required information
            if not incident_id:
                result["status"] = "FAILED"
                result["message"] = "Incident ID is missing."
                return result

            if not action:
                result["status"] = "FAILED"
                result["message"] = "Recommended action is missing."
                return result

            # Check whether action is allowed
            if action not in self.allowed_actions:
                result["status"] = "FAILED"
                result["message"] = (
                    f"Action '{action}' is not allowed."
                )
                return result

            # Simulation mode
            if self.simulation_mode:

                if action == "restart_service":
                    result["status"] = "SUCCESS"
                    result["message"] = (
                        f"Service restart simulated successfully "
                        f"on {target_system}."
                    )

                elif action == "check_service_status":
                    result["status"] = "SUCCESS"
                    result["message"] = (
                        f"Service status checked on {target_system}. "
                        f"Service is running."
                    )

                elif action == "check_disk_space":
                    result["status"] = "SUCCESS"
                    result["message"] = (
                        f"Disk space checked on {target_system}. "
                        f"Sufficient disk space is available."
                    )

                elif action == "run_health_check":
                    result["status"] = "SUCCESS"
                    result["message"] = (
                        f"Health check completed on {target_system}. "
                        f"System is healthy."
                    )

            else:
                result["status"] = "PENDING"
                result["message"] = (
                    "Real system execution is disabled for safety."
                )

        except Exception as e:
            result["status"] = "FAILED"
            result["message"] = "Execution failed."
            result["error"] = str(e)

        return result


if __name__ == "__main__":

    print("\n====================================")
    print("       EXECUTION AGENT TEST")
    print("====================================")

    # Simulated output from Resolution Agent
    resolution_output = {
        "incident_id": "INC-101",
        "incident_type": "HDFS DataNode Failure",
        "root_cause": "DataNode service stopped",
        "recommended_action": "restart_service",
        "target_system": "hdfs-node-03"
    }

    print("\nReceived from Resolution Agent:")
    print("------------------------------------")

    for key, value in resolution_output.items():
        print(f"{key}: {value}")

    # Create Execution Agent
    execution_agent = ExecutionAgent(
        simulation_mode=True
    )

    # Execute action
    execution_result = execution_agent.execute(
        resolution_output
    )

    print("\nExecution Agent Result")
    print("------------------------------------")

    for key, value in execution_result.items():
        print(f"{key}: {value}")

    print("------------------------------------")

    if execution_result["status"] == "SUCCESS":
        print("\nExecution successful.")
        print(
            "Result ready for Reporting & Verification Agent."
        )

    elif execution_result["status"] == "PENDING":
        print("\nExecution is pending.")

    else:
        print("\nExecution failed.")