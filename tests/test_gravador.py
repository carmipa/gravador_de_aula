"""
Testes do módulo gravador.
Cobre: _build_ffmpeg_cmd (todos os codecs), _janela_em_foco, _find_teams_window,
parar_gravacao, TeamsRecorder, gravar, copiar_para_gdrive.
"""
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import gravador
from gravador import (
    TeamsRecorder,
    _build_ffmpeg_cmd,
    _find_teams_window,
    _janela_em_foco,
    copiar_para_gdrive,
    gravar,
    parar_gravacao,
)


# --- _build_ffmpeg_cmd (com config mockado) ---


@patch("gravador.config")
def test_build_ffmpeg_cmd_av1(mock_config, tmp_gravacoes_dir):
    mock_config.FPS = 30
    mock_config.CODEC = "av1"
    mock_config.CRF = 30
    mock_config.AUDIO_DEVICE_DSHOW = None
    mock_config.AV1_PRESET = 10
    out = tmp_gravacoes_dir / "aula"
    cmd, path = _build_ffmpeg_cmd(out, False, None, "Teams")
    assert "ffmpeg" in cmd
    assert "-f" in cmd and "gdigrab" in cmd
    assert "-c:v" in cmd and "libsvtav1" in cmd
    assert "-preset" in cmd and "10" in cmd
    assert path.endswith(".mkv")


@patch("gravador.config")
def test_build_ffmpeg_cmd_hevc_nvenc(mock_config, tmp_gravacoes_dir):
    mock_config.FPS = 30
    mock_config.CODEC = "hevc_nvenc"
    mock_config.CRF = 28
    mock_config.AUDIO_DEVICE_DSHOW = None
    out = tmp_gravacoes_dir / "aula"
    cmd, path = _build_ffmpeg_cmd(out, False, None, "Teams")
    assert "hevc_nvenc" in cmd
    assert path.endswith(".mp4")


@patch("gravador.config")
def test_build_ffmpeg_cmd_hevc(mock_config, tmp_gravacoes_dir):
    mock_config.FPS = 30
    mock_config.CODEC = "hevc"
    mock_config.CRF = 28
    mock_config.AUDIO_DEVICE_DSHOW = None
    out = tmp_gravacoes_dir / "aula"
    cmd, path = _build_ffmpeg_cmd(out, False, None, "Teams")
    assert "libx265" in cmd
    assert path.endswith(".mkv")


@patch("gravador.config")
def test_build_ffmpeg_cmd_h264(mock_config, tmp_gravacoes_dir):
    mock_config.FPS = 30
    mock_config.CODEC = "h264"
    mock_config.CRF = 23
    mock_config.AUDIO_DEVICE_DSHOW = None
    out = tmp_gravacoes_dir / "aula"
    cmd, path = _build_ffmpeg_cmd(out, False, None, "Teams")
    assert "libx264" in cmd
    assert path.endswith(".mp4")


@patch("gravador.config")
def test_build_ffmpeg_cmd_com_hwnd(mock_config, tmp_gravacoes_dir):
    mock_config.FPS = 30
    mock_config.CODEC = "av1"
    mock_config.CRF = 30
    mock_config.AUDIO_DEVICE_DSHOW = None
    mock_config.AV1_PRESET = 10
    out = tmp_gravacoes_dir / "aula"
    cmd, _ = _build_ffmpeg_cmd(out, True, 99999, "Teams")
    assert "hwnd=99999" in cmd


@patch("gravador.config")
def test_build_ffmpeg_cmd_com_audio_dshow(mock_config, tmp_gravacoes_dir):
    mock_config.FPS = 30
    mock_config.CODEC = "av1"
    mock_config.CRF = 30
    mock_config.AUDIO_DEVICE_DSHOW = "audio=Virtual Cable"
    mock_config.AV1_PRESET = 10
    out = tmp_gravacoes_dir / "aula"
    cmd, _ = _build_ffmpeg_cmd(out, False, None, "Teams")
    assert "dshow" in cmd
    assert "audio=Virtual Cable" in cmd
    assert "libopus" in cmd
    assert "-shortest" in cmd


# --- _janela_em_foco ---


def test_janela_em_foco_nao_win32_retorna_true():
    """Em não-Windows, sempre retorna True (não quebra)."""
    with patch("gravador.sys") as m:
        m.platform = "linux"
        win = MagicMock()
        win.hWnd = 1
        assert _janela_em_foco(win) is True


def test_janela_em_foco_win32_excecao_retorna_true():
    """Se GetForegroundWindow (ctypes) levantar exceção, retorna True (fallback seguro)."""
    win = MagicMock()
    win.hWnd = 12345
    mock_ctypes = MagicMock()
    mock_ctypes.windll.user32.GetForegroundWindow.side_effect = OSError("DLL not found")
    with patch("gravador.sys") as m:
        m.platform = "win32"
    with patch.dict("sys.modules", {"ctypes": mock_ctypes}):
        # _janela_em_foco faz "import ctypes" dentro da função; pega nosso mock
        assert _janela_em_foco(win) is True


# --- _find_teams_window ---


def test_find_teams_window_vazio():
    """Sem janelas com título Teams, retorna None."""
    with patch("gravador.gw.getAllWindows", return_value=[]):
        assert _find_teams_window() is None


