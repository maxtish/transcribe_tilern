# Базовый образ Python
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Не буферизовать вывод (удобнее для логов)
ENV PYTHONUNBUFFERED=1

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y ffmpeg git && apt-get clean

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости проекта
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY app/ ./

# Открываем порт
EXPOSE 8000

# Запуск FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
