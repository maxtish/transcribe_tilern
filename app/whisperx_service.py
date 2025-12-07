import logging

import torch
import whisperx

# --- ПАТЧ ДЛЯ РЕШЕНИЯ ПРОБЛЕМЫ UnpicklingError ---
# Это решение является универсальным, так как принудительно устанавливает
# weights_only=False при загрузке модели PyTorch, обходя проблемы совместимости
# с метаданными Pyannote VAD.

original_torch_load = torch.load


def custom_torch_load(*args, **kwargs):
    """Принудительно устанавливает weights_only=False при загрузке."""
    kwargs["weights_only"] = False
    return original_torch_load(*args, **kwargs)


# Временно заменяем torch.load на нашу пропатченную версию
torch.load = custom_torch_load
logging.info("[PATCH] Applied forceful PyTorch load patch (weights_only=False).")
# ----------------------------------------------------


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# --- Настройки ---
# Выбираем устройство: GPU если доступен, иначе CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
# Используем float16 для GPU (меньше VRAM, быстрее), float32 для CPU
compute_type = "float16" if device == "cuda" else "float32"
batch_size = 16

logging.info(
    f"Using device: {device}, compute_type: {compute_type}, batch_size: {batch_size}"
)


# Глобальные переменные для моделей, загруженных при старте
model = None
# Кэш для моделей выравнивания (Alignment)
ALIGN_MODELS_CACHE = {}


def load_whisperx_models():
    """Отдельная функция для загрузки ASR модели при старте"""
    global model
    logging.info("[INIT] Starting WhisperX ASR model loading...")

    # 1. Модель транскрипции (ASR)
    model = whisperx.load_model("large-v2", device=device, compute_type=compute_type)
    logging.info("[INIT] WhisperX ASR model ready ✅")

    # ⚠️ Восстанавливаем оригинальный torch.load после загрузки всех моделей
    global original_torch_load
    torch.load = original_torch_load
    logging.info("[PATCH] Restored original torch.load function.")


def transcribe_audio(filepath: str):
    """
    Транскрибирует аудио-файл и возвращает словарь с таймингами слов.
    """
    global model, ALIGN_MODELS_CACHE

    if model is None:
        raise RuntimeError("WhisperX model is not initialized.")

    logging.info(f"Processing file: {filepath}")

    # Загружаем аудио один раз
    audio = whisperx.load_audio(filepath)

    # 1️⃣ базовая транскрипция
    result = model.transcribe(audio, batch_size=batch_size)
    detected_language = result.get("language", "unknown")
    logging.info(f"Detected language: {detected_language}")

    # 2️⃣ получаем сегменты
    segments = result["segments"]
    logging.info(f"Number of segments: {len(segments)}")

    # 3️⃣ align (точные тайминги слов)

    # 3a. Проверяем кэш для модели выравнивания
    if detected_language not in ALIGN_MODELS_CACHE:
        logging.info(f"Loading new alignment model for language: {detected_language}")
        model_a, metadata = whisperx.load_align_model(
            language_code=detected_language, device=device
        )
        ALIGN_MODELS_CACHE[detected_language] = (model_a, metadata)
    else:
        logging.info(f"Using cached alignment model for language: {detected_language}")
        model_a, metadata = ALIGN_MODELS_CACHE[detected_language]

    # 3b. Выполняем выравнивание
    aligned = whisperx.align(segments, model_a, metadata, audio, device)

    # Очистка памяти (важно при использовании GPU)
    if device == "cuda":
        pass

    # 4️⃣ собираем список слов с таймингами
    words = []
    duration = 0.0
    for segment in aligned["segments"]:
        duration = max(duration, segment.get("end", 0.0))
        for w in segment.get("words", []):
            words.append(
                {
                    "word": w["word"],
                    "start": round(w.get("start", 0.0), 3),
                    "end": round(w.get("end", 0.0), 3),
                }
            )

            logging.debug(f"Word: {w['word']}, start: {w['start']}, end: {w['end']}")

    # Пересчитываем длительность, если она не была найдена в результате (редко)
    if duration == 0.0 and segments:
        duration = segments[-1].get("end", 0.0)

    logging.info(f"Audio duration: {duration}s, total words: {len(words)}")

    return {
        "language": detected_language,
        "duration": duration,
        "words": words,
    }
