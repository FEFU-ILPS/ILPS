from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from service_logging import logger

from .utils.audio import convert_audio, denoise_audio

router = APIRouter()


@router.post("/", summary="Предобработка аудиофайла.")
async def process_audio(file: Annotated[UploadFile, File(...)]) -> StreamingResponse:
    """Принимает на вход аудиофайл, конвертирует его в моноканальный
    WAV формат с частотой дескритизации 16 кГц.
    """
    logger.info("Checking file properties...")
    if not file.filename.lower().endswith(".pcm"):
        logger.error("Invalid file extension.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only files with the extension '.pcm' are allowed.",
        )

    if file.content_type not in ["application/octet-stream", None]:
        logger.error("Invalid content type.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid content type. Only application/octet-stream is allowed for PCM files.",
        )

    file_bytes = await file.read()
    if len(file_bytes) % 4 != 0:  # 2 канала * 2 байта на выборку = 4 байта на фрейм
        logger.error("ncorrect size of the PCM file.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect size of the PCM file. 16-bit PCM with 2 channels was expected.",
        )

    try:
        logger.info("Preprocessing audio....")
        converted_audio = convert_audio(file_bytes)
        denoised_audio = denoise_audio(converted_audio)

        logger.success("Done. Sending preprocessed file.")
        return StreamingResponse(
            denoised_audio,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=preprocessed_audio.wav",
            },
        )

    except Exception as error:
        logger.error(f"File preprocessing error: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preprocessing error: {str(error)}",
        )
