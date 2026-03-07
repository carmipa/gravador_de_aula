"""
Grava a janela do Microsoft Teams usando FFmpeg (gdigrab no Windows).
Suporta AV1, HEVC e H.264 para arquivos pequenos com boa qualidade.
Arquitetura: RecorderInterface -> TeamsRecorder; FileManager para hash e cópia.
"""
import re
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pygetwindow as gw
from loguru import logger

import config

if TYPE_CHECKING:
    from pygetwindow import BaseWindow


def _janela_em_foco(win: "BaseWindow") -> bool:
    """Verifica se a janela está em foco (evita gravar notificações de outras apps - leak prevention)."""
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        hwnd_fg = ctypes.windll.user32.GetForegroundWindow()  # type: ignore[attr-defined]
        return getattr(win, "hWnd", None) == hwnd_fg
    except Exception:
        return True


def _find_teams_window():
    """Retorna a primeira janela cujo título contém TEAMS_WINDOW_TITLE."""
    title = config.TEAMS_WINDOW_TITLE
    for win in gw.getAllWindows():
        if not win.title:
            continue
        if title.lower() in win.title.lower():
            return win
    return None


def _detect_teams_mode(window_title: str) -> Literal["screen_share", "video"]:
    """
    Detecta se o Teams está em compartilhamento de tela ou vídeo pelo título da janela.
    Modo compartilhamento → bitrate tipicamente menor → CRF mais alto para arquivo menor.
    """
    if not window_title:
        return "video"
    keywords = getattr(config, "TEAMS_SCREEN_SHARE_KEYWORDS", "Compartilhando|Screen|Partage|Sharing")
    pattern = re.compile("|".join(re.escape(k.strip()) for k in keywords.split("|") if k.strip()), re.I)
    return "screen_share" if pattern.search(window_title) else "video"


def _build_ffmpeg_cmd(
    output_path: Path,
    use_hwnd: bool,
    hwnd: int,
    window_title: str,
    mode: Literal["screen_share", "video"] = "video",
):
    """Monta o comando FFmpeg para captura gdigrab + codec; opcionalmente áudio dshow; CRF dinâmico por modo."""
    base = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning"]
    base.extend(["-f", "gdigrab", "-framerate", str(config.FPS)])
    if use_hwnd and hwnd is not None:
        base.extend(["-i", f"hwnd={hwnd}"])
    else:
        base.extend(["-i", f"title={window_title}"])

    has_audio = bool(getattr(config, "AUDIO_DEVICE_DSHOW", None))
    if has_audio:
        base.extend(["-f", "dshow", "-i", config.AUDIO_DEVICE_DSHOW])

    # Bitrate dinâmico: compartilhamento de tela = mais estático → CRF mais alto (arquivo menor).
    crf = config.CRF
    if mode == "screen_share":
        offset = getattr(config, "CRF_OFFSET_SCREEN_SHARE", 3)
        crf = min(32, crf + offset)
    ext = "mkv"

    if config.CODEC == "av1":
        # libsvtav1: preset 10 = mais lento, arquivos menores (ideal para aulas, pouco movimento)
        preset = getattr(config, "AV1_PRESET", 10)
        base.extend(["-c:v", "libsvtav1", "-preset", str(preset), "-crf", str(crf)])
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

    if has_audio:
        base.extend(["-c:a", "libopus", "-b:a", "32k"])
        base.append("-shortest")

    out = str(output_path.with_suffix(f".{ext}"))
    base.append(out)
    return base, out


class RecorderInterface(ABC):
    """Interface para gravadores (ex.: Teams, futuros Genérico/Chrome)."""

    @abstractmethod
    def find_window(self):
        """Retorna a janela a ser gravada ou None."""
        ...

    @abstractmethod
    def start(self, sufixo: str = "") -> tuple[subprocess.Popen | None, Path | None]:
        """Inicia a gravação. Retorna (processo, caminho_arquivo)."""
        ...


class TeamsRecorder(RecorderInterface):
    """Implementa a lógica específica de buscar a janela do Teams e gravar com FFmpeg."""

    def find_window(self):
        return _find_teams_window()

    def start(self, sufixo: str = "") -> tuple[subprocess.Popen | None, Path | None]:
        if shutil.which("ffmpeg") is None:
            logger.error("FFmpeg não encontrado. Instale e adicione ao PATH.")
            return None, None

        win = self.find_window()
        if not win:
            logger.error(
                f"Nenhuma janela com '{config.TEAMS_WINDOW_TITLE}' no título encontrada. "
                "Abra o app do Teams e deixe a janela da reunião visível."
            )
            return None, None

        # Leak prevention: avisar se a janela não está em foco (evitar gravar e-mail/Slack etc.)
        if not _janela_em_foco(win):
            logger.warning(
                "A janela do Teams não está em foco. Coloque-a em foco ou full screen "
                "para evitar gravar notificações de outras janelas."
            )

        hwnd = getattr(win, "hWnd", None)
        use_hwnd = hwnd is not None

        Path(config.GRAVACOES_DIR).mkdir(parents=True, exist_ok=True)
        data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nome = f"aula_{data_hora}{sufixo}" if sufixo else f"aula_{data_hora}"
        output_path = Path(config.GRAVACOES_DIR) / nome

        mode = _detect_teams_mode(win.title)
        cmd, out_path = _build_ffmpeg_cmd(output_path, use_hwnd, hwnd, win.title, mode=mode)
        out_path = Path(out_path)
        logger.info(f"Janela: {win.title}")
        if mode == "screen_share":
            logger.info("Modo detectado: compartilhamento de tela (CRF otimizado para arquivo menor).")
        logger.info(f"Gravando em: {out_path}")
        logger.info("Para parar: feche este terminal ou pressione Ctrl+C.")

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            return proc, out_path
        except FileNotFoundError:
            logger.error("FFmpeg não encontrado no PATH.")
            return None, None
        except Exception as e:
            logger.exception(f"Erro ao iniciar FFmpeg: {e}")
            return None, None


def gravar(sufixo: str = "") -> tuple[subprocess.Popen | None, Path | None]:
    """
    Localiza a janela do Teams e inicia a gravação com FFmpeg (via TeamsRecorder).
    Retorna (processo, caminho_do_arquivo). Encerre com parar_gravacao(proc) ou Ctrl+C.
    """
    return TeamsRecorder().start(sufixo=sufixo)


def parar_gravacao(processo: subprocess.Popen) -> None:
    """
    Encerra a gravação enviando 'q' ao stdin do FFmpeg para fechar o container
    graciosamente (evita arquivo .mp4/.mkv corrompido por cabeçalho não finalizado).
    Se o processo não responder em 5s, faz kill.
    """
    if processo is None or processo.poll() is not None:
        return
    try:
        processo.communicate(input=b"q", timeout=5)
    except subprocess.TimeoutExpired:
        processo.kill()
        processo.wait(timeout=2)


def copiar_para_gdrive(local_path: Path) -> bool:
    """Copia o arquivo gravado para a pasta local do Google Drive (delega ao FileManager)."""
    from file_manager import FileManager
    return FileManager.copy_to_gdrive_local(local_path)
