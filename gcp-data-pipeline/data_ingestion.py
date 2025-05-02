import confluent_kafka
import argparse
import time 
import requests
from tokenprovider import TokenProvider
import requests, json, uuid

# Custom arguments to start producing events
parser = argparse.ArgumentParser()
bootstrap_default = 'bootstrap.data-ingestion.us-central1.managedkafka.cool-continuity-457614-b2.cloud.goog:9092'
parser.add_argument('-b', '--bootstrap-servers', dest='bootstrap', type=str,  default=bootstrap_default, required=False)
parser.add_argument('-t', '--topic-name', dest='topic_name', type=str, default='iot-data', required=False)
parser.add_argument('-n', '--num_messages', dest='num_messages', type=int, default=2, required=False)
parser.add_argument('--delay', dest='delay', type=float, default=5.0, required=False)
args = parser.parse_args()


# Pub/Sub Config
token_provider = TokenProvider()
config = {
    'bootstrap.servers': args.bootstrap,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'OAUTHBEARER',
    'oauth_cb': token_provider.get_token,
    'acks': 'all',
    'retries': 5,
    'linger.ms': 5,
}


URL = f'https://api.thingspeak.com/channels/12397/feeds.json?results={args.num_messages}'

print(URL)

producer = confluent_kafka.Producer(config)


def callBack(err, msg):
    if err is not None:
        print(f'Msg delivery to Kafka failed: {err}')
    else:
        print(f'Delivered message to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


while True:
    resp = requests.get(URL, timeout=10).json()
    feeds_data = resp['feeds']

    for feed in feeds_data:
        uid = uuid.uuid1()
        key = f"key-{uid}".encode('utf-8')
        
        current_time = time.gmtime()
        formatted_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", current_time)
        feed['vm_timestamp'] = formatted_time
        
        value = json.dumps(feed).encode('utf-8')
        producer.produce(args.topic_name, key=key, value=value, callback=callBack)
        # Internal queue handling
        producer.poll(0)
    
    producer.flush()
    print(f"Successfully produced {args.num_messages} messages to topic '{args.topic_name}' with {args.delay} sec delay between each.")
    
    # Pause between calls to thingspeak API
    if args.delay > 0:
        time.sleep(args.delay)
