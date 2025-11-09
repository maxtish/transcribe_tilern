# Transcribe Tilern

## Требования
- Python 3.11.x

## Настройка виртуального окружения

Если есть старое окружение, удаляем его:
```powershell
# Деактивировать окружение
deactivate

# Удалить папку venv
Remove-Item -Recurse -Force .\venv
```

Создать новое виртуальное окружение на Python 3.11 и активировать его:
```powershell
python -m venv venv
.\venv\Scripts\activate
```
Или если окружение уже создано:
```powershell
.\venv\Scripts\activate
```

Установить зависимости:
```powershell
pip install --upgrade -r requirements.txt
```

## Запуск сервера (без Docker)
```powershell
python -m uvicorn app.main:app --reload --port 8000
```
После запуска можно открыть страницу загрузки mp3 и тестировать тайминги слов:
```
http://localhost:8000/test
```

## Windows: настройка FFmpeg

Необходим BtbN FFmpeg:
[Ссылка на релизы](https://github.com/BtbN/FFmpeg-Builds/releases)

1. Выбрать `win64-gpl` → распаковать архив.
2. В распакованной папке есть `bin\ffmpeg.exe`.
3. Добавить путь до `bin` в системный PATH:
   1. Win + R → `sysdm.cpl`
   2. Вкладка `Erweitert` (Дополнительно)
   3. Кнопка `Umgebungsvariablen…` (Переменные среды)
   4. В разделе `Systemvariablen` найти переменную `Path` → выделить → `Bearbeiten…`
   5. Кнопка `Neu` → ввести путь к `bin`, например:
   ```text
   C:\ffmpeg\bin
   ```

Проверка установки:
```powershell
ffmpeg -version
```






## Запуск сервера (Docker)
```powershell
docker-compose build
docker-compose up -d
```
После запуска можно открыть страницу загрузки mp3 и тестировать тайминги слов:
```
http://localhost:8000/test
```







## requirements.txt
- **fastapi** — фреймворк для создания API.
- **uvicorn** — сервер ASGI для запуска FastAPI.
- **whisperx** — библиотека для транскрипции аудио с точным таймингом слов.
- **torch** и **torchaudio** — PyTorch и аудио-библиотека для работы с моделями.
- **numpy** — для работы с массивами данных.






docker-compose down -v  
docker-compose up -d
docker system prune -a --volumes
docker-compose up -d --build