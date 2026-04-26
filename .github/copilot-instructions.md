# Cybersecurity Data Engineering Learning Project — Copilot Instructions

This repo is a **hands-on learning project** for data engineering with Airflow, focused on building a threat detection pipeline using cybersecurity logs. Primary focus: learning Airflow DAGs, implementing Bronze/Silver/Gold architecture, and building data transformation workflows.

**Learning Goal:** Master Airflow fundamentals and data engineering patterns  
**Domain:** Cybersecurity threat detection (synthetic logs)  
**Tech Stack:** Python 3.13, Apache Airflow 3.0, pandas, polars, DuckDB, SQLite  
**Architecture:** Bronze/Silver/Gold medallion architecture

---

## Project Structure

```
threat_detection_pipeline/
├── dags/
│   ├── cybersec_learning_dag.py       # Learning-focused DAG examples
│   ├── synthetic_log_pipeline.py      # Log generation pipeline
│   └── threat_etl_dag.py              # Main ETL pipeline
├── scripts/
│   ├── extract_logs.py                # Extract from log files
│   ├── transform_logs.py              # Transform and enrich
│   ├── load_to_splunk.py              # Load to destination
│   └── etl_to_sqlite.py               # ETL to SQLite database
├── data/
│   ├── generated_logs.json            # Synthetic log data
│   └── raw/                           # Raw log files
├── sql/                               # SQL queries and schemas
├── db/                                # SQLite databases
├── docs/
│   └── learning_notes/
│       └── understanding_dags.md      # ⭐ START HERE
├── learning_plan.md                   # Structured 8-week learning path
├── YOUR_LEARNING_PATH.md              # Personal progress tracker
└── pyproject.toml                     # Dependencies
```

---

## Airflow Conventions

### DAG Definition Pattern

**Standard DAG structure:**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Define DAG with context manager
with DAG(
    dag_id="my_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",  # or cron expression
    catchup=False,  # Don't run historical DAG runs
    tags=['learning', 'etl']
) as dag:
    
    # Define tasks
    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_function,
        op_kwargs={'param1': 'value1'}
    )
    
    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_function
    )
    
    load_task = PythonOperator(
        task_id="load_data",
        python_callable=load_function
    )
    
    # Define dependencies
    extract_task >> transform_task >> load_task
```

### Task Dependencies

**Multiple dependency patterns:**

```python
# Linear dependency
task1 >> task2 >> task3

# Fan-out (parallel tasks)
task1 >> [task2, task3, task4]

# Fan-in (join parallel tasks)
[task1, task2, task3] >> task4

# Mixed
task1 >> [task2, task3] >> task4
```

### Python Callable Pattern

```python
def my_task_function(**context):
    """
    Standard Airflow task function.
    
    Args:
        **context: Airflow context with execution_date, task_instance, etc.
    
    Returns:
        Any: Value pushed to XCom (for task communication)
    """
    # Task logic here
    print(f"Running task at {context['execution_date']}")
    
    # Optional: return value for XCom
    return {"status": "success", "records": 1000}

# Wrapper for existing functions
def wrapper_function():
    """
    Wrapper to call existing scripts/functions from DAGs.
    Useful for organizing code outside DAG files.
    """
    from scripts.extract_logs import extract_logs
    extract_logs()
```

---

## Bronze/Silver/Gold Architecture

### Data Quality Layers

**Bronze (Raw):**
- Unprocessed data as-is from source
- No schema enforcement
- Minimal validation
- Location: `data/raw/` or `bronze/` tables

```python
# Bronze layer: Ingest raw logs
def ingest_raw_logs():
    """Read raw log files without transformation"""
    with open('logs/system.log', 'r') as f:
        raw_data = f.read()
    # Store as-is in bronze layer
    save_to_bronze(raw_data)
```

**Silver (Cleaned):**
- Parsed and structured
- Data quality checks applied
- Schema enforcement
- Deduplication
- Location: `data/silver/` or `silver/` tables

```python
# Silver layer: Clean and structure
def clean_logs():
    """Parse, validate, and structure raw logs"""
    raw_data = load_from_bronze()
    
    # Parse log format
    parsed = parse_log_lines(raw_data)
    
    # Data quality checks
    validated = apply_validation_rules(parsed)
    
    # Remove duplicates
    deduplicated = remove_duplicates(validated)
    
    save_to_silver(deduplicated)
```

**Gold (Analytics-Ready):**
- Aggregated metrics
- Business logic applied
- Optimized for queries
- Threat detection algorithms
- Location: `data/gold/` or `gold/` tables

```python
# Gold layer: Create analytics views
def create_threat_metrics():
    """Generate threat detection metrics"""
    silver_data = load_from_silver()
    
    # Aggregate by time windows
    hourly_stats = aggregate_hourly(silver_data)
    
    # Apply threat detection logic
    threats = detect_anomalies(hourly_stats)
    
    # Create analytics tables
    save_to_gold(threats)
