# Задача 1.2 — синхронизация через Lock
import threading
import sys
import time

counter = 0
lock = threading.Lock()

def incrementer():
    global counter
    for _ in range(100_000):
        with lock:
            temp = counter
            temp += 1
            counter = temp

def decrementer():
    global counter
    for _ in range(100_000):
        with lock:
            temp = counter
            temp -= 1
            counter = temp

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python rsp.3.2.py <n> <m>")
        sys.exit(1)

    n = int(sys.argv[1])
    m = int(sys.argv[2])

    threads = []
    for _ in range(n):
        threads.append(threading.Thread(target=incrementer))
    for _ in range(m):
        threads.append(threading.Thread(target=decrementer))

    start_time = time.time()

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Финальное значение счётчика (с Lock): {counter}")
    print(f"Ожидаемое значение: {(n - m) * 100_000}")
    print(f"Время выполнения: {execution_time:.4f} секунд")