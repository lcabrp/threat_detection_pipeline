import json
import sqlite3
import os
import pandas as pd
import polars as pl
import duckdb

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

def etl_to_sqlite_polars(json_path="data/generated_logs.json", db_path="db/threat_logs.db"):
    """ETL using Polars - faster and more memory efficient"""
    df = (
        pl.read_json(json_path)
        .with_columns([
            pl.col("timestamp").str.to_datetime(),
            pl.col("severity").is_in(["warning", "critical"]).alias("is_suspicious")
        ])
    )
    
    # Write to SQLite using DuckDB for speed
    conn = duckdb.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS threat_logs AS SELECT * FROM df")
    print(f"Inserted {len(df)} logs using Polars + DuckDB")

def etl_to_sqlite_duckdb(json_path="data/generated_logs.json", db_path="db/threat_logs.db"):
    """Pure DuckDB approach - fastest for analytical queries"""
    conn = duckdb.connect(db_path)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS threat_logs AS
        SELECT *,
               severity IN ('warning', 'critical') as is_suspicious,
               strptime(timestamp, '%Y-%m-%dT%H:%M:%S') as parsed_timestamp
        FROM read_json_auto('{json_path}')
    """)
    print("ETL completed using pure DuckDB")
