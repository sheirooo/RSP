# Лабораторная работа 3, задача 2.1 — Дикари и повар (одноразовое питание)
import threading
import time
import random

M = 5                       # размер кастрюли
servings = 0                # текущее количество порций
lock = threading.Lock()
not_empty = threading.Condition(lock)    # есть еда
not_full = threading.Condition(lock)     # кастрюла не полная (можно варить)

total_savages = 20          # дикарей больше, чем порций

def savage(name):
    global servings         
    print(f"Дикарь {name} пришёл к кастрюле")

    with lock:
        while servings == 0:
            print(f"  Дикарь {name} ждёт еды...")
            not_empty.wait()

        servings -= 1
        print(f"Дикарь {name} взял порцию! Осталось: {servings}")

        if servings == 0:
            print("  Кастрюля пуста → будим повара")
            not_full.notify()

    print(f"Дикарь {name} наелся и ушёл\n")
    time.sleep(0.1)

def cook():
    global servings
    while True:
        with lock:
            while servings > 0:
                not_full.wait()

            print(f"\nПОВАР НАПОЛНИЛ КАСТРЮЛЮ! Положил {M} порций")
            servings = M
            not_empty.notify_all()

        time.sleep(random.uniform(2, 4))


threading.Thread(target=cook, daemon=True).start()
time.sleep(1)

for i in range(total_savages):
    time.sleep(random.uniform(0.1, 0.5))
    threading.Thread(target=savage, args=(i,)).start()

time.sleep(5)
print("Симуляция завершена.")