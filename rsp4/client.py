import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import pickle
import struct

# Настройки
SERVER_TCP_HOST = '127.0.0.1'
SERVER_TCP_PORT = 1501
MULTICAST_GROUP = '233.0.0.1'
MULTICAST_PORT = 1502

class ChatClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        # Запрос логина
        username = simpledialog.askstring("Вход", "Введите ваш логин:", parent=self.root)
        if not username or not username.strip():
            messagebox.showinfo("Выход", "Логин не введён. Программа закрывается.")
            self.root.destroy()
            return

        self.username = username.strip()[:20]
        if not self.username:
            self.username = "Аноним"

        # Настройка окна
        self.root.deiconify()
        self.root.title(f"Чат • {self.username}")
        self.root.geometry("700x600")
        self.root.configure(bg="#1a1a1a")

        # Заголовок
        tk.Label(self.root, text="Широковещательный мультикаст-чат", font=("Arial", 14, "bold"),
                 bg="#1a1a1a", fg="#00ff99").pack(pady=10)

        # Область сообщений
        self.chat_area = scrolledtext.ScrolledText(
            self.root, state='disabled', wrap=tk.WORD,
            bg="#0f0f0f", fg="#00ff99", font=("Consolas", 11)
        )
        self.chat_area.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

        # Теги для своих сообщений
        self.chat_area.tag_config("my", foreground="#88ff88", font=("Consolas", 11, "bold"))
        self.chat_area.tag_config("other", foreground="#00ff99")

        # Поле ввода
        frame = tk.Frame(self.root, bg="#1a1a1a")
        frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.entry = tk.Entry(frame, font=("Arial", 12), bg="#333333", fg="white", insertbackground="white")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.send_message)
        self.entry.focus()

        tk.Button(frame, text="Отправить", command=self.send_message,
                  bg="#00aa00", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)

        # Мультикаст-приёмник
        self.setup_multicast()
        threading.Thread(target=self.receive_loop, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_multicast(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', MULTICAST_PORT))
        mreq = struct.pack("4s4s", socket.inet_aton(MULTICAST_GROUP), socket.inet_aton("0.0.0.0"))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def send_message(self, event=None):
        message = self.entry.get().strip()
        if not message:
            return

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_TCP_HOST, SERVER_TCP_PORT))
            payload = f"{self.username}|{message}"
            s.sendall(payload.encode('utf-8'))
            s.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отправить:\n{e}")

        self.entry.delete(0, tk.END)

    def receive_loop(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(8192)
                messages = pickle.loads(data)
                self.root.after(0, self.display_messages, messages)
            except:
                continue

    def display_messages(self, messages):
        self.chat_area.config(state='normal')
        for msg in messages:
            if f"{self.username}:" in msg:
                self.chat_area.insert(tk.END, msg + "\n", "my")
            else:
                self.chat_area.insert(tk.END, msg + "\n", "other")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def on_closing(self):
        try:
            self.sock.close()
        except:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ChatClient()
    if hasattr(app, 'username'):
        app.run()