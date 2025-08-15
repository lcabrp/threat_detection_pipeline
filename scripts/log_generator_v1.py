# scripts/log_generator.py
import json
import random
import numpy as np
import datetime as dt
import ipaddress
import time

def generate_log_entry() -> dict:
    """
    Generates a random log entry with a timestamp, source IP, destination IP, port, protocol, event, severity, and action.

    Returns:
        dict: A dictionary containing the generated log entry.
    """
    ip_range = range(2, 255)
    ports = [22, 80, 443, 3389, 53]
    protocols = ["TCP", "UDP"]
    events = [
        {"event": "Failed SSH login", "severity": "warning", "actions": ["ignored", "blocked"]},
        {"event": "RDP brute force attempt", "severity": "critical", "actions": ["blocked", "reported"]},
        {"event": "Suspicious DNS activity", "severity": "info", "actions": ["monitored", "allowed"]},
        {"event": "Failed SSH login", "severity": "warning", "actions": ["ignored", "blocked"]},
        {"event": "RDP brute force attempt", "severity": "critical", "actions": ["blocked", "reported"]},
        {"event": "Suspicious DNS activity", "severity": "info", "actions": ["monitored", "allowed"]},
        {"event": "Port scan detected", "severity": "warning", "actions": ["blocked", "rate limited"]},
        {"event": "Malware signature match", "severity": "critical", "actions": ["quarantined", "eradicated"]},
        {"event": "Suspicious file activity", "severity": "critical", "actions": ["blocked", "eradicated"]},
        {"event": "Unusual login location", "severity": "warning", "actions": ["monitored", "verified"]},
        {"event": "Failed login attempts", "severity": "warning", "actions": ["blocked", "rate limited"]},
        {"event": "Potential SQL injection attempt", "severity": "critical", "actions": ["blocked", "reported"]},
        {"event": "Cross-site scripting (XSS) attempt", "severity": "critical", "actions": ["blocked", "reported"]},
        {"event": "System file modification", "severity": "warning", "actions": ["monitored", "verified"]},
        {"event": "Malware outbreak detected", "severity": "critical", "actions": ["quarantined", "eradicated"]},
        {"event": "Denial of Service (DoS) attack detected", "severity": "critical", "actions": ["blocked", "reported"]},
        {"event": "Potential data exfiltration attempt", "severity": "critical", "actions": ["blocked", "reported"]},
        {"event": "Suspicious network traffic", "severity": "warning", "actions": ["monitored", "scanned"]}
    ]

    event = random.choice(events)
    action = random.choice(event["actions"])

    # Make the severity more dynamic
    if event["event"] == "RDP brute force attempt" and random.random() < 0.5:
        event["severity"] = "high"
    
    # Generate random timestamp starting two weeks ago
    start_time = dt.datetime.now(dt.timezone.utc) - dt.timedelta(weeks=2)

    # Using random(slower)
    random_time = start_time + dt.timedelta(seconds=random.randint(0, int(dt.timedelta(weeks=2).total_seconds())))
    timestamp = random_time.isoformat(timespec='seconds').replace("+00:00", "Z")

    # Using numpy(faster)
    #random_ts = np.random.uniform(start_time.timestamp(), dt.datetime.now(dt.timezone.utc).timestamp())
    #timestamp = dt.datetime.fromtimestamp(random_ts, tz=dt.timezone.utc).isoformat(timespec='seconds').replace("+00:00", "Z")

    # Generate random IP address from 10.1.26.0/8 range
    network = ipaddress.ip_network('10.1.26.0/24', strict=False)
    destination_ip = str(ipaddress.ip_address(random.randint(int(network.network_address), int(network.broadcast_address))))
    return {
        "timestamp": timestamp,
        "source_ip": f"192.168.1.{random.randrange(2, 255)}",
        "destination_ip": destination_ip,
        "port": random.choice(ports),
        "protocol": random.choice(protocols),
        "event": event["event"],
        "severity": event["severity"],
        "action": action
    }
def generate_logs(n: int = 1000, output_file: str = "data/generated_logs.json") -> None:
    """
    Generates a specified number of log entries and writes them to a JSON file.

    Args:
        n (int): The number of log entries to generate. Defaults to 1000.
        output_file (str): The path to the JSON file where the logs will be written. Defaults to "data/generated_logs.json".

    Raises:
        ValueError: If n is not a positive integer or if output_file does not end with .json.

    Returns:
        None
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")
    if not isinstance(output_file, str) or not output_file.endswith(".json"):
        raise ValueError("output_file must be a string ending with .json")

    try:
        logs = [generate_log_entry() for _ in range(n)]
        logs = [log for log in logs if log is not None]  # Filter out any None log entries
        with open(output_file, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"An error occurred while generating logs: {e}")

def main():
    """
    Generates 100,000 log entries and writes them to data/generated_logs.json,
    printing the time taken to do so.

    Returns:
        None
    """
    start_time = time.time()
    generate_logs(n=1000_000)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()