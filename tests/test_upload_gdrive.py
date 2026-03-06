"""
Testes do upload_gdrive.
Cobre: _safe_auth_message (credential scrubbing), upload_para_drive_api com mocks.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from upload_gdrive import _safe_auth_message, upload_para_drive_api


def test_safe_auth_message_nao_expoe_excecao():
    """Mensagem de auth nunca inclui o texto da exceção (pode conter token)."""
    e = Exception("access_token_secret_xyz")
    msg = _safe_auth_message(e)
    assert "access_token_secret" not in msg
    assert "Erro de autenticação" in msg


def test_upload_sem_gdrive_pasta_id_retorna_false(sample_video_file):
    """Sem GDRIVE_PASTA_ID, retorna False."""
    with patch("upload_gdrive.config") as cfg:
        cfg.GDRIVE_PASTA_ID = None
        result = upload_para_drive_api(sample_video_file)
    assert result is False


def test_upload_com_pasta_id_vazio_retorna_false(sample_video_file):
    """Com GDRIVE_PASTA_ID vazio, retorna False."""
    with patch("upload_gdrive.config") as cfg:
        cfg.GDRIVE_PASTA_ID = ""
    result = upload_para_drive_api(sample_video_file)
    assert result is False
