from confluent_kafka import Consumer, Producer
import json
from datetime import datetime

INPUT_TOPIC = 'test-topic'
OUTPUT_TOPIC = 'processed-topic'
BOOTSTRAP_SERVERS = 'localhost:9092'

consumer = Consumer({
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': 'stream-processor-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([INPUT_TOPIC])

producer = Producer({'bootstrap.servers': BOOTSTRAP_SERVERS})

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue

        value = json.loads(msg.value().decode('utf-8'))
        if 'text' in value:
            value['processed'] = value['text'].upper() + " (PROCESSED)"
            value['processed_at'] = datetime.now().isoformat()
            producer.produce(OUTPUT_TOPIC, value=json.dumps(value))
            producer.flush()
            print(f"Преобразовано и отправлено: {value['processed']}")
except KeyboardInterrupt:
    print("Stream processor остановлен")
finally:
    consumer.close()