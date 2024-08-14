# backend/data_ingestion/tasks.py
from celery import Celery
import requests
import json
import boto3
from datetime import datetime
import os

# Configure AWS credentials and S3 bucket name
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

# Celery configuration
app = Celery('tasks', broker='redis://redis:6379/0')

@app.task
def fetch_and_store_data(provider: dict):
    """
    Fetches data from a provider and stores it in S3.
    
    Parameters:
        provider (dict): A dictionary containing the provider's name and URL.
        
    Returns:
        None
    """
    response = requests.request(
            method="GET", 
            url=provider.get('url'), 
            timeout=3
        )
    if response.status_code == 200:
        data = response.json()
        timestamp = datetime.now().isoformat()
        filename = f"{provider['name']}_{timestamp}.json"
        # Store raw data in S3
        s3.put_object(
            Bucket=AWS_S3_BUCKET,
            Key=filename,
            Body=json.dumps(data)
        )
        print(f"Stored data for {provider['name']} at {timestamp}")
    else:
        print(f"Failed to fetch data for {provider['name']}")

PROVIDERS = [
    {
        'name': 'check_almere',
        'url': 'https://api.ridecheck.app/gbfs/v3/almere/vehicle_status.json'
    },
    {
        'name': 'check_delft',
        'url': 'https://api.ridecheck.app/gbfs/v3/delft/vehicle_status.json'
    },
    {
        'name': 'check_breda',
        'url': 'https://api.ridecheck.app/gbfs/v3/breda/vehicle_status.json'
    }
]

# Dynamic task scheduling
@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    """
    Sets up period tasks for fetching and storing GBFS data.
    
    This function is called after the Celery app is configured. It adds a
    periodic task for each GBFS provider in the PROVIDERS list. The task
    is executed every T seconds and fetches and stores the data for the
    provider.
    """
    T = 5 * 60.0  # 5 minutes
    for provider in PROVIDERS:
        # Add a periodic task for the provider
        sender.add_periodic_task(
            T,
            fetch_and_store_data.s(provider),
            name=f'Fetch {provider["url"]} every {T} seconds'
        )