```

---

## Python/ETL Conventions

### Script Organization

**Separation of concerns:**

```
scripts/
├── extract_logs.py        # Source system extraction
├── transform_logs.py      # Data transformation logic
├── load_to_splunk.py      # Destination loading
└── etl_to_sqlite.py       # Full ETL for SQLite
```

**Keep DAG files clean:**
- DAG files: Define workflow structure only
- Script files: Contain business logic
- Utils: Shared functions and utilities

### Data Processing Patterns

**pandas for small datasets:**

```python
import pandas as pd

def process_logs_pandas():
    """Process logs with pandas (< 1GB)"""
    df = pd.read_json('data/generated_logs.json')
    
    # Filter suspicious activity
    threats = df[df['severity'] == 'critical']
    
    # Aggregate
    summary = threats.groupby('source_ip').agg({
        'event_count': 'sum',
        'unique_events': 'nunique'
    })
    
    return summary
```

**polars for larger datasets:**

```python
import polars as pl

def process_logs_polars():
    """Process logs with polars (1-10GB)"""
    lf = pl.scan_json('data/generated_logs.json')
    
    # Lazy evaluation
    threats = lf.filter(pl.col('severity') == 'critical')
    
    # Aggregate (executes on .collect())
    summary = threats.group_by('source_ip').agg([
        pl.col('event_count').sum(),
        pl.col('event_type').n_unique().alias('unique_events')
    ]).collect()
    
    return summary
```

**DuckDB for analytical queries:**

```python
import duckdb

def analyze_with_duckdb():
    """Run SQL analytics on logs"""
    conn = duckdb.connect('db/threat_logs.db')
    
    result = conn.execute("""
        SELECT 
            source_ip,
            COUNT(*) as event_count,
            COUNT(DISTINCT event_type) as unique_events,
            MAX(timestamp) as last_seen
        FROM logs
        WHERE severity = 'critical'
        GROUP BY source_ip
        HAVING event_count > 10
        ORDER BY event_count DESC
    """).df()
    
    conn.close()
    return result
```

---

## Airflow Commands

### Development Workflow

```bash
# Initialize Airflow database (first time only)
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Start services (2 terminals)
# Terminal 1: Scheduler
airflow scheduler

# Terminal 2: Webserver
airflow webserver --port 8080

# Access UI: http://localhost:8080
# Login: admin / admin
```

### DAG Management

```bash
# List all DAGs
airflow dags list

# Show DAG structure
airflow dags show threat_etl_pipeline

# Test a task (without dependencies)
airflow tasks test dag_id task_id 2025-01-01

# Run a task (with dependencies)
airflow tasks run dag_id task_id 2025-01-01

# Trigger DAG manually
airflow dags trigger dag_id

# Pause/unpause DAG
airflow dags pause dag_id
airflow dags unpause dag_id
```

### Debugging

```bash
# Check task logs
airflow tasks logs dag_id task_id 2025-01-01 1

# List task instances
airflow tasks list dag_id

# Clear task state (to re-run)
airflow tasks clear dag_id

# Test Python file syntax
python dags/my_dag.py  # Should run without errors
```

---

## Learning Path Structure

### Week-by-Week Plan (learning_plan.md)

**Week 1-2: Airflow Basics**
- ✅ Understand DAGs (START: `docs/learning_notes/understanding_dags.md`)
- Set up local Airflow
- Create first DAG
- Implement daily log generation
- Add basic data quality checks

**Week 3-4: Data Architecture**
- Implement Bronze/Silver/Gold layers
- Add data validation pipelines
- Create analytical transformations
- Build threat detection algorithms

**Week 5-6: Advanced Workflows**
- Parallel processing patterns
- Error handling and recovery
- Performance monitoring
- Real-time alerting

**Week 7-8: Cloud Deployment**
- Containerize with Docker
- Deploy to cloud platform
- Set up production monitoring
- Implement cost optimization

### Personal Progress (YOUR_LEARNING_PATH.md)

Track your progress:
- [ ] Completed tasks (check off as you go)
- [ ] Current blockers
- [ ] Questions for research
- [ ] Key learnings

---

## Threat Detection Patterns

### Anomaly Detection

```python
def detect_anomalies(df):
    """
    Identify suspicious patterns in log data.
    
    Detection rules:
    - High event count from single IP (DDoS indicator)
    - Failed login attempts > threshold (brute force)
    - Unusual time patterns (off-hours activity)
    - Geographic anomalies (impossible travel)
    """
    anomalies = []
    
    # High event count
    high_volume = df[df['event_count'] > 1000]
    anomalies.append(high_volume)
    
    # Failed logins
    failed_logins = df[
        (df['event_type'] == 'login_failed') & 
        (df['count'] > 5)
    ]
    anomalies.append(failed_logins)
    
    return pd.concat(anomalies)
