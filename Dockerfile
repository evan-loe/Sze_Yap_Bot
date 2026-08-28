FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    SZEYAP_DATA_DIR=/mnt/data/szeyap-bot-files

WORKDIR /app

# System packages needed for audio handling and common Python wheels.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        build-essential \
        gcc \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first so code changes don't invalidate the layer.
COPY requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install -r requirements.txt

# Copy the application code and data files.
COPY src ./src
COPY Procfile ./Procfile

# Ensure the persistent data directory exists in the container image.
RUN mkdir -p "$SZEYAP_DATA_DIR"

# Run the bot from repo root so existing relative paths continue to work.
CMD ["python", "src/dictionary_bot.py"]
