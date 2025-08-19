# benchmark.py
import time
import pandas as pd
import modin.pandas as mpd
import polars as pl
import duckdb
import platform
import modin.config as cfg
import logging
import warnings
import sys
import os
from contextlib import redirect_stderr

# Check if FireDucks is available (Linux/macOS only)
FIREDUCKS_AVAILABLE = False
if platform.system() in ['Linux', 'Darwin']:  # Darwin = macOS
    try:
        import fireducks.pandas as fpd
        FIREDUCKS_AVAILABLE = True
    except ImportError:
        pass

CSV_PATH = "data/synthetic_logs_test.csv"

def setup_modin():
    """Initialize Modin with proper Dask configuration"""
    cfg.Engine.put("dask")
    logging.getLogger("distributed").setLevel(logging.CRITICAL)
    logging.getLogger("tornado").setLevel(logging.CRITICAL)
    warnings.filterwarnings("ignore")

def benchmark_pandas():
    start = time.time()
    df = pd.read_csv(CSV_PATH)
    result = df[df["status_code"] == 200].groupby("source_ip").agg({"bytes": "sum"})
    duration = time.time() - start
    print(f"Pandas duration: {duration:.2f}s")
    return result

def benchmark_modin():
    start = time.time()
    df = mpd.read_csv(CSV_PATH)
    result = df[df["status_code"] == 200].groupby("source_ip").agg({"bytes": "sum"})
    duration = time.time() - start
    print(f"Modin duration: {duration:.2f}s")
    return result

def benchmark_polars():
    start = time.time()
    df = pl.read_csv(CSV_PATH)
    result = (
        df.filter(pl.col("status_code") == 200)
          .group_by("source_ip")
          .agg(pl.sum("bytes"))
    )
    duration = time.time() - start
    print(f"Polars duration: {duration:.2f}s")
    return result

def benchmark_duckdb():
    start = time.time()
    conn = duckdb.connect()
    result = conn.execute(f"""
        SELECT source_ip, SUM(bytes) as bytes
        FROM read_csv_auto('{CSV_PATH}')
        WHERE status_code = 200
        GROUP BY source_ip
    """).fetchdf()
    duration = time.time() - start
    print(f"DuckDB duration: {duration:.2f}s")
    return result

def benchmark_fireducks():
    if not FIREDUCKS_AVAILABLE:
        print("FireDucks not available on Windows")
        return None
    
    start = time.time()
    df = fpd.read_csv(CSV_PATH)
    result = df[df["status_code"] == 200].groupby("source_ip").agg({"bytes": "sum"})
    duration = time.time() - start
    print(f"FireDucks duration: {duration:.2f}s")
    return result

if __name__ == "__main__":
    setup_modin()
    pd.set_option('display.float_format', '{:.0f}'.format)
    
    print("Running Pandas benchmark...")
    pandas_result = benchmark_pandas()
    print(pandas_result)

    print("Running Modin benchmark...")
    modin_result = benchmark_modin()
    print(modin_result)

    print("\nRunning Polars benchmark...")
    polars_result = benchmark_polars()
    print(polars_result)
    
    print("\nRunning DuckDB benchmark...")
    duckdb_result = benchmark_duckdb()
    print(duckdb_result)
    
    print("\nRunning FireDucks benchmark...")
    fireducks_result = benchmark_fireducks()
    if fireducks_result is not None:
        print(fireducks_result)
    
    print("\nBenchmark completed!")
    
    # Suppress any remaining output
    with redirect_stderr(open(os.devnull, 'w')):
        time.sleep(0.1)  # Brief pause for cleanup
