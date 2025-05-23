from io import BytesIO

import librosa
import noisereduce as nr
import numpy as np
import soundfile as sf

from service_logging import logger


def convert_audio(pcm_bytes: bytes) -> BytesIO:
    """Функция принимает байты PCM аудиофайла, имеющего
    заранее определенные характеристики, и конвертирует его
    в моно WAV файл с частотой дискретизации 16 кГц.

    Args:
        pcm_bytes (bytes): Байты аудиофайла.

    Returns:
        BytesIO: Байтстрим WAV файла.
    """
    logger.info("Audio file format conversion...")

    audio_data = np.frombuffer(pcm_bytes, dtype=np.int16)

    audio_data = audio_data.reshape((-1, 2))
    audio_data = audio_data.mean(axis=1).astype(np.int16)  # Среднее значение для моно

    audio_data = librosa.resample(
        audio_data.astype(np.float32) / 32768.0,  # Нормализация
        orig_sr=44100,
        target_sr=16000,
    )
    audio_data = (audio_data * 32768.0).astype(np.int16)  # Денормализация

    buffer = BytesIO()
    sf.write(buffer, audio_data, 16000, format="WAV", subtype="PCM_16")
    buffer.seek(0)
    return buffer


def denoise_audio(wav_bytestream: BytesIO) -> BytesIO:
    """Функция принимает байтстрим WAV файла и старается убрать
    лишние шумы из аудио для улучшения качества звучания речи.

    Args:
        pcm_bytes (bytes): Байты аудиофайла.

    Returns:
        BytesIO: Байтстрим WAV файла без шумов.
    """
    logger.info("Filtering out background noise...")

    y, sr = librosa.load(wav_bytestream, sr=16000, mono=True)

    reduced_noise = nr.reduce_noise(y=y, sr=sr)

    buffer = BytesIO()
    sf.write(buffer, reduced_noise, sr, format="WAV", subtype="PCM_16")
    buffer.seek(0)
    return buffer
