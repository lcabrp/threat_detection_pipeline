import json

def extract_logs():
    """
    Extracts the sample logs from the JSON file and returns them as a list of
    dictionaries.

    Returns:
        list: A list of log dictionaries, each containing the timestamp, source_ip,
              destination_ip, port, and event of each log entry.
    """
    with open("data/sample_logs.json", "r") as f:
        logs = json.load(f)
    return logs