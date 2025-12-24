from confluent_kafka import Producer
import json
import time

BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC = 'test-topic'
COUNT = 10000

producer = Producer({'bootstrap.servers': BOOTSTRAP_SERVERS})

start = time.time()
for i in range(COUNT):
    msg = {"text": f"Perf message {i}", "ts": time.time()}
    producer.produce(TOPIC, value=json.dumps(msg).encode('utf-8'))

producer.flush()
duration = time.time() - start

print(f"Отправлено {COUNT} сообщений за {duration:.2f} секунд")
print(f"Производительность: {COUNT / duration:.0f} сообщений/сек")