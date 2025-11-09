import logging

import torch
import whisperx

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # можно DEBUG для более подробного вывода
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# Выбираем устройство: GPU если доступен, иначе CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(f"Using device: {device}")


# Загружаем модель WhisperX один раз при старте сервиса
model = whisperx.load_model("large-v2", device=device, compute_type="float32")


def transcribe_audio(filepath: str):
    """
    Функция транскрибирует аудио-файл и возвращает
    словарь с языком, длительностью и списком слов с таймингами.
    """

    logging.info(f"Processing file: {filepath}")

    # 1️⃣ базовая транскрипция
    result = model.transcribe(filepath)
    logging.info(f"Detected language: {result.get('language', 'unknown')}")

    # 2️⃣ получаем сегменты и текст
    segments = result["segments"]
    logging.info(f"Number of segments: {len(segments)}")

    # 3️⃣ align (точные тайминги слов)
    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"], device=device
    )
    aligned = whisperx.align(segments, model_a, metadata, filepath, device)

    # 4️⃣ собираем список слов с таймингами
    words = []
    for segment in aligned["segments"]:
        for w in segment["words"]:
            words.append(
                {
                    "word": w["word"],
                    "start": round(w["start"], 3),
                    "end": round(w["end"], 3),
                }
            )

            logging.debug(f"Word: {w['word']}, start: {w['start']}, end: {w['end']}")

    duration = result.get("duration", sum([s["end"] for s in segments]))
    logging.info(f"Audio duration: {duration}s, total words: {len(words)}")

    return {
        "language": result.get("language", "unknown"),
        "duration": duration,
        "words": words,
    }
