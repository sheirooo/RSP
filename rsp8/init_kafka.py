from confluent_kafka.admin import AdminClient, NewTopic

BOOTSTRAP = 'localhost:9092'
TOPICS = [
    ('test-topic', 1),
    ('processed-topic', 1),
    ('dlq-topic', 1),
    ('multi-topic', 3)  # для демонстрации масштабирования
]

admin = AdminClient({'bootstrap.servers': BOOTSTRAP})

new_topics = [NewTopic(topic, num_partitions=partitions, replication_factor=1)
              for topic, partitions in TOPICS]

fs = admin.create_topics(new_topics)

for topic, f in fs.items():
    try:
        f.result()
        print(f"Тема {topic} успешно создана")
    except Exception as e:
        print(f"Тема {topic}: {e}")

print("Все темы готовы")