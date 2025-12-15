import os
import tempfile
import threading

import whisperx_service as ws
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Transcribe Service")
templates = Jinja2Templates(directory="templates")

# --- Флаг готовности модели ---
model_ready = False


@app.on_event("startup")
def load_model_on_startup():
    """Загрузка модели при старте FastAPI."""

    def load():
        global model_ready
        print("[INIT] Loading WhisperX ASR model... (this may take a few minutes)")
        ws.load_whisperx_model()
        model_ready = True
        print("[INIT] WhisperX is ready ✅")

    threading.Thread(target=load, daemon=True).start()


@app.get("/test", response_class=HTMLResponse)
async def test():
    return HTMLResponse("<h1>WhisperX Server is running</h1>")


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Обрабатывает аудио и возвращает JSON с таймингами слов."""
    if not model_ready:
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

        result = ws.transcribe_audio(tmp.name)
        return JSONResponse(result)

    finally:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)
            print(f"[DEBUG] Removed temp file: {tmp.name}")
