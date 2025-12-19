# Базовый образ с Python (лёгкий и актуальный)
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала копируем только requirements.txt (это ускорит пересборку при изменениях кода)
COPY requirements.txt .

# Устанавливаем все зависимости из твоего requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта
COPY . .

# Создаём папки, которые нужны приложению (БД и скачанные файлы)
RUN mkdir -p instance static/downloads

# Открываем порт 5000 (тот, на котором работает твоё приложение)
EXPOSE 5000

# Команда запуска — точно как у тебя локально: python app.py
# (SocketIO запустится автоматически)
CMD ["python", "app.py"]