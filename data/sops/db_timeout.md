# Standard Operating Procedure: Database Connection Timeout (db_timeout)

## Overview
This SOP applies when database read/write queries timeout or throw pool exhaustion exceptions (e.g. `java.net.SocketTimeoutException` or `ConnectionTimeout`).

## Diagnosis Steps
1. Verify if the database service (MySQL/PostgreSQL) is running:
   `systemctl status postgresql` or `systemctl status mysql`
2. Check lock tables and active queries:
   `SELECT pid, query, state, age(clock_timestamp(), query_start) FROM pg_stat_activity WHERE state != 'idle';`
3. Inspect system CPU and memory load on the database node.

## Remediation Steps
1. Terminate long-running blocking queries causing lock contentions.
2. If connection pooling is exhausted, temporarily increase connection limits in config:
   `max_connections = 250` (and restart the database service).
3. Ensure the application-side pool configuration specifies a reasonable connection lifetime.
