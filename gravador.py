"""
Grava a janela do Microsoft Teams usando FFmpeg (gdigrab no Windows).
Suporta AV1, HEVC e H.264 para arquivos pequenos com boa qualidade.
"""
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pygetwindow as gw

import config


def _find_teams_window():
    """Retorna a primeira janela cujo título contém TEAMS_WINDOW_TITLE."""
    title = config.TEAMS_WINDOW_TITLE
    for win in gw.getAllWindows():
        if not win.title:
            continue
        if title.lower() in win.title.lower():
            return win
    return None


def _build_ffmpeg_cmd(output_path: Path, use_hwnd: bool, hwnd: int, window_title: str):
    """Monta o comando FFmpeg para captura gdigrab + codec escolhido."""
    base = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning"]
    base.extend(["-f", "gdigrab", "-framerate", str(config.FPS)])
    if use_hwnd and hwnd is not None:
        base.extend(["-i", f"hwnd={hwnd}"])
    else:
        base.extend(["-i", f"title={window_title}"])

    crf = config.CRF
    ext = "mkv"

    if config.CODEC == "av1":
        # libsvtav1: preset 8 = bom equilíbrio velocidade/compressão
        base.extend(["-c:v", "libsvtav1", "-preset", "8", "-crf", str(crf)])
        ext = "mkv"
    elif config.CODEC == "hevc_nvenc":
        base.extend(["-c:v", "hevc_nvenc", "-rc", "vbr", "-cq", str(crf)])
        ext = "mp4"
    elif config.CODEC == "hevc":
        base.extend(["-c:v", "libx265", "-preset", "medium", "-crf", str(crf)])
        ext = "mkv"
    else:
        base.extend(["-c:v", "libx264", "-preset", "fast", "-crf", str(crf)])
        ext = "mp4"

    out = str(output_path.with_suffix(f".{ext}"))
    base.append(out)
    return base, out


def gravar(sufixo: str = "") -> tuple[subprocess.Popen | None, Path | None]:
    """
    Localiza a janela do Teams e inicia a gravação com FFmpeg.
    Retorna (processo, caminho_do_arquivo). Encerre com Ctrl+C; depois use copiar_para_gdrive(caminho).
    """
    if shutil.which("ffmpeg") is None:
        print("Erro: FFmpeg não encontrado. Instale e adicione ao PATH.", file=sys.stderr)
        return None, None

    win = _find_teams_window()
    if not win:
        print(
            f"Nenhuma janela com '{config.TEAMS_WINDOW_TITLE}' no título encontrada. "
            "Abra o app do Teams e deixe a janela da reunião visível.",
            file=sys.stderr,
        )
        return None, None

    # HWND para captura estável (FFmpeg 7+ suporta hwnd= no gdigrab)
    hwnd = getattr(win, "hWnd", None)
    use_hwnd = hwnd is not None

    Path(config.GRAVACOES_DIR).mkdir(parents=True, exist_ok=True)
    data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nome = f"aula_{data_hora}{sufixo}" if sufixo else f"aula_{data_hora}"
    output_path = Path(config.GRAVACOES_DIR) / nome

    cmd, out_path = _build_ffmpeg_cmd(output_path, use_hwnd, hwnd, win.title)
    out_path = Path(out_path)
    print(f"Janela: {win.title}")
    print(f"Gravando em: {out_path}")
    print("Para parar: feche este terminal ou pressione Ctrl+C.")

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return proc, out_path
    except FileNotFoundError:
        print("Erro: FFmpeg não encontrado no PATH.", file=sys.stderr)
        return None, None
    except Exception as e:
        print(f"Erro ao iniciar FFmpeg: {e}", file=sys.stderr)
        return None, None


def copiar_para_gdrive(local_path: Path) -> bool:
    """Copia o arquivo gravado para a pasta local do Google Drive, se configurada."""
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
