# 🛡️ Threat Detection ETL Pipeline

This project simulates a cybersecurity ETL pipeline using Python, Apache Airflow, and Splunk. It extracts logs, detects suspicious activity, and sends alerts to Splunk for visualization.

## 🔧 Features

- Extracts sample logs from JSON
- Flags suspicious events using regex
- Pushes alerts to Splunk via HTTP Event Collector (HEC)
- Scheduled daily via Airflow DAG

## 🧰 Tech Stack

- Python
- Apache Airflow
- Pandas & Regex
- Splunk HEC
- dotenv

## 🚀 Setup

1. Clone the repo  
2. Create `.env` with your Splunk HEC credentials  
3. Install dependencies:  
   ```bash
   pip install -r requirements.txt