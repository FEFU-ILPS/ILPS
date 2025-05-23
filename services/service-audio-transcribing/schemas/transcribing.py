from pydantic import BaseModel, Field

from .examples import TRANSCRIPTIONS_EXAMPLE


class TranscribingResponse(BaseModel):
    """Данные, отправляемые после транскрибирования речи из файла."""

    transcription: str = Field(description="Транскрипция речи", examples=TRANSCRIPTIONS_EXAMPLE)