def test_find_teams_window_ignora_sem_titulo():
    """Janelas sem título são ignoradas."""
    with patch("gravador.gw.getAllWindows") as m:
        w = MagicMock()
        w.title = None
        m.return_value = [w]
        assert _find_teams_window() is None


def test_find_teams_window_encontra():
    """Retorna primeira janela cujo título contém TEAMS_WINDOW_TITLE (case insensitive)."""
    with patch("gravador.config") as cfg:
        cfg.TEAMS_WINDOW_TITLE = "Teams"
    win_teams = MagicMock()
    win_teams.title = "Microsoft Teams - Reunião"
    with patch("gravador.gw.getAllWindows", return_value=[win_teams]):
        assert _find_teams_window() is win_teams


def test_find_teams_window_case_insensitive():
    """Busca é case insensitive."""
    with patch("gravador.config") as cfg:
        cfg.TEAMS_WINDOW_TITLE = "teams"
    win = MagicMock()
    win.title = "TEAMS"
    with patch("gravador.gw.getAllWindows", return_value=[win]):
        assert _find_teams_window() is win


# --- parar_gravacao ---


def test_parar_gravacao_none_nao_faz_nada():
    """Processo None: não chama communicate nem kill."""
    parar_gravacao(None)


def test_parar_gravacao_ja_terminado(mock_popen_finished):
    """Processo já terminado (poll() != None): retorna sem fazer nada."""
    parar_gravacao(mock_popen_finished)
    mock_popen_finished.communicate.assert_not_called()


def test_parar_gravacao_envia_q_e_communicate(mock_popen):
    """Processo ativo: envia 'q' e communicate(timeout=5)."""
    mock_popen.poll.return_value = None
    parar_gravacao(mock_popen)
    mock_popen.communicate.assert_called_once_with(input=b"q", timeout=5)


def test_parar_gravacao_timeout_faz_kill(mock_popen):
    """Se communicate levantar TimeoutExpired, faz kill e wait."""
    import subprocess as sp
    mock_popen.poll.return_value = None
    mock_popen.communicate.side_effect = sp.TimeoutExpired("ffmpeg", 5)
    parar_gravacao(mock_popen)
    mock_popen.kill.assert_called_once()
    mock_popen.wait.assert_called_once()


# --- TeamsRecorder ---


def test_teams_recorder_find_window_delega():
    """TeamsRecorder.find_window chama _find_teams_window."""
    with patch("gravador._find_teams_window", return_value=MagicMock()) as m:
        r = TeamsRecorder()
        r.find_window()
        m.assert_called_once()


def test_teams_recorder_start_sem_ffmpeg_retorna_none_none():
    """Sem ffmpeg no PATH, start retorna (None, None)."""
    with patch("gravador.shutil.which", return_value=None):
        with patch("gravador.gw.getAllWindows", return_value=[MagicMock(title="Teams")]):
            rec = TeamsRecorder()
            proc, path = rec.start()
            assert proc is None
            assert path is None


def test_teams_recorder_start_sem_janela_retorna_none_none():
    """Sem janela Teams, start retorna (None, None)."""
    with patch("gravador.shutil.which", return_value="/usr/bin/ffmpeg"):
        with patch("gravador.gw.getAllWindows", return_value=[]):
            rec = TeamsRecorder()
            proc, path = rec.start()
            assert proc is None
            assert path is None


def test_teams_recorder_start_retorna_proc_e_path(tmp_gravacoes_dir, mock_teams_window, mock_popen):
    """Com janela e ffmpeg, start retorna (proc, out_path)."""
    with patch("gravador.shutil.which", return_value="/usr/bin/ffmpeg"):
        with patch("gravador.gw.getAllWindows", return_value=[mock_teams_window]):
            with patch("gravador.config") as cfg:
                cfg.TEAMS_WINDOW_TITLE = "Teams"
                cfg.GRAVACOES_DIR = str(tmp_gravacoes_dir)
                cfg.FPS = 30
                cfg.CODEC = "av1"
                cfg.CRF = 30
                cfg.AUDIO_DEVICE_DSHOW = None
                cfg.AV1_PRESET = 10
            with patch("gravador.subprocess.Popen", return_value=mock_popen):
                with patch("gravador._janela_em_foco", return_value=True):
                    rec = TeamsRecorder()
                    proc, path = rec.start()
                    assert proc is mock_popen
                    assert path is not None
                    assert isinstance(path, Path)
                    assert "aula_" in str(path)


# --- gravar ---


def test_gravar_delega_para_teams_recorder():
    """gravar() delega para TeamsRecorder().start()."""
    with patch.object(TeamsRecorder, "start", return_value=(MagicMock(), Path("/tmp/out.mkv"))):
        proc, path = gravar()
        assert proc is not None
        assert path is not None


# --- copiar_para_gdrive ---


def test_copiar_para_gdrive_delega_file_manager(sample_video_file):
    """copiar_para_gdrive chama FileManager.copy_to_gdrive_local."""
    with patch("file_manager.FileManager") as fm:
        fm.copy_to_gdrive_local.return_value = True
        result = copiar_para_gdrive(sample_video_file)
        fm.copy_to_gdrive_local.assert_called_once_with(sample_video_file)
        assert result is True
