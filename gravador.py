"""
Grava a janela do Microsoft Teams usando FFmpeg (gdigrab no Windows).
Suporta AV1, HEVC e H.264 para arquivos pequenos com boa qualidade.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

import pygetwindow as gw
from loguru import logger

import config
from file_manager import FileManager


def _sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos para nome de arquivo."""
    clean = re.sub(r'[<>:"/\\|?*]+', "_", name)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:120] if len(clean) > 120 else clean


def _build_output_base(window_title: str) -> Path:
    """Gera o path base do arquivo de saída: timestamp__titulo_sanitizado."""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_title = _sanitize_filename(window_title or "Teams")
    filename = f"{ts}__{safe_title}"
    return Path(config.GRAVACOES_DIR) / filename


def _janela_em_foco(win) -> bool:
    """Verifica se a janela está em foco (leak prevention)."""
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        hwnd_fg = ctypes.windll.user32.GetForegroundWindow()  # type: ignore[attr-defined]
        return getattr(win, "hWnd", getattr(win, "_hWnd", None)) == hwnd_fg
    except Exception:
        return True


def _contains_screen_share_keywords(title: str) -> bool:
    if not title.strip():
        return False
    keywords = [
        k.strip()
        for k in config.TEAMS_SCREEN_SHARE_KEYWORDS.split("|")
        if k.strip()
    ]
    title_lower = title.lower()
    return any(keyword.lower() in title_lower for keyword in keywords)


def _find_teams_window():
    """
    Retorna a melhor janela encontrada do Teams.
    Prioridades: título, visível, em foco, maior área; compartilhamento de tela ganha prioridade extra.
    """
    target = config.TEAMS_WINDOW_TITLE.lower()
    candidates = []

    for win in gw.getAllWindows():
        title = (getattr(win, "title", "") or "").strip()
        if not title:
            continue
        if target not in title.lower():
            continue

        width = max(0, int(getattr(win, "width", 0) or 0))
        height = max(0, int(getattr(win, "height", 0) or 0))
        area = width * height
        visible = width > 0 and height > 0
        active = _janela_em_foco(win)
        screen_share = _contains_screen_share_keywords(title)

        score = (
            1000 if screen_share else 0,
            100 if active else 0,
            10 if visible else 0,
            area,
        )
        candidates.append((score, win, title))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    best = candidates[0][1]
    logger.info("Janela selecionada: {}", candidates[0][2])
    return best


def _build_ffmpeg_cmd(
    output_path: Path,
    use_hwnd: bool,
    hwnd: int | None,
    window_title: str,
    mode: Literal["screen_share", "video"] = "video",
) -> tuple[list[str], str]:
    """Monta o comando FFmpeg para captura gdigrab + codec; opcionalmente áudio dshow."""
    base = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", config.FFMPEG_LOGLEVEL,
        "-f", "gdigrab", "-framerate", str(config.FPS),
    ]
    if use_hwnd and hwnd is not None:
        base.extend(["-i", f"hwnd={hwnd}"])
    else:
        base.extend(["-i", f"title={window_title}"])

    has_audio = bool(config.AUDIO_DEVICE_DSHOW)
    if has_audio:
        base.extend(["-f", "dshow", "-i", config.AUDIO_DEVICE_DSHOW])

    crf = config.CRF
    if mode == "screen_share":
        crf = min(40, crf + config.CRF_OFFSET_SCREEN_SHARE)

    ext = "mkv"
    if config.CODEC == "av1":
        base.extend(["-c:v", "libsvtav1", "-preset", str(config.AV1_PRESET), "-crf", str(crf)])
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
        base.extend(["-c:a", "libopus", "-b:a", "32k", "-shortest"])

    out = str(output_path.with_suffix(f".{ext}"))
    base.append(out)
    return base, out


def parar_gravacao(proc: subprocess.Popen) -> None:
    """
    Encerra a gravação enviando 'q' ao stdin do FFmpeg para fechar o container
    graciosamente. Se não responder em 5s, faz kill.
    """
    if proc is None or proc.poll() is not None:
        return
    try:
        proc.communicate(input=b"q", timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)


def copiar_para_gdrive(local_path: Path) -> bool:
    """Copia o arquivo gravado para a pasta local do Google Drive (delega ao FileManager)."""
    return FileManager.copy_to_gdrive_local(local_path)


class TeamsRecorder:
    """Implementa a lógica de buscar a janela do Teams e gravar com FFmpeg."""

    def __init__(self) -> None:
        self.window = None
        self.window_title = ""
        self.mode: Literal["screen_share", "video"] = "video"

    def find_window(self) -> bool:
        """Localiza a melhor janela do Teams. Retorna True se encontrou."""
        self.window = _find_teams_window()
        if self.window is None:
            return False
        self.window_title = (getattr(self.window, "title", "") or "").strip()
        self.mode = (
            "screen_share"
            if _contains_screen_share_keywords(self.window_title)
            else "video"
        )
        logger.info("Modo detectado: {}", self.mode)
        return True

    def start(self, sufixo: str = "") -> tuple[subprocess.Popen | None, Path | None]:
        if shutil.which("ffmpeg") is None:
            logger.error("FFmpeg não encontrado. Instale e adicione ao PATH.")
            return None, None

        if self.window is None and not self.find_window():
            logger.error(
                "Nenhuma janela com '{}' no título encontrada. Abra o app do Teams.",
                config.TEAMS_WINDOW_TITLE,
            )
            return None, None

        if not _janela_em_foco(self.window):
            logger.warning(
                "A janela do Teams não está em foco. Coloque-a em foco para evitar gravar outras janelas."
            )

        hwnd = getattr(self.window, "hWnd", getattr(self.window, "_hWnd", None))
        use_hwnd = hwnd is not None

        gravacoes_dir = Path(config.GRAVACOES_DIR)
        gravacoes_dir.mkdir(parents=True, exist_ok=True)
        data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nome = f"aula_{data_hora}{sufixo}" if sufixo else f"aula_{data_hora}"
        output_path = gravacoes_dir / nome

        cmd, out_str = _build_ffmpeg_cmd(
            output_path,
            use_hwnd=use_hwnd,
            hwnd=hwnd,
            window_title=self.window_title,
            mode=self.mode,
        )
        out_path = Path(out_str)
        logger.info("Janela: {}", self.window_title)
        if self.mode == "screen_share":
            logger.info("Modo detectado: compartilhamento de tela (CRF otimizado para arquivo menor).")
        logger.info("Gravando em: {}", out_path)
        logger.info("Para parar: feche este terminal ou pressione Ctrl+C.")

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            return proc, out_path
        except FileNotFoundError:
            logger.error("FFmpeg não encontrado no PATH.")
            return None, None
        except Exception as e:
            logger.exception("Erro ao iniciar FFmpeg: {}", e)
            return None, None


def gravar(sufixo: str = "") -> tuple[subprocess.Popen | None, Path | None]:
    """
    Localiza a janela do Teams e inicia a gravação com FFmpeg.
    Retorna (processo, caminho_do_arquivo). Encerre com parar_gravacao(proc) ou Ctrl+C.
    """
    rec = TeamsRecorder()
    if not rec.find_window():
        return None, None
    return rec.start(sufixo=sufixo)
