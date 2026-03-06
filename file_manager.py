"""
FileManager: integridade (SHA-256), cópia e verificação pós-upload.
Uso em GRC: garantir que o arquivo não foi corrompido no disco ou no upload.
Audit trail: barra de progresso Rich no hash para arquivos grandes (ex.: 1h de aula).
"""
import hashlib
import shutil
import sys
from pathlib import Path

from loguru import logger
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

import config
from logger_config import get_console


def compute_sha256(path: Path) -> str:
    """Calcula o hash SHA-256 do arquivo para verificação de integridade."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_md5(path: Path) -> str:
    """Calcula MD5 (Drive API retorna md5Checksum para verificação pós-upload)."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sha256(path: Path, expected: str) -> bool:
    """Verifica se o hash SHA-256 do arquivo coincide com o esperado."""
    if not path.exists():
        return False
    return compute_sha256(path) == expected.lower()


class FileManager:
    """
    Cuida do hash (integridade), cópia para pasta local e integridade.
    Uso: hash antes de mover/upload; verificação após upload (Drive: md5).
    Audit trail: hash_sha256 exibe barra de progresso para arquivos grandes.
    """

    @staticmethod
    def hash_sha256(path: Path, show_progress: bool = True) -> str:
        """Calcula SHA-256; se show_progress e arquivo > 1MB, exibe barra de progresso Rich."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        size = path.stat().st_size
        if not show_progress or size < 1024 * 1024:
            digest = compute_sha256(path)
            logger.debug(f"Integridade SHA-256: {digest[:16]}...")
            return digest

        sha256_hash = hashlib.sha256()
        console = get_console()
        chunk_size = 65536
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                description="[cyan]Gerando hash de integridade (SHA-256)...",
                total=size,
            )
            with open(path, "rb") as f:
                for byte_block in iter(lambda: f.read(chunk_size), b""):
                    sha256_hash.update(byte_block)
                    progress.advance(task, len(byte_block))
        digest = sha256_hash.hexdigest()
        logger.debug(f"Integridade verificada: {digest[:16]}...")
        return digest

    @staticmethod
    def hash_md5(path: Path) -> str:
        """Calcula MD5 (Drive API retorna md5Checksum para verificação pós-upload)."""
        return compute_md5(path)

    @staticmethod
    def copy_to_gdrive_local(local_path: Path) -> bool:
        """Copia o arquivo para a pasta local do Google Drive, se configurada."""
        if not config.GDRIVE_PASTA_LOCAL or not local_path.exists():
            return False
        dest_dir = Path(config.GDRIVE_PASTA_LOCAL)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / local_path.name
        try:
            shutil.copy2(local_path, dest)
            logger.info(f"Cópia para Google Drive: {dest}")
            return True
        except Exception as e:
            logger.error(f"Erro ao copiar para GDrive: {e}")
            return False

    @staticmethod
    def verify_integrity_sha256(path: Path, expected_sha256: str) -> bool:
        """Verifica integridade local por SHA-256."""
        ok = verify_sha256(path, expected_sha256)
        if not ok and path.exists():
            logger.warning("Verificação SHA-256 falhou (arquivo pode estar corrompido).")
        return ok
