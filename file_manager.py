"""
FileManager: integridade (SHA-256), cópia e verificação pós-upload.
Uso em GRC: garantir que o arquivo não foi corrompido no disco ou no upload.
"""
import hashlib
import shutil
import sys
from pathlib import Path

import config


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
    """

    @staticmethod
    def hash_sha256(path: Path) -> str:
        return compute_sha256(path)

    @staticmethod
    def hash_md5(path: Path) -> str:
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
            print(f"Cópia para Google Drive: {dest}")
            return True
        except Exception as e:
            print(f"Erro ao copiar para GDrive: {e}", file=sys.stderr)
            return False

    @staticmethod
    def verify_integrity_sha256(path: Path, expected_sha256: str) -> bool:
        """Verifica integridade local por SHA-256."""
        ok = verify_sha256(path, expected_sha256)
        if not ok and path.exists():
            print("Aviso: verificação SHA-256 falhou (arquivo pode estar corrompido).", file=sys.stderr)
        return ok
