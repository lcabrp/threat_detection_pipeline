# 🎓 Cybersecurity Data Engineering Learning Project

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize Airflow database
airflow db init

# Create Airflow admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### 2. Start Airflow
```bash
# Terminal 1: Start Airflow scheduler
airflow scheduler

# Terminal 2: Start Airflow webserver  
airflow webserver --port 8080
```

### 3. Access Airflow UI
- Open browser: http://localhost:8080
- Login: admin / admin

## 📚 Learning Path

### Week 1-2: Airflow Basics
- [ ] **FIRST: Understand DAGs** (`docs/learning_notes/understanding_dags.md`)
- [ ] Set up local Airflow environment
- [ ] Create your first DAG
- [ ] Implement daily log generation
- [ ] Add basic data quality checks

### Week 3-4: Data Architecture
- [ ] Implement Bronze/Silver/Gold layers
- [ ] Add data validation pipelines
- [ ] Create analytical transformations
- [ ] Build threat detection algorithms

### Week 5-6: Advanced Workflows
- [ ] Parallel processing patterns
- [ ] Error handling and recovery
- [ ] Performance monitoring
- [ ] Real-time alerting

### Week 7-8: Cloud Deployment
- [ ] Containerize with Docker
- [ ] Deploy to cloud platform
- [ ] Set up production monitoring
- [ ] Implement cost optimization

## 🛠 Key Commands

```bash
# List all DAGs
airflow dags list

# Test a task
airflow tasks test dag_id task_id 2025-01-01

# Trigger a DAG run
airflow dags trigger dag_id

# Check task logs
airflow tasks logs dag_id task_id 2025-01-01 1
```

## 📊 Project Metrics

Track your progress with these metrics:
- Daily logs processed
- Pipeline success rate
- Data quality scores
- Query performance
- Storage efficiency

## 🆘 Troubleshooting

### Common Issues
1. **Airflow won't start**: Check port 8080 availability
2. **DAG not appearing**: Verify syntax with `python dag_file.py`
3. **Task failures**: Check logs in Airflow UI
4. **Database locked**: Restart Airflow scheduler

### Learning Resources
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)
- [SQL Window Functions](https://mode.com/sql-tutorial/sql-window-functions/)