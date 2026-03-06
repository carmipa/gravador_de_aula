"""
Fixtures compartilhadas para os testes.
Evita duplicação e centraliza mocks (pygetwindow, subprocess, config, filesystem).
"""
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tmp_gravacoes_dir(tmp_path):
    """Diretório temporário para simular GRAVACOES_DIR."""
    d = tmp_path / "gravacoes"
    d.mkdir()
    return d


@pytest.fixture
def sample_video_file(tmp_path):
    """Arquivo binário temporário (simula vídeo) para testes de hash e cópia."""
    f = tmp_path / "aula_teste.mkv"
    # Conteúdo determinístico para hash previsível
    f.write_bytes(b"x" * 10000)
    return f


@pytest.fixture
def sample_large_file(tmp_path):
    """Arquivo > 1MB para testar barra de progresso no hash_sha256."""
    f = tmp_path / "large.mkv"
    f.write_bytes(b"y" * (1024 * 1024 + 100))
    return f


@pytest.fixture
def mock_teams_window():
    """Janela fake do Teams para pygetwindow."""
    win = MagicMock()
    win.title = "Microsoft Teams - Reunião"
    win.hWnd = 12345
    return win


@pytest.fixture
def mock_gw_empty():
    """Lista vazia de janelas (nenhum Teams)."""
    return []


@pytest.fixture
def mock_gw_with_teams(mock_teams_window):
    """Lista com uma janela Teams."""
    return [mock_teams_window]


@pytest.fixture
def mock_popen():
    """Processo fake que simula FFmpeg em execução e depois encerra."""
    proc = MagicMock(spec=subprocess.Popen)
    proc.poll.return_value = None  # ainda rodando
    proc.communicate.return_value = (b"", b"")
    return proc


@pytest.fixture
def mock_popen_finished():
    """Processo fake que já terminou (poll retorna 0)."""
    proc = MagicMock(spec=subprocess.Popen)
    proc.poll.return_value = 0
    return proc
