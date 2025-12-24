from confluent_kafka import Consumer
import json
import sqlite3
from datetime import datetime

BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC = 'dlq-topic'

consumer = Consumer({
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': 'dlq-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([TOPIC])

conn = sqlite3.connect('messages.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS dlq (id INTEGER PRIMARY KEY, raw TEXT, received_at TEXT)')

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue

        raw = msg.value().decode('utf-8')
        print(f"DLQ сообщение получено: {raw}")
        cursor.execute('INSERT INTO dlq (raw, received_at) VALUES (?, ?)',
                       (raw, datetime.now().isoformat()))
        conn.commit()
except KeyboardInterrupt:
    print("DLQ consumer остановлен")
finally:
    consumer.close()
    conn.close()