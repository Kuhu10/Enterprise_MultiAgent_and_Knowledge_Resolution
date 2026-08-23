from data.test_dataset_to_execution import analyse_hdfs_log
from agents.execution_agent import ExecutionAgent


tests = [
    {
        "file": "data/test_logs/datanode_test.log",
        "expected_action": "restart_service"
    },
    {
        "file": "data/test_logs/disk_test.log",
        "expected_action": "check_disk_space"
    },
    {
        "file": "data/test_logs/healthy_test.log",
        "expected_action": "run_health_check"
    }
]


agent = ExecutionAgent(simulation_mode=True)

passed = 0

for test in tests:
    resolution = analyse_hdfs_log(test["file"])

    result = agent.execute(resolution)

    expected = test["expected_action"]
    actual = resolution["recommended_action"]

    print("\nFile:", test["file"])
    print("Expected:", expected)
    print("Actual:", actual)
    print("Execution:", result["status"])

    if actual == expected and result["status"] == "SUCCESS":
        print("TEST PASSED")
        passed += 1
    else:
        print("TEST FAILED")


print("\n==============================")
print(f"Passed {passed}/{len(tests)} tests")
print("==============================")