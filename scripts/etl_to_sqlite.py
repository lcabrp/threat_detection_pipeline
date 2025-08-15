import json
import sqlite3
import os
import pandas as pd

def etl_to_sqlite(json_path="data/generated_logs.json", db_path="db/threat_logs.db"):
    """
    Loads JSON logs, transforms them with Pandas, and inserts them into an SQLite DB.

    :param json_path: Path to JSON log file.
    :param db_path: Path to SQLite DB.
    """
    try:
        with open(json_path, "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {json_path} was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_path}.")
        return

    if not logs:
        print("Error: No logs to process.")
        return

    # Transform with Pandas
    try:
        df = pd.DataFrame(logs)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
        df["is_suspicious"] = df["severity"].isin(["warning", "critical"])
    except KeyError as e:
        print(f"Error: Missing expected key in logs - {str(e)}")
        return

    # Connect to SQLite
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(f"Error: SQLite connection failed - {str(e)}")
        return

    # Insert logs
    try:
        df.to_sql("threat_logs", conn, if_exists="append", index=False, method="multi")
        conn.commit()
        print(f"Inserted {len(df)} logs into {db_path}")
    except sqlite3.Error as e:
        print(f"Error: Failed to insert logs into SQLite - {str(e)}")
    finally:
        conn.close()
