import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import uuid
import logging
from tokenprovider import TokenProvider
from google.cloud import bigtable
from google.cloud.bigtable import row
from apache_beam.utils.timestamp import MAX_TIMESTAMP, MIN_TIMESTAMP
import time, datetime, json

def run():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create a unique group ID
    group_id = "beam-test-group"
    logger.info(f"Using consumer group ID: {group_id}")
    
    # Get the required OAuth token
    # We're creating the token provider here but not using it directly in the pipeline
    # This avoids serialization issues
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
                bootstrap_servers='bootstrap.data-ingestion.us-central1.managedkafka.cool-continuity-457614-b2.cloud.goog:9092',
                topic='iot-data',
                group_id=group_id,
                token_provider_class=TokenProvider
            ))
            | 'LogMessages' >> beam.Map(
                lambda msg: (logger.info(f"Received message: {msg}") or msg)
            )
            | 'WriteToBigtable' >> beam.ParDo(WriteToBigtable(
                project_id='cool-continuity-457614-b2',
                instance_id='iot-data-store',
                table_id='weather-info'
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
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        self.logger.info(f"Reached end of partition: {msg.topic()}/{msg.partition()}")
                    else:
                        self.logger.error(f"Error: {msg.error()}")
                else:
                    # Process the message
                    key = msg.key().decode('utf-8') if msg.key() else None
                    value = msg.value().decode('utf-8')
                    self.consumer.commit(asynchronous=False)
                    yield value
        except Exception as e:
            self.logger.error(f"Error processing Kafka messages: {e}")
    
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
            event_dt = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        else:
            event_dt = timestamp.to_utc_datetime()          # already tz-aware

        # ----- write the row --------------
        row_key = uuid.uuid4().bytes
        bt_row  = self.table.direct_row(row_key)

        bt_row.set_cell(
            self.column_family,
            b"message",
            element.encode(),
            timestamp=event_dt          # <-- pass datetime, not int
        )
        bt_row.commit()


if __name__ == "__main__":
    run()