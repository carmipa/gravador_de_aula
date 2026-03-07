"""
Testes do logger_config.
Verifica: setup_logging não quebra, get_console retorna Console, diretório logs criado.
"""
from pathlib import Path


def test_setup_logging_nao_levanta():
    """setup_logging deve executar sem exceção."""
    from logger_config import setup_logging
    setup_logging()


def test_get_console_retorna_console():
    """get_console retorna instância de Console do Rich."""
    from rich.console import Console

    from logger_config import get_console
    c = get_console()
    assert isinstance(c, Console)


def test_setup_logging_cria_diretorio_logs():
    """Após setup_logging, o diretório logs/ existe no projeto."""
    from logger_config import setup_logging
    setup_logging()
    base = Path(__file__).resolve().parent.parent
    log_dir = base / "logs"
    assert log_dir.is_dir()


def test_console_exportado():
    """console está disponível no módulo."""
    from rich.console import Console

    from logger_config import console
    assert isinstance(console, Console)
