"""
Testes do FileManager e funções de hash/verificação.
Cobre: compute_sha256, compute_md5, verify_sha256, hash_sha256 (com e sem progresso),
copy_to_gdrive_local, verify_integrity_sha256.
"""
import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest

from file_manager import (
    FileManager,
    compute_md5,
    compute_sha256,
    verify_sha256,
)


def test_compute_sha256_arquivo_pequeno(sample_video_file):
    """SHA-256 de conteúdo fixo deve ser determinístico."""
    digest = compute_sha256(sample_video_file)
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)
    # Verifica com hashlib direto
    expected = hashlib.sha256(sample_video_file.read_bytes()).hexdigest()
    assert digest == expected


def test_compute_md5_arquivo_pequeno(sample_video_file):
    """MD5 de conteúdo fixo deve ser determinístico."""
    digest = compute_md5(sample_video_file)
    assert len(digest) == 32
    assert all(c in "0123456789abcdef" for c in digest)
    expected = hashlib.md5(sample_video_file.read_bytes()).hexdigest()
    assert digest == expected


def test_verify_sha256_ok(sample_video_file):
    """verify_sha256 retorna True quando hash confere."""
    h = compute_sha256(sample_video_file)
    assert verify_sha256(sample_video_file, h) is True
    assert verify_sha256(sample_video_file, h.upper()) is True


def test_verify_sha256_falha(sample_video_file):
    """verify_sha256 retorna False quando hash não confere."""
    assert verify_sha256(sample_video_file, "0" * 64) is False


def test_verify_sha256_arquivo_inexistente(tmp_path):
    """verify_sha256 retorna False para arquivo que não existe."""
    assert verify_sha256(tmp_path / "naoexiste", "ab" * 32) is False


def test_file_manager_hash_sha256_sem_progresso(sample_video_file):
    """FileManager.hash_sha256 com show_progress=False igual a compute_sha256."""
    a = FileManager.hash_sha256(sample_video_file, show_progress=False)
    b = compute_sha256(sample_video_file)
    assert a == b


def test_file_manager_hash_sha256_arquivo_pequeno_sem_barra(sample_video_file):
    """Arquivo < 1MB não deve usar barra de progresso (resultado igual)."""
    a = FileManager.hash_sha256(sample_video_file, show_progress=True)
    b = compute_sha256(sample_video_file)
    assert a == b


def test_file_manager_hash_sha256_arquivo_grande(sample_large_file):
    """Arquivo >= 1MB: hash_sha256 retorna mesmo digest que compute_sha256."""
    expected = compute_sha256(sample_large_file)
    got = FileManager.hash_sha256(sample_large_file, show_progress=True)
    assert got == expected


def test_file_manager_hash_sha256_arquivo_inexistente_levanta(tmp_path):
    """hash_sha256 em arquivo inexistente deve levantar FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        FileManager.hash_sha256(tmp_path / "naoexiste")


def test_file_manager_hash_md5(sample_video_file):
    """FileManager.hash_md5 igual a compute_md5."""
    assert FileManager.hash_md5(sample_video_file) == compute_md5(sample_video_file)


def test_file_manager_copy_to_gdrive_local_sem_config(sample_video_file):
    """Sem GDRIVE_PASTA_LOCAL configurado, copy retorna False."""
    with patch("file_manager.config") as m:
        m.GDRIVE_PASTA_LOCAL = None
        m.GDRIVE_PASTA_ID = None
        assert FileManager.copy_to_gdrive_local(sample_video_file) is False


def test_file_manager_copy_to_gdrive_local_arquivo_inexistente(tmp_path):
    """Arquivo inexistente: copy retorna False."""
    with patch("file_manager.config") as m:
        m.GDRIVE_PASTA_LOCAL = str(tmp_path / "drive")
        assert FileManager.copy_to_gdrive_local(tmp_path / "naoexiste.mkv") is False


def test_file_manager_copy_to_gdrive_local_ok(sample_video_file, tmp_path):
    """Com pasta configurada, copia e retorna True."""
    dest_dir = tmp_path / "gdrive_local"
    with patch("file_manager.config") as m:
        m.GDRIVE_PASTA_LOCAL = str(dest_dir)
        result = FileManager.copy_to_gdrive_local(sample_video_file)
    assert result is True
    assert (dest_dir / sample_video_file.name).exists()
    assert (dest_dir / sample_video_file.name).read_bytes() == sample_video_file.read_bytes()


def test_file_manager_verify_integrity_sha256_ok(sample_video_file):
    """verify_integrity_sha256 retorna True quando hash confere."""
    h = FileManager.hash_sha256(sample_video_file, show_progress=False)
    assert FileManager.verify_integrity_sha256(sample_video_file, h) is True


def test_file_manager_verify_integrity_sha256_falha(sample_video_file):
    """verify_integrity_sha256 retorna False quando hash não confere."""
    assert FileManager.verify_integrity_sha256(sample_video_file, "0" * 64) is False
