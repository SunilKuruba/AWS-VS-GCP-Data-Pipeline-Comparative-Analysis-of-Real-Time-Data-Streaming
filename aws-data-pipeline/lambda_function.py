"""
AWS Lambda Function: Kinesis to DynamoDB Mapper

This Lambda function processes records from an AWS Kinesis Data Stream,
remaps ThingSpeak-style fields to human-readable field names,
adds timestamps, and inserts the cleaned data into a DynamoDB table.

"""

import json
import base64
import boto3
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict

# AWS DynamoDB Client Initialization
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('data-storage-dynamodb')

field_mapping: Dict[str, str] = {
    "field1": "wind_direction",
    "field2": "wind_speed",
    "field3": "humidity_percent",
    "field4": "temperature_fahrenheit",
    "field5": "rain_inches_per_minute",
    "field6": "pressure_inhg",
    "field7": "power_level_volts",
    "field8": "light_intensity"
}

def lambda_handler(event, context):
    """
    AWS Lambda handler function triggered by Kinesis events.

    Args:
        event: The event data from Kinesis.
        context: Runtime information.

    Returns:
        dict: API Gateway compatible response indicating success.
    """
    for record in event['Records']:
        try:
            # Decode and parse the Kinesis record payload
            payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
            payload_dict = json.loads(payload, parse_float=Decimal)

            # Remap fields to user-friendly names
            mapped_payload = {}
            for original_field, mapped_field in field_mapping.items():
                if original_field in payload_dict:
                    mapped_payload[mapped_field] = payload_dict[original_field]

            # Copy non-sensor metadata if available
            for key in ['entry_id', 'created_at']:
                if key in payload_dict:
                    mapped_payload[key] = payload_dict[key]

            # Add timestamps
            mapped_payload['lambda_timestamp'] = datetime.utcnow().isoformat() + "Z"
            mapped_payload['kinesis_timestamp'] = datetime.fromtimestamp(
                record['kinesis']['approximateArrivalTimestamp'], timezone.utc
            ).isoformat()

            # Write the record to DynamoDB
            table.put_item(Item=mapped_payload)

            print(f"Successfully inserted: {mapped_payload}")

        except Exception as e:
            print(f"Error processing record: {e}")
            raise

    return {
        'statusCode': 200,
        'body': 'Processed all records successfully.'
    }
