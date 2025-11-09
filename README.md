python --version
Python 3.11.x


Удаляем старый venv: если есть
deactivate
Remove-Item -Recurse -Force .\venv


Создать новое виртуальное окружение на Python 3.11:
python -m venv venv
.\venv\Scripts\activate


или если создано 
.\venv\Scripts\activate


pip install --upgrade -r requirements.txt


БЕЗ ДОКЕРА 
Запуск сервера: 

python -m uvicorn app.main:app --reload --port 8000


страницу загрузки mp3 и  тестировать тайминги слов.

http://localhost:8000/test




WINDOWS 

необходим BtbN

Ссылка: https://github.com/BtbN/FFmpeg-Builds/releases
Выбираешь win64-gpl → распаковываешь.
В распакованной папке есть bin\ffmpeg.exe.
Добавь путь до bin в системный PATH: 



Нажми Win + R, введи:
sysdm.cpl
Перейди на вкладку Erweitert (Дополнительно).
Нажми кнопку Umgebungsvariablen… (Переменные среды).
Внизу в разделе Systemvariablen (Системные переменные) найди переменную Path → выдели → Bearbeiten… (Редактировать).
Нажми Neu (Создать)
Введи путь к bin внутри твоей папки ffmpeg, например:
C:\ffmpeg\bin


Проверка
ffmpeg -version




requirements.txt

fastapi — фреймворк для создания API.

uvicorn — сервер ASGI, на котором запускается FastAPI.

whisperx — библиотека для транскрипции аудио и точного тайминга слов.

torch и torchaudio — PyTorch и аудио-библиотека для работы с моделями.

numpy — для работы с массивами данных.

