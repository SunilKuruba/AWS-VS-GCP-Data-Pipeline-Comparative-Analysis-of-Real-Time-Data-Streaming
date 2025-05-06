import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import uuid
import logging
from tokenprovider import TokenProvider
from google.cloud import bigtable
from google.cloud.bigtable import row
from apache_beam.utils.timestamp import MAX_TIMESTAMP, MIN_TIMESTAMP
import time, json, argparse
from datetime import datetime, timezone

parser = argparse.ArgumentParser()
bootstrap_default = 'bootstrap.data-ingestion.us-central1.managedkafka.cool-continuity-457614-b2.cloud.goog:9092'
parser.add_argument('-b', '--bootstrap-servers', dest='bootstrap', type=str,  default=bootstrap_default, required=False)
parser.add_argument('-t', '--topic-name', dest='topic_name', type=str, default='iot-data', required=False)
parser.add_argument('-n', '--num_messages', dest='num_messages', type=int, default=2, required=False)
parser.add_argument('-project_id', '--project_id', dest='project_id', type=str, default='cool-continuity-457614-b2', required=False)
parser.add_argument('-instance_id','--instance_id',  dest='instance_id', type=str, default='iot-data-store', required=False)
parser.add_argument('-table_id', '--table_id',  dest='table_id', type=str, default='weather-info', required=False)
args = parser.parse_args()

# For processing the records
field_mapping =  {
    "field1": "wind_direction",
    "field2": "wind_speed",
    "field3": "humidity_percent",
    "field4": "temperature_fahrenheit",
    "field5": "rain_inches_per_minute",
    "field6": "pressure_inhg",
    "field7": "power_level_volts",
    "field8": "light_intensity"
}

def run():
    # Group ID for consuming from kafka
    group_id = "beam-test-group"
    print(f"Using consumer group ID: {group_id}")
    
    token_provider = TokenProvider()
    
    # Set up pipeline options
    options = PipelineOptions()
    std_options = options.view_as(StandardOptions)
    std_options.streaming = True
    
    # For Kafka IO, we need to define a function to extract the message value
    def extract_message(kafka_record):
        return kafka_record.value.decode('utf-8')
    
    # Create and run the pipeline
    with beam.Pipeline(options=options) as pipeline:
        messages = (
            pipeline
            | 'Create' >> beam.Create([1])
            | 'ReadFromKafka' >> beam.ParDo(ReadKafkaMessages(
                bootstrap_servers=args.bootstrap,
                topic=args.topic_name,
                group_id=group_id,
                token_provider_class=TokenProvider
            ))
            | 'LogMessages' >> beam.Map(
                lambda msg: (print(f"Received message: {msg}") or msg)
            )
            | 'WriteToBigtable' >> beam.ParDo(WriteToBigtable(
                project_id=args.project_id,
                instance_id=args.instance_id,
                table_id=args.table_id
            ))
        )

# Custom DoFn for Kafka reading
class ReadKafkaMessages(beam.DoFn):
    def __init__(self, bootstrap_servers, topic, group_id, token_provider_class):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.token_provider_class = token_provider_class
    
    def setup(self):
        # Import here to avoid serialization issues
        from confluent_kafka import Consumer, KafkaError
        
        # Create token provider inside setup
        self.token_provider = self.token_provider_class()
        
        # Configure Kafka consumer
        self.conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'OAUTHBEARER',
            'oauth_cb': self.token_provider.get_token,
        }
        
        # Create consumer
        self.consumer = Consumer(self.conf)
        self.consumer.subscribe([self.topic])
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Kafka consumer set up for topic: {self.topic}")
    
    def process(self, element):
        # Poll for messages
        try:
            while True:
                msg = self.consumer.poll(timeout=25.0)
                print(msg)

                if msg is None:
                    self.logger.info("No message received, continuing...")
                    break
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        self.logger.info(f"Reached end of partition: {msg.topic()}/{msg.partition()}")
                    else:
                        self.logger.error(f"Error: {msg.error()}")
                else:
                    # Process the message
                    key = msg.key().decode('utf-8') if msg.key() else None
                    value = msg.value().decode('utf-8')
                    formatted_data =  self.process_helper(json.loads(value), msg.timestamp()[1])
                    
                    self.consumer.commit(asynchronous=False)

                    yield formatted_data
        except Exception as e:
            self.logger.error(f"Error processing Kafka messages: {e}")

    def process_helper(self, records, kafka_timestamp_ms):
        formatted_data = {} 

        for (field, value) in records.items():
            key = field_mapping.get(field, field)
            formatted_data[key] = value
        
        # adding kafka and beam time stamps
        # dt = datetime.fromtimestamp(kafka_timestamp_ms / 1000, tz=timezone.utc)
        # formatted_data['kafka_timestamp'] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        # current_time = time.gmtime()
        # formatted_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", current_time)
        # formatted_data['beam_timestamp'] = formatted_time

        # a) from Kafka: msg.timestamp()[1] is **milliseconds since epoch**
        formatted_data['kafka_timestamp'] = kafka_timestamp_ms // 1000

        # b) “Beam produce time”: just take current clock in seconds
        formatted_data['beam_timestamp'] = int(time.time())

        return formatted_data
    
    def teardown(self):
        if hasattr(self, 'consumer'):
            self.consumer.close()
            self.logger.info("Kafka consumer closed")


class WriteToBigtable(beam.DoFn):
    def __init__(self, project_id, instance_id, table_id, column_family='cf1'):
        self.project_id = project_id
        self.instance_id = instance_id
        self.table_id = table_id
        self.column_family = column_family

    # ---------- Beam lifecycle ----------
    def setup(self):
        self.client   = bigtable.Client(project=self.project_id, admin=True)
        self.instance = self.client.instance(self.instance_id)
        self.table    = self.instance.table(self.table_id)

    def process(self, element, timestamp=beam.DoFn.TimestampParam):
        # ----- choose a safe datetime -----
        if timestamp in (MAX_TIMESTAMP, MIN_TIMESTAMP):
            event_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        else:
            event_dt = timestamp.to_utc_datetime()   

        # ----- write the row --------------
        row_key = uuid.uuid4().bytes
        bt_row  = self.table.direct_row(row_key)

        bt_row.set_cell(
            self.column_family,
            b"message",
            json.dumps(element).encode(),
            timestamp=event_dt # Datatime
        )
        bt_row.commit()


if __name__ == "__main__":
    run()