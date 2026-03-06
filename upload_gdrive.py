"""
Upload opcional para Google Drive via API.
Para usar: configure as credenciais OAuth (ver README) e defina GDRIVE_PASTA_ID no .env.
Alternativa mais simples: use GDRIVE_PASTA_LOCAL no .env para copiar para a pasta do Google Drive Desktop.
"""
import sys
from pathlib import Path

import config


def upload_para_drive_api(local_path: Path, nome_remoto: str | None = None) -> bool:
    """
    Faz upload do arquivo para o Google Drive via API.
    Requer: pip install google-api-python-client google-auth-oauthlib
    e arquivo credentials.json + token.json (fluxo OAuth uma vez).
    """
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        print("Para upload via API instale: google-api-python-client google-auth-oauthlib", file=sys.stderr)
        return False

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None
    token_path = Path(__file__).parent / "token.json"
    creds_path = Path(__file__).parent / "credentials.json"

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                print("Coloque credentials.json na pasta do projeto (Google Cloud Console).", file=sys.stderr)
                return False
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    drive_id = config.GDRIVE_PASTA_ID
    if not drive_id:
        print("Defina GDRIVE_PASTA_ID no .env com o ID da pasta do Drive.", file=sys.stderr)
        return False

    service = build("drive", "v3", credentials=creds)
    nome = nome_remoto or local_path.name
    mime = "video/mp4" if local_path.suffix.lower() == ".mp4" else "video/x-matroska"
    media = MediaFileUpload(str(local_path), mimetype=mime, resumable=True)
    body = {"name": nome, "parents": [drive_id]}
    service.files().create(body=body, media_body=media).execute()
    print(f"Upload concluído: {nome}")
    return True
