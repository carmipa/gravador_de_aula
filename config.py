"""
Configurações do gravador (variáveis de ambiente + defaults).
Use .env para sobrescrever; nunca commite .env.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Pasta de gravações (default: pasta do projeto / gravacoes)
GRAVACOES_DIR = os.getenv("GRAVACOES_DIR") or str(Path(__file__).resolve().parent / "gravacoes")
Path(GRAVACOES_DIR).mkdir(parents=True, exist_ok=True)

# Pasta local do Google Drive (opcional) para copiar após gravar
GDRIVE_PASTA_LOCAL = os.getenv("GDRIVE_PASTA_LOCAL", "").strip() or None
# ID da pasta no Drive para upload via API (opcional)
GDRIVE_PASTA_ID = os.getenv("GDRIVE_PASTA_ID", "").strip() or None

# Codec: av1 | hevc_nvenc | hevc | h264
CODEC = os.getenv("CODEC", "av1").strip().lower()
if CODEC not in ("av1", "hevc_nvenc", "hevc", "h264"):
    CODEC = "h264"

# Qualidade (CRF/CQ): 18 = máxima, 32 = menor arquivo
CRF = int(os.getenv("CRF", "30"))
CRF = max(18, min(32, CRF))

# FPS
FPS = int(os.getenv("FPS", "30"))
FPS = max(15, min(60, FPS))

# Título (parcial) da janela do Teams
TEAMS_WINDOW_TITLE = os.getenv("TEAMS_WINDOW_TITLE", "Teams").strip()

# Áudio: dispositivo DShow (Windows). Listar com: ffmpeg -list_devices true -f dshow -i dummy
# Ex.: "audio=Linha 1 (Virtual Audio Cable)" ou "audio=Microfone (Realtek)"
# Deixe vazio para gravar só vídeo (gdigrab não captura áudio do sistema).
AUDIO_DEVICE_DSHOW = os.getenv("AUDIO_DEVICE_DSHOW", "").strip() or None

# Preset AV1 (0–13): maior = mais lento e menor arquivo. 10 = bom para aulas (pouco movimento).
AV1_PRESET = int(os.getenv("AV1_PRESET", "10"))
AV1_PRESET = max(0, min(13, AV1_PRESET))
