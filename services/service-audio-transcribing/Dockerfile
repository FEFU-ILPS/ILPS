FROM python:3.13-slim

# Установка espeak-ng и очиска кешей
RUN apt-get update && apt-get install -y espeak-ng curl \
    && rm -rf /var/lib/apt/lists/*

# Поиск установочного пути espeak-ng и создание переменных среды
RUN LIB_PATH=$(find / -name "libespeak-ng.so.1" 2>/dev/null | head -n 1) \
    && if [ -z "$LIB_PATH" ]; then \
           echo "Error: unable to locate 'libespeak-ng.so.1'"; \
           exit 1; \
       fi \
    && DIR_PATH=$(dirname "$LIB_PATH") \
    && echo "export PHONEMIZER_ESPEAK_LIBRARY=$LIB_PATH" >> /etc/environment \
    && echo "export PHONEMIZER_ESPEAK_PATH=$DIR_PATH" >> /etc/environment 

RUN pip install poetry && poetry config virtualenvs.create false

WORKDIR /service

COPY ./pyproject.toml .

RUN poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8066

CMD ["python", "start.py"]