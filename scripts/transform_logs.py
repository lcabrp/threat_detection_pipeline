import pandas as pd
import re
import json

def transform_logs(log_file: str = "data/sample_logs.json") -> pd.DataFrame:
    """
    Transforms log data by identifying suspicious events and saving alerts to a JSON file.

    This function extracts logs from a source, converts them into a pandas DataFrame,
    and marks events as suspicious if they contain keywords such as "Failed", "brute force",
    or "scan". It filters the DataFrame for suspicious events and writes these to a JSON
    file 'data/alerts.json'. The filtered DataFrame of suspicious events is returned.

    Returns:
        pandas.DataFrame: A DataFrame containing only the suspicious log events.
    """
    try:
        with open(log_file, "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {log_file} was not found.")
        return pd.DataFrame([])
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {log_file}.")
        return pd.DataFrame([])

    df = pd.DataFrame(logs)
    df["suspicious"] = df["event"].apply(lambda x: bool(re.search(r"(Failed|brute force|scan)", x, re.IGNORECASE)))
    suspicious_df = df[df["suspicious"]]
    suspicious_df.to_json("data/alerts.json", orient="records")
    return suspicious_df


if __name__ == "__main__":
    transform_logs()