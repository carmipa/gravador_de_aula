"""
Testes do upload_gdrive.
Cobre: _safe_auth_message (credential scrubbing), upload_para_drive_api com mocks.
Fluxos de erro de rede (HttpError 403/500) e mock de googleapiclient.discovery.build.
"""
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


# --- Testes com mock da API Google (sem credenciais reais) ---


def _make_creds_and_path_mocks():
    """Fixtures de creds e Path para simular token.json existente (Path usado em upload_gdrive)."""
    token_mock = MagicMock()
    token_mock.exists.return_value = True
    creds_mock = MagicMock()
    creds_mock.valid = True
    parent = MagicMock()
    parent.__truediv__ = lambda self, name: token_mock if name == "token.json" else MagicMock(exists=lambda: False)
    path_mock = MagicMock()
    path_mock.parent = parent
    return creds_mock, path_mock


def test_upload_mock_build_retorna_true(sample_video_file):
    """Com build() mockado e service retornando create/get, upload retorna True."""
    import upload_gdrive as ud
    from pathlib import Path as RealPath

    creds_mock, path_mock = _make_creds_and_path_mocks()
    path_mock.resolve.return_value = path_mock
    path_mock.parent = path_mock
    path_mock.__truediv__ = lambda self, name: (
        path_mock._token if name == "token.json" else path_mock._creds
    )
    token_mock = MagicMock()
    token_mock.exists.return_value = True
    creds_path_mock = MagicMock()
    creds_path_mock.exists.return_value = True
    path_mock._token = token_mock
    path_mock._creds = creds_path_mock

    def path_side_effect(*args):
        if args and args[0] == ud.__file__:
            return path_mock
        return RealPath(*args)

    service = MagicMock()
    service.files.return_value.create.return_value.execute.return_value = {"id": "file_xyz"}
    service.files.return_value.get.return_value.execute.return_value = {
        "sha256Checksum": "a" * 64,
        "md5Checksum": "b" * 32,
    }

    import google.oauth2.credentials as creds_mod
    with patch("upload_gdrive.config") as cfg:
        cfg.GDRIVE_PASTA_ID = "folder_id"
        with patch("upload_gdrive.Path", side_effect=path_side_effect):
            with patch.object(creds_mod, "Credentials", MagicMock()) as Creds:
                Creds.from_authorized_user_file.return_value = creds_mock
                with patch("googleapiclient.discovery.build", return_value=service):
                    with patch("upload_gdrive.FileManager") as fm:
                        fm.hash_sha256.return_value = "a" * 64
                        fm.hash_md5.return_value = "b" * 32
                        result = upload_para_drive_api(sample_video_file)
    assert result is True


def test_upload_httperror_403_retorna_false_sem_expor_token(sample_video_file, capsys):
    """HttpError 403 (ex.: token expirado) retorna False e não imprime corpo da resposta (pode conter token)."""
    try:
        from googleapiclient.errors import HttpError
    except ImportError:
        pytest.skip("googleapiclient não instalado")

    creds_mock, path_mock = _make_creds_and_path_mocks()
    path_mock.parent.__truediv__ = lambda self, name: MagicMock(exists=lambda: True) if name == "token.json" else MagicMock(exists=lambda: False)

    service = MagicMock()
    # Simula resposta 403 com corpo que poderia vazar token
    service.files.return_value.create.return_value.execute.side_effect = HttpError(
        MagicMock(status=403),
        b'{"error": "invalid_grant", "access_token": "secret_leak"}',
    )

    import google.oauth2.credentials as creds_mod
    with patch("upload_gdrive.config") as cfg:
        cfg.GDRIVE_PASTA_ID = "folder_id"
    with patch("upload_gdrive.Path", return_value=path_mock):
        with patch.object(creds_mod, "Credentials", MagicMock()) as Creds:
            Creds.from_authorized_user_file.return_value = creds_mock
        with patch("googleapiclient.discovery.build", return_value=service):
            with patch("upload_gdrive.FileManager") as fm:
                fm.hash_sha256.return_value = "a" * 64
                result = upload_para_drive_api(sample_video_file)

    assert result is False
    out = capsys.readouterr()
    err = out.err
    assert "secret_leak" not in err
    assert "access_token" not in err


def test_upload_httperror_500_retorna_false(sample_video_file):
    """HttpError 500 (erro de rede/servidor) retorna False."""
    try:
        from googleapiclient.errors import HttpError
    except ImportError:
        pytest.skip("googleapiclient não instalado")

    creds_mock, path_mock = _make_creds_and_path_mocks()
    path_mock.parent.__truediv__ = lambda self, name: MagicMock(exists=lambda: True) if name == "token.json" else MagicMock(exists=lambda: False)

    service = MagicMock()
    service.files.return_value.create.return_value.execute.side_effect = HttpError(
        MagicMock(status=500),
        b"Internal Server Error",
    )

    import google.oauth2.credentials as creds_mod
    with patch("upload_gdrive.config") as cfg:
        cfg.GDRIVE_PASTA_ID = "folder_id"
    with patch.object(creds_mod, "Credentials", MagicMock()) as Creds:
        Creds.from_authorized_user_file.return_value = creds_mock
    with patch("googleapiclient.discovery.build", return_value=service):
        with patch("upload_gdrive.FileManager") as fm:
            fm.hash_sha256.return_value = "a" * 64
            fm.hash_md5.return_value = "b" * 32
            result = upload_para_drive_api(sample_video_file)

    assert result is False


def test_upload_integridade_sha256_falha_avisa(sample_video_file):
    """Quando SHA-256 do Drive difere do local, retorna False (integridade violada)."""
    creds_mock, path_mock = _make_creds_and_path_mocks()
    path_mock.parent.__truediv__ = lambda self, name: MagicMock(exists=lambda: True) if name == "token.json" else MagicMock(exists=lambda: False)

    service = MagicMock()
    service.files.return_value.create.return_value.execute.return_value = {"id": "f1"}
    service.files.return_value.get.return_value.execute.return_value = {
        "sha256Checksum": "diferente_" + "0" * 55,
        "md5Checksum": None,
    }

    import google.oauth2.credentials as creds_mod
    with patch("upload_gdrive.config") as cfg:
        cfg.GDRIVE_PASTA_ID = "folder_id"
        with patch.object(creds_mod, "Credentials", MagicMock()) as Creds:
            Creds.from_authorized_user_file.return_value = creds_mock
            with patch("googleapiclient.discovery.build", return_value=service):
                with patch("upload_gdrive.FileManager") as fm:
                    fm.hash_sha256.return_value = "a" * 64
                    fm.hash_md5.return_value = "b" * 32
                    result = upload_para_drive_api(sample_video_file)

    assert result is False
