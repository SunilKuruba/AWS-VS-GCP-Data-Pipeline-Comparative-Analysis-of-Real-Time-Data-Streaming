"""
ThingSpeak to AWS Kinesis Stream Ingestion Script

This script continuously fetches sensor data from a ThingSpeak API endpoint
and streams the data into an AWS Kinesis Data Stream. It adds a timestamp
(`ec2_timestamp`) indicating when the data was fetched from the EC2 instance.

"""

import requests
import boto3
import json
import time
from datetime import datetime
from typing import List, Dict

# Configuration
THINGSPEAK_URL = "https://api.thingspeak.com/channels/12397/feeds.json?results=100"
STREAM_NAME = "data-ingestion-kinesis"
REGION_NAME = "us-east-1"
FETCH_INTERVAL_SECONDS = 60
kinesis_client = boto3.client("kinesis", region_name=REGION_NAME)


def fetch_thing_speak_feeds() -> List[Dict]:
    """
    Fetches the latest sensor feeds from ThingSpeak API.

    Returns:
        List of feed entries as dictionaries. Empty list if error.
    """
    try:
        response = requests.get(THINGSPEAK_URL, timeout=10)
        response.raise_for_status()
        feeds = response.json().get("feeds", [])
        return feeds
    except Exception as e:
        print(f"[{datetime.now()}] Error fetching ThingSpeak data: {e}")
        return []

def push_feeds_to_kinesis(feeds: List[Dict]) -> None:
    """
    Pushes each feed record to the AWS Kinesis Data Stream.

    Args:
        feeds: List of sensor data dictionaries.
    """
    for entry in feeds:
        try:
            partition_key = str(entry.get("entry_id", "default"))

            # Add EC2 processing timestamp
            entry["ec2_timestamp"] = datetime.utcnow().isoformat() + "Z"

            # Send the record to Kinesis
            kinesis_client.put_record(
                StreamName=STREAM_NAME,
                Data=json.dumps(entry),
                PartitionKey=partition_key
            )
            print(f"[{datetime.now()}] Successfully pushed to Kinesis: Entry ID {partition_key}")

        except Exception as e:
            print(f"[{datetime.now()}] Error sending entry to Kinesis: {e}")

def main():
    """
    Main loop to fetch and push data continuously.
    """
    print("Starting ThingSpeak to Kinesis ingestion service...")
    while True:
        feeds = fetch_thing_speak_feeds()
        if feeds:
            push_feeds_to_kinesis(feeds)
        else:
            print(f"[{datetime.now()}] No feeds to process.")
        time.sleep(FETCH_INTERVAL_SECONDS)

# Entry Point
if __name__ == "__main__":
    main()
