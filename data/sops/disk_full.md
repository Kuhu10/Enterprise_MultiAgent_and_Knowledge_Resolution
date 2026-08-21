# Standard Operating Procedure: Disk Space Full (disk_full)

## Overview
This SOP addresses disk saturation alerts (100% capacity) on system nodes. When disk space is full, services cannot write temporary files, logs, or blocks, causing immediate crashes or network timeouts.

## Diagnosis Steps
1. SSH into the reported host.
2. Check disk usage metrics:
   `df -h`
3. Identify the largest directories under root or data mount:
   `du -sh /* 2>/dev/null | sort -hr | head -n 10`

## Remediation Steps
1. Clean up obsolete system logs and temporary files:
   `sudo rm -rf /var/log/nginx/*.gz`
2. Run log rotation:
   `sudo logrotate -f /etc/logrotate.conf`
3. For HDFS DataNodes, run the balancer to redistribute data blocks:
   `hdfs balancer -threshold 10`
