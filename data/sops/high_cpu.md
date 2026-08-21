# Standard Operating Procedure: High CPU Saturation (high_cpu)

## Overview
This SOP details procedures to resolve CPU utilization exceeding 95% on application hosts, causing slow response times and timeouts.

## Diagnosis Steps
1. Log in to the affected server.
2. Run `top` or `htop` to identify CPU-hogging processes.
3. Check the process threads consuming CPU:
   `ps -H -eo pid,tid,%cpu,cmd --sort=-%cpu | head -20`

## Remediation Steps
1. Kill orphan background processes that are taking up CPU:
   `kill -9 <PID>`
2. If the culprit is a JVM process, take a thread dump to check for infinite loops:
   `jcmd <PID> Thread.print > thread_dump.txt`
3. Dynamically scale the container instance size or scale horizontally by adding more instances.
