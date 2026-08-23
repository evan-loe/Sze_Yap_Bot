import os
from pathlib import Path

# Environment variable to override persistent storage location
# Set SZEYAP_DATA_DIR to change where runtime files are stored
DATA_DIR = Path(os.getenv('SZEYAP_DATA_DIR', '/mnt/data/szeyap-bot-files'))

# Create required directories inside the data dir
COGS_DIR = DATA_DIR / 'cogs'
SYNONYMS_DIR = DATA_DIR / 'synonyms'
ORIG_AUDIO_DIR = DATA_DIR / 'orig_audio'
TONES_AUDIO_DIR = DATA_DIR / 'tones_audio'
TEMP_DIR = DATA_DIR / 'temp'

for d in (DATA_DIR, COGS_DIR, SYNONYMS_DIR, ORIG_AUDIO_DIR, TONES_AUDIO_DIR, TEMP_DIR):
    d.mkdir(parents=True, exist_ok=True)


def cog_file(name: str) -> str:
    return str(COGS_DIR / name)


def synonyms_file(name: str) -> str:
    return str(SYNONYMS_DIR / name)


def orig_audio_path(*parts) -> str:
    return str(ORIG_AUDIO_DIR.joinpath(*parts))


def tones_audio_path(*parts) -> str:
    return str(TONES_AUDIO_DIR.joinpath(*parts))


def temp_path(*parts) -> str:
    return str(TEMP_DIR.joinpath(*parts))
