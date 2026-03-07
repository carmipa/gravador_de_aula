"""
Configuração centralizada de logs: UX no terminal (Rich) e auditoria em arquivo (GRC).
Segurança: logs de arquivo não incluem credenciais; tracebacks completos para depuração.
"""
from __future__ import annotations

from loguru import logger
from rich.console import Console
from rich.logging import RichHandler

import config

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
        level=config.LOG_LEVEL,
    )

    # Arquivo: foco em GRC — auditoria completa, rotação e retenção
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(config.LOG_DIR / "audit_{time:YYYY-MM-DD}.log"),
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
