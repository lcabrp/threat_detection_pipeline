# 📚 Week 1: Getting Started with Data Engineering

## 🎯 Learning Objectives
By the end of this week, you'll understand:
- Core Data Engineering concepts
- Airflow basics and workflow orchestration
- Data partitioning strategies
- Local development setup

## 🛠 Setup Instructions (Step by Step)

### 1. Install Dependencies
```bash
# Navigate to project directory
cd /app

# Install Python dependencies
pip install -r requirements.txt

# Install Airflow (if not already included)
pip install apache-airflow==2.8.0
```

### 2. Initialize Airflow
```bash
# Set Airflow home (optional, defaults to ~/airflow)
export AIRFLOW_HOME=/app/airflow

# Initialize the database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Data \
    --lastname Engineer \
    --role Admin \
    --email admin@dataeng.com \
    --password admin123
```

### 3. Configure Airflow for Learning
```bash
# Update airflow.cfg (or create airflow.cfg in /app)
# Key settings for learning:
dags_folder = /app/dags
base_log_folder = /app/logs/airflow
sql_alchemy_conn = sqlite:///data/airflow.db
executor = LocalExecutor
load_examples = False
max_active_runs_per_dag = 1
catchup_by_default = False
```

### 4. Start Airflow Services
```bash
# Terminal 1: Start the scheduler
airflow scheduler

# Terminal 2: Start the webserver
airflow webserver --port 8080
```

### 5. Access Airflow UI
- Open browser: http://localhost:8080
- Login: admin / admin123
- You should see your learning DAG: `cybersec_learning_pipeline`

## 🧠 Key Concepts to Understand

### Data Engineering Pipeline Layers
```
Raw Data (Bronze) → Cleaned Data (Silver) → Analytics (Gold)
     ↑                    ↑                      ↑
   As-is data      Validated & enriched    Business insights
```

### Airflow Components
- **DAG**: Directed Acyclic Graph (your workflow)
- **Task**: Individual step in the workflow
- **Operator**: Defines what a task does
- **Scheduler**: Runs tasks based on schedule
- **Executor**: How tasks are executed (LocalExecutor for learning)

### Data Partitioning Strategy
```
data/
├── bronze/logs/date=2025-01-15/logs.json
├── bronze/logs/date=2025-01-16/logs.json
├── silver/validated_logs/date=2025-01-15/cleaned_logs.json
└── gold/daily_summaries/date=2025-01-15_summary.json
```

## 🚀 Your First Pipeline Run

### Step 1: Trigger the DAG
1. Go to Airflow UI (http://localhost:8080)
2. Find `cybersec_learning_pipeline`
3. Toggle it ON (switch on the left)
4. Click "Trigger DAG" (play button)

### Step 2: Monitor Execution
1. Click on the DAG name to see the graph view
2. Watch tasks change colors:
   - **Gray**: Not started
   - **Yellow**: Running
   - **Green**: Success
   - **Red**: Failed

### Step 3: Check Results
```bash
# View generated data
ls -la /app/data/bronze/logs/
ls -la /app/data/silver/validated_logs/
ls -la /app/data/gold/daily_summaries/

# Check a sample file
head /app/data/bronze/logs/date=*/logs.json
cat /app/data/gold/daily_summaries/date=*_summary.json | jq .
```

## 🔍 Understanding the Pipeline

### Task Flow
```
setup_directories → generate_daily_logs → validate_data_quality → transform_to_silver → create_gold_analytics
```

### What Each Task Does

1. **setup_directories**: Creates folder structure
   - *Learning*: Environment preparation
   - *Real-world*: Setting up data lake structure

2. **generate_daily_logs**: Creates synthetic security logs
   - *Learning*: Data ingestion simulation
   - *Real-world*: Reading from APIs, databases, files

3. **validate_data_quality**: Checks data completeness and correctness
   - *Learning*: Data validation concepts
   - *Real-world*: Critical for data trust and reliability

4. **transform_to_silver**: Cleans and enriches data
   - *Learning*: Data transformation patterns
   - *Real-world*: Business rule application, standardization

5. **create_gold_analytics**: Creates business insights
   - *Learning*: Analytics layer concepts
   - *Real-world*: Reports, dashboards, ML features

## 📊 Analyze Your Results

### Check Daily Summary
```bash
# View the analytics created
cat /app/data/gold/daily_summaries/date=*_summary.json | jq '
{
  date: .date,
  total_events: .total_events,
  suspicious_events: .suspicious_events,
  suspicious_rate: .kpis.suspicious_event_rate,
  peak_hour: .kpis.peak_hour,
  top_users: .top_users_by_activity
}
'
```

### Explore Data Quality Report
```bash
# Check data quality metrics
cat /app/data/silver/quality_reports/date=*_report.json | jq '
{
  date: .date,
  total_records: .metrics.total_records,
  quality_passed: .quality_passed,
  null_timestamps: .metrics.null_timestamps,
  invalid_ips: .metrics.invalid_ips
}
'
```

## 🎯 Week 1 Exercises

### Exercise 1: Modify Log Volume
1. Edit the DAG to generate different volumes on weekends
2. Run the pipeline for different dates
3. Compare the results

### Exercise 2: Add New Data Quality Check
1. Add a check for valid event types
2. Update the validation function
3. Test with intentionally bad data

### Exercise 3: Create Custom Analytics
1. Add a new metric to the gold layer (e.g., top source IPs by suspicious activity)
2. Modify the `create_gold_analytics` function
3. Verify the new metric appears in results

### Exercise 4: Understand Task Dependencies
1. Try removing a dependency (comment out `>>` in the DAG)
2. See what happens when you run the pipeline
3. Restore the dependency and explain why it's needed

## 🛠 Troubleshooting

### Common Issues

**DAG not appearing in UI**
```bash
# Check DAG syntax
python /app/dags/cybersec_learning_dag.py

# Check Airflow logs
tail -f /app/logs/airflow/scheduler/latest/*.log
```

**Task failing**
```bash
# Check specific task logs in Airflow UI
# Or from command line:
airflow tasks logs cybersec_learning_pipeline generate_daily_logs 2025-01-15 1
```

**Airflow won't start**
```bash
# Check if port 8080 is in use
lsof -i :8080

# Check Airflow processes
ps aux | grep airflow

# Reset if needed
airflow db reset  # WARNING: This deletes all data
```

## 📚 Additional Learning Resources

### Recommended Reading
- [Airflow Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html)
- [Data Engineering Cookbook](https://github.com/andkret/Cookbook)
- [The Data Engineering Handbook](https://github.com/DataExpert-io/data-engineer-handbook)

### SQL Practice
- Work through `/app/sql/queries/learning_queries.sql`
- Practice window functions with your generated data
- Try the anomaly detection queries

### Next Week Preview
- Database integration (SQLite → PostgreSQL)
- Advanced Airflow features (sensors, branching)
- Data validation with Great Expectations
- Performance monitoring and optimization

## ✅ Week 1 Checklist

- [ ] Airflow installed and running
- [ ] First DAG executed successfully
- [ ] Data generated in all three layers (Bronze/Silver/Gold)
- [ ] Understand pipeline task flow
- [ ] Completed at least 2 exercises
- [ ] Read additional resources
- [ ] Ready for Week 2 challenges

---

**🎓 Congratulations!** You've completed your first week of Data Engineering learning. You now have a foundation in pipeline orchestration and data processing concepts.