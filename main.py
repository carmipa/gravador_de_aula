"""
Gravador de Aula - Teams FIAP
Execute antes de entrar na reunião (ou com a janela do Teams já aberta).
Grava só a janela do Teams. Para parar: Ctrl+C. Opcional: copia para pasta do GDrive.
"""
import signal
import sys

import config
import gravador
from upload_gdrive import upload_para_drive_api


def main():
    print("Gravador de Aula - Teams")
    print(f"Codec: {config.CODEC} | CRF: {config.CRF} | Saída: {config.GRAVACOES_DIR}")
    print()

    proc, out_path = gravador.gravar()
    if proc is None:
        sys.exit(1)

    def encerrar(sig=None, frame=None):
        gravador.parar_gravacao(proc)
        if out_path and out_path.exists():
            if config.GDRIVE_PASTA_LOCAL:
                gravador.copiar_para_gdrive(out_path)
            if config.GDRIVE_PASTA_ID:
                upload_para_drive_api(out_path)
        print("Gravação encerrada.")
        sys.exit(0)

    signal.signal(signal.SIGINT, encerrar)
    signal.signal(signal.SIGTERM, encerrar)

    proc.wait()
    if out_path and out_path.exists():
        if config.GDRIVE_PASTA_LOCAL:
            gravador.copiar_para_gdrive(out_path)
        if config.GDRIVE_PASTA_ID:
            upload_para_drive_api(out_path)
    print("Gravação encerrada.")


if __name__ == "__main__":
    main()
