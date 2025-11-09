import os
import tempfile

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from whisperx_service import transcribe_audio

app = FastAPI(title="Transcribe Tilern")
templates = Jinja2Templates(directory="app/templates")


@app.get("/test", response_class=HTMLResponse)
async def get_test_page(request: Request):
    """Отдаёт простую HTML страницу для загрузки файла"""
    return templates.TemplateResponse("test.html", {"request": request})


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Обрабатывает mp3 и возвращает JSON"""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

    try:
        # записываем содержимое файла
        tmp.write(await file.read())
        tmp.close()

        # лог для наглядности
        print(f"[DEBUG] Saved temp file: {tmp.name}")

        # передаём путь в WhisperX
        result = transcribe_audio(tmp.name)

        return JSONResponse(result)

    finally:
        # удаляем временный файл после обработки
        if os.path.exists(tmp.name):
            os.remove(tmp.name)
            print(f"[DEBUG] Removed temp file: {tmp.name}")
