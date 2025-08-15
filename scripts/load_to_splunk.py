import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def load_to_splunk():
    """Sends alerts to Splunk HEC endpoint.

    This function reads JSON alerts from `data/alerts.json`, sets up the
    necessary headers and payload, and sends a POST request to the
    Splunk HEC endpoint configured in the `.env` file.

    The function prints a message for each alert indicating the
    event name and the HTTP status code of the request.
    """
    
    with open("data/alerts.json", "r") as f:
        alerts = json.load(f)

    url = os.getenv("SPLUNK_HEC_URL")
    token = os.getenv("SPLUNK_TOKEN")
    headers = {
        "Authorization": f"Splunk {token}",
        "Content-Type": "application/json"
    }

    for alert in alerts:
        payload = {"event": alert}
        response = requests.post(url, headers=headers, json=payload)
        print(f"Sent alert: {alert['event']} | Status: {response.status_code}")