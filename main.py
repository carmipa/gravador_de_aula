"""
Gravador de Aula - Teams FIAP
Execute antes de entrar na reunião (ou com a janela do Teams já aberta).
Grava só a janela do Teams. Para parar: Ctrl+C. Opcional: cópia/upload em background.
Health check: alerta se o arquivo parar de crescer (codec travado).
CLI: fiap-recorder (--codec, --fps, --crf, --title, --no-upload, --list-windows).
"""
from __future__ import annotations

import argparse
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


def _upload_em_background(out_path: Path, skip_upload: bool = False) -> None:
    """Executa cópia local e upload API em uma thread (libera o terminal imediatamente)."""
    if skip_upload:
        logger.info("Upload ignorado por parâmetro de linha de comando.")
        return
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
            args=(_out_path_atual, False),
            daemon=False,
            name="UploadSigterm",
        )
        t.start()
    logger.warning("Sinal de encerramento recebido. Gravação finalizada.")
    sys.exit(0)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fiap-recorder",
        description="Gravador pessoal de aulas no Microsoft Teams com FFmpeg.",
    )
    parser.add_argument(
        "--codec",
        choices=["av1", "hevc_nvenc", "hevc", "h264"],
        help="Sobrescreve o codec definido no .env",
    )
    parser.add_argument(
        "--fps",
        type=int,
        help="Sobrescreve o FPS definido no .env",
    )
    parser.add_argument(
        "--crf",
        type=int,
        help="Sobrescreve o CRF definido no .env",
    )
    parser.add_argument(
        "--title",
        help="Sobrescreve o trecho do título da janela do Teams",
    )
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Não copia para Drive local nem faz upload por API",
    )
    parser.add_argument(
        "--list-windows",
        action="store_true",
        help="Lista as janelas abertas para ajudar no ajuste do título",
    )
    return parser


def _apply_cli_overrides(args: argparse.Namespace) -> None:
    if args.codec:
        config.CODEC = args.codec
    if args.fps is not None:
        config.FPS = max(10, min(60, args.fps))
    if args.crf is not None:
        config.CRF = max(18, min(40, args.crf))
    if args.title:
        config.TEAMS_WINDOW_TITLE = args.title.strip()


def _list_windows() -> None:
    import pygetwindow as gw

    logger.info("Listando janelas abertas...")
    for win in gw.getAllWindows():
        title = (getattr(win, "title", "") or "").strip()
        if title:
            print(title)


@logger.catch(reraise=False)
def run(skip_upload: bool = False) -> int:
    """Fluxo principal de gravação. Retorna 0 em sucesso, 1 em falha."""
    global _processo_atual, _out_path_atual

    setup_logging()

    signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _encerrar_por_sinal)

    logger.info("=== FIAP Class Recorder ===")
    logger.info(
        "Configuração: codec={} | crf={} | fps={} | pasta={}",
        config.CODEC,
        config.CRF,
        config.FPS,
        config.GRAVACOES_DIR,
    )

    recorder = TeamsRecorder()

    with console.status("[bold yellow]Buscando janela do Teams...[/]", spinner="bouncingBar"):
        if not recorder.find_window():
            logger.error("Nenhuma janela do Teams compatível foi encontrada.")
            return 1

    processo, out_path = recorder.start()
    if processo is None or out_path is None:
        logger.error("Falha ao iniciar a gravação.")
        return 1

    _processo_atual = processo
    _out_path_atual = Path(out_path)

    logger.success("Gravação em andamento: {}", _out_path_atual)
    logger.info("Pressione Ctrl+C para encerrar corretamente.")

    monitor_thread = threading.Thread(
        target=_monitor_health,
        args=(processo, _out_path_atual),
        daemon=True,
        name="HealthCheck",
    )
    monitor_thread.start()

    try:
        processo.wait()
    except KeyboardInterrupt:
        logger.warning("Interrupção detectada. Finalizando gravação graciosamente...")
        parar_gravacao(processo)
        logger.success("Arquivo salvo e finalizado com sucesso.")
    except Exception as e:
        logger.critical("Erro crítico no fluxo principal: {}", e)
        parar_gravacao(processo)
        return 1
    finally:
        _processo_atual = None
        _out_path_atual = None

        if out_path and Path(out_path).exists():
            upload_thread = threading.Thread(
                target=_upload_em_background,
                args=(out_path, skip_upload),
                daemon=False,
                name="UploadBackground",
            )
            upload_thread.start()
            if not skip_upload and (config.GDRIVE_PASTA_LOCAL or config.GDRIVE_PASTA_ID):
                logger.info("Gravação encerrada. Cópia/upload em background.")
            else:
                logger.info("Gravação encerrada.")
        else:
            logger.info("Gravação encerrada.")

    return 0


def main() -> None:
    """Ponto de entrada legado: chama run() e sai com o código de retorno."""
    sys.exit(run(skip_upload=False))


def cli() -> None:
    """Entry point da CLI (fiap-recorder)."""
    parser = _build_parser()
    args = parser.parse_args()

    _apply_cli_overrides(args)
    setup_logging()

    if args.list_windows:
        _list_windows()
        sys.exit(0)

    sys.exit(run(skip_upload=args.no_upload))


if __name__ == "__main__":
    cli()
