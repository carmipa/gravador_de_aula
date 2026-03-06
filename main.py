"""
Gravador de Aula - Teams FIAP
Execute antes de entrar na reunião (ou com a janela do Teams já aberta).
Grava só a janela do Teams. Para parar: Ctrl+C. Opcional: copia para pasta do GDrive.
Observabilidade: Loguru + Rich; resiliência com @logger.catch e finally para upload.
"""
import signal
import subprocess
import sys
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
            if config.GDRIVE_PASTA_LOCAL:
                gravador.copiar_para_gdrive(out_path)
            if config.GDRIVE_PASTA_ID:
                upload_para_drive_api(out_path)
        logger.info("Gravação encerrada.")


def _encerrar_por_sinal(sig=None, frame=None):
    """Handler para SIGTERM: encerra graciosamente (parar_gravacao) e sai."""
    global _processo_atual, _out_path_atual
    if _processo_atual is not None:
        parar_gravacao(_processo_atual)
    if _out_path_atual and _out_path_atual.exists():
        if config.GDRIVE_PASTA_LOCAL:
            gravador.copiar_para_gdrive(_out_path_atual)
        if config.GDRIVE_PASTA_ID:
            upload_para_drive_api(_out_path_atual)
    logger.warning("Sinal de encerramento recebido. Gravação finalizada.")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _encerrar_por_sinal)
    main()
