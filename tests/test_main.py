"""
Testes do main.
Cobre: main() com mocks (recorder, parar_gravacao, config), handler SIGTERM, fluxo KeyboardInterrupt.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_main_sem_janela_sai_1():
    """Se find_window retorna None, main chama sys.exit(1)."""
    with patch("main.setup_logging"):
        with patch("main.TeamsRecorder") as Rec:
            rec = MagicMock()
            rec.find_window.return_value = None
            Rec.return_value = rec
            with pytest.raises(SystemExit) as exc:
                from main import main
                main()
            assert exc.value.code == 1


def test_main_com_janela_mas_start_falha_sai_1():
    """Se start retorna (None, None), main chama sys.exit(1)."""
    with patch("main.setup_logging"):
        with patch("main.TeamsRecorder") as Rec:
            rec = MagicMock()
            rec.find_window.return_value = MagicMock()
            rec.start.return_value = (None, None)
            Rec.return_value = rec
            with pytest.raises(SystemExit) as exc:
                from main import main
                main()
            assert exc.value.code == 1


def test_main_keyboard_interrupt_chama_parar_gravacao():
    """Em KeyboardInterrupt, main chama parar_gravacao(processo)."""
    fake_proc = MagicMock()
    fake_path = Path("/tmp/out.mkv")
    with patch("main.setup_logging"):
        with patch("main.TeamsRecorder") as Rec:
            rec = MagicMock()
            rec.find_window.return_value = MagicMock()
            rec.start.return_value = (fake_proc, fake_path)
            Rec.return_value = rec
            with patch("main.parar_gravacao") as parar:
                with patch.object(fake_proc, "wait", side_effect=KeyboardInterrupt):
                    with patch("main.config") as cfg:
                        cfg.GDRIVE_PASTA_LOCAL = None
                        cfg.GDRIVE_PASTA_ID = None
                    try:
                        from main import main
                        main()
                    except KeyboardInterrupt:
                        pass
                parar.assert_called_with(fake_proc)


def test_main_finally_faz_upload_se_configurado():
    """No finally, se out_path existe e GDRIVE_PASTA_ID está setado, chama upload."""
    fake_proc = MagicMock()
    fake_proc.wait.return_value = None
    fake_path = MagicMock()
    fake_path.exists.return_value = True
    fake_path.__bool__ = lambda self: True  # if out_path
    import main as main_mod
    with patch.object(main_mod, "TeamsRecorder") as Rec:
        rec = MagicMock()
        rec.find_window.return_value = MagicMock()
        rec.start.return_value = (fake_proc, fake_path)
        Rec.return_value = rec
        with patch.object(main_mod, "parar_gravacao"):
            with patch.object(main_mod.gravador, "copiar_para_gdrive"):
                with patch.object(main_mod, "upload_para_drive_api") as upload:
                    with patch.object(main_mod.config, "GDRIVE_PASTA_LOCAL", None):
                        with patch.object(main_mod.config, "GDRIVE_PASTA_ID", "folder_id"):
                            main_mod.main()
                    upload.assert_called_once_with(fake_path)


def test_main_finally_copia_para_gdrive_local_se_configurado():
    """No finally, se GDRIVE_PASTA_LOCAL está setado, chama copiar_para_gdrive."""
    fake_proc = MagicMock()
    fake_proc.wait.return_value = None
    fake_path = MagicMock()
    fake_path.exists.return_value = True
    fake_path.__bool__ = lambda self: True
    import main as main_mod
    with patch.object(main_mod, "TeamsRecorder") as Rec:
        rec = MagicMock()
        rec.find_window.return_value = MagicMock()
        rec.start.return_value = (fake_proc, fake_path)
        Rec.return_value = rec
        with patch.object(main_mod, "parar_gravacao"):
            with patch.object(main_mod.gravador, "copiar_para_gdrive") as copy:
                with patch.object(main_mod, "upload_para_drive_api"):
                    with patch.object(main_mod.config, "GDRIVE_PASTA_LOCAL", "/path/to/drive"):
                        with patch.object(main_mod.config, "GDRIVE_PASTA_ID", None):
                            main_mod.main()
                    copy.assert_called_once_with(fake_path)


def test_encerrar_por_sinal_chama_parar_gravacao():
    """_encerrar_por_sinal chama parar_gravacao quando _processo_atual está setado."""
    import main as main_mod
    with patch("main.parar_gravacao") as parar:
        with patch("main.config") as cfg:
            cfg.GDRIVE_PASTA_LOCAL = None
            cfg.GDRIVE_PASTA_ID = None
        main_mod._processo_atual = MagicMock()
        main_mod._out_path_atual = None
        with pytest.raises(SystemExit):
            main_mod._encerrar_por_sinal()
        parar.assert_called_once()
