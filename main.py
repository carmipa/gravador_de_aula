"""
Gravador de Aula - Teams FIAP
Execute antes de entrar na reunião (ou com a janela do Teams já aberta).
Grava só a janela do Teams. Para parar: Ctrl+C. Opcional: cópia/upload em background.
Health check: alerta se o arquivo parar de crescer (codec travado).
"""
from __future__ import annotations

import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

from loguru import logger

import config
import gravador
from gravador import TeamsRecorder, parar_gravacao
from logger_config import console, setup_logging
from upload_gdrive import upload_para_drive_api

_processo_atual: subprocess.Popen | None = None
_out_path_atual: Path | None = None


def _monitor_health(processo: subprocess.Popen, out_path: Path) -> None:
    """Enquanto o processo estiver ativo, verifica se o arquivo de saída está crescendo."""
    interval = config.HEALTH_CHECK_INTERVAL_SEC
    stall_sec = config.HEALTH_CHECK_STALL_SECONDS

    last_size: int | None = None
    last_growth_time = time.monotonic()

    while processo.poll() is None:
        time.sleep(interval)

        if processo.poll() is not None:
            break

        if not out_path.exists():
            continue

        try:
            size = out_path.stat().st_size
        except OSError:
            continue

        if last_size is None or size > last_size:
            last_size = size
            last_growth_time = time.monotonic()
            continue

        stalled_for = time.monotonic() - last_growth_time
        if stalled_for >= stall_sec:
            logger.critical(
                "Health check: arquivo não cresce há {}s (codec pode ter travado). Tamanho atual: {} bytes.",
                stall_sec,
                last_size,
            )
            last_growth_time = time.monotonic()


def _upload_em_background(out_path: Path) -> None:
    """Executa cópia local e upload API em uma thread (libera o terminal imediatamente)."""
    try:
        if config.GDRIVE_PASTA_LOCAL:
            gravador.copiar_para_gdrive(out_path)

        if config.GDRIVE_PASTA_ID:
            upload_para_drive_api(out_path)

        logger.info("Upload/cópia em background concluídos.")
    except Exception:
        logger.exception("Falha no upload/cópia em background.")


def _signal_handler(signum, frame) -> None:
    global _processo_atual
    if _processo_atual is not None:
        logger.warning("Sinal {} recebido. Encerrando gravação...", signum)
        parar_gravacao(_processo_atual)


def _encerrar_por_sinal(sig=None, frame=None) -> None:
    """Handler para SIGTERM: encerra graciosamente e inicia upload em background se configurado."""
    global _processo_atual, _out_path_atual
    if _processo_atual is not None:
        parar_gravacao(_processo_atual)
    if _out_path_atual and _out_path_atual.exists() and (config.GDRIVE_PASTA_LOCAL or config.GDRIVE_PASTA_ID):
        t = threading.Thread(
            target=_upload_em_background,
            args=(_out_path_atual,),
            daemon=False,
            name="UploadSigterm",
        )
        t.start()
    logger.warning("Sinal de encerramento recebido. Gravação finalizada.")
    sys.exit(0)


@logger.catch(reraise=False)
def main() -> None:
    global _processo_atual, _out_path_atual

    setup_logging()

    signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _encerrar_por_sinal)

    logger.info(
        "Codec: {} | CRF: {} | FPS: {} | Saída: {}",
        config.CODEC,
        config.CRF,
        config.FPS,
        config.GRAVACOES_DIR,
    )

    recorder = TeamsRecorder()

    with console.status("[bold yellow]Buscando janela do Teams...[/]", spinner="bouncingBar"):
        if not recorder.find_window():
            logger.error("Janela do Teams não encontrada. Certifique-se de que o app está aberto.")
            sys.exit(1)

    processo, out_path = recorder.start()
    if processo is None or out_path is None:
        logger.error("Falha ao iniciar gravação (FFmpeg ou janela).")
        sys.exit(1)

    _processo_atual = processo
    _out_path_atual = Path(out_path)

    logger.info("Gravação em andamento: {}", _out_path_atual)
    logger.info("Para parar: feche este terminal ou pressione Ctrl+C.")

    health_thread = threading.Thread(
        target=_monitor_health,
        args=(processo, _out_path_atual),
        daemon=True,
        name="HealthCheck",
    )
    health_thread.start()

    try:
        processo.wait()
    except KeyboardInterrupt:
        logger.warning("Interrupção detectada. Finalizando gravação graciosamente...")
        parar_gravacao(processo)
        logger.success("Arquivo salvo e finalizado com sucesso.")
    except Exception as e:
        logger.critical("Erro crítico no fluxo principal: {}", e)
        parar_gravacao(processo)
        sys.exit(1)
    finally:
        _processo_atual = None
        _out_path_atual = None

        if out_path and Path(out_path).exists():
            if config.GDRIVE_PASTA_LOCAL or config.GDRIVE_PASTA_ID:
                upload_thread = threading.Thread(
                    target=_upload_em_background,
                    args=(out_path,),
                    daemon=False,
                    name="UploadBackground",
                )
                upload_thread.start()
                logger.info("Gravação encerrada. Cópia/upload em background.")
            else:
                logger.info("Gravação encerrada.")
        else:
            logger.info("Gravação encerrada.")


if __name__ == "__main__":
    main()
