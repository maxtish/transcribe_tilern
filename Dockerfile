# базовый образ с CUDA (если GPU есть)
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# системные зависимости
RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg git

# копируем и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# копируем исходники
COPY app/ /app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
