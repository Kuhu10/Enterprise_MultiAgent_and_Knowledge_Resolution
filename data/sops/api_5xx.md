# Standard Operating Procedure: High Rate of HTTP 5xx Server Errors (api_5xx)

## Overview
This SOP applies when external HTTP gateways or API servers report excessive 500/502/503/504 response codes.

## Diagnosis Steps
1. Inspect Gateway access logs (e.g., Nginx, Envoy) to identify affected routes.
2. Check upstream microservice status and request latency.
3. Check target microservice error logs for unhandled exceptions or connection errors.

## Remediation Steps
1. Scale up upstream microservice pods to handle request spikes.
2. Apply circuit breaker settings to temporarily reject slow requests.
3. Roll back any recent release that introduced unhandled codebase exceptions.
