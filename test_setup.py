#!/usr/bin/env python3
"""
Test script to validate your Data Engineering learning environment setup
Run this to ensure everything is working before starting your learning journey
"""

import sys
import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime

def test_python_dependencies():
    """Test if all required Python packages are available"""
    print("🐍 Testing Python Dependencies...")
    
    required_packages = [
        'pandas', 'sqlite3', 'json', 'pathlib', 'datetime'
    ]
    
    optional_packages = [
        ('polars', 'pip install polars'),
        ('duckdb', 'pip install duckdb'),
        ('airflow', 'pip install apache-airflow==2.8.0')
    ]
    
    # Test required packages
    missing_required = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - REQUIRED")
            missing_required.append(package)
    
    # Test optional packages
    for package, install_cmd in optional_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ⚠️  {package} - Install with: {install_cmd}")
    
    return len(missing_required) == 0

def test_directory_structure():
    """Test if the directory structure is properly created"""
    print("\n📁 Testing Directory Structure...")
    
    required_dirs = [
        "data/bronze/logs",
        "data/silver/validated_logs", 
        "data/gold/daily_summaries",
        "sql/ddl",
        "sql/queries",
        "dags",
        "docs/learning_notes"
    ]
    
    base_path = Path("/app")
    missing_dirs = []
    
    for directory in required_dirs:
        dir_path = base_path / directory
        if dir_path.exists():
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory} - Missing")
            missing_dirs.append(directory)
    
    return len(missing_dirs) == 0

def test_file_creation():
    """Test if we can create and read files in the data directories"""
    print("\n📝 Testing File Operations...")
    
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "test_event",
        "message": "Setup validation test"
    }
    
    # Test Bronze layer
    try:
        bronze_path = Path("/app/data/bronze/logs/test_file.json")
        bronze_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(bronze_path, 'w') as f:
            json.dump(test_data, f)
        
        # Verify we can read it back
        with open(bronze_path, 'r') as f:
            read_data = json.load(f)
        
        assert read_data == test_data
        print("  ✅ Bronze layer file operations")
        
        # Clean up
        bronze_path.unlink()
        
    except Exception as e:
        print(f"  ❌ Bronze layer file operations - {e}")
        return False
    
    # Test SQLite database operations
    try:
        db_path = "/app/data/test_database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                data TEXT
            )
        """)
        
        # Insert test data
        cursor.execute("""
            INSERT INTO test_table (timestamp, data)
            VALUES (?, ?)
        """, (datetime.now().isoformat(), "test data"))
        
        # Query test data
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        
        assert count == 1
        print("  ✅ SQLite database operations")
        
        conn.close()
        
        # Clean up
        os.unlink(db_path)
        
    except Exception as e:
        print(f"  ❌ SQLite database operations - {e}")
        return False
    
    return True

def test_dag_syntax():
    """Test if the learning DAG has valid syntax"""
    print("\n🔄 Testing DAG Syntax...")
    
    dag_path = Path("/app/dags/cybersec_learning_dag.py")
    
    if not dag_path.exists():
        print("  ❌ Learning DAG file not found")
        return False
    
    try:
        # Try to compile the DAG file
        with open(dag_path, 'r') as f:
            dag_code = f.read()
        
        compile(dag_code, str(dag_path), 'exec')
        print("  ✅ DAG syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"  ❌ DAG syntax error: {e}")
        return False
    except Exception as e:
        print(f"  ⚠️  DAG validation warning: {e}")
        return True  # May have import issues but syntax is OK

def test_sql_files():
    """Test if SQL files exist and have basic syntax"""
    print("\n🗄️  Testing SQL Resources...")
    
    sql_files = [
        "sql/ddl/create_tables.sql",
        "sql/queries/learning_queries.sql"
    ]
    
    base_path = Path("/app")
    all_good = True
    
    for sql_file in sql_files:
        file_path = base_path / sql_file
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                if len(content) > 100:  # Basic check for non-empty content
                    print(f"  ✅ {sql_file}")
                else:
                    print(f"  ⚠️  {sql_file} - Seems empty")
            except Exception as e:
                print(f"  ❌ {sql_file} - Error reading: {e}")
                all_good = False
        else:
            print(f"  ❌ {sql_file} - Not found")
            all_good = False
    
    return all_good

def run_sample_data_generation():
    """Run a sample of the data generation logic"""
    print("\n🎲 Testing Data Generation Logic...")
    
    try:
        import random
        import json
        from datetime import datetime, timedelta
        
        # Simple data generation test
        execution_date = "2025-01-15"
        random.seed(42)  # For reproducible results
        
        logs = []
        for i in range(10):  # Small sample
            log_entry = {
                "timestamp": f"{execution_date}T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}Z",
                "event_id": f"test_evt_{i:06d}",
                "event_type": random.choice(["login_success", "login_failed", "file_access"]),
                "source_ip": f"192.168.1.{random.randint(1, 100)}",
                "user": f"test_user{random.randint(1, 10)}",
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "risk_score": round(random.uniform(0, 100), 2)
            }
            logs.append(log_entry)
        
        # Test saving to file
        output_path = Path("/app/data/bronze/logs/test_generation.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            for log in logs:
                f.write(json.dumps(log) + '\n')
        
        # Test reading back
        read_logs = []
        with open(output_path, 'r') as f:
            for line in f:
                read_logs.append(json.loads(line.strip()))
        
        assert len(read_logs) == 10
        print(f"  ✅ Generated and validated {len(logs)} sample log entries")
        
        # Clean up
        output_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data generation test failed: {e}")
        return False

def main():
    """Run all setup validation tests"""
    print("=" * 60)
    print("🧪 DATA ENGINEERING SETUP VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("Directory Structure", test_directory_structure),  
        ("File Operations", test_file_creation),
        ("DAG Syntax", test_dag_syntax),
        ("SQL Resources", test_sql_files),
        ("Data Generation", run_sample_data_generation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  💥 {test_name} - Unexpected error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Congratulations! Your setup is ready for learning.")
        print("Next steps:")
        print("1. Read /app/docs/learning_notes/week1_getting_started.md")
        print("2. Install Airflow: pip install apache-airflow")
        print("3. Initialize Airflow: airflow db init")
        print("4. Start your Data Engineering journey!")
    else:
        print(f"\n⚠️  Setup issues found. Please fix the failed tests before proceeding.")
        print("Refer to the setup guide in /app/docs/learning_notes/")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)