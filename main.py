"""
Gravador de Aula - Teams FIAP
Execute antes de entrar na reunião (ou com a janela do Teams já aberta).
Grava só a janela do Teams. Para parar: Ctrl+C. Opcional: cópia/upload em background.
Health check: alerta se o arquivo parar de crescer (codec travado).
"""
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


# Referência para o handler de sinal encerrar a gravação graciosamente (SIGTERM)
_processo_atual: subprocess.Popen | None = None
_out_path_atual: Path | None = None


def _monitor_health(processo: subprocess.Popen, out_path: Path) -> None:
    """
    Enquanto o processo estiver ativo, verifica se o arquivo de saída está crescendo.
    Se parar de crescer por HEALTH_CHECK_STALL_SECONDS, dispara alerta crítico (codec pode ter travado).
    """
    interval = getattr(config, "HEALTH_CHECK_INTERVAL_SEC", 10)
    stall_sec = getattr(config, "HEALTH_CHECK_STALL_SECONDS", 30)
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
        if last_size is not None and size > last_size:
            last_size = size
            last_growth_time = time.monotonic()
        else:
            if last_size is None:
                last_size = size
            if time.monotonic() - last_growth_time >= stall_sec:
                logger.critical(
                    f"Health check: arquivo não cresce há {stall_sec}s (codec pode ter travado). "
                    f"Tamanho atual: {last_size} bytes. Verifique espaço em disco e codec."
                )
                last_growth_time = time.monotonic()


def _upload_em_background(out_path: Path) -> None:
    """Executa cópia local e upload API em uma thread (libera o terminal imediatamente)."""
    if config.GDRIVE_PASTA_LOCAL:
        gravador.copiar_para_gdrive(out_path)
    if config.GDRIVE_PASTA_ID:
        upload_para_drive_api(out_path)
    logger.info("Upload/cópia em background concluídos.")


@logger.catch(reraise=False)
def main() -> None:
    global _processo_atual, _out_path_atual
    setup_logging()

    logger.info(
        f"Codec: {config.CODEC} | CRF: {config.CRF} | Saída: {config.GRAVACOES_DIR}"
    )

    recorder = TeamsRecorder()

    with console.status("[bold yellow]Buscando janela do Teams...[/]", spinner="bouncingBar"):
        if not recorder.find_window():
            logger.error(
                "Janela do Teams não encontrada! Certifique-se de que o app está aberto."
            )
            sys.exit(1)

    processo, out_path = None, None
    try:
        processo, out_path = recorder.start()
        _processo_atual, _out_path_atual = processo, out_path
        if processo is None:
            logger.error("Falha ao iniciar gravação (FFmpeg ou janela).")
            sys.exit(1)

        logger.info(
            "Gravação em andamento... Pressione [bold white]Ctrl+C[/] para encerrar."
        )
        health_thread = threading.Thread(
            target=_monitor_health,
            args=(processo, out_path),
            daemon=True,
            name="HealthCheck",
        )
        health_thread.start()
        processo.wait()

    except KeyboardInterrupt:
        logger.warning("Interrupção detectada. Finalizando gravação graciosamente...")
        parar_gravacao(processo)
        logger.success("Arquivo salvo e finalizado com sucesso.")

    except Exception as e:
        logger.critical(f"Erro crítico no fluxo principal: {e}")
        if processo:
            parar_gravacao(processo)
        sys.exit(1)

    finally:
        _processo_atual, _out_path_atual = None, None
        if out_path and out_path.exists():
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


def _encerrar_por_sinal(sig=None, frame=None):
    """Handler para SIGTERM: encerra graciosamente (parar_gravacao) e sai."""
    global _processo_atual, _out_path_atual
    if _processo_atual is not None:
        parar_gravacao(_processo_atual)
    if _out_path_atual and _out_path_atual.exists() and (config.GDRIVE_PASTA_LOCAL or config.GDRIVE_PASTA_ID):
        t = threading.Thread(target=_upload_em_background, args=(_out_path_atual,), daemon=False, name="UploadSigterm")
        t.start()
    logger.warning("Sinal de encerramento recebido. Gravação finalizada.")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _encerrar_por_sinal)
    main()