```

### Time-Based Analysis

```python
def analyze_time_patterns(df):
    """
    Analyze temporal patterns in threat data.
    
    Patterns to detect:
    - Hourly spikes
    - Weekend vs weekday differences
    - Off-hours activity
    - Sustained attacks
    """
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
    
    # Hourly aggregation
    hourly = df.groupby('hour')['event_count'].sum()
    
    # Off-hours threshold (2am-6am)
    off_hours = df[df['hour'].between(2, 6)]
    
    return hourly, off_hours
```

---

## Common Workflows

### Creating New DAG

1. **Design workflow:** Draw task dependencies on paper
2. **Create DAG file:** Copy template from existing DAG
3. **Define tasks:** Write or wrap Python callables
4. **Set dependencies:** Use `>>` operator
5. **Test syntax:** `python dags/new_dag.py`
6. **Test task:** `airflow tasks test dag_id task_id 2025-01-01`
7. **Enable in UI:** Unpause DAG in Airflow web interface

### Implementing Bronze/Silver/Gold

1. **Bronze:** Create ingest task (raw data as-is)
2. **Silver:** Add cleaning task (parse, validate, deduplicate)
3. **Gold:** Add analytics task (aggregate, detect threats)
4. **Connect layers:** Bronze >> Silver >> Gold
5. **Add quality checks:** Validate between layers

### Debugging Failed Tasks

1. **Check Airflow UI:** View task logs in web interface
2. **Run task test:** `airflow tasks test dag_id task_id 2025-01-01`
3. **Check syntax:** `python dags/dag_file.py`
4. **Review logs:** `airflow tasks logs dag_id task_id`
5. **Fix issue:** Update code
6. **Clear state:** `airflow tasks clear dag_id task_id`
7. **Re-run:** Trigger DAG again

---

## Testing Patterns

### Unit Testing Tasks

```python
import pytest
from scripts.transform_logs import clean_logs

def test_clean_logs():
    """Test log cleaning function"""
    # Arrange
    raw_data = [
        {"ip": "192.168.1.1", "event": "login"},
        {"ip": "192.168.1.1", "event": "login"},  # duplicate
    ]
    
    # Act
    result = clean_logs(raw_data)
    
    # Assert
    assert len(result) == 1  # Duplicate removed
    assert result[0]['ip'] == "192.168.1.1"
```

### Integration Testing DAGs

```python
# Test DAG structure and dependencies
def test_dag_structure():
    from dags.threat_etl_dag import dag
    
    # Check DAG exists
    assert dag is not None
    
    # Check task count
    assert len(dag.tasks) == 3
    
    # Check dependencies
    extract_task = dag.get_task('extract_logs')
    downstream = extract_task.downstream_task_ids
    assert 'transform_logs' in downstream
```

---

## Troubleshooting

### Common Issues

**DAG not appearing:**
- Check syntax: `python dags/my_dag.py`
- Check logs in Airflow UI
- Verify DAG file is in `dags/` directory
- Restart scheduler

**Task failures:**
- Review task logs in UI
- Test task in isolation
- Check file paths (relative vs absolute)
- Verify database connections

**Database locked (SQLite):**
- Only one write operation at a time
- Restart scheduler if stuck
- Consider PostgreSQL for production

**Port 8080 already in use:**
- Change port: `airflow webserver --port 8081`
- Or kill process on 8080

---

## Learning Resources

### Documentation

- **Airflow Official Docs:** https://airflow.apache.org/docs/
- **Data Engineering Zoomcamp:** https://github.com/DataTalksClub/data-engineering-zoomcamp
- **SQL Window Functions:** https://mode.com/sql-tutorial/sql-window-functions/

### Project Documentation

- **Understanding DAGs:** `docs/learning_notes/understanding_dags.md` (⭐ START HERE)
- **Learning Plan:** `learning_plan.md` (8-week structured path)
- **Progress Tracker:** `YOUR_LEARNING_PATH.md` (personal checklist)

---

## Project Scope

### Learning Project

**This is educational code:**
- Focus on learning Airflow concepts
- Synthetic data (not real threats)
- Simplified implementations
- Local development environment

**Not production-ready:**
- No authentication/authorization
- No monitoring/alerting
- No high availability
- No cloud deployment (yet)

### Progression Path

1. **Current:** Local Airflow, SQLite, basic DAGs
2. **Next:** Docker containerization, PostgreSQL
3. **Future:** Cloud deployment (AWS/GCP/Azure), production monitoring

---

## References

- **Airflow Documentation:** https://airflow.apache.org/docs/
- **Apache Airflow GitHub:** https://github.com/apache/airflow
- **Data Engineering Best Practices:** See learning_plan.md
- **Cybersecurity Patterns:** Industry standard threat detection algorithms
