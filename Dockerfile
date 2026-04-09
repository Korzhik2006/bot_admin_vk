# 1. Берем официальный легкий образ Python
FROM python:3.12-slim

# 2. Устанавливаем рабочую папку внутри контейнера
WORKDIR /app

# 3. Копируем файл со списком библиотек
COPY requirements.txt .

# 4. Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем все остальные файлы бота (твои .py файлы)
COPY . .

# 6. Команда для запуска бота при старте контейнера
CMD ["python", "main.py"]
