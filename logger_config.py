"""
Configuração centralizada de logs: UX no terminal (Rich) e auditoria em arquivo (GRC).
Segurança: logs de arquivo não incluem credenciais; tracebacks completos para depuração.
"""
from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.logging import RichHandler

console = Console()


def setup_logging() -> None:
    """Remove o handler padrão do Loguru e adiciona terminal (Rich) + arquivo de auditoria."""
    logger.remove()

    # Terminal: foco em UX com ícones, cores e tracebacks ricos
    logger.add(
        RichHandler(
            console=console,
            rich_tracebacks=True,
            markup=True,
            show_path=False,
        ),
        format="[bold blue]FIAP-BOT[/] | {message}",
        level="INFO",
    )

    # Arquivo: foco em GRC — auditoria completa, rotação e retenção
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    logger.add(
        log_dir / "audit_{time:YYYY-MM-DD}.log",
        rotation="100 MB",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
    )

    logger.info("Sistema de monitoramento e auditoria iniciado.")


def get_console() -> Console:
    """Retorna o Console do Rich para uso em outros módulos (ex.: barra de progresso)."""
    return console
