from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .whisperx_service import transcribe_audio
import tempfile
import json

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
    tmp.write(await file.read())
    tmp.close()

    result = transcribe_audio(tmp.name)
    return JSONResponse(result)
