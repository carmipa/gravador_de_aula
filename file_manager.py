"""
FileManager: integridade (SHA-256/MD5), cópia e verificação pós-upload.
Uso em GRC: garantir que o arquivo não foi corrompido no disco ou no upload.
"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from loguru import logger

import config


def compute_sha256(path: Path) -> str:
    """Calcula o hash SHA-256 do arquivo para verificação de integridade."""
    return FileManager.hash_sha256(path, show_progress=False)


def compute_md5(path: Path) -> str:
    """Calcula MD5 (Drive API retorna md5Checksum para verificação pós-upload)."""
    return FileManager.hash_md5(path)


def verify_sha256(path: Path, expected: str) -> bool:
    """Verifica se o hash SHA-256 do arquivo coincide com o esperado."""
    if not path.exists():
        return False
    return FileManager.hash_sha256(path, show_progress=False) == expected.lower()


class FileManager:
    """
    Cuida do hash (integridade), cópia para pasta local e integridade.
    Uso: hash antes de mover/upload; verificação após upload (Drive: md5).
    """

    @staticmethod
    def hash_sha256(path: str | Path, chunk_size: int = 1024 * 1024, show_progress: bool = True) -> str:
        """Calcula SHA-256 do arquivo. show_progress é ignorado (compatibilidade com testes)."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        digest = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def hash_md5(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
        """Calcula MD5 (Drive API retorna md5Checksum para verificação pós-upload)."""
        file_path = Path(path)
        digest = hashlib.md5()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def copiar_arquivo(origem: str | Path, destino_dir: str | Path) -> Path:
        """Copia o arquivo para o diretório de destino. Cria o diretório se necessário."""
        origem_path = Path(origem)
        destino_dir_path = Path(destino_dir)
        destino_dir_path.mkdir(parents=True, exist_ok=True)
        destino = destino_dir_path / origem_path.name
        shutil.copy2(origem_path, destino)
        logger.info("Arquivo copiado para {}", destino)
        return destino

    @staticmethod
    def copy_to_gdrive_local(local_path: Path) -> bool:
        """Copia o arquivo para a pasta local do Google Drive, se configurada."""
        if not config.GDRIVE_PASTA_LOCAL or not local_path.exists():
            return False
        try:
            FileManager.copiar_arquivo(local_path, config.GDRIVE_PASTA_LOCAL)
            return True
        except Exception as e:
            logger.error("Erro ao copiar para GDrive: {}", e)
            return False

    @staticmethod
    def verify_integrity_sha256(path: Path, expected_sha256: str) -> bool:
        """Verifica integridade local por SHA-256."""
        ok = verify_sha256(path, expected_sha256)
        if not ok and path.exists():
            logger.warning("Verificação SHA-256 falhou (arquivo pode estar corrompido).")
        return ok
