# Standard Operating Procedure: Service Crash Loop (crash_loop)

## Overview
This SOP addresses services failing and restarting repeatedly (CrashLoopBackOff). This is typically caused by bad environment variables, missing configs, or database schema mismatches.

## Diagnosis Steps
1. Get the status of the failing container or process:
   `kubectl get pods` or `systemctl status <service>`
2. Fetch the exit code and logs of the previous crashed instance:
   `kubectl logs <pod-name> --previous`
3. Verify if there are dependency/health check errors.

## Remediation Steps
1. Roll back the latest deployment version to a known stable version:
   `kubectl rollout undo deployment/<deployment-name>`
2. Correct missing environment variables or file permissions.
3. Restart dependencies (e.g., database, cache) if they were unreachable during bootstrap.
