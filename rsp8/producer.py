from flask import Flask, request, jsonify
from confluent_kafka import Producer
import json

app = Flask(__name__)
BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC = 'test-topic'

producer = Producer({'bootstrap.servers': BOOTSTRAP_SERVERS})

def delivery_report(err, msg):
    if err is not None:
        print(f'Ошибка доставки: {err}')
    else:
        print(f'Сообщение доставлено в {msg.topic()} [{msg.partition()}]')

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'message required'}), 400
    try:
        producer.produce(TOPIC, value=json.dumps(data['message']), callback=delivery_report)
        producer.poll(0)
        producer.flush()
        return jsonify({'status': 'sent'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-send/<int:count>')
def test_send(count):
    for i in range(count):
        msg = {"text": f"Test message {i}", "id": i}
        producer.produce(TOPIC, value=json.dumps(msg), callback=delivery_report)
    producer.flush()
    return jsonify({'status': f'Sent {count} messages'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)