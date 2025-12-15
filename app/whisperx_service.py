import logging

import torch
import whisperx

# =======================
# 🔧 PATCH for PyTorch 2.6 + pyannote
# =======================
_original_torch_load = torch.load


def _patched_torch_load(*args, **kwargs):
    # Принудительно отключаем weights_only
    kwargs["weights_only"] = False
    return _original_torch_load(*args, **kwargs)


# =======================
# Конфигурация
# =======================
DEVICE = "cpu"
COMPUTE_TYPE = "float32"
BATCH_SIZE = 16

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

model = None
align_model = None
align_metadata = None


def load_whisperx_model():
    """
    Загружает WhisperX + pyannote VAD
    Патч применяется ТОЛЬКО на время загрузки
    """
    global model, align_model, align_metadata

    logging.info("[PATCH] Applying torch.load(weights_only=False)")
    torch.load = _patched_torch_load

    try:
        logging.info("[INIT] Loading WhisperX SMALL model (DE, CPU)")
        model = whisperx.load_model(
            "small",
            device=DEVICE,
            compute_type=COMPUTE_TYPE,
        )
        logging.info("[INIT] WhisperX ASR model ready ✅")

        logging.info("[INIT] Loading alignment model (DE)")
        align_model, align_metadata = whisperx.load_align_model(
            language_code="de",
            device=DEVICE,
        )
        logging.info("[INIT] Alignment model ready ✅")

    finally:
        # 🔥 ОБЯЗАТЕЛЬНО вернуть torch.load обратно
        torch.load = _original_torch_load
        logging.info("[PATCH] Restored original torch.load")


def transcribe_audio(filepath: str):
    if model is None:
        raise RuntimeError("Model not loaded")

    audio = whisperx.load_audio(filepath)
    result = model.transcribe(audio, batch_size=BATCH_SIZE)
    segments = result["segments"]

    aligned = whisperx.align(
        segments,
        align_model,
        align_metadata,
        audio,
        DEVICE,
    )

    words = []
    duration = 0.0
    for seg in aligned["segments"]:
        duration = max(duration, seg.get("end", 0.0))
        for w in seg.get("words", []):
            words.append(
                {
                    "word": w["word"],
                    "start": round(w.get("start", 0.0), 3),
                    "end": round(w.get("end", 0.0), 3),
                }
            )

    return {
        "language": "de",
        "duration": duration,
        "words": words,
    }
