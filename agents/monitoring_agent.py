import os
import re

class LogMonitoringAgent:
    """
    A rule-based monitoring agent to parse HDFS system logs, detect anomalies
    using keyword matching, and extract structured incident contexts for diagnostic agents.
    """
    def __init__(self, keywords=None):
        # Default keywords that trigger anomaly flags (case-insensitive)
        if keywords is None:
            self.anomaly_keywords = ["error", "fatal", "timeout", "outofmemory", "crash", "failed", "exception"]
        else:
            self.anomaly_keywords = [k.lower() for k in keywords]
            
        # Regex to parse HDFS log format: Date Time ThreadId Level Component: Message
        # Example: "081109 203615 148 INFO dfs.DataNode$PacketResponder: PacketResponder 1 ..."
        self.log_pattern = re.compile(r'^(\d{6})\s+(\d{6})\s+(\d+)\s+(\S+)\s+([^:]+):\s+(.*)$')

    def parse_line(self, line: str, line_num: int) -> dict:
        """
        Parses a single HDFS log line into a structured dictionary.
        """
        line_clean = line.strip()
        match = self.log_pattern.match(line_clean)
        
        if match:
            date_str, time_str, thread_id, level, component, message = match.groups()
            
            # Format date (yymmdd -> 20yy-mm-dd) and time (hhmmss -> hh:mm:ss)
            try:
                formatted_date = f"20{date_str[0:2]}-{date_str[2:4]}-{date_str[4:6]}"
                formatted_time = f"{time_str[0:2]}:{time_str[2:4]}:{time_str[4:6]}"
                timestamp = f"{formatted_date} {formatted_time}"
            except Exception:
                timestamp = f"{date_str} {time_str}"
                
            return {
                "timestamp": timestamp,
                "level": level,
                "component": component,
                "message": message,
                "raw": line_clean,
                "line_number": line_num
            }
        else:
            # Fallback for non-standard lines
            return {
                "timestamp": "Unknown",
                "level": "UNKNOWN",
                "component": "System",
                "message": line_clean,
                "raw": line_clean,
                "line_number": line_num
            }

    def calculate_anomaly_score(self, level: str, message: str) -> float:
        """
        Determines the anomaly score based on severity and keyword matches.
        Scores range from 0.0 (no anomaly) to 1.0 (critical error).
        """
        msg_lower = message.lower()
        level_lower = level.lower()
        
        # Determine score based on severity keywords
        if "fatal" in msg_lower or "crash" in msg_lower or "outofmemory" in msg_lower or level_lower == "fatal":
            return 0.95
        elif "error" in msg_lower or level_lower == "error":
            return 0.85
        elif "exception" in msg_lower or "failed" in msg_lower:
            return 0.75
        elif "timeout" in msg_lower:
            return 0.70
        elif "warn" in msg_lower or level_lower == "warn":
            return 0.50
        
        # Catch-all if any other custom keyword matched
        return 0.30

    def get_incidents(self, log_file_path: str) -> list[dict]:
        """
        Reads the log file, parses entries, detects anomalies, and packages
        them with 2 lines of surrounding context (before and after).
        """
        if not os.path.exists(log_file_path):
            print(f"Error: Log file not found at '{log_file_path}'")
            return []

        with open(log_file_path, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()

        incidents = []
        parsed_entries = []

        # Step 1: Parse all lines to build sequential context
        for idx, line in enumerate(raw_lines, 1):
            parsed_entries.append(self.parse_line(line, idx))

        # Step 2: Detect anomalies and capture surrounding context
        for idx, entry in enumerate(parsed_entries):
            message = entry["message"]
            level = entry["level"]
            
            # Check if any anomaly keyword is present in the message or log level
            has_anomaly = (
                any(keyword in message.lower() for keyword in self.anomaly_keywords) or
                any(keyword in level.lower() for keyword in self.anomaly_keywords)
            )
            
            if has_anomaly:
                anomaly_score = self.calculate_anomaly_score(level, message)
                
                # Fetch 2 lines before and 2 lines after for context
                start_ctx = max(0, idx - 2)
                end_ctx = min(len(parsed_entries), idx + 3) # Slice end is exclusive
                
                # Format surrounding context as a single readable block
                context_lines = []
                for j in range(start_ctx, end_ctx):
                    prefix = "--> " if j == idx else "    "
                    context_lines.append(f"{prefix}Line {parsed_entries[j]['line_number']}: {parsed_entries[j]['raw']}")
                
                surrounding_context_str = "\n".join(context_lines)

                # Append structured incident
                incidents.append({
                    "timestamp": entry["timestamp"],
                    "source_system": entry["component"],
                    "raw_log_snippet": entry["raw"],
                    "anomaly_score": anomaly_score,
                    "surrounding_context": surrounding_context_str,
                    "line_number": entry["line_number"]
                })

        return incidents

if __name__ == "__main__":
    # Test path to HDFS sample logs
    sample_log_path = os.path.join("data", "raw_logs", "HDFS_2k.log")
    
    print("--- Log Monitoring Agent Test ---")
    print(f"Reading logs from: {sample_log_path}")
    
    agent = LogMonitoringAgent()
    incidents = agent.get_incidents(sample_log_path)
    
    print(f"Total lines processed: 2000")
    print(f"Total anomalies flagged: {len(incidents)}")
    
    if incidents:
        print("\n--- Printing First 5 Flagged Incidents ---")
        for idx, incident in enumerate(incidents[:5], 1):
            print(f"\n[Incident #{idx}]")
            print(f"Timestamp:      {incident['timestamp']}")
            print(f"Source System:  {incident['source_system']}")
            print(f"Line Number:    {incident['line_number']}")
            print(f"Anomaly Score:  {incident['anomaly_score']}")
            print(f"Raw Log:        {incident['raw_log_snippet']}")
            print("Surrounding Context:")
            print(incident['surrounding_context'])
            print("="*60)
    else:
        print("No incidents found in log file.")
