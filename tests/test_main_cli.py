"""
Testes da CLI (argparse, overrides, run com mocks).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import main


def test_parser_builds():
    """Parser aceita --codec, --fps, --crf."""
    parser = main._build_parser()
    args = parser.parse_args(["--codec", "av1", "--fps", "30", "--crf", "28"])
    assert args.codec == "av1"
    assert args.fps == 30
    assert args.crf == 28


def test_parser_no_upload_and_list_windows():
    """Parser aceita --no-upload e --list-windows."""
    parser = main._build_parser()
    args = parser.parse_args(["--no-upload"])
    assert args.no_upload is True
    args2 = parser.parse_args(["--list-windows"])
    assert args2.list_windows is True


def test_apply_cli_overrides():
    """_apply_cli_overrides altera config.CODEC, FPS, CRF, TEAMS_WINDOW_TITLE."""
    parser = main._build_parser()
    args = parser.parse_args([
        "--codec", "h264",
        "--fps", "25",
        "--crf", "29",
        "--title", "Meu Teams",
    ])
    main._apply_cli_overrides(args)
    assert main.config.CODEC == "h264"
    assert main.config.FPS == 25
    assert main.config.CRF == 29
    assert main.config.TEAMS_WINDOW_TITLE == "Meu Teams"


@patch("main.TeamsRecorder")
def test_run_returns_1_when_window_not_found(mock_recorder_cls):
    """run() retorna 1 quando find_window retorna False."""
    recorder = MagicMock()
    recorder.find_window.return_value = False
    mock_recorder_cls.return_value = recorder

    rc = main.run(skip_upload=True)
    assert rc == 1


@patch("main.TeamsRecorder")
def test_run_returns_1_when_start_fails(mock_recorder_cls):
    """run() retorna 1 quando start retorna (None, None)."""
    recorder = MagicMock()
    recorder.find_window.return_value = True
    recorder.start.return_value = (None, None)
    mock_recorder_cls.return_value = recorder

    rc = main.run(skip_upload=True)
    assert rc == 1
