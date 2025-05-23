FROM python:3.13-slim

# Установка утилиты lsb-release для определения кодового имени релиза
RUN apt-get update && \
    apt-get install -y --no-install-recommends lsb-release && \
    rm -rf /var/lib/apt/lists/*

# Добавление репозиториев Debian с компонентами main, contrib и non-free
RUN echo "deb http://deb.debian.org/debian $(lsb_release -cs) main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian $(lsb_release -cs)-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security $(lsb_release -cs)-security main contrib non-free" >> /etc/apt/sources.list

# Установка аудиозависимостей 
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg

# Установка curl для heath-check
RUN apt-get install -y curl && rm -rf /var/lib/apt/lists/*


RUN pip install poetry && poetry config virtualenvs.create false

WORKDIR /service

COPY ./pyproject.toml .

RUN poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8064

CMD ["python", "start.py"]