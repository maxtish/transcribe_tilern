import os
import tempfile
import threading

# Импортируем нашу оптимизированную логику
import whisperx_service as ws
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Transcribe Service")
templates = Jinja2Templates(directory="templates")

# Глобальная ссылка на сервис (ленивая инициализация)
whisperx_service = None


@app.on_event("startup")
def load_model_background():
    """Фоновая загрузка WhisperX при запуске FastAPI"""

    def load():
        global whisperx_service
        print("[INIT] Loading WhisperX ASR model... (this may take a few minutes)")

        # ⚠️ Вызываем функцию загрузки ASR-модели из сервиса
        ws.load_whisperx_models()

        whisperx_service = ws
        print("[INIT] WhisperX is ready ✅")

    # запускаем загрузку в отдельном потоке
    threading.Thread(target=load, daemon=True).start()


@app.get("/test", response_class=HTMLResponse)
# ... (остается без изменений)


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Обрабатывает файл и возвращает JSON с таймингами слов."""
    global whisperx_service

    if whisperx_service is None:
        return JSONResponse(
            {
                "status": "loading",
                "message": "Model is still initializing, please retry in a minute.",
            },
            status_code=503,
        )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

    try:
        tmp.write(await file.read())
        tmp.close()
        print(f"[DEBUG] Saved temp file: {tmp.name}")

        # Вызываем функцию транскрипции
        result = whisperx_service.transcribe_audio(tmp.name)
        return JSONResponse(result)

    finally:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)
            print(f"[DEBUG] Removed temp file: {tmp.name}")
