from enum import Enum
from typing import Annotated

import soundfile as sf
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from models import model_manager
from schemas import TranscribingResponse
from service_logging import logger

from .utils.transcribing import transcribe_audio

router = APIRouter()


class ModelLang(Enum):
    ENGLISH = "english"


@router.post("/", summary="Транскрипция речи")
async def transcribe(
    lang: Annotated[ModelLang, Form(...)],
    file: Annotated[UploadFile, File(...)],
) -> TranscribingResponse:
    """Получает транскрипцию речи из аудиофайла и возвращает ее в виде текста."""
    logger.info("Checking Necessary model...")
    if not model_manager.is_model_loaded(lang.value):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"The model for the language '{lang.value}' is not uploaded in the service.",
        )

    logger.info("Checking file properties...")
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only files with the extension '.wav' are allowed.",
        )

    if file.content_type not in ["audio/wav", None]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid content type. Only audio/wav is allowed for WAV files.",
        )

    audio_input, sample_rate = sf.read(file.file)

    logger.info("Transcribing audio....")
    transcription = transcribe_audio(audio_input, sample_rate, lang.value)

    logger.success("Done. Transcription extracted.")
    return TranscribingResponse(transcription=transcription)
