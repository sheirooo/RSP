from confluent_kafka import Consumer, KafkaException
from confluent_kafka import Producer
import json
import sqlite3
from datetime import datetime

BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC = 'test-topic'
GROUP_ID = 'main-consumer-group'

# Создаём консьюмер
consumer = Consumer({
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([TOPIC])

# Подключение к SQLite
conn = sqlite3.connect('messages.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        received_at TEXT
    )
''')

# Счётчик обработанных сообщений (список, чтобы можно было изменять внутри цикла)
processed_count = [0]

# Продюсер для отправки в DLQ (создаём один раз, чтобы не создавать в цикле)
dlq_producer = Producer({'bootstrap.servers': BOOTSTRAP_SERVERS})

try:
    print("Консьюмер запущен. Ожидание сообщений...")
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        value = msg.value().decode('utf-8')

        try:
            data = json.loads(value)

            if 'text' in data:
                # Успешная обработка
                processed_count[0] += 1
                text = data['text']
                print(f"[{processed_count[0]}] Обработано: {text} (длина: {len(text)} символов)")

                cursor.execute(
                    'INSERT INTO messages (content, received_at) VALUES (?, ?)',
                    (text, datetime.now().isoformat())
                )
                conn.commit()

            else:
                raise ValueError("Отсутствует обязательное поле 'text'")

        except Exception as e:
            # Любая ошибка — отправляем оригинальное сообщение в DLQ
            print(f"Ошибка обработки сообщения: {e}")
            print(f"Отправка в DLQ: {value}")

            dlq_producer.produce('dlq-topic', value=value.encode('utf-8'))
            dlq_producer.poll(0)  # Обработка callback'ов
            # Можно добавить dlq_producer.flush() периодически, но poll достаточно

except KeyboardInterrupt:
    print("\nОстановлено пользователем")
finally:
    # Корректное закрытие ресурсов
    dlq_producer.flush()  # Гарантируем отправку всех сообщений в DLQ
    consumer.close()
    conn.close()
    print(f"Консьюмер завершил работу. Всего обработано сообщений: {processed_count[0]}")