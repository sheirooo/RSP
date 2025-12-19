# Лабораторная работа 3, задача 2.2 — Вечно голодные дикари
import threading
import time
import random

M = 5
servings = M                        
lock = threading.Lock()
pot_empty = threading.Condition(lock)      
pot_has_food = threading.Condition(lock)   

num_savages = 10

def savage(name):
    global servings         
    while True:
        time.sleep(random.uniform(2, 6))  

        with lock:
            while servings == 0:
                pot_has_food.wait()

            servings -= 1
            print(f"Дикарь {name} съел порцию. Осталось: {servings}")

            if servings == 0:
                print(f"  Дикарь {name} съел последнюю → БУДИТ ПОВАРА!")
                pot_empty.notify()          
            else:
                pot_has_food.notify()       

def cook():
    global servings
    while True:
        with lock:
            while servings != 0:        
                pot_empty.wait()

            print(f"\nПОВАР ПРОСНУЛСЯ! Варил еду...")
            time.sleep(random.uniform(2, 4))
            servings = M
            print(f"ПОВАР положил {M} порций! Кастрюля полная\n")
            pot_has_food.notify_all()   

print(f"Запуск: {num_savages} вечно голодных дикарей, кастрюля на {M} порций\n")

threading.Thread(target=cook, daemon=True).start()

for i in range(num_savages):
    threading.Thread(target=savage, args=(i,), daemon=True).start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nОстановлено пользователем")