import socket
import threading
import time
import pickle
from datetime import datetime

# Настройки
TCP_HOST = '0.0.0.0'
TCP_PORT = 1501
MULTICAST_GROUP = '233.0.0.1'
MULTICAST_PORT = 1502
BROADCAST_INTERVAL = 10

class ChatServer:
    def __init__(self):
        self.messages_buffer = []
        self.buffer_lock = threading.Lock()
        self.last_sent_time = time.time()

        # TCP-сокет для приёма сообщений
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind((TCP_HOST, TCP_PORT))
        self.tcp_socket.listen(10)
        print(f"[SERVER] Запущен на {TCP_HOST}:{TCP_PORT}")

        # UDP-мультикаст сокет
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

    def handle_client(self, conn, addr):
        try:
            data = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            if not data:
                return

            if "|" in data:
                username, message = data.split("|", 1)
                username = username.strip()[:20]
                message = message.strip()
            else:
                username = "Аноним"
                message = data.strip()

            if not message:
                return

            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_msg = f"[{timestamp}] {username}: {message}"
            print(f"[SERVER] → {formatted_msg}")

            with self.buffer_lock:
                self.messages_buffer.append(formatted_msg)

        except Exception as e:
            print(f"[SERVER] Ошибка от {addr}: {e}")
        finally:
            conn.close()

    def broadcast_loop(self):
        while True:
            time.sleep(0.1)
            now = time.time()
            if now - self.last_sent_time >= BROADCAST_INTERVAL:
                with self.buffer_lock:
                    if self.messages_buffer:
                        data = pickle.dumps(self.messages_buffer)
                        self.udp_socket.sendto(data, (MULTICAST_GROUP, MULTICAST_PORT))
                        print(f"[SERVER] Рассылка {len(self.messages_buffer)} сообщений → {MULTICAST_GROUP}:{MULTICAST_PORT}")
                        self.messages_buffer.clear()
                    self.last_sent_time = now

    def start(self):
        threading.Thread(target=self.broadcast_loop, daemon=True).start()
        print("[SERVER] Сервер готов. Ожидание сообщений...\n")

        while True:
            conn, addr = self.tcp_socket.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    ChatServer().start()