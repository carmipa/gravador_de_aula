"""
Upload opcional para Google Drive via API.
Para usar: configure as credenciais OAuth (ver README) e defina GDRIVE_PASTA_ID no .env.
Credential scrubbing: em caso de erro nunca imprimimos token/creds nos logs.
Integridade: após upload comparamos SHA-256/MD5 local com o do Drive.
"""
from __future__ import annotations

from pathlib import Path

from loguru import logger

import config
from file_manager import FileManager


def _safe_auth_message(_: Exception) -> str:
    """Mensagem genérica para erros de auth; nunca expõe token/creds."""
    return "Erro de autenticação. Verifique credentials.json, token.json e permissões da API."


def upload_para_drive_api(local_path: str | Path, nome_remoto: str | None = None) -> bool:
    """
    Faz upload do arquivo para o Google Drive via API.
    Após upload, verifica integridade via SHA-256/MD5 quando disponível.
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        logger.error(
            "Dependências do Google Drive ausentes. Instale: pip install -r requirements-gdrive.txt"
        )
        return False

    local_file = Path(local_path)

    if not local_file.exists():
        logger.error("Arquivo não encontrado para upload: {}", local_file)
        return False

    if not config.GDRIVE_PASTA_ID:
        logger.error("GDRIVE_PASTA_ID não definido no .env.")
        return False

    scopes = ["https://www.googleapis.com/auth/drive.file"]
    base_dir = Path(__file__).resolve().parent
    token_path = base_dir / "token.json"
    creds_path = base_dir / "credentials.json"
    creds = None

    try:
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not creds_path.exists():
                    logger.error("credentials.json não encontrado na pasta do projeto.")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), scopes)
                creds = flow.run_local_server(port=0)
                token_path.write_text(creds.to_json(), encoding="utf-8")
    except Exception as exc:
        logger.error(_safe_auth_message(exc))
        return False

    sha256_local = FileManager.hash_sha256(local_file)
    md5_local = FileManager.hash_md5(local_file)

    try:
        service = build("drive", "v3", credentials=creds)
        remote_name = nome_remoto or local_file.name
        mime_type = "video/mp4" if local_file.suffix.lower() == ".mp4" else "video/x-matroska"

        media = MediaFileUpload(str(local_file), mimetype=mime_type, resumable=True)
        body = {
            "name": remote_name,
            "parents": [config.GDRIVE_PASTA_ID],
        }

        created = (
            service.files()
            .create(body=body, media_body=media, fields="id,name")
            .execute()
        )

        file_id = created.get("id")
        metadata = (
            service.files()
            .get(fileId=file_id, fields="id,name,sha256Checksum,md5Checksum")
            .execute()
        )

        sha256_drive = metadata.get("sha256Checksum")
        md5_drive = metadata.get("md5Checksum")

    except Exception as exc:
        msg = str(exc).lower()
        if any(word in msg for word in ("token", "credential", "access_token", "unauthorized")):
            logger.error("Erro de autenticação/permissão no Google Drive.")
        else:
            logger.error("Erro no upload para o Google Drive: {}", exc)
        return False

    if sha256_drive and sha256_drive.lower() != sha256_local.lower():
        logger.warning("SHA-256 divergente entre arquivo local e Google Drive.")
        return False

    if md5_drive and md5_drive.lower() != md5_local.lower():
        logger.warning("MD5 divergente entre arquivo local e Google Drive.")
        return False

    logger.success("Upload concluído com integridade validada: {}", local_file.name)
    return True
