"""
Upload opcional para Google Drive via API.
Para usar: configure as credenciais OAuth (ver README) e defina GDRIVE_PASTA_ID no .env.
Credential scrubbing: em caso de erro nunca imprimimos token/creds nos logs.
Integridade: após upload comparamos MD5 local com md5Checksum do Drive.
"""
import sys
from pathlib import Path

import config


def _safe_auth_message(e: Exception) -> str:
    """Mensagem genérica para erros de auth; nunca expõe token/creds (credential scrubbing)."""
    return "Erro de autenticação. Verifique credentials.json e token.json."


def upload_para_drive_api(local_path: Path, nome_remoto: str | None = None) -> bool:
    """
    Faz upload do arquivo para o Google Drive via API.
    Requer: pip install google-api-python-client google-auth-oauthlib
    e arquivo credentials.json + token.json (fluxo OAuth uma vez).
    Após upload, verifica integridade comparando MD5 local com md5Checksum do Drive.
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

    from file_manager import FileManager

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None
    token_path = Path(__file__).parent / "token.json"
    creds_path = Path(__file__).parent / "credentials.json"

    try:
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
    except Exception as e:
        print(_safe_auth_message(e), file=sys.stderr)
        return False

    drive_id = config.GDRIVE_PASTA_ID
    if not drive_id:
        print("Defina GDRIVE_PASTA_ID no .env com o ID da pasta do Drive.", file=sys.stderr)
        return False

    sha256_local = FileManager.hash_sha256(local_path)

    try:
        service = build("drive", "v3", credentials=creds)
        nome = nome_remoto or local_path.name
        mime = "video/mp4" if local_path.suffix.lower() == ".mp4" else "video/x-matroska"
        media = MediaFileUpload(str(local_path), mimetype=mime, resumable=True)
        body = {"name": nome, "parents": [drive_id]}
        created = service.files().create(body=body, media_body=media, fields="id").execute()
        file_id = created.get("id")
        # Verificação de integridade: comparar SHA-256 local com o do Drive (get após create)
        meta = service.files().get(fileId=file_id, fields="sha256Checksum,md5Checksum").execute()
        sha256_drive = meta.get("sha256Checksum")
        md5_drive = meta.get("md5Checksum")
    except Exception as e:
        print(f"Erro no upload: {e}", file=sys.stderr)
        return False

    if sha256_drive and sha256_local.lower() != sha256_drive.lower():
        print("Aviso: verificação de integridade falhou (SHA-256 local != Drive). Arquivo pode estar corrompido.", file=sys.stderr)
    elif sha256_drive:
        print("Integridade verificada (SHA-256 local = Drive).")
    elif md5_drive:
        md5_local = FileManager.hash_md5(local_path)
        if md5_local.lower() != md5_drive.lower():
            print("Aviso: verificação MD5 falhou (local != Drive).", file=sys.stderr)
        else:
            print("Integridade verificada (MD5 local = Drive).")

    print(f"Upload concluído: {nome}")
    return True
