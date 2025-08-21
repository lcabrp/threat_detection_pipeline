#!/usr/bin/env python3
"""
Local Development Environment Setup Script
Creates the directory structure and initial configuration for learning Data Engineering
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

def create_directory_structure():
    """Create the organized directory structure for the DE learning project"""
    
    directories = [
        # Data lake structure (Bronze/Silver/Gold)
        "data/raw/logs",           # Bronze: Raw incoming data
        "data/processed/daily",    # Silver: Cleaned, structured data
        "data/analytics/alerts",   # Gold: Business insights
        "data/analytics/reports",
        
        # SQL queries and schemas
        "sql/ddl",                 # Data Definition Language
        "sql/dml",                 # Data Manipulation Language  
        "sql/queries",             # Analytical queries
        
        # Configuration and secrets
        "config/airflow",
        "config/database",
        
        # Docker and deployment
        "docker",
        
        # Documentation
        "docs/learning_notes",
        "docs/architecture",
        
        # Logs and monitoring
        "logs/airflow",
        "logs/pipeline",
        
        # Testing
        "tests/unit",
        "tests/integration",
    ]
    
    base_path = Path("/app")
    created_dirs = []
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(dir_path))
        print(f"✅ Created: {dir_path}")
    
    return created_dirs

def create_gitignore():
    """Create a comprehensive .gitignore for the project"""
    
    gitignore_content = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Airflow
airflow.cfg
airflow.db
airflow-webserver.pid
logs/
standalone_admin_password.txt

# Data files (too large for git)
data/raw/
data/processed/
*.parquet
*.csv
*.json
!data/sample/

# Database files  
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
.env.local
.env.production

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
docker-compose.override.yml

# Logs
*.log

# Backup files
*.bak
*.backup
"""
    
    with open("/app/.gitignore", "w") as f:
        f.write(gitignore_content.strip())
    
    print("✅ Created comprehensive .gitignore")

def create_sample_config():
    """Create sample configuration files"""
    
    # Database configuration
    db_config = {
        "development": {
            "type": "sqlite",
            "path": "data/cybersec_pipeline.db",
            "echo": False
        },
        "production": {
            "type": "postgresql", 
            "host": "localhost",
            "port": 5432,
            "database": "cybersec_pipeline",
            "echo": False
        }
    }
    
    with open("/app/config/database/config.json", "w") as f:
        json.dump(db_config, f, indent=2)
    
    # Airflow configuration
    airflow_config = {
        "core": {
            "dags_folder": "/app/dags",
            "base_log_folder": "/app/logs/airflow",
            "executor": "LocalExecutor",
            "sql_alchemy_conn": "sqlite:///data/airflow.db",
            "load_examples": False,
            "max_active_runs_per_dag": 1
        },
        "webserver": {
            "web_server_port": 8080,
            "base_url": "http://localhost:8080"
        },
        "scheduler": {
            "catchup_by_default": False,
            "max_threads": 2
        }
    }
    
    with open("/app/config/airflow/local_config.json", "w") as f:
        json.dump(airflow_config, f, indent=2)
    
    print("✅ Created sample configuration files")

def create_learning_readme():
    """Create a README specifically for the learning journey"""
    
    readme_content = """# 🎓 Cybersecurity Data Engineering Learning Project

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize Airflow database
airflow db init

# Create Airflow admin user
airflow users create \\
    --username admin \\
    --firstname Admin \\
    --lastname User \\
    --role Admin \\
    --email admin@example.com \\
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
"""
    
    with open("/app/README_LEARNING.md", "w") as f:
        f.write(readme_content.strip())
    
    print("✅ Created learning-focused README")

def create_requirements_file():
    """Create enhanced requirements.txt for the learning project"""
    
    requirements = """
# Core Data Engineering
apache-airflow==2.8.0
pandas>=2.1.0
polars>=0.20.0
duckdb>=0.9.0
SQLAlchemy>=2.0.0

# Database drivers
psycopg2-binary>=2.9.0

# Data validation and quality
great-expectations>=0.18.0
pydantic>=2.0.0

# Monitoring and logging
prometheus-client>=0.19.0

# Development and testing
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0

# Utilities
python-dotenv>=1.0.0
click>=8.0.0
rich>=13.0.0
tqdm>=4.66.0

# Existing dependencies
requests>=2.31.0
numpy>=1.24.0
modin[dask]>=0.25.0
"""
    
    with open("/app/requirements.txt", "w") as f:
        f.write(requirements.strip())
    
    print("✅ Created enhanced requirements.txt")

def main():
    """Main setup function"""
    print("🚀 Setting up Data Engineering Learning Environment...\n")
    
    try:
        # Create directory structure
        created_dirs = create_directory_structure()
        print(f"\n📁 Created {len(created_dirs)} directories")
        
        # Create configuration files
        create_gitignore()
        create_sample_config()
        create_learning_readme()
        create_requirements_file()
        
        print("\n✅ Setup completed successfully!")
        print("\n🎯 Next Steps:")
        print("1. Install requirements: pip install -r requirements.txt")
        print("2. Read README_LEARNING.md for detailed instructions")
        print("3. Initialize Airflow: airflow db init")
        print("4. Start your learning journey!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()