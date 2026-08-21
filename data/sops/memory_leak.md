# Standard Operating Procedure: Application Memory Leak (memory_leak)

## Overview
This SOP applies when host system memory utilization increases steadily over time, leading to OutOfMemory (OOM) killer terminations.

## Diagnosis Steps
1. Monitor memory growth charts.
2. Check if the process has been killed by OOM killer:
   `dmesg -T | grep -i -E 'oom|kill'`
3. Run `free -m` or inspect GC logs to see memory reclamation metrics.

## Remediation Steps
1. Restart the process immediately to restore service availability:
   `systemctl restart <service>`
2. Take a heap dump for post-mortem analysis:
   `jmap -dump:live,format=b,file=heap.hprof <PID>`
3. Set appropriate JVM heap size parameters (e.g. `-Xmx`).
